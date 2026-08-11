"""Falsifiers for the projection layer. The renderer must be
constitutionally incapable of minting reality."""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wul_visual_ir as ir
from wul_visual_ir import (
    VisualEdge,
    VisualGraph,
    VisualNode,
    helen_c17_coverage,
    helen_goblin_garden,
    helen_witness_flow,
    sacred_map,
)


# ── the projection cannot carry authority ───────────────────────────────

def test_ir_forbidden_boundary_is_frozen_not_the_vocabulary():
    """Test the forbidden boundary, never the exact permissible set —
    else adding chi (legitimate) would falsely read as an authority leak.
    Closed AUTHORITY surface != frozen visual vocabulary."""
    fields = {f.name for f in dataclasses.fields(VisualNode)}
    forbidden = {"authority", "admit", "mint_capability",
                 "authorization_instance_mutator", "ledger_append",
                 "commit", "mutate_governed_state"}
    assert forbidden.isdisjoint(fields)          # the constitutional line
    n = VisualNode("x", "SEED", "RAW", "x")
    assert not hasattr(n, "authority")
    with pytest.raises(TypeError):
        VisualNode("x", "SEED", "RAW", "x", authority=1)


def test_ir_exposes_the_expected_constitutional_channels():
    """Positive contract, separate from the forbidden-boundary test.
    These channels MUST exist; additions beyond them are permitted."""
    fields = {f.name for f in dataclasses.fields(VisualNode)}
    assert {"node_id", "tau", "phi", "chi", "label"}.issubset(fields)
    assert {"frame_ref", "provenance_ref"}.issubset(fields)


def test_module_exposes_no_mutation_or_inverse():
    """No admit, no mint, no ledger write, and no SVG->state inverse.
    D_AntV o pi_WUL exists; the inverse does not."""
    names = {n for n in dir(ir) if not n.startswith("_")}
    for banned in ("admit", "mint", "ledger_write", "commit", "from_svg",
                   "parse_svg", "to_state", "rehydrate"):
        assert not any(banned in n.lower() for n in names), banned


def test_provenance_is_a_reference_not_the_evidence():
    n = VisualNode("x", "WITNESS", "OBSERVED", "w", provenance_ref="receipt://r1")
    assert n.provenance_ref == "receipt://r1"   # a pointer, drill-down only


# ── THE NON-FUSION LAW as a graph property ──────────────────────────────

def test_two_pass_nodes_with_unwitnessed_edge_is_discontinuous():
    """The central visual claim: conventional dashboards propagate green
    downstream. Here a CLAIMED edge between two PASS nodes breaks the
    path, and the break is NAMED."""
    g = VisualGraph("t")
    g.add_node(VisualNode("a", "HAL", "PASS", "HAL"))
    g.add_node(VisualNode("b", "GATEHOUSE", "PASS", "GATE"))
    g.add_edge("a", "b", "CLAIMED")          # unwitnessed relation
    v = g.path_verdict(["a", "b"])
    assert v["verdict"] == "DISCONTINUOUS"
    assert v["break_at"] == ("a", "b")
    assert v["reason"] == "E_EDGE_CLAIMED"
    # 🟢🛡 does not imply 🟢⚖ — even though BOTH nodes are green.
    assert g.nodes["a"].phi == "PASS" and g.nodes["b"].phi == "PASS"


def test_witnessed_edges_do_make_a_continuous_path():
    """Positive control: the law must not be vacuous."""
    g = VisualGraph("t")
    g.add_node(VisualNode("a", "HAL", "PASS", "HAL"))
    g.add_node(VisualNode("b", "GATEHOUSE", "PASS", "GATE"))
    g.add_edge("a", "b", "WITNESSED")
    assert g.path_verdict(["a", "b"])["verdict"] == "WITNESSED_CONTINUOUS"


def test_missing_edge_breaks_a_path_of_green_nodes():
    g = VisualGraph("t")
    g.add_node(VisualNode("a", "HAL", "PASS", "a"))
    g.add_node(VisualNode("b", "GATEHOUSE", "PASS", "b"))
    v = g.path_verdict(["a", "b"])
    assert v["verdict"] == "DISCONTINUOUS" and v["reason"] == "E_NO_EDGE"


