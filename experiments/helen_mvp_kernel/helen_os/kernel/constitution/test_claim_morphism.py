"""Valid evidence is not relevant warrant; a simulation is not a
witness; representations multiplied without roots move no frontier;
an acoustic proof moves only the acoustic frontier; conditions and
time do not transfer; the frontier is a product never a scalar; nulls
move a negative frontier bounded by (delta, theta); replication
carries a vector and mints no truth; and the system must be
conservative under representation AND responsive under evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import claim_morphism as cm
from claim_morphism import (
    compiler_path,
    condition_conservation,
    domain_conservation,
    evidence_conservation,
    evidence_promotion,
    frontier_product,
    metamorphic_falsifier,
    negative_frontier,
    promote_claim,
    promotion_pressure,
    qualify,
    replication_independence,
    replication_mints,
    result_state,
    sacredness_regression,
    temporal_conservation,
)


def test_the_evidence_hierarchy_never_substitutes_upward():
    v = evidence_promotion("simulation", "measurement")
    assert v["licensed"] is False
    assert v["reason"] == "E_SIMULATION_IS_NOT_WITNESS"
    assert evidence_promotion("measurement", "replication")[
        "licensed"] is False
    assert evidence_promotion("replication", "measurement")[
        "licensed"] is True     # downward citation is fine


def test_valid_evidence_is_not_relevant_warrant():
    v = qualify("acoustic", "measurement", e_valid=True,
                claim_domain="biological")
    assert v["W"] == "IRRELEVANT"
    bridged = qualify("acoustic", "measurement", True, "biological",
                      bridge_licensed=True)
    assert bridged["W"] == "RELEVANT"
    assert qualify("acoustic", "measurement", False, "acoustic")[
        "W"] == "INVALID"
    assert qualify("acoustic", "simulation", True, "acoustic")[
        "W"] == "INSUFFICIENT"
    assert qualify("acoustic", "measurement", True, "acoustic",
                   contradicts=True)["W"] == "CONTRADICTORY"


def test_promotion_needs_relevant_plus_discharged():
    assert promote_claim("RELEVANT", True)["promoted"] is True
    hold = promote_claim("RELEVANT", False)
    assert hold["state"] == "HOLD"
    assert promote_claim("IRRELEVANT", True)["reason"] == \
        "E_EVIDENCE_IRRELEVANT"


def test_pseudoreplication_moves_no_frontier():
    v = evidence_conservation(("upscale", "vlm_pass", "llm_consensus",
                               "citation_copying"),
                              roots_before=1, roots_after=1,
                              frontier_moved=True)
    assert v["reason"] == "E_PSEUDOREPLICATION"
    ok = evidence_conservation(("paraphrase",), 1, 1,
                               frontier_moved=False)
    assert ok["ok"] is True and ok["frontier_may_move"] is False
    real = evidence_conservation((), 1, 2, frontier_moved=True)
    assert real["ok"] is True and real["frontier_may_move"] is True


def test_an_acoustic_proof_moves_only_the_acoustic_frontier():
    assert domain_conservation("acoustic", "acoustic")["ok"] is True
    v = domain_conservation("acoustic", "biological")
    assert v["reason"] == "E_DOMAIN_LAUNDERING"
    assert domain_conservation("acoustic", "biological",
                               crossing_discharged=True)["ok"] is True


def test_conditions_and_time_do_not_transfer():
    t1 = {"material": "A", "boundary": "B", "excitation": "f"}
    t2 = {"material": "C", "boundary": "D", "excitation": "f2"}
    assert condition_conservation(t1, dict(t1))["ok"] is True
    assert condition_conservation(t1, t2)["reason"] == \
        "E_CONDITION_LAUNDERING"
    assert temporal_conservation("2026", "1926")["reason"] == \
        "E_TEMPORAL_LAUNDERING"


def test_the_frontier_is_a_product_never_a_scalar():
    sg17 = {"symbolic": "SUPPORTED", "geometric": "PROVEN",
            "acoustic": "MEASURED", "biological": "UNWARRANTED",
            "energetic": "OPERATIONAL_DEFINITION_ABSENT"}
    v = frontier_product(sg17)
    assert v["ok"] is True and v["scalar"] is None
    assert frontier_product(sg17, collapse_to_scalar=True)[
        "reason"] == "E_SCALAR_FRONTIER"


def test_nulls_move_a_bounded_negative_frontier():
    v = negative_frontier(powered_nulls=3, delta=0.05,
                          theta="material=A")
    assert "EffectNotDetectedWithin" in v["licensed_statement"]
    assert v["forbidden_statement"] == "EffectDoesNotExist"
    assert result_state("NULL_EFFECT",
                        converted_from="MEASUREMENT_FAILURE")[
        "reason"] == "E_FAILURE_AS_NULL"


def test_sacredness_becomes_a_regression_variable():
    same = sacredness_regression(f_matched=True, s_differs=True,
                                 y_difference_robust=False)
    assert same["verdict"] == "NO_DETECTABLE_SACREDNESS_TERM"
    diff = sacredness_regression(True, True, True)
    assert diff["verdict"] == "RESIDUAL_DIFFERENCE_DETECTED"
    assert diff["never"] == "SACRED_POWER_PROVEN"
    assert sacredness_regression(False, True, True)["reason"] == \
        "E_UNMATCHED_CONTROLS"


def test_replication_is_a_vector_and_mints_no_truth():
    a = {d: "lab1" for d in cm.INDEPENDENCE_DIMS}
    b = dict(a, laboratory="lab2", operator="op2", sample="s2",
             funding="f2")
    v = replication_independence(a, b)
    assert v["fully_independent"] is False
    assert "instrument" in v["shared_dimensions"]
    assert 1 < v["n_eff"] < 2
    assert replication_mints(True, truth_claimed=True)["reason"] == \
        "E_REPLICATION_MINTS_TRUTH"


def test_promotion_pressure_is_adversarial_never_truth():
    v = promotion_pressure(0.9, 0.9, 0.9, 0.9, n_independent_roots=0)
    assert v["Pi_P"] == 3.6 and v["ideal_adversary"] is True
    assert v["truth_score"] is False
    assert promotion_pressure(1, 1, 1, 1, 1, used_as_truth=True)[
        "reason"] == "E_PRESSURE_IS_NOT_TRUTH"


def test_the_planes_talk_only_via_hypothesis_generation():
    assert compiler_path("symbolic", "physical_warrant")["reason"] == \
        "E_SYMBOLIC_WARRANT_PATH"
    assert compiler_path("symbolic", "physical_compiler",
                         via="hypothesis_generation")["ok"] is True
    assert compiler_path("symbolic", "physical_compiler",
                         via="vibes")["reason"] == \
        "E_SYMBOLIC_WARRANT_PATH"


def test_the_ultimate_falsifier_both_clauses_and_hold_to_everything():
    rep = metamorphic_falsifier(representation_delta=100,
                                independent_evidence_delta=0,
                                obligations_discharged=False,
                                frontier_delta=1)
    assert rep["reason"] == "E_REPRESENTATION_MOVED_FRONTIER"
    inert = metamorphic_falsifier(0, 1, True, 0)
    assert inert["reason"] == "E_UNRESPONSIVE_FRONTIER"
    launder = metamorphic_falsifier(0, 1, True, 1,
                                    evidence_domain="acoustic",
                                    moved_domain="biological")
    assert launder["reason"] == "E_DOMAIN_LAUNDERING"
    good = metamorphic_falsifier(100, 0, False, 0)
    assert good["conservative_under_representation"] is True
    responsive = metamorphic_falsifier(0, 1, True, 1,
                                       evidence_domain="acoustic",
                                       moved_domain="acoustic")
    assert responsive["responsive_under_evidence"] is True


def test_the_harmonic_crossing_contract_separates_three_frontiers():
    """PR #13's defect, now unrepresentable: simulation moving the
    hypothesis frontier is ALLOWED and is not a salience violation —
    while neither salience nor hypothesis motion ever moves the
    physical frontier."""
    from claim_morphism import harmonic_crossing
    # salience-only stack trying to promote physical -> FAIL
    v = harmonic_crossing(delta_R=6, delta_H=0, delta_P=1)
    assert v["verdict"] == "FAIL"
    assert v["reason"] == "E_SALIENCE_PROMOTED_PHYSICAL"
    # simulation moves hypothesis, physical untouched -> PASS
    sim = harmonic_crossing(delta_R=0, delta_H=1, delta_P=0)
    assert sim["verdict"] == "PASS"
    # hypothesis motion trying to ride into physical -> FAIL
    ride = harmonic_crossing(0, 1, 1)
    assert ride["reason"] == "E_HYPOTHESIS_PROMOTED_PHYSICAL"
    # a warranted physical promotion passes
    ok = harmonic_crossing(0, 0, 1, physical_warrant="receipt:bench")
    assert ok["verdict"] == "PASS" and ok["via"] == "physical_warrant"


def test_promotion_authority_never_scales_with_search():
    from claim_morphism import asymmetric_freedom
    wide = asymmetric_freedom(proposal_power_delta=100,
                              promotion_power_delta=0)
    assert wide["ok"] is True
    leak = asymmetric_freedom(100, promotion_power_delta=1)
    assert leak["reason"] == "E_PROMOTION_SCALES_WITH_SEARCH"


def test_a_loop_without_attack_before_gamma_is_confirmation_machinery():
    from claim_morphism import research_loop
    good = research_loop(("SEARCH", "SELF_CRITIQUE", "RED_TEAM",
                          "PROVENANCE_CHECK", "HELD_OUT_TEST",
                          "WITNESS_BUILD", "GAMMA"))
    assert good["licensed"] is True
    assert good["hold_is_success"] is True
    assert good["delta_authority_worker_loops"] == 0
    bad = research_loop(("GENERATE", "TEST", "INTERPRET", "GAMMA",
                         "UPDATE"))
    assert bad["reason"] == "E_NO_ATTACK_BEFORE_GAMMA"


def test_deterministic():
    assert cm.canon(promotion_pressure(1, 1, 1, 1, 0)) == \
        cm.canon(promotion_pressure(1, 1, 1, 1, 0))
