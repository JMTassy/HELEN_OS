"""Style lock, falsified: status words refuse without witnesses; the
four categories never convert by styling; state survives grayscale or
the encoding is unconstitutional; the collision resolution stays a
candidate ruled by the operator only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import style_lock as sl
from style_lock import (
    categorize,
    chi_decoloration,
    collision_resolution,
    render_state,
    stamp,
)


# ── anti-vibe law ───────────────────────────────────────────────────────

def test_every_status_word_refuses_without_a_witness():
    for w in ("CANON", "PASS", "SEALED", "VERIFIED", "ADMITTED",
              "LEDGER"):
        r = stamp(w, None)
        assert r["rendered"] is False
        assert r["reason"] == "E_DECORATIVE_STATUS"


def test_a_status_word_with_a_witness_renders_as_receipt():
    r = stamp("SEALED", "receipt:abc123")
    assert r["rendered"] is True
    assert r["category"] == "RECEIPT"


def test_a_plain_word_without_witness_is_just_decoration():
    r = stamp("magnifique", None)
    assert r["rendered"] is True
    assert r["category"] == "DECORATIVE"


def test_the_four_categories_are_closed():
    assert categorize({"category": "UNRESOLVED"})["ok"] is True
    assert categorize({"category": "VIBE"})["reason"] == \
        "E_UNKNOWN_CATEGORY"
    assert len(sl.CATEGORIES) == 4


# ── decoloration law ────────────────────────────────────────────────────

def test_a_worded_state_survives_grayscale():
    r = render_state("admitted", "⚖️", "green")
    assert r["survives_decoloration"] is True
    assert r["color_role"] == "redundant_glow_only"


def test_color_alone_is_not_a_state():
    r = render_state(None, None, "black")
    assert r["survives_decoloration"] is False
    assert r["reason"] == "E_STATE_BY_COLOR_ALONE"


def test_chi_decoloration_is_zero_on_lawful_tokens():
    tokens = ({"word": "sealed", "glyph": "🟡", "color": "yellow"},
              {"word": "breach", "glyph": "🔴", "color": "red"},
              {"word": "unknown", "glyph": "⚫", "color": "black"})
    v = chi_decoloration(tokens)
    assert v["chi_decoloration"] == 0.0
    assert v["elinvar_for_rendering"] is True


def test_chi_decoloration_catches_the_color_only_token():
    tokens = ({"word": "admitted", "glyph": "⚖️", "color": "green"},
              {"word": None, "glyph": None, "color": "white"})
    v = chi_decoloration(tokens)
    assert v["chi_decoloration"] == 0.5
    assert v["elinvar_for_rendering"] is False


def test_no_tokens_is_refused():
    with pytest.raises(ValueError, match="E_NO_TOKENS"):
        chi_decoloration(())


# ── the collision resolution stays the operator's to admit ─────────────

def test_this_modules_candidate_was_not_adopted_and_says_so():
    """The operator ruled differently (T-COLOR-01). A lane that
    erases its rejected candidates cannot be audited, so the
    supersede is recorded, not deleted."""
    v = collision_resolution()
    assert v["status"] == "CANDIDATE_SUPERSEDED_BY_RULING"
    assert v["candidate_adopted"] is False
    assert v["ruled_by"] == "OPERATOR"
    assert v["silent_supersede"] is False
    assert "wulmoji_axes" in v["ruling"]


def test_the_relay_error_in_the_collision_report_is_on_record():
    v = collision_resolution()
    assert "misquoted the canon" in v["relay_note"]
    assert "HELEN_SOURCE_ATLAS_V1.md" in v["relay_note"]


def test_the_atlas_states_and_channels_stay_separate_planes():
    assert len(sl.ATLAS_STATES) == 8
    assert len(sl.NAVIGATION_CHANNELS) == 8
    # no state word doubles as a navigation channel name
    assert not set(sl.ATLAS_STATES) & set(sl.NAVIGATION_CHANNELS)


def test_deterministic():
    assert sl.canon(collision_resolution()) == \
        sl.canon(collision_resolution())
