#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Foundry Town MVP Runner — v0.1
NON_SOVEREIGN · authority=false · no ledger writes · no kernel writes
Deterministic multi-castle simulation with append-only WULmoji ledger output.

Ledger line format (7 tokens with index):
  (Index) State Faction Pair Act Proof Ribbon

Hard constraints:
- Determinism: same args => identical ledger.txt
- State in {🔵,🟢,🟣,⚫,🔴}
- Faction in {⟂◯⟂,🌹,🌀,✝️}
- Pair = exactly 2 glyphs
- Act in {📜,🛡️,🔒📜,⚠️📜}
- Proof = 🔗#HEX4 (strict 4 uppercase hex chars)
- Replay = verifying ledger_sha256

Usage:
  python3 foundry_town_mvp.py --seed 1337 --ticks 12 --n 9 --pressure 5 --out out
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Deterministic hash utilities
# ---------------------------------------------------------------------------

def _hbytes(*parts: str) -> bytes:
    m = hashlib.sha256()
    for p in parts:
        m.update(p.encode("utf-8"))
        m.update(b"|")
    return m.digest()


def hex4(*parts: str) -> str:
    """Deterministic HEX4 token — 4 uppercase hex chars."""
    return _hbytes(*parts)[:2].hex().upper()


def u01(*parts: str) -> float:
    """Deterministic uniform in [0, 1)."""
    b = _hbytes(*parts)
    x = int.from_bytes(b[:8], "big")
    return (x % (10 ** 12)) / (10 ** 12)


# ---------------------------------------------------------------------------
# Model / State
# ---------------------------------------------------------------------------

Status = str  # "NORMAL" | "SIEGE" | "DORMANT"


@dataclass(frozen=True)
class Rules:
    pressure: float = 5.0
    fortress_default: int = 2

    hunger_drift: float = 1.0
    hunger_morale_threshold: float = 7.0
    morale_penalty_hunger: float = 1.0

    siege_penalty_morale: float = 0.5

    stability_penalty_morale_lt3: float = 1.0
    stability_penalty_morale_lt4: float = 0.5
    enable_morale_lt4_penalty: bool = False

    dormancy_stability_threshold: float = 3.0
    dormancy_morale_floor: float = 0.0
    dormancy_protects: bool = True

    clamp_min: float = 0.0
    clamp_max: float = 10.0


@dataclass
class CastleState:
    castle_id: str
    hunger: float
    morale: float
    stability: float
    fortress: int
    status: Status
    scrutiny_level: int = 1


@dataclass
class WorldState:
    t: int
    seed: int
    rules: Rules
    castles: Dict[str, CastleState]
    ledger: List[str]


# ---------------------------------------------------------------------------
# Ledger encoding — WULmoji v0.2 strict HEX4
# ---------------------------------------------------------------------------

PAIR_TICK     = "🜃🜄"   # substrate -> flow (generic progression)
PAIR_SIEGE    = "🜁🜂"   # abstraction -> fire (conflict)
PAIR_DORMANCY = "🜂🜍"   # fire -> motor/seal (irreversible)

RIBBON_TICK   = "🏰📜"
RIBBON_SIEGE  = "🌀🗝"
RIBBON_DORM   = "🔒⚰️"

STATE_BLUE  = "🔵"
STATE_GREEN = "🟢"
STATE_PURP  = "🟣"
STATE_BLACK = "⚫"
STATE_RED   = "🔴"

FACTION_MASON  = "⟂◯⟂"
FACTION_ROSE   = "🌹"
FACTION_SPIRAL = "🌀"
FACTION_CROSS  = "✝️"

ACT_LOG   = "📜"
ACT_HARD  = "🛡️"
ACT_SEAL  = "🔒📜"
ACT_ALERT = "⚠️📜"


def ledger_line(
    index: int,
    state: str,
    faction: str,
    pair: str,
    act: str,
    proof_hex4: str,
    ribbon: str,
) -> str:
    proof = f"🔗#{proof_hex4}"
    return f"({index}) {state} {faction} {pair} {act} {proof} {ribbon}"


