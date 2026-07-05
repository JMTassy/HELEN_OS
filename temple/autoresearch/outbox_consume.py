#!/usr/bin/env python3
"""
outbox_consume.py — The Pen of the Consumption Organ

Reads a TRIAGE_RECEIPT_V0 (or scans outbox) and "consumes" by:
- Emitting a CONSUME_RECEIPT_V0 in garden (triage/consumed/)
- Suggesting or simulating routing to bounded tranches
- Never mutating the outbox or sovereign paths

This is the "install" of the consumer: triage lens + consume pen.

authority=false · sovereign=false · canon=false · ledger_effect=none

Usage:
  python temple/autoresearch/outbox_consume.py --triage-id TRIAGE-xxx
  python temple/autoresearch/outbox_consume.py --dry  # just report

Part of closing the loop per emergent property ③.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

OUTBOX = Path("temple/autoresearch/outbox")
TRIAGE_DIR = Path("temple/autoresearch/triage")
CONSUMED_DIR = TRIAGE_DIR / "consumed"
CONSUMED_DIR.mkdir(parents=True, exist_ok=True)
RESOLVED_DIR = TRIAGE_DIR / "resolved"
RESOLVED_DIR.mkdir(parents=True, exist_ok=True)

def load_triage(triage_id: str) -> Dict[str, Any]:
    p = TRIAGE_DIR / f"{triage_id}.json"
    if not p.exists():
        raise FileNotFoundError(f"No triage {triage_id}")
    return json.loads(p.read_text())

def consume(triage: Dict[str, Any], dry: bool = False) -> Dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()
    consume_id = "CONSUME-" + hashlib.sha256((triage['triage_id'] + ts).encode()).hexdigest()[:12]
    
    actions = []
    for rec in triage.get("recommended_actions", []):
        if "outbox_consumer" in rec:
            actions.append({"action": "NOTED", "detail": rec, "status": "simulated"})
        elif "CI" in rec or "validator" in rec.lower():
            actions.append({"action": "ROUTE_TO_CI_WIRING", "detail": rec, "status": "pending_operator"})
        else:
            actions.append({"action": "ROUTE_TO_BOUNDED_TRANCHE", "detail": rec, "status": "candidate"})

    receipt = {
        "schema": "CONSUME_RECEIPT_V0",
        "consume_id": consume_id,
        "from_triage": triage["triage_id"],
        "timestamp": ts,
        "packet_count_consumed": triage["packet_count"],
        "actions": actions,
        "summary": f"Consumed triage {triage['triage_id']} into {len(actions)} routed actions. No sovereign mutation.",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "source": "temple/autoresearch/outbox_consume.py"
    }

    if not dry:
        out = CONSUMED_DIR / f"{consume_id}.json"
        out.write_text(json.dumps(receipt, indent=2))
        print(f"📦 CONSUME receipt: {out}")
    else:
        print("(dry) Would emit:")
        print(json.dumps(receipt, indent=2))

    return receipt

def mark_packet(packet_id: str, decision: str, note: str):
    """Mark a specific outbox packet as resolved/acted. Garden-only sidecar."""
    packet_path = OUTBOX / f"{packet_id}.json"
    if not packet_path.exists():
        print(f"Packet {packet_id} not found in outbox.")
        return
    mark = {
        "packet_id": packet_id,
        "decision": decision,
        "note": note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authority": False,
        "source": "outbox_consume.py --mark"
    }
    out = RESOLVED_DIR / f"{packet_id}_marked.json"
    out.write_text(json.dumps(mark, indent=2))
    print(f"✅ Marked {packet_id} as {decision}: {out}")

def main(triage_id: str = None, dry: bool = False, mark_packet_id: str = None, decision: str = None, note: str = None):
    if mark_packet_id:
        mark_packet(mark_packet_id, decision or "acted", note or "")
        return

    if not triage_id:
        latest = sorted(TRIAGE_DIR.glob("TRIAGE-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not latest:
            print("No triage receipts found.")
            return
        triage_id = latest[0].stem
        print(f"Auto-selected latest: {triage_id}")

    triage = load_triage(triage_id)
    print(f"Consuming {triage_id} ({triage['packet_count']} packets, {len(triage['themes'])} themes)")

    receipt = consume(triage, dry=dry)
    print("Membrane: triage lens → consume pen → claimable action. No ledger write.")

if __name__ == "__main__":
    import sys
    triage_id = None
    dry = "--dry" in sys.argv
    mark_id = None
    decision = None
    note = None
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--triage-id="):
            triage_id = arg.split("=",1)[1]
        elif arg == "--mark":
            if i + 1 < len(sys.argv):
                mark_id = sys.argv[i+1]
                i += 1
        elif arg.startswith("--decision="):
            decision = arg.split("=",1)[1]
        elif arg.startswith("--note="):
            note = arg.split("=",1)[1]
        i += 1
    main(triage_id=triage_id, dry=dry, mark_packet_id=mark_id, decision=decision, note=note)