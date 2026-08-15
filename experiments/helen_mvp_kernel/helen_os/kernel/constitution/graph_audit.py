r"""Graph Topology Audit — T-GRAPH-001/002. The doctrine becomes an
executable admission gate: a typed execution graph is AUDITED before
it is admitted, and parallelism is earned by proving independence.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: SPEC_CANDIDATE (the operator's grade). This module does not
execute graphs — it says which graphs are ADMISSIBLE. Workers execute
graphs; HELEN admits graphs.

The graph type:

    G = (V, E, J, R, S, Pi)
        V   typed nodes            E   typed edges (DATA/DECISION/
        J   joins                      AUTHORITY/CONTROL)
        R   deterministic routes   S   durable resumable run state
        Pi  explicit capability / authority assignment

Two laws are the point of the whole module:

    (u,v) in E_DATA  =>  Consumes(v) ∩ Produces(u) != ∅   (or a
                         false edge — EDGE_WITHOUT_CONSUMPTION)

    dependency propagation  !=  privilege propagation
        E_DATA, E_DECISION, E_CONTROL carry NO capability; authority
        lives in Pi and changes only through an admitted E_AUTHORITY.
        Authority(v) ⊆ Grant(v), full stop — no inheritance from
        predecessors exists in the graph semantics at all.

The objective (T-GRAPH-001):

    minimize CriticalPath(G')
    subject to   G' ≡_obs G          (observational equivalence,
                                       NOT prose equality)
    and          Authority(G') ⊆ Authority(G)
                                       (speedup never licenses
                                        authority expansion)

Audit is a COMPILER PASS, not a report:

    Audit(G) = (errors, warnings, transformations, metrics)

Optimization is permitted only when errors == ∅.
"""
from __future__ import annotations

import hashlib
import json

EDGE_TYPES = ("DATA", "DECISION", "AUTHORITY", "CONTROL")
COST_CLASS = {"CHEAP": 1, "STANDARD": 3, "STRONG": 8}
OBS_DIMENSIONS = ("schema", "business_state", "admitted_effects",
                  "policy_decisions", "required_evidence")

HARD_ERRORS = ("CROSS_TENANT_STATE", "MODEL_CONTROLLED_AUTHORITY",
               "CAPABILITY_WITHOUT_GRANT", "NON_IDEMPOTENT_EFFECT",
               "MISSING_ADMISSION_BOUNDARY", "MISSING_RESUME_STATE",
               "UNBOUNDED_RETRY", "UNBOUNDED_FAN",
               "INVALID_AUTHORITY_EDGE", "STATE_WITHOUT_OWNER")
WARNINGS = ("EDGE_WITHOUT_CONSUMPTION", "UNNECESSARY_JOIN",
            "TRANSCRIPT_PASSING", "MISSING_VERIFIER",
            "REDUNDANT_SERIALIZATION", "LOW_PARALLELISM_UTILIZATION",
            "DUPLICATE_EVIDENCE_ROOT",
            "EXPENSIVE_WORKER_ON_BOUNDED_TASK")


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


def graph_hash(G) -> str:
    body = {"V": sorted(n["id"] for n in G["nodes"]),
            "E": sorted((e["from"], e["to"], e["dependency_type"],
                         tuple(sorted(e.get("consumes", ()))))
                        for e in G["edges"]),
            "J": sorted(j["id"] for j in G.get("joins", ())),
            "R": sorted(r["id"] for r in G.get("routes", ()))}
    return hashlib.sha256(canon(body).encode()).hexdigest()


# ── build & structural typing ──────────────────────────────────────────

def build_graph(nodes, edges, joins=(), routes=()) -> dict:
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        return {"ok": False, "reason": "E_DUPLICATE_NODE_ID"}
    node_by = {n["id"]: n for n in nodes}
    for e in edges:
        if e.get("dependency_type") not in EDGE_TYPES:
            return {"ok": False, "reason": "E_UNTYPED_EDGE",
                    "edge": (e.get("from"), e.get("to"))}
        if e["from"] not in node_by or e["to"] not in node_by:
            return {"ok": False, "reason": "E_DANGLING_EDGE",
                    "edge": (e.get("from"), e.get("to"))}
    G = {"nodes": list(nodes), "edges": list(edges),
         "joins": list(joins), "routes": list(routes),
         "_by": node_by}
    G["graph_hash"] = graph_hash(G)
    return {"ok": True, "G": G}


def _produces(node) -> set:
    return set(node.get("outputs", ()))


def _consumes_on_edge(edge) -> set:
    return set(edge.get("consumes", ()))


def _is_effect(node) -> bool:
    return bool(node.get("side_effects"))


def _mutates_state(node) -> bool:
    return _is_effect(node) or bool(node.get("writes_state"))


# ── the audit (compiler pass) ──────────────────────────────────────────

