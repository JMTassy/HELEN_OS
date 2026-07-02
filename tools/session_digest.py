#!/usr/bin/env python3
"""Session bootstrap digest -- one command, one screen, instead of
manually re-reading STATE.md + memory.md + ROUTING.md + LOOPS.md +
git status + checking routing drift by hand every session.

This is the single highest-recurring-cost item this operator has paid
this whole session: re-deriving context that was already written down
somewhere. This script doesn't replace reading the source files when
you need depth -- it tells you which of them actually changed and
what's overdue, so you know WHERE to look instead of reading all four
cold every time.

Usage: python3 tools/session_digest.py
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)


def run(cmd):
    try:
        out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=15)
        return out.stdout.strip()
    except Exception as e:
        return f"<error: {e}>"


def section(title):
    print(f"\n{'─'*3} {title} {'─'*(60-len(title))}")


def read_file(rel):
    p = os.path.join(REPO_ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def last_touched(rel):
    ts = run(["git", "log", "-1", "--format=%cr", "--", rel])
    return ts or "never committed"


def main():
    print("🏛️ HELEN SESSION DIGEST")
    print(f"   generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    # ── git state ──────────────────────────────────────────────
    section("GIT")
    branch = run(["git", "branch", "--show-current"])
    status = run(["git", "status", "--short"])
    ahead = run(["git", "log", "@{u}..HEAD", "--oneline"]) if run(["git", "rev-parse", "--abbrev-ref", "@{u}"]) else ""
    print(f"branch: {branch}")
    print(f"uncommitted changes: {len(status.splitlines()) if status else 0}")
    if status:
        for line in status.splitlines()[:10]:
            print(f"  {line}")
    last_commit = run(["git", "log", "-1", "--format=%h %s (%cr)"])
    print(f"last commit: {last_commit}")

    # ── STATE.md freshness + open items ───────────────────────
    section("STATE.md (stage 5 -- resume, don't restart)")
    state = read_file(".claude/STATE.md")
    if state is None:
        print("MISSING -- no compounding memory found. First session, or it was never written.")
    else:
        print(f"last touched: {last_touched('.claude/STATE.md')}")
        m = re.search(r"## Open failures.*?\n(.*?)(?=\n## |\Z)", state, re.S)
        if m:
            open_items = [l.strip() for l in m.group(1).splitlines() if l.strip().startswith("- **")]
            print(f"open failures tracked: {len(open_items)}")
            for item in open_items:
                print(f"  {item[:110]}")
        m = re.search(r"## Last session.*?\n(.*)", state, re.S)
        if m:
            print("last session summary:")
            print(f"  {m.group(1).strip()[:400]}")

    # ── model routing drift ───────────────────────────────────
    section("MODEL ROUTING DRIFT")
    try:
        from tools.model_registry import check_drift
        drift, migrations = check_drift()
        if not drift and not migrations:
            print("no known drift")
        else:
            for role, entry in drift.items():
                print(f"  DRIFT  {role}: {entry['status']}")
            for mgn in migrations:
                print(f"  OPEN MIGRATION: {mgn}")
    except Exception as e:
        print(f"  registry not readable ({e}) -- run tools/model_registry.py --check-drift directly")

    # ── PROPOSED items overdue for review ─────────────────────
    section("GOVERNANCE -- overdue PROPOSED items")
    receipt_path = "temple/autoresearch/AR_TERMINATION_002_RECEIPT.md"
    receipt = read_file(receipt_path)
    if receipt:
        # anchored to line start + date-shaped value, so this can't match a
        # prose mention of the field name elsewhere in the document (found
        # during QA: the unanchored version matched "`review_date:` /" in
        # the descriptive text above the real field and silently dropped
        # the whole line via the except-pass below)
        m = re.search(r"^review_date:\s*(\d{4}-\d{2}-\d{2})", receipt, re.MULTILINE)
        if m:
            due = datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_left = (due - datetime.now(timezone.utc)).days
            if days_left < 0:
                print(f"  ⚠ {receipt_path} is OVERDUE for review ({-days_left}d past {m.group(1)})")
            else:
                print(f"  {receipt_path}: due for review in {days_left}d ({m.group(1)})")
        else:
            print(f"  {receipt_path}: no review_date field found (should not happen -- check format)")
        m2 = re.search(r"STALE_PENDING\s*=\s*\*\*(\d+)", receipt)
        if m2:
            print(f"  last known stale-PROPOSED count: {m2.group(1)} (from AR-TERMINATION-002 -- rerun for current)")
    else:
        print("  no termination receipt found yet -- run temple/autoresearch/ar_termination_002.py")

    # ── what to read next, ranked ──────────────────────────────
    section("READ NEXT, IN ORDER")
    print("  1. this digest's OPEN items above (not the full STATE.md, unless depth is needed)")
    print("  2. .claude/memory.md 'Session Decisions Log' -- only the newest rows")
    print("  3. CLAUDE.md 'Current State' -- only if this is a fresh session with no STATE.md")
    print("  (ROUTING.md / LOOPS.md are reference docs -- read on demand, not every session)")


if __name__ == "__main__":
    main()
