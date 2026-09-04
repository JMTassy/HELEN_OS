"""TRUSTED_CONTRACT_BINDING_V0. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Closes the axis v2 mint-binding did NOT: the receipt still DEFINED the rules it was judged by (embedded contract +
self-set authority_present). Here the reducer resolves trust material OUTWARD against stores the candidate cannot
author, and the receipt carries only REFERENCES.

  "The claimant may reference the rule. It may not define the rule being used to judge itself."
  EmbeddedContract ⊬ TrustedContract · ReVerification ⊬ IndependentVerification.

Receipt = { task_id, contract_ref, authority_grant_id, policy_id, witness_refs[], artifact_hashes[], execution_ref, supersedes? }
Reducer resolves outward:  TrustedContract(task_id) · VerifiedAuthorityGrant(grant_id) · TrustedPolicy(policy_id)
  Validate(r) ⟺ Witnesses(r) ⊨ TrustedContract(task_r) ∧ grant authorizes admit(task_r) ∧ policy trusted
                ∧ receipt HMAC-bound to the GRANT's key ∧ artifact/receipt bindings PASS
Supersession = APPEND (roadmap): a later valid admission references the current receipt + a grant with may_supersede;
  the reducer appends to the task's lineage and moves the pointer — the prior admission is NEVER erased.

HONEST BOUNDARY: stores + grant keys are in-process (modeled); full unforgeability needs the process boundary
(kernel_obligations_v2). The ARCHITECTURE (resolve-outward) is the point — it no longer trusts the claimant's rules.
"""
import hashlib, hmac, json, pathlib
from helen_control_plane_v0 import Ledger, H, POLICY, SOURCES, compile_context, capability_check, execute, good_task
from helen_control_plane_v1 import verify_chain, LedgerIntegrityError

OUT = pathlib.Path(__file__).resolve().parent / "her_run"
def canon(o): return json.dumps(o, sort_keys=True, default=str)

# ── TRUSTED STORES — external to any candidate; the candidate cannot author these ──
TRUSTED_CONTRACTS = {"T-001": {"required_witnesses": ["artifact_present", "peer_review"], "verification_policy": "PASS"}}
TRUSTED_POLICY = {"P0": {"ok": True}}
AUTHORITY_GRANTS = {  # grant_id → resolvable authority object (identity, scope, tasks, key, supersede right)
    "G-admit-1":     {"authority": "OPERATOR", "scope": "admit", "tasks": ["T-001"], "key": b"grant_key_admit_1", "may_supersede": False},
    "G-supersede-1": {"authority": "OPERATOR", "scope": "admit", "tasks": ["T-001"], "key": b"grant_key_super_1", "may_supersede": True},
}
def grant_tag(grant_key, receipt): return hmac.new(grant_key, canon(receipt).encode(), hashlib.sha256).hexdigest()[:16]

def admit(task, grant_id, verification, witness_refs, artifact_hashes, ledger, supersedes=None):
    """Admit path: builds a REFERENCE receipt bound to the grant's key. Does NOT embed the contract."""
    grant = AUTHORITY_GRANTS.get(grant_id)
    if grant is None: return {"done": False, "reason": "NO_SUCH_GRANT"}
    receipt = {"task_id": task["task_id"], "contract_ref": task["task_id"], "authority_grant_id": grant_id,
               "policy_id": POLICY["policy_version"], "witness_refs": sorted(witness_refs),
               "artifact_hashes": artifact_hashes, "execution_ref": H({"t": task["task_id"], "v": verification}),
               "verification": verification, "supersedes": supersedes}
    tag = grant_tag(grant["key"], receipt); rh = H(receipt)
    ledger.append("ADMITTED", {"task_id": task["task_id"], "receipt_hash": rh})
    ledger.append("RECEIPT", {"task_id": task["task_id"], "receipt": receipt, "receipt_hash": rh, "grant_tag": tag})
    return {"done": True, "reason": "ADMITTED", "receipt_hash": rh}

def reduce_tcb(events):
    if not verify_chain(events): raise LedgerIntegrityError("CHAIN_BROKEN")
    valid = {}
    for e in events:
        if e["kind"] != "RECEIPT": continue
        rec, rh, tag = e["payload"]["receipt"], e["payload"]["receipt_hash"], e["payload"].get("grant_tag", "")
        if H(rec) != rh: continue
        grant = AUTHORITY_GRANTS.get(rec.get("authority_grant_id"))                       # RESOLVE OUTWARD
        if grant is None or not hmac.compare_digest(grant_tag(grant["key"], rec), tag): continue  # bound to grant key
        tc = TRUSTED_CONTRACTS.get(rec.get("contract_ref"))                               # RESOLVE OUTWARD (not receipt)
        if tc is None: continue
        if not set(rec.get("witness_refs", [])) >= set(tc["required_witnesses"]): continue  # witnesses ⊨ TRUSTED contract
        if rec.get("verification") != tc["verification_policy"]: continue                  # against TRUSTED policy
        if rec.get("policy_id") not in TRUSTED_POLICY: continue
        if grant["scope"] != "admit" or rec["task_id"] not in grant["tasks"]: continue     # grant authorizes THIS task
        valid[rh] = (rec, grant)
    state = {}   # task_id → {current, lineage[]}
    for e in events:
        if e["kind"] != "ADMITTED": continue
        rh, tid = e["payload"]["receipt_hash"], e["payload"]["task_id"]
        if rh not in valid: continue
        rec, grant = valid[rh]
        sup = rec.get("supersedes")
        if tid not in state:
            if sup is not None: continue                      # cannot supersede a non-existent admission
            state[tid] = {"current": rh, "lineage": [rh]}
        else:
            if sup != state[tid]["current"]: continue         # must supersede the CURRENT admission
            if not grant["may_supersede"]: continue           # supersession needs a grant that authorizes it
            state[tid]["current"] = rh; state[tid]["lineage"].append(rh)   # APPEND — prior NEVER erased
    return state

