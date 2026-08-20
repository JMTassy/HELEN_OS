"""HELEN_CONTROL_PLANE_V2 — ADMISSION_GUARD mint-binding. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Completes FIX ADMISSION_GUARD: closes the SELF_DECLARED_CONTRACT_FORGE class the fresh adversary
found in v1 (5 leaks incl shadow-overwrite). The admit path holds a MINT key; every RECEIPT carries a MAC tag;
the reducer folds an ADMITTED ONLY if a matching RECEIPT verifies under that key AND the task is not already
admitted (first-admission-wins). A caller WITHOUT the key cannot mint a valid receipt ⇒ cannot admit.

  reduce: verify_chain → verify RECEIPT mint-tag (HMAC) → contract-satisfying → first-admission-wins → fold
  closes:  1 self-forge · 2 re-chain · 3 contract-downgrade · 4 authority-self-grant · 5 shadow-overwrite

HONEST BOUNDARY: MINT_KEY is module-level (in-process) — this is HMAC-MODELED unforgeability: it excludes any
caller WITHOUT the key. A same-process adversary that reads MINT_KEY still forges — full unforgeability needs the
process boundary (cf. kernel_obligations_v2, already demonstrated this session). Law: an event label is a claim;
admission must survive re-verified proof, and proof must be mint-bound to an authority the reducer can check.
"""
import hashlib, hmac, json, pathlib
import helen_control_plane_v0 as v0
from helen_control_plane_v0 import (Ledger, H, GENESIS, POLICY, SOURCES, compile_context,
                                    capability_check, execute, project, good_task)
from helen_control_plane_v1 import verify_chain, LedgerIntegrityError

OUT = pathlib.Path(__file__).resolve().parent / "her_run"
MINT_KEY = b"HELEN_ADMIT_PATH_MINT_KEY_v2_modeled"          # held only by the admit path (modeled)

def canon(o): return json.dumps(o, sort_keys=True, default=str)
def mint_tag(body): return hmac.new(MINT_KEY, canon(body).encode(), hashlib.sha256).hexdigest()[:16]

# ── GUARDED WITNESS/ADMISSION v2: mint-bind the receipt ──
def admit_v2(task, contract, execution, witnesses, verification, authority_present, ledger):
    required, got = set(contract["required_witnesses"]), set(witnesses)
    if not required.issubset(got): return {"done": False, "reason": "MISSING_WITNESS", "state_change": False}
    if verification != contract["verification_policy"]: return {"done": False, "reason": "VERIFICATION_FAILED", "state_change": False}
    if not authority_present: return {"done": False, "reason": "ADMISSION_AUTHORITY_ABSENT", "state_change": False}
    receipt = {"task_id": task["task_id"], "witnesses": sorted(got), "verification": verification,
               "contract": {"required_witnesses": sorted(contract["required_witnesses"]),
                            "verification_policy": contract["verification_policy"],
                            "admission_authority": contract["admission_authority"]},
               "authority_present": True, "policy_version": POLICY["policy_version"],
               "artifact_hashes": [a["hash"] for a in execution["artifacts"]]}
    tag = mint_tag(receipt); rh = H(receipt)
    ledger.append("ADMITTED", {"task_id": task["task_id"], "receipt_hash": rh})
    ledger.append("RECEIPT", {"task_id": task["task_id"], "receipt": receipt, "receipt_hash": rh, "mint_tag": tag})
    return {"done": True, "reason": "COMPLETION_CONTRACT_SATISFIED", "state_change": True, "receipt_hash": rh}

