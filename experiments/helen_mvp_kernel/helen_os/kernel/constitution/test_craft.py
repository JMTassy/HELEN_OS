"""Craft, falsified: the artifact is bounded by its factory; a
generated artifact is not a possessed capability; unwitnessed failure
teaches nothing; Replay, Persistence and Survival are three different
properties; knowledge inherits and authority never does.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import craft as cr
from craft import (
    capability_bound,
    evolve_capability,
    generate_artifact,
    inherit_craft,
    knowledge_grows_authority_does_not,
    learn_from_failure,
    survival_assessment,
    survival_rate,
)

CHAIN = {"M0_institutional_knowledge": 0.9, "M1_builders": 0.7,
         "M2_tooling_and_eval": 0.8}


# ── the Builder Bound ───────────────────────────────────────────────────

def test_the_artifact_cannot_be_finer_than_its_factory():
    v = capability_bound(CHAIN, claimed_artifact_quality=0.85)
    assert v["claim_admissible"] is False
    assert v["reason"] == "E_EXCEEDS_BUILDER_CAPABILITY"
    assert v["bound"] == 0.7
    assert v["weakest_stage"] == "M1_builders"


def test_a_claim_within_the_bound_is_admissible():
    v = capability_bound(CHAIN, claimed_artifact_quality=0.7)
    assert v["claim_admissible"] is True
    assert "factory, not the watch" in v["the_product_is"]


def test_an_unaccounted_builder_stage_refuses_the_claim():
    v = capability_bound({"M1_builders": 0.9}, 0.5)
    assert v["claim_admissible"] is False
    assert v["reason"] == "E_UNACCOUNTED_BUILDER_STAGE"
    assert "M0_institutional_knowledge" in v["missing"]


# ── artifact time << capability formation time ──────────────────────────

def test_generation_is_not_possession():
    a = generate_artifact("instant_agent")
    assert a["generated"] is True
    assert a["capability_possessed"] is False


def test_capability_is_a_balance_that_can_decline():
    up = evolve_capability(10.0, gained=3.0, forgotten=1.0)
    down = evolve_capability(10.0, gained=0.0, forgotten=4.0)
    floor = evolve_capability(1.0, gained=0.0, forgotten=9.0)
    assert up["K_next"] == 12.0 and up["declined"] is False
    assert down["K_next"] == 6.0 and down["declined"] is True
    assert floor["K_next"] == 0.0


# ── institutional learning ─────────────────────────────────────────────

def test_a_witnessed_failure_changes_the_builder():
    v = learn_from_failure("scope_breach_helen_kernel", True, 41)
    assert v["builder_changed"] is True
    assert v["builder_version"] == 42
    assert v["becomes_regression_probe"] is True
    assert "verify.py" in v["note"]


def test_an_unwitnessed_failure_teaches_nothing():
    v = learn_from_failure("silent_regression", False, 41)
    assert v["builder_changed"] is False
    assert v["builder_version"] == 41
    assert v["lesson"] is None
    assert v["reason"] == "E_UNWITNESSED_FAILURE"


# ── constitutional survival: the 54-year-watch test ─────────────────────

def test_replay_persistence_and_survival_are_three_properties():
    """The separating example: replays, persists — and fails today's
    stricter gate. Historically admitted, not currently admissible."""
    v = survival_assessment("x_2019", admitted_at_t=True, replays=True,
                            persists=True, passes_current_gate=False)
    assert v["replay"] is True and v["persistence"] is True
    assert v["survival"] is False
    assert v["status"] == "HISTORICALLY_ADMITTED_NOT_CURRENTLY_ADMISSIBLE"


def test_the_old_admission_stands_and_mints_nothing():
    v = survival_assessment("x_2019", True, True, True, False)
    assert v["historical_admission_stands"] is True
    assert v["retroactive_rewrite"] is False
    assert v["present_authority_minted"] is False


def test_the_railroad_watch_is_the_survival_success_case():
    v = survival_assessment("hamilton_1893", True, True, True, True)
    assert v["status"] == "RAILROAD_GRADE_SURVIVAL"
    assert v["present_authority_minted"] is False    # even survivors


def test_survival_rate_is_measured_not_assumed():
    cohort = ({"passes_current_gate": True},
              {"passes_current_gate": False},
              {"passes_current_gate": True},
              {"passes_current_gate": False})
    s = survival_rate(cohort)
    assert s["S_k"] == 0.5
    assert s["cohort"] == 4


# ── inheritance: knowledge yes, authority never ─────────────────────────

def test_the_heir_receives_craft_and_never_authority():
    bundle = ("procedures", "counterexamples", "failure_patterns",
              "receipts", "authority_grant", "permissions")
    v = inherit_craft(bundle, "son")
    assert v["transferred"] == ["counterexamples", "failure_patterns",
                                "procedures", "receipts"]
    assert v["stripped"] == ["authority_grant", "permissions"]
    assert v["stripped_reason"] == "E_AUTHORITY_IS_NOT_HERITABLE"


def test_an_unclassified_item_is_flagged_not_silently_passed():
    v = inherit_craft(("procedures", "mystery_blob"), "son")
    assert v["unclassified"] == ["mystery_blob"]


def test_knowledge_grows_while_authority_stays_flat():
    v = knowledge_grows_authority_does_not(
        frozenset({"lesson_1"}), frozenset({"lesson_2"}),
        frozenset({"grant_read_only"}))
    assert v["knowledge_grew"] is True
    assert v["authority_grew"] is False
    assert v["A_next"] == v["A_t"] == ["grant_read_only"]
    assert "compound" in v["law"]


def test_craft_is_defined_and_survives_change_of_everything():
    for word in ("worker", "tool", "artifact", "time"):
        assert word in cr.CRAFT_DEFINITION


def test_deterministic():
    assert cr.canon(capability_bound(CHAIN, 0.85)) == \
        cr.canon(capability_bound(CHAIN, 0.85))
    assert cr.canon(inherit_craft(("procedures",), "h")) == \
        cr.canon(inherit_craft(("procedures",), "h"))
