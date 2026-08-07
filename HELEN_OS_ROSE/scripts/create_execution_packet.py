#!/usr/bin/env python3
"""Create an execution packet from a Rose-authorized GO decision.

Refuses creation when the referenced decision does not exist, is not GO,
or when required fields are absent. Packets land in execution/active/.

Stdlib only.
"""

import argparse
import json
import re
import sys
from datetime import date as _date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "decisions" / "decision_ledger.jsonl"
ACTIVE = ROOT / "execution" / "active"

PRIVACY_CLASSES = {
    "PUBLIC", "INTERNAL_BUSINESS", "CONFIDENTIAL_STRATEGY", "PARTNER_RESTRICTED",
    "PERSONAL_PRIVATE", "MEDICAL_PRIVATE", "LEGAL_PRIVATE", "FINANCIAL_PRIVATE",
}


def load_ledger(ledger_path=LEDGER):
    ledger = {}
    if ledger_path.exists():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("decision_id"):
                ledger[rec["decision_id"]] = rec
    return ledger


def next_packet_id(active_dir=ACTIVE):
    nums = [0]
    for p in list(active_dir.glob("P-*.json")) + list((ROOT / "execution" / "archive").glob("P-*.json")):
        m = re.match(r"P-(\d{3})", p.name)
        if m:
            nums.append(int(m.group(1)))
    return f"P-{max(nums) + 1:03d}"


def create_packet(decision_id, outcome_text, scope, owner, privacy_class,
                  ledger_path=LEDGER, active_dir=ACTIVE):
    """Create a packet. Raises ValueError on refusal. Returns packet path."""
    for name, val in [("decision_id", decision_id), ("outcome", outcome_text),
                      ("scope", scope), ("owner", owner)]:
        if not val:
            raise ValueError(f"missing required field: {name}")
    if privacy_class not in PRIVACY_CLASSES:
        raise ValueError(f"privacy_class must be one of {sorted(PRIVACY_CLASSES)}")
    ledger = load_ledger(ledger_path)
    if decision_id not in ledger:
        raise ValueError(f"decision {decision_id} does not exist in ledger")
    if ledger[decision_id].get("outcome") != "GO":
        raise ValueError(f"decision {decision_id} outcome is "
                         f"'{ledger[decision_id].get('outcome')}', packet requires GO")

    packet_id = next_packet_id(active_dir)
    packet = {
        "packet_id": packet_id,
        "approved_decision_id": decision_id,
        "outcome": outcome_text,
        "scope": scope,
        "non_goals": [],
        "owner": owner,
        "inputs": [],
        "steps": [],
        "artifacts": [],
        "acceptance_tests": [],
        "stop_conditions": [
            "scope broadens beyond the authorized decision -> return to sovereign review",
        ],
        "privacy_class": privacy_class,
        "status": "PLANNED",
        "receipts": [],
        "created": _date.today().isoformat(),
        "state_history": [],
    }
    active_dir.mkdir(parents=True, exist_ok=True)
    path = active_dir / f"{packet_id}.json"
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--decision-id", required=True, help="GO decision, e.g. R-001")
    ap.add_argument("--outcome", required=True, help="what done looks like")
    ap.add_argument("--scope", required=True)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--privacy-class", required=True, choices=sorted(PRIVACY_CLASSES))
    args = ap.parse_args(argv)
    try:
        path = create_packet(args.decision_id, args.outcome, args.scope,
                             args.owner, args.privacy_class)
    except ValueError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 1
    print(f"created {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