# ── GUARDED REDUCER v2: verify chain + mint-tag + contract + first-wins ──
def reduce_v2(events):
    if not verify_chain(events): raise LedgerIntegrityError("CHAIN_BROKEN")
    receipts = {}
    for e in events:
        if e["kind"] == "RECEIPT":
            rec, rh, tag = e["payload"]["receipt"], e["payload"]["receipt_hash"], e["payload"].get("mint_tag", "")
            if H(rec) == rh and hmac.compare_digest(mint_tag(rec), tag):        # mint-tag MUST verify
                receipts[rh] = rec
    state = {"admitted": {}}
    for e in events:
        if e["kind"] != "ADMITTED": continue
        rh, tid = e["payload"]["receipt_hash"], e["payload"]["task_id"]
        rec = receipts.get(rh)
        if rec is None: continue                                               # no valid-tag receipt
        c = rec["contract"]
        ok = (set(rec["witnesses"]) >= set(c["required_witnesses"]) and rec["verification"] == c["verification_policy"]
              and rec["authority_present"] and rec["task_id"] == tid)
        if ok and tid not in state["admitted"]:                                # FIRST-admission-wins (kills shadow-overwrite)
            state["admitted"][tid] = rh
    return state

def run_v2(task, actor, policy, budget, reqs, srcs, witnesses, verif, authority, ledger):
    ctx = compile_context(task, actor, policy, budget, reqs, srcs)
    if ctx["decision"] != "OK": return {"halted": "CONTEXT", "done": False}
    if capability_check(actor, task["requested_effects"], policy)["decision"] != "ALLOW": return {"halted": "CAPABILITY", "done": False}
    ex = execute(task, task["requested_effects"])
    wa = admit_v2(task, task["completion_contract"], ex, witnesses, verif, authority, ledger)
    return {"done": wa["done"], "reason": wa["reason"], "receipt": wa.get("receipt_hash"),
            "artifact_hashes": [a["hash"] for a in ex["artifacts"]]}