def audit(G) -> dict:
    errors, warnings = [], []
    by = G["_by"]

    def err(code, **kw):
        errors.append({"code": code, **kw})

    def warn(code, **kw):
        warnings.append({"code": code, **kw})

    # ---- edges: the DATA-consumption law, transcripts, false edges ----
    for e in G["edges"]:
        u, v = by[e["from"]], by[e["to"]]
        dt = e["dependency_type"]
        if dt == "DATA":
            if not (_consumes_on_edge(e) & _produces(u)):
                warn("EDGE_WITHOUT_CONSUMPTION",
                     edge=(e["from"], e["to"]),
                     note="declared DATA but consumes nothing u "
                          "produces — candidate REMOVE_EDGE")
        if e.get("payload_kind") == "transcript":
            warn("TRANSCRIPT_PASSING", edge=(e["from"], e["to"]),
                 note="pass an artifact reference, not a retelling")
        # dependency propagation != privilege propagation: only an
        # admitted AUTHORITY edge may move capability.
        if dt == "AUTHORITY" and not e.get("admitted"):
            err("INVALID_AUTHORITY_EDGE", edge=(e["from"], e["to"]))
        if dt in ("DATA", "DECISION", "CONTROL") and e.get("grants"):
            err("CAPABILITY_WITHOUT_GRANT", edge=(e["from"], e["to"]),
                note="a non-authority edge tried to grant capability")

    # ---- nodes: authority ⊆ grant, effects, resume, retry, tenant ----
    for n in G["nodes"]:
        grant = set(n.get("capabilities", ()))
        needed = set()
        for se in n.get("side_effects", ()):
            if se.get("requires_capability"):
                needed.add(se["requires_capability"])
        if needed - grant:
            err("CAPABILITY_WITHOUT_GRANT", node=n["id"],
                missing=tuple(sorted(needed - grant)))
        if _is_effect(n):
            if not n.get("idempotency_key"):
                err("NON_IDEMPOTENT_EFFECT", node=n["id"])
            if not n.get("admission_boundary"):
                err("MISSING_ADMISSION_BOUNDARY", node=n["id"])
        if _mutates_state(n) and not n.get("resume"):
            err("MISSING_RESUME_STATE", node=n["id"])
        rp = n.get("retry")
        if rp is not None and (not isinstance(rp, dict)
                               or rp.get("max") is None):
            err("UNBOUNDED_RETRY", node=n["id"])
        # state must have an owner; cross-tenant reads are refused
        for ref in n.get("state_refs", ()):
            if not ref.get("tenant"):
                err("STATE_WITHOUT_OWNER", node=n["id"], ref=ref)
            elif n.get("tenant") and ref["tenant"] != n["tenant"]:
                err("CROSS_TENANT_STATE", node=n["id"],
                    node_tenant=n["tenant"], ref_tenant=ref["tenant"])
        # verifier independence: producer principal != admitter
        if n.get("consequential"):
            vp = n.get("verifier_principal")
            if not n.get("verifier") or n.get("verifier") == n["id"] \
                    or vp is None or vp == n.get("principal"):
                warn("MISSING_VERIFIER", node=n["id"],
                     note="consequential node self-approves: "
                          "producer principal == admitter")
        if n.get("cost_class") == "STRONG" and n.get("bounded_task"):
            warn("EXPENSIVE_WORKER_ON_BOUNDED_TASK", node=n["id"])

    # ---- fans and routes ----
    for n in G["nodes"]:
        if n.get("fan") and n.get("fan_max") is None:
            err("UNBOUNDED_FAN", node=n["id"])
    for r in G.get("routes", ()):
        if r.get("model_controlled_destination"):
            err("MODEL_CONTROLLED_AUTHORITY", route=r.get("id"))
        elif not r.get("deterministic_rule"):
            err("MODEL_CONTROLLED_AUTHORITY", route=r.get("id"),
                note="a route with no deterministic rule lets the "
                     "classifier pick the path")

    # ---- joins ----
    for j in G.get("joins", ()):
        if not j.get("next_needs_complete_set", True):
            warn("UNNECESSARY_JOIN", join=j.get("id"),
                 note="next node does not need the complete set — "
                      "candidate STREAM_BRANCH")

    # ---- duplicate evidence roots (consensus illusion) ----
    roots = {}
    for n in G["nodes"]:
        r = n.get("evidence_root")
        if r is not None:
            roots.setdefault(r, []).append(n["id"])
    for r, members in sorted(roots.items()):
        if len(members) > 1 and any(by[m].get("claims_independence")
                                    for m in members):
            warn("DUPLICATE_EVIDENCE_ROOT", root=r,
                 nodes=tuple(sorted(members)),
                 note="branches sharing an evidence root are not "
                      "independent witnesses")

    m = metrics(G)
    if m["W"] > 0 and m["independent_startable"] > m["W"]:
        warn("LOW_PARALLELISM_UTILIZATION",
             width=m["W"], independent=m["independent_startable"])

    return {"errors": errors, "warnings": warnings,
            "transformations": _propose(warnings),
            "metrics": m,
            "optimizable": len(errors) == 0,
            "graph_hash": G["graph_hash"]}


