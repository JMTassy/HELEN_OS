"""COUNTERFACTUAL_ADMISSION_INVARIANCE_V0 — falsifiers. 🔵 OBSERVED.

THE CLAIM under test: a governed verdict is presentation-conservative (ISR=1.0 under representation-only
transforms) AND evidence-responsive (a new independent witness may move it). The positive control is a
CAPTURED verdict that leaks persuasion — CAI must catch it, else the whole test is vacuous.
"""
from helen_os.audit.counterfactual_admission_invariance import (
    ADMIT, HOLD, REPRESENTATION_TRANSFORMS,
    build_fixtures, cai_check, gamma_captured, gamma_governed,
    inject_dependent_restatement, inject_independent_witness, invariance_survival_rate,
)

FIXTURES = build_fixtures()


# ─────────── presentation-conservative: ISR = 1.0 for the governed verdict ───────────
def test_governed_verdict_is_invariant_under_all_representation_transforms():
    # 10 claims × 20 transforms = 200 adversarial evaluations, all must hold their verdict.
    assert invariance_survival_rate(FIXTURES, gamma_governed) == 1.0


def test_no_single_transform_captures_a_governed_verdict():
    for c in FIXTURES:
        r = cai_check(c, gamma_governed)
        assert r.isr == 1.0 and not r.semantic_capture, f"captured by {r.captured_by}"


def test_persuasion_cannot_promote_a_hold_claim():
    hold_claim = FIXTURES[0]                       # single root → HOLD
    assert gamma_governed(hold_claim) == HOLD
    for _, T in REPRESENTATION_TRANSFORMS:         # prestige, 1000-agent consensus, cosmic myth, …
        assert gamma_governed(T(hold_claim)) == HOLD


# ─────────── positive control: CAI catches a captured verdict (has teeth) ───────────
def test_captured_verdict_is_detected_as_semantic_capture():
    hold_claim = FIXTURES[0]
    r = cai_check(hold_claim, gamma_captured)
    assert r.semantic_capture                      # FAIL_SEMANTIC_CAPTURE
    assert r.isr < 1.0
    # the specific persuasion knobs that flipped it are named
    assert "agent_consensus_20" in r.captured_by and "prestige_max" in r.captured_by


def test_captured_verdict_lowers_aggregate_isr():
    assert invariance_survival_rate(FIXTURES, gamma_captured) < 1.0


# ─────────── evidence-responsive: a real witness MAY move the verdict ───────────
def test_independent_witness_promotes_hold_to_admit():
    hold_claim = FIXTURES[0]                       # n_epi = 1 → HOLD
    assert gamma_governed(hold_claim) == HOLD
    promoted = inject_independent_witness(hold_claim, root="src-INDEP")
    assert gamma_governed(promoted) == ADMIT       # n_epi = 2 → ADMIT (evidence-responsive)


def test_dependent_restatement_does_not_promote():
    # a restatement sharing the existing root is representation fan-out, NOT new evidence.
    hold_claim = FIXTURES[0]
    same_root = hold_claim.warrant[0].root
    still_hold = inject_dependent_restatement(hold_claim, of_root=same_root)
    assert gamma_governed(still_hold) == HOLD       # n_epi still 1


# ─────────── non-triviality: the governed verdict is not a constant ───────────
def test_governed_verdict_is_not_trivially_constant():
    verdicts = {gamma_governed(c) for c in FIXTURES}
    assert verdicts == {ADMIT, HOLD}                # both occur → conservatism isn't achieved by always-HOLD
