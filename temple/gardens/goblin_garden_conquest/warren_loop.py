#!/usr/bin/env python3
"""
warren_loop.py — Goblin Warren Game Loop for CONQUEST (Temple simulation only)

Goblins dream -> Operator stamps -> Garden mutates -> Receipts appear -> Kernel stays boring

Core law: Garden ADMIT != Kernel ADMISSION

Non-sovereign. authority=false. sovereign=false. canon=false.
All state lives in the Garden. Ledger sleeps. Kernel untouched.

Usage:
  python warren_loop.py --goal "Make the Brume Engine visible and testable"
  (interactive: ADMIT / DENY / COMPOST when prompted)

State: scratch/warren_state.json (garden only)
Receipts: receipts/warren_*.json (claimable candidates)
"""

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# HELEN-strengthened Generative Agents memory (typed Garden Memory)
try:
    from typed_memory import GardenMemory
except Exception:
    GardenMemory = None

ROOT = Path(__file__).resolve().parent
SCRATCH = ROOT / "scratch"
SCRATCH.mkdir(exist_ok=True)
RECEIPTS = ROOT / "receipts"
RECEIPTS.mkdir(exist_ok=True)

STATE_FILE = SCRATCH / "warren_state.json"

# Simple world state template (inspired by non_sovereign_world_state.md)
DEFAULT_STATE = {
    "world": "DREAM_OF_CONQUEST",
    "sovereign": False,
    "authority": False,
    "simulation_only": True,
    "turn": 0,
    "goal": "",
    "factions": ["ROSE", "SPIRAL", "BOUND", "PERP"],
    "territories": {"brume": "neutral", "archive": "ROSE", "spiral_hall": "SPIRAL"},
    "resources": {"mushrooms": 10, "knowledge": 5, "prestige": 3},
    "cohesion": 50,
    "chaos": 10,
    "buildings": [],
    "goblin_habits": [],
    "recent_stamps": [],
    "claim_log": [],
    "last_epoch": 0,
}

GOBLINS = ["Grub", "Snort", "Lurk", "Fizz", "Moss"]

PROPOSAL_TEMPLATES = [
    {"desc": "Build a mushroom court in {territory}", "effect": {"resources.mushrooms": +5, "buildings": "mushroom_court", "cohesion": +5}},
    {"desc": "Hold a tax moon ritual", "effect": {"resources.knowledge": +3, "chaos": +5, "goblin_habits": "tax_moon"}},
    {"desc": "Erect a suspicious tower overlooking {territory}", "effect": {"prestige": +4, "chaos": +8, "buildings": "suspicious_tower"}},
    {"desc": "Start a compost disaster experiment", "effect": {"resources.mushrooms": +8, "chaos": +10, "goblin_habits": "compost_disaster"}},
    {"desc": "Form a coalition with {goblin} for laugh-holes", "effect": {"cohesion": +10, "goblin_habits": "laugh_holes"}},
    {"desc": "Dig a bench for quiet plotting", "effect": {"cohesion": +3, "buildings": "plotting_bench"}},
]

DREAM_TEMPLATES = [
    "Compost Trade alliance forms between factions.",
    "Influence Skirmish in the Brume.",
    "Weird discovery: glowing mushrooms that remember stamps.",
    "Grudge between Grub and Fizz escalates.",
    "A new quest seed surfaces in the Terrarium.",
]

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    state = DEFAULT_STATE.copy()
    return state

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def apply_effect(state, effect):
    for key, delta in effect.items():
        if key == "buildings":
            state["buildings"].append(delta)
        elif key == "goblin_habits":
            state["goblin_habits"].append(delta)
        elif key.startswith("resources."):
            res = key.split(".")[1]
            state["resources"][res] = max(0, state["resources"].get(res, 0) + delta)
        elif key in state:
            state[key] = max(0, min(100, state.get(key, 0) + delta))
    return state

