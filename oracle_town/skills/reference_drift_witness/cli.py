"""CLI entry point: python -m oracle_town.skills.reference_drift_witness.cli"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from oracle_town.skills.reference_drift_witness.skill import ReferenceDriftWitness


def main() -> None:
    p = argparse.ArgumentParser(description="REFERENCE_DRIFT_WITNESS_V1 — non-sovereign artifact drift scanner")
    p.add_argument("--dir",     required=True,  help="Directory to scan")
    p.add_argument("--pattern", default="*.json", help="Glob pattern (default: *.json)")
    p.add_argument("--epoch",   type=int, default=0, help="Current epoch number for staleness check")
    p.add_argument("--stale-threshold", type=int, default=10, dest="stale",
                   help="Epoch lag before a receipt is considered stale (default: 10)")
    p.add_argument("--snapshot-file", default=None, dest="snapshot",
                   help="JSON file with expected SHAs {path: sha} from a prior snapshot")
    p.add_argument("--sot-root", default=str(REPO), dest="sot",
                   help="SOT root (default: repo root)")
    args = p.parse_args()

    expected: dict[str, str] = {}
    if args.snapshot:
        snap = json.loads(Path(args.snapshot).read_text())
        if isinstance(snap, list):
            expected = {e["path"]: e["sha"] for e in snap}
        elif isinstance(snap, dict):
            expected = snap

    witness = ReferenceDriftWitness(
        sot_root=args.sot,
        current_epoch=args.epoch,
        staleness_epochs=args.stale,
    )
    report = witness.scan_directory(
        directory=args.dir,
        pattern=args.pattern,
        expected_shas=expected or None,
    )

    print(json.dumps(report.to_dict(), indent=2))

    if not report.clean:
        print(f"\ndrift={report.drift_count} missing={report.missing_count} stale={report.stale_count}",
              file=sys.stderr)
        sys.exit(1)
    print(f"\nCLEAN — {report.total_artifacts} artifacts, zero drift/missing/stale")


if __name__ == "__main__":
    main()