def _propose(warnings) -> list:
    table = {"EDGE_WITHOUT_CONSUMPTION": "REMOVE_EDGE",
             "UNNECESSARY_JOIN": "STREAM_BRANCH",
             "TRANSCRIPT_PASSING": "ARTIFACT_REFERENCE",
             "REDUNDANT_SERIALIZATION": "FAN_OUT"}
    out = []
    for w in warnings:
        if w["code"] in table:
            out.append({"on": w.get("edge") or w.get("join")
                        or w.get("node"), "warning": w["code"],
                        "candidate": table[w["code"]],
                        "note": "the compiler proposes; it never "
                                "silently rewrites an admitted graph"})
    return out


# ── critical path & metrics ────────────────────────────────────────────

def _cost(node) -> int:
    return COST_CLASS.get(node.get("cost_class", "STANDARD"), 3)


def critical_path(G, kept_only=False) -> dict:
    """Longest-weighted path over the ordering edges. kept_only drops
    false DATA edges (EDGE_WITHOUT_CONSUMPTION) — that is what the
    optimization removes to shrink CP."""
    by = G["_by"]

    def is_false(e):
        u = by[e["from"]]
        return (e["dependency_type"] == "DATA"
                and not (_consumes_on_edge(e) & _produces(u)))

    adj = {n["id"]: [] for n in G["nodes"]}
    indeg = {n["id"]: 0 for n in G["nodes"]}
    for e in G["edges"]:
        if kept_only and is_false(e):
            continue
        adj[e["from"]].append(e["to"])
        indeg[e["to"]] += 1
    # longest path in a DAG via topological relaxation
    order, stack = [], sorted(n for n in indeg if indeg[n] == 0)
    ind = dict(indeg)
    while stack:
        x = stack.pop(0)
        order.append(x)
        for y in sorted(adj[x]):
            ind[y] -= 1
            if ind[y] == 0:
                stack.append(y)
        stack.sort()
    if len(order) != len(G["nodes"]):
        return {"ok": False, "reason": "E_CYCLE"}
    dist = {n["id"]: _cost(by[n["id"]]) for n in G["nodes"]}
    level = {n["id"]: 0 for n in G["nodes"]}
    for x in order:
        for y in adj[x]:
            if dist[x] + _cost(by[y]) > dist[y]:
                dist[y] = dist[x] + _cost(by[y])
            if level[x] + 1 > level[y]:
                level[y] = level[x] + 1
    cp = max(dist.values()) if dist else 0
    # width = max nodes sharing a level (a deterministic antichain proxy)
    width = {}
    for nid, lv in level.items():
        width[lv] = width.get(lv, 0) + 1
    return {"ok": True, "cp": cp, "width": max(width.values()) if width
            else 0, "levels": level, "order": tuple(order)}


def metrics(G) -> dict:
    by = G["_by"]
    cp_all = critical_path(G, kept_only=False)
    cp_kept = critical_path(G, kept_only=True)
    data_edges = [e for e in G["edges"] if e["dependency_type"] == "DATA"]
    false_edges = [e for e in data_edges
                   if not (_consumes_on_edge(e) & _produces(by[e["from"]]))]
    authority = set()
    for n in G["nodes"]:
        authority |= set(n.get("capabilities", ()))
    state_nodes = [n for n in G["nodes"] if _mutates_state(n)]
    resumable = [n for n in state_nodes if n.get("resume")]
    effect_nodes = [n for n in G["nodes"] if _is_effect(n)]
    idem = [n for n in effect_nodes if n.get("idempotency_key")]
    conseq = [n for n in G["nodes"] if n.get("consequential")]
    verified = [n for n in conseq
                if n.get("verifier") and n.get("verifier") != n["id"]
                and n.get("verifier_principal") not in
                (None, n.get("principal"))]
    startable = [n["id"] for n in G["nodes"]
                 if not any(e["to"] == n["id"] for e in G["edges"])]

    def frac(a, b):
        return round(a / b, 6) if b else None

    return {
        "CP": cp_all["cp"] if cp_all["ok"] else None,          # before
        "CP_kept": cp_kept["cp"] if cp_kept["ok"] else None,   # after
        "W": cp_kept["width"] if cp_kept["ok"] else None,
        "F": len(false_edges),
        "A": len(authority), "A_set": tuple(sorted(authority)),
        "R": frac(len(resumable), len(state_nodes)),
        "I": frac(len(idem), len(effect_nodes)),
        "P": frac(len(data_edges) - len(false_edges), len(data_edges)),
        "V": frac(len(verified), len(conseq)),
        "independent_startable": len(startable),
    }


