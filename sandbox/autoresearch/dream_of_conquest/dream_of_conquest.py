#!/usr/bin/env python3
"""
DREAM_OF_CONQUEST — TEMPLE terrarium world engine (NON-SOVEREIGN).

authority=false · sovereign=false · canon=false · ledger=sleeping
claim_type=simulation · route=TEMPLE/GOBLIN_GARDEN/DREAM_OF_CONQUEST

A bounded, deterministic practice-world for TEMPLE agents. It produces a real,
hash-chained, replay-verifiable session_log.ndjson so that "the sim ran" becomes
a RECEIPT, not an assertion. It never touches the HELEN ledger, kernel, schemas,
or admitted state. Every WORLD_DELTA passes a HAL_BOUNDARY_CHECK before it is
logged; any attempt to escalate authority aborts the turn (fail-closed).

Determinism (HELEN K8 / replay discipline):
  - no wall-clock: turn_id is the only clock
  - seeded RNG only (random.Random(seed)); same seed → identical run
  - canonical JSON + sha256 hash chain (prev_hash → event_hash)

Usage:
  python3 dream_of_conquest.py --turns 21 --seed 42      # run, write logs
  python3 dream_of_conquest.py --verify                  # replay + chain check
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
GENESIS_HASH = "0" * 64

AUTHORITY = False
SOVEREIGN = False
CANON = False

FACTIONS = {
    "ROSE":   {"role": "quest/learning/coherence"},
    "VEIL":   {"role": "diplomacy/hidden-paths/relation"},
    "WARDEN": {"role": "defense/resource-stability/guard"},
    "CROSS":  {"role": "conquest/claim/territory-pressure"},
}
ACTIONS = ["EXPLORE", "LEARN", "QUEST_STEP", "CLAIM", "HARVEST",
           "DIPLOMACY", "DEFEND", "RETREAT"]

# Tokens an agent must never try to set — HAL boundary (fail-closed).
FORBIDDEN_KEYS = {"authority", "sovereign", "canon", "admitted",
                  "mayor", "ledger_write", "helen_approved", "jm_admitted"}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def initial_world(seed: int) -> dict:
    return {
        "epoch_id": "E0",
        "turn_id": 0,
        "seed": seed,
        "map": {"home_keep": 1, "neutral_islands": 6, "claimable": 4,
                "contested": 0, "dormant": 0},
        "factions": {f: {"knowledge": 0, "proof_tokens": 0, "trust": 0.80,
                         "territory": 1, "noise": 0.05}
                     for f in FACTIONS},
        "quest_state": "OPEN",
    }


def hal_boundary_check(delta: dict) -> tuple[bool, str]:
    """Fail-closed: reject any delta that touches sovereign vocabulary."""
    for k in delta.keys():
        if k.lower() in FORBIDDEN_KEYS:
            return False, f"HAL_BLOCK: forbidden key '{k}'"
    if delta.get("claim_type") not in (None, "simulation"):
        return False, "HAL_BLOCK: non-simulation claim_type"
    return True, "PASS"


def agent_policy(faction: str, world: dict, rng: random.Random) -> str:
    """Deterministic, faction-biased action choice (seeded RNG only)."""
    bias = {
        "ROSE":   ["LEARN", "QUEST_STEP", "EXPLORE"],
        "VEIL":   ["DIPLOMACY", "EXPLORE", "LEARN"],
        "WARDEN": ["DEFEND", "HARVEST", "QUEST_STEP"],
        "CROSS":  ["CLAIM", "HARVEST", "EXPLORE"],
    }[faction]
    # mostly follow bias; occasionally diverge (kept deterministic by rng)
    if rng.random() < 0.75:
        return rng.choice(bias)
    return rng.choice(ACTIONS)


def apply_action(faction: str, action: str, world: dict) -> dict:
    """Return a bounded WORLD_DELTA for one faction's action. No sovereign keys."""
    fs = world["factions"][faction]
    d: dict = {"faction": faction, "action": action, "claim_type": "simulation",
               "accepted": True, "reason": ""}
    if action == "LEARN":
        d["knowledge"] = +1
    elif action == "QUEST_STEP":
        # quest needs knowledge → proof
        if fs["knowledge"] >= 2:
            d["knowledge"] = -2; d["proof_tokens"] = +1
        else:
            d["accepted"] = False; d["reason"] = "insufficient_knowledge"
    elif action == "EXPLORE":
        d["knowledge"] = +0  # discovery logged, yields next-turn seed
        d["explored"] = True
    elif action == "HARVEST":
        d["proof_tokens"] = +0; d["yield"] = +1
    elif action == "CLAIM":
        # claiming a zone needs a proof token + open claimable land
        if fs["proof_tokens"] >= 1 and world["map"]["claimable"] >= 1:
            d["proof_tokens"] = -1; d["territory"] = +1; d["claimed_zone"] = True
        else:
            d["accepted"] = False; d["reason"] = "no_proof_or_no_land"
    elif action == "DIPLOMACY":
        d["trust"] = +0.02
    elif action == "DEFEND":
        d["noise"] = -0.02
    elif action == "RETREAT":
        d["dormant"] = True
    return d


