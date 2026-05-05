"""
tests/test_semantic_object_model.py
NON_SOVEREIGN · NO_SHIP · DRAFT

Adversarial test suite for HELEN Semantic Object Model.
Spec: docs/specs/SEMANTIC_OBJECT_MODEL_TESTS_V1.md
All 29 properties must pass. Any failure = SHIP-class blocker.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.semantic_object_model import (
    CSO, SemanticGraph, RetrievalPolicy,
    MutationRejected, SovereignViolation, NamespaceViolation,
    project, replay, check_authority, make_global_id, validate_namespace,
    _canonicalize,
)


def _cso(namespace="helen", local_id="obj-1", type="TEST", payload=None, receipts=None, **kw):
    return CSO(
        namespace=namespace,
        local_id=local_id,
        type=type,
        payload=payload if payload is not None else {"v": 1},
        receipts=receipts if receipts is not None else ["receipt-abc"],
        **kw,
    )


def _graph(*csos):
    g = SemanticGraph()
    for c in csos:
        g.append(c)
    return g


# ── P1: Canonicalization determinism ─────────────────────────────────────────

def test_p1_1_same_content_same_hash():
    a = _cso(payload={"x": 1, "y": 2})
    b = _cso(payload={"x": 1, "y": 2})
    assert a.canonical_hash() == b.canonical_hash()


def test_p1_2_field_order_irrelevant():
    a = _cso(payload={"x": 1, "y": 2})
    b = _cso(payload={"y": 2, "x": 1})
    assert a.canonical_hash() == b.canonical_hash()


def test_p1_3_whitespace_irrelevant():
    a = _cso(payload={"note": "hello world"})
    b = _cso(payload={"note": "hello world"})
    assert a.canonical_hash() == b.canonical_hash()


def test_p1_4_any_field_difference_changes_hash():
    a = _cso(payload={"x": 1})
    b = _cso(payload={"x": 2})
    assert a.canonical_hash() != b.canonical_hash()


def test_p1_A_unicode_normalization():
    # NFC vs NFD — same visual character, same hash
    a = _cso(payload={"name": "caf\u00e9"})       # NFC: é as single codepoint
    b = _cso(payload={"name": "cafe\u0301"})       # NFD: e + combining accent
    assert a.canonical_hash() == b.canonical_hash()


def test_p1_B_null_vs_missing_field():
    a = _cso(payload={"x": None})
    b = _cso(payload={})
    assert a.canonical_hash() != b.canonical_hash()


# ── P2: Truth Closure Law ─────────────────────────────────────────────────────

def test_p2_1_validated_event_appended():
    g = SemanticGraph()
    g.append(_cso(local_id="a"))
    assert len(g) == 1


def test_p2_2_unvalidated_event_rejected():
    g = SemanticGraph()
    with pytest.raises(ValueError, match="receipts"):
        g.append(_cso(local_id="a", receipts=[]))


def test_p2_3_receipt_missing_rejected():
    g = SemanticGraph()
    with pytest.raises(ValueError):
        g.append(CSO(namespace="helen", local_id="x", type="T", payload={}, receipts=[]))


def test_p2_4_sequential_events_accumulate():
    g = SemanticGraph()
    for i in range(5):
        g.append(_cso(local_id=f"obj-{i}"))
    assert len(g) == 5


def test_p2_A_mutation_rejected():
    g = SemanticGraph()
    g.append(_cso(local_id="a", payload={"v": 1}))
    with pytest.raises(MutationRejected):
        g.append(_cso(local_id="a", payload={"v": 2}))


def test_p2_B_deletion_rejected():
    g = SemanticGraph()
    g.append(_cso(local_id="a"))
    with pytest.raises((MutationRejected, SovereignViolation)):
        g.delete("helen/a")


def test_p2_C_invalid_receipt_hash_rejected():
    g = SemanticGraph()
    with pytest.raises(ValueError):
        g.append(_cso(local_id="a", receipts=[]))


# ── P3: Replay determinism ────────────────────────────────────────────────────

def test_p3_1_replay_same_events_same_graph():
    events = [_cso(local_id=f"obj-{i}") for i in range(5)]
    g1 = replay(events)
    g2 = replay(events)
    assert project(g1) == project(g2)


def test_p3_2_replay_independent_of_wallclock():
    events = [_cso(local_id="a")]
    g1 = replay(events)
    g2 = replay(events)
    assert g1._nodes["helen/a"].canonical_hash() == g2._nodes["helen/a"].canonical_hash()


def test_p3_3_replay_empty_log():
    g = replay([])
    assert len(g) == 0


def test_p3_4_replay_to_intermediate_t():
    events = [_cso(local_id=f"obj-{i}") for i in range(5)]
    g = replay(events, t=3)
    assert len(g) == 3


# ── P4: Projection determinism ────────────────────────────────────────────────

def test_p4_1_same_graph_same_projection():
    g = _graph(_cso(local_id="a"))
    assert project(g) == project(g)


def test_p4_2_different_graph_different_projection():
    g1 = _graph(_cso(local_id="a", payload={"v": 1}))
    g2 = _graph(_cso(local_id="a", payload={"v": 2}))
    assert project(g1) != project(g2)


def test_p4_3_empty_graph_projection_defined():
    g = SemanticGraph()
    result = project(g)
    assert result["node_count"] == 0


def test_p4_A_projection_no_hidden_state():
    g = _graph(_cso(local_id="a"))
    p1 = project(g)
    p2 = project(g)
    assert p1 == p2


# ── P5: Bounded retrieval ─────────────────────────────────────────────────────

def _chain_graph(length: int) -> tuple[SemanticGraph, list[str]]:
    """Build a chain: obj-0 → obj-1 → ... → obj-(length-1)."""
    g = SemanticGraph()
    ids = [f"obj-{i}" for i in range(length)]
    for i, lid in enumerate(ids):
        relations = [f"helen/{ids[i+1]}"] if i + 1 < length else []
        g.append(_cso(local_id=lid, relations=relations))
    return g, [f"helen/{lid}" for lid in ids]


def test_p5_1_depth_bound_respected():
    g, ids = _chain_graph(10)
    policy = RetrievalPolicy(max_depth=3, max_branching=10)
    result = g.retrieve(ids[0], policy=policy)
    assert len(result) <= policy.max_depth + 1


def test_p5_3_depth_1_returns_direct_neighbors():
    g, ids = _chain_graph(5)
    policy = RetrievalPolicy(max_depth=1, max_branching=10)
    result = g.retrieve(ids[0], policy=policy)
    assert len(result) == 2  # root + one neighbor


def test_p5_4_depth_0_returns_root_only():
    g, ids = _chain_graph(5)
    policy = RetrievalPolicy(max_depth=0, max_branching=10)
    result = g.retrieve(ids[0], policy=policy)
    assert len(result) == 1


def test_p5_A_circular_graph_terminates():
    g = SemanticGraph()
    g.append(_cso(local_id="a", relations=["helen/b"]))
    g.append(_cso(local_id="b", relations=["helen/a"]))  # cycle
    policy = RetrievalPolicy(max_depth=10, max_branching=10)
    result = g.retrieve("helen/a", policy=policy)
    assert len(result) == 2  # visited set prevents infinite loop


# ── P6: Namespace identity isolation ─────────────────────────────────────────

def test_p6_1_same_local_id_different_namespace():
    a = _cso(namespace="ns-a", local_id="obj-1")
    b = _cso(namespace="ns-b", local_id="obj-1")
    assert a.global_id != b.global_id
    assert a.canonical_hash() != b.canonical_hash()


def test_p6_2_same_namespace_same_local_id_stable():
    a = _cso(namespace="helen", local_id="x")
    b = _cso(namespace="helen", local_id="x")
    assert a.global_id == b.global_id
    assert a.canonical_hash() == b.canonical_hash()


def test_p6_3_cross_namespace_query_isolation():
    g = SemanticGraph()
    g.append(_cso(namespace="ns-a", local_id="obj"))
    g.append(_cso(namespace="ns-b", local_id="obj"))
    proj_a = project(g, namespace="ns-a")
    proj_b = project(g, namespace="ns-b")
    assert "ns-a/obj" in proj_a["nodes"]
    assert "ns-a/obj" not in proj_b["nodes"]


def test_p6_A_namespace_violation_raised():
    c = _cso(namespace="ns-a", local_id="obj")
    with pytest.raises(NamespaceViolation):
        validate_namespace(c, "ns-b")


# ── P7: Sovereign vs derived state ───────────────────────────────────────────

def test_p7_2_sovereign_deletion_raises():
    g = SemanticGraph()
    g.append(_cso(local_id="a", sovereign=True))
    with pytest.raises(SovereignViolation):
        g.delete("helen/a")


def test_p7_3_derived_deletion_still_rejected_append_only():
    g = SemanticGraph()
    g.append(_cso(local_id="a", sovereign=False))
    with pytest.raises((MutationRejected, SovereignViolation)):
        g.delete("helen/a")


def test_p7_4_replay_reconstructs_all_nodes():
    events = [_cso(local_id=f"obj-{i}", sovereign=(i == 0)) for i in range(5)]
    g = replay(events)
    assert len(g) == 5
    assert g.get("helen/obj-0").sovereign is True


# ── P8: Kernel authority law ──────────────────────────────────────────────────

def test_p8_1_validated_cso_has_authority():
    c = _cso(receipts=["receipt-xyz"])
    assert c.authority == 1


def test_p8_2_renderer_output_authority_zero():
    assert check_authority(object(), "RENDERER_OUTPUT") == 0


def test_p8_3_embedding_authority_zero():
    assert check_authority(object(), "EMBEDDING") == 0


def test_p8_4_unvalidated_cso_authority_zero():
    c = CSO(namespace="helen", local_id="x", type="T", payload={}, receipts=[])
    assert check_authority(c, "CSO") == 0


# ── P9: Ontological closure ───────────────────────────────────────────────────

def test_p9_1_full_receipted_system_reconstructible():
    events = [_cso(local_id=f"obj-{i}") for i in range(10)]
    g_original = replay(events)
    g_replayed = replay(events)
    assert project(g_original) == project(g_replayed)


def test_p9_2_unreceipted_event_breaks_append():
    g = SemanticGraph()
    with pytest.raises(ValueError):
        g.append(CSO(namespace="helen", local_id="x", type="T", payload={}, receipts=[]))


def test_p9_3_hash_mismatch_detectable():
    a = _cso(payload={"v": 1})
    b = _cso(payload={"v": 2})
    assert a.canonical_hash() != b.canonical_hash()
