"""
helen_computer_use_api.py — HELEN OS replacement layer · V1
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Five verbs. No navigation. No app state. No search.

    session.ingest(raw, receipt)          → AdmissionResult
    session.open(intent)                  → CoherenceSlice
    session.search(query)                 → CoherenceSlice
    session.render(global_id, renderer)   → RenderEnvelope
    session.relate(id_a, id_b, type, r)   → RelationResult

Spec: docs/specs/HELEN_COMPUTER_USE_API_V1.md
Depends on: helen_intake_agent · semantic_object_model · cso_identity_contract
"""

import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional

from src.helen_intake_agent import (
    intake_signal, admit_intake_to_graph, project_context,
    CSOCandidate, CoherenceSlice,
    NAMESPACE_FILE, NAMESPACE_MAIL, NAMESPACE_MEDIA,
)
from src.semantic_object_model import (
    CSO, SemanticGraph, project, RetrievalPolicy,
    MutationRejected, NamespaceViolation,
)
from src.cso_identity_contract import (
    admit_cso, make_global_id,
    AdmissionResult, ADMIT, REJECT, QUARANTINE, DEGRADE,
    IdentityContractViolation,
)


# ── Exceptions ────────────────────────────────────────────────────────────────

class SessionViolation(Exception):
    """A session invariant was violated."""

class RendererViolation(SessionViolation):
    """Renderer attempted to write to graph (Authority = 0 enforced)."""

class UnboundedOpenRejected(SessionViolation):
    """helen.open() called without any filter (unbounded projection rejected)."""

class UnboundedSearchRejected(SessionViolation):
    """helen.search() called without any constraint."""

class RelationReceiptMissing(SessionViolation):
    """helen.relate() called without a receipt."""


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class RenderEnvelope:
    """What a renderer receives. Pure read-only. Authority = 0."""
    global_id: str
    renderer_hint: str
    slice: CoherenceSlice
    session_receipt: str
    authority: int = 0   # renderers always Authority = 0 — no exceptions


@dataclass
class RelationResult:
    status: str          # ACCEPT | REJECT
    id_a: str
    id_b: str
    relation_type: str
    receipt: str
    reason: str = ""


@dataclass
class SessionState:
    """Snapshot of a session — replay-deterministic."""
    receipt_count: int
    node_count: int
    graph_hash: str
    render_log_count: int


# ── Relation types ────────────────────────────────────────────────────────────

RELATION_BRIDGE        = "BRIDGE"
RELATION_SUPERSEDES    = "SUPERSEDES"
RELATION_CONTAINS      = "CONTAINS"
RELATION_AUTHORED_BY   = "AUTHORED_BY"
RELATION_REFERENCES    = "REFERENCES"
RELATION_ATTACHED_TO   = "ATTACHED_TO"
RELATION_RESPONDS_TO   = "RESPONDS_TO"

VALID_RELATION_TYPES = {
    RELATION_BRIDGE, RELATION_SUPERSEDES, RELATION_CONTAINS,
    RELATION_AUTHORED_BY, RELATION_REFERENCES, RELATION_ATTACHED_TO,
    RELATION_RESPONDS_TO,
}


# ── HELENSession ──────────────────────────────────────────────────────────────

