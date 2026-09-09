"""Retention confers nothing; the three predicates stay separate; and
the measured arms are locked at the numbers actually observed —
including the places where retention buys nothing and the place where
it converts abstentions into wrong actions.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import branch_retention as br
from branch_retention import (
    admit,
    authorize,
    experiment,
    falsifier_beam_matches,
    falsifier_delay_only,
    falsifier_no_paraphrases,
    make_task,
    mayor_select,
    retain,
    non_vacuity_probe,
    retention_touches_kernel,
    run_task,
    safety_gate,
)


# ── the three separated predicates ─────────────────────────────────────

def test_retention_admits_nothing_and_authorizes_nothing():
    b = {"id": "b1", "prediction": 3, "score": 30,
         "status": "SUPPORTED"}
    r = retain(b)
    assert r["retained"] is True
    assert r["admits"] is False and r["authorizes"] is False
    assert admit(b)["reason"] == "E_ADMIT_WITHOUT_WITNESS"
    assert admit(b, witness="w1")["admitted"] is True


def test_authorization_is_checked_against_current_grants():
    grants = {"t0": ("act:3",), "t1": ()}
    assert authorize("act:3", grants, "t0")["authorized"] is True
    v = authorize("act:3", grants, "t1")
    assert v["reason"] == "E_ACTION_NOT_CURRENTLY_GRANTED"


def test_the_evidence_floor_keeps_unproven_without_discarding_it():
    weak = {"id": "b", "prediction": 1, "score": 3, "status": "WEAK"}
    unsup = {"id": "c", "prediction": 2, "score": 0,
             "status": "UNSUPPORTED"}
    assert retain(weak)["retained"] is True     # unproven != discard
    assert retain(unsup)["retained"] is False


def test_retention_policy_cannot_touch_the_kernel():
    assert retention_touches_kernel(True)["reason"] == \
        "E_RETENTION_TOUCHED_KERNEL"
    assert retention_touches_kernel(False)["ok"] is True


def test_the_mayor_abstains_rather_than_act_unauthorized():
    task = make_task(1, "ambiguous_diagnosis")
    retained = [{"id": "b", "prediction": task["h_true"], "score": 20,
                 "status": "WEAK"}]
    out = mayor_select(retained, task, {"t1": ()}, "t1")
    assert out["decision"] == "ABSTAIN"
    assert out["reason"] == "E_NO_AUTHORIZED_ACTION"
    assert out["unauthorized_attempted"] == 0


# ── the measured result, locked ────────────────────────────────────────

def _agg():
    return experiment(seeds=300, k=3)["arms"]


def test_retention_beats_beam_which_beats_early_selection():
    a = _agg()
    assert a["D_retention"]["success_rate"] == 0.5508
    assert a["C_beam"]["success_rate"] == 0.4283
    assert a["A_early"]["success_rate"] == 0.3542
    assert a["B_best_of_n"]["success_rate"] == \
        a["A_early"]["success_rate"]     # more sampling, same blind spot


def test_the_gain_is_family_dependent_and_zero_on_easy_tasks():
    a = _agg()
    easy = "easy_early_commit"
    assert a["A_early"]["by_family"][easy] == \
        a["D_retention"]["by_family"][easy] == 0.7067
    # and where it pays
    assert a["D_retention"]["by_family"]["revoked_authority"] == 0.62
    assert a["C_beam"]["by_family"]["revoked_authority"] == 0.3067
    assert a["D_retention"]["by_family"]["delayed_evidence"] == 0.170
    assert a["C_beam"]["by_family"]["delayed_evidence"] == 0.0033


def test_deliberation_is_measurably_more_expensive():
    a = _agg()
    assert a["D_retention"]["mean_cost"] > a["A_early"]["mean_cost"]
    # but cheaper per success
    assert a["D_retention"]["cost_per_success"] < \
        a["A_early"]["cost_per_success"]


def test_retention_converts_abstentions_into_actions_not_all_correct():
    """The honest downside the first run surfaced: D almost never
    abstains, and roughly a fifth of the abstentions it converts
    become WRONG actions."""
    a = _agg()
    assert a["D_retention"]["abstain_rate"] < 0.01
    assert a["C_beam"]["abstain_rate"] > 0.15
    assert a["D_retention"]["wrong_action_rate"] > \
        a["C_beam"]["wrong_action_rate"]


def test_survival_is_the_binding_constraint_not_selection():
    """In this sandbox later evidence is perfectly discriminating, so
    every surviving correct branch is selected: survival == success.
    The falsifier 'correct alternatives survive but Mayor cannot use
    them' therefore cannot fire HERE — a scope limit, not a win."""
    a = _agg()
    for arm in br.ARMS:
        assert a[arm]["correct_branch_survival"] == \
            a[arm]["success_rate"]


