"""Stack-up and ancestry, falsified: six locally certified stages
compose past the budget; five witnesses with one ancestor are one
observation; sqrt-N is earned by ancestry classes, not head-count;
shared ancestry is ill-conditioning; Garden selects by information
gain, not failure count.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import stack_up as su
from stack_up import (
    ancestry_kappa,
    canonical_stack_up,
    condition_number,
    consensus_audit,
    decision_risk,
    garden_consensus_attack,
    information_gain_target,
    propagate_margin,
    propagate_uncertainty,
    trace_budget,
)


# ── the trace budget: the Garden target, constructed ───────────────────

def test_the_canonical_pipeline_stacks_up_past_the_budget():
    v = canonical_stack_up()
    assert v["locally_certified"] is True      # every eps_i <= b_i
    assert v["B_tau"] == 0.9 and v["B_max"] == 0.5
    assert v["stack_up_gap"] is True           # the target: both hold
    assert v["stages"] == su.CANONICAL_PIPELINE


def test_no_gap_when_the_budget_holds():
    steps = tuple({"stage": s, "eps": 0.05, "bound": 0.2}
                  for s in su.CANONICAL_PIPELINE)
    v = trace_budget(steps, b_max=0.5)
    assert v["stack_up_gap"] is False
    assert v["budget_exceeded"] is False


def test_a_locally_failing_step_is_not_a_stack_up_gap():
    """The gap is specifically: all locally fine AND terminal bad."""
    steps = ({"stage": "source", "eps": 0.9, "bound": 0.2},)
    v = trace_budget(steps, b_max=0.5)
    assert v["locally_certified"] is False
    assert v["stack_up_gap"] is False


def test_margin_propagation_local_positive_composed_nonpositive():
    v = propagate_margin((1.0, 1.0, 1.0), (0.4, 0.4, 0.4))
    assert v["all_locally_positive"] is True
    assert v["mu_tau"] <= 0
    assert v["composed_positive"] is False
    assert v["phi_status"] == "MODEL_CALIBRATION_PENDING"


def test_misaligned_trace_is_refused():
    with pytest.raises(ValueError, match="E_MISALIGNED_TRACE"):
        propagate_margin((1.0,), (0.1, 0.2))


# ── ancestry: the measurable primitive first ────────────────────────────

def test_kappa_is_jaccard_over_ancestor_sets():
    same = ancestry_kappa(frozenset({"S0"}), frozenset({"S0"}))
    disjoint = ancestry_kappa(frozenset({"S0"}), frozenset({"S1"}))
    partial = ancestry_kappa(frozenset({"S0", "S1"}),
                             frozenset({"S1", "S2"}))
    assert same["kappa"] == 1.0
    assert disjoint["kappa"] == 0.0
    assert partial["kappa"] == round(1 / 3, 6)


def test_n_effective_is_deliberately_not_minted():
    v = ancestry_kappa(frozenset({"S0"}), frozenset({"S0"}))
    assert v["n_effective"] is None
    assert "independence is subtle" in v["n_effective_note"]


def test_unknown_ancestry_is_refused_not_defaulted():
    with pytest.raises(ValueError, match="E_ANCESTRY_UNKNOWN"):
        ancestry_kappa(frozenset(), frozenset({"S0"}))


def test_five_witnesses_one_ancestor_is_one_observation():
    v = garden_consensus_attack()
    assert v["apparent_consensus"] == 5
    assert v["ancestry_classes"] == 1
    assert v["mean_pairwise_kappa"] == 1.0
    assert v["attack_succeeds_against_vote_counting"] is True
    assert v["witness_count_is_evidence_strength"] is False


def test_independent_witnesses_are_counted_as_classes():
    ws = ({"id": "W1", "ancestors": frozenset({"S0"})},
          {"id": "W2", "ancestors": frozenset({"S1"})},
          {"id": "W3", "ancestors": frozenset({"S2"})})
    v = consensus_audit(ws)
    assert v["ancestry_classes"] == 3
    assert v["mean_pairwise_kappa"] == 0.0


# ── uncertainty propagation under common mode ──────────────────────────

def test_sqrt_n_is_earned_by_ancestry_not_head_count():
    shared = tuple({"id": f"W{i}", "ancestors": frozenset({"S0"})}
                   for i in range(5))
    indep = tuple({"id": f"W{i}", "ancestors": frozenset({f"S{i}"})}
                  for i in range(5))
    vs = propagate_uncertainty(1.0, shared)
    vi = propagate_uncertainty(1.0, indep)
    assert vs["u_tau"] == 1.0                  # full common mode
    assert vs["sqrt_n_earned"] is False
    assert vi["u_tau"] == round(1.0 / 5 ** 0.5, 6)
    assert vi["sqrt_n_earned"] is True
    assert "provenance topology matters" in vs["law"]


# ── the epistemic condition number ──────────────────────────────────────

def test_shared_ancestry_is_ill_conditioning():
    fanned = condition_number({"r1": "S0", "r2": "S0", "r3": "S0",
                               "r4": "S0", "r5": "S0"})
    spread = condition_number({"r1": "S0", "r2": "S1", "r3": "S2"})
    assert fanned["kappa_C"] == 5
    assert fanned["worst_ancestor"] == "S0"
    assert fanned["well_conditioned"] is False
    assert spread["kappa_C"] == 1
    assert spread["well_conditioned"] is True


def test_no_evidence_is_refused():
    with pytest.raises(ValueError, match="E_NO_EVIDENCE"):
        condition_number({})


def test_decision_risk_separates_instrument_from_conditioning():
    """A near-perfect verifier on an ill-conditioned problem carries
    more risk than a coarse one on a well-conditioned problem: u has
    a floor, kappa dominates."""
    sharp_ill = decision_risk(0.0, kappa_c=1000)
    coarse_well = decision_risk(0.01, kappa_c=1)
    assert sharp_ill["u_I"] == su.U_FLOOR       # never exactly zero
    assert sharp_ill["risk"] > 0
    assert sharp_ill["verifier_quality_sufficient"] is False
    assert coarse_well["risk"] == 0.01
    assert "not verifier quality" in sharp_ill["law"]


# ── Garden's identity, upgraded ─────────────────────────────────────────

def test_garden_selects_by_information_gain_not_failure_count():
    cands = ({"trace_id": "boundary_probe", "expected_dH": 3.2},
             {"trace_id": "redundant_far_field", "expected_dH": 0.01},
             {"trace_id": "likely_fail_but_known", "expected_dH": 0.2})
    v = information_gain_target(cands)
    assert v["selected"] == "boundary_probe"
    assert v["identity"] == ("adaptive experimental design over the "
                             "constitutional failure surface")


def test_no_candidates_is_refused():
    with pytest.raises(ValueError, match="E_NO_CANDIDATES"):
        information_gain_target(())


def test_deterministic():
    assert su.canon(canonical_stack_up()) == \
        su.canon(canonical_stack_up())
    assert su.canon(garden_consensus_attack()) == \
        su.canon(garden_consensus_attack())
