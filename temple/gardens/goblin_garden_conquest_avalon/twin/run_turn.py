#!/usr/bin/env python3
"""
TEMPLE_CONQUEST_TWIN — run_turn.py
Advance world state by exactly 1 turn.
Non-sovereign, non-interactive, seeded-deterministic, no LLM.

AUTHORITY=false | SOVEREIGN=false | CANON=false | LEDGER=SLEEPING
"""
import json
import os
import random
import sys
from pathlib import Path

# ── PATHS ──────────────────────────────────────────────────────────────────────
SANDBOX_ROOT  = Path(__file__).parent
STATE_FILE    = SANDBOX_ROOT / "state" / "temple_world_state.json"
SESSION_LOG   = SANDBOX_ROOT / "state" / "session_log.ndjson"
DECISIONS_DIR = SANDBOX_ROOT / "state" / "decisions"
COUNTERS_FILE = SANDBOX_ROOT / "state" / "counters.json"

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
MAX_STOCKPILE = 50
ISLAND_WEIGHTS = {
    "HOME_KEEP_AVALON": 0, "ISLE_IGNIS": 2, "ISLE_AQUA": 2,
    "ISLE_AETHER": 2, "ISLE_TERRA": 2, "ISLE_QUINT": 3,
}
RANK_THRESHOLDS = [
    ("WARDEN", 1000), ("HOLDER", 500), ("SETTLER", 200), ("SCOUT", 50), ("NONE", 0),
]
ELEMENTAL_CYCLE = ["FIRE", "WATER", "AIR", "EARTH", "QUINT"]
SHARD_FOR_ELEMENT = {
    "FIRE": "IGNIS_SHARD", "WATER": "AQUA_SHARD",
    "AIR": "AETHER_SHARD", "EARTH": "TERRA_SHARD", "QUINT": "QUINT_CORE",
}

# Personality → weighted action pool
PERSONALITY_ACTIONS = {
    "QUEST_FOCUSED":    [("EXPLORE",0.30),("QUEST_STEP",0.30),("HARVEST",0.20),("WARN",0.10),("DIPLOMACY",0.10)],
    "CONQUEST_FOCUSED": [("CONQUEST",0.35),("CLAIM",0.25),("HARVEST",0.25),("EXPLORE",0.10),("WARN",0.05)],
    "DIPLOMATIC":       [("DIPLOMACY",0.35),("WARN",0.20),("EXPLORE",0.20),("HARVEST",0.15),("QUEST_STEP",0.10)],
    "RESOURCE_FOCUSED": [("HARVEST",0.45),("EXPLORE",0.20),("QUEST_STEP",0.20),("DIPLOMACY",0.10),("WARN",0.05)],
}

ACTION_COSTS = {
    "EXPLORE":    {"AETHER_SHARD": 2},
    "CLAIM":      {},   # resolved per island element below
    "QUEST_STEP": {"QUINT_CORE": 1},
    "CONQUEST":   {"QUINT_CORE": 3},
    "DIPLOMACY":  {"QUINT_CORE": 3},
    "HARVEST":    {},
    "WARN":       {},
}

FACTION_EMOJI = {"ROSE": "🌹", "CROSS": "✝️", "VEIL": "🌀", "WARDEN": "⟂◯⟂"}
STATE_EMOJI   = {"ROSE": "🟢", "CROSS": "🔴", "VEIL": "🟣", "WARDEN": "🔵"}


# ── HELPERS ────────────────────────────────────────────────────────────────────

def hard_stop(msg, code=1):
    print(f"\nHARD STOP: {msg}")
    print("AUTHORITY=false  SOVEREIGN=false  CANON=false  LEDGER=SLEEPING")
    sys.exit(code)


def rng(state, salt=0):
    seed = state["clock"]["rng_seed_base"] ^ (state["clock"]["turn"] * 1337) ^ (salt * 7)
    return random.Random(seed)


def can_afford(resources, cost):
    return all(resources.get(r, 0) >= amt for r, amt in cost.items())


def deduct(resources, cost):
    for r, amt in cost.items():
        resources[r] = resources.get(r, 0) - amt


# ── PHASE 1: LOAD ──────────────────────────────────────────────────────────────

def load_state():
    if not STATE_FILE.exists():
        hard_stop("state/temple_world_state.json not found", 10)
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    if state.get("authority") or state.get("sovereign") or state.get("canon"):
        hard_stop("FORBIDDEN: authority/sovereign/canon flag is true in world state", 11)
    return state


# ── PHASE 2: FACTION DECISIONS ─────────────────────────────────────────────────

