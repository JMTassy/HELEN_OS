"""The color ruling, falsified: the palette is frozen and refuses
redefinition; the two axes are disjoint so future collisions are
structurally impossible; the four reported clashes dissolve with zero
Atlas entries changed; axis confusion is caught in both directions.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wulmoji_axes as wa
from wulmoji_axes import (
    add_marker,
    axes_are_disjoint,
    redefine_color,
    resolves_the_four_collisions,
    token,
)


# ── axis 1 frozen ───────────────────────────────────────────────────────

def test_the_palette_refuses_redefinition():
    for color, candidate in (("white", "void"), ("black", "restricted"),
                             ("yellow", "candidate"),
                             ("orange", "hold")):
        r = redefine_color(color, candidate)
        assert r["applied"] is False
        assert r["reason"] == "E_COLOR_AXIS_FROZEN"
        assert r["lawful_door"] == "receipted operator amendment"


def test_the_atlas_lifecycle_is_intact():
    assert wa.EPISTEMIC_PHASE["white"] == "replayable"
    assert wa.EPISTEMIC_PHASE["black"] == "unknown"
    assert wa.EPISTEMIC_PHASE["yellow"] == "sealed"
    assert wa.EPISTEMIC_PHASE["orange"] == "review"
    assert wa.EPISTEMIC_PHASE["red"] == "breach"
    assert len(wa.EPISTEMIC_PHASE) == 8
    assert len(wa.LIFECYCLE_ORDER) == 7      # breach is off-lifecycle


# ── composition across the two axes ─────────────────────────────────────

def test_the_ruling_example_tokens_compose():
    assert token("purple", ("candidate",))["reading"] == \
        "claim + candidate"
    assert token("orange", ("hold",))["reading"] == "review + hold"
    assert token("blue", ("restricted",))["reading"] == \
        "observed + restricted"


def test_a_phase_with_no_marker_is_still_lawful():
    t = token("green")
    assert t["ok"] is True and t["phase"] == "admitted"
    assert t["markers"] == ()


def test_axis_confusion_is_caught_in_both_directions():
    # a marker used where a phase belongs
    assert token("restricted")["reason"] == "E_AXIS_CONFUSION"
    # a phase name used where a marker belongs
    assert token("green", ("admitted",))["reason"] == "E_AXIS_CONFUSION"


def test_unknown_symbols_are_refused_not_guessed():
    assert token("chartreuse")["reason"] == "E_UNKNOWN_COLOR"
    assert token("green", ("sparkly",))["reason"] == "E_UNKNOWN_MARKER"


# ── growth happens on axis 2 only ───────────────────────────────────────

def test_new_concepts_enter_the_marker_axis():
    r = add_marker("quarantined", "held pending rights review")
    assert r["added"] is True and r["axis"] == "MARKERS"
    assert r["collides_with_color_axis"] is False


def test_a_new_marker_may_not_shadow_a_phase():
    assert add_marker("sealed", "x")["reason"] == "E_AXIS_CONFUSION"


# ── the immunity proof and the four collisions ──────────────────────────

def test_the_axes_are_disjoint_so_no_future_collision():
    v = axes_are_disjoint()
    assert v["disjoint"] is True
    assert v["value_overlap"] == []
    assert v["future_collision_possible"] is False
    assert v["color_axis_frozen"] is True


def test_all_four_collisions_dissolve_without_touching_the_atlas():
    v = resolves_the_four_collisions()
    assert set(v["collisions"]) == {"white", "black", "yellow",
                                    "orange"}
    assert all(c["rehomed_to"] == "MARKERS"
               for c in v["collisions"].values())
    assert v["atlas_entries_changed"] == 0
    assert v["one_color_one_meaning"] is True
    assert v["verdict"] == "RESOLVED_BY_FACTORING"


def test_every_rehomed_meaning_exists_on_the_marker_axis():
    for c in resolves_the_four_collisions()["collisions"].values():
        assert c["candidate_meaning"] in wa.STATE_MARKERS


def test_deterministic():
    assert wa.canon(axes_are_disjoint()) == wa.canon(axes_are_disjoint())


# ── sigma as a product type; chi projects E alone ──────────────────────

def _sig(**o):
    d = dict(E="observed", A="open", D="active", U="granted",
             R="replayable")
    d.update(o)
    return wa.sigma(**d)


def test_sigma_needs_all_five_projections():
    v = wa.sigma(E="observed", A="open")
    assert v["ok"] is False and v["reason"] == "E_INCOMPLETE_SIGMA"
    assert set(v["missing"]) == {"D", "U", "R"}


def test_a_projection_may_not_borrow_another_domain():
    v = _sig(A="hold")            # hold is a disposition, not access
    assert v["reason"] == "E_PROJECTION_DOMAIN_VIOLATION"


def test_chi_reads_only_the_epistemic_projection():
    c = wa.chi(_sig(E="admitted"))
    assert c["colour"] == "green"
    assert c["reads_projection"] == "E"
    assert set(c["ignores"]) == {"A", "D", "U", "R"}


def test_same_colour_never_entails_same_state():
    """The falsifier the collision was hiding."""
    a = _sig(E="observed", A="open", U="granted")
    b = _sig(E="observed", A="restricted", U="denied")
    v = wa.same_colour_same_state(a, b)
    assert v["same_colour"] is True
    assert v["same_state"] is False
    assert v["differing_projections"] == ["A", "U"]
    assert v["colour_entails_state"] is False


def test_each_marker_declares_its_projection():
    assert wa.marker_projection("restricted")["projection"] == "A"
    assert wa.marker_projection("hold")["projection"] == "D"
    assert wa.marker_projection("authority_denied")["projection"] == "U"
    assert wa.marker_projection("nope")["reason"] == "E_UNKNOWN_MARKER"


def test_conformance_restoration_is_not_a_constitutional_change():
    v = wa.conformance_restoration_is_not_amendment(
        "one colour => one epistemic meaning", was_violated=True)
    assert v["action"] == "CONFORMANCE_RESTORATION"
    assert v["is_constitutional_change"] is False
    assert v["requires_amendment_door"] is False