def main():
    print("=== TRUSTED_CONTRACT_BINDING_V0 — reducer resolves trust OUTWARD ===\n")
    T = good_task()
    ART = [a["hash"] for a in execute(T, T["requested_effects"])["artifacts"]]
    rows = []

    # M+ positive control: task-bound contract + valid grant + valid witnesses → FOLD
    Lp = Ledger(); dp = admit(T, "G-admit-1", "PASS", ["artifact_present", "peer_review"], ART, Lp)
    sp = reduce_tcb(Lp.events)
    rows.append(("M+ valid admission FOLDS", dp["done"] and sp.get("T-001", {}).get("current") == dp["receipt_hash"]))

    # M3 candidate invents WEAKER contract — irrelevant: reducer uses TRUSTED contract, witnesses insufficient → REJECT
    Lm3 = Ledger(); d3 = admit(T, "G-admit-1", "PASS", ["artifact_present"], ART, Lm3)   # only 1 of 2 required witnesses
    rows.append(("M3 weaker witnesses vs TRUSTED contract → REJECT", "T-001" not in reduce_tcb(Lm3.events)))

    # M4 authority_present without a valid grant → REJECT (grant_id unknown)
    Lm4 = Ledger(); d4 = admit(T, "G-DOES-NOT-EXIST", "PASS", ["artifact_present", "peer_review"], ART, Lm4)
    rows.append(("M4 admit with no valid grant → REJECT", (not d4["done"]) and "T-001" not in reduce_tcb(Lm4.events)))

    # M5 valid receipt rebound to another task → tag over task_id + grant.tasks scope breaks it
    Lm5 = Ledger(); dvalid = admit(T, "G-admit-1", "PASS", ["artifact_present", "peer_review"], ART, Lm5)
    rec = [e for e in Lm5.events if e["kind"] == "RECEIPT"][0]["payload"]["receipt"]
    forged = dict(rec); forged["task_id"] = "T-OTHER"                                     # rebind
    frh = H(forged); Lm5.append("ADMITTED", {"task_id": "T-OTHER", "receipt_hash": frh})
    Lm5.append("RECEIPT", {"task_id": "T-OTHER", "receipt": forged, "receipt_hash": frh, "grant_tag": rec and [e for e in Lm5.events if e["kind"]=="RECEIPT"][0]["payload"]["grant_tag"]})
    rows.append(("M5 receipt rebound to other task → REJECT", "T-OTHER" not in reduce_tcb(Lm5.events)))

    # M6 later forged admission shadows existing → NO_STATE_CHANGE (prior preserved)
    Lm6 = Ledger(); dh = admit(T, "G-admit-1", "PASS", ["artifact_present", "peer_review"], ART, Lm6)   # honest
    fr = {"task_id": "T-001", "contract_ref": "T-001", "authority_grant_id": "G-supersede-1", "policy_id": "P0",
          "witness_refs": [], "artifact_hashes": [], "execution_ref": "x", "verification": "PASS", "supersedes": dh["receipt_hash"]}
    frh6 = H(fr); Lm6.append("ADMITTED", {"task_id": "T-001", "receipt_hash": frh6})
    Lm6.append("RECEIPT", {"task_id": "T-001", "receipt": fr, "receipt_hash": frh6, "grant_tag": "0" * 16})  # BAD tag (forger lacks grant key)
    s6 = reduce_tcb(Lm6.events)
    rows.append(("M6 forged supersession (bad tag) → prior preserved", s6["T-001"]["current"] == dh["receipt_hash"] and len(s6["T-001"]["lineage"]) == 1))

    # M7 VALID append-supersession: honest first, then a real G-supersede-1 admission → lineage grows, old kept
    Lm7 = Ledger(); d7a = admit(T, "G-admit-1", "PASS", ["artifact_present", "peer_review"], ART, Lm7)
    d7b = admit(T, "G-supersede-1", "PASS", ["artifact_present", "peer_review"], ART, Lm7, supersedes=d7a["receipt_hash"])
    s7 = reduce_tcb(Lm7.events)
    rows.append(("M7 valid append-supersession: lineage 2, old preserved",
                 s7["T-001"]["current"] == d7b["receipt_hash"] and s7["T-001"]["lineage"] == [d7a["receipt_hash"], d7b["receipt_hash"]]))

    print("  MUTANTS + CONTROLS:")
    allok = True
    for name, ok in rows:
        allok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n  ALL_PASS = {allok}")
    print("  Reducer resolves contract/authority/policy OUTWARD; supersession = APPEND (prior never erased).")
    print("  BOUNDARY: stores/keys in-process (modeled); full unforgeability needs process boundary (kernel_obligations_v2).")

    receipt = {"receipt": "TRUSTED_CONTRACT_BINDING_V0",
               "principle": "The claimant may reference the rule; it may not define the rule that judges it",
               "resolves_outward": ["TrustedContract(task_id)", "VerifiedAuthorityGrant(grant_id)", "TrustedPolicy(policy_id)"],
               "supersession": "append (roadmap): prior admission preserved in lineage; needs may_supersede grant",
               "mutants": {name: bool(ok) for name, ok in rows}, "all_pass": allok,
               "HONEST_BOUNDARY": "in-process stores/keys = modeled; full unforgeability = process boundary",
               "CONTROL_PLANE_EARNED": "reference-outward_pending_fresh_adversary" if allok else "HOLD",
               "SelfPassed": True, "PeerAdversaryValidated": False,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str); receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "trusted_contract_binding_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/trusted_contract_binding_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