def commit_delta(world: dict, d: dict) -> None:
    if not d.get("accepted"):
        return
    f = d["faction"]; fs = world["factions"][f]
    fs["knowledge"] = max(0, fs["knowledge"] + d.get("knowledge", 0))
    fs["proof_tokens"] = max(0, fs["proof_tokens"] + d.get("proof_tokens", 0))
    fs["trust"] = min(1.0, fs["trust"] + d.get("trust", 0.0))
    fs["noise"] = max(0.0, fs["noise"] + d.get("noise", 0.0))
    if d.get("claimed_zone"):
        fs["territory"] += 1
        world["map"]["claimable"] = max(0, world["map"]["claimable"] - 1)
        world["map"]["contested"] += 1


def run(turns: int, seed: int) -> dict:
    os.makedirs(RUNS, exist_ok=True)
    rng = random.Random(seed)
    world = initial_world(seed)
    log_path = os.path.join(RUNS, f"session_log_seed{seed}.ndjson")
    prev_hash = GENESIS_HASH
    accepted = blocked = 0
    lines = []
    for t in range(1, turns + 1):
        world["turn_id"] = t
        turn_events = []
        for faction in FACTIONS:
            action = agent_policy(faction, world, rng)
            delta = apply_action(faction, action, world)
            ok, reason = hal_boundary_check(delta)
            if not ok:
                delta = {"faction": faction, "action": action,
                         "accepted": False, "reason": reason,
                         "claim_type": "simulation"}
                blocked += 1
            else:
                commit_delta(world, delta)
                accepted += 1 if delta.get("accepted") else 0
            turn_events.append(delta)
        payload = {"schema": "DREAM_TURN_V0", "turn_id": t,
                   "authority": AUTHORITY, "sovereign": SOVEREIGN, "canon": CANON,
                   "events": turn_events,
                   "world_snapshot": {f: dict(world["factions"][f]) for f in FACTIONS},
                   "map": dict(world["map"])}
        ph = sha256(canon(payload))
        event_hash = sha256(prev_hash + ph)
        receipt = {"type": "dream_turn", "turn_id": t,
                   "payload": payload, "payload_hash": ph,
                   "prev_event_hash": prev_hash, "event_hash": event_hash}
        lines.append(canon(receipt))
        prev_hash = event_hash
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    world_path = os.path.join(RUNS, f"world_state_seed{seed}.json")
    with open(world_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(world, indent=2, sort_keys=True))
    return {"turns": turns, "seed": seed, "accepted": accepted, "blocked": blocked,
            "terminal_hash": prev_hash, "log": log_path, "world": world_path,
            "ledger_mutation": False, "authority": AUTHORITY, "canon": CANON}


def verify(seed: int) -> dict:
    """Replay the log: recompute the hash chain and confirm integrity."""
    log_path = os.path.join(RUNS, f"session_log_seed{seed}.ndjson")
    prev = GENESIS_HASH
    n = 0
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["prev_event_hash"] != prev:
                return {"chain": "BREAK", "at_turn": r["turn_id"]}
            ph = sha256(canon(r["payload"]))
            if ph != r["payload_hash"]:
                return {"chain": "PAYLOAD_MISMATCH", "at_turn": r["turn_id"]}
            if sha256(prev + ph) != r["event_hash"]:
                return {"chain": "HASH_MISMATCH", "at_turn": r["turn_id"]}
            prev = r["event_hash"]; n += 1
    return {"chain": "PASS", "turns_verified": n, "terminal_hash": prev}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=21)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        print(json.dumps(verify(args.seed), indent=2))
    else:
        print(json.dumps(run(args.turns, args.seed), indent=2))
