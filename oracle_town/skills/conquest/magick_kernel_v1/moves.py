"""CONQUEST MAGICK — 12 canonical moves (v1 lock).

Each move is a canonical string in the kernel grammar. They cover the
expected coverage of MANDAT x OPUS x OUTIL x SEAL x RESULT combinations
for the v1 corpus. Promotion from DOCTRINE to INVARIANT requires a fresh
session replay to prove determinism across all 12.

Grammar constraints (enforced by parser.py):
    - exactly 1 MANDAT, 1-2 OPUS, 0-1 OUTIL, 0-1 SEAL, 1 RESULT
    - croix_sang (CROIX-SANG) OUTIL requires CERCUEIL SEAL

Referenced by tick.py for the deterministic demonstration tick.
"""
from __future__ import annotations

CANONICAL_MOVES: list[tuple[str, str]] = [
    ("01_earth_shield_seal_to_mur",       "\u271d\ufe0f \U0001f703 \U0001f6e1\ufe0f \u26b0 / \U0001f9f1"),
    ("02_water_scroll_seal_to_mind",      "\U0001f339 \U0001f704 \U0001f4dc \u26b0 / \U0001f9e0"),
    ("03_air_bloodoath_seal_to_fort",     "\U0001f339 \U0001f701 \u2e38 \u26b0 / \U0001f3f0"),
    ("04_fire_sword_to_fort",             "\u271d\ufe0f \U0001f702 \u2694\ufe0f / \U0001f3f0"),
    ("05_earth_fire_scroll_to_fort",      "\u271d\ufe0f \U0001f703 \U0001f702 \U0001f4dc / \U0001f3f0"),
    ("06_spiral_water_sword_to_shadow",   "\U0001f300 \U0001f704 \u2694\ufe0f / \U0001f311"),
    ("07_spiral_air_scroll_to_mind",      "\U0001f300 \U0001f701 \U0001f4dc / \U0001f9e0"),
    ("08_quint_bloodoath_seal_to_mur",    "\U0001f339 \u2697 \u2e38 \u26b0 / \U0001f9f1"),
    ("09_rose_earth_scroll_to_heart",     "\U0001f339 \U0001f703 \U0001f4dc / \u2764\ufe0f"),
    ("10_earth_water_shield_seal_to_fort","\u271d\ufe0f \U0001f703 \U0001f704 \U0001f6e1\ufe0f \u26b0 / \U0001f3f0"),
    ("11_spiral_fire_shield_to_mur",      "\U0001f300 \U0001f702 \U0001f6e1\ufe0f / \U0001f9f1"),
    ("12_rose_water_quint_to_mind",       "\U0001f339 \U0001f704 \u2697 / \U0001f9e0"),
]