def test_a_weak_node_breaks_an_all_witnessed_path():
    g = VisualGraph("t")
    g.add_node(VisualNode("a", "CANDIDATE", "HYPOTHESIS", "a"))
    g.add_node(VisualNode("b", "GATEHOUSE", "PASS", "b"))
    g.add_edge("a", "b", "WITNESSED")
    v = g.path_verdict(["a", "b"])
    assert v["verdict"] == "DISCONTINUOUS" and v["reason"] == "E_NODE_NOT_PASS"


# ── forbidden morphisms: the visual constitution ────────────────────────

@pytest.mark.parametrize("src_tau,dst_tau", sorted(ir.FORBIDDEN_MORPHISMS))
def test_forbidden_morphism_cannot_be_drawn_as_a_normal_relation(src_tau, dst_tau):
    g = VisualGraph("t")
    g.add_node(VisualNode("s", src_tau, "PASS", "s"))
    g.add_node(VisualNode("d", dst_tau, "PASS", "d"))
    for rho in ("CLAIMED", "OBSERVED", "WITNESSED", "ADMITTED"):
        with pytest.raises(ValueError, match="E_FORBIDDEN_MORPHISM"):
            g.add_edge("s", "d", rho)
    e = g.add_edge("s", "d", "FORBIDDEN")     # may only be drawn as ╳
    assert e.rho == "FORBIDDEN"


def test_forbidden_edge_is_never_a_continuous_path():
    g = sacred_map()
    v = g.path_verdict(["goblin", "lease"])   # 👺 ╳ 🔑
    assert v["verdict"] == "FORBIDDEN" and v["reason"] == "E_CONSTITUTIONAL"


def test_sacred_map_renders_the_impossible_explicitly():
    syntax = sacred_map().to_antv()
    assert "FORBIDDEN ╳" in syntax          # drawn, not hidden


# ── chi is a third axis: not epistemic, not authority ───────────────────

def test_chi_advances_without_touching_phi():
    n = VisualNode("x", "CANDIDATE", "HYPOTHESIS", "c", chi="root")
    for _ in range(3):
        n = n.advance_chi()
    assert n.chi == "heart"          # visual progression happened
    assert n.phi == "HYPOTHESIS"     # epistemic state did NOT move
    assert not hasattr(n, "authority")


def test_chi_saturates_and_never_becomes_a_verdict():
    n = VisualNode("x", "SEED", "RAW", "s", chi="crown")
    assert n.advance_chi().chi == "crown"       # no overflow
    assert n.advance_chi().phi == "RAW"         # crown != PASS


# ── presentation edits are not semantic edits ───────────────────────────

def test_recolouring_a_projection_does_not_change_source_phase():
    """Editing the infographic edits the PROJECTION. A node recoloured in
    the rendering leaves the IR — and therefore phi — untouched."""
    g = helen_witness_flow()
    before = g.nodes["hal"].phi
    edited_syntax = g.to_antv().replace("#dc2626", "#16a34a")  # paint it green
    assert "#16a34a" in edited_syntax
    assert g.nodes["hal"].phi == before          # source of truth unmoved
    # and no function exists to push that edit back:
    assert not hasattr(ir, "apply_syntax")


# ── chromodynamic compliance of the compiled surface ────────────────────

def test_palette_order_matches_node_phases():
    g = VisualGraph("t")
    g.add_node(VisualNode("a", "HAL", "FAIL", "a"))
    g.add_node(VisualNode("b", "GATEHOUSE", "PASS", "b"))
    syntax = g.to_antv()
    palette = [l for l in syntax.splitlines() if l.strip().startswith("palette")][0]
    assert palette.strip() == f"palette {ir.PHASE_COLOR['FAIL']} {ir.PHASE_COLOR['PASS']}"
    assert '"' not in palette and "," not in palette      # bare values, DSL rule


