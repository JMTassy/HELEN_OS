"""Falsifiers for the render path: design-memory -> WVIS -> SVG.

The render is downstream of the membrane. It must inherit every refusal
and mint nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "wul_visual"))

import design_memory as dm            # noqa: E402
import render_border as rb            # noqa: E402
from design_memory import Composition, Operator, Primitive, apply_transform  # noqa: E402


def _render():
    comp = rb.build_composition()
    verdict = dm.chiddush(rb.CORPUS, comp)
    _graph, fid = rb.project(comp)
    return comp, verdict, fid, rb.build_svg(comp, verdict, fid)


# ── the render inherits the refusal: no chiddush, no SVG ───────────────

def test_anachronistic_operator_stops_the_pipeline_before_any_render():
    """An operator outside the 1902 corpus never reaches the renderer.
    The membrane refuses upstream; there is no 'render it anyway' path."""
    bad = Composition("smuggled", parts=(
        apply_transform(Primitive("p", "seed"),
                        Operator("gradient_mesh", (), source_ref="modern tool")),))
    v = dm.chiddush(rb.CORPUS, bad)
    assert v["verdict"] == "REJECT"
    assert "artifact" not in v            # nothing exists to hand the renderer


# ── the SVG carries no authority ───────────────────────────────────────

def test_svg_contains_no_authority_bearing_field():
    _c, _v, _f, svg = _render()
    low = svg.lower()
    for banned in ("admit", "authority=1", 'authority="1"', "mint_cap",
                   "ledger_append", "canon=true", "valid_by_transport"):
        assert banned not in low, banned
    # and it says so, visibly, on the face of the render
    assert "A = 0" in svg and "LEDGER_EFFECT = NONE" in svg


def test_render_declares_candidate_status_never_pass():
    """Beauty does not promote. The artifact is rendered as a CANDIDATE
    with its verdict printed; nothing in the SVG claims PASS or ADMITTED."""
    _c, verdict, _f, svg = _render()
    assert verdict["verdict"] == "CANDIDATE_PROPOSED"
    assert "CANDIDATE_PROPOSED" in svg
    assert "PASS" not in svg and "ADMITTED" not in svg


# ── phi survives the crossing (projection fidelity) ────────────────────

def test_every_projected_node_is_faithful():
    _c, _v, fid, _out = _render()
    assert fid, "projection produced no nodes"
    for name, f in fid:
        assert f["faithful"], (name, f)


def test_artifact_node_stays_hypothesis_through_projection():
    comp = rb.build_composition()
    graph, _fid = rb.project(comp)
    assert graph.nodes["artifact"].phi == "HYPOTHESIS"   # not upgraded
    assert graph.nodes["primitive"].phi == "HYPOTHESIS"  # my form, unwitnessed
    for t in comp.parts:                                  # cited operators
        assert graph.nodes[f"op_{t.operator.op_id}"].phi == "OBSERVED"


# ── the honest verdict: a pretty border is NOT a proven thing ──────────

def test_path_to_the_artifact_is_discontinuous_by_construction():
    """The non-fusion law fires on our OWN artifact. The operators are
    witnessed, but the form is original — so the chain from primitive to
    artifact is CLAIMED, and the path verdict must say so. A border can
    be beautiful, lineage-closed, and still not a proof."""
    comp = rb.build_composition()
    graph, _fid = rb.project(comp)
    v = graph.path_verdict(["primitive", "artifact"])
    assert v["verdict"] == "DISCONTINUOUS"
    assert v["reason"] == "E_EDGE_CLAIMED"
    # while a CITED operator's edge to the artifact is witnessed
    op = f"op_{comp.parts[0].operator.op_id}"
    assert any(e.src == op and e.dst == "artifact" and e.rho == "WITNESSED"
               for e in graph.edges)


# ── no reverse path: editing the render changes nothing upstream ───────

def test_editing_the_svg_does_not_touch_the_composition():
    comp, _v, _f, svg = _render()
    before = comp.lineage()
    edited = svg.replace(rb.INK, "#00ff00").replace("A = 0", "A = 1")
    assert "#00ff00" in edited and "A = 1" in edited   # the render changed
    assert comp.lineage() == before                     # the source did not
    for banned in ("from_svg", "parse_svg", "svg_to_composition", "apply_svg"):
        assert not hasattr(rb, banned), banned


# ── determinism ────────────────────────────────────────────────────────

def test_render_is_byte_deterministic():
    _c1, _v1, _f1, a = _render()
    _c2, _v2, _f2, b = _render()
    assert a == b


def test_geometry_is_computed_not_traced():
    """Every path comes from parameters. Changing a parameter changes the
    output — proof the form is generated, not embedded."""
    d1 = rb.seed_d(0, 0, 20, 30)
    d2 = rb.seed_d(0, 0, 40, 30)
    assert d1 != d2 and d1.startswith("M ") and "Q " in d1
    assert "<image" not in rb.build_svg(*_render()[:3])   # no embedded raster