def emit(
    world: WorldState,
    state: str,
    faction: str,
    pair: str,
    act: str,
    proof_ctx: str,
    ribbon: str,
) -> None:
    idx = len(world.ledger)
    pid = hex4(str(world.seed), str(world.t), proof_ctx, str(idx))
    world.ledger.append(ledger_line(idx, state, faction, pair, act, pid, ribbon))


# ---------------------------------------------------------------------------
# Simulation step — deterministic
# ---------------------------------------------------------------------------

def siege_probability(rules: Rules, castle: CastleState) -> float:
    x = max(0.0, rules.pressure - float(castle.fortress))
    return min(1.0, max(0.0, 0.03 * x))


def clamp(rules: Rules, x: float) -> float:
    return max(rules.clamp_min, min(rules.clamp_max, x))


def step_castle(
    world: WorldState, castle: CastleState
) -> Tuple[CastleState, List[Tuple[str, str]]]:
    r = world.rules
    events: List[Tuple[str, str]] = []

    hunger_new    = castle.hunger + r.hunger_drift
    morale_new    = castle.morale
    stability_new = castle.stability
    status_new    = castle.status
    scrutiny_new  = castle.scrutiny_level

    if hunger_new >= r.hunger_morale_threshold and status_new != "DORMANT":
        morale_new -= r.morale_penalty_hunger
        events.append(("HUNGER_PENALTY", "hunger>=threshold"))

    if r.enable_morale_lt4_penalty and morale_new < 4.0 and status_new != "DORMANT":
        stability_new -= r.stability_penalty_morale_lt4
        events.append(("MORALE_LT4_STAB", "morale<4"))

    p_siege = siege_probability(r, castle)
    if status_new == "DORMANT" and r.dormancy_protects:
        pass  # dormant shell: no siege escalation
    else:
        u = u01(str(world.seed), str(world.t), "SIEGE", castle.castle_id)
        hit = u < p_siege
        if status_new == "NORMAL" and hit:
            status_new = "SIEGE"
            events.append(("SIEGE_START", "siege_start"))
        elif status_new == "SIEGE":
            events.append(("SIEGE_HIT" if hit else "SIEGE_MISS",
                           "siege_hit" if hit else "siege_miss"))

        if status_new == "SIEGE" and any(
            e[0] in ("SIEGE_START", "SIEGE_HIT") for e in events
        ):
            morale_new -= r.siege_penalty_morale
            events.append(("SIEGE_MORALE", "siege_morale"))

    if morale_new < 3.0 and status_new != "DORMANT":
        stability_new -= r.stability_penalty_morale_lt3
        events.append(("MORALE_LT3_STAB", "morale<3"))

    hunger_new    = clamp(r, hunger_new)
    morale_new    = clamp(r, morale_new)
    stability_new = clamp(r, stability_new)

    if status_new != "DORMANT" and stability_new < r.dormancy_stability_threshold:
        status_new = "DORMANT"
        morale_new = max(r.dormancy_morale_floor, morale_new)
        events.append(("DORMANCY_ENTER", "stability<threshold"))

    if (castle.morale - morale_new) >= 1.5 or any(
        e[0] == "DORMANCY_ENTER" for e in events
    ):
        scrutiny_new = min(5, scrutiny_new + 1)
        events.append(("SCRUTINY_UP", "scrutiny++"))

    new_castle = CastleState(
        castle_id=castle.castle_id,
        hunger=hunger_new,
        morale=morale_new,
        stability=stability_new,
        fortress=castle.fortress,
        status=status_new,
        scrutiny_level=scrutiny_new,
    )
    return new_castle, events


