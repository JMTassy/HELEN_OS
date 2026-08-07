#!/usr/bin/env python3
"""
tools/garden_epoch_wul.py — Render one Insight Garden epoch in HELEN OS WULmath + WULmoji.

Shows HAL-MAYOR-JESTER processing for a single epoch using:
- WULmath: HELEN OS logic sequence (governance colors + operators)
- WULmoji: AVALON grammar + garden state line

Usage:
    python3 tools/garden_epoch_wul.py E02
    python3 tools/garden_epoch_wul.py E11
    python3 tools/garden_epoch_wul.py --list

All output is garden-only (authority=false, no ledger, no canon).
"""

import json
import sys
from pathlib import Path

RUNS = Path("temple/autoresearch/insight_garden_hal_mayor/runs")

WUL_LEGEND = """\
Legend (HELEN OS + WULMOJI):
  🔵 = OBSERVED (governance color)
  ⚡ = HAL activation / verdict
  ⇄ = MAYOR reflection
  🌹 = bounded garden receipt
  📜 = receipt granted
  🛡️ = authority=false boundary
  🔗 = linked to AVALON garden epoch
  🟣 = CLAIM (not granted / deferred)
"""

def load_epoch(epoch_id: str) -> dict | None:
    matches = list(RUNS.glob(f"{epoch_id}_epoch_*.json"))
    if not matches:
        return None
    return json.loads(matches[0].read_text())

def render(epoch_id: str) -> int:
    d = load_epoch(epoch_id)
    if not d:
        print(f"Epoch {epoch_id} not found in Insight Garden runs.")
        print("Available epochs:")
        for p in sorted(RUNS.glob("E[0-9][0-9]_epoch_*.json")):
            print("  ", p.stem.split("_")[0])
        return 1

    epoch   = d["epoch"]
    insight = d["insight_id"]
    label   = d["insight_label"]
    hal     = d["hal"].get("status", "?")
    mayor   = d["mayor"]["decision"]
    score   = d["mayor"]["score"]
    granted = d.get("receipt_granted", False)
    jester  = d["jester_comment"]

    if granted:
        wulmath = "🔵⚡⇄🌹📜"
        wulmoji = f"({epoch}) 🔵 ⚡ ⇄ 🌹 📜 🛡️ 🔗#AVALON-{epoch} 🌿🌹"
        logic = "HAL=PASS → MAYOR=GRANT → BOUNDED_RECEIPT (garden_only, authority=false)"
        status = "🌹 GRANTED (bounded garden receipt)"
    else:
        wulmath = "🔵🟣🛡️"
        wulmoji = f"({epoch}) 🔵 🟣 🛡️ 🔗#AVALON-{epoch}"
        logic = f"HAL={hal} → MAYOR={mayor} → DEFER (no receipt)"
        status = "🟣 DEFERRED"

    print()
    print("┌" + "─" * 82 + "┐")
    print(f"│ HELEN OS WULmath + WULmoji — EPOCH {epoch} (Insight Garden) {' ' * 31}│")
    print("├" + "─" * 82 + "┤")
    print(f"│ Insight : {insight} — {label[:42]:<42} │")
    print(f"│ HAL     : {hal:<6}   MAYOR: {mayor:<22}   score={score:<2} │")
    print(f"│ Status  : {status}")
    print("├" + "─" * 82 + "┤")
    print("│ WULmath (HELEN OS logic sequence):")
    print(f"│   {wulmath}")
    print("├" + "─" * 82 + "┤")
    print("│ WULmoji (AVALON grammar + garden state):")
    print(f"│   {wulmoji}")
    print("├" + "─" * 82 + "┤")
    print("│ Logic:")
    print(f"│   {logic}")
    print("├" + "─" * 82 + "┤")
    jline = (jester[:66] + "...") if len(jester) > 66 else jester
    print(f"│ JESTER  : {jline}")
    print("└" + "─" * 82 + "┘")
    print()
    print(WUL_LEGEND)
    return 0

def list_epochs():
    print("Insight Garden epochs with records:")
    for p in sorted(RUNS.glob("E[0-9][0-9]_epoch_*.json")):
        ep = p.stem.split("_")[0]
        try:
            d = json.loads(p.read_text())
            flag = " ✓ GRANTED" if d.get("receipt_granted") else ""
            print(f"  {ep} — {d['insight_id']}{flag}")
        except:
            print(f"  {ep}")
    print()
    print("Usage: python3 tools/garden_epoch_wul.py E02")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("--list", "-l", "list"):
        list_epochs()
        sys.exit(0)

    epoch = sys.argv[1].upper()
    if not epoch.startswith("E"):
        epoch = "E" + epoch.zfill(2)
    sys.exit(render(epoch))
