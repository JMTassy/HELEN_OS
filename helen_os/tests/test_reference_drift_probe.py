"""
Tests for REFERENCE_DRIFT_WITNESS_V1 (tools/reference_drift_probe.py).

Acceptance criteria (CTO Guide V1.1 Phase 3):
  - D(x) = PageRank(x) * (1 - P(x))
  - top drift queue is deterministic
  - no reducer mutation (read-only probe)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

from tools.reference_drift_probe import (
    Artifact, ReferenceGraph,
    _build_graph, _drift, _pagerank, _replay_provenance, probe,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _art(node_id: str, provenance: float = 0.0, artifact_type: str = "tool") -> Artifact:
    return Artifact(
        node_id=node_id,
        artifact_type=artifact_type,
        file_path=f"/nonexistent/{node_id}",
        provenance=provenance,
    )


def _graph_from(nodes: Dict[str, Artifact], edges=()) -> ReferenceGraph:
    g = ReferenceGraph(nodes=dict(nodes))
    for src, tgt in edges:
        g.adjacency.setdefault(src, set()).add(tgt)
        g.adjacency.setdefault(tgt, set())
        g.edges.append((src, tgt))
    return g


def _write_ledger(path: str, entries: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _promotion_event(skill_id: str, seq: int = 1, sovereign: bool = True) -> dict:
    return {
        "type": "SKILL_PROMOTION_DECISION_V1",
        "seq": seq,
        "payload": {
            "schema_name": "SKILL_PROMOTION_DECISION_V1",
            "skill_id": skill_id,
            "sovereign_promotion": sovereign,
            "decision_type": "ADMITTED",
        },
    }


# ── Test 1: D(x) = rank(x) * (1 - P(x)) exactly ─────────────────────────────

def test_drift_formula_exact():
    """D must equal rank * (1 - P) for every artifact — no approximation."""
    arts = {
        "A": _art("A", provenance=0.0),
        "B": _art("B", provenance=1.0),
        "C": _art("C", provenance=0.0),
    }
    g = _graph_from(arts)
    ranks = _pagerank(g)
    ranked = _drift(arts, ranks)

    for a in ranked:
        expected = a.rank * (1.0 - a.provenance)
        assert abs(a.drift_score - expected) < 1e-12, (
            f"{a.node_id}: D={a.drift_score} ≠ rank={a.rank} * (1-P={a.provenance})"
        )


# ── Test 2: zero provenance → D equals rank ───────────────────────────────────

def test_zero_provenance_uses_full_rank():
    """P=0 → D = rank (no discount)."""
    arts = {"X": _art("X", provenance=0.0)}
    g = _graph_from(arts)
    ranks = _pagerank(g)
    _drift(arts, ranks)

    x = arts["X"]
    assert abs(x.drift_score - x.rank) < 1e-12


# ── Test 3: full provenance → D is zero ──────────────────────────────────────

def test_full_provenance_zeroes_drift():
    """P=1 → D = 0 regardless of rank."""
    arts = {"Y": _art("Y", provenance=1.0)}
    g = _graph_from(arts)
    ranks = _pagerank(g)
    _drift(arts, ranks)

    assert arts["Y"].drift_score == 0.0
    assert arts["Y"].rank > 0        # rank must be non-zero (meaningful test)


# ── Test 4: PageRank determinism ──────────────────────────────────────────────

def test_pagerank_is_deterministic():
    """Same graph → identical rank vector on every call."""
    arts = {
        "tools/a.py": _art("tools/a.py"),
        "tools/b.py": _art("tools/b.py"),
        "tools/c.py": _art("tools/c.py"),
    }
    g = _graph_from(arts, edges=[("tools/a.py", "tools/b.py"), ("tools/c.py", "tools/b.py")])
    ranks1 = _pagerank(g)
    ranks2 = _pagerank(g)
    for nid in arts:
        assert abs(ranks1[nid] - ranks2[nid]) < 1e-14


# ── Test 5: star graph — hub has highest rank ─────────────────────────────────

def test_central_hub_has_highest_rank():
    """Hub pointed to by B, C, D must have highest PageRank (all P=0)."""
    arts = {
        "hub": _art("hub"),
        "B":   _art("B"),
        "C":   _art("C"),
        "D":   _art("D"),
    }
    g = _graph_from(arts, edges=[("B", "hub"), ("C", "hub"), ("D", "hub")])
    ranks = _pagerank(g)
    _drift(arts, ranks)

    rank_of = {a.node_id: a.rank for a in arts.values()}
    assert rank_of["hub"] > rank_of["B"]
    assert rank_of["hub"] > rank_of["C"]
    assert rank_of["hub"] > rank_of["D"]


# ── Test 6: receipted central node — D = 0 despite high rank ─────────────────

def test_receipted_central_has_zero_drift():
    """Hub with P=1 must have D=0 even though rank is high."""
    arts = {
        "hub": _art("hub", provenance=1.0),
        "B":   _art("B",   provenance=0.0),
        "C":   _art("C",   provenance=0.0),
    }
    g = _graph_from(arts, edges=[("B", "hub"), ("C", "hub")])
    ranks = _pagerank(g)
    _drift(arts, ranks)

    hub = arts["hub"]
    assert hub.rank > arts["B"].rank, "hub must be central (test precondition)"
    assert hub.drift_score == 0.0


# ── Test 7: provenance extracted from sovereign ledger promotion ──────────────

def test_provenance_from_sovereign_promotion(tmp_path):
    ledger = str(tmp_path / "ledger.ndjson")
    _write_ledger(ledger, [_promotion_event("REFERENCE_DRIFT_WITNESS_V1")])
    receipted = _replay_provenance(ledger)
    assert "oracle_town/skills/reference_drift_witness/skill.py" in receipted


# ── Test 8: non-sovereign promotion not in receipted set ──────────────────────

def test_non_sovereign_promotion_excluded(tmp_path):
    ledger = str(tmp_path / "ledger.ndjson")
    _write_ledger(ledger, [_promotion_event("GHOST_SKILL_V1", sovereign=False)])
    receipted = _replay_provenance(ledger)
    assert not receipted


# ── Test 9: empty ledger → empty receipted set ────────────────────────────────

def test_empty_ledger_empty_provenance(tmp_path):
    ledger = str(tmp_path / "empty.ndjson")
    open(ledger, "w").close()
    assert _replay_provenance(ledger) == set()


# ── Test 10: probe() with empty _artifacts → empty top_drift ─────────────────

def test_probe_empty_artifacts_empty_output(tmp_path):
    ledger = str(tmp_path / "empty.ndjson")
    open(ledger, "w").close()
    result = probe(ledger_path=ledger, _artifacts={})
    assert result["schema_name"] == "REFERENCE_DRIFT_WITNESS_V1"
    assert result["top_drift"] == []
    assert result["graph_stats"]["node_count"] == 0
    assert result["graph_stats"]["edge_count"] == 0
    assert result["deterministic"] is True


# ── Test 11: probe() — top_n parameter respected ──────────────────────────────

def test_probe_top_n_respected(tmp_path):
    ledger = str(tmp_path / "empty.ndjson")
    open(ledger, "w").close()
    arts = {f"tools/t{i}.py": _art(f"tools/t{i}.py") for i in range(10)}
    result = probe(ledger_path=ledger, _artifacts=arts, top_n=3)
    assert len(result["top_drift"]) <= 3
    # Each entry must have positive D and P < 1
    for entry in result["top_drift"]:
        assert entry["drift_score"] > 0
        assert entry["provenance"] < 1.0


# ── Test 12: live ledger integration ─────────────────────────────────────────

def test_live_probe_runs_without_error():
    """
    The actual town/ledger_v1.ndjson must produce a valid REFERENCE_DRIFT_WITNESS_V1
    dict with correct structure and no exceptions.
    """
    live_ledger = str(Path(__file__).parents[2] / "town" / "ledger_v1.ndjson")
    if not os.path.exists(live_ledger):
        pytest.skip("live ledger not present")

    result = probe(live_ledger)

    assert result["schema_name"] == "REFERENCE_DRIFT_WITNESS_V1"
    assert result["schema_version"] == "1.0.0"
    assert isinstance(result["top_drift"], list)
    assert result["graph_stats"]["node_count"] > 0
    assert result["deterministic"] is True

    # Every drift entry must satisfy the invariant
    for entry in result["top_drift"]:
        assert entry["drift_score"] > 0, "top_drift entries must have D > 0"
        assert entry["provenance"] < 1.0, "receipted artifacts must not appear in top_drift"