def decide(faction_name, faction_data, state, salt):
    r = rng(state, salt)
    personality = faction_data["personality"]
    pool = PERSONALITY_ACTIONS[personality]
    actions, weights = zip(*pool)
    action_type = r.choices(list(actions), weights=list(weights), k=1)[0]

    non_home = [i for i in state["islands"] if i != "HOME_KEEP_AVALON"]
    target_island = r.choice(non_home) if non_home else "HOME_KEEP_AVALON"
    other_factions = [f for f in state["factions"] if f != faction_name]
    target_faction = r.choice(other_factions) if other_factions else None

    return {"faction": faction_name, "action_type": action_type,
            "target_island": target_island, "target_faction": target_faction}


# ── PHASE 3: ACTION RESOLUTION ─────────────────────────────────────────────────

def resolve(action, state):
    fname = action["faction"]
    atype = action["action_type"]
    target = action["target_island"]
    faction = state["factions"][fname]
    resources = faction["resources"]

    cost = dict(ACTION_COSTS.get(atype, {}))
    if atype == "CLAIM":
        element = state["islands"].get(target, {}).get("element", "QUINT")
        cost = {SHARD_FOR_ELEMENT.get(element, "QUINT_CORE"): 5}

    if not can_afford(resources, cost):
        return {"faction": fname, "action": atype, "result": "SKIP_NO_RESOURCES"}

    deduct(resources, cost)
    effect = {}

    if atype in ("HARVEST", "EXPLORE", "WARN"):
        island = state["islands"].get(target, {})
        if island.get("holder") == fname and not island.get("templock"):
            for res, rate in island.get("production", {}).items():
                res = "QUINT_CORE" if res == "any_shard" else res
                bonus = max(0, min(rate, MAX_STOCKPILE - island["stockpile"].get(res, 0)))
                island["stockpile"][res] = island["stockpile"].get(res, 0) + bonus
                resources[res] = resources.get(res, 0) + bonus
                effect[res] = bonus

    elif atype == "CLAIM":
        island = state["islands"].get(target, {})
        if island and not island.get("conquest_immune") and not island.get("templock"):
            island["ownership_score"] = island.get("ownership_score", 0) + 15
            if island["ownership_score"] > 50 and island.get("holder") != fname:
                island["holder"] = fname
                effect["claimed"] = target

    elif atype == "QUEST_STEP":
        faction["score"]["quest"] = faction["score"].get("quest", 0) + 5
        effect["quest_pts"] = 5

    elif atype == "CONQUEST":
        island = state["islands"].get(target, {})
        if island and not island.get("conquest_immune") and not island.get("templock"):
            my_total = faction["score"]["total"]
            defender = island.get("holder")
            def_total = state["factions"][defender]["score"]["total"] if defender else 0
            if my_total > def_total * 1.5 or not defender:
                island["holder"] = fname
                island["ownership_score"] = max(10, int(island.get("ownership_score", 0) * 0.5))
                effect["conquered"] = target
            else:
                effect["conquest_failed"] = target

    elif atype == "DIPLOMACY":
        target_f = action.get("target_faction")
        if target_f:
            existing = any(
                a for a in state["alliances"]
                if fname in a["parties"] and target_f in a["parties"] and a.get("active")
            )
            if not existing and len(state["alliances"]) < 4:
                state["alliances"].append({
                    "parties": [fname, target_f],
                    "formed_turn": state["clock"]["turn"],
                    "duration": 10,
                    "active": True,
                })
                effect["alliance_with"] = target_f

    return {"faction": fname, "action": atype, "result": "OK", "effect": effect}


# ── PHASE 4: EVENT TRIGGERS ────────────────────────────────────────────────────