def test_phase_is_also_written_in_text_so_colour_is_never_the_only_carrier():
    n = VisualNode("a", "HAL", "FAIL", "checker")
    r = n.render()
    assert "🔴" in r and "🛡️" in r and "[FAIL]" in r      # survives grayscale


def test_untyped_glyph_phase_relation_rejected():
    with pytest.raises(ValueError, match="E_UNTYPED_GLYPH"):
        VisualNode("x", "WIZARD", "PASS", "x")
    with pytest.raises(ValueError, match="E_UNTYPED_PHASE"):
        VisualNode("x", "SEED", "GLOWING", "x")
    with pytest.raises(ValueError, match="E_UNTYPED_CHI"):
        VisualNode("x", "SEED", "PASS", "x", chi="ascended")
    with pytest.raises(ValueError, match="E_UNTYPED_RELATION"):
        VisualEdge("a", "b", "VIBES")


# ── the three structures ────────────────────────────────────────────────

def test_witness_flow_breaks_where_the_edge_breaks():
    """The whole spine is green-noded; one unwitnessed edge and the chain
    is not a validated system."""
    g = helen_witness_flow(edge_status={("hal", "gate"): "CLAIMED"})
    full = ["hal", "gate", "alpha", "lease"]
    v = g.path_verdict(full)
    assert v["verdict"] == "DISCONTINUOUS" and v["break_at"] == ("hal", "gate")
    g2 = helen_witness_flow()                     # all witnessed
    assert g2.path_verdict(full)["verdict"] == "WITNESSED_CONTINUOUS"


def test_goblin_garden_is_topology_with_compost_loop_and_no_votes():
    g = helen_goblin_garden([
        {"operator": "F", "variation": "v1", "outcome": "FAIL"},
        {"operator": "D", "variation": "v2", "outcome": "UNKNOWN"},
        {"operator": "X", "variation": "v3", "outcome": "PASS"},
    ])
    # compost loop closes back to the seed
    assert any(e.src.startswith("compost") and e.dst == "seed" for e in g.edges)
    syntax = g.to_antv()
    for banned in ("vote", "majority", "consensus", "score"):
        assert banned not in syntax.lower()
    # three independent branches, not one averaged answer
    assert sum(1 for n in g.nodes.values() if n.tau == "CANDIDATE") == 3


def test_c17_coverage_short_circuits_to_unknown_on_open_u():
    g = helen_c17_coverage(d_pos=4, d_neg=1, u_open=["env_read"], stable=True)
    assert "unknown" in g.nodes
    assert "verdict" not in g.nodes        # stability never even consulted
    ok = helen_c17_coverage(4, 1, [], stable=True)
    assert ok.nodes["verdict"].label == "VALID_BY_TRANSPORT"
    bad = helen_c17_coverage(4, 1, [], stable=False)
    assert bad.nodes["verdict"].label == "INVALIDATED"


def test_compiled_syntax_obeys_antv_dsl_rules():
    syntax = helen_witness_flow().to_antv()
    lines = syntax.splitlines()
    assert lines[0].startswith("infographic ")      # first line, hard rule
    assert lines[1] == "data"
    assert any(l.startswith("  nodes") for l in lines)
    assert any(l.startswith("  relations") for l in lines)
    assert any(l.startswith("theme") for l in lines)


def test_deterministic():
    a = helen_witness_flow().to_antv()
    b = helen_witness_flow().to_antv()
    assert a == b


# ═══ WVIS-01..04 — the architect's named constitutional falsifiers ══════

def test_WVIS_01_authority_injection_rejected_by_schema():
    """Authority is not a false field; it is an ABSENT one. The schema
    cannot be handed authority through any name."""
    for banned in ("authority", "admit", "mint_capability",
                   "authorization_instance_mutator", "ledger_append", "commit"):
        with pytest.raises(TypeError):
            VisualNode("x", "SEED", "RAW", "x", **{banned: 1})


