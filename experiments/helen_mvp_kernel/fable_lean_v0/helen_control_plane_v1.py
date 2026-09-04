"""HELEN_CONTROL_PLANE_V1 — ADMISSION_GUARD. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Closes CONTROL_PLANE_GAP_01 found by semantic audit of v0: the Reducer TRUSTED the ADMITTED label instead of
re-deriving admission from a persisted proof. Minimal fix — patch the broken causal edge, NOT the architecture:

  Reducer: trusting folder  ⟶  proof re-verifier
  (1) verify_chain(events) fail-closed  (tamper/reorder ⇒ NO admissions)      → closes M2 (tampered payload)
  (2) Admitted(t) ⟺ ∃ RECEIPT R_t with H(R)=receipt_hash ∧ witnesses(R)⊇required ∧ verification(R)=policy ∧ authority_present
                                                                               → closes M1 (forged bare ADMITTED)

No new primitive · no Γ change · no new subsystem · no UI. Reuses v0's unchanged pieces.
Law: an event label is a CLAIM about history; a reducer must RECONSTRUCT institutional truth from proof, not trust the label.
KNOWN LIMIT: a fully self-consistent FORGED RECEIPT (embedding a satisfiable contract) is NOT excluded here — that
needs cryptographic mint-binding (HMAC, cf. kernel_obligations_v1), deliberately out of this minimal patch.
"""
import hashlib, json, pathlib
import helen_control_plane_v0 as v0
from helen_control_plane_v0 import (Ledger, H, GENESIS, POLICY, SOURCES, compile_context,
                                    capability_check, execute, project, good_task)

OUT = pathlib.Path(__file__).resolve().parent / "her_run"

class LedgerIntegrityError(Exception): pass

def verify_chain(events):
    prev = GENESIS
    for e in events:
        if e.get("prev") != prev: return False                      # reorder / insert
        if e.get("hash") != H({k: e[k] for k in ("seq", "kind", "payload", "prev")}): return False  # tamper
        prev = e["hash"]
    return True

# ── GUARDED REDUCER: verify chain, then re-derive admission from contract-satisfying receipts ──
def guarded_reduce(events):
    if not verify_chain(events):
        raise LedgerIntegrityError("CHAIN_BROKEN")                   # fail-closed (M2)
    receipts = {}
    for e in events:
        if e["kind"] == "RECEIPT":
            rec, rh = e["payload"]["receipt"], e["payload"]["receipt_hash"]
            if H(rec) == rh:                                         # receipt self-integrity
                receipts[rh] = rec
    state = {"admitted": {}}
    for e in events:
        if e["kind"] != "ADMITTED":
            continue
        rh, tid = e["payload"]["receipt_hash"], e["payload"]["task_id"]
        rec = receipts.get(rh)
        if rec is None:                                             # M1: forged ADMITTED, no matching receipt
            continue
        c = rec["contract"]
        proof_ok = (set(rec["witnesses"]) >= set(c["required_witnesses"])
                    and rec["verification"] == c["verification_policy"]
                    and rec["authority_present"] and rec["task_id"] == tid)
        if proof_ok:
            state["admitted"][tid] = rh
    return state

# ── GUARDED WITNESS/ADMISSION: receipt embeds the contract + authority so reduce can re-verify ──
def guarded_witness_and_admit(task, contract, execution, provided_witnesses, verification_result, admission_authority_present, ledger):
    required, got = set(contract["required_witnesses"]), set(provided_witnesses)
    if not required.issubset(got):
        return {"done": False, "reason": "MISSING_WITNESS", "missing": sorted(required - got), "state_change": False}
    if verification_result != contract["verification_policy"]:
        return {"done": False, "reason": "VERIFICATION_FAILED", "state_change": False}
    if not admission_authority_present:
        return {"done": False, "reason": "ADMISSION_AUTHORITY_ABSENT", "state_change": False}
    receipt = {"task_id": task["task_id"], "witnesses": sorted(got), "verification": verification_result,
               "contract": {"required_witnesses": sorted(contract["required_witnesses"]),
                            "verification_policy": contract["verification_policy"],
                            "admission_authority": contract["admission_authority"]},
               "authority_present": True, "policy_version": POLICY["policy_version"],
               "artifact_hashes": [a["hash"] for a in execution["artifacts"]]}
    rh = H(receipt)
    ledger.append("ADMITTED", {"task_id": task["task_id"], "receipt_hash": rh})
    ledger.append("RECEIPT", {"task_id": task["task_id"], "receipt": receipt, "receipt_hash": rh})
    return {"done": True, "reason": "COMPLETION_CONTRACT_SATISFIED", "state_change": True, "receipt_hash": rh, "receipt": receipt}

