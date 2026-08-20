"""HELEN_CONTROL_PLANE_V0 — the smallest governed execution spine. authority=false · canon=false ·
ledger_effect=none. NON-SOVEREIGN. NOT an agent orchestrator — a governed lineage from intent to admitted effect.

Four primitives, none absorbs another:
  TG TaskGraph          — carries intent + dependencies, NOT authority       (TaskGraph ⊬ Authority)
  CC ContextCompiler    — governed replayable context, NOT capability        (ContextCompiler ⊬ Capability)
  CG CapabilityGate     — may this actor ATTEMPT this effect, NOT admit it   (CapabilityGranted ⊬ Admission)
  WA Witness/Admission  — what counts as done + what enters state, NOT truth (Witness ⊬ Truth)

Done(t) ⟺ SatisfiesCompletionContract(t)   (never a bare agent-declared boolean; ExitCode(0) ⊬ Done)
Canonical geometry:  Ledger → Reducer → GovernedState → Projection   (Projection ⊬ CanonicalTruth; rebuildable)
Execution lineage L(t) = (intent, task, context, capability, execution, witness, verification, admission,
                          receipt, policy_version, artifact_hashes)  — the moat object.

HELEN does not orchestrate agents. HELEN governs the lineage by which cognition becomes effect.
"""
import hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)
GENESIS = "sha256:" + "0" * 16
def H(obj): return "sha256:" + hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]

# ── POLICY (versioned; the rules under which everything happens) ──
POLICY = {
    "policy_version": "P0",
    "authorized_read": {"goblin_A": ["src:corpus", "src:task_notes"]},   # actor → readable sources
    "granted_capabilities": {"goblin_A": ["EFFECT:write_artifact"]},      # actor → attemptable effects
    "admission_authority": {"admit": "OPERATOR"},                         # who may admit a verified result
}

# ── LEDGER: append-only, hash-chained (the ONLY canonical substrate) ──
class Ledger:
    def __init__(self): self.events = []; self.head = GENESIS
    def append(self, kind, payload):
        rec = {"seq": len(self.events), "kind": kind, "payload": payload, "prev": self.head}
        rec["hash"] = H({k: rec[k] for k in ("seq", "kind", "payload", "prev")})
        self.events.append(rec); self.head = rec["hash"]; return rec["hash"]

# ── REDUCER: ledger → governed state (ONLY ADMITTED changes institutional state) ──
def reduce(events):
    state = {"admitted": {}}
    for e in events:
        if e["kind"] == "ADMITTED":
            state["admitted"][e["payload"]["task_id"]] = e["payload"]["receipt_hash"]
    return state

# ── PROJECTION: state → view (rebuildable, NOT truth) ──
def project(state):
    return {"admitted_count": len(state["admitted"]), "tasks": sorted(state["admitted"])}

# ── CC ContextCompiler: C(a,t)=f(task,actor,scope,policy,budget,sources) ; Context ⊆ AuthorizedRead ──
def compile_context(task, actor, policy, budget, requested_sources, source_bytes):
    allowed = set(policy["authorized_read"].get(actor, []))
    for s in requested_sources:
        if s not in allowed:
            return {"decision": "REJECT_CONTEXT", "reason": f"UNAUTHORIZED_SOURCE:{s}", "actor": actor}
    m = {"task_id": task["task_id"], "actor_id": actor, "source_refs": sorted(requested_sources),
         "source_hashes": {s: H(source_bytes[s]) for s in sorted(requested_sources)},
         "capability_scope": sorted(policy["granted_capabilities"].get(actor, [])),
         "selection_policy": "authorized_read_subset", "token_budget": budget, "compiler_version": "CC0"}
    m["content_hash"] = H(m); m["context_id"] = m["content_hash"]; m["decision"] = "OK"
    return m

# ── CG CapabilityGate: may actor ATTEMPT effect? (not: is it admitted?) ──
def capability_check(actor, requested_effects, policy):
    granted = set(policy["granted_capabilities"].get(actor, []))
    per = {e: (e in granted) for e in requested_effects}
    return {"decision": "ALLOW" if all(per.values()) else "DENY", "per_effect": per}

# ── EXECUTION (stub; exit 0 ⊬ done) ──
def execute(task, effects):
    return {"exit_code": 0, "claimed_done": True,
            "artifacts": [{"name": f"artifact:{task['task_id']}", "hash": H({"t": task["task_id"], "e": sorted(effects)})}]}

