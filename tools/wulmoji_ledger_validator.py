#!/usr/bin/env python3
"""
wulmoji_ledger_validator.py — CONQUEST WhatsApp bulletin / WULmoji parser.

NON_SOVEREIGN. NOT the HELEN sovereign ledger.
authority=false. No ledger writes. No sovereign interactions.

Usage:
    python tools/wulmoji_ledger_validator.py bulletin.txt
    python tools/wulmoji_ledger_validator.py bulletin.txt --strict-proof
    python tools/wulmoji_ledger_validator.py bulletin.txt --alchemy-strict
    python tools/wulmoji_ledger_validator.py bulletin.txt --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Grapheme cluster splitter — stdlib only (regex library unavailable)
# ---------------------------------------------------------------------------
_VARIATION_SELECTORS = frozenset(range(0xFE00, 0xFE10))       # U+FE00–U+FE0F
_VARIATION_SELECTORS_SUP = frozenset(range(0xE0100, 0xE01F0)) # U+E0100–U+E01EF
_FITZPATRICK = frozenset(range(0x1F3FB, 0x1F400))              # U+1F3FB–U+1F3FF
_ZWJ = 0x200D
_REGIONAL_LOW = 0x1F1E0
_REGIONAL_HIGH = 0x1F1FF


def grapheme_clusters(s: str) -> list[str]:
    """Split s into Unicode grapheme clusters (simplified, no external libs)."""
    if not s:
        return []

    clusters: list[str] = []
    current = ""
    prev_was_zwj = False
    prev_was_regional = False

    for ch in s:
        cp = ord(ch)
        is_regional = _REGIONAL_LOW <= cp <= _REGIONAL_HIGH

        # Two consecutive regional indicators → one flag cluster
        if is_regional and prev_was_regional:
            current += ch
            clusters.append(current)
            current = ""
            prev_was_zwj = False
            prev_was_regional = False
            continue

        is_extending = (
            cp in _VARIATION_SELECTORS
            or cp in _VARIATION_SELECTORS_SUP
            or cp in _FITZPATRICK
            or cp == _ZWJ
            or unicodedata.category(ch) in ("Mn", "Mc", "Me")
            or prev_was_zwj  # char after ZWJ always extends previous cluster
        )

        if current and is_extending:
            current += ch
        else:
            if current:
                clusters.append(current)
            current = ch

        prev_was_zwj = cp == _ZWJ
        prev_was_regional = is_regional and not prev_was_regional

    if current:
        clusters.append(current)

    return clusters


# ---------------------------------------------------------------------------
# Grammar constants
# ---------------------------------------------------------------------------
# CONQUEST bulletin-grammar states — an intentional subset namespace of the
# governance palette with game-local meanings. Canonical table + the
# subset/disjointness law live in tools/wulmoji_palette.py; drift between
# this set and that table is caught by tests/test_wulmoji_palette_disjointness.py.
VALID_STATES = frozenset({"🔵", "🟢", "🟣", "⚫", "🔴"})

VALID_FACTIONS = frozenset({"⟂◯⟂", "🌹", "🌀", "✝️"})

VALID_ACTS = frozenset({"📜", "🛡️", "🔒📜", "⚠️📜"})

_WARNING_SIGN = "⚠"    # ⚠ base codepoint (U+26A0)
_LINK_EMOJI = "\U0001F517"  # 🔗 (U+1F517)
_LOCK_EMOJI = "\U0001F512"  # 🔒 (U+1F512) — common proof confusion

_PROOF_ID_RE = re.compile(r"^[A-Z0-9_\-]+$")
_PROOF_ID_STRICT_RE = re.compile(r"^[0-9A-F]{4}$")
_INDEX_RE = re.compile(r"^\(\d+\)$")

# Alchemy chain — forward-only transitions: Earth→Water→Air→Fire→Salt
_ALCHEMY_ORDER = ["🜃", "🜄", "🜁", "🜂", "🜍"]
_ALCHEMY_TRANSITIONS: frozenset[tuple[str, str]] = frozenset(
    (_ALCHEMY_ORDER[i], _ALCHEMY_ORDER[i + 1]) for i in range(len(_ALCHEMY_ORDER) - 1)
)
_ALCHEMY_GLYPHS = frozenset(_ALCHEMY_ORDER)

_WARNING_ACT = "⚠️📜"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------
@dataclass
class LineResult:
    line_num: int
    raw: str
    ok: bool
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core validator
# ---------------------------------------------------------------------------
def _has_warning(s: str) -> bool:
    return _WARNING_SIGN in s


def validate_line(
    raw: str,
    line_num: int,
    *,
    strict_proof: bool = False,
    alchemy_strict: bool = False,
) -> LineResult:
    result = LineResult(line_num=line_num, raw=raw, ok=True)
    errs = result.errors

    def fail(msg: str) -> None:
        result.ok = False
        errs.append(msg)

    tokens = raw.split(" ")
    n = len(tokens)

    if n == 7:
        idx_tok, state, faction, pair, act, proof, ribbon = tokens
        if not _INDEX_RE.match(idx_tok):
            fail(f"INVALID_INDEX: {idx_tok!r} must match (N)")
    elif n == 6:
        state, faction, pair, act, proof, ribbon = tokens
    else:
        fail(f"INVALID_ARITY: expected 6 or 7 tokens, got {n}")
        return result

    # State
    if state not in VALID_STATES:
        fail(f"INVALID_STATE: {state!r}")

    # Faction
    if faction not in VALID_FACTIONS:
        fail(f"INVALID_FACTION: {faction!r}")

    # Pair — exactly 2 grapheme clusters, ⚠️ forbidden
    if _has_warning(pair):
        fail("FORBIDDEN_WARNING_IN_PAIR: ⚠️ not allowed in Pair field")
    pair_clusters = grapheme_clusters(pair)
    if len(pair_clusters) != 2:
        fail(f"INVALID_PAIR_LENGTH: expected 2 grapheme clusters, got {len(pair_clusters)} in {pair!r}")

    # Act
    if act not in VALID_ACTS:
        fail(f"INVALID_ACT: {act!r}")

    # Proof — must start with 🔗#, ⚠️ forbidden in ID
    if not proof.startswith(_LINK_EMOJI + "#"):
        if proof.startswith(_LOCK_EMOJI + "#"):
            fail("PROOF_CONFUSION: proof starts with 🔒# but must start with 🔗#")
        else:
            fail(f"INVALID_PROOF_PREFIX: proof must start with 🔗#, got {proof!r}")
    else:
        # len('🔗') == 1, len('#') == 1 → ID starts at index 2
        proof_id = proof[2:]
        if _has_warning(proof_id):
            fail("FORBIDDEN_WARNING_IN_PROOF_ID: ⚠️ not allowed in ProofID")
        id_re = _PROOF_ID_STRICT_RE if strict_proof else _PROOF_ID_RE
        if not id_re.match(proof_id):
            mode = "STRICT" if strict_proof else "DEFAULT"
            fail(f"INVALID_PROOF_ID_{mode}: {proof_id!r}")

    # Ribbon — exactly 2 grapheme clusters, ⚠️ allowed only when act == ⚠️📜
    if _has_warning(ribbon) and act != _WARNING_ACT:
        fail("FORBIDDEN_WARNING_IN_RIBBON: ⚠️ in Ribbon only permitted when Act=⚠️📜")
    ribbon_clusters = grapheme_clusters(ribbon)
    if len(ribbon_clusters) != 2:
        fail(f"INVALID_RIBBON_LENGTH: expected 2 grapheme clusters, got {len(ribbon_clusters)} in {ribbon!r}")

    # AlchemyStrict: when both Pair clusters are alchemy glyphs, enforce forward chain
    if alchemy_strict and len(pair_clusters) == 2:
        a, b = pair_clusters
        if a in _ALCHEMY_GLYPHS and b in _ALCHEMY_GLYPHS:
            if (a, b) not in _ALCHEMY_TRANSITIONS:
                fail(f"INVALID_ALCHEMY_TRANSITION: {a}→{b} is not an allowed forward transition")

    return result


def validate_bulletin(
    text: str,
    *,
    strict_proof: bool = False,
    alchemy_strict: bool = False,
) -> list[LineResult]:
    results = []
    for i, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            continue
        results.append(
            validate_line(stripped, i, strict_proof=strict_proof, alchemy_strict=alchemy_strict)
        )
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a WULmoji bulletin file.")
    parser.add_argument("file", help="Path to bulletin text file")
    parser.add_argument("--strict-proof", action="store_true",
                        help="Require 4-hex-digit proof ID (e.g. A1B2)")
    parser.add_argument("--alchemy-strict", action="store_true",
                        help="Enforce alchemy forward-chain in Pair field")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output JSON instead of human-readable text")
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 1

    results = validate_bulletin(text, strict_proof=args.strict_proof,
                                alchemy_strict=args.alchemy_strict)
    all_ok = all(r.ok for r in results)

    if args.as_json:
        payload = {
            "ok": all_ok,
            "authority": False,
            "sovereign": False,
            "lines": [
                {"line": r.line_num, "ok": r.ok, "errors": r.errors, "raw": r.raw}
                for r in results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            mark = "✅" if r.ok else "❌"
            print(f"[{r.line_num}] {mark} {r.raw}")
            for e in r.errors:
                print(f"      ERROR: {e}")
        print()
        passed = sum(1 for r in results if r.ok)
        total = len(results)
        print(f"{'✅' if all_ok else '❌'} {passed}/{total} lines passed")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
