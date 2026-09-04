#!/usr/bin/env python3
"""Append a Rose decision safely to the decision ledger.

The ledger is append-only. This script is the only sanctioned writer.
It refuses records that lack required fields, use an unknown outcome,
duplicate an existing decision_id, or fail to indicate Rose as authorizer.

Stdlib only.
"""

import argparse
import json
import sys
from datetime import date as _date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "decisions" / "decision_ledger.jsonl"
OUTCOMES = {"GO", "HOLD", "REVISE", "REJECT", "RESEARCH"}


def existing_ids(ledger_path):
    ids = set()
    if ledger_path.exists():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(json.loads(line).get("decision_id"))
            except json.JSONDecodeError:
                pass
    return ids


def append_decision(record, ledger_path=LEDGER):
    """Validate and append one decision record. Returns the record.

    Raises ValueError on any violation. Never rewrites existing lines.
    """
    required = ["decision_id", "date", "subject", "outcome", "scope",
                "rationale", "authorized_by"]
    missing = [f for f in required if not record.get(f)]
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    if record["outcome"] not in OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(OUTCOMES)}")
    if "rose" not in str(record["authorized_by"]).lower():
        raise ValueError("authorized_by must explicitly indicate Rose")
    if record["decision_id"] in existing_ids(ledger_path):
        raise ValueError(f"duplicate decision_id: {record['decision_id']}")
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--decision-id", required=True, help="e.g. R-001")
    ap.add_argument("--date", default=_date.today().isoformat())
    ap.add_argument("--subject", required=True)
    ap.add_argument("--outcome", required=True, choices=sorted(OUTCOMES))
    ap.add_argument("--scope", required=True)
    ap.add_argument("--rationale", required=True)
    ap.add_argument("--authorized-by", required=True,
                    help="must explicitly indicate Rose")
    args = ap.parse_args(argv)

    record = {
        "decision_id": args.decision_id,
        "date": args.date,
        "subject": args.subject,
        "outcome": args.outcome,
        "scope": args.scope,
        "rationale": args.rationale,
        "authorized_by": args.authorized_by,
    }
    try:
        append_decision(record)
    except ValueError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 1
    print(f"appended {args.decision_id} ({args.outcome}) to {LEDGER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