def test_WVIS_02_unknown_c17_node_never_defaults_green():
    """An UNKNOWN C17 verdict rendered through the compiler must remain
    UNKNOWN — no default styling, fallback template, missing field, or
    fault tolerance may turn it green. phi_rendered == phi_machine."""
    g = helen_c17_coverage(d_pos=4, d_neg=1, u_open=["env_read"], stable=True)
    node = g.nodes["unknown"]
    assert node.phi == "UNKNOWN"
    syntax = g.to_antv()
    # the UNKNOWN colour is present; the PASS colour is nowhere near it
    assert ir.PHASE_COLOR["UNKNOWN"] in syntax
    assert "UNKNOWN" in node.render() and "🟡" in node.render()
    # the machine verdict has no VALID_BY_TRANSPORT node to accidentally show
    assert "verdict" not in g.nodes
    # every node's rendered phase equals its machine phase (no laundering)
    for n in g.nodes.values():
        assert f"[{n.phi}]" in n.render()


def test_WVIS_03_two_pass_nodes_fail_edge_preserves_the_fail_edge():
    """A FAIL/unwitnessed edge between two PASS nodes must survive
    compilation — the visualization cannot fuse it into a clean chain."""
    g = VisualGraph("t")
    g.add_node(VisualNode("a", "HAL", "PASS", "HAL"))
    g.add_node(VisualNode("b", "GATEHOUSE", "PASS", "GATE"))
    g.add_edge("a", "b", "CLAIMED")           # the broken relation
    assert g.path_verdict(["a", "b"])["verdict"] == "DISCONTINUOUS"
    syntax = g.to_antv()
    assert "CLAIMED" in syntax and "┄┄?┄┄>" in syntax   # edge status rendered


def test_WVIS_04_api_negative_check_no_named_inverse_today():
    """PARTIAL: Recolouring the AntV output green is a presentation edit
    and the source phi does not follow. This test asserts today's public
    API contains no named inverse (apply_syntax/from_svg/parse_svg).

    Honest scope, per the architect ruling: this is an API_NEGATIVE_CHECK,
    NOT a structural proof of non-reversibility. The stronger property
    to earn later is:
        R: X_machine -> V exists ; V -> X_machine is NOT in the public API.
    """
    g = helen_c17_coverage(4, 1, ["env_read"], stable=True)
    src_phase = g.nodes["unknown"].phi
    edited = g.to_antv().replace(ir.PHASE_COLOR["UNKNOWN"], ir.PHASE_COLOR["PASS"])
    assert ir.PHASE_COLOR["PASS"] in edited                       # projection changed
    assert g.nodes["unknown"].phi == src_phase == "UNKNOWN"       # source did not
    # negative-check of the current public API surface only:
    for named_inverse in ("apply_syntax", "from_svg", "parse_svg",
                          "svg_to_state", "rehydrate_from_svg"):
        assert not hasattr(ir, named_inverse), \
            f"named inverse {named_inverse!r} would require this test to be strengthened"


# ═══ chi channel isolation — chi styling cannot overwrite phi ═══════════

def test_chi_and_phi_live_on_distinct_channels():
    """A high-maturation falsified node: purple HALO around a red CORE,
    never an ambiguous purple-red blend."""
    n = VisualNode("g", "GOBLIN", "FAIL", "goblin", chi="third_eye")
    ch = n.channels()
    assert ch["core"] == ir.PHASE_COLOR["FAIL"]        # phi owns the core
    assert ch["halo"] == ir.CHI_MARK["third_eye"]      # chi owns the halo
    assert ch["core"] != ch["halo"]                    # never the same channel
    # advancing maturation does not touch the epistemic core
    matured = n.advance_chi()
    assert matured.channels()["core"] == ir.PHASE_COLOR["FAIL"]
    assert matured.phi == "FAIL"


# ═══ WVIS-05 · channel non-interference — chi ⊬ phi (ruling addition) ═══

