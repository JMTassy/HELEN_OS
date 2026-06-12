"""
Test: sovereign_promotion flag in SKILL_PROMOTION_DECISION_V1 sets sovereign: true in state.

Validates Gap 4 of SOVEREIGN_PROMOTION_PROTOCOL_V1:
  - Decision with sovereign_promotion: true → skill_entry["sovereign"] == True
  - Decision without sovereign_promotion → no sovereign field (skill_local only)
  - Existing decision shape unchanged when sovereign_promotion absent
"""
from __future__ import annotations

from helen_os.state.skill_library_state_updater import apply_skill_promotion_decision


def _initial_state():
    return {
        "schema_name": "SKILL_LIBRARY_STATE_V1",
        "schema_version": "1.0.0",
        "law_surface_version": "v1",
        "active_skills": {},
    }


def _decision(sovereign_promotion=None):
    d = {
        "schema_name":             "SKILL_PROMOTION_DECISION_V1",
        "schema_version":          "1.0.0",
        "decision_id":             "DECISION_TEST_V1_001",
        "skill_id":                "TEST_SKILL_V1",
        "candidate_version":       "V1",
        "decision_type":           "ADMITTED",
        "reason_code":             "OK_ADMITTED",
        "candidate_identity_hash": "sha256:" + "a" * 64,
    }
    if sovereign_promotion is not None:
        d["sovereign_promotion"] = sovereign_promotion
    return d


def test_sovereign_flag_set_when_sovereign_promotion_true():
    state = apply_skill_promotion_decision(_initial_state(), _decision(sovereign_promotion=True))
    skill = state["active_skills"]["TEST_SKILL_V1"]
    assert skill["status"] == "ACTIVE"
    assert skill.get("sovereign") is True


def test_sovereign_flag_absent_when_sovereign_promotion_false():
    state = apply_skill_promotion_decision(_initial_state(), _decision(sovereign_promotion=False))
    skill = state["active_skills"]["TEST_SKILL_V1"]
    assert skill["status"] == "ACTIVE"
    assert "sovereign" not in skill


def test_sovereign_flag_absent_when_field_missing():
    """Existing decisions (no sovereign_promotion field) must not gain sovereign: true."""
    state = apply_skill_promotion_decision(_initial_state(), _decision())
    skill = state["active_skills"]["TEST_SKILL_V1"]
    assert skill["status"] == "ACTIVE"
    assert "sovereign" not in skill


def test_skill_local_admission_unchanged():
    """Verify the existing skill-local admission shape is untouched."""
    state = apply_skill_promotion_decision(_initial_state(), _decision())
    skill = state["active_skills"]["TEST_SKILL_V1"]
    assert skill["active_version"] == "V1"
    assert skill["last_decision_id"] == "DECISION_TEST_V1_001"
    assert skill["status"] == "ACTIVE"
    assert "sovereign" not in skill


def test_non_admitted_decision_unchanged():
    d = _decision()
    d["decision_type"] = "REJECTED"
    state = apply_skill_promotion_decision(_initial_state(), d)
    assert state["active_skills"] == {}
