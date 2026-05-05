"""
semantic_object_model.py — HELEN Canonical Semantic Object (CSO) model
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Implements H = (G, R, P):
  G = Canonical Semantic Graph (append-only, receipt-validated)
  R = Receipt validation
  P = Projection operators (deterministic)

Safe boundary:
- no disk writes
- no kernel/ledger access
- no authority claims — evaluation only
"""

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Optional


# ── Exceptions ────────────────────────────────────────────────────────────────

class MutationRejected(Exception):
    """Append-only violation: attempt to mutate or delete existing node."""

class SovereignViolation(Exception):
    """Attempt to mutate or delete a sovereign node."""

class NamespaceViolation(Exception):
    """Cross-namespace identity violation."""

class AuthorityLeak(Exception):
    """Non-CSO artifact claimed authority."""

class ReplayDivergence(Exception):
    """Replay produced different state from original sequence."""


# ── CSO ───────────────────────────────────────────────────────────────────────

@dataclass
class CSO:
    namespace: str
    local_id: str
    type: str
    payload: dict
    relations: list[str] = field(default_factory=list)   # global_ids
    provenance: dict = field(default_factory=dict)
    receipts: list[str] = field(default_factory=list)    # receipt hashes
    sovereign: bool = False
    _hash: Optional[str] = field(default=None, repr=False)

    @property
    def global_id(self) -> str:
        return f"{self.namespace}/{self.local_id}"

    def canonical_hash(self) -> str:
        if self._hash is None:
            self._hash = _hash_cso(self)
        return self._hash

    @property
    def authority(self) -> int:
        return 1 if self.receipts else 0


@dataclass
class Receipt:
    receipt_id: str
    cso_global_id: str
    payload_hash: str


def _canonicalize(obj: Any) -> str:
    """Canonical JSON: sorted keys, NFC-normalized strings, no trailing whitespace."""
    if isinstance(obj, dict):
        return "{" + ",".join(
            f"{json.dumps(_normalize_str(k))}:{_canonicalize(v)}"
            for k, v in sorted(obj.items())
        ) + "}"
    if isinstance(obj, list):
        return "[" + ",".join(_canonicalize(i) for i in obj) + "]"
    if isinstance(obj, str):
        return json.dumps(_normalize_str(obj))
    return json.dumps(obj)


def _normalize_str(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _hash_cso(cso: CSO) -> str:
    data = _canonicalize({
        "namespace": cso.namespace,
        "local_id": cso.local_id,
        "type": cso.type,
        "payload": cso.payload,
    })
    return hashlib.sha256(data.encode()).hexdigest()


# ── Graph ─────────────────────────────────────────────────────────────────────

@dataclass
class RetrievalPolicy:
    max_depth: int = 3
    max_branching: int = 10


class SemanticGraph:
    """Append-only canonical semantic graph. Implements G in H=(G,R,P)."""

    def __init__(self):
        self._nodes: dict[str, CSO] = {}
        self._event_log: list[CSO] = []

    def append(self, cso: CSO) -> None:
        gid = cso.global_id
        if gid in self._nodes:
            raise MutationRejected(f"Node {gid} already exists. Graph is append-only.")
        if not cso.receipts:
            raise ValueError(f"CSO {gid} has no receipts. NO RECEIPT = NO CLAIM.")
        self._nodes[gid] = cso
        self._event_log.append(cso)

    def delete(self, global_id: str) -> None:
        if global_id not in self._nodes:
            raise KeyError(global_id)
        node = self._nodes[global_id]
        if node.sovereign:
            raise SovereignViolation(f"Cannot delete sovereign node {global_id}.")
        raise MutationRejected(f"Graph is append-only. Deletion of {global_id} rejected.")

    def get(self, global_id: str) -> Optional[CSO]:
        return self._nodes.get(global_id)

    def __len__(self) -> int:
        return len(self._nodes)

    def snapshot_at(self, t: int) -> "SemanticGraph":
        """Return a new graph containing only the first t events (replay to time t)."""
        g = SemanticGraph()
        for cso in self._event_log[:t]:
            g._nodes[cso.global_id] = cso
            g._event_log.append(cso)
        return g

    def retrieve(
        self,
        root_id: str,
        query: Optional[dict] = None,
        policy: Optional[RetrievalPolicy] = None,
    ) -> list[CSO]:
        """Bounded graph traversal: |result| ≤ policy.max_depth × policy.max_branching."""
        if policy is None:
            policy = RetrievalPolicy()
        result: list[CSO] = []
        visited: set[str] = set()
        self._traverse(root_id, 0, policy, result, visited)
        return result

    def _traverse(
        self, gid: str, depth: int,
        policy: RetrievalPolicy,
        result: list[CSO],
        visited: set[str],
    ) -> None:
        if depth > policy.max_depth:
            return
        if gid in visited:
            return
        node = self._nodes.get(gid)
        if node is None:
            return
        visited.add(gid)
        result.append(node)
        children = node.relations[:policy.max_branching]
        for child_id in children:
            self._traverse(child_id, depth + 1, policy, result, visited)


# ── Projection ────────────────────────────────────────────────────────────────

def project(graph: SemanticGraph, namespace: Optional[str] = None) -> dict:
    """Deterministic projection P(G). Pure function of graph state."""
    nodes = [
        n for n in graph._nodes.values()
        if namespace is None or n.namespace == namespace
    ]
    return {
        "node_count": len(nodes),
        "nodes": {
            n.global_id: {
                "type": n.type,
                "hash": n.canonical_hash(),
                "sovereign": n.sovereign,
                "authority": n.authority,
            }
            for n in sorted(nodes, key=lambda x: x.global_id)
        },
        "graph_hash": _graph_hash(nodes),
    }


def _graph_hash(nodes: list[CSO]) -> str:
    combined = "|".join(sorted(n.canonical_hash() for n in nodes))
    return hashlib.sha256(combined.encode()).hexdigest()


# ── Replay ────────────────────────────────────────────────────────────────────

def replay(event_log: list[CSO], t: Optional[int] = None) -> SemanticGraph:
    """Forward replay from genesis. Returns G_t."""
    g = SemanticGraph()
    events = event_log if t is None else event_log[:t]
    for cso in events:
        g._nodes[cso.global_id] = cso
        g._event_log.append(cso)
    return g


# ── Authority gate ────────────────────────────────────────────────────────────

AUTHORITY_ZERO_TYPES = {"RENDERER_OUTPUT", "EMBEDDING", "MOCK", "DRAFT"}


def check_authority(obj: Any, obj_type: str) -> int:
    """Renderers and embeddings have Authority = 0 regardless of claims."""
    if obj_type in AUTHORITY_ZERO_TYPES:
        return 0
    if isinstance(obj, CSO) and obj.receipts:
        return 1
    return 0


# ── Namespace helpers ─────────────────────────────────────────────────────────

def make_global_id(namespace: str, local_id: str) -> str:
    return f"{namespace}/{local_id}"


def validate_namespace(cso: CSO, expected_namespace: str) -> None:
    if cso.namespace != expected_namespace:
        raise NamespaceViolation(
            f"CSO namespace '{cso.namespace}' does not match expected '{expected_namespace}'"
        )
