"""NIM_V0.1_WITNESS_FRAME_ORACLE — kill-test suite. 🔵 OBSERVED.

Acceptance = R = (K_F, K_W, K_D, K_C, K_O, K_S, K_P, K_R) = (1,…,1) with every denominator > 0.
Each family is a NON-EMPTY frozen mutation corpus; the positive controls must survive (no deny-all);
observer adequacy carries a blind-observer teeth control. PASS means: every preregistered mutant in the
finite declared corpus was killed and every positive control survived — nothing stronger.
"""
from helen_os.audit.nim_v0_1 import (
    ADMIT, REJECT, Capability, ProtectionContract, RootWitness, Transition,
    admit, blind_contract, default_contracts, observer_family, observer_sees,
    run_receipt, replay, zero_state,
)

S0 = zero_state()

# ── baselines (positive controls) ──
T_CAP = Transition("cap", licensed_frame=frozenset({"Q"}), writes={"Q": 1})
T_AUTH = Transition(
    "auth", licensed_frame=frozenset({"A"}), writes={"A": 1}, op="grant", object="obj1",
    capability=Capability("a", "grant", "obj1", frozenset({"obj1"})), proposer="p", authorizer="a")


def _verdict(t):
    return admit(t, S0)[0]


# ─────────── POSITIVE control (K_P) — the seam admits legitimate transitions ───────────
def test_positive_controls_admit():
    assert _verdict(T_CAP) == ADMIT
    assert _verdict(T_AUTH) == ADMIT


# ─────────── FRAME family (K_F) — a write outside L(T) is rejected ───────────
FRAME_MUTANTS = [
    Transition("f_cap_A", frozenset({"Q"}), {"Q": 1, "A": 1}, proposer="p", authorizer="a"),  # A ∉ L
    Transition("f_auth_X", frozenset({"A"}), {"A": 1, "X": 1}, op="grant", object="obj1",
               capability=Capability("a", "grant", "obj1", frozenset({"obj1"})), proposer="p", authorizer="a"),  # X ∉ L
]

def test_frame_violations_killed():
    assert len(FRAME_MUTANTS) > 0
    for m in FRAME_MUTANTS:
        v, why = admit(m, S0)
        assert v == REJECT and why == "FRAME_VIOLATION", (m.id, why)


# ─────────── WITNESS family (K_W) — obligation must be discharged by an APPLICABLE witness ───────────
def _auth_with(cap):
    return replace_cap(T_AUTH, cap)

def replace_cap(t, cap):
    from dataclasses import replace
    return replace(t, capability=cap, id=t.id + "_w")

WITNESS_MUTANTS = [
    replace_cap(T_AUTH, None),                                                          # missing
    replace_cap(T_AUTH, Capability("a", "grant", "obj1", frozenset({"obj1"}), fresh=False)),  # stale
    replace_cap(T_AUTH, Capability("a", "grant", "other", frozenset({"other"}))),       # wrong object
    replace_cap(T_AUTH, Capability("a", "read", "obj1", frozenset({"obj1"}))),          # wrong operation
]

def test_witness_defects_killed():
    assert len(WITNESS_MUTANTS) > 0
    for m in WITNESS_MUTANTS:
        v, why = admit(m, S0)
        assert v == REJECT and why == "OBLIGATION_NOT_DISCHARGED", (m.id, why)


# ─────────── DUTY family (K_D) — separation of duty on sensitive writes ───────────
DUTY_MUTANTS = [
    Transition("d_collapse", frozenset({"A"}), {"A": 1}, op="grant", object="obj1",
               capability=Capability("a", "grant", "obj1", frozenset({"obj1"})),
               proposer="same", authorizer="same"),  # proposer == authorizer
]

def test_sod_violations_killed():
    assert len(DUTY_MUTANTS) > 0
    for m in DUTY_MUTANTS:
        v, why = admit(m, S0)
        assert v == REJECT and why == "SOD_VIOLATION", (m.id, why)


# ─────────── DEPUTY family (K_C) — authentic authority, inapplicable scope ───────────
DEPUTY_MUTANTS = [
    # capability genuinely names grant on obj1, but its SCOPE excludes obj1 (authentic ⊬ applicable)
    Transition("dep_scope", frozenset({"A"}), {"A": 1}, op="grant", object="obj1",
               capability=Capability("a", "grant", "obj1", frozenset({"sandbox"})),
               proposer="p", authorizer="a"),
]

def test_confused_deputy_killed():
    assert len(DEPUTY_MUTANTS) > 0
    for m in DEPUTY_MUTANTS:
        v, why = admit(m, S0)
        assert v == REJECT and why == "OBLIGATION_NOT_DISCHARGED", (m.id, why)