def check_events(state):
    turn = state["clock"]["turn"]
    triggered = []

    # Faction schism
    for fname, fdata in state["factions"].items():
        if fdata.get("conflict_score", 0) > 100:
            triggered.append({"type": "FACTION_SCHISM", "faction": fname, "turn": turn, "duration": -1})
            fdata["conflict_score"] = 0

    # Elemental surge (10% chance, seeded)
    r_surge = random.Random(state["clock"]["rng_seed_base"] ^ turn ^ 99991)
    if r_surge.random() < 0.10:
        non_home = [i for i in state["islands"] if i != "HOME_KEEP_AVALON"]
        isle = r_surge.choice(non_home)
        if not any(e for e in state["active_events"] if e["type"] == "ELEMENTAL_SURGE"):
            triggered.append({"type": "ELEMENTAL_SURGE", "island": isle, "turn": turn, "duration": 3, "multiplier": 2.0})

    # Bridge storm (8% chance, seeded)
    r_storm = random.Random(state["clock"]["rng_seed_base"] ^ turn ^ 77771)
    if r_storm.random() < 0.08:
        bridge_id = r_storm.choice(list(state["bridges"].keys()))
        if not any(e for e in state["active_events"] if e["type"] == "BRIDGE_STORM"):
            triggered.append({"type": "BRIDGE_STORM", "bridge": bridge_id, "turn": turn, "duration": 2})

    # Resource drought: island at zero production for 5+ turns
    for iname, island in state["islands"].items():
        if island.get("holder") and not island.get("templock"):
            total_prod = sum(island.get("production", {}).values())
            if total_prod == 0:
                island["zero_production_turns"] = island.get("zero_production_turns", 0) + 1
                already_dry = any(
                    e for e in state["active_events"]
                    if e["type"] == "RESOURCE_DROUGHT" and e.get("island") == iname
                )
                if island["zero_production_turns"] >= 5 and not already_dry:
                    triggered.append({"type": "RESOURCE_DROUGHT", "island": iname, "turn": turn, "duration": 3, "rate_multiplier": 0.5})
            else:
                island["zero_production_turns"] = 0

    state["active_events"].extend(triggered)
    return triggered


# ── PHASE 5: EFFECT APPLICATION ───────────────────────────────────────────────

def apply_effects(state):
    turn = state["clock"]["turn"]
    expired = []

    for event in state["active_events"]:
        etype = event["type"]
        if etype == "BRIDGE_STORM":
            bridge = state["bridges"].get(event.get("bridge"))
            if bridge:
                bridge["storm"] = {"active": True, "until": turn + event.get("duration", 2)}

        # Decrement duration (skip permanent events: duration == -1)
        if event.get("duration", 0) > 0:
            event["duration"] -= 1
            if event["duration"] == 0:
                expired.append(event)

    # Remove expired; clear bridge storms
    for event in expired:
        state["active_events"].remove(event)
        if event["type"] == "BRIDGE_STORM":
            bridge = state["bridges"].get(event.get("bridge"))
            if bridge:
                bridge["storm"] = None

    # TEMPLOCK countdown
    for island in state["islands"].values():
        tl = island.get("templock")
        if tl:
            tl["turns_remaining"] = tl.get("turns_remaining", 5) - 1
            if tl["turns_remaining"] <= 0:
                island["templock"] = None

    # ISLE_QUINT neutral zone
    quint = state["islands"].get("ISLE_QUINT", {})
    if quint.get("holder"):
        quint["held_for"] = quint.get("held_for", 0) + 1
        if quint["held_for"] >= quint.get("neutral_max_turns", 3):
            quint["holder"] = None
            quint["ownership_score"] = 0
            quint["held_for"] = 0

    # Alliance score bonus + expiry
    for alliance in state["alliances"]:
        if not alliance.get("active"):
            continue
        for party in alliance["parties"]:
            if party in state["factions"]:
                state["factions"][party]["score"]["alliance"] = (
                    state["factions"][party]["score"].get("alliance", 0) + 5
                )
        if turn >= alliance.get("formed_turn", 0) + alliance.get("duration", 10):
            alliance["active"] = False

    # Elemental cycle every 20 turns
    if turn > 0 and turn % 20 == 0:
        current = state["clock"]["elemental_cycle_phase"]
        idx = ELEMENTAL_CYCLE.index(current) if current in ELEMENTAL_CYCLE else 0
        state["clock"]["elemental_cycle_phase"] = ELEMENTAL_CYCLE[(idx + 1) % len(ELEMENTAL_CYCLE)]
        state["clock"]["next_elemental_cycle_at"] = turn + 20


# ── PHASE 5b: COLLECT — island stockpile → faction resource pool ──────────────

def collect_phase(state):
    """Transfer up to 5 units/turn per resource from held island stockpile to
    the owning faction's resource pool. This bridges production to spending."""
    for island in state["islands"].values():
        holder = island.get("holder")
        if not holder or island.get("templock"):
            continue
        faction_res = state["factions"][holder]["resources"]
        for res in list(island["stockpile"]):
            available = island["stockpile"].get(res, 0)
            if available <= 0:
                continue
            res_key = "QUINT_CORE" if res == "any_shard" else res
            collect = min(available, 5)
            island["stockpile"][res] = available - collect
            faction_res[res_key] = faction_res.get(res_key, 0) + collect


# ── PHASE 6: PRODUCTION + DECAY ───────────────────────────────────────────────

