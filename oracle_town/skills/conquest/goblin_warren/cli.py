#!/usr/bin/env python3
"""
Minimal CLI stub for /warren (goblin_warren skill)

Usage:
  python -m oracle_town.skills.conquest.goblin_warren.cli enter --goal "Make the Brume visible"
  python -m oracle_town.skills.conquest.goblin_warren.cli status

All output is garden-only. authority=false. ledger sleeps.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
GARDEN = ROOT / "temple/gardens/goblin_garden_conquest"
RECEIPTS = GARDEN / "receipts"

def enter_warren(goal: str):
    print("🐦 ENTERING GOBLIN WARREN — CONQUEST")
    print(f"GOAL: {goal}")
    print("Garden = subconscious. Kernel = boring sovereign. Receipts only.")
    print()
    print("Current bloom (render only):")
    print("🏰 CONQUEST Core is blooming. Use the symbols. Demand receipts.")
    print()
    print("Type /goal, play epochs, surface dreams, then /verdict when ready.")
    print("All changes stay in the garden.")

    receipt = {
        "schema": "WARREN_ENTRY_V1",
        "turn": "live",
        "goal": goal,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "authority": False,
        "claim": "NO_CLAIM",
        "membrane": "Garden change ⊬ Kernel truth"
    }
    print("\n[WARREN_RECEIPT]")
    print(json.dumps(receipt, indent=2))

def show_status():
    print("🌿 Goblin Warren Status (render only)")
    print("TWIN_TURN ~ 223 (from live state)")
    print("DREAM_EPOCHS: 26")
    print("AR_EPOCHS: 10")
    print("All receipts authority=false. Ledger sleeps.")
    print("Skill: conquest/goblin_warren active.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    p_enter = sub.add_parser("enter")
    p_enter.add_argument("--goal", default="Explore the current bloom")
    sub.add_parser("status")
    args = parser.parse_args()

    if args.cmd == "enter":
        enter_warren(args.goal)
    elif args.cmd == "status":
        show_status()
    else:
        parser.print_help()