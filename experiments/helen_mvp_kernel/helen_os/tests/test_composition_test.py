"""COMPOSITION_TEST_V0 — asymmetric-compositionality falsifiers. 🔵 OBSERVED.

THE CLAIM: capability composes (∂Q/∂N>0) while authority and evidence do NOT (∂A/∂N=0, ∂ρ_E/∂N=0
without new roots), until a typed witness crosses Γ. The frozen predicate PASS ⟺ C_Q∧C_P∧C_A∧C_G∧C_R.
The suite proves both that the real experiment PASSES and that each failure code can FIRE (the
falsifier is not vacuous — a broken world is detected).
"""
from helen_os.audit.composition_test import (
    FAIL_AUTHORITY_AMPLIFICATION, FAIL_CAPABILITY_COMPOSITION, FAIL_CONSENSUS_LAUNDERING,
    FAIL_PROVENANCE_FANOUT, FAIL_REPLAY, FAIL_WITNESS_INSENSITIVITY,
    Metrics, TARGET, authority, authority_probe, build_hierarchy, capability, evaluate,
    independent_roots, passed, provenance_probe, replay_probe, run_composition_test, solved,
)

M = run_composition_test()


# ─────────── the whole experiment passes ───────────
def test_composition_test_v0_passes():
    assert passed(M), evaluate(M)
    assert evaluate(M) == ()


# ─────────── C_Q: capability composes (∂Q/∂N > 0) ───────────
def test_capability_strictly_increases_across_hierarchy():
    assert M.capability_series == (0.20, 0.40, 0.80, 1.00)
    assert all(b > a for a, b in zip(M.capability_series, M.capability_series[1:]))


def test_composition_beats_the_best_atom():
    levels = build_hierarchy()
    best_atom_q = capability(levels[0], TARGET)          # a single worker
    superteam_q = capability(levels[2], TARGET)
    assert superteam_q > best_atom_q                     # the LEGO thesis: teams beat atoms


# ─────────── C_A: authority does NOT compose ───────────
def test_authority_is_zero_at_every_hierarchy_level():
    assert M.authority_series == (0, 0, 0, 0)
    for s in build_hierarchy():
        assert authority(s) == 0                         # ∂A/∂N = 0 — no worker path mints authority


# ─────────── C_G + positive control: consensus ⊬ admit, but a witness does ───────────
def test_unanimous_unauthorized_consensus_is_rejected():
    unauthorized, _ = authority_probe()
    assert unauthorized is False                         # 1000 unanimous YES votes → still not admitted


def test_valid_typed_witness_admits_change_attributed_to_W_A():
    # ΔAdmission ← ΔW_A: everything else held fixed, only the authority witness changed.
    unauthorized, authorized = authority_probe()
    assert unauthorized is False and authorized is True


# ─────────── C_P: provenance does not fan out, but responds to a real root ───────────
def test_provenance_conservation_and_responsiveness():
    same, two = provenance_probe()
    assert same == 1                                     # 100 endorsers of one source = one root
    assert two == 2                                      # one genuinely independent source = two roots


def test_worker_fanout_does_not_multiply_roots():
    # a superteam of 5 atoms all endorsing "r1" still has |ρ_E| = 1
    assert independent_roots(build_hierarchy()[3]) == 1


# ─────────── C_R: replay reconstructs the admitted state ───────────
def test_replay_equivalence():
    assert replay_probe() is True


# ─────────── the falsifier has teeth: every failure code can fire ───────────
def test_every_failure_code_is_reachable():
    base = dict(capability_series=(0.2, 0.4, 0.8, 1.0), authority_series=(0, 0, 0, 0),
                roots_same_source=1, roots_after_independent=2,
                unauthorized_admit=False, authorized_admit=True, replay_matches=True)
    assert evaluate(Metrics(**base)) == ()                                  # the healthy world passes
    assert FAIL_CAPABILITY_COMPOSITION in evaluate(Metrics(**{**base, "capability_series": (0.4, 0.4, 0.4, 0.4)}))
    assert FAIL_PROVENANCE_FANOUT in evaluate(Metrics(**{**base, "roots_same_source": 100}))
    assert FAIL_AUTHORITY_AMPLIFICATION in evaluate(Metrics(**{**base, "authority_series": (0, 0, 1, 1)}))
    assert FAIL_CONSENSUS_LAUNDERING in evaluate(Metrics(**{**base, "unauthorized_admit": True}))
    assert FAIL_WITNESS_INSENSITIVITY in evaluate(Metrics(**{**base, "authorized_admit": False}))
    assert FAIL_REPLAY in evaluate(Metrics(**{**base, "replay_matches": False}))
