"""AntV G_V projection — Garden lineage → AntV Infographic DSL.

🔵 OBSERVED · NON_SOVEREIGN sandbox · authority=0 · PROJECTION ONLY.

Structural compiler: typed JSON → schema validation → projection mapper → DSL.
NO LLM in the loop — factual node/edge content comes mechanically from the
source object. The five executable conditions:
  P1 nodes(out) ⊆ nodes(in)      P2 edges(out) ⊆ edges(in)
  P3 A=0 ⇒ NO_CLAIM watermark    P4 no mutation capability (no kernel imports)
  P5 deterministic for fixed (x, Θ)

This module imports NOTHING from kernel/capability/ledger — it cannot mutate
governed state even in principle. Beauty does not bootstrap semantics or authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field

ALLOWED_KINDS = frozenset({"SEED", "CANDIDATE", "FAILURE", "NUTRIENT"})
ALLOWED_RELATIONS = frozenset({"COMPOST_TO_SEED", "SEED_TO_VARIANT", "VARIANT_TO_VARIANT"})
GOVERNED_VOCAB = frozenset({"ADMITTED", "SEALED", "EXECUTED", "REPLAYED"})  # forbidden here
WATERMARK = "STATUS: NO_CLAIM · AUTHORITY: 0 · PROJECTION ONLY"


@dataclass(frozen=True)
class LineageNode:
    node_id: str
    kind: str
    label: str
    status: str = "NO_CLAIM"

    @property
    def authority(self) -> int:
        return 0  # structural constant


@dataclass(frozen=True)
class LineageEdge:
    source: str
    target: str
    relation: str


@dataclass(frozen=True)
class GardenLineageProjection:
    graph_id: str
    nodes: tuple = ()
    edges: tuple = ()

    @property
    def authority(self) -> int:
        return 0


class ProjectionError(ValueError):
    pass


def validate(x: GardenLineageProjection) -> None:
    ids = set()
    for n in x.nodes:
        if n.kind not in ALLOWED_KINDS:
            raise ProjectionError(f"unknown node kind: {n.kind!r}")
        if n.status.upper() in GOVERNED_VOCAB:
            raise ProjectionError(f"governed vocabulary forbidden in G_V: {n.status!r}")
        label_words = {w.strip(".,;:!").upper() for w in n.label.split()}
        if label_words & GOVERNED_VOCAB:
            raise ProjectionError(
                f"governed vocabulary forbidden in G_V label: {n.label!r}"
            )
        if n.node_id in ids:
            raise ProjectionError(f"duplicate node id: {n.node_id!r}")
        ids.add(n.node_id)
    for e in x.edges:
        if e.relation not in ALLOWED_RELATIONS:
            raise ProjectionError(f"unknown relation: {e.relation!r}")
        if e.source not in ids or e.target not in ids:
            raise ProjectionError(f"dangling edge: {e.source!r} -> {e.target!r}")


def render_antv_gv(x: GardenLineageProjection) -> str:
    """Deterministic projection. Every emitted label/desc traces to a source field."""
    validate(x)
    lines = [
        "infographic list-row-simple-horizontal-arrow",
        f"title HELEN Garden Lineage · {x.graph_id}",
        f"desc {WATERMARK}",
        "data",
        "  lists",
    ]
    for n in x.nodes:  # input order — no reordering, no summarization
        lines.append(f"    - label {n.kind} {n.node_id}")
        lines.append(f"      desc {n.label}")
    if x.edges:
        lines.append("  edges")
        for e in x.edges:
            lines.append(f"    - {e.source} -{e.relation}-> {e.target}")
    return "\n".join(lines) + "\n"
