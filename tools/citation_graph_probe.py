#!/usr/bin/env python3
"""
tools/citation_graph_probe.py — HELEN citation graph oracle.

Usage:
  python3 tools/citation_graph_probe.py receipts.json [--emit-sidecar]

Input: JSON array of receipt objects with optional claim_id + cites fields.
Output: JSON with loop_nodes, loop_count, graph_edges, and per-receipt annotation.

This is a NON-SOVEREIGN tool — it produces a risk signal, not a verdict.
The reducer / semantic review decides what to do with CITATION_LOOP_V1 receipts.
"""
import json
import sys
from pathlib import Path


def tarjan_scc(graph: dict) -> list:
    index_counter = [0]
    stack: list = []
    lowlink: dict = {}
    index: dict = {}
    on_stack: dict = {}
    sccs: list = []

    def _visit(root: str) -> None:
        index[root] = lowlink[root] = index_counter[0]
        index_counter[0] += 1
        stack.append(root)
        on_stack[root] = True
        work = [(root, iter(graph.get(root, [])))]
        while work:
            v, it = work[-1]
            try:
                w = next(it)
                if w not in index:
                    index[w] = lowlink[w] = index_counter[0]
                    index_counter[0] += 1
                    stack.append(w)
                    on_stack[w] = True
                    work.append((w, iter(graph.get(w, []))))
                elif on_stack.get(w):
                    lowlink[v] = min(lowlink[v], index[w])
            except StopIteration:
                work.pop()
                if work:
                    lowlink[work[-1][0]] = min(lowlink[work[-1][0]], lowlink[v])
                if lowlink[v] == index[v]:
                    scc: list = []
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        scc.append(w)
                        if w == v:
                            break
                    sccs.append(scc)

    for node in list(graph):
        if node not in index:
            _visit(node)
    return sccs


def run_probe(receipts: list) -> dict:
    graph: dict = {}
    id_map: dict = {}
    for rec in receipts:
        node = rec.get("claim_id", rec.get("id", "unknown"))
        cites = rec.get("cites", [])
        graph.setdefault(node, []).extend(cites)
        id_map[node] = rec
        for c in cites:
            graph.setdefault(c, [])

    in_loop: set = set()
    for node, nbrs in graph.items():
        if node in nbrs:
            in_loop.add(node)
    for scc in tarjan_scc(graph):
        if len(scc) > 1:
            in_loop.update(scc)

    annotated = []
    for rec in receipts:
        node = rec.get("claim_id", rec.get("id", "unknown"))
        annotated.append({**rec, "citation_loop_detected": node in in_loop,
                          "signal": "CITATION_LOOP_V1" if node in in_loop else "CLEAN"})

    # Typed verdict: P2_ROUTER → ROUTE when loops detected, OBSERVE when clean
    loop_count = len(in_loop)
    if loop_count > 0:
        verdict = {
            "probe": "citation_graph_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "ROUTE",
            "reason": "CITATION_LOOP_V1",
            "semantic_claim": False,
            "requires": "SEMANTIC_REVIEW_RECEIPT_V1",
            "loop_nodes": sorted(in_loop),
            "loop_count": loop_count,
        }
    else:
        verdict = {
            "probe": "citation_graph_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "OBSERVE",
            "reason": "CLEAN",
            "loop_count": 0,
        }

    return {
        "verdict": verdict,
        "loop_nodes": sorted(in_loop),
        "loop_count": loop_count,
        "graph_node_count": len(graph),
        "graph_edge_count": sum(len(v) for v in graph.values()),
        "receipts": annotated,
    }


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = Path(args[0])
    receipts = json.loads(path.read_text())
    result = run_probe(receipts)
    emit_sidecar = "--emit-sidecar" in args
    if emit_sidecar:
        sidecar = path.with_suffix(".citation_probe.json")
        sidecar.write_text(json.dumps(result, indent=2))
        print(f"Sidecar written: {sidecar}", file=sys.stderr)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