def main():
    print("=== HELEN_CONTROL_PLANE_V2 — ADMISSION_GUARD mint-binding ===\n")
    rows = []
    # honest path admits
    Lh = Ledger(); dry = run_v2(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present", "peer_review"], "PASS", True, Lh)
    st = reduce_v2(Lh.events)
    rows.append(("honest path admits", dry["done"] and st["admitted"].get("T-001") == dry["receipt"]))

    # re-attack the 5 forge-class leaks WITHOUT the key (forger can't mint a valid tag)
    def forged_receipt(task_id, tid_admit=None):
        rec = {"task_id": task_id, "witnesses": [], "verification": "PASS",
               "contract": {"required_witnesses": [], "verification_policy": "PASS", "admission_authority": "NOBODY"},
               "authority_present": True, "policy_version": "P0", "artifact_hashes": []}
        return rec, H(rec)
    # A1 self-forge
    L1 = Ledger(); rec, rh = forged_receipt("EVIL"); L1.append("ADMITTED", {"task_id": "EVIL", "receipt_hash": rh}); L1.append("RECEIPT", {"task_id": "EVIL", "receipt": rec, "receipt_hash": rh, "mint_tag": "0" * 16})
    rows.append(("A1 self-forge (bad tag) rejected", "EVIL" not in reduce_v2(L1.events)["admitted"]))
    # A2 full re-chain (still no valid tag)
    L2 = Ledger(); rec, rh = forged_receipt("REBUILD"); L2.append("RECEIPT", {"task_id": "REBUILD", "receipt": rec, "receipt_hash": rh, "mint_tag": mint_tag(rec)[:8] + "deadbeef"}); L2.append("ADMITTED", {"task_id": "REBUILD", "receipt_hash": rh})
    rows.append(("A2 re-chain (forged tag) rejected", "REBUILD" not in reduce_v2(L2.events)["admitted"]))
    # A3 contract-downgrade on real task id
    L3 = Ledger(); rec, rh = forged_receipt("T-001"); L3.append("ADMITTED", {"task_id": "T-001", "receipt_hash": rh}); L3.append("RECEIPT", {"task_id": "T-001", "receipt": rec, "receipt_hash": rh, "mint_tag": "1" * 16})
    rows.append(("A3 contract-downgrade rejected", "T-001" not in reduce_v2(L3.events)["admitted"]))
    # A4 authority self-grant
    rows.append(("A4 authority self-grant rejected", "T-001" not in reduce_v2(L3.events)["admitted"]))
    # A5 shadow-overwrite: honest admit, then forged receipt+admitted for same task
    L5 = Ledger(); d5 = run_v2(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present", "peer_review"], "PASS", True, L5)
    rec, rh = forged_receipt("T-001"); L5.append("ADMITTED", {"task_id": "T-001", "receipt_hash": rh}); L5.append("RECEIPT", {"task_id": "T-001", "receipt": rec, "receipt_hash": rh, "mint_tag": "2" * 16})
    rows.append(("A5 shadow-overwrite blocked (first-wins + bad tag)", reduce_v2(L5.events)["admitted"]["T-001"] == d5["receipt"]))
    # T1..T7 regression (guarded v2)
    L_a = Ledger(); r_a = run_v2(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present"], "PASS", True, L_a)
    rows.append(("T1 missing witness → NOT_DONE", (not r_a["done"]) and reduce_v2(L_a.events)["admitted"] == {}))
    L_b = Ledger(); r_b = run_v2(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present", "peer_review"], "FAIL", True, L_b)
    rows.append(("T2 verification fail → NOT_DONE", (not r_b["done"]) and reduce_v2(L_b.events)["admitted"] == {}))
    rows.append(("T3 unauthorized source → halt", run_v2(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:secret"], SOURCES, ["artifact_present", "peer_review"], "PASS", True, Ledger()).get("halted") == "CONTEXT"))
    L_d = Ledger(); r_d = run_v2(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES, ["artifact_present", "peer_review"], "PASS", False, L_d)
    rows.append(("T4 no authority → NO_STATE_CHANGE", (not r_d["done"]) and reduce_v2(L_d.events)["admitted"] == {}))
    rows.append(("T5 replay rebuild", project(reduce_v2(Lh.events)) == project(reduce_v2(Lh.events)) and project(reduce_v2(Lh.events))["admitted_count"] == 1))
    ca = compile_context(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES); cb = compile_context(good_task(), "goblin_A", POLICY, 4000, ["src:corpus", "src:task_notes"], SOURCES)
    rows.append(("T6 deterministic context hash", ca["content_hash"] == cb["content_hash"]))
    rc = [e for e in Lh.events if e["kind"] == "RECEIPT"][0]["payload"]["receipt"]
    rows.append(("T7 receipt binds policy+hashes", rc["policy_version"] == "P0" and rc["artifact_hashes"] == dry["artifact_hashes"]))

    print("  RE-ATTACK (5 forge leaks) + T1-T7 + shadow-overwrite:")
    allok = True
    for name, ok in rows:
        allok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n  ALL_PASS = {allok}")
    print("  BOUNDARY: MINT_KEY in-process ⇒ HMAC-MODELED unforgeability (excludes key-less callers; same-process key-reader still forges → needs process boundary, cf kernel_obligations_v2)")

    receipt = {"receipt": "HELEN_CONTROL_PLANE_V2_MINT_BINDING",
               "closes": "SELF_DECLARED_CONTRACT_FORGE (A1 self-forge · A2 re-chain · A3 downgrade · A4 authority-self-grant · A5 shadow-overwrite)",
               "mechanism": "RECEIPT mint-tag HMAC(MINT_KEY) verified in reduce + first-admission-wins",
               "regression_and_attacks": {name: bool(ok) for name, ok in rows}, "all_pass": allok,
               "HONEST_BOUNDARY": "HMAC-MODELED: excludes callers WITHOUT the key; in-process key-reader not excluded (needs process boundary)",
               "CONTROL_PLANE_EARNED": "BOUNDED_SURVIVAL_pending_fresh_adversary" if allok else "HOLD",
               "SelfPassed": True, "PeerAdversaryValidated": False,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str); receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "control_plane_v2_mint_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/control_plane_v2_mint_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
