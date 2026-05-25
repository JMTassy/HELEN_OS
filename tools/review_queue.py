#!/usr/bin/env python3
"""
review_queue.py

Read-only operational queue over local GEMMA_PROPOSALS and/or RALPH_PROPOSALS.

Classifies each receipt into governance categories and lets the operator
filter the working set. Used to answer "what do I need to act on now?"

Categories (a receipt may belong to several):
  NEEDS_OPERATOR  operator_decision is null
  NEEDS_HAL       hal_verdict is null
  BLOCKED         hal_verdict.status == NEEDS_MORE_RECEIPTS
  READY_SANDBOX   operator APPROVED_FOR_SANDBOX_ONLY + HAL PASS
  REJECTED        operator REJECTED or HAL FAIL

Sources:
  --source gemma  GOVERNANCE/GEMMA_PROPOSALS  (default)
  --source ralph  GOVERNANCE/RALPH_PROPOSALS
  --source all    both combined

Usage:
  python tools/review_queue.py                        # full summary (gemma)
  python tools/review_queue.py --source ralph         # RALPH proposals only
  python tools/review_queue.py --source all           # both combined
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

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = {
    "gemma": REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS",
    "ralph": REPO_ROOT / "GOVERNANCE" / "RALPH_PROPOSALS",
}

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


def _line(path: Path, receipt: dict, source_tag: str = "") -> str:
    t = receipt.get("receipt_timestamp_utc", "????-??-??T??:??:??Z")
    topic = (extract_topic(receipt) or "(no topic)")[:48]
    op = get_status(receipt.get("operator_decision"))
    hal = get_status(receipt.get("hal_verdict"))
    env = "envOK" if receipt.get("envelope_complete") else "envFAIL"
    prefix = f"[{source_tag}] " if source_tag else ""
    return f"{prefix}{t}  {env}  op={op}  hal={hal}  topic='{topic}'  ({path.name})"


def render_summary(tagged_receipts: list[tuple[Path, dict, str]]) -> None:
    by_cat: dict[str, list[tuple[Path, dict, str]]] = defaultdict(list)
    for path, r, src in tagged_receipts:
        for cat in classify(r):
            by_cat[cat].append((path, r, src))
    print(f"=== REVIEW QUEUE  ({len(tagged_receipts)} receipt(s) total) ===\n")
    for cat in CATEGORIES:
        items = by_cat.get(cat, [])
        print(f"[{cat}]  {len(items)}")
        for path, r, src in items:
            print(f"  - {_line(path, r, src)}")
        if not items:
            print("  (empty)")
        print()


def render_filtered(filtered: list[tuple[Path, dict, str, set[str]]]) -> None:
    if not filtered:
        print("(no matching receipts)")
        return
    print(f"=== {len(filtered)} matching receipt(s) ===\n")
    for path, r, src, cats in filtered:
        tag = ",".join(sorted(cats)) or "(no category)"
        print(f"  {_line(path, r, src)}  [{tag}]")


def apply_filters(
    tagged_receipts: list[tuple[Path, dict, str]], args
) -> list[tuple[Path, dict, str, set[str]]]:
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

    out: list[tuple[Path, dict, str, set[str]]] = []
    for path, r, src in tagged_receipts:
        cats = classify(r)
        if required_cats and not required_cats.issubset(cats):
            continue
        if topic_needle is not None:
            topic = extract_topic(r).lower()
            if topic_needle not in topic:
                continue
        out.append((path, r, src, cats))
    return out


def _load_tagged(source: str) -> list[tuple[Path, dict, str]]:
    """Load receipts from the named source(s), tagging each with its source label."""
    if source == "all":
        sources = list(SOURCE_DIRS.keys())
    else:
        sources = [source]

    tagged: list[tuple[Path, dict, str]] = []
    for src_name in sources:
        src_dir = SOURCE_DIRS[src_name]
        if not src_dir.exists():
            print(f"[queue] directory not found, skipping: {src_dir}", file=__import__("sys").stderr)
            continue
        label = src_name.upper()
        for path, receipt in load_receipts(src_dir):
            tagged.append((path, receipt, label))
    return tagged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=["gemma", "ralph", "all"],
        default="gemma",
        help="receipt source: gemma (default), ralph, or all",
    )
    parser.add_argument(
        "--dir",
        default=None,
        help="explicit proposal directory (overrides --source)",
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

    if args.dir is not None:
        raw = load_receipts(Path(args.dir))
        tagged = [(p, r, "CUSTOM") for p, r in raw]
        label = args.dir
    else:
        tagged = _load_tagged(args.source)
        label = args.source

    if not tagged:
        print(f"[queue] no receipts found (source={label}).")
        return 0

    has_filter = any([
        args.needs_operator, args.needs_hal, args.blocked,
        args.ready_sandbox, args.rejected, bool(args.topic),
    ])

    if has_filter:
        render_filtered(apply_filters(tagged, args))
    else:
        render_summary(tagged)
    return 0


if __name__ == "__main__":
    sys.exit(main())