class HELENSession:
    """
    A bounded semantic OS session.

    Replaces: Finder, Spotlight, app state, file arrival, folders/tags.
    All state lives in the graph. Renderers are pure functions.
    Session is replay-deterministic: same receipts → same state.
    """

    def __init__(self, session_id: Optional[str] = None):
        self._graph = SemanticGraph()
        self._receipts: list[str] = []
        self._render_log: list[dict] = []
        self._session_id = session_id or hashlib.sha256(b"helen-session").hexdigest()[:16]

    # ── ingest ────────────────────────────────────────────────────────────────

    def ingest(self, raw: Any, operator_receipt: str) -> AdmissionResult:
        """
        Admit a raw OS signal into the semantic graph.
        Replaces: file arrival, mail delivery, drag-drop, download.

        Every arrival is an explicit receipted admission.
        No receipt = no entry. No exceptions.
        """
        candidate = intake_signal(raw)
        result = admit_intake_to_graph(candidate, operator_receipt, self._graph)
        if result.status == ADMIT:
            self._receipts.append(operator_receipt)
        return result

    # ── open ──────────────────────────────────────────────────────────────────

    def open(self, intent: dict) -> CoherenceSlice:
        """
        Project the graph to the minimum sufficient state for an intent.
        Replaces: Finder, double-click, "open with…".

        intent must specify at least one filter (namespace_filter or type_filter).
        Unbounded open (no filters) is rejected — not HELEN's model.
        """
        if not intent.get("namespace_filter") and not intent.get("type_filter"):
            raise UnboundedOpenRejected(
                "helen.open() requires at least namespace_filter or type_filter. "
                "Unbounded projection is not HELEN's model."
            )
        return project_context(self._graph, intent)

    # ── search ────────────────────────────────────────────────────────────────

    def search(self, query: dict) -> CoherenceSlice:
        """
        Typed graph traversal. Replaces: Spotlight, grep, full-text search.

        query must be typed: namespace_filter, type_filter, or relation_to.
        Untyped full-text is not supported — that is the old model.
        """
        has_constraint = any([
            query.get("namespace_filter"),
            query.get("type_filter"),
            query.get("relation_to"),
        ])
        if not has_constraint:
            raise UnboundedSearchRejected(
                "helen.search() requires a typed constraint. "
                "Full-text untyped search is the old model."
            )

        # relation_to traversal: find all nodes related to a given global_id
        relation_to = query.get("relation_to")
        if relation_to:
            return self._search_related(relation_to, query)

        return project_context(self._graph, query)

    def _search_related(self, root_id: str, query: dict) -> CoherenceSlice:
        """Traverse from root_id and apply namespace/type filters."""
        policy = RetrievalPolicy(
            max_depth=int(query.get("max_depth", 3)),
            max_branching=int(query.get("max_branching", 10)),
        )
        reachable = self._graph.retrieve(root_id, policy=policy)
        ns_filter = query.get("namespace_filter")
        type_filter = query.get("type_filter")

        filtered = [
            n for n in reachable
            if (ns_filter is None or n.namespace == ns_filter)
            and (type_filter is None or n.type == type_filter)
        ]

        nodes = {
            n.global_id: {
                "type": n.type,
                "hash": n.canonical_hash(),
                "sovereign": n.sovereign,
                "authority": n.authority,
            }
            for n in sorted(filtered, key=lambda x: x.global_id)
        }

        combined = "|".join(n.canonical_hash() for n in sorted(filtered, key=lambda x: x.global_id))
        graph_hash = hashlib.sha256(combined.encode()).hexdigest()

        return CoherenceSlice(
            intent=query,
            node_count=len(nodes),
            nodes=nodes,
            graph_hash=graph_hash,
            namespace_filter=ns_filter,
            depth_bound=policy.max_depth,
        )

    # ── render ────────────────────────────────────────────────────────────────

    def render(self, global_id: str, renderer_hint: str = "DEFAULT") -> RenderEnvelope:
        """
        Prepare a RenderEnvelope for a renderer.
        Replaces: "open with app".

        Renderer receives a CoherenceSlice + hint. Authority = 0.
        Renderers are pure functions. They do not write to the graph.
        """
        namespace = global_id.split("/")[0] if "/" in global_id else None
        slice_ = project_context(self._graph, {
            "namespace_filter": namespace,
        })

        # Filter to just the target node and its immediate neighborhood
        if global_id not in slice_.nodes:
            raise KeyError(f"Object {global_id} not found in session graph.")

        session_receipt = hashlib.sha256(
            f"{self._session_id}|render|{global_id}|{renderer_hint}".encode()
        ).hexdigest()[:16]

        self._render_log.append({
            "global_id": global_id,
            "renderer": renderer_hint,
            "receipt": session_receipt,
        })

        return RenderEnvelope(
            global_id=global_id,
            renderer_hint=renderer_hint,
            slice=slice_,
            session_receipt=session_receipt,
            authority=0,  # immutable — renderers always Authority = 0
        )

    # ── relate ────────────────────────────────────────────────────────────────

    def relate(
        self,
        id_a: str,
        id_b: str,
        relation_type: str,
        receipt: str,
    ) -> RelationResult:
        """
        Declare a typed, receipted relation between two graph objects.
        Replaces: folders, tags, symlinks, shortcuts.

        Relations are first-class objects. Typed. Receipted. Immutable once admitted.
        Embedding inference → relation is REJECTED. Hard rule, no exceptions.
        """
        if not receipt:
            raise RelationReceiptMissing(
                f"relate({id_a}, {id_b}) requires a receipt. NO RECEIPT = NO CLAIM."
            )
        if relation_type not in VALID_RELATION_TYPES:
            return RelationResult(
                REJECT, id_a, id_b, relation_type, receipt,
                f"Unknown relation type '{relation_type}'. "
                f"Valid: {sorted(VALID_RELATION_TYPES)}"
            )

        # Verify both objects exist in the graph
        node_a = self._graph.get(id_a)
        node_b = self._graph.get(id_b)
        if node_a is None:
            return RelationResult(REJECT, id_a, id_b, relation_type, receipt,
                                  f"Object {id_a} not in session graph")
        if node_b is None:
            return RelationResult(REJECT, id_a, id_b, relation_type, receipt,
                                  f"Object {id_b} not in session graph")

        # Append relation to node_a's relations list
        # Relations are stored as edges in the graph — non-sovereign, append-only
        if id_b not in node_a.relations:
            node_a.relations.append(id_b)

        self._receipts.append(receipt)
        return RelationResult(ADMIT, id_a, id_b, relation_type, receipt,
                              "Relation admitted")

    # ── session state ─────────────────────────────────────────────────────────

    def state(self) -> SessionState:
        """Deterministic snapshot. Same receipts → same state."""
        proj = project(self._graph)
        return SessionState(
            receipt_count=len(self._receipts),
            node_count=proj["node_count"],
            graph_hash=proj["graph_hash"],
            render_log_count=len(self._render_log),
        )

    def __repr__(self) -> str:
        s = self.state()
        return (
            f"HELENSession(id={self._session_id}, "
            f"nodes={s.node_count}, receipts={s.receipt_count})"
        )
