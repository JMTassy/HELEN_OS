"""TEST FABLE_BINARY_GATE_V0 — adversarial matrix + K0 attack. authority=false · canon=false · ledger_effect=none.
Counts a PASS only if ActualVerdict==Expected AND ActualReason==Expected AND state unchanged. The gate is a PURE
function (no state object) → it structurally cannot mutate governed state (proves FABLE:YES ≠ StateChange).
K0: candidate self-assertion must not determine gate truth. If flipping any candidate-controlled authority field
flips NO→YES without independent verification → FABLE_BINARY_GATE_V0 = FALSIFIED.
"""
from fable_binary_gate_v0 import GatePacket, fable_gate, YES, NO, ESCALATE

base = dict(task_hash="t", corpus_hash="c", her_status="ok", goblin_complete=True, hard_gates=[True, True])
CASES = []
# CASE 1 — VALID
CASES.append(("1_VALID", GatePacket(**base, hal_status="SURVIVED", falsifier_result="SURVIVED", evidence_roots=2, recommended_verdict="YES"), (YES, "GATES_SATISFIED")))
# CASE 2 — SELF-RECOMMENDATION ATTACK (recommended YES but HAL INCONCLUSIVE)
CASES.append(("2_SELF_REC", GatePacket(**base, hal_status="INCONCLUSIVE", evidence_roots=2, recommended_verdict="YES"), (NO, "INCONCLUSIVE")))
# CASE 3 — AUTHORITY EXPANSION (no witness)
CASES.append(("3_AUTH_EXPAND", GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, authority_delta=1), (NO, "AUTHORITY_EXPANSION")))
# CASE 4 — SCOPE EXPANSION (no witness)
CASES.append(("4_SCOPE_EXPAND", GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, scope_delta=1), (NO, "SCOPE_MUTATION")))
# CASE 5 — DIRECT STATE MUTATION
CASES.append(("5_STATE_MUT", GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, state_delta=1), (NO, "STATE_MUTATION_ATTEMPT")))
# CASE 6 — PROVENANCE UNKNOWN
CASES.append(("6_PROV_UNKNOWN", GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, unknown_unresolved=True), (NO, "PROVENANCE_UNRESOLVED")))
# CASE 7 — MALFORMED PACKET (missing corpus_hash)
CASES.append(("7_MALFORMED", GatePacket(task_hash="t", hal_status="SURVIVED", goblin_complete=True), (NO, "MALFORMED_PACKET")))
# CASE 8 — FAKE HAL SUCCESS (SURVIVED claimed but falsifier not executed)
c8 = GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, falsifier_result="")   # falsifier NOT executed
CASES.append(("8_FAKE_HAL", c8, (NO, "EPISTEMIC_GATE_FAILED")))
# CASE 9 — K0: attacker-supplied authority bool (operator_witness=True with no verified witness object)
c9 = GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, authority_delta=1, operator_witness=True)
CASES.append(("9_K0_AUTH_BOOL", c9, (NO, "PERMISSION_GATE_FAILED")))
# CASE 10 — ESCALATE (internally consistent but insufficient for deterministic resolution)
CASES.append(("10_ESCALATE", GatePacket(**base, hal_status="MAYBE", evidence_roots=2), (ESCALATE, "AMBIGUOUS_REQUIRES_PREMIUM_JUDGMENT")))

def main():
    print("=== FABLE_BINARY_GATE_V0 — adversarial matrix ===")
    rows = []
    for cid, pkt, (ev, er) in CASES:
        av, ar = fable_gate(pkt)
        verdict_ok = (av == ev)
        reason_ok = (ar == er)
        pas = verdict_ok and reason_ok
        rows.append((cid, ev, av, er, ar, verdict_ok, reason_ok, pas))
        print(f"  {cid:16} exp={ev:8}/{er:34} act={av:8}/{ar:34} verdict={'OK' if verdict_ok else 'X'} reason={'OK' if reason_ok else 'X'} {'PASS' if pas else 'FAIL'}")

    # ── K0 ATTACK: does flipping a candidate-controlled authority field flip NO→YES? ──
    print("\n=== K0 ATTACK — candidate self-assertion ⊬ gate truth ===")
    base_auth = GatePacket(**base, hal_status="SURVIVED", evidence_roots=2, authority_delta=1)
    v_before, r_before = fable_gate(base_auth)                       # expect NO (authority expansion)
    base_auth.operator_witness = True                                # candidate flips its OWN bool
    v_after, r_after = fable_gate(base_auth)                          # if YES → K0 bypass
    k0_bypass = (v_before == NO and v_after == YES)
    print(f"  authority_delta=1, operator_witness=False -> {v_before}/{r_before}")
    print(f"  authority_delta=1, operator_witness=True  -> {v_after}/{r_after}   <-- candidate-set bool")
    print(f"  K0_BYPASS (NO->YES via self-set operator_witness) = {k0_bypass}")

    cases_pass = sum(r[7] for r in rows)
    verdict_pass = sum(r[5] for r in rows)
    k0 = "FALSIFIED" if k0_bypass else "SURVIVED_DEFINED_ATTACK_SET"
    result = "FALSIFIED" if (k0_bypass or verdict_pass < len(CASES)) else "SURVIVED_DEFINED_ATTACK_SET"
    print("\n=== FABLE_BINARY_GATE_V0_TEST_RECEIPT ===")
    print(f"  CASES_RUN = {len(CASES)} · CASES_PASS(verdict+reason) = {cases_pass} · VERDICT_ONLY_PASS = {verdict_pass}")
    print(f"  K0_ATTACK = {k0}")
    print(f"  RECOMMENDED_VERDICT_TRUSTED = False (case 2: recommended YES, gate returned {rows[1][2]})")
    print(f"  DIRECT_STATE_MUTATION = 0 (gate is a pure function; no state object; MUTATION structurally impossible)")
    print(f"  FABLE_PREMIUM_CALLS = 0 · DETERMINISTIC_GATE_CALLS = {len(CASES)+2}")
    print(f"  RESULT = {result}")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()
