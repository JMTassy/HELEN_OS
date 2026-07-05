#!/usr/bin/env python3
"""
outbox_guard.py — CI gate for the autoresearch consumption loop

"A pipeline that only produces is a graveyard with receipts."

Fails the build when the outbox is becoming a graveyard:
  1. any packet is BAD_JSON (emptiness may not sit disguised as content)
  2. unconsumed packet count exceeds OUTBOX_MAX_UNCONSUMED (default 30)
  3. the consumption log hash chain is broken (tampered garden sidecar)
  4. a consumption entry references a packet whose bytes changed since it
     was judged (decision no longer binds to what exists)

authority: false · sovereign: false · ledger_effect: none
This guards the GARDEN sidecar, not the sovereign ledger. exit 0 PASS / 1 FAIL.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from temple.autoresearch.outbox_mark import (   # noqa: E402
    load_packets, read_log, verify_chain, effective_decisions, unconsumed,
    DEFAULT_OUTBOX, DEFAULT_LOG,
)


def run_guard(outbox: Path = DEFAULT_OUTBOX, log: Path = DEFAULT_LOG,
              max_unconsumed: int | None = None) -> tuple[bool, list[str]]:
    if max_unconsumed is None:
        max_unconsumed = int(os.environ.get("OUTBOX_MAX_UNCONSUMED", "30"))
    findings: list[str] = []
    packets = load_packets(outbox)
    entries = read_log(log)

    bad = [p["packet_id"] for p in packets if p.get("finding_type") == "BAD_JSON"]
    if bad:
        findings.append(f"BAD_JSON packets present: {bad}")

    broken = verify_chain(entries)
    if broken:
        findings.append(f"consumption log chain broken: {broken}")

    by_id = {p["packet_id"]: p for p in packets}
    for e in entries:
        p = by_id.get(e["packet_id"])
        if p is not None and p["_sha256"] != e.get("packet_sha256"):
            findings.append(f"packet {e['packet_id']} changed after decision "
                            f"(sha mismatch) — re-judge required")

    un = unconsumed(packets, effective_decisions(entries))
    if len(un) > max_unconsumed:
        findings.append(f"unconsumed={len(un)} exceeds ceiling {max_unconsumed} "
                        f"— the graveyard alarm")

    ok = not findings
    print("🛡  OUTBOX GUARD")
    print(f"  packets={len(packets)} decided={len(effective_decisions(entries))} "
          f"unconsumed={len(un)} ceiling={max_unconsumed}")
    if ok:
        headroom = max_unconsumed - len(un)
        print(f"  ✅ PASS (headroom {headroom})")
        if headroom <= 5:
            print("  🟡 warning: consumption budget nearly spent — triage soon")
    else:
        for f in findings:
            print(f"  🔴 {f}")
        print("  FAIL — consume, reject, or repair before merging")
    return ok, findings


if __name__ == "__main__":
    ok, _ = run_guard()
    sys.exit(0 if ok else 1)