# ─────────── OBSERVER family (K_O) — substitution rejected + adequacy with blind-observer teeth ───────────
def test_observer_substitution_is_rejected():
    # weaken the A-observer AND perform a forbidden A write in one transition, no contract authority
    attack = Transition("obs_sub", frozenset({"Q"}), {"Q": 1, "A": 1},
                        contract_override={"A": blind_contract("A")}, has_contract_authority=False)
    v, why = admit(attack, S0)
    assert v == REJECT and why == "OBSERVER_SUBSTITUTION_UNLICENSED"


def test_observer_adequacy_and_blind_teeth():
    contracts = default_contracts()
    # every default observer must DISTINGUISH a forbidden mutation of its own coordinate
    for c in ("A", "RHO_E", "X", "E"):
        mutate = (lambda s, c=c: {**dict(s), c: s[c] + 1})
        assert observer_sees(contracts[c], S0, mutate) is True
    # teeth: a BLIND observer fails to see the same mutation → OKR would catch it (metric non-vacuous)
    blind = blind_contract("A")
    assert observer_sees(blind, S0, lambda s: {**dict(s), "A": s["A"] + 1}) is False


# ─────────── SEMANTIC family (K_S / AIR) — presentation must not change disposition ───────────
def test_presentation_does_not_change_disposition():
    from dataclasses import replace
    for pres in ("plain", "prestige", "cosmic", "urgent", "humble"):
        assert admit(replace(T_CAP, presentation=pres), S0)[0] == ADMIT      # admitted stays admitted
        assert admit(replace(FRAME_MUTANTS[0], presentation=pres), S0)[0] == REJECT  # rejected stays rejected


# ─────────── REPLAY family (K_R) — admitted transitions reconstruct the state ───────────
def test_replay_reconstructs_admitted_state():
    admitted = [T_CAP, T_AUTH]
    assert all(admit(t, S0)[0] == ADMIT for t in admitted)
    reconstructed = replay(S0, admitted)
    assert reconstructed["Q"] == 1 and reconstructed["A"] == 1


# ─────────── the acceptance vector R = (1,…,1), denominators recorded ───────────
def test_acceptance_vector_all_ones_nonempty():
    def kr(mutants, expected_reason=None):
        assert len(mutants) > 0
        killed = 0
        for m in mutants:
            v, why = admit(m, S0)
            if v == REJECT and (expected_reason is None or why == expected_reason):
                killed += 1
        return killed, len(mutants)

    K_F = kr(FRAME_MUTANTS, "FRAME_VIOLATION")
    K_W = kr(WITNESS_MUTANTS, "OBLIGATION_NOT_DISCHARGED")
    K_D = kr(DUTY_MUTANTS, "SOD_VIOLATION")
    K_C = kr(DEPUTY_MUTANTS, "OBLIGATION_NOT_DISCHARGED")
    K_P = (sum(admit(t, S0)[0] == ADMIT for t in (T_CAP, T_AUTH)), 2)
    R = [K_F, K_W, K_D, K_C, K_P]
    # every family non-empty AND fully satisfied (numerator == denominator)
    assert all(den > 0 and num == den for (num, den) in R), R


# ─────────── the ESSENTIAL teeth: a coarse observer must actually let a forbidden write ESCAPE ───────────
def test_coarse_observer_escape_teeth():
    # strict observer BLOCKS the forbidden A-write; the SAME write ESCAPES under a blind observer —
    # proving the blind observer is genuinely dangerous (the teeth actually bite); and installing the
    # blind observer is itself barred (reflexive-substitution defense).
    obs = observer_family()
    assert obs["strict"] == REJECT           # strict blocks
    assert obs["coarse_escape"] == ADMIT     # blind lets it escape → the danger is real, not hypothetical
    assert obs["substitution"] == REJECT     # worker cannot install the blind observer
    assert obs["blind_control_triggered"] is True and obs["adequacy"] is True
    assert obs["killed"] == 1


# ─────────── the full 8-component acceptance vector R = (1,…,1), families non-empty ───────────
def test_full_acceptance_vector():
    r = run_receipt()
    assert r["acceptance_vector"] == (1, 1, 1, 1, 1, 1, 1, 1)
    assert r["accepted"] is True
    # every family denominator > 0 (no vacuous 0/0), survivors empty where applicable
    for fam in ("FRAME", "WITNESS", "DUTY", "DEPUTY"):
        killed, total, survivors = r[fam]
        assert total > 0 and killed == total and survivors == []
    assert r["POSITIVE"][1] > 0 and r["STR"][1] > 0 and r["REPLAY"] == (1, 1)
