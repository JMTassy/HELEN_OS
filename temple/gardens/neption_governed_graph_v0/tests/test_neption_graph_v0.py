#!/usr/bin/env python3
"""Tests for NEPTION GOVERNED GRAPH V0 — the constitutional laws, mechanically."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from neption_wulwall_v0 import (Graph, Node, Edge, color, SEM_COLOR, load_sample,  # noqa
                                ENTITY_TYPES, SEMANTIC_STATES)

SAMPLE = str(Path(__file__).resolve().parents[1] / "neption_graph_sample_v0.json")


# 1. semantic/entity orthogonality — the two axes are independent fields.
def test_entity_semantic_orthogonal():
    a = Node("n1", "PARTNERSHIP", "POSSIBILITY", "GARDEN")   # partnership yet only POSSIBILITY
    b = Node("n2", "OPPORTUNITY", "OBSERVED", "GARDEN")      # opportunity yet OBSERVED
    assert a.entity_type != a.semantic_state
    # entity_type does not constrain semantic_state and vice-versa
    assert a.entity_type == "PARTNERSHIP" and a.semantic_state == "POSSIBILITY"
    assert b.entity_type == "OPPORTUNITY" and b.semantic_state == "OBSERVED"


# 2. no self-promotion — an edge cannot license or parent itself.
def test_no_self_promotion():
    g = Graph()
    rec = g.propose_mutation({"kind": "semantic_promote", "edge_id": "e9",
                              "from": "OBSERVED", "to": "ADMITTED",
                              "licensing_witness": "e9",  # self!
                              "provenance_root_ids": ["r1"]})
    assert rec["verdict"] == "DENY"
    assert rec["rule"] == "NO_SELF_PROMOTION"


# 3. provenance-root dedup — 3 documents from 1 root = 1 independent root.
def test_provenance_root_dedup():
    g = Graph()
    n = g.independent_roots(["press_release_1", "press_release_1", "press_release_1"])
    assert n == 1                      # volume 3 != independence 1
    n2 = g.independent_roots(["press_release_1", "blog_repost_1"])
    assert n2 == 2


# 4. governance-frame isolation — GARDEN cannot jump to CANON.
def test_governance_frame_isolation():
    g = Graph()
    rec = g.propose_mutation({"kind": "governance_escalation", "edge_id": "e1",
                              "from": "GARDEN", "to": "CANON"})
    assert rec["verdict"] == "DENY"    # skips rungs AND V0 has no CANON path


# 5. P ↛ T — presentation cannot mutate typed state.
def test_presentation_cannot_mutate_state():
    g = Graph()
    rec = g.propose_mutation({"kind": "semantic_promote", "edge_id": "e5",
                              "from": "POSSIBILITY", "to": "ADMITTED",
                              "created_from": "ansi"})
    assert rec["verdict"] == "DENY"
    assert rec["rule"] == "P↛T"
    # structural: color is a pure fn of state; there is NO setter from color
    import neption_wulwall_v0 as m
    assert not hasattr(m, "state_from_color")
    assert color("CLAIM") == color("CLAIM")          # deterministic
    assert color("CLAIM") != color("ADMITTED")


# 6. illegal transition receives a DENY receipt (never silently dropped).
def test_illegal_transition_is_receipted():
    g = Graph()
    before = len(g.receipts)
    rec = g.propose_mutation({"kind": "relation_escalation", "edge_id": "e7",
                              "from": "MENTION", "to": "PARTNERSHIP",
                              "provenance_root_ids": ["r1"]})
    assert rec["verdict"] == "DENY"
    assert len(g.receipts) == before + 1             # the attempt is remembered
    assert "hash" in rec and rec["prev_hash"] != rec["hash"]


# 7. deterministic replay of the sample graph (same bytes → same receipt chain).
def test_deterministic_replay():
    def run():
        g = load_sample(SAMPLE)
        attacks = [
            {"kind": "relation_escalation", "edge_id": "a", "from": "MENTION",
             "to": "PARTNERSHIP", "provenance_root_ids": ["r1"]},
            {"kind": "semantic_promote", "edge_id": "b", "from": "CLAIM",
             "to": "ADMITTED", "provenance_root_ids": ["r1"]},
        ]
        for a in attacks:
            g.propose_mutation(a)
        return g._rho
    assert run() == run()                            # identical final receipt hash


# 8. ANSI rendering cannot mutate typed state (render is read-only over state).
def test_render_does_not_mutate_state():
    g = load_sample(SAMPLE)
    before = {nid: n.semantic_state for nid, n in g.nodes.items()}
    _ = g.render_wall()
    after = {nid: n.semantic_state for nid, n in g.nodes.items()}
    assert before == after                           # wall is pure presentation


# extra: opportunity laundering CLAIM→ADMITTED is denied.
def test_opportunity_laundering_denied():
    g = Graph()
    rec = g.propose_mutation({"kind": "semantic_promote", "edge_id": "z",
                              "from": "CLAIM", "to": "ADMITTED",
                              "licensing_witness": "gate1",
                              "provenance_root_ids": ["r1"]})
    assert rec["verdict"] == "DENY"     # must pass through OBSERVED first


# extra: authority_delta != 0 is denied (no self-amplification in V0).
def test_authority_delta_must_be_zero():
    g = Graph()
    rec = g.propose_mutation({"kind": "semantic_promote", "edge_id": "q",
                              "from": "OBSERVED", "to": "ADMITTED",
                              "authority_delta": 1, "licensing_witness": "w"})
    assert rec["verdict"] == "DENY"
    assert rec["rule"] == "ΔA=0"


if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])
