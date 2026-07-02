#!/usr/bin/env python3
"""Lifecycle stub inserter -- the fix for AR-TERMINATION-002's finding
that 0/931 PROPOSED items have an owner, review_date, or kill_criterion.

DRY-RUN BY DEFAULT. Never writes without --apply. Even with --apply,
this is a large-blast-radius change (potentially 900+ files) and should
not be run against the full repo without explicit operator confirmation
-- see the safety note in the CLI help below.

Usage:
    python3 temple/autoresearch/lifecycle_stub_inserter.py            # dry-run, all PROPOSED files
    python3 temple/autoresearch/lifecycle_stub_inserter.py --sample 5 # dry-run, show 5 examples in full
    python3 temple/autoresearch/lifecycle_stub_inserter.py --apply --limit 10   # actually write, capped
    python3 temple/autoresearch/lifecycle_stub_inserter.py --apply    # actually write, ALL matching files
                                                                        # (requires typing CONFIRM at prompt)
"""
import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from temple.autoresearch.ar_termination_002 import (  # noqa: E402
    iter_text_files, classify_file, has_any,
    OWNER_PATTERNS, REVIEW_DATE_PATTERNS, KILL_CRITERION_PATTERNS,
)

REVIEW_WINDOW_DAYS = 14


def find_candidates():
    candidates = []
    for path in iter_text_files():
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            continue
        states = classify_file(text)
        if "PROPOSED" not in states:
            continue
        missing = []
        if not has_any(OWNER_PATTERNS, text):
            missing.append("owner")
        if not has_any(REVIEW_DATE_PATTERNS, text):
            missing.append("review_date")
        if not has_any(KILL_CRITERION_PATTERNS, text):
            missing.append("kill_criterion")
        if missing:
            candidates.append((path, missing, text))
    return candidates


def build_stub(missing, review_date):
    lines = []
    if "owner" in missing:
        lines.append("owner: unassigned -- needs operator confirmation")
    if "review_date" in missing:
        lines.append(f"review_date: {review_date}")
    if "kill_criterion" in missing:
        lines.append("kill_criterion: superseded or deleted if not reviewed by review_date")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="actually write files (default: dry-run only)")
    ap.add_argument("--limit", type=int, default=None, help="cap the number of files touched with --apply")
    ap.add_argument("--sample", type=int, default=3, help="how many full examples to print in dry-run")
    args = ap.parse_args()

    candidates = find_candidates()
    review_date = (datetime.now(timezone.utc) + timedelta(days=REVIEW_WINDOW_DAYS)).strftime("%Y-%m-%d")

    print(f"AR-TERMINATION-002 follow-up: lifecycle stub inserter")
    print(f"candidates (PROPOSED, missing >=1 of owner/review_date/kill_criterion): {len(candidates)}")
    print(f"review_date to be stamped: {review_date} (+{REVIEW_WINDOW_DAYS}d)\n")

    if not args.apply:
        print(f"DRY RUN -- no files written. Showing {min(args.sample, len(candidates))} examples:\n")
        for path, missing, _ in candidates[: args.sample]:
            rel = os.path.relpath(path)
            print(f"  {rel}")
            print(f"    missing: {', '.join(missing)}")
            print(f"    would append:")
            for line in build_stub(missing, review_date).splitlines():
                print(f"      {line}")
            print()
        print(f"To actually write (capped): --apply --limit N")
        print(f"To write to ALL {len(candidates)} candidates: --apply  (will ask for typed confirmation)")
        return

    targets = candidates[: args.limit] if args.limit else candidates
    if not args.limit and len(candidates) > 20:
        print(f"⚠ About to APPEND a lifecycle stub to {len(candidates)} files. This is additive-only")
        print(f"  (appends 2-3 lines, does not delete or rewrite existing content) but touches a lot")
        print(f"  of files at once. Type CONFIRM to proceed, anything else to abort:")
        resp = input("> ").strip()
        if resp != "CONFIRM":
            print("Aborted. No files written.")
            return

    written = 0
    for path, missing, text in targets:
        stub = build_stub(missing, review_date)
        marker = "\n\n<!-- lifecycle stub, AR-TERMINATION-002 follow-up -->\n" + stub + "\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(marker)
        written += 1
    print(f"Wrote lifecycle stubs to {written} files.")


if __name__ == "__main__":
    main()