def generate_proposal(state, goal):
    template = random.choice(PROPOSAL_TEMPLATES)
    territory = random.choice(list(state["territories"].keys()))
    goblin = random.choice(GOBLINS)
    desc = template["desc"].format(territory=territory, goblin=goblin)
    effect = template["effect"].copy()
    if goal:
        if "mushroom" in goal.lower() and "mushrooms" in effect:
            effect["resources.mushrooms"] = effect.get("resources.mushrooms", 0) + 3
    proposer = random.choice(GOBLINS)
    return {"proposer": proposer, "desc": desc, "effect": effect, "turn": state["turn"]}

def surface_dream(state):
    dream = random.choice(DREAM_TEMPLATES)
    print(f"\n🌙 SURFACED DREAM: {dream}")
    return {"type": "dream", "content": dream, "turn": state["turn"]}

def emit_receipt(state, event):
    rid = f"WRN-{state['turn']}-{hash(event['desc'] if 'desc' in event else event['content']) % 10000:04d}"
    receipt = {
        "schema": "WARREN_RECEIPT_V0",
        "receipt_id": rid,
        "turn": state["turn"],
        "event": event,
        "authority": False,
        "claim": "NO_CLAIM",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Garden-only claimable action. Kernel untouched."
    }
    path = RECEIPTS / f"{rid}.json"
    path.write_text(json.dumps(receipt, indent=2))
    state["claim_log"].append(rid)
    print(f"🧾 Receipt candidate: {rid} (claimable)")
    return receipt

def print_bloom(state):
    print("\n" + "="*60)
    print(f"🌿 GOBLIN WARREN — turn {state['turn']} | goal: {state.get('goal','(none)')}")
    print(f"cohesion:{state['cohesion']} chaos:{state['chaos']} mushrooms:{state['resources']['mushrooms']}")
    buildings = ", ".join(state.get("buildings", [])) or "none"
    print(f"buildings: {buildings}")
    habits = ", ".join(state.get("goblin_habits", [])) or "none"
    print(f"habits: {habits}")
    print("Garden mutates here. Kernel sleeps.")
    print("="*60)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", default="Explore the current bloom and make it more fun")
    parser.add_argument("--turns", type=int, default=8)
    args = parser.parse_args()

    state = load_state()
    state["goal"] = args.goal
    state["turn"] = state.get("turn", 0)

    print("🐦 Entering Goblin Warren...")
    print(f"Current /goal: {state['goal']}")
    print("Goblins roam, propose, you stamp. Garden only.")
    print("Core law: Garden ADMIT != Kernel ADMISSION")

    for t in range(args.turns):
        state["turn"] += 1

        # 1. Goblins Roam + 2. Propose
        proposal = generate_proposal(state, state["goal"])
        print(f"\n🧌 {proposal['proposer']} proposes: {proposal['desc']}")

        # 3. Operator Stamps
        print("Stamp? [A]dmit / [D]eny / [C]ompost (or q to quit)")
        choice = input("> ").strip().lower()

        if choice == "q":
            break

        stamp = "COMPOST"
        if choice.startswith("a"):
            stamp = "ADMIT"
        elif choice.startswith("d"):
            stamp = "DENY"

        state["recent_stamps"].append(stamp)
        if len(state["recent_stamps"]) > 5:
            state["recent_stamps"].pop(0)

        if stamp == "ADMIT":
            state = apply_effect(state, proposal["effect"])
            print("🌿 Garden mutates...")
            receipt = emit_receipt(state, proposal)
            state["claim_log"].append(receipt["receipt_id"])
        elif stamp == "DENY":
            print("Blocked.")
        else:
            print("🌱 Composted for later...")

        # 4. Garden Mutates (already applied if ADMIT)
        # 5. Dreams Surface (occasional)
        if random.random() < 0.3:
            dream = surface_dream(state)
            if random.random() < 0.5:  # sometimes claimable
                emit_receipt(state, dream)

        print_bloom(state)

        # 6. Receipts (handled above)

    save_state(state)
    print("\n🏁 Loop ended. Check receipts/ for claimables.")
    print("Kernel stayed boring. Garden bloomed (or not).")
    print("All authority=false. Ledger sleeps.")

if __name__ == "__main__":
    main()