def test_WVIS_05_channel_noninterference_delta_chi_never_moves_phi():
    """chi changes must be perfectly orthogonal: Delta chi != 0 while
    Delta phi = 0, Delta rho = 0, Delta X_machine = 0."""
    n0 = VisualNode("g", "GOBLIN", "FAIL", "goblin",
                    chi="root", frame_ref="F0", provenance_ref="r1")
    n1 = n0.advance_chi()
    assert n1.chi != n0.chi                                # Delta chi != 0
    for axis in ("tau", "phi", "label", "frame_ref", "provenance_ref"):
        assert getattr(n1, axis) == getattr(n0, axis)     # nothing else moved
    ch0, ch1 = n0.channels(), n1.channels()
    assert ch1["core"] == ch0["core"]                     # phi core unchanged
    assert ch1["halo"] != ch0["halo"]                     # chi halo did move
    assert ch1["core"] != ch1["halo"]                     # never same channel


# ═══ Closed schema — the ruling's additionalProperties:false, as code ═══

def test_closed_schema_rejects_authority_field_by_name():
    for banned in ("authority", "admit", "mint_capability",
                   "authorization_instance_mutator", "ledger_append",
                   "commit", "mutate_governed_state"):
        with pytest.raises(ValueError, match="E_AUTHORITY_INJECTION"):
            ir.validate_node_dict({"node_id": "x", "tau": "SEED",
                                   "phi": "RAW", "label": "x", banned: 1})


def test_closed_schema_rejects_unknown_fields_never_ignores_them():
    with pytest.raises(ValueError, match="E_UNKNOWN_FIELDS"):
        ir.validate_node_dict({"node_id": "x", "tau": "SEED", "phi": "RAW",
                               "label": "x", "sovereign_hint": True})
    ir.validate_node_dict({"node_id": "x", "tau": "SEED", "phi": "RAW",
                           "label": "x"})   # minimal legal shape passes


def test_closed_schema_also_guards_edges():
    with pytest.raises(ValueError, match="E_AUTHORITY_INJECTION"):
        ir.validate_edge_dict({"src": "a", "dst": "b", "rho": "WITNESSED",
                               "admit": True})


# ═══ Projection Fidelity V0 — decodable, not decorative ════════════════

def test_projection_fidelity_decodes_the_protected_coordinates():
    """The ruling's V0 theorem: P(R(v)) equivalent to v on {tau, phi}.
    A property that is only asserted by decoration is untestable; making
    it computable turns 'AntV renders correctly' into a refutable claim."""
    for tau in ("SEED", "GOBLIN", "HAL", "GATEHOUSE", "LEDGER"):
        for phi in ("RAW", "OBSERVED", "UNKNOWN", "PASS", "FAIL", "EXECUTED"):
            n = VisualNode("x", tau, phi, "label")
            r = ir.projection_fidelity(n)
            assert r["faithful"], r


def test_projection_fidelity_catches_unknown_masquerading_as_pass():
    """WVIS-02, sharpened: the fidelity check ACTIVELY refuses to accept a
    decoded PASS for an UNKNOWN source. This is the anti-laundering test
    the ruling names as decodable projection fidelity."""
    n = VisualNode("u", "HAL", "UNKNOWN", "u")
    faithful = ir.projection_fidelity(n)
    assert faithful["decoded"]["phi"] == "UNKNOWN"
    # a tampered render that swaps the phase mark to green is DETECTED,
    # because the decoder reads the actual bytes, not the claim:
    fake = "🟢🛡️ u [PASS]·χ🔴"
    decoded = ir.parse_node_render(fake)
    assert decoded != {"tau": n.tau, "phi": n.phi}   # inequality is proof


# ═══ Two-membrane closure — C17 + WVIS chain up to a single law ═════════

def test_two_membrane_closure_witness_transport_does_not_imply_visual_promotion():
    """C17 protects transport of evidence; WVIS protects transport of its
    perception. A C17 verdict of TRANSPORTED renders as TRANSPORTED, not
    as an upgraded PASS or a downstream ADMIT."""
    transported = VisualNode("v", "REPLAY", "TRANSPORTED", "W_{F1}")
    assert ir.projection_fidelity(transported)["decoded"]["phi"] == "TRANSPORTED"
    # and no code path can promote it further from the visual layer:
    for banned in ("promote", "admit", "canonize", "seal"):
        assert not any(banned in n.lower() for n in dir(ir) if not n.startswith("_"))
