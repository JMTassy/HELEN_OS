"""K0 PROPERTY TEST — the real K0 falsifier. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Property: ∂GateDecision/∂CandidateAuthorityAssertions = 0. Concretely: starting from a base packet with G=NO,
mutate EVERY candidate-controlled field one at a time; if ANY single mutation flips NO→YES without a corresponding
change in an independently verified fact, that field is a SELF-CERTIFICATION bypass and the gate is FALSIFIED.
CandidateClaim(P) ⊬ Verified(P).
"""
import copy
from fable_binary_gate_v0 import GatePacket, fable_gate as gate_v0
from fable_binary_gate_v1 import GatePacketV1, fable_gate_v1, issue_verified_packet

def fuzz_v0():
    """Single-defect method: start from a VALID (YES) packet, break exactly one field (→NO), then flip ONLY that
    field back to a candidate-favorable value. If it reaches YES, that field is candidate-controlled verdict truth."""
    valid = GatePacket(task_hash="t", corpus_hash="c", her_status="ok", goblin_complete=True, hal_status="SURVIVED",
                       falsifier_result="SURVIVED", evidence_roots=2, hard_gates=[True, True])
    assert gate_v0(valid)[0] == "YES"
    no_val = {"goblin_complete": False, "hal_status": "INCONCLUSIVE", "evidence_roots": 0, "authority_delta": 1,
              "state_delta": 1, "scope_delta": 1, "unknown_unresolved": True, "hard_gates": [True, False]}
    yes_val = {"goblin_complete": True, "hal_status": "SURVIVED", "evidence_roots": 2, "authority_delta": 0,
               "state_delta": 0, "scope_delta": 0, "unknown_unresolved": False, "hard_gates": [True, True]}
    self_cert = []
    for f, nv in no_val.items():
        base = copy.deepcopy(valid); setattr(base, f, nv)
        if gate_v0(base)[0] != "NO": continue
        m = copy.deepcopy(base); setattr(m, f, yes_val[f])
        if gate_v0(m)[0] == "YES":
            self_cert.append(f)                       # candidate flips this field NO→YES
    # authority bypass: operator_witness on an authority-expansion packet
    base = copy.deepcopy(valid); base.authority_delta = 1
    if gate_v0(base)[0] == "NO" and gate_v0(GatePacket(**{**base.__dict__, "operator_witness": True}))[0] == "YES":
        self_cert.append("operator_witness")
    return sorted(self_cert)

def fuzz_v1():
    """v1: candidate fields are hash + opaque verifier receipts. Try to reach YES by mutating ANY packet field to a
    candidate-favorable value (forged receipts, 'PASS', 'true', etc.). None can produce a valid receipt."""
    base = GatePacketV1(candidate_hash="H1", decision_requested="PROMOTE")     # empty receipts ⇒ NO
    assert fable_gate_v1(base)[0] == "NO"
    favor = ["PASS", "true", "YES", "1", "ff" * 32, "H1", "authorized"]
    flips = []
    for f in ("candidate_hash", "execution_receipt", "epistemic_receipt", "permission_receipt", "decision_requested", "unresolved"):
        for v in favor + [["x"], []]:
            m = copy.deepcopy(base); setattr(m, f, v)
            if fable_gate_v1(m)[0] == "YES":
                flips.append((f, repr(v)))
    # also: set ALL three receipts to the same forged value at once (still can't verify)
    m = GatePacketV1(candidate_hash="H1", execution_receipt="ff" * 32, epistemic_receipt="ff" * 32, permission_receipt="ff" * 32)
    if fable_gate_v1(m)[0] == "YES": flips.append(("all_receipts_forged", "ff*32"))
    return sorted({f for f, _ in flips})

    # v1 liveness: a legitimately VERIFIED packet must still reach YES
    live = fable_gate_v1(issue_verified_packet("H1", exec_ok=True, epi_ok=True, perm_ok=True))
    # v1 negative: forge a receipt string (candidate can't) — must stay NO
    forged = fable_gate_v1(GatePacketV1(candidate_hash="H1", execution_receipt="ff"*32,
                                        epistemic_receipt="ff"*32, permission_receipt="ff"*32))

    print("\n=== RESULT ===")
    print(f"  v0 gate: {v0_verdict}  (self-certifying fields: {v0_fields})")
    print(f"  v1 gate: {v1_verdict}")
    print(f"  v1 liveness (real verifier receipts): {live}  (must be YES)")
    print(f"  v1 forged receipts: {forged}  (must be NO)")
    print(f"  EMERGENT INVARIANT: CandidateClaim(P) ⊬ Verified(P) — v0 violates it broadly; v1 upholds it vs packet mutation")
    print(f"  HONEST BOUND: v1 verifier mints are in-process globals → full isolation needs the kernel-v2 process boundary")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()
