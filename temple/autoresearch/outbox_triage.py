#!/usr/bin/env python3
"""outbox_triage.py — the consumer lens for the AUTORESEARCH outbox.

NON_SOVEREIGN | authority=false | ledger=SLEEPING

The 3-epoch FABLE_GEMMA loop (2026-07-03) surfaced the bottleneck: packets are
generated, validated, and held — but never consumed. This tool is the missing
organ: it lists unconsumed packets, groups them by finding_type, ranks them,
and renders the operator decision queue.

It records operator decisions ONLY via an explicit --mark command (JM decides;
this tool never decides). Decisions land in triage_state.json beside the outbox
— a local, non-sovereign consumption record. It is NOT the ledger and carries
no constitutional weight.

Usage:
    python3 outbox_triage.py                    # render decision queue (text)
    python3 outbox_triage.py --format md        # render as markdown
    python3 outbox_triage.py --all              # include already-triaged packets
    python3 outbox_triage.py --mark AR-xxxx DECISION [--note "..."]
        DECISION in: COMMIT_PACKET | BUILD_TASK | COMPOST | DISCARD | DEFER
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
OUTBOX = HERE / "outbox"
STATE_FILE = HERE / "triage_state.json"

VALID_DECISIONS = ("COMMIT_PACKET", "BUILD_TASK", "COMPOST", "DISCARD", "DEFER")

# risk first (unaddressed danger), then test_gap (missing rails), then the rest
TYPE_PRIORITY = {
    "risk": 0,
    "test_gap": 1,
    "doc_gap": 2,
    "proposal": 3,
    "quest_candidate": 4,
    "compost_candidate": 5,
}


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"schema": "TRIAGE_STATE_V0", "authority": False, "decisions": {}}


def save_state(state: dict) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE_FILE)


def load_packets() -> list[dict]:
    packets = []
    for p in sorted(OUTBOX.glob("AR-*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            packets.append({"packet_id": p.stem, "finding_type": "risk",
                            "summary": f"UNREADABLE PACKET: {e}", "risk_flags": ["corrupt_packet"],
                            "source_refs": [str(p)], "_corrupt": True})
            continue
        packets.append(d)
    return packets


def sort_key(p: dict) -> tuple:
    return (TYPE_PRIORITY.get(p.get("finding_type", ""), 9), p.get("packet_id", ""))


def render(packets: list[dict], state: dict, fmt: str, show_all: bool) -> str:
    decisions = state.get("decisions", {})
    unconsumed = [p for p in packets if p.get("packet_id") not in decisions]
    shown = packets if show_all else unconsumed
    shown = sorted(shown, key=sort_key)

    groups: dict[str, list[dict]] = {}
    for p in shown:
        groups.setdefault(p.get("finding_type", "?"), []).append(p)

    lines: list[str] = []
    h = (lambda s: f"## {s}") if fmt == "md" else (lambda s: f"=== {s} ===")
    lines.append(h("OUTBOX TRIAGE — operator decision queue"))
    lines.append(f"packets: {len(packets)} total · {len(unconsumed)} unconsumed · "
                 f"{len(decisions)} decided")
    lines.append("authority=false · this queue proposes; only the operator decides")
    lines.append("")
    for ftype in sorted(groups, key=lambda t: TYPE_PRIORITY.get(t, 9)):
        lines.append(h(f"{ftype.upper()}  ({len(groups[ftype])})"))
        for p in groups[ftype]:
            pid = p.get("packet_id", "?")
            mark = decisions.get(pid, {}).get("decision", "⏳ UNDECIDED")
            flags = ",".join(p.get("risk_flags", [])) or "-"
            summary = (p.get("summary", "") or "")[:140]
            refs = "; ".join(p.get("source_refs", [])[:3])
            if fmt == "md":
                lines.append(f"- **{pid}** [{mark}] flags:`{flags}`")
                lines.append(f"  - {summary}")
                lines.append(f"  - refs: `{refs}`")
            else:
                lines.append(f"  {pid}  [{mark}]  flags:{flags}")
                lines.append(f"    {summary}")
                lines.append(f"    refs: {refs}")
        lines.append("")
    lines.append(h("DECISIONS AVAILABLE"))
    lines.append("  " + " | ".join(VALID_DECISIONS)
                 + "   (record with: --mark <PACKET_ID> <DECISION>)")
    return "\n".join(lines)


def mark(packet_id: str, decision: str, note: str) -> int:
    if decision not in VALID_DECISIONS:
        print(f"INVALID DECISION {decision!r} — must be one of {VALID_DECISIONS}")
        return 1
    ids = {p.get("packet_id") for p in load_packets()}
    if packet_id not in ids:
        print(f"UNKNOWN PACKET {packet_id!r} — not in outbox")
        return 1
    state = load_state()
    state["decisions"][packet_id] = {
        "decision": decision,
        "note": note,
        "decided_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "decided_by": "operator",
    }
    save_state(state)
    print(f"MARKED {packet_id} → {decision}  (recorded in triage_state.json; non-sovereign)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--format", choices=("text", "md"), default="text")
    ap.add_argument("--all", action="store_true", help="include triaged packets")
    ap.add_argument("--mark", nargs=2, metavar=("PACKET_ID", "DECISION"))
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    if args.mark:
        return mark(args.mark[0], args.mark[1], args.note)

    print(render(load_packets(), load_state(), args.format, args.all))
    return 0


if __name__ == "__main__":
    sys.exit(main())
