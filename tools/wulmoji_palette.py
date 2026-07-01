"""wulmoji_palette.py — canonical machine-readable WULmoji glyph tables.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none

Single source of truth for glyph → role → meaning, so that the palette law
lives in code, not only in CLAUDE.md prose. Two namespaces exist ON PURPOSE
and must never be conflated:

  GOVERNANCE (Source Atlas doctrine, CLAUDE.md "HELEN OS Look & Feel"):
    status predicates render governance state; interaction verbs name acts.
    One glyph, one meaning, and the two role sets are disjoint.

  CONQUEST (bulletin grammar, tools/wulmoji_ledger_validator.py):
    a non-sovereign game layer that intentionally REUSES five governance
    status colors with game-local meanings. That reuse is registered
    explicitly below (CROSS_NAMESPACE_REUSE) — it is a documented seam,
    not silent drift.

Enforced by tests/test_wulmoji_palette_disjointness.py:
  - one glyph → one meaning within each namespace
  - STATUS_PREDICATES ∩ INTERACTION_VERBS = ∅
  - validator VALID_STATES == CONQUEST_BULLETIN_STATES glyphs
  - CONQUEST glyphs ⊆ GOVERNANCE_STATUS glyphs, exclusions documented
  - CLAUDE.md doctrine line and these tables agree
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# GOVERNANCE namespace — Source Atlas doctrine (CLAUDE.md)
# ---------------------------------------------------------------------------

# Palette (strict, one meaning per color)
GOVERNANCE_STATUS: dict[str, str] = {
    "⚫": "unknown",
    "🔵": "observed",
    "🟣": "claim",
    "🟠": "review",
    "🟢": "admitted",
    "🟡": "sealed",
    "⚪": "replayable",
    "🔴": "breach",
}

# Interaction vocabulary — verbs/acts, never status predicates
INTERACTION_VERBS: dict[str, str] = {
    "👁️": "OBSERVE",
    "📜": "CLAIM",
    "🧪": "REVIEW",
    "⚖️": "ADMIT",
    "🔒": "SEAL",
    "🔁": "REPLAY",
    "✂️": "CUT",
}

# ---------------------------------------------------------------------------
# CONQUEST namespace — bulletin grammar (tools/wulmoji_ledger_validator.py)
# ---------------------------------------------------------------------------

# Game-local state meanings (E031 STATE_GRAMMAR; see
# temple/gardens/.../batch_001/run_batch_001.py). Same glyphs as five of the
# governance status colors, DIFFERENT meanings — registered, not hidden.
CONQUEST_BULLETIN_STATES: dict[str, str] = {
    "🔵": "ACTIVE",        # established
    "🟢": "RESOLVED",      # quest complete
    "🟣": "PROPOSED",      # pending
    "⚫": "SEALED_LOCAL",  # local-only irreversible
    "🔴": "CONTESTED",     # unstable
}

# Governance statuses the bulletin grammar intentionally does NOT accept.
# The validator's test_invalid_state pins 🟡 as INVALID_STATE — expanding
# the grammar is a game-design decision, not a drift fix.
CONQUEST_EXCLUDED_GOVERNANCE_STATUS: frozenset[str] = frozenset({"🟠", "🟡", "⚪"})

# Explicit cross-namespace reuse register: glyph → (governance meaning,
# conquest meaning). Every glyph whose meaning diverges across namespaces
# MUST appear here; the test fails on any unregistered divergence.
CROSS_NAMESPACE_REUSE: dict[str, tuple[str, str]] = {
    "🔵": ("observed", "ACTIVE"),
    "🟢": ("admitted", "RESOLVED"),
    "🟣": ("claim", "PROPOSED"),
    "⚫": ("unknown", "SEALED_LOCAL"),
    "🔴": ("breach", "CONTESTED"),
}
