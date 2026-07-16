#!/usr/bin/env python3
"""
ci_outbox_guard.py — CI Gate for the Consumption Organ

Fails the build (exit 1) if unconsumed AUTORESEARCH packets exceed threshold.

This "installs" the CI part of the trio for property ③.

Run in CI on every push to garden/temple layers:
  python temple/autoresearch/ci_outbox_guard.py --max-unconsumed 5

authority=false · sovereign=false · canon=false
"""

import sys
from pathlib import Path
import json

OUTBOX = Path("temple/autoresearch/outbox")
LOG = Path("temple/autoresearch/consumption_log.ndjson")


def _pen():
    """Import the operator pen (the hand). The guard measures ITS marks only."""
    try:
        from temple.autoresearch import operator_pen as pen
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        import operator_pen as pen
    return pen


def count_unconsumed(outbox: Path = OUTBOX, log: Path = LOG) -> int:
    """Packets with NO operator mark in the pen's hash-chained log.

    Anatomy (operator-ruled 2026-07-06): triage receipts do NOT count —
    grouping ⊬ consumption; only an operator_pen mark consumes. Fails
    closed (SystemExit) if the decision-log chain is broken: a tampered
    log means the consumption count cannot be trusted.
    """
    pen = _pen()
    entries = pen.read_log(log)
    broken = pen.verify_chain(entries)
    if broken:
        raise SystemExit(
            f"❌ BUILD FAIL: consumption log chain broken ({broken}) — "
            "guard fails closed; repair the log before counting")
    eff = pen.effective_decisions(entries)
    return sum(1 for p in outbox.glob("AR-*.json") if p.stem not in eff)

def main(max_unconsumed: int = 5):
    count = count_unconsumed()
    print(f"Outbox unconsumed: {count} (threshold {max_unconsumed})")
    if count > max_unconsumed:
        print("❌ BUILD FAIL: too many unconsumed packets.")
        print("   eye:  python3 temple/autoresearch/outbox_triage.py --themes")
        print("   hand: python3 temple/autoresearch/operator_pen.py --mark <AR-id> --decision <acted|rejected|deferred> --note '...'")
        sys.exit(1)
    print("✅ Outbox consumption gate passed.")
    sys.exit(0)

if __name__ == "__main__":
    max_u = 5
    for arg in sys.argv[1:]:
        if arg.startswith("--max-unconsumed="):
            max_u = int(arg.split("=",1)[1])
    main(max_unconsumed=max_u)