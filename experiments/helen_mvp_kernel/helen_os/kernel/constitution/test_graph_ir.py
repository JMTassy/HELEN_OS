"""HELEN_GRAPH_IR_V0, falsified: the edge is non-promotional by
default; DATA may not carry authority; the three static checks refuse;
and the FOURTH — locally admissible everywhere, globally laundering —
is detected. That last one is the whole difference.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import graph_ir as gi
from graph_ir import (
    compile_graph,
    edge,
    expand_graph,
    globally_admissible,
    hold,
    painted_on,
    static_check,
    topology_rule,
)


# ── the edge under contract ────────────────────────────────────────────

def test_communication_is_non_promotional_by_default():
    e = edge("a", "b", "DATA", root="r1")
    assert e["ok"] is True
    assert (e["dP"], e["dA"], e["dE"]) == (0, 0, 0)


def test_a_delta_without_a_witness_is_refused():
    for d in ({"dP": 1}, {"dA": 1}, {"dE": 1}):
        assert edge("a", "b", "DERIVATION", **d)["reason"] == \
            "E_UNWITNESSED_PROMOTION"


def test_a_delta_with_a_witness_is_lawful():
    assert edge("a", "b", "DERIVATION", dP=1,
                witness="receipt:x")["ok"] is True


def test_a_data_edge_may_never_carry_authority_or_effect():
    assert edge("a", "b", "DATA", dA=1, witness="w")["reason"] == \
        "E_DATA_EDGE_CARRIES_AUTHORITY"
    assert edge("a", "b", "DATA", dE=1, witness="w")["reason"] == \
        "E_DATA_EDGE_CARRIES_AUTHORITY"


def test_an_unknown_edge_type_is_refused():
    assert edge("a", "b", "VIBES")["reason"] == "E_UNKNOWN_EDGE_TYPE"


def test_an_edge_that_transfers_nothing_is_painted_on():
    assert painted_on(edge("a", "b", "DATA"))["painted_on"] is True
    assert painted_on(edge("a", "b", "DATA", root="r1"))[
        "painted_on"] is False


# ── the three static checks ────────────────────────────────────────────

def test_the_three_static_checks_refuse():
    for premise, conclusion in gi.STATIC_CHECKS:
        v = static_check(premise, conclusion)
        assert v["licensed"] is False
        assert v["reason"] == \
            f"E_{premise}_DOES_NOT_ENTAIL_{conclusion}"
    assert len(gi.STATIC_CHECKS) == 3


def test_an_unnamed_inference_is_left_alone():
    assert static_check("EFFECT", "DATA")["licensed"] is None


def test_a_graph_of_well_typed_edges_compiles():
    v = compile_graph((edge("a", "b", "DATA", root="r"),
                       edge("b", "c", "DERIVATION", dP=1,
                            witness="w")))
    assert v["compiles"] is True
    assert v["static_checks_enforced"] == 3


def test_a_malformed_edge_stops_compilation():
    assert compile_graph((edge("a", "b", "DATA", dA=1, witness="w"),))[
        "compiles"] is False


# ── THE FOURTH: locally admissible, globally laundering ────────────────

def test_locally_admissible_does_not_entail_globally_admissible():
    """Four workers, each edge lawful, each preserving THE SAME root —
    and the merge reports four. Every node passes; the graph does
    not."""
    edges = tuple(edge(f"w{i}", "merge", "DATA", root="ATF_1900")
                  for i in range(4))
    v = globally_admissible(edges, merge_root_count=4)
    assert v["all_locally_admissible"] is True
    assert v["true_independent_roots"] == 1
    assert v["globally_admissible"] is False
    assert v["gap_detected"] is True
    assert v["reason"] == "E_ROOT_INFLATION_AT_MERGE"


def test_an_honest_merge_is_globally_admissible():
    edges = tuple(edge(f"w{i}", "merge", "DATA", root="ATF_1900")
                  for i in range(4))
    v = globally_admissible(edges, merge_root_count=1)
    assert v["globally_admissible"] is True
    assert v["gap_detected"] is False


def test_genuinely_distinct_roots_do_count():
    edges = (edge("w0", "m", "DATA", root="ATF_1900"),
             edge("w1", "m", "DATA", root="EXHIBITION_1851"))
    v = globally_admissible(edges, merge_root_count=2)
    assert v["true_independent_roots"] == 2
    assert v["globally_admissible"] is True


def test_an_empty_graph_is_refused():
    with pytest.raises(ValueError, match="E_EMPTY_GRAPH"):
        globally_admissible((), 1)


# ── HOLD as a productive object ────────────────────────────────────────

def test_a_hold_that_cannot_name_its_missing_witness_is_refused():
    v = hold(question="does border 4 register?")
    assert v["ok"] is False and v["reason"] == "E_UNTYPED_HOLD"
    assert "missing_witness" in v["missing"]


def test_a_typed_hold_becomes_an_acquisition_edge():
    u = hold(question="does any border outside 6/9/10 register?",
             missing_witness="catalogue line", discriminator="grep_ocr",
             cost=1, authority_required=0)
    v = expand_graph((edge("a", "b", "DATA", root="r"),), (u,))
    assert v["acquisition_edges_added"] == 1
    assert v["G_next_size"] == 2


def test_untyped_holds_do_not_expand_the_graph():
    v = expand_graph((), (hold(question="vague"),))
    assert v["acquisition_edges_added"] == 0
    assert v["untyped_holds_refused"] == 1


# ── topology ────────────────────────────────────────────────────────────

def test_a_transaction_is_a_dag_and_epochs_may_cycle():
    assert topology_rule("admission_transaction")["must_be_acyclic"] \
        is True
    assert topology_rule("research_epochs")["cycles_lawful"] is True
    assert topology_rule("nonsense")["reason"] == "E_UNKNOWN_SCOPE"


def test_deterministic():
    assert gi.canon(topology_rule("research_epochs")) == \
        gi.canon(topology_rule("research_epochs"))
