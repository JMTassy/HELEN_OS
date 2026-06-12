"""
SKILL_ADMISSION_CHECKER_V1
oracle_town/skills/skill_admission_checker/skill.py

Given a skill_id, determines institutional admission status
according to SKILL_ADMISSION_PROTOCOL_V1.

Core invariant: never return REPLAY_ACTIVE or higher unless
replay state file explicitly marks skill ACTIVE.

authority   : NONE
world_effect: NONE
sovereign_touch: False
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


REPORT_SCHEMA = "SKILL_ADMISSION_REPORT_V1"


class AdmissionLevel(str, Enum):
    MISSING              = "MISSING"
    IMPLEMENTED_ONLY     = "IMPLEMENTED_ONLY"
    TESTED_ONLY          = "TESTED_ONLY"
    ADMIT_ARTIFACT_ONLY  = "ADMIT_ARTIFACT_ONLY"
    LEDGER_APPENDED      = "LEDGER_APPENDED"
    REPLAY_ACTIVE        = "REPLAY_ACTIVE"
    OPERATIONALLY_WITNESSED = "OPERATIONALLY_WITNESSED"


@dataclass
class AdmissionReport:
    schema: str         = REPORT_SCHEMA
    skill_id: str       = ""
    status: str         = AdmissionLevel.MISSING.value
    evidence: dict      = field(default_factory=dict)
    authority: str      = "NONE"
    world_effect: str   = "NONE"
    sovereign_touch: bool = False

    def to_dict(self) -> dict:
        return {
            "schema":          self.schema,
            "skill_id":        self.skill_id,
            "status":          self.status,
            "evidence":        self.evidence,
            "authority":       self.authority,
            "world_effect":    self.world_effect,
            "sovereign_touch": self.sovereign_touch,
        }

    @property
    def is_active(self) -> bool:
        return self.status in (
            AdmissionLevel.REPLAY_ACTIVE.value,
            AdmissionLevel.OPERATIONALLY_WITNESSED.value,
        )


class SkillAdmissionChecker:
    """
    Inspects non-sovereign artifact paths to determine a skill's
    institutional admission level.

    Usage::

        checker = SkillAdmissionChecker(sot_root="/path/to/helen_os_v1")
        report  = checker.check("REFERENCE_DRIFT_WITNESS_V1")
        print(report.status)   # OPERATIONALLY_WITNESSED
    """

    def __init__(self, sot_root: str | Path = "."):
        self.sot_root = Path(sot_root).resolve()

    # ── Public API ────────────────────────────────────────────────────────────

    def check(
        self,
        skill_id: str,
        skill_dir: Optional[str] = None,
    ) -> AdmissionReport:
        """
        Returns an AdmissionReport for *skill_id*.

        skill_dir: path to skill directory, relative to sot_root.
                   Derived from skill_id when not provided:
                   REFERENCE_DRIFT_WITNESS_V1 → oracle_town/skills/reference_drift_witness
        """
        report   = AdmissionReport(skill_id=skill_id)
        evidence = {}

        skill_path = self._skill_path(skill_id, skill_dir)

        # Gate 1 — implementation
        impl = skill_path / "skill.py"
        evidence["implementation"] = self._rel(impl) if impl.exists() else None
        if not impl.exists():
            return self._close(report, evidence, AdmissionLevel.MISSING)

        # Gate 2 — tests
        tests_dir  = skill_path / "tests"
        has_tests  = tests_dir.exists() and any(tests_dir.glob("test_*.py"))
        evidence["tests"] = self._rel(tests_dir) if has_tests else None
        if not has_tests:
            return self._close(report, evidence, AdmissionLevel.IMPLEMENTED_ONLY)

        # Gate 3 — reducer ADMIT artifact
        reducer = self._find_reducer_artifact(skill_id)
        evidence["reducer_artifact"] = self._rel(reducer) if reducer else None
        if not reducer:
            return self._close(report, evidence, AdmissionLevel.TESTED_ONLY)

        # Gate 4 — admission ledger
        ledger = skill_path / "ADMISSION_LEDGER_V1.json"
        evidence["admission_ledger"] = self._rel(ledger) if ledger.exists() else None
        if not ledger.exists():
            return self._close(report, evidence, AdmissionLevel.ADMIT_ARTIFACT_ONLY)

        # Gate 5 — replay state file must exist
        replay = skill_path / "ADMISSION_STATE_V1.json"
        evidence["replay_state"] = self._rel(replay) if replay.exists() else None
        if not replay.exists():
            return self._close(report, evidence, AdmissionLevel.LEDGER_APPENDED)

        # Gate 5b — replay state must explicitly mark ACTIVE (fail closed)
        replay_active = self._read_replay_active(replay, skill_id)
        evidence["replay_active"] = replay_active
        if not replay_active:
            return self._close(report, evidence, AdmissionLevel.LEDGER_APPENDED)

        # Gate 6 — operational witness
        witnesses = sorted(skill_path.glob("WITNESS_REPORT_*.json"))
        evidence["witness"] = self._rel(witnesses[0]) if witnesses else None

        level = (
            AdmissionLevel.OPERATIONALLY_WITNESSED if witnesses
            else AdmissionLevel.REPLAY_ACTIVE
        )
        return self._close(report, evidence, level)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _skill_path(self, skill_id: str, skill_dir: Optional[str]) -> Path:
        if skill_dir is not None:
            return self.sot_root / skill_dir
        base = re.sub(r"_V\d+$", "", skill_id, flags=re.IGNORECASE).lower()
        return self.sot_root / "oracle_town" / "skills" / base

    def _find_reducer_artifact(self, skill_id: str) -> Optional[Path]:
        scratch = self.sot_root / "oracle_town/skills/ops/dan_goblin/scratch"
        if scratch.exists():
            for pattern in (f"*REDUCER_DECISION*{skill_id}*", f"*ADMIT*{skill_id}*"):
                hits = sorted(scratch.glob(pattern))
                if hits:
                    return hits[0]
        return None

    @staticmethod
    def _read_replay_active(replay_path: Path, skill_id: str) -> bool:
        """Fail closed: any exception → False."""
        try:
            state = json.loads(replay_path.read_text())
            skill_state = state.get("active_skills", {}).get(skill_id, {})
            return skill_state.get("status") == "ACTIVE"
        except Exception:
            return False

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.sot_root))
        except ValueError:
            return str(path)

    @staticmethod
    def _close(
        report: AdmissionReport,
        evidence: dict,
        level: AdmissionLevel,
    ) -> AdmissionReport:
        report.status   = level.value
        report.evidence = evidence
        return report
