"""J3 harvest falsified: no amount without state+date+provenance and no
arrow skipped by narration; U_d checked before any probe budget; D_gov
refuses an unpinned coder; sunk cost cannot enter Delta V; the engine
refuses hindsight variables and slogans; and confirmations accumulate
without ever reinforcing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import decision_boundaries as db
from decision_boundaries import (
    baseline_moved,
    debt_negative_control,
    delta_v,
    engine_task,
    governance_debt,
    j4_cursor,
    promote_to_canon,
    qualify,
    reinforcement,
    state_transition,
    surface_point,
    typed_amount,
)


# ── typed commercial states ────────────────────────────────────────────

def test_the_seven_states_are_ordered_and_distinct():
    assert len(set(db.COMMERCIAL_STATES)) == 7
    assert db.COMMERCIAL_STATES[1:4] == ("REQUESTED", "LIKELY",
                                         "APPROVED")


def test_an_amount_without_provenance_or_date_is_refused():
    assert typed_amount("REQUESTED", dated=True, provenance=None)[
        "reason"] == "E_UNTYPED_AMOUNT"
    assert typed_amount("REQUESTED", dated=False,
                        provenance="thread:x")["missing"] == ["date"]
    assert typed_amount("VIBES", True, "t")["reason"] == \
        "E_UNKNOWN_COMMERCIAL_STATE"


def test_a_fully_typed_amount_is_admitted_without_its_number():
    v = typed_amount("REQUESTED", dated=True, provenance="thread:x")
    assert v["ok"] is True
    assert "amount" not in v          # figures never travel through here


def test_no_arrow_is_skipped_by_narration():
    v = state_transition("REQUESTED", "CONTRACTED", witness="w")
    assert v["licensed"] is False
    assert v["reason"] == "E_NARRATIVE_SKIP"
    assert v["skipped"] == ("LIKELY", "APPROVED")


def test_a_single_forward_arrow_needs_a_witness():
    assert state_transition("REQUESTED", "LIKELY", None)["reason"] == \
        "E_UNWITNESSED_TRANSITION"
    assert state_transition("REQUESTED", "LIKELY", "email:reply")[
        "licensed"] is True


def test_bad_news_needs_no_permission():
    v = state_transition("LIKELY", "REQUESTED", witness=None)
    assert v["licensed"] is True and v["direction"] == "regression"


# ── qualification before elaboration ───────────────────────────────────

def test_disqualifying_uncertainty_is_checked_first():
    """High U_d rejects even when the probe would pay for itself —
    no budget is spent qualifying what is out of mandate."""
    v = qualify(u_r=0.9, u_d=0.8, tau=0.5, evsi=100.0, probe_cost=1.0)
    assert v["act"] == "REJECT"
    assert v["checked_first"] == "U_d"


def test_a_probe_must_pay_for_itself():
    assert qualify(0.5, 0.1, 0.5, evsi=10.0, probe_cost=2.0)["act"] \
        == "PROBE"
    assert qualify(0.5, 0.1, 0.5, evsi=1.0, probe_cost=2.0)["act"] \
        == "HOLD"


def test_negative_inputs_are_refused():
    with pytest.raises(ValueError, match="E_NEGATIVE_INPUT"):
        qualify(-0.1, 0, 0, 0, 0)


# ── commitment coupling ────────────────────────────────────────────────

def test_an_unpinned_coder_yields_no_number():
    v = governance_debt(((0.9, 0.1, 1.0),), coder={"frozen": False})
    assert v["measured"] is False
    assert v["reason"] == "E_UNPINNED_CODER"
    assert "D_gov" not in v


def test_a_pinned_coder_measures_the_positive_part_only():
    coder = {"frozen": True, "version": "cgov-v1"}
    v = governance_debt(((0.9, 0.1, 2.0), (0.2, 0.8, 5.0)), coder)
    assert v["measured"] is True
    assert v["D_gov"] == 1.6          # second sample clips to zero
    assert v["status"] == "TESTABLE_CANDIDATE_METRIC"


def test_no_samples_is_refused():
    with pytest.raises(ValueError, match="E_NO_SAMPLES"):
        governance_debt((), {"frozen": True, "version": "v"})


def test_high_debt_with_no_friction_bounds_the_metric():
    v = debt_negative_control(d_gov=4.2, frictions_observed=0)
    assert v["is_negative_control"] is True
    assert v["verdict"] == "BOUNDS_THE_METRIC"
    assert debt_negative_control(4.2, 3)["verdict"] == \
        "CONSISTENT_CASE"


# ── dynamic comparative advantage ──────────────────────────────────────

def test_sunk_cost_has_no_way_in():
    """The signature is the law: current values only."""
    import inspect
    params = list(inspect.signature(delta_v).parameters)
    assert params == ["v_external", "v_baseline", "cost_external"]


def test_a_stronger_baseline_flips_the_verdict():
    assert delta_v(10.0, 3.0, 2.0)["keep_external"] is True
    assert delta_v(10.0, 9.0, 2.0)["keep_external"] is False
    assert delta_v(10.0, 9.0, 2.0)["act_if_not"] == "SWITCH"


def test_the_manucurist_shape_is_switch_not_defend():
    v = baseline_moved(dv_before=5.0, dv_after=-1.0)
    assert v["act"] == "SWITCH"
    assert baseline_moved(5.0, 2.0)["act"] == "KEEP"


# ── the engine, kept narrow ────────────────────────────────────────────

def test_a_surface_point_carries_only_decision_time_variables():
    v = surface_point("HOLD",
                      {"brief_ambiguity": 1, "eventual_outcome": 0},
                      evidence="thread:16ef56")
    assert v["ok"] is False
    assert v["reason"] == "E_HINDSIGHT_VARIABLE"
    assert v["tainted"] == ["eventual_outcome"]


def test_no_receipt_is_a_lawful_outcome():
    v = surface_point("HOLD", {"u_d": 0.7, "provenance": "indirect"},
                      evidence="thread:16ef56")
    assert v["ok"] is True
    assert v["outcome"] == "NO_RECEIPT"


def test_the_six_decisions_are_the_whole_alphabet():
    assert db.DECISIONS == ("GO", "PROBE", "HOLD", "REJECT", "STOP",
                            "SWITCH")
    assert surface_point("PIVOT", {}, "e")["reason"] == \
        "E_UNKNOWN_DECISION"


def test_an_unevidenced_point_is_refused():
    assert surface_point("GO", {"x": 1}, evidence="")["reason"] == \
        "E_UNEVIDENCED_POINT"


def test_the_engine_reconstructs_and_does_not_recommend():
    assert engine_task("reconstruct observed decision surfaces")[
        "licensed"] is True
    for t in db.ENGINE_OUT_OF_SCOPE:
        v = engine_task(t)
        assert v["licensed"] is False
        assert v["reason"] == "E_OUT_OF_SCOPE"


# ── the J4 reinforcement law ───────────────────────────────────────────

def test_confirmations_accumulate_and_never_reinforce():
    v = reinforcement(predictors_present=True, effect_present=True)
    assert v["case"] == "CONFIRMATION"
    assert v["reinforced"] is False
    assert v["accumulates"] is True


def test_reinforcement_is_bought_only_where_the_method_could_die():
    v = reinforcement(True, False, survived=True)
    assert v["case"] == "NEGATIVE_CONTROL"
    assert v["reinforced"] is True
    dead = reinforcement(True, False, survived=False)
    assert dead["reinforced"] is False and dead["weakened"] is True


def test_an_unscored_negative_control_reinforces_nothing():
    v = reinforcement(True, False, survived=None)
    assert v["reinforced"] is False
    assert v["reason"] == "E_SURVIVAL_UNSCORED"


def test_an_unexplained_success_bounds_and_never_supports():
    v = reinforcement(predictors_present=False, effect_present=True)
    assert v["case"] == "UNEXPLAINED_SUCCESS"
    assert v["reinforced"] is False
    assert v["boundary_information"] is True


def test_a_confounded_confirmation_supports_nothing():
    from decision_boundaries import outcome_attribution
    v = outcome_attribution(outcome_consistent=True,
                            causal_path_through_predictors=False)
    assert v["case"] == "CONFOUNDED_CONFIRMATION"
    assert v["supports_method"] is False
    assert v["accumulates"] is False
    assert v["stratum_flag"] == "EXOGENOUS_SHOCK"


def test_a_clean_confirmation_still_only_accumulates():
    from decision_boundaries import outcome_attribution
    v = outcome_attribution(True, causal_path_through_predictors=True)
    assert v["case"] == "CONFIRMATION"
    assert v["supports_method"] is False and v["accumulates"] is True


def test_an_inconsistent_outcome_is_routed_to_reinforcement():
    from decision_boundaries import outcome_attribution
    assert outcome_attribution(False, True)["case"] == \
        "DISCONFIRMING_OUTCOME"


# ── status discipline ──────────────────────────────────────────────────

def test_nothing_here_can_become_canon():
    assert promote_to_canon("typed_states")["promoted"] is False
    assert promote_to_canon("D_gov")["reason"] == \
        "E_CANDIDATE_IS_NOT_CANON"


def test_the_j4_cursor_expects_a_boundary_not_a_method():
    v = j4_cursor()
    assert v["J4_MODE"] == "FAILURES+COUNTEREXAMPLES+NEGATIVE_CONTROLS"
    assert v["PROMOTE_TO_CANON"] is False


def test_deterministic():
    assert db.canon(qualify(0.5, 0.1, 0.5, 3.0, 1.0)) == \
        db.canon(qualify(0.5, 0.1, 0.5, 3.0, 1.0))