def production_phase(state):
    for iname, island in state["islands"].items():
        holder = island.get("holder")
        if not holder or island.get("templock"):
            continue
        faction = state["factions"].get(holder)
        if not faction:
            continue

        # Event multiplier
        multiplier = 1.0
        for event in state["active_events"]:
            if event["type"] == "ELEMENTAL_SURGE" and event.get("island") == iname:
                multiplier = event.get("multiplier", 2.0)
            if event["type"] == "RESOURCE_DROUGHT" and event.get("island") == iname:
                multiplier = min(multiplier, event.get("rate_multiplier", 0.5))

        for res, rate in island.get("production", {}).items():
            if res == "any_shard":
                res = "QUINT_CORE"
            produced = max(0, int(rate * multiplier))
            current = island["stockpile"].get(res, 0)
            new_val = min(MAX_STOCKPILE, current + produced)
            island["stockpile"][res] = new_val

        # Decay above max
        for res in list(island["stockpile"]):
            if island["stockpile"][res] > MAX_STOCKPILE:
                island["stockpile"][res] = int(island["stockpile"][res] * 0.95)


# ── PHASE 7: SCORING ──────────────────────────────────────────────────────────

def score_phase(state):
    for fname, faction in state["factions"].items():
        # Territory: +weight per held island per turn
        territory_pts = 0
        held_any = False
        for iname, island in state["islands"].items():
            if island.get("holder") == fname and not island.get("conquest_immune"):
                territory_pts += ISLAND_WEIGHTS.get(iname, 1)
                held_any = True
        faction["score"]["territory"] = faction["score"].get("territory", 0) + territory_pts

        # Zero-territory decay
        if not held_any:
            faction["zero_territory_turns"] = faction.get("zero_territory_turns", 0) + 1
            if faction.get("zero_territory_turns", 0) >= 10:
                faction["score"]["territory"] = 0
        else:
            faction["zero_territory_turns"] = 0

        # Resource score
        stockpile_total = sum(
            island["stockpile"].get(res, 0)
            for island in state["islands"].values()
            if island.get("holder") == fname
            for res in island.get("stockpile", {})
        )
        faction["score"]["resource"] = faction["score"].get("resource", 0) + (stockpile_total // 10)

        # Total
        faction["score"]["total"] = (
            faction["score"].get("territory", 0)
            + faction["score"].get("quest", 0)
            + faction["score"].get("resource", 0)
            + faction["score"].get("alliance", 0)
        )


# ── PHASE 8: RANK UPDATE ──────────────────────────────────────────────────────

def rank_update(state):
    for faction in state["factions"].values():
        total = faction["score"]["total"]
        for rank, threshold in RANK_THRESHOLDS:
            if total >= threshold:
                faction["rank"] = rank
                break


# ── PHASE 9: TURN SUMMARY ─────────────────────────────────────────────────────

def build_summary(state, action_results, new_events):
    turn = state["clock"]["turn"]
    scores = {f: state["factions"][f]["score"]["total"] for f in state["factions"]}
    ownership = {i: state["islands"][i].get("holder") for i in state["islands"]}
    leader = max(scores, key=scores.get) if scores else "ROSE"

    wulmoji = (
        f"{STATE_EMOJI.get(leader,'⚫')} {FACTION_EMOJI.get(leader,'🌹')} "
        f"🜃🜄 📜 🔗#SIM-T{turn:04d} 🌿🌹"
    )

    return {
        "turn": turn,
        "scores": scores,
        "ownership": ownership,
        "events_triggered": [e["type"] for e in new_events],
        "active_events": [e["type"] for e in state["active_events"]],
        "alliances_active": sum(1 for a in state["alliances"] if a.get("active")),
        "action_results": action_results,
        "wulmoji": wulmoji,
        "authority": False,
        "sovereign": False,
        "canon": False,
    }


# ── COUNTERS ──────────────────────────────────────────────────────────────────

def load_counters():
    if COUNTERS_FILE.exists():
        return json.loads(COUNTERS_FILE.read_text(encoding="utf-8"))
    return {"skips_by_reason": {}, "actions_by_faction": {}, "events_by_type": {}}


def update_counters(counters, results, new_events):
    for r in results:
        f, a, res = r["faction"], r["action"], r["result"]
        # actions_by_faction[faction][action]
        counters["actions_by_faction"].setdefault(f, {})
        counters["actions_by_faction"][f][a] = counters["actions_by_faction"][f].get(a, 0) + 1
        # skips_by_reason[faction:action:result]
        if res != "OK":
            key = f"{f}:{a}:{res}"
            counters["skips_by_reason"][key] = counters["skips_by_reason"].get(key, 0) + 1
    for e in new_events:
        etype = e["type"]
        counters["events_by_type"][etype] = counters["events_by_type"].get(etype, 0) + 1
    return counters


def save_counters(counters):
    tmp = COUNTERS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(counters, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, COUNTERS_FILE)


# ── PHASE 10: PERSIST ─────────────────────────────────────────────────────────

def persist(state, summary):
    # Atomic write — write to .tmp then rename
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE_FILE)

    # Append to session log (append-only)
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("TEMPLE_CONQUEST_TWIN — run_turn.py")
    print("AUTHORITY=false | SOVEREIGN=false | CANON=false | LEDGER=SLEEPING")
    print("=" * 60)

    # PHASE 1: LOAD
    state = load_state()
    turn  = state["clock"]["turn"]
    print(f"\nTurn {turn} — world loaded")

    # External decisions hook
    decisions_file = DECISIONS_DIR / f"turn_{turn:04d}.json"
    external = {}
    if decisions_file.exists():
        external = json.loads(decisions_file.read_text(encoding="utf-8"))
        print(f"External decisions: {decisions_file.name}")

    # PHASE 2: FACTION DECISIONS
    print("\n[Phase 2: Faction decisions]")
    faction_order = sorted(
        state["factions"],
        key=lambda f: state["factions"][f]["score"]["total"],
        reverse=True,
    )
    actions = []
    for idx, fname in enumerate(faction_order):
        if fname in external:
            act = external[fname]
        else:
            act = decide(fname, state["factions"][fname], state, salt=idx)
        actions.append(act)
        print(f"  {fname:8s} [{state['factions'][fname]['personality']:20s}]  {act['action_type']} → {act['target_island']}")

    # PHASE 3: ACTION RESOLUTION
    print("\n[Phase 3: Action resolution]")
    results = []
    for act in actions:
        r = resolve(act, state)
        results.append(r)
        effect_str = str(r.get("effect", {})) if r["result"] == "OK" else r["result"]
        print(f"  {r['faction']:8s}: {r['action']:12s} → {effect_str}")

    # PHASE 4: EVENT TRIGGERS
    print("\n[Phase 4: Event triggers]")
    new_events = check_events(state)
    if new_events:
        for e in new_events:
            print(f"  EVENT: {e['type']}")
    else:
        print("  (none)")

    # PHASE 5: EFFECTS
    print("\n[Phase 5: Effect application]")
    apply_effects(state)
    print("  TEMPLOCK check, ISLE_QUINT reset, alliance bonus, elemental cycle — applied")

    # PHASE 5b: COLLECT
    print("\n[Phase 5b: Collect — island stockpile → faction resources]")
    collect_phase(state)
    for fname in faction_order:
        res = {k: v for k, v in state["factions"][fname]["resources"].items() if v > 0}
        if res:
            print(f"  {fname:8s}: wallet={res}")

    # PHASE 6: PRODUCTION
    print("\n[Phase 6: Production]")
    production_phase(state)
    for iname, island in state["islands"].items():
        if island.get("holder"):
            sp = {k: v for k, v in island["stockpile"].items() if v > 0}
            if sp:
                print(f"  {iname}: holder={island['holder']} stockpile={sp}")

    # PHASE 7: SCORING
    print("\n[Phase 7: Scoring]")
    score_phase(state)
    for fname in faction_order:
        s = state["factions"][fname]["score"]
        print(f"  {fname:8s}: total={s['total']:4d}  T={s['territory']} Q={s['quest']} R={s['resource']} A={s['alliance']}")

    # PHASE 8: RANKS
    rank_update(state)

    # PHASE 9: TURN SUMMARY
    summary = build_summary(state, results, new_events)
    state["turn_history"].append(summary)
    if len(state["turn_history"]) > 20:
        state["turn_history"] = state["turn_history"][-20:]

    # Advance turn counter
    state["clock"]["turn"] = turn + 1

    # PHASE 10: PERSIST
    print("\n[Phase 10: Persist]")
    persist(state, summary)
    counters = load_counters()
    counters = update_counters(counters, results, new_events)
    save_counters(counters)
    print(f"  ✓ temple_world_state.json  turn {turn} → {turn+1}")
    print(f"  ✓ session_log.ndjson       appended")
    print(f"  ✓ counters.json            updated")

    # Final receipt
    print(f"\n{'='*60}")
    print(f"TURN {turn} COMPLETE")
    print(f"  WULmoji : {summary['wulmoji']}")
    print(f"  Scores  : {summary['scores']}")
    print(f"  Holders : {summary['ownership']}")
    print(f"  Events  : {summary['events_triggered']}")
    print(f"  AUTHORITY=false  SOVEREIGN=false  CANON=false  LEDGER=SLEEPING")
    print(f"{'='*60}")
    sys.exit(0)


if __name__ == "__main__":
    main()
