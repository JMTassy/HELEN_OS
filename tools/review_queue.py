#!/usr/bin/env python3
"""
review_queue.py

Read-only operational queue over local GEMMA_PROPOSALS.

Classifies each receipt into governance categories and lets the operator
filter the working set. Used to answer "what do I need to act on now?"

Categories (a receipt may belong to several):
  NEEDS_OPERATOR  operator_decision is null
  NEEDS_HAL       hal_verdict is null
  BLOCKED         hal_verdict.status == NEEDS_MORE_RECEIPTS
  READY_SANDBOX   operator APPROVED_FOR_SANDBOX_ONLY + HAL PASS
  REJECTED        operator REJECTED or HAL FAIL

Usage:
  python tools/review_queue.py                        # full summary
  python tools/review_queue.py --needs-operator       # filter
  python tools/review_queue.py --needs-hal
  python tools/review_queue.py --blocked
  python tools/review_queue.py --ready-sandbox
  python tools/review_queue.py --rejected
  python tools/review_queue.py --topic parser         # substring on topic
  python tools/review_queue.py --blocked --topic parser   # combinable (AND)

Hard constraints:
  - NEVER write to receipt files
  - NEVER write to town/ledger_v1.ndjson
  - NEVER mutate lifecycle_entry
  - NEVER promote, ship, or annotate
  - This tool has no writers. Operator action goes through review_cockpit.py.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hal_receipt_analyzer import (  # noqa: E402
    DEFAULT_PROPOSAL_DIR,
    extract_topic,
    get_status,
    load_receipts,
)

CATEGORIES = ("NEEDS_OPERATOR", "NEEDS_HAL", "BLOCKED", "READY_SANDBOX", "REJECTED")


def classify(receipt: dict) -> set[str]:
    """Categories this receipt belongs to. Can be multiple."""
    op = get_status(receipt.get("operator_decision"))
    hal = get_status(receipt.get("hal_verdict"))
    cats: set[str] = set()
    if op == "(none)":
        cats.add("NEEDS_OPERATOR")
    if hal == "(none)":
        cats.add("NEEDS_HAL")
    if hal == "NEEDS_MORE_RECEIPTS":
        cats.add("BLOCKED")
    if op == "APPROVED_FOR_SANDBOX_ONLY" and hal == "PASS":
        cats.add("READY_SANDBOX")
    if op == "REJECTED" or hal == "FAIL":
        cats.add("REJECTED")
    return cats


def _line(path: Path, receipt: dict) -> str:
    t = receipt.get("receipt_timestamp_utc", "????-??-??T??:??:??Z")
    topic = (extract_topic(receipt) or "(no topic)")[:48]
    op = get_status(receipt.get("operator_decision"))
    hal = get_status(receipt.get("hal_verdict"))
    env = "envOK" if receipt.get("envelope_complete") else "envFAIL"
    return f"{t}  {env}  op={op}  hal={hal}  topic='{topic}'  ({path.name})"


def render_summary(receipts) -> None:
    by_cat: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for path, r in receipts:
        for cat in classify(r):
            by_cat[cat].append((path, r))
    print(f"=== REVIEW QUEUE  ({len(receipts)} receipt(s) total) ===\n")
    for cat in CATEGORIES:
        items = by_cat.get(cat, [])
        print(f"[{cat}]  {len(items)}")
        for path, r in items:
            print(f"  - {_line(path, r)}")
        if not items:
            print("  (empty)")
        print()


def render_filtered(filtered: list[tuple[Path, dict, set[str]]]) -> None:
    if not filtered:
        print("(no matching receipts)")
        return
    print(f"=== {len(filtered)} matching receipt(s) ===\n")
    for path, r, cats in filtered:
        tag = ",".join(sorted(cats)) or "(no category)"
        print(f"  {_line(path, r)}  [{tag}]")


def apply_filters(receipts, args) -> list[tuple[Path, dict, set[str]]]:
    """AND-combine the active filters. Topic is a case-insensitive substring."""
    active = {
        "NEEDS_OPERATOR": args.needs_operator,
        "NEEDS_HAL": args.needs_hal,
        "BLOCKED": args.blocked,
        "READY_SANDBOX": args.ready_sandbox,
        "REJECTED": args.rejected,
    }
    required_cats = {c for c, on in active.items() if on}
    topic_needle = args.topic.lower() if args.topic else None

    out: list[tuple[Path, dict, set[str]]] = []
    for path, r in receipts:
        cats = classify(r)
        if required_cats and not required_cats.issubset(cats):
            continue
        if topic_needle is not None:
            topic = extract_topic(r).lower()
            if topic_needle not in topic:
                continue
        out.append((path, r, cats))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_PROPOSAL_DIR),
        help="proposal directory to scan",
    )
    parser.add_argument("--needs-operator", action="store_true",
                        help="operator_decision is null")
    parser.add_argument("--needs-hal", action="store_true",
                        help="hal_verdict is null")
    parser.add_argument("--blocked", action="store_true",
                        help="hal_verdict.status == NEEDS_MORE_RECEIPTS")
    parser.add_argument("--ready-sandbox", action="store_true",
                        help="operator APPROVED_FOR_SANDBOX_ONLY + HAL PASS")
    parser.add_argument("--rejected", action="store_true",
                        help="operator REJECTED or HAL FAIL")
    parser.add_argument("--topic", metavar="STR",
                        help="case-insensitive substring filter on topic")
    args = parser.parse_args()

    receipts = load_receipts(Path(args.dir))
    if not receipts:
        print(f"[queue] no receipts found in {args.dir}.")
        return 0

    has_filter = any([
        args.needs_operator, args.needs_hal, args.blocked,
        args.ready_sandbox, args.rejected, bool(args.topic),
    ])

    if has_filter:
        render_filtered(apply_filters(receipts, args))
    else:
        render_summary(receipts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
