"""CONQUEST MAGICK — deterministic tick engine.

One function: tick(state, line) -> (new_state, chronicle_line).

Pure. No randomness, no network, no I/O outside stdout when run as main.
Same (state, line) always produces the same (new_state, chronicle_line).

Enforces:
    - KERNEL_SPEC delta semantics (RESULT base deltas)
    - OUTIL modifiers (sword amplifies negative, shield dampens, scroll halves+tax)
    - SEAL (cercueil) modifiers (doubles worst axis or adds +1 bonus with tension tax)
    - MANDAT modifiers (spiral +TENSION, rose +1 SEC if result is heart)
    - TERRENOIR interaction (earth nullifies spiral TENSION +1)
    - Spiral cap (TENSION >= 8 nullifies spiral acte)
    - Axis clamping [0, 10]

Run as module for the deterministic 12-move demo:
    python3 -m oracle_town.skills.conquest.magick_kernel_v1.tick
"""
from __future__ import annotations

import json
from typing import Any

try:
    from .parser import parse
    from .moves import CANONICAL_MOVES
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from parser import parse
    from moves import CANONICAL_MOVES


CANONICAL_START = {"COH": 5, "KNOW": 5, "SEC": 5, "TENSION": 1}


def _clamp(v: int) -> int:
    return max(0, min(10, v))


def _apply_deltas(state: dict, deltas: dict) -> dict:
    out = dict(state)
    for k, v in deltas.items():
        out[k] = _clamp(out.get(k, 0) + v)
    return out


def compute_deltas(parsed: dict) -> dict:
    """Compute raw deltas from a parsed acte. Pure function."""
    result = parsed["result"]
    outil = parsed["outil"]
    seal = parsed["seal"]
    mandat = parsed["mandat"]
    opus = parsed["opus"]

    deltas: dict[str, int] = {}

    base = {
        "FORT":   {"COH": 2},
        "MUR":    {"COH": 1},
        "OMBRE":  {"COH": -2, "TENSION": 1},
        "ESPRIT": {"KNOW": 2},
        "COEUR":  {"SEC": 2},
    }[result]
    for k, v in base.items():
        deltas[k] = deltas.get(k, 0) + v

    if outil == "EPEE" and result == "OMBRE":
        deltas["COH"] = deltas.get("COH", 0) + (-1)
    if outil == "BOUCLIER" and result == "OMBRE":
        deltas["COH"] = deltas.get("COH", 0) + 1

    if outil == "PARCHEMIN":
        for k in list(deltas.keys()):
            if deltas[k] > 0:
                deltas[k] = max(1, deltas[k] // 2)
        deltas["KNOW"] = deltas.get("KNOW", 0) + 1

    if seal == "CERCUEIL":
        if result == "OMBRE":
            deltas["COH"] = deltas.get("COH", 0) + (-2)
        elif result == "ESPRIT":
            deltas["KNOW"] = deltas.get("KNOW", 0) + 1
            deltas["TENSION"] = deltas.get("TENSION", 0) + 1
        elif result == "COEUR":
            deltas["SEC"] = deltas.get("SEC", 0) + 1
            deltas["TENSION"] = deltas.get("TENSION", 0) + 1

    if outil == "CROIX_SANG":
        deltas["TENSION"] = deltas.get("TENSION", 0) + 1

    if mandat == "ROSE" and result == "COEUR":
        deltas["SEC"] = deltas.get("SEC", 0) + 1

    if mandat == "SPIRALE":
        if "TERRE" not in opus:
            deltas["TENSION"] = deltas.get("TENSION", 0) + 1

    return deltas


def tick(state: dict, line: str, tick_n: int = 0) -> tuple[dict, str]:
    """Apply one acte to state. Return (new_state, chronicle_line)."""
    valid, parsed, reason = parse(line)

    if not valid:
        chronicle = (
            f"tick={tick_n} acte={line} valid=False "
            f"reason={reason} state={json.dumps(state, sort_keys=True)}"
        )
        return dict(state), chronicle

    if parsed["mandat"] == "SPIRALE" and state.get("TENSION", 0) >= 8:
        chronicle = (
            f"tick={tick_n} acte={line} valid=False "
            f"reason=spiral_cap state={json.dumps(state, sort_keys=True)}"
        )
        return dict(state), chronicle

    deltas = compute_deltas(parsed)
    new_state = _apply_deltas(state, deltas)
    chronicle = (
        f"tick={tick_n} acte={line} valid=True "
        f"deltas={json.dumps(deltas, sort_keys=True)} "
        f"state={json.dumps(new_state, sort_keys=True)}"
    )
    return new_state, chronicle


def run_demo() -> int:
    """Deterministic demo: apply all 12 canonical moves from CANONICAL_START."""
    state = dict(CANONICAL_START)
    print("CONQUEST MAGICK — deterministic tick demo")
    print(f"start  state={json.dumps(state, sort_keys=True)}")
    print()
    for i, (name, line) in enumerate(CANONICAL_MOVES, start=1):
        state, chronicle = tick(state, line, tick_n=i)
        print(f"move={name}")
        print(f"  {chronicle}")
        print()
    print(f"end    state={json.dumps(state, sort_keys=True)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_demo())
