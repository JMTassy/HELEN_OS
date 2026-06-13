#!/usr/bin/env python3
"""
REFERENCE_DRIFT_WITNESS_V1

Measures reference centrality vs provenance for HELEN artifacts.

    D(x) = C_R(x) * (1 - P(x))

    C_R(x) = PageRank centrality in artifact reference graph G_R
    P(x)   = 1.0 if x has a sovereign ledger receipt, 0.0 otherwise
    D(x)   = drift score: high-centrality, unreceipted artifacts

Output: deterministic ranked drift queue (top-N by D). Read-only.

Usage:
    python3 tools/reference_drift_probe.py
    python3 tools/reference_drift_probe.py --ledger PATH
    python3 tools/reference_drift_probe.py --json
    python3 tools/reference_drift_probe.py --top N
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

_REPO_ROOT = Path(__file__).parent.parent
LEDGER_DEFAULT = str(_REPO_ROOT / "town" / "ledger_v1.ndjson")

_ARTIFACT_ROOTS = [
    "oracle_town/skills",
    "tools",
    "helen_os/governance",
    "helen_os/schemas",
    "src",
]

_PAGERANK_DAMPING = 0.85
_PAGERANK_ITERS   = 50
_TOP_N_DEFAULT    = 20
_SKIP_DIRS        = {"__pycache__", ".venv", ".venv-gates"}


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class Artifact:
    node_id:       str
    artifact_type: str
    file_path:     str
    provenance:    float = 0.0
    rank:          float = 0.0
    drift_score:   float = 0.0


@dataclass
class ReferenceGraph:
    nodes:     Dict[str, Artifact]      = field(default_factory=dict)
    edges:     List[Tuple[str, str]]    = field(default_factory=list)
    adjacency: Dict[str, Set[str]]      = field(default_factory=dict)


# ── Artifact discovery ─────────────────────────────────────────────────────────

def _normalize_id(path: Path) -> str:
    try:
        return str(path.relative_to(_REPO_ROOT))
    except ValueError:
        return str(path)


def _classify(rel_path: str) -> str:
    if rel_path.startswith("oracle_town/skills"):   return "skill"
    if rel_path.startswith("tools/"):               return "tool"
    if rel_path.startswith("helen_os/schemas"):     return "schema"
    if rel_path.startswith("helen_os/governance"):  return "governance"
    if rel_path.startswith("src/"):                 return "src"
    return "other"


def _discover_artifacts() -> Dict[str, Artifact]:
    arts: Dict[str, Artifact] = {}
    for root_rel in _ARTIFACT_ROOTS:
        root_abs = _REPO_ROOT / root_rel
        if not root_abs.exists():
            continue
        for ext in ("*.py", "*.json"):
            for fp in sorted(root_abs.rglob(ext)):          # sorted → deterministic
                if any(s in fp.parts for s in _SKIP_DIRS):
                    continue
                rel = _normalize_id(fp)
                if rel not in arts:
                    arts[rel] = Artifact(
                        node_id=rel,
                        artifact_type=_classify(rel),
                        file_path=str(fp),
                    )
    return arts


# ── Reference extraction ───────────────────────────────────────────────────────

def _python_imports(file_path: str) -> Set[str]:
    refs: Set[str] = set()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = re.match(r"\s*(?:from|import)\s+([\w.]+)", line)
                if m:
                    refs.add(m.group(1))
    except OSError:
        pass
    return refs


def _json_refs(file_path: str) -> Set[str]:
    refs: Set[str] = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def walk(obj: Any) -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ("schema_name", "skill_id", "$ref") and isinstance(v, str):
                        refs.add(v)
                    else:
                        walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)
    except Exception:
        pass
    return refs


def _build_graph(artifacts: Dict[str, Artifact]) -> ReferenceGraph:
    g = ReferenceGraph(nodes=dict(artifacts))
    known = set(artifacts.keys())
    seen: Set[Tuple[str, str]] = set()

    # Stem lookup for JSON reference resolution
    stem_map: Dict[str, str] = {}
    for nid in artifacts:
        s = Path(nid).stem
        stem_map.setdefault(s, nid)
        stem_map.setdefault(s.upper(), nid)

    for nid, art in artifacts.items():
        g.adjacency.setdefault(nid, set())
        fp = art.file_path

        if fp.endswith(".py"):
            for mod in _python_imports(fp):
                parts = mod.replace(".", "/")
                for suffix in (".py", "/__init__.py"):
                    target = parts + suffix
                    if target in known and target != nid:
                        edge = (nid, target)
                        if edge not in seen:
                            seen.add(edge)
                            g.adjacency[nid].add(target)
                            g.edges.append(edge)
                        break

        elif fp.endswith(".json"):
            for ref in _json_refs(fp):
                target = ref if ref in known else stem_map.get(ref)
                if target and target != nid:
                    edge = (nid, target)
                    if edge not in seen:
                        seen.add(edge)
                        g.adjacency[nid].add(target)
                        g.edges.append(edge)

    return g


# ── Provenance ─────────────────────────────────────────────────────────────────

def _skill_node_id(skill_id: str) -> str:
    """REFERENCE_DRIFT_WITNESS_V1 → oracle_town/skills/reference_drift_witness/skill.py"""
    name = re.sub(r"_V\d+$", "", skill_id).lower()
    return f"oracle_town/skills/{name}/skill.py"


def _replay_provenance(ledger_path: str) -> Set[str]:
    """
    Returns a set of repo-relative node_ids with sovereign provenance.
    Currently: skill files with SKILL_PROMOTION_DECISION_V1 + sovereign_promotion=True.
    """
    receipted: Set[str] = set()
    if not os.path.exists(ledger_path):
        return receipted
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "SKILL_PROMOTION_DECISION_V1":
                    p = ev.get("payload", {})
                    if p.get("sovereign_promotion") is True:
                        sid = p.get("skill_id", "")
                        if sid:
                            receipted.add(_skill_node_id(sid))
    except OSError:
        pass
    return receipted


# ── PageRank ───────────────────────────────────────────────────────────────────

def _pagerank(g: ReferenceGraph) -> Dict[str, float]:
    """Deterministic power-iteration PageRank over G_R."""
    nodes = sorted(g.nodes.keys())          # sorted → deterministic
    n = len(nodes)
    if n == 0:
        return {}

    idx      = {nd: i for i, nd in enumerate(nodes)}
    rank: List[float] = [1.0 / n] * n

    in_e: Dict[int, List[int]] = {i: [] for i in range(n)}
    out_d: Dict[int, int]      = {i: 0  for i in range(n)}

    for src, tgt in g.edges:
        s, t = idx.get(src), idx.get(tgt)
        if s is not None and t is not None:
            in_e[t].append(s)
            out_d[s] += 1

    for _ in range(_PAGERANK_ITERS):
        dangling = sum(rank[i] for i in range(n) if out_d[i] == 0)
        base = (1.0 - _PAGERANK_DAMPING) / n + _PAGERANK_DAMPING * dangling / n
        new: List[float] = [base] * n
        for i in range(n):
            for j in in_e[i]:
                if out_d[j] > 0:
                    new[i] += _PAGERANK_DAMPING * rank[j] / out_d[j]
        rank = new

    return {nodes[i]: rank[i] for i in range(n)}


# ── Drift computation ──────────────────────────────────────────────────────────

def _drift(artifacts: Dict[str, Artifact], ranks: Dict[str, float]) -> List[Artifact]:
    """Compute D(x) = rank(x) * (1 - P(x)) for all artifacts. Deterministic sort."""
    for nid, art in artifacts.items():
        art.rank        = ranks.get(nid, 0.0)
        art.drift_score = art.rank * (1.0 - art.provenance)
    return sorted(artifacts.values(), key=lambda a: (-a.drift_score, a.node_id))


# ── Public API ─────────────────────────────────────────────────────────────────

def probe(
    ledger_path: str = LEDGER_DEFAULT,
    top_n: int = _TOP_N_DEFAULT,
    _artifacts: Optional[Dict[str, Artifact]] = None,
) -> Dict[str, Any]:
    """Run the reference drift probe. Returns REFERENCE_DRIFT_WITNESS_V1 dict."""
    arts = _artifacts if _artifacts is not None else _discover_artifacts()

    graph     = _build_graph(arts)
    receipted = _replay_provenance(ledger_path)

    for nid, art in arts.items():
        art.provenance = 1.0 if nid in receipted else 0.0

    ranks  = _pagerank(graph)
    ranked = _drift(arts, ranks)

    top_drift = [
        {
            "node_id":       a.node_id,
            "artifact_type": a.artifact_type,
            "drift_score":   round(a.drift_score, 8),
            "rank":          round(a.rank, 8),
            "provenance":    a.provenance,
        }
        for a in ranked
        if a.drift_score > 0
    ][:top_n]

    n_receipted = sum(1 for a in arts.values() if a.provenance == 1.0)

    return {
        "schema_name":    "REFERENCE_DRIFT_WITNESS_V1",
        "schema_version": "1.0.0",
        "ledger_path":    ledger_path,
        "graph_stats": {
            "node_count":        len(arts),
            "edge_count":        len(graph.edges),
            "receipted_count":   n_receipted,
            "unreceipted_count": len(arts) - n_receipted,
        },
        "top_drift":    top_drift,
        "deterministic": True,
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="REFERENCE_DRIFT_WITNESS_V1 probe")
    parser.add_argument("--ledger", default=LEDGER_DEFAULT)
    parser.add_argument("--top",    type=int, default=_TOP_N_DEFAULT, dest="top_n")
    parser.add_argument("--json",   action="store_true", dest="json_out")
    args = parser.parse_args()

    result = probe(ledger_path=args.ledger, top_n=args.top_n)

    if args.json_out:
        print(json.dumps(result, indent=2))
        sys.exit(0)

    gs = result["graph_stats"]
    print(f"\nREFERENCE DRIFT WITNESS V1")
    print(f"  Ledger       : {result['ledger_path']}")
    print(f"  Artifacts    : {gs['node_count']} nodes  /  {gs['edge_count']} edges")
    print(f"  Receipted    : {gs['receipted_count']}  /  {gs['node_count']}")
    print(f"  Unreceipted  : {gs['unreceipted_count']}")

    if result["top_drift"]:
        print(f"\n  Top {len(result['top_drift'])} drift artifacts (D = rank × (1 - P)):")
        for e in result["top_drift"]:
            prov = "✓" if e["provenance"] == 1.0 else "✗"
            print(
                f"    [{prov}] D={e['drift_score']:.6f}  R={e['rank']:.6f}"
                f"  {e['artifact_type']:12}  {e['node_id']}"
            )
    else:
        print("\n  No drift detected — all artifacts receipted or unranked.")

    sys.exit(0)


if __name__ == "__main__":
    main()
