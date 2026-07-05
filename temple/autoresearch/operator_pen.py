#!/usr/bin/env python3
"""
operator_pen.py — The Operator's Pen (per-packet decision log)

Records OPERATOR decisions on autoresearch outbox packets. Companion to:
  outbox_triage.py  — the lens (groups packets into themes)
  outbox_consume.py — the router (consumes TRIAGE receipts into routed actions)
This module is the final pen: the per-packet, hash-chained record of what the
operator actually decided. The guard (scripts/outbox_guard.py) counts a packet
as consumed ONLY when it has an operator mark here.

authority: false
sovereign: false
canon: false
ledger_effect: none

LAW OF THE PEN
  - Only the operator decides. This tool RECORDS decisions; it never makes
    them. An agent invoking --mark on its own initiative is self-stamping
    (Agent admits ≡ REDUCER admits — authority laundering).
  - The decision log is a GARDEN sidecar (temple/autoresearch/
    consumption_log.ndjson), append-only, hash-chained for tamper evidence.
    It is NOT the sovereign ledger and never routes to it.
  - Every decision binds to the sha256 of the exact packet bytes it judged
    (NO HASH = NO VOICE, applied locally).
  - Failure is classified, never synthesized: unreadable packets surface as
    named BAD_JSON findings. A BAD_JSON packet can be 'rejected', never
    'acted' — you cannot act on content that does not exist.

Decisions: acted | rejected | deferred
  acted    — the packet's recommendation was turned into bounded work
  rejected — the packet was judged not worth acting on (with a note)
  deferred — seen and postponed (counts as consumed; resurface via --list --all)

Usage:
  python temple/autoresearch/operator_pen.py --list
  python temple/autoresearch/operator_pen.py --list --all
  python temple/autoresearch/operator_pen.py --mark AR-xxxx --decision acted \
      --note "built tests/test_foo.py" [--operator JM]
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_OUTBOX = Path("temple/autoresearch/outbox")
DEFAULT_LOG = Path("temple/autoresearch/consumption_log.ndjson")
DECISIONS = ("acted", "rejected", "deferred")
GENESIS = "GENESIS"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_packets(outbox: Path) -> List[Dict[str, Any]]:
    """Load all packets; unreadable ones become named BAD_JSON findings."""
    out = []
    for p in sorted(outbox.glob("AR-*.json")):
        try:
            d = json.loads(p.read_text())
            d["_path"] = str(p)
            d["_sha256"] = sha256_file(p)
            d.setdefault("packet_id", p.stem)
            out.append(d)
        except Exception as exc:
            out.append({
                "packet_id": p.stem, "_path": str(p),
                "_sha256": sha256_file(p),
                "finding_type": "BAD_JSON",
                "summary": f"unreadable packet: {exc}",
            })
    return out


def read_log(log: Path) -> List[Dict[str, Any]]:
    if not log.exists():
        return []
    entries = []
    for line in log.read_text().splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def verify_chain(entries: List[Dict[str, Any]]) -> Optional[str]:
    """Return None if the hash chain is intact, else a description of the break."""
    prev = GENESIS
    for i, e in enumerate(entries):
        if e.get("prev") != prev:
            return f"entry {i} ({e.get('packet_id')}): prev mismatch"
        body = {k: v for k, v in e.items() if k != "entry_hash"}
        want = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if e.get("entry_hash") != want:
            return f"entry {i} ({e.get('packet_id')}): entry_hash mismatch"
        prev = e["entry_hash"]
    return None


def effective_decisions(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Latest decision per packet_id (log is append-only; latest wins)."""
    eff: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        eff[e["packet_id"]] = e
    return eff


def unconsumed(packets: List[Dict[str, Any]], eff: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [p for p in packets if p["packet_id"] not in eff]


def mark(outbox: Path, log: Path, packet_id: str, decision: str,
         note: str, operator: str) -> Dict[str, Any]:
    if decision not in DECISIONS:
        raise SystemExit(f"BLOCK: decision must be one of {DECISIONS}, got {decision!r}")
    if not note.strip():
        raise SystemExit("BLOCK: a decision without a note is not a decision — --note required")
    packets = {p["packet_id"]: p for p in load_packets(outbox)}
    if packet_id not in packets:
        raise SystemExit(f"BLOCK: {packet_id} not found in {outbox} — cannot judge a phantom")
    pkt = packets[packet_id]
    if pkt.get("finding_type") == "BAD_JSON" and decision == "acted":
        raise SystemExit("BLOCK: BAD_JSON packet cannot be 'acted' — content does not exist; "
                         "reject it or repair the packet first")
    entries = read_log(log)
    broken = verify_chain(entries)
    if broken:
        raise SystemExit(f"BLOCK: decision log chain broken ({broken}) — repair before writing")
    prev = entries[-1]["entry_hash"] if entries else GENESIS
    body = {
        "schema": "CONSUMPTION_ENTRY_V0",
        "packet_id": packet_id,
        "packet_sha256": pkt["_sha256"],
        "decision": decision,
        "note": note,
        "operator": operator,
        "at": datetime.now(timezone.utc).isoformat(),
        "authority": False,
        "sovereign": False,
        "ledger_effect": "none",
        "prev": prev,
    }
    body["entry_hash"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with log.open("a") as f:
        f.write(json.dumps(body, separators=(",", ":")) + "\n")
    return body


def cmd_list(outbox: Path, log: Path, show_all: bool) -> int:
    packets = load_packets(outbox)
    entries = read_log(log)
    broken = verify_chain(entries)
    eff = effective_decisions(entries)
    un = unconsumed(packets, eff)
    print("🖋  OUTBOX MARK (the operator's pen)")
    print(f"  packets: {len(packets)} · decided: {len(eff)} · unconsumed: {len(un)}")
    if broken:
        print(f"  🔴 LOG CHAIN BROKEN: {broken}")
    for p in un:
        flag = " 🔴BAD_JSON" if p.get("finding_type") == "BAD_JSON" else ""
        print(f"    ⏳ {p['packet_id']}  [{p.get('finding_type','?')}]{flag}  {p.get('summary','')[:70]}")
    if show_all:
        for pid, e in eff.items():
            print(f"    {'✅' if e['decision']=='acted' else '🍂' if e['decision']=='rejected' else '🌫'} "
                  f"{pid}  {e['decision']}  — {e['note'][:60]}")
    print("  law: only the operator marks · log is garden sidecar, not ledger")
    return 1 if broken else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Record operator decisions on outbox packets (NON_SOVEREIGN)")
    ap.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX)
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all", action="store_true", help="with --list: also show decided packets")
    ap.add_argument("--mark", metavar="PACKET_ID")
    ap.add_argument("--decision", choices=DECISIONS)
    ap.add_argument("--note", default="")
    ap.add_argument("--operator", default="JM")
    a = ap.parse_args()
    if a.mark:
        if not a.decision:
            raise SystemExit("BLOCK: --mark requires --decision")
        e = mark(a.outbox, a.log, a.mark, a.decision, a.note, a.operator)
        print(f"🖋  recorded: {e['packet_id']} → {e['decision']}  (entry {e['entry_hash'][:12]}…)")
        print("  ledger_effect: none · garden sidecar only")
        return 0
    return cmd_list(a.outbox, a.log, a.all)


if __name__ == "__main__":
    sys.exit(main())