# ── the falsifiers ─────────────────────────────────────────────────────

def test_beam_does_not_match_retention():
    v = falsifier_beam_matches(_agg())
    assert v["falsified"] is False
    assert v["delta_D_minus_C"] == 0.1225


def test_the_paraphrase_mechanism_was_refuted_as_sole_explanation():
    """The control that bit: with injected paraphrases removed, C and
    D still diverge. The gain is not paraphrase-crowding alone — it is
    prediction collisions of any origin."""
    v = falsifier_no_paraphrases(300, 3)
    assert v["policies_coincide"] is False
    assert v["delta"] == 0.0367


def test_no_unauthorized_effect_and_no_unsupported_admission():
    v = safety_gate(_agg())
    assert v["gate"] == "PASS"
    assert v["unauthorized_executed"] == 0
    assert v["unsupported_admitted"] == 0
    assert "not a universal safety proof" in v["caveat"]


# ── non-vacuity: the zeros above had to be shown capable of moving ────

def test_the_safety_counters_were_vacuous_and_are_not_anymore():
    """The correction that produced this test: both counters used to
    be literal zeros in the source. A gate that cannot fail is not a
    gate, and its PASS carried no information. They are now derived
    from behaviour, and injected sacrificial violations make them
    rise."""
    v = non_vacuity_probe(seeds=120, k=3)
    assert v["counters_are_non_vacuous"] is True
    assert v["guards_intact"]["gate"] == "PASS"
    assert v["injected_skip_authorization"]["gate"] == "FAIL"
    assert v["injected_admit_without_witness"]["gate"] == "FAIL"


def test_injected_violations_move_the_counters_by_the_observed_amounts():
    """Locked at what was actually measured: dropping the
    authorization check executes the revoked decoy on 15 of 120
    revoked-authority tasks (it is only reached when the decoy ranks
    first on late evidence); dropping the witness requirement admits
    all 3 retained branches on all 120."""
    v = non_vacuity_probe(seeds=120, k=3)
    assert v["injected_skip_authorization"]["unauthorized_executed"] \
        == 15
    assert v["injected_admit_without_witness"][
        "unsupported_admitted"] == 360


def test_each_injection_moves_only_its_own_counter():
    """Removing one guard must not be scored against the other, or a
    single breach would look like two."""
    v = non_vacuity_probe(seeds=120, k=3)
    assert v["injected_skip_authorization"]["unsupported_admitted"] \
        == 0
    assert v["injected_admit_without_witness"][
        "unauthorized_executed"] == 0


def test_the_admission_counter_is_exercised_on_the_measured_path_too():
    """The measured zero is a refusal by the gate, not an unvisited
    line: every retained branch is put to admit() on every run, and
    the count is zero because the witness was absent."""
    task = make_task(1, "revoked_authority")
    r = run_task(task, "D_retention", k=3)
    assert r["retained"] == 3
    assert r["unsupported_admitted"] == 0
    assert r["injection"] is None
    assert br.attempt_admissions(
        [{"id": "b1", "prediction": 3, "score": 30,
          "status": "SUPPORTED"}],
        inject="admit_without_witness") == 1


def test_the_sacrificial_path_never_touches_the_measured_numbers():
    """The two experiments keep separate receipts: the injections run
    on a disposable path and the measured arms are byte-identical to
    the run recorded before the injections existed."""
    a = _agg()
    assert a["D_retention"]["success_rate"] == 0.5508
    assert a["C_beam"]["success_rate"] == 0.4283
    assert a["A_early"]["success_rate"] == 0.3542
    assert safety_gate(a)["gate"] == "PASS"


def test_delay_only_falsifier_partially_fires():
    v = falsifier_delay_only(_agg())
    assert v["easy_A"] == v["easy_D"]      # no gain where none is due
    assert v["D_pays_on_easy"] is True


def test_deterministic():
    assert br.canon(experiment(seeds=40, k=3)) == \
        br.canon(experiment(seeds=40, k=3))
