"""CLI: python -m oracle_town.skills.skill_admission_checker.cli SKILL_ID"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # cli.py→checker/→skills/→oracle_town/→sot
sys.path.insert(0, str(REPO))

from oracle_town.skills.skill_admission_checker.skill import SkillAdmissionChecker


def main() -> None:
    p = argparse.ArgumentParser(
        description="SKILL_ADMISSION_CHECKER_V1 — non-sovereign admission status inspector"
    )
    p.add_argument("skill_id", help="Canonical skill ID, e.g. REFERENCE_DRIFT_WITNESS_V1")
    p.add_argument("--skill-dir", default=None, dest="skill_dir",
                   help="Path to skill directory relative to sot-root (overrides auto-derive)")
    p.add_argument("--sot-root", default=str(REPO), dest="sot",
                   help="SOT root (default: repo root)")
    p.add_argument("--json", action="store_true", help="Emit JSON output")
    args = p.parse_args()

    checker = SkillAdmissionChecker(sot_root=args.sot)
    report  = checker.check(args.skill_id, skill_dir=args.skill_dir)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"skill_id : {report.skill_id}")
        print(f"status   : {report.status}")
        print(f"active   : {report.is_active}")
        print("evidence :")
        for k, v in report.evidence.items():
            mark = "✓" if v else "✗"
            print(f"  {mark} {k}: {v or 'NOT FOUND'}")

    if not report.is_active:
        sys.exit(1)


if __name__ == "__main__":
    main()
