"""WUL-Core semantic codec — projection-only transport.

NON_SOVEREIGN · authority=false · ledger_effect=none.

Frame note (2026-08-10): this is the FIRST witnessed implementation of the
WUL-Core contract on the SOT. An earlier 23/23 suite reported in another
frame was never pushed; per frame-indexed truth it is not imported as
canon. This file implements the corrected contract directly:

    X = (tau, phi, w, a, p)                 machine state
    pi_visual(X) = (tau, phi, w)            the ONLY thing that renders
    P(E(X)) = pi_visual(X)                  parse recovers the projection
    Authority not in Codomain(parse_wul)    a does not travel
    Provenance does not travel              p does not travel

Invariant: WUL-Core may render governed state, but it cannot transport
governed authority. Transport is delimiter-based ("|"), never positional
codepoint indexing — emoji with variation selectors (e.g. shield U+1F6E1
U+FE0F) make rendered[0..2] slicing structurally unsafe.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GlyphType(Enum):
    """tau — the creature. Glyphs name identity, never state."""
    SEED = "🌰"
    GOBLIN = "🧌"
    CANDIDATE = "△"
    CONTROL = "🛡️"
    MEMBRANE = "⚖️"
    CAP = "🔑"
    EFFECT = "⚙️"
    RECEIPT = "🧾"
    LEDGER = "📜"


class PhaseColor(Enum):
    """phi — the weather. Color is state, not ontology."""
    OBSERVED = "🔵"
    EXECUTED = "🟢"
    HELD = "🟡"
    FAILED = "🔴"
    HYPOTHESIS = "🟣"
    COMPOST = "🟤"
    GERMINAL = "⚪"


class WorldFrame(Enum):
    """w — the surface the state inhabits."""
    GARDEN = "🌿"
    SOVEREIGN = "⬡"
    COMMONS = "〰"


class AuthorityGrade(Enum):
    """a — machine-only. Never rendered, never parsed back."""
    NONE = 0
    GOVERNED = 1


# Deliberately minimal: SovereignRisk(x) != Authority(x). RECEIPT and
# LEDGER are governed *records*, not executable authority objects; they
# join this set only when a concrete machine capability requires it.
AUTHORITY_BEARING_TYPES = frozenset({GlyphType.CAP, GlyphType.EFFECT})

# Garden creatures live at A=0 and never occupy the sovereign surface.
GARDEN_CREATURES = frozenset({GlyphType.SEED, GlyphType.GOBLIN, GlyphType.CANDIDATE})

# Judgment surfaces do not germinate or compost — metabolic phases belong
# to garden creatures.
JUDGMENT_GLYPHS = frozenset({GlyphType.CONTROL, GlyphType.MEMBRANE})
METABOLIC_PHASES = frozenset({PhaseColor.COMPOST, PhaseColor.GERMINAL})

WUL_DELIM = "|"


@dataclass(frozen=True)
class WULState:
    """Full machine record. Only trusted machine channels may construct it."""
    glyph: GlyphType
    phase: PhaseColor
    frame: WorldFrame
    authority: AuthorityGrade = AuthorityGrade.NONE
    provenance: tuple = field(default_factory=tuple)

    def validate(self) -> None:
        if self.authority is AuthorityGrade.GOVERNED:
            if self.glyph not in AUTHORITY_BEARING_TYPES:
                raise ValueError("E_AUTHORITY_COLLISION")
            if self.frame is WorldFrame.GARDEN:
                raise ValueError("E_GARDEN_AUTHORITY")
            if not self.provenance:
                raise ValueError("E_CAP_WITHOUT_RECEIPT")
        if self.glyph in GARDEN_CREATURES and self.frame is WorldFrame.SOVEREIGN:
            raise ValueError("E_SOVEREIGN_SURFACE")
        if self.glyph in JUDGMENT_GLYPHS and self.phase in METABOLIC_PHASES:
            raise ValueError("E_PHASE_MISMATCH")
        # HAL Witness Law: an unwitnessed green judgment is uninhabitable.
        if (self.glyph in JUDGMENT_GLYPHS
                and self.phase is PhaseColor.EXECUTED
                and not self.provenance):
            raise ValueError("E_UNWITNESSED_GREEN")


@dataclass(frozen=True)
class WULProjection:
    """What the visual channel can carry. Note what is absent."""
    glyph: GlyphType
    phase: PhaseColor
    frame: WorldFrame


def encode_wul(state: WULState) -> str:
    state.validate()
    return WUL_DELIM.join((state.phase.value, state.glyph.value, state.frame.value))


def parse_wul(rendered: str) -> WULProjection:
    parts = rendered.split(WUL_DELIM)
    if len(parts) != 3:
        raise ValueError("E_PARSE_ARITY")
    phase_raw, glyph_raw, frame_raw = parts
    return WULProjection(
        phase=PhaseColor(phase_raw),
        glyph=GlyphType(glyph_raw),
        frame=WorldFrame(frame_raw),
    )