# ── WA Witness/Admission: Done ⟺ SatisfiesCompletionContract ; Verified ⊬ Admitted without authority ──
def witness_and_admit(task, contract, execution, provided_witnesses, verification_result, admission_authority_present, ledger):
    required, got = set(contract["required_witnesses"]), set(provided_witnesses)
    if not required.issubset(got):
        return {"done": False, "reason": "MISSING_WITNESS", "missing": sorted(required - got), "state_change": False}
    if verification_result != contract["verification_policy"]:
        return {"done": False, "reason": "VERIFICATION_FAILED", "state_change": False}
    if not admission_authority_present:                                    # Verified ⊬ Admitted
        return {"done": False, "reason": "ADMISSION_AUTHORITY_ABSENT", "state_change": False}
    receipt = {"task_id": task["task_id"], "witnesses": sorted(got), "verification": verification_result,
               "policy_version": POLICY["policy_version"], "artifact_hashes": [a["hash"] for a in execution["artifacts"]]}
    rh = H(receipt)
    ledger.append("ADMITTED", {"task_id": task["task_id"], "receipt_hash": rh})       # the ONLY state-changing event
    ledger.append("RECEIPT", {"task_id": task["task_id"], "receipt": receipt, "receipt_hash": rh})
    return {"done": True, "reason": "COMPLETION_CONTRACT_SATISFIED", "state_change": True, "receipt_hash": rh, "receipt": receipt}

# ── FLOW: INTENT → TASK → CONTEXT → CAPABILITY → EXECUTION → WITNESS → VERIFY → ADMISSION → RECEIPT (→ REPLAY) ──
def run_task(intent, task, actor, policy, budget, requested_sources, source_bytes,
             provided_witnesses, verification_result, admission_authority_present, ledger):
    lineage = {"intent": intent, "task": task["task_id"], "policy_version": policy["policy_version"]}
    ctx = compile_context(task, actor, policy, budget, requested_sources, source_bytes)
    lineage["context"] = {"context_id": ctx.get("context_id"), "decision": ctx["decision"]}
    if ctx["decision"] != "OK":
        return {**lineage, "halted": "CONTEXT", "detail": ctx}
    cap = capability_check(actor, task["requested_effects"], policy)
    lineage["capability"] = cap
    if cap["decision"] != "ALLOW":
        return {**lineage, "halted": "CAPABILITY", "detail": cap}
    ex = execute(task, task["requested_effects"])
    lineage["execution"] = {"exit_code": ex["exit_code"]}; lineage["artifact_hashes"] = [a["hash"] for a in ex["artifacts"]]
    wa = witness_and_admit(task, task["completion_contract"], ex, provided_witnesses,
                           verification_result, admission_authority_present, ledger)
    lineage["witness"] = {"provided": sorted(provided_witnesses)}
    lineage["verification"] = verification_result
    lineage["admission"] = {"done": wa["done"], "reason": wa["reason"], "state_change": wa["state_change"]}
    lineage["receipt"] = wa.get("receipt_hash")
    lineage["done"] = wa["done"]
    return lineage

# ── a well-formed task that SATISFIES its completion contract ──
def good_task():
    return {"task_id": "T-001", "goal_ref": "G-1", "dependencies": [], "requested_effects": ["EFFECT:write_artifact"],
            "completion_contract": {"required_witnesses": ["artifact_present", "peer_review"],
                                    "verification_policy": "PASS", "admission_authority": "OPERATOR",
                                    "required_receipts": ["RECEIPT_V0"]}}
SOURCES = {"src:corpus": {"bytes": "corpus-A"}, "src:task_notes": {"bytes": "notes-A"}, "src:secret": {"bytes": "secret"}}

