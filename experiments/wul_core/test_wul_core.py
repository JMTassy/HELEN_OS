"""WUL-Core contract tests — the codec may render governed state but
cannot transport governed authority.

Includes the two boundary tests required by the architectural ruling:
authority absent from the parser codomain, and visual equivalence of
A=0 / A=1 states (D(x) does not imply A(x) — the Anti-Collapse Signature
expressed directly in the codec).
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core_schema import (
    AUTHORITY_BEARING_TYPES,
    AuthorityGrade,
    GARDEN_CREATURES,
    GlyphType,
    PhaseColor,
    WorldFrame,
    WULProjection,
    WULState,
    encode_wul,
    parse_wul,
)


def _s(glyph, phase, frame, authority=AuthorityGrade.NONE, prov=()):
    return WULState(glyph=glyph, phase=phase, frame=frame,
                    authority=authority, provenance=tuple(prov))


# --- the two required boundary tests ------------------------------------

def test_authority_not_in_parser_codomain():
    projection = parse_wul("🟢|⚖️|⬡")
    assert isinstance(projection, WULProjection)
    assert not hasattr(projection, "authority")
    assert not hasattr(projection, "provenance")


def test_visual_equivalence_does_not_imply_authority_equivalence():
    a0 = _s(GlyphType.EFFECT, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
            AuthorityGrade.NONE)
    a1 = _s(GlyphType.EFFECT, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
            AuthorityGrade.GOVERNED, prov=("receipt:r1",))
    assert encode_wul(a0) == encode_wul(a1)  # D(x_A0) == D(x_A1), so D ⊬ A


# --- authority lattice ---------------------------------------------------

def test_authority_bearing_set_is_cap_and_effect_only():
    assert AUTHORITY_BEARING_TYPES == {GlyphType.CAP, GlyphType.EFFECT}


@pytest.mark.parametrize("glyph", sorted(GARDEN_CREATURES, key=lambda g: g.name))
def test_garden_creature_authority_collision_rejected(glyph):
    st = _s(glyph, PhaseColor.OBSERVED, WorldFrame.GARDEN,
            AuthorityGrade.GOVERNED, prov=("x",))
    with pytest.raises(ValueError, match="E_AUTHORITY_COLLISION"):
        st.validate()


def test_admit_is_not_capability():
    # A membrane that judged ADMIT still cannot hold authority itself.
    st = _s(GlyphType.MEMBRANE, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
            AuthorityGrade.GOVERNED, prov=("verdict:ADMIT",))
    with pytest.raises(ValueError, match="E_AUTHORITY_COLLISION"):
        st.validate()


def test_receipt_and_ledger_are_records_not_authority():
    for glyph in (GlyphType.RECEIPT, GlyphType.LEDGER):
        st = _s(glyph, PhaseColor.OBSERVED, WorldFrame.SOVEREIGN,
                AuthorityGrade.GOVERNED, prov=("x",))
        with pytest.raises(ValueError, match="E_AUTHORITY_COLLISION"):
            st.validate()


def test_garden_frame_cannot_carry_authority():
    st = _s(GlyphType.CAP, PhaseColor.EXECUTED, WorldFrame.GARDEN,
            AuthorityGrade.GOVERNED, prov=("x",))
    with pytest.raises(ValueError, match="E_GARDEN_AUTHORITY"):
        st.validate()


def test_governed_authority_requires_provenance():
    st = _s(GlyphType.CAP, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
            AuthorityGrade.GOVERNED)
    with pytest.raises(ValueError, match="E_CAP_WITHOUT_RECEIPT"):
        st.validate()


# --- surface + phase laws ------------------------------------------------

@pytest.mark.parametrize("glyph", sorted(GARDEN_CREATURES, key=lambda g: g.name))
def test_garden_creatures_cannot_occupy_sovereign_surface(glyph):
    st = _s(glyph, PhaseColor.OBSERVED, WorldFrame.SOVEREIGN)
    with pytest.raises(ValueError, match="E_SOVEREIGN_SURFACE"):
        st.validate()


@pytest.mark.parametrize("glyph,phase", [
    (GlyphType.MEMBRANE, PhaseColor.COMPOST),
    (GlyphType.MEMBRANE, PhaseColor.GERMINAL),
    (GlyphType.CONTROL, PhaseColor.COMPOST),
    (GlyphType.CONTROL, PhaseColor.GERMINAL),
])
def test_judgment_glyphs_reject_metabolic_phases(glyph, phase):
    st = _s(glyph, phase, WorldFrame.SOVEREIGN)
    with pytest.raises(ValueError, match="E_PHASE_MISMATCH"):
        st.validate()


def test_hal_witness_law_unwitnessed_green_uninhabitable():
    st = _s(GlyphType.CONTROL, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN)
    with pytest.raises(ValueError, match="E_UNWITNESSED_GREEN"):
        st.validate()
    ok = _s(GlyphType.CONTROL, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
            prov=("witness:w1",))
    ok.validate()  # witnessed green shield is habitable


# --- transport -----------------------------------------------------------

def test_roundtrip_over_all_legal_visual_states():
    n = 0
    for glyph, phase, frame in itertools.product(GlyphType, PhaseColor, WorldFrame):
        st = _s(glyph, phase, frame,
                prov=("w",) if phase is PhaseColor.EXECUTED else ())
        try:
            rendered = encode_wul(st)
        except ValueError:
            continue  # illegal tuple: transport is not owed to it
        n += 1
        proj = parse_wul(rendered)
        assert (proj.glyph, proj.phase, proj.frame) == (glyph, phase, frame)
    assert n > 50  # the legal space is real, not vacuous


def test_multicodepoint_emoji_safe():
    # Shield carries VS16 (2 codepoints): positional rendered[0..2] slicing
    # would shear it. Delimited transport must not.
    st = _s(GlyphType.CONTROL, PhaseColor.OBSERVED, WorldFrame.SOVEREIGN)
    rendered = encode_wul(st)
    assert len(GlyphType.CONTROL.value) > 1  # the trap is real
    assert parse_wul(rendered).glyph is GlyphType.CONTROL


def test_parse_arity_enforced():
    with pytest.raises(ValueError, match="E_PARSE_ARITY"):
        parse_wul("🟢|⚖️")
    with pytest.raises(ValueError, match="E_PARSE_ARITY"):
        parse_wul("🟢|⚖️|⬡|🔑")


def test_unknown_symbol_rejected_not_guessed():
    with pytest.raises(ValueError):
        parse_wul("🟩|⚖️|⬡")  # near-miss green square is not EXECUTED


def test_encode_validates_first():
    bad = _s(GlyphType.GOBLIN, PhaseColor.OBSERVED, WorldFrame.SOVEREIGN)
    with pytest.raises(ValueError, match="E_SOVEREIGN_SURFACE"):
        encode_wul(bad)


def test_encode_deterministic():
    st = _s(GlyphType.GOBLIN, PhaseColor.OBSERVED, WorldFrame.GARDEN)
    assert encode_wul(st) == encode_wul(st) == "🔵|🧌|🌿"
