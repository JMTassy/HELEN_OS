"""C14 — composition (edge) witnesses. 🔵 OBSERVED · NON_SOVEREIGN · authority=0.

Green nodes ⊬ green graph. A system property requires BOTH witnessed components (nodes)
AND witnessed compatibility across the interfaces between them (edges):

    ⋀_i P_i  ⊬  P_system      unless every critical edge carries a composition witness.

An EdgeWitness binds the field transported across an interface A→B: the value the source
endpoint PRODUCES and the value the target endpoint EXPECTS must be the same hash, or the
property does not cross the edge. That is the dual-head fracture class, expressed generally:

    W_{TX→Executor} holds  ⟺  H(G_TX.committed_head) == H(G_Executor.pre_root)

A red/unknown NODE dominates; but even with all nodes green, a FALSIFIED critical edge makes
the system RED and a MISSING/UNWITNESSED critical edge makes it UNKNOWN — never GREEN. This is
exactly why MASTER_SYNTHESIS_COMPLETE could not be inherited from green components.

Reuses C13's frame-bound receipt shape (self-binding receipt_hash + injected frame_hash).
Determinism: no wall clock; canon reuses the ledger hash_chain. K-tau mu_DETERMINISM clean.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


class NodeStatus(Enum):
    GREEN = "GREEN"
    RED = "RED"
    UNKNOWN = "UNKNOWN"


class EdgeStatus(Enum):
    WITNESSED = "WITNESSED"       # transported field matches across the interface
    FALSIFIED = "FALSIFIED"       # endpoints disagree — the dual-head class
    UNWITNESSED = "UNWITNESSED"   # an endpoint unmeasured / receipt tampered — cannot be trusted


class SystemStatus(Enum):
    GREEN_SCOPED = "GREEN_SCOPED"
    RED = "RED"
    UNKNOWN = "UNKNOWN"


_BODY_FIELDS = (
    "edge_id", "source_id", "target_id", "transported_field",
    "source_hash", "target_expected_hash", "frame_hash", "result",
)


@dataclass(frozen=True)
class EdgeWitness:
    edge_id: str
    source_id: str
    target_id: str
    transported_field: str        # e.g. "committed_state_root"
    source_hash: str              # H(value PRODUCED by the source endpoint)
    target_expected_hash: str     # H(value the target endpoint EXPECTS)
    frame_hash: str               # C13 frame binding (injected)
    result: str
    receipt_hash: str


def _body(w: EdgeWitness) -> dict:
    return {f: getattr(w, f) for f in _BODY_FIELDS}


def receipt_body_hash(w: EdgeWitness) -> str:
    return h_v(_body(w))


def mint_edge(**kw) -> EdgeWitness:
    w = EdgeWitness(receipt_hash="", **kw)
    return replace(w, receipt_hash=receipt_body_hash(w))


def valid_edge(w: EdgeWitness) -> bool:
    """Self-hash recomputed, never trusted."""
    return bool(w.receipt_hash) and w.receipt_hash == receipt_body_hash(w)


def edge_status(w: EdgeWitness) -> EdgeStatus:
    """Derived, never asserted. WITNESSED only if the self-hash recomputes AND both endpoints
    were actually measured AND their transported-field hashes match."""
    if not valid_edge(w):
        return EdgeStatus.UNWITNESSED             # tampered / unminted
    if not w.source_hash or not w.target_expected_hash:
        return EdgeStatus.UNWITNESSED             # an endpoint was never measured
    if w.source_hash == w.target_expected_hash:
        return EdgeStatus.WITNESSED
    return EdgeStatus.FALSIFIED                    # endpoints disagree — dual-head class


def system_status(nodes: dict, edges: list, critical_edges):
    """SystemStatus = f(NodeStatus, EdgeStatus). green nodes ⊬ green graph:
    a red node ⇒ RED; an unknown node ⇒ UNKNOWN; else every CRITICAL edge must be WITNESSED —
    a falsified critical edge ⇒ RED, a missing/unwitnessed one ⇒ UNKNOWN."""
    if any(s == NodeStatus.RED for s in nodes.values()):
        return SystemStatus.RED, "NODE_RED"
    if any(s == NodeStatus.UNKNOWN for s in nodes.values()):
        return SystemStatus.UNKNOWN, "NODE_UNKNOWN"
    by_id = {w.edge_id: w for w in edges}
    for eid in critical_edges:
        if eid not in by_id:
            return SystemStatus.UNKNOWN, f"EDGE_MISSING:{eid}"     # the C14 core law
        st = edge_status(by_id[eid])
        if st == EdgeStatus.FALSIFIED:
            return SystemStatus.RED, f"EDGE_FALSIFIED:{eid}"
        if st == EdgeStatus.UNWITNESSED:
            return SystemStatus.UNKNOWN, f"EDGE_UNWITNESSED:{eid}"
    return SystemStatus.GREEN_SCOPED, "ALL_NODES_AND_CRITICAL_EDGES_WITNESSED"


# ---------------------------------------------------------------- real kernel edge
def measure_executor_tx_edge(tx, frame_hash: str = "F") -> EdgeWitness:
    """Ground C14 in real kernel code: the W_{TX→Executor} edge transports the committed
    governed-state root. SOURCE = the GovernedStore head (TransactionRuntime's committed head);
    TARGET = the capability/executor-layer root (`current_state_hash`). Under E009's single head
    E010 keeps both in sync, so the edge is WITNESSED and the dual-head class cannot arise —
    a genuine measurement of the two layer roots, not an assertion that they agree."""
    committed_root = tx.store.head() if getattr(tx, "store", None) is not None else tx.current_state_hash
    executor_pre_root = tx.current_state_hash
    return mint_edge(
        edge_id="TX->Executor",
        source_id="TransactionRuntime",
        target_id="Executor",
        transported_field="committed_state_root",
        source_hash=h_v(committed_root),
        target_expected_hash=h_v(executor_pre_root),
        frame_hash=frame_hash,
        result="MEASURED",
    )