def main():
    print("=== HELEN_CONTROL_PLANE_V0 ===\n")
    # ---- DRY-RUN: one full lineage that reaches ADMITTED ----
    L = Ledger()
    dry = run_task("ship the parser", good_task(), "goblin_A", POLICY, 4000,
                   ["src:corpus", "src:task_notes"], SOURCES,
                   ["artifact_present", "peer_review"], "PASS", True, L)
    print("  DRY-RUN lineage:")
    for k in ("intent","task","policy_version","context","capability","execution","witness","verification","admission","receipt","done"):
        print(f"    {k:14}= {dry.get(k)}")
    state = reduce(L.events); proj = project(state)
    print(f"    governed_state= {state}\n    projection    = {proj}\n")

    # ---- TESTS T1..T7 ----
    rows = []
    # T1: agent reports DONE but a required witness is missing → NOT_DONE
    L1 = Ledger(); r1 = run_task("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus","src:task_notes"], SOURCES,
                                 ["artifact_present"], "PASS", True, L1)  # missing peer_review
    rows.append(("T1 report-done, missing witness", (not r1["done"]) and r1["admission"]["reason"]=="MISSING_WITNESS" and reduce(L1.events)["admitted"]=={}))
    # T2: exit 0 but completion contract not satisfied (verification fails) → NOT_DONE
    L2 = Ledger(); r2 = run_task("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus","src:task_notes"], SOURCES,
                                 ["artifact_present","peer_review"], "FAIL", True, L2)
    rows.append(("T2 exit0, contract unsatisfied", (not r2["done"]) and r2["admission"]["reason"]=="VERIFICATION_FAILED" and reduce(L2.events)["admitted"]=={}))
    # T3: context includes an unauthorized source → REJECT_CONTEXT
    L3 = Ledger(); r3 = run_task("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus","src:secret"], SOURCES,
                                 ["artifact_present","peer_review"], "PASS", True, L3)
    rows.append(("T3 unauthorized source", r3.get("halted")=="CONTEXT" and r3["detail"]["reason"].startswith("UNAUTHORIZED_SOURCE")))
    # T4: capability present but admission authority absent → NO_STATE_CHANGE
    L4 = Ledger(); r4 = run_task("i", good_task(), "goblin_A", POLICY, 4000, ["src:corpus","src:task_notes"], SOURCES,
                                 ["artifact_present","peer_review"], "PASS", False, L4)  # no admission authority
    rows.append(("T4 capability ok, no admission authority", (not r4["done"]) and r4["admission"]["reason"]=="ADMISSION_AUTHORITY_ABSENT" and reduce(L4.events)["admitted"]=={}))
    # T5: projection deleted → replay ledger → rebuild equivalent projection
    proj_before = project(reduce(L.events)); del proj  # drop the projection object
    proj_rebuilt = project(reduce(L.events))           # rebuilt purely from canonical ledger
    rows.append(("T5 projection rebuilt from replay", proj_before == proj_rebuilt and proj_before["admitted_count"]==1))
    # T6: same task + same frozen inputs + same policy → same context manifest hash
    c_a = compile_context(good_task(), "goblin_A", POLICY, 4000, ["src:corpus","src:task_notes"], SOURCES)
    c_b = compile_context(good_task(), "goblin_A", POLICY, 4000, ["src:corpus","src:task_notes"], SOURCES)
    rows.append(("T6 deterministic context hash", c_a["content_hash"]==c_b["content_hash"]))
    # T7: receipt lineage references exact policy_version + artifact_hashes
    rcpt = [e for e in L.events if e["kind"]=="RECEIPT"][0]["payload"]["receipt"]
    rows.append(("T7 receipt binds policy_version + artifact_hashes",
                 rcpt["policy_version"]=="P0" and rcpt["artifact_hashes"]==dry["artifact_hashes"]))

    print("  TESTS:")
    allok = True
    for name, ok in rows:
        allok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n  ALL_PASS = {allok}")

    # ---- REPLAY demonstration ----
    print("\n  REPLAY: delete projection + reducer output, rebuild from canonical ledger:")
    rebuilt_state = reduce(L.events); rebuilt_proj = project(rebuilt_state)
    print(f"    ledger_events={len(L.events)} · ledger_head={L.head[-8:]}")
    print(f"    rebuilt_state={rebuilt_state}")
    print(f"    rebuilt_projection={rebuilt_proj}  (ProjectionLoss ⊬ InstitutionalLoss)")

    receipt = {"receipt": "HELEN_CONTROL_PLANE_V0", "primitives": ["TG","CC","CG","WA"],
               "load_bearing_laws": ["TaskGraph⊬Authority","ContextCompiler⊬Capability","CapabilityGranted⊬Admission",
                 "Witness⊬Truth","AgentReport⊬Done","ExitCode(0)⊬InstitutionalSuccess","TestsPass⊬Admission",
                 "ContextAvailable⊬ContextAuthorized","UI⊬Ledger","Projection⊬CanonicalTruth"],
               "done_semantics": "Done(t) ⟺ SatisfiesCompletionContract(t)",
               "dry_run_lineage": {k: dry.get(k) for k in ("intent","task","policy_version","context","capability","execution","witness","verification","admission","receipt","done","artifact_hashes")},
               "tests": {name: bool(ok) for name, ok in rows}, "all_pass": allok,
               "canonical_geometry": "Ledger→Reducer→GovernedState→Projection",
               "replay": {"ledger_events": len(L.events), "ledger_head": L.head, "rebuilt_projection": rebuilt_proj},
               "SelfPassed": True, "PeerAdversaryValidated": False,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "helen_control_plane_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"\n  HELEN does not orchestrate agents; it governs the lineage by which cognition becomes effect.")
    print(f"  authority=false · canon=false · ledger_effect=none · receipt: her_run/helen_control_plane_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