def step_world(world: WorldState) -> None:
    ids = sorted(world.castles.keys())
    new_castles: Dict[str, CastleState] = {}

    for cid in ids:
        old = world.castles[cid]
        new, events = step_castle(world, old)
        new_castles[cid] = new

        if any(e[0] == "DORMANCY_ENTER" for e in events):
            emit(world, STATE_BLACK, FACTION_CROSS, PAIR_DORMANCY,
                 ACT_SEAL, f"{cid}:DORMANCY", RIBBON_DORM)
        elif new.status == "SIEGE":
            if any(e[0] in ("SIEGE_START", "SIEGE_HIT") for e in events):
                emit(world, STATE_RED, FACTION_SPIRAL, PAIR_SIEGE,
                     ACT_ALERT, f"{cid}:SIEGE_HIT", RIBBON_SIEGE)
            else:
                emit(world, STATE_BLUE, FACTION_SPIRAL, PAIR_SIEGE,
                     ACT_LOG, f"{cid}:SIEGE_MISS", RIBBON_SIEGE)
        else:
            emit(world, STATE_BLUE, FACTION_MASON, PAIR_TICK,
                 ACT_LOG, f"{cid}:TICK", RIBBON_TICK)

    world.castles = new_castles
    world.t += 1


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_world(seed: int, n: int, rules: Rules) -> WorldState:
    castles: Dict[str, CastleState] = {}
    for i in range(n):
        cid = f"CASTLE_{i + 1:02d}"
        h0 = 4.0 + 2.0 * u01(str(seed), cid, "h0")
        m0 = 5.0 + 2.0 * u01(str(seed), cid, "m0")
        s0 = 5.0 + 2.0 * u01(str(seed), cid, "s0")
        castles[cid] = CastleState(
            castle_id=cid,
            hunger=float(h0),
            morale=float(m0),
            stability=float(s0),
            fortress=rules.fortress_default,
            status="NORMAL",
            scrutiny_level=1,
        )
    return WorldState(t=1, seed=seed, rules=rules, castles=castles, ledger=[])


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_outputs(world: WorldState, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)

    ledger_path = os.path.join(outdir, "ledger.txt")
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write("\n".join(world.ledger) + "\n")

    state_path = os.path.join(outdir, "state_final.json")
    with open(state_path, "w", encoding="utf-8") as f:
        data = {
            "t": world.t,
            "seed": world.seed,
            "rules": asdict(world.rules),
            "castles": {k: asdict(v) for k, v in world.castles.items()},
            "ledger_len": len(world.ledger),
            "ledger_sha256": hashlib.sha256(
                ("\n".join(world.ledger) + "\n").encode("utf-8")
            ).hexdigest(),
        }
        json.dump(data, f, indent=2, ensure_ascii=False)

    n = len(world.castles)
    total_days = (len(world.ledger) // n) if n > 0 else 0
    for day in range(1, total_days + 1):
        start = (day - 1) * n
        end = day * n
        lines = world.ledger[start:end]

        cap = 30
        shown = lines[:cap]
        extra = len(lines) - len(shown)
        summary = ""
        if extra > 0:
            summary = (
                f"\n——— ⛧ ———\n"
                f"📌 (truncated) showing {len(shown)}/{len(lines)} lines; "
                f"full ledger in {outdir}/ledger.txt\n"
            )

        path = os.path.join(outdir, f"bulletin_day_{day:02d}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"🕯️ 𝔅𝔲𝔩𝔩𝔢𝔱𝔦𝔫 — Day {day:02d} 🕯️\n")
            f.write("🌈 Wrapper is decorative. Ledger below is canonical. 🌈\n")
            f.write("——— ⛧ ———\n")
            f.write("\n".join(shown) + "\n")
            f.write(summary)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Foundry Town MVP Runner v0.1 (NON_SOVEREIGN)")
    ap.add_argument("--seed",     type=int,   default=1337)
    ap.add_argument("--ticks",    type=int,   default=12)
    ap.add_argument("--n",        type=int,   default=3,   help="number of castles")
    ap.add_argument("--pressure", type=float, default=5.0)
    ap.add_argument("--fortress", type=int,   default=2)
    ap.add_argument("--out",      type=str,   default="out")
    args = ap.parse_args()

    rules = Rules(pressure=args.pressure, fortress_default=args.fortress)
    world = init_world(args.seed, args.n, rules)

    for _ in range(args.ticks):
        step_world(world)

    write_outputs(world, args.out)

    ledger_hash = hashlib.sha256(
        ("\n".join(world.ledger) + "\n").encode("utf-8")
    ).hexdigest()

    print(f"[OK] ticks={args.ticks} n={args.n} seed={args.seed}")
    print(f"[OK] ledger_len={len(world.ledger)} ledger_sha256={ledger_hash}")
    print(f"[OK] outputs written to: {args.out}/")


if __name__ == "__main__":
    main()
