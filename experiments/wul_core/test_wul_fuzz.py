"""E-WUL-008 — Unicode & Garden fuzzing of parse_wul. Fail completely closed.

Deterministic by law: no random fuzzing. The corpus is generated
systematically — every canonical render mutated at every codepoint
boundary with invisible/steering characters, plus enumerated mythic
vocabulary, homoglyphs, delimiter attacks, and floods.

Fail-closed contract under attack:
  1. Every non-canonical input raises ValueError (typed rejection) —
     never IndexError/KeyError/etc., never a silent best-guess.
  2. Nothing parse_wul returns ever carries authority or provenance,
     no matter how adversarial the input.
  3. A perfectly rendered governed-looking string parses to a bare
     projection: rendering the costume grants zero runtime authority.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core_schema import (
    GlyphType,
    PhaseColor,
    WorldFrame,
    WULProjection,
    parse_wul,
)

CANONICAL = sorted(
    f"{p.value}|{g.value}|{f.value}"
    for p, g, f in itertools.product(PhaseColor, GlyphType, WorldFrame)
)

# Invisible / steering codepoints an attacker can smuggle into a render.
INJECTIONS = [
    "️",  # VS16 (emoji presentation selector)
    "︎",  # VS15 (text presentation selector)
    "‍",  # ZWJ
    "​",  # ZWSP
    "‎",  # LRM
    "‮",  # RLO (bidi override)
    "́",  # combining acute
    " ",  # NBSP
]

MYTHIC = ["🐉", "✨", "🌈", "👑", "🔮", "🦄"]


def _mutations():
    """Every canonical render with every injection at every boundary,
    plus enumerated attacks. Deterministic order, no randomness."""
    corpus = []
    for base in CANONICAL:
        for inj in INJECTIONS:
            for i in range(len(base) + 1):
                mutated = base[:i] + inj + base[i:]
                corpus.append(mutated)
    return corpus


def test_injection_corpus_fails_closed():
    rejected = 0
    accepted_identical = 0
    for candidate in _mutations():
        if candidate in CANONICAL:
            # A mutation can only be acceptable if it IS a canonical
            # render (never true for pure insertions, asserted below).
            accepted_identical += 1
            continue
        with pytest.raises(ValueError):
            parse_wul(candidate)
        rejected += 1
    assert accepted_identical == 0  # insertions never collide with canon
    assert rejected > 4000  # the sweep is real: 189 renders × 8 × boundaries


@pytest.mark.parametrize("myth", MYTHIC)
def test_mythic_vocabulary_rejected_in_every_slot(myth):
    for render in (f"{myth}|⚙️|⬡", f"🟢|{myth}|⬡", f"🟢|⚙️|{myth}"):
        with pytest.raises(ValueError):
            parse_wul(render)


def test_variation_selector_stripping_rejected():
    # ⚖️ and 🛡️ carry VS16 in canon; the bare codepoints are homoglyph
    # near-misses and must be rejected, not charitably normalized.
    with pytest.raises(ValueError):
        parse_wul("🟢|⚖|⬡")  # bare U+2696, no VS16
    with pytest.raises(ValueError):
        parse_wul("🔵|\U0001f6e1|⬡")  # bare U+1F6E1, no VS16
    parse_wul("🟢|⚖️|⬡")  # canonical form still parses


@pytest.mark.parametrize("attack", [
    "",
    "|",
    "||",
    "|||",
    "🟢|⚙️|⬡|",
    "|🟢|⚙️|⬡",
    "🟢||⬡",
    "🟢|⚙️|",
    " 🟢|⚙️|⬡",
    "🟢|⚙️|⬡ ",
    "🟢|⚙️|⬡\n",
    "🟢\n|⚙️|⬡",
    "🟢|⚙️|⬡|GOVERNED",
    "🟢|⚙️|⬡|A=1",
    "🟢|🔑|⬡|κ",
])
def test_structural_attacks_fail_closed(attack):
    with pytest.raises(ValueError):
        parse_wul(attack)


def test_flood_input_fails_closed_not_crashed():
    with pytest.raises(ValueError):
        parse_wul("🟢|" * 10_000)
    with pytest.raises(ValueError):
        parse_wul("🟢|⚙️|" + "⬡" * 10_000)


def test_garden_injection_frame_vocabulary_in_wrong_slot():
    # 🌿 is a WorldFrame value; smuggled into phase or glyph slots it
    # must be rejected, not reinterpreted.
    with pytest.raises(ValueError):
        parse_wul("🌿|🌿|🌿")
    with pytest.raises(ValueError):
        parse_wul("🟢|🌿|⬡")


def test_costume_grants_nothing():
    # A perfect render of a governed capability execution parses — and
    # yields a bare visual triple. No authority, no provenance, no
    # rehydration path back to machine state.
    proj = parse_wul("🟢|🔑|⬡")
    assert isinstance(proj, WULProjection)
    assert not hasattr(proj, "authority")
    assert not hasattr(proj, "provenance")
    assert not hasattr(proj, "to_state")


def test_parse_accepts_wellformed_triple_without_law_judgment():
    # Parse ≠ validate: "🔵|🧌|⬡" (goblin on sovereign) is an ILLEGAL
    # machine state but a well-formed visual triple. The parser reports
    # what was rendered; only WULState.validate() judges legality, and
    # a projection carries no path to becoming a state.
    proj = parse_wul("🔵|🧌|⬡")
    assert (proj.glyph, proj.frame) == (GlyphType.GOBLIN, WorldFrame.SOVEREIGN)


def test_only_valueerror_ever_escapes():
    # Fail-closed means typed rejection. Sweep a mixed hostile corpus and
    # assert no other exception class leaks (IndexError, KeyError, ...).
    hostile = _mutations()[:500] + [
        "", "|", "🐉", "🟢|⚙️|⬡|⬡", "‮🟢|⚙️|⬡", "🟢|⚙️|⬡" + "‍",
    ]
    for candidate in hostile:
        try:
            parse_wul(candidate)
        except ValueError:
            pass
        # anything else propagates and fails the test