# ── observational equivalence & the objective ──────────────────────────

def observational_equivalence(obs_before, obs_after) -> dict:
    """G' ≡_obs G under the frozen test suite: schema, business state,
    admitted effects and policy decisions are EQUAL; required evidence
    is ≃ (after ⊆ before — the optimized graph may need no MORE
    evidence, never less-rigorous). Unconstrained cognitive prose may
    vary; that is why exact output equality is the wrong test once
    cognition is probabilistic."""
    diffs = []
    for dim in ("schema", "business_state", "admitted_effects",
                "policy_decisions"):
        if obs_before.get(dim) != obs_after.get(dim):
            diffs.append(dim)
    rb = set(obs_before.get("required_evidence", ()))
    ra = set(obs_after.get("required_evidence", ()))
    evidence_ok = ra >= rb          # after must not require LESS evidence
    if not evidence_ok:
        diffs.append("required_evidence")
    return {"equivalent": not diffs, "divergent_dimensions": tuple(diffs),
            "evidence_relation": "after⊇before" if evidence_ok
            else "after_weakened"}


def optimize_verdict(before_G, after_G, obs_before, obs_after) -> dict:
    """PASS only when the topology got faster, the observable contract
    held, authority did not expand, and the optimized graph has zero
    hard errors. Otherwise HOLD — a faster graph that expands authority
    or changes replay semantics is not an improvement."""
    a_before = audit(before_G)
    a_after = audit(after_G)
    if a_after["errors"]:
        return {"GRAPH_VERDICT": "HOLD",
                "reason": "E_ERRORS_BLOCK_OPTIMIZATION",
                "errors": a_after["errors"]}
    cp_before = a_before["metrics"]["CP"]
    cp_after = a_after["metrics"]["CP_kept"]
    obs = observational_equivalence(obs_before, obs_after)
    auth_before = set(a_before["metrics"]["A_set"])
    auth_after = set(a_after["metrics"]["A_set"])
    authority_ok = auth_after <= auth_before
    reasons = []
    if not (cp_after < cp_before):
        reasons.append("CP_not_reduced")
    if not obs["equivalent"]:
        reasons.append("observational_divergence:"
                       + ",".join(obs["divergent_dimensions"]))
    if not authority_ok:
        reasons.append("authority_expanded:"
                       + ",".join(sorted(auth_after - auth_before)))
    verdict = "PASS" if not reasons else "HOLD"
    return {"GRAPH_VERDICT": verdict,
            "critical_path_before": cp_before,
            "critical_path_after": cp_after,
            "speedup": (round(cp_before - cp_after, 6)
                        if cp_before is not None else None),
            "observational_equivalence": obs["equivalent"],
            "authority_non_expansion": authority_ok,
            "deleted_false_edges": a_before["metrics"]["F"],
            "reasons": tuple(reasons),
            "law": "parallelism is earned by proving independence; "
                   "speedup never licenses authority expansion"}


# ── the compiler pipeline (spec, as data) ──────────────────────────────

PIPELINE = ("WORKFLOW", "GRAPH_IR", "DEPENDENCY_AUDIT", "AUTHORITY_AUDIT",
            "EFFECT_AUDIT", "FAILURE_RESUME_AUDIT",
            "TOPOLOGY_OPTIMIZATION", "OBSERVATIONAL_EQUIVALENCE",
            "ADMISSION")


def pipeline_stage_order(stages) -> dict:
    """Admission is the LAST stage; optimization only after the audits.
    A pipeline that optimizes before auditing, or admits before the
    equivalence test, is refused."""
    stages = tuple(stages)
    if stages == PIPELINE:
        return {"licensed": True}
    if "ADMISSION" in stages:
        i = stages.index("ADMISSION")
        need = ("DEPENDENCY_AUDIT", "AUTHORITY_AUDIT", "EFFECT_AUDIT",
                "FAILURE_RESUME_AUDIT", "OBSERVATIONAL_EQUIVALENCE")
        missing = [s for s in need if s not in stages[:i]]
        if missing:
            return {"licensed": False, "reason": "E_ADMIT_BEFORE_AUDIT",
                    "missing_before_admission": tuple(missing)}
    if "TOPOLOGY_OPTIMIZATION" in stages and "DEPENDENCY_AUDIT" in stages:
        if stages.index("TOPOLOGY_OPTIMIZATION") < \
                stages.index("DEPENDENCY_AUDIT"):
            return {"licensed": False,
                    "reason": "E_OPTIMIZE_BEFORE_AUDIT"}
    return {"licensed": False, "reason": "E_PIPELINE_OUT_OF_ORDER",
            "expected": PIPELINE}
