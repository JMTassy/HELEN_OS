"""
Tests for SKILL_ADMISSION_CHECKER_V1.

Covers all 7 admission levels and the fail-closed invariant.
NON_SOVEREIGN — no ledger writes, no sovereign path access.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from oracle_town.skills.skill_admission_checker.skill import (
    AdmissionLevel,
    SkillAdmissionChecker,
    REPORT_SCHEMA,
)

SKILL_ID = "TEST_SKILL_V1"


# ── Fixture builders ──────────────────────────────────────────────────────────

def _impl(skill_dir: Path) -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "skill.py").write_text("# stub")


def _tests(skill_dir: Path) -> None:
    t = skill_dir / "tests"
    t.mkdir(exist_ok=True)
    (t / "test_stub.py").write_text("def test_stub(): pass")


def _reducer(root: Path, skill_id: str) -> None:
    scratch = root / "oracle_town/skills/ops/dan_goblin/scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / f"REDUCER_DECISION_{skill_id}.md").write_text(
        f"REDUCER_DECISION_V1\nTarget: {skill_id}\nDecision: ADMIT\n"
    )


def _ledger(skill_dir: Path) -> None:
    (skill_dir / "ADMISSION_LEDGER_V1.json").write_text(
        json.dumps({"schema_name": "DECISION_LEDGER_V1", "entries": [{"entry_index": 0}]})
    )


def _replay(skill_dir: Path, skill_id: str, status: str = "ACTIVE") -> None:
    (skill_dir / "ADMISSION_STATE_V1.json").write_text(
        json.dumps({"active_skills": {skill_id: {"status": status, "active_version": "V1"}}})
    )


def _witness(skill_dir: Path) -> None:
    (skill_dir / "WITNESS_REPORT_LIVE_E99.json").write_text(
        json.dumps({"schema": "REFERENCE_DRIFT_REPORT_V1", "drift_count": 0})
    )


def _checker(root: Path) -> SkillAdmissionChecker:
    return SkillAdmissionChecker(sot_root=root)


def _skill_dir_path(root: Path, skill_id: str) -> Path:
    import re
    base = re.sub(r"_V\d+$", "", skill_id, flags=re.IGNORECASE).lower()
    return root / "oracle_town" / "skills" / base


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_report_schema():
    assert REPORT_SCHEMA == "SKILL_ADMISSION_REPORT_V1"


def test_missing_skill(tmp_path):
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.MISSING.value
    assert report.evidence["implementation"] is None
    assert not report.is_active


def test_implementation_only(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.IMPLEMENTED_ONLY.value
    assert report.evidence["implementation"] is not None
    assert report.evidence["tests"] is None
    assert not report.is_active


def test_tested_only(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.TESTED_ONLY.value
    assert report.evidence["tests"] is not None
    assert report.evidence["reducer_artifact"] is None
    assert not report.is_active


def test_admit_artifact_only(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    _reducer(tmp_path, SKILL_ID)
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.ADMIT_ARTIFACT_ONLY.value
    assert report.evidence["reducer_artifact"] is not None
    assert report.evidence["admission_ledger"] is None
    assert not report.is_active


def test_ledger_without_replay(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    _reducer(tmp_path, SKILL_ID)
    _ledger(d)
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.LEDGER_APPENDED.value
    assert report.evidence["admission_ledger"] is not None
    assert report.evidence.get("replay_state") is None
    assert not report.is_active


def test_replay_active_no_witness(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    _reducer(tmp_path, SKILL_ID)
    _ledger(d)
    _replay(d, SKILL_ID, status="ACTIVE")
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.REPLAY_ACTIVE.value
    assert report.evidence["replay_active"] is True
    assert report.evidence["witness"] is None
    assert report.is_active


def test_replay_active_with_witness(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    _reducer(tmp_path, SKILL_ID)
    _ledger(d)
    _replay(d, SKILL_ID, status="ACTIVE")
    _witness(d)
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.OPERATIONALLY_WITNESSED.value
    assert report.evidence["witness"] is not None
    assert report.is_active


def test_malformed_replay_fails_closed(tmp_path):
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    _reducer(tmp_path, SKILL_ID)
    _ledger(d)
    (d / "ADMISSION_STATE_V1.json").write_text("not valid json {{{{")
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.LEDGER_APPENDED.value
    assert not report.is_active


def test_replay_non_active_status_fails_closed(tmp_path):
    # Replay exists but status is QUARANTINED — must not be treated as ACTIVE
    d = _skill_dir_path(tmp_path, SKILL_ID)
    _impl(d)
    _tests(d)
    _reducer(tmp_path, SKILL_ID)
    _ledger(d)
    _replay(d, SKILL_ID, status="QUARANTINED")
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.status == AdmissionLevel.LEDGER_APPENDED.value
    assert report.evidence["replay_active"] is False
    assert not report.is_active


def test_report_authority_never_sovereign(tmp_path):
    report = _checker(tmp_path).check(SKILL_ID)
    assert report.authority == "NONE"
    assert report.world_effect == "NONE"
    assert report.sovereign_touch is False


def test_to_dict_has_schema(tmp_path):
    report = _checker(tmp_path).check(SKILL_ID)
    d = report.to_dict()
    assert d["schema"] == REPORT_SCHEMA
    assert "evidence" in d
    assert d["authority"] == "NONE"


# ── Known-positive: REFERENCE_DRIFT_WITNESS_V1 ───────────────────────────────

def test_reference_drift_witness_known_positive():
    """
    Runs against the live SOT. REFERENCE_DRIFT_WITNESS_V1 must be
    OPERATIONALLY_WITNESSED (all 7 gates pass).
    """
    import re
    from pathlib import Path as P

    sot = P(__file__).resolve().parents[4]   # tests/→checker/→skills/→oracle_town/→sot
    checker = SkillAdmissionChecker(sot_root=sot)
    report  = checker.check("REFERENCE_DRIFT_WITNESS_V1")

    assert report.is_active, (
        f"Expected REFERENCE_DRIFT_WITNESS_V1 to be active, got: {report.status}\n"
        f"evidence: {report.evidence}"
    )
    assert report.status == AdmissionLevel.OPERATIONALLY_WITNESSED.value
