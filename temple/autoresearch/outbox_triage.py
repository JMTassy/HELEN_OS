#!/usr/bin/env python3
"""outbox_triage.py — the consumer lens for the AUTORESEARCH outbox.

NON_SOVEREIGN | authority=false | sovereign=false | canon=false | ledger_effect=none

MERGED TOOL (2026-07-05, operator-ruled): two independently built consumption
designs, one file.
- Decision lens (this session's committed design): list unconsumed packets,
  group by finding_type, rank, and record operator decisions ONLY via explicit
  --mark (JM decides; the tool never decides). Decisions land in
  triage_state.json — local, non-sovereign, NOT the ledger.
- Theme lens (sibling design): cluster packets into emergent themes
  (test_gap_cluster / unconsumed_queue / ci_seam), and --emit a
  TRIAGE_RECEIPT_V0 into temple/autoresearch/triage/ (garden-only, claimable,
  reducer_required).

This closes the loop: generation → compression → validation → CONSUMPTION.

Usage:
    python3 outbox_triage.py                    # decision queue (text)
    python3 outbox_triage.py --format md        # markdown render
    python3 outbox_triage.py --all              # include already-triaged packets
    python3 outbox_triage.py --themes           # add emergent-theme clustering
    python3 outbox_triage.py --emit             # write TRIAGE_RECEIPT_V0 (garden receipt)
ANATOMY (operator-ruled 2026-07-05): triage is the EYE, not the hand.
    triage  = sight  (classify · group · propose · emit candidates)
    operator_pen.py = hand (marks · consumption_log.ndjson, hash-chained)
    outbox_guard.py = immune system (unconsumed-pressure CI gate)
Hard invariant: triage_receipt ⊬ operator_mark · grouping ⊬ consumption.
The CLI therefore has NO --mark; marking lives in operator_pen.py. The mark()
function below is retained for the committed test contract (legacy
triage_state.json) and as a library shim — new code must use the pen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
OUTBOX = HERE / "outbox"
STATE_FILE = HERE / "triage_state.json"
TRIAGE_DIR = HERE / "triage"

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


# --- theme lens (sibling design, merged) --------------------------------------

def group_packets(packets: list[dict]) -> dict[str, list[dict]]:
    """Cluster packets into emergent themes (coarser than finding_type)."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for p in packets:
        ft = p.get("finding_type", "unknown")
        summary = str(p.get("summary", "")).lower()
        if "test_gap" in ft or "test" in summary:
            groups["test_gap_cluster"].append(p)
        elif "unconsumed" in summary or "queue" in summary or "consumer" in summary:
            groups["unconsumed_queue"].append(p)
        elif "ci" in summary or "validator" in summary or "garden" in summary:
            groups["ci_seam"].append(p)
        else:
            groups[ft].append(p)
    return dict(groups)


def make_triage_receipt(groups: dict[str, list[dict]], packet_count: int) -> dict:
    """TRIAGE_RECEIPT_V0 — garden-only, claimable, reducer_required."""
    ts = datetime.now(timezone.utc).isoformat()
    evidence = [f"{theme}: {len(ps)} packets e.g. {ps[0].get('packet_id') if ps else ''}"
                for theme, ps in groups.items()]
    return {
        "schema": "TRIAGE_RECEIPT_V0",
        "triage_id": "TRIAGE-" + hashlib.sha256(ts.encode()).hexdigest()[:12],
        "timestamp": ts,
        "packet_count": packet_count,
        "themes": list(groups.keys()),
        "summary": f"Outbox triage: {packet_count} packets, {len(groups)} themes.",
        "evidence": evidence,
        "recommended_actions": [
            "Review the decision queue and --mark each packet",
            "Route BUILD_TASK survivors to bounded tranches",
        ],
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "source": "temple/autoresearch/outbox_triage.py",
    }


# --- decision lens (committed design) ------------------------------------------

def render(packets: list[dict], state: dict, fmt: str, show_all: bool,
           themes: bool = False) -> str:
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
    if themes:
        tgroups = group_packets(shown)
        lines.append(h("EMERGENT THEMES"))
        for theme in sorted(tgroups):
            ex = tgroups[theme][0].get("packet_id", "") if tgroups[theme] else ""
            lines.append(f"  {theme}: {len(tgroups[theme])} (e.g. {ex})")
        lines.append("")
    lines.append(h("DECISIONS AVAILABLE"))
    lines.append("  " + " | ".join(VALID_DECISIONS)
                 + "   (record with: --mark <PACKET_ID> <DECISION>)")
    return "\n".join(lines)


def mark(packet_id: str, decision: str, note: str) -> int:
    """LEGACY decision shim (triage_state.json). The sovereign hand is
    operator_pen.mark() with its hash-chained consumption log — use that.
    Kept because the committed test contract exercises this function."""
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
    ap.add_argument("--themes", action="store_true", help="add emergent-theme clustering")
    ap.add_argument("--emit", action="store_true",
                    help="write TRIAGE_RECEIPT_V0 to triage/ (garden-only receipt)")
    ap.add_argument("--mark", nargs=2, metavar=("PACKET_ID", "DECISION"))
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    if args.mark:
        # Triage is sight, not hand: grouping ⊬ consumption.
        print("TRIAGE CANNOT CONSUME — marking belongs to the operator pen:")
        print(f"  python3 temple/autoresearch/operator_pen.py mark {args.mark[0]} "
              f"--decision {args.mark[1]}" + (f" --note \"{args.note}\"" if args.note else ""))
        return 2

    packets = load_packets()
    # Union the pen's hash-chained decisions into the view (pen wins on conflict)
    state = load_state()
    try:
        import operator_pen as pen
        eff = pen.effective_decisions(pen.read_log(pen.DEFAULT_LOG))
        merged = dict(state.get("decisions", {}))
        for pid, e in eff.items():
            merged[pid] = {"decision": e.get("decision", "?"), "note": e.get("note", "")}
        state = dict(state, decisions=merged)
    except Exception:
        pass  # pen absent/unreadable → legacy view only
    print(render(packets, state, args.format, args.all, themes=args.themes))

    if args.emit:
        TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
        receipt = make_triage_receipt(group_packets(packets), len(packets))
        out = TRIAGE_DIR / f"{receipt['triage_id']}.json"
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n📦 TRIAGE_RECEIPT_V0 emitted: {out}")
        print("   (garden-only, claimable, reducer_required=true — not the ledger)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
