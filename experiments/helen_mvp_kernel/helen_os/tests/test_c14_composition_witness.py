"""C14 — composition (edge) witness falsifiers. 🔵 OBSERVED.

green nodes ⊬ green graph. The marquee edge (Executor ↔ TransactionRuntime) is measured from
REAL kernel objects, so the dual-head fracture class is detectable, not just theorized.

C14-01 matching endpoints          → WITNESSED
C14-02 mismatched endpoints        → FALSIFIED (dual-head class)
C14-03 unmeasured endpoint         → UNWITNESSED
C14-04 tampered receipt            → UNWITNESSED
C14-05 green nodes, missing edge   → system UNKNOWN (NOT green — the core law)
C14-06 green nodes, falsified edge → system RED
C14-07 all green + edge witnessed  → GREEN_SCOPED
C14-08 red node dominates          → RED
C14-09 unknown node                → UNKNOWN
C14-10 real TX→Executor edge       → WITNESSED (one GovernedStore head)
C14-11 real edge, simulated split  → FALSIFIED
"""
from dataclasses import replace

from helen_os.compose.edge import (
    EdgeStatus, NodeStatus, SystemStatus, edge_status, h_v, measure_executor_tx_edge,
    mint_edge, system_status, valid_edge,
)
from helen_os.kernel.governed_store import GovernedStore
from helen_os.kernel.transaction import TransactionRuntime

G0 = h_v({"head": "A"})
G1 = h_v({"head": "B"})


def _edge(eid="e", sh="hA", th="hA"):
    return mint_edge(edge_id=eid, source_id="SRC", target_id="TGT",
                     transported_field="root", source_hash=sh, target_expected_hash=th,
                     frame_hash="F", result="MEASURED")


NODES_GREEN = {"A": NodeStatus.GREEN, "B": NodeStatus.GREEN}


# ---- edge machinery
def test_c14_01_matching_endpoints_witnessed():
    assert edge_status(_edge(sh="h", th="h")) == EdgeStatus.WITNESSED


def test_c14_02_mismatched_endpoints_falsified():
    assert edge_status(_edge(sh="hX", th="hY")) == EdgeStatus.FALSIFIED   # dual-head class


def test_c14_03_unmeasured_endpoint_unwitnessed():
    assert edge_status(_edge(sh="", th="h")) == EdgeStatus.UNWITNESSED


def test_c14_04_tampered_edge_unwitnessed():
    w = _edge(sh="h", th="h")
    tampered = replace(w, source_hash="hZ")   # mutate after mint, keep stale receipt_hash
    assert not valid_edge(tampered)
    assert edge_status(tampered) == EdgeStatus.UNWITNESSED


# ---- system composition: green nodes ⊬ green graph
def test_c14_05_green_nodes_missing_edge_not_green():
    st, reason = system_status(NODES_GREEN, edges=[], critical_edges={"A->B"})
    assert st == SystemStatus.UNKNOWN and reason == "EDGE_MISSING:A->B"


def test_c14_06_green_nodes_falsified_edge_red():
    e = _edge(eid="A->B", sh="hX", th="hY")
    st, reason = system_status(NODES_GREEN, [e], {"A->B"})
    assert st == SystemStatus.RED and reason == "EDGE_FALSIFIED:A->B"


def test_c14_07_all_green_and_edge_witnessed_green_scoped():
    e = _edge(eid="A->B", sh="h", th="h")
    st, _ = system_status(NODES_GREEN, [e], {"A->B"})
    assert st == SystemStatus.GREEN_SCOPED


def test_c14_08_red_node_dominates():
    e = _edge(eid="A->B", sh="h", th="h")
    st, reason = system_status({"A": NodeStatus.GREEN, "B": NodeStatus.RED}, [e], {"A->B"})
    assert st == SystemStatus.RED and reason == "NODE_RED"


def test_c14_09_unknown_node_yields_unknown():
    st, reason = system_status({"A": NodeStatus.GREEN, "B": NodeStatus.UNKNOWN}, [], set())
    assert st == SystemStatus.UNKNOWN and reason == "NODE_UNKNOWN"


# ---- REAL kernel edge: Executor ↔ TransactionRuntime shares one committed head (E009/E010)
def _rig():
    store = GovernedStore(G0)
    return store, TransactionRuntime(current_state_hash=G0, store=store)


def test_c14_10_real_executor_tx_edge_is_witnessed():
    store, tx = _rig()
    tx.prepare("t", h_v({"e": 1})); tx.execute("t", lambda: G1); tx.evidence("t"); tx.commit("t")
    assert store.head() == G1
    w = measure_executor_tx_edge(tx)
    assert edge_status(w) == EdgeStatus.WITNESSED     # both layers read the one head → coherent


def test_c14_11_real_edge_falsified_under_simulated_dual_head():
    store, tx = _rig()
    tx.prepare("t", h_v({"e": 1})); tx.execute("t", lambda: G1); tx.evidence("t"); tx.commit("t")
    tx.current_state_hash = G0     # simulate a dual head: executor-layer root left stale at G0
    w = measure_executor_tx_edge(tx)
    assert edge_status(w) == EdgeStatus.FALSIFIED     # C14 detects the exact fracture class
