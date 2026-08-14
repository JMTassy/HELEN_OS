"""Round 2 falsified: width may not buy authority outside the policy
door; deterministic cognition and probabilistic authority are both
refused; the observer commands nothing; the critic only proposes; an
agent with an unpriced cost is not hired; dictation is never truth;
EXECUTE never precedes ADMIT; and the bare term 'control plane' is
ambiguous by law.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import workforce_runtime as wr
from workforce_runtime import (
    boundary_promise,
    critic_emission,
    determinism_grade,
    factory_gate,
    hire_agent,
    human_action,
    observer_report,
    opportunity_score,
    pipeline_step,
    plane,
    tacit_capture,
    width_expansion,
)


# ── law 2: width without authority ─────────────────────────────────────

def test_width_may_expand_with_authority_flat():
    v = width_expansion(delta_width=10.0, delta_authority=0,
                        policy_change_admitted=False)
    assert v["lawful"] is True
    assert v["invariant"] == "dA/dN = 0 held"


def test_width_may_not_buy_authority():
    v = width_expansion(10.0, delta_authority=1.0,
                        policy_change_admitted=False)
    assert v["lawful"] is False
    assert v["reason"] == "E_WIDTH_BOUGHT_AUTHORITY"


def test_authority_moves_only_through_the_policy_door():
    v = width_expansion(0.0, 1.0, policy_change_admitted=True)
    assert v["lawful"] is True and v["via"] == "admitted_policy_change"


# ── law 3: the determinism split ───────────────────────────────────────

def test_cognition_is_probabilistic_and_authority_is_not():
    assert determinism_grade("llm_recommendation")["grade"] == \
        "PROBABILISTIC"
    assert determinism_grade("authorization_check")["grade"] == \
        "DETERMINISTIC"
    assert determinism_grade("database_mutation")["grade"] == \
        "TRANSACTIONAL"
    assert determinism_grade("vibes")["reason"] == \
        "E_UNKNOWN_COMPONENT"


def test_promising_deterministic_cognition_is_refused():
    v = boundary_promise("deterministic_cognition")
    assert v["promisable"] is False
    assert v["reason"] == "E_OVERPROMISED_DETERMINISM"


def test_probabilistic_authority_is_refused():
    v = boundary_promise("probabilistic_authority")
    assert v["promisable"] is False
    assert v["reason"] == "E_PROBABILISTIC_AUTHORITY"


def test_the_lawful_promise_lists_its_deterministic_components():
    v = boundary_promise("deterministic_state_transition_governance")
    assert v["promisable"] is True
    assert "authorization_check" in v["deterministic_components"]
    assert "llm_recommendation" not in v["deterministic_components"]


# ── the human role ─────────────────────────────────────────────────────

def test_the_seven_human_primitives():
    for p in wr.HUMAN_PRIMITIVES:
        assert human_action(p)["ok"] is True
    assert len(wr.HUMAN_PRIMITIVES) == 7


def test_prompting_is_lawful_but_named_as_the_first_domino():
    v = human_action("PROMPT")
    assert v["ok"] is True
    assert v["role"] == "first domino"


# ── the opportunity engine ─────────────────────────────────────────────

def test_the_score_subtracts_all_three_costs():
    assert opportunity_score(10, 2, 3, 1)["score"] == 4


def test_execute_never_precedes_admit():
    v = pipeline_step("EXECUTE", admitted=False)
    assert v["ok"] is False
    assert v["reason"] == "E_UNADMITTED_EXECUTION"
    assert pipeline_step("EXECUTE", admitted=True)["ok"] is True


def test_admit_sits_before_execute_in_the_pipeline():
    assert wr.OPPORTUNITY_PIPELINE.index("ADMIT") < \
        wr.OPPORTUNITY_PIPELINE.index("EXECUTE")
    assert wr.OPPORTUNITY_PIPELINE[0] == "SCAN"
    assert wr.OPPORTUNITY_PIPELINE[-1] == "LEARN"


# ── the metacognitive roles ────────────────────────────────────────────

def test_the_observer_commands_nothing():
    v = observer_report(("friction", "reorganization_order"))
    assert v["ok"] is False
    assert v["reason"] == "E_OBSERVER_HAS_NO_AUTHORITY"
    assert v["refused_outputs"] == ("reorganization_order",)


def test_the_observer_reports_the_four_kinds():
    v = observer_report(("friction", "duplication",
                         "automation_candidates"))
    assert v["ok"] is True and v["authority"] == 0


def test_the_critic_may_only_propose():
    assert critic_emission("directive")["reason"] == \
        "E_CRITIC_MAY_ONLY_PROPOSE"
    v = critic_emission("proposal")
    assert v["ok"] is True
    assert "why does a human initiate this?" in v["questions"]


def test_both_metacognitive_roles_exist_in_the_taxonomy():
    assert "WORKFORCE_OBSERVER" in wr.ROLES
    assert "CRITIC" in wr.ROLES
    assert len(wr.ROLES) == 12


# ── agent economics ────────────────────────────────────────────────────

def _costs(**over):
    c = {k: 1.0 for k in wr.AGENT_COSTS}
    c.update(over)
    return c


def test_an_unpriced_cost_blocks_the_hire():
    c = _costs()
    del c["coordination"]
    v = hire_agent(100.0, c)
    assert v["hired"] is False
    assert v["reason"] == "E_UNPRICED_COST"
    assert v["missing"] == ("coordination",)


def test_value_below_total_cost_is_not_a_hire():
    v = hire_agent(5.0, _costs())          # C_a = 6
    assert v["hired"] is False
    assert v["reason"] == "E_AGENT_COUNT_IS_NOT_A_KPI"


def test_a_priced_positive_hire_passes():
    v = hire_agent(10.0, _costs())
    assert v["hired"] is True and v["C_a"] == 6.0


# ── dictation and the factory ──────────────────────────────────────────

def test_dictation_enters_as_reported_and_never_promoted():
    v = tacit_capture("OPERATOR", "the dates are still moving")
    assert v["epistemic_state"] == "REPORTED"
    assert v["source_type"] == "HUMAN_REPORT"
    assert v["promoted"] is False


def test_the_second_automation_productizes_the_factory():
    assert factory_gate(1)["verdict"] == "AUTOMATE_THE_TASK"
    assert factory_gate(2)["verdict"] == "PRODUCTIZE_THE_FACTORY"
    with pytest.raises(ValueError, match="E_NEGATIVE_COUNT"):
        factory_gate(-1)


# ── the plane collision ────────────────────────────────────────────────

def test_the_bare_term_control_plane_is_ambiguous_by_law():
    v = plane("control_plane")
    assert v["ok"] is False
    assert v["reason"] == "E_AMBIGUOUS_PLANE"
    assert set(v["must_qualify_as"]) == {"POLICY_AUTHORITY",
                                         "RELEASE_DISTRIBUTION"}


def test_both_qualified_planes_resolve():
    assert plane("control_plane", "POLICY_AUTHORITY")["ok"] is True
    assert plane("RELEASE_DISTRIBUTION")["ok"] is True
    assert plane("vibes")["reason"] == "E_UNKNOWN_PLANE"


def test_the_four_laws_are_locked():
    assert len(wr.LAWS) == 4
    assert wr.LAWS[0].endswith("Humans govern.")
    assert "factory once" in wr.LAWS[3]


def test_deterministic():
    assert wr.canon(hire_agent(10.0, _costs())) == \
        wr.canon(hire_agent(10.0, _costs()))
