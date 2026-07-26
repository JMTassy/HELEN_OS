"""
Tests for _score_proposal() specificity heuristic.
authority=false  sovereign=false  ledger_effect=none
"""
from helen_os.autonomy.self_improve_loop_v1 import (
    _score_proposal,
    PROPOSAL_QUALITY_THRESHOLD,
    REQUIRED_PROPOSAL_FIELDS,
)


def _base():
    return {field: "value" for field in REQUIRED_PROPOSAL_FIELDS}


def test_vague_effect_scores_0_75():
    p = {**_base(), "skill_id": "summary_v1",
         "expected_effects": ["improve summarization quality"]}
    assert _score_proposal(p) == 0.75


def test_specific_effect_scores_1_0():
    p = {**_base(), "skill_id": "summary_v1",
         "expected_effects": [
             "reduce summary tokens by 20% while preserving named entities"
         ]}
    assert _score_proposal(p) == 1.0


def test_noop_scores_0_5():
    p = {**_base(), "skill_id": "noop_v1",
         "expected_effects": ["leave behavior unchanged"]}
    assert _score_proposal(p) == 0.5


def test_missing_fields_scores_0_0():
    assert _score_proposal({"skill_id": "x_v1", "description": "broken"}) == 0.0


def test_specific_with_constraint_scores_1_0():
    p = {**_base(), "skill_id": "router_v1",
         "expected_effects": ["retain entity recall above 0.9 without increasing latency"]}
    assert _score_proposal(p) == 1.0


def test_specific_with_identifier_scores_1_0():
    p = {**_base(), "skill_id": "trimmer_v1",
         "expected_effects": ["compress speak() history to last 5 turns"]}
    assert _score_proposal(p) == 1.0


def test_gate_threshold_preserved_for_vague():
    p = {**_base(), "skill_id": "vague_v1",
         "expected_effects": ["enhance performance"]}
    score = _score_proposal(p)
    assert score == 0.75
    assert score >= PROPOSAL_QUALITY_THRESHOLD


def test_proposal_quality_threshold_is_0_75():
    # Pin constant against future drift — noop_v1 (score=0.5) must not pass gate
    assert PROPOSAL_QUALITY_THRESHOLD == 0.75


def test_noop_score_below_threshold():
    # Confirms noop_v1 score (0.5) < threshold (0.75) — noop blocked at gate
    p = {**_base(), "skill_id": "noop_v1",
         "expected_effects": ["leave behavior unchanged"]}
    score = _score_proposal(p)
    assert score < PROPOSAL_QUALITY_THRESHOLD