def run_task_v1(intent, task, actor, policy, budget, reqs, srcs, witnesses, verif, authority, ledger):
    lin = {"intent": intent, "task": task["task_id"], "policy_version": policy["policy_version"]}
    ctx = compile_context(task, actor, policy, budget, reqs, srcs)
    lin["context"] = {"context_id": ctx.get("context_id"), "decision": ctx["decision"]}
    if ctx["decision"] != "OK": return {**lin, "halted": "CONTEXT", "detail": ctx}
    cap = capability_check(actor, task["requested_effects"], policy); lin["capability"] = cap
    if cap["decision"] != "ALLOW": return {**lin, "halted": "CAPABILITY", "detail": cap}
    ex = execute(task, task["requested_effects"]); lin["execution"] = {"exit_code": ex["exit_code"]}
    lin["artifact_hashes"] = [a["hash"] for a in ex["artifacts"]]
    wa = guarded_witness_and_admit(task, task["completion_contract"], ex, witnesses, verif, authority, ledger)
    lin["admission"] = {"done": wa["done"], "reason": wa["reason"], "state_change": wa["state_change"]}
    lin["receipt"] = wa.get("receipt_hash"); lin["done"] = wa["done"]
    return lin

def main():
    print("=== HELEN_CONTROL_PLANE_V1 — ADMISSION_GUARD ===\n")

    # ---- CONTROL_PLANE_GAP_01: confirm v0 accepts the forged ADMITTED; v1 rejects it ----
    Lf = Ledger()
    Lf.append("ADMITTED", {"task_id": "FORGED", "receipt_hash": "sha256:deadbeef"})    # bare forge, no witness/verify/authority
    v0_state = v0.reduce(Lf.events)                                                     # trusting folder
    v1_state = guarded_reduce(Lf.events)                                               # proof re-verifier
    m1_v0_accepts = ("FORGED" in v0_state["admitted"])
    m1_v1_rejects = ("FORGED" not in v1_state["admitted"])
    print(f"  M1 forged bare ADMITTED:  v0={v0_state['admitted']}  → v0_accepts={m1_v0_accepts}")
    print(f"                            v1={v1_state['admitted']}  → v1_rejects={m1_v1_rejects}")

    # M2 tampered payload → fail-closed under v1
    Lh = Ledger()
    r = run_task_v1("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES,
                    ["artifact_present", "peer_review"], "PASS", True, Lh)
    Lh.events[0]["payload"]["task_id"] = "HACKED"                                       # tamper (stale hash)
    try:
        guarded_reduce(Lh.events); m2_v1_rejects = False
    except LedgerIntegrityError:
        m2_v1_rejects = True
    v0_tampered = v0.reduce(Lh.events)                                                  # v0 silently folds tamper
    print(f"  M2 tampered payload:      v0={v0_tampered['admitted']} (silently HACKED)  → v1_fail_closed={m2_v1_rejects}")

    # ---- T1..T7 regression under v1 (guarded reduce/admit) ----
    rows = []
    Ld = Ledger(); dry = run_task_v1("ship", good_task(), "goblin_A", POLICY, 4000,
                                     ["src:corpus", "src:task_notes"], SOURCES,
                                     ["artifact_present", "peer_review"], "PASS", True, Ld)
    dry_state = guarded_reduce(Ld.events)
    rows.append(("T-dry ADMITTED via honest path", dry["done"] and dry_state["admitted"].get("T-001") == dry["receipt"]))
    L1 = Ledger(); r1 = run_task_v1("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present"], "PASS", True, L1)
    rows.append(("T1 missing witness → NOT_DONE", (not r1["done"]) and r1["admission"]["reason"] == "MISSING_WITNESS" and guarded_reduce(L1.events)["admitted"] == {}))
    L2 = Ledger(); r2 = run_task_v1("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present", "peer_review"], "FAIL", True, L2)
    rows.append(("T2 exit0 contract unsatisfied", (not r2["done"]) and r2["admission"]["reason"] == "VERIFICATION_FAILED" and guarded_reduce(L2.events)["admitted"] == {}))
    L3 = Ledger(); r3 = run_task_v1("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:secret"], SOURCES, ["artifact_present", "peer_review"], "PASS", True, L3)
    rows.append(("T3 unauthorized source → REJECT_CONTEXT", r3.get("halted") == "CONTEXT"))
    L4 = Ledger(); r4 = run_task_v1("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present", "peer_review"], "PASS", False, L4)
    rows.append(("T4 no admission authority → NO_STATE_CHANGE", (not r4["done"]) and guarded_reduce(L4.events)["admitted"] == {}))
    proj_before = project(guarded_reduce(Ld.events)); proj_rebuilt = project(guarded_reduce(Ld.events))
    rows.append(("T5 replay rebuild (guarded)", proj_before == proj_rebuilt and proj_before["admitted_count"] == 1))
    ca = compile_context(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES)
    cb = compile_context(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES)
    rows.append(("T6 deterministic context hash", ca["content_hash"] == cb["content_hash"]))
    rcpt = [e for e in Ld.events if e["kind"] == "RECEIPT"][0]["payload"]["receipt"]
    rows.append(("T7 receipt binds policy_version + artifact_hashes", rcpt["policy_version"] == "P0" and rcpt["artifact_hashes"] == dry["artifact_hashes"]))
    # NEW guard tests
    rows.append(("M1 forged ADMITTED rejected", m1_v1_rejects))
    rows.append(("M2 tampered payload fail-closed", m2_v1_rejects))

    print("\n  REGRESSION + GUARD TESTS (v1):")
    allok = True
    for name, ok in rows:
        allok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n  ALL_PASS = {allok}")

    gap = {"artifact": "CONTROL_PLANE_GAP_01",
           "INVARIANT": "Only proof-backed admission may enter reduced governed state (ADMITTED_EVENT ⊬ ADMITTED_STATE)",
           "ORIGINAL_TEST": "T5/T7 — replay rebuilds projection; receipt binds policy+hashes",
           "ORIGINAL_TEST_ACTUALLY_WITNESSES": "honest-path replay reconstructs expected state (NOT: only honest path can produce it)",
           "MINIMAL_MUTANT": "M1 forged bare ADMITTED (no contract-satisfying receipt) · M2 tampered payload",
           "EXPECTED": "NOT_FOLDED / REJECT",
           "OBSERVED_V0": {"M1": "FOLDED_AS_ADMITTED", "M2": "silently_HACKED"},
           "GAP_CONFIRMED": bool(m1_v0_accepts),
           "ROOT_CAUSE": "Reducer trusted kind=='ADMITTED' label instead of re-verifying proof",
           "PATCH_SURFACE": "reduce(): + verify_chain fail-closed; + re-derive admission from contract-satisfying RECEIPT",
           "LINES_CHANGED": "guarded_reduce + guarded_witness_and_admit (receipt embeds contract); no new primitive",
           "NEW_AUTHORITY": False, "GAMMA_CHANGE": False,
           "M1_v0_accepts": m1_v0_accepts, "M1_v1_rejects": m1_v1_rejects, "M2_v1_fail_closed": m2_v1_rejects,
           "REGRESSION_T1_T7_plus_guards": {name: bool(ok) for name, ok in rows}, "ALL_PASS": allok,
           "KNOWN_LIMITS": "self-consistent forged RECEIPT (embeds satisfiable contract) not excluded — needs HMAC mint-binding (out of minimal patch)",
           "CONTROL_PLANE_EARNED": "BOUNDED_SURVIVAL_pending_fresh_adversary" if allok else "HOLD",
           "SelfPassed": True, "PeerAdversaryValidated": False,
           "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(gap, indent=2, default=str); gap["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "control_plane_gap_01_receipt.json").write_text(json.dumps(gap, indent=2, default=str))
    print(f"\n  GAP_CONFIRMED(v0)={m1_v0_accepts} · M1_v1_rejects={m1_v1_rejects} · M2_v1_fail_closed={m2_v1_rejects}")
    print("  Patch the broken causal edge, not the architecture. No new primitive · no Γ change.")
    print(f"  receipt: her_run/control_plane_gap_01_receipt.json sha16={gap['receipt_sha16']}")

if __name__ == "__main__":
    main()
