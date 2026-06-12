"""
Test: admitted skills must be OPERATIONALLY_WITNESSED.

Discovers all skills that declare skill_local_admission: CONFIRMED in their
SKILL.md and asserts the checker returns OPERATIONALLY_WITNESSED for each.

Prevents silent drift where a skill's admission artifacts are deleted or
corrupted after the fact. Runs as part of `make test`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO / "oracle_town/skills"

# ── Discovery ─────────────────────────────────────────────────────────────────

def _find_admitted_skills() -> list[tuple[str, Path]]:
    """Return [(skill_id, skill_dir)] for every skill with skill_local_admission: CONFIRMED."""
    admitted = []
    for skill_md in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        text = skill_md.read_text()
        if "skill_local_admission: CONFIRMED" not in text:
            continue
        skill_id = None
        for line in text.splitlines():
            if line.startswith("skill_id:"):
                skill_id = line.split(":", 1)[1].strip()
                break
        if skill_id:
            admitted.append((skill_id, skill_md.parent))
    return admitted


# ── Hardcoded known-admitted registry (belt-and-suspenders) ──────────────────

KNOWN_ADMITTED = [
    "REFERENCE_DRIFT_WITNESS_V1",
    "SKILL_ADMISSION_CHECKER_V1",
]

# ── Tests ─────────────────────────────────────────────────────────────────────

def test_known_admitted_skills_are_discoverable():
    """Every hardcoded known-admitted skill must appear in the discovered list."""
    discovered_ids = {sid for sid, _ in _find_admitted_skills()}
    for skill_id in KNOWN_ADMITTED:
        assert skill_id in discovered_ids, (
            f"{skill_id} is in KNOWN_ADMITTED but has no SKILL.md with "
            f"skill_local_admission: CONFIRMED — admission drift detected"
        )


@pytest.mark.parametrize("skill_id,skill_dir", _find_admitted_skills())
def test_admitted_skill_is_operationally_witnessed(skill_id, skill_dir):
    """
    Every skill that declares skill_local_admission: CONFIRMED must pass
    the checker at OPERATIONALLY_WITNESSED level.

    Failure means one of the 7 admission gates regressed:
      implementation / tests / reducer_artifact /
      admission_ledger / replay_state / replay_active / witness
    """
    from oracle_town.skills.skill_admission_checker import SkillAdmissionChecker, AdmissionLevel

    checker = SkillAdmissionChecker(sot_root=REPO)
    report  = checker.check(skill_id, skill_dir=str(skill_dir.relative_to(REPO)))

    assert report.is_active, (
        f"{skill_id}: declared admitted but checker says {report.status}\n"
        f"evidence: {report.evidence}"
    )
    assert report.status == AdmissionLevel.OPERATIONALLY_WITNESSED.value, (
        f"{skill_id}: expected OPERATIONALLY_WITNESSED, got {report.status}\n"
        f"evidence: {report.evidence}"
    )
