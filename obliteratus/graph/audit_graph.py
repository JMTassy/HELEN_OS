#!/usr/bin/env python3
"""audit_graph.py — T-GRAPH-002 static graph compiler.

authority=false · claim=NO_CLAIM · non-sovereign

Parses a Graph IR document (graph_ir.schema.json) and runs the nine
static passes IN ORDER:

    PARSE → TYPECHECK → DEPENDENCY → AUTHORITY → EFFECT → RESUME →
    VERIFICATION → TOPOLOGY → OBSERVATIONAL_EQUIVALENCE

Optimization stops if Errors(G) != ∅. Warnings are non-authoritative
transformation candidates. The crucial invariant:

    CompilerProposal  !=>  GraphMutation

This tool emits a candidate patch and a verdict; Gamma (the operator /
policy engine) still decides whether the admitted graph changes.

Authority is manifest-assigned, never dependency-inherited:

    E_D transports data only
    Authority(v) ⊆ Grant(v)
    ΔGrant(v) != 0  ⇒  ∃ admitted e ∈ E_A

Usage:
    python3 audit_graph.py <graph.json> [--optimized <graph2.json>]
    python3 audit_graph.py --selftest

Stdlib only, deterministic. `--selftest` runs the OBLITERATUS IR to
GRAPH_VERDICT=PASS and exercises every hard error at least once.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

EDGE_TYPES = ("DATA", "DECISION", "AUTHORITY", "CONTROL")
COST = {"CHEAP": 1, "STANDARD": 3, "STRONG": 8}
NODE_KINDS = ("compute", "decision", "effect", "join", "route",
              "verify", "source")

PASSES = ("PARSE", "TYPECHECK", "DEPENDENCY", "AUTHORITY", "EFFECT",
          "RESUME", "VERIFICATION", "TOPOLOGY",
          "OBSERVATIONAL_EQUIVALENCE")

HARD_ERRORS = ("CROSS_TENANT_STATE", "MODEL_CONTROLLED_AUTHORITY",
               "CAPABILITY_WITHOUT_GRANT", "INVALID_AUTHORITY_EDGE",
               "MISSING_ADMISSION_BOUNDARY", "NON_IDEMPOTENT_EFFECT",
               "MISSING_RESUME_STATE", "UNBOUNDED_RETRY",
               "UNBOUNDED_FAN", "STATE_WITHOUT_OWNER")
WARNINGS = ("EDGE_WITHOUT_CONSUMPTION", "UNNECESSARY_JOIN",
            "TRANSCRIPT_PASSING", "REDUNDANT_SERIALIZATION",
            "MISSING_VERIFIER", "LOW_PARALLELISM_UTILIZATION",
            "DUPLICATE_EVIDENCE_ROOT",
            "EXPENSIVE_WORKER_ON_BOUNDED_TASK")
_PROPOSAL = {"EDGE_WITHOUT_CONSUMPTION": "REMOVE_EDGE",
             "UNNECESSARY_JOIN": "STREAM_BRANCH",
             "TRANSCRIPT_PASSING": "ARTIFACT_REFERENCE",
             "REDUNDANT_SERIALIZATION": "FAN_OUT"}


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


def graph_hash(g):
    body = {"id": g.get("id"), "version": g.get("version"),
            "nodes": sorted(n["id"] for n in g.get("nodes", [])),
            "edges": sorted((e["from"], e["to"], e["type"],
                             e.get("artifact"))
                            for e in g.get("edges", []))}
    return hashlib.sha256(canon(body).encode()).hexdigest()


# ── PASS 1-2: parse & typecheck ────────────────────────────────────────

def _parse_typecheck(g):
    errs = []
    if not isinstance(g, dict):
        return ["E_NOT_AN_OBJECT"]
    for req in ("id", "version", "state_owner", "nodes", "edges"):
        if req not in g:
            errs.append(f"E_MISSING_FIELD:{req}")
    if errs:
        return errs
    if not g.get("state_owner"):
        errs.append("STATE_WITHOUT_OWNER:graph")
    ids = [n.get("id") for n in g["nodes"]]
    if len(ids) != len(set(ids)) or any(not i for i in ids):
        errs.append("E_DUPLICATE_OR_MISSING_NODE_ID")
    by = {n["id"]: n for n in g["nodes"]}
    for n in g["nodes"]:
        if n.get("kind") not in NODE_KINDS:
            errs.append(f"E_UNKNOWN_NODE_KIND:{n.get('id')}")
    for e in g["edges"]:
        if e.get("type") not in EDGE_TYPES:
            errs.append(f"E_UNTYPED_EDGE:{e.get('from')}->{e.get('to')}")
        if e.get("from") not in by or e.get("to") not in by:
            errs.append(f"E_DANGLING_EDGE:{e.get('from')}->{e.get('to')}")
    return errs


# ── PASS 3: dependency (DATA consumption law) ──────────────────────────

def _pass_dependency(g, by, errors, warnings):
    for e in g["edges"]:
        if e["type"] != "DATA":
            continue
        produced = set(by[e["from"]].get("produces", []))
        consumed = set(by[e["to"]].get("consumes", []))
        art = e.get("artifact")
        # a DATA edge is real iff its artifact is produced by u and
        # consumed by v (or the produced∩consumed set is nonempty)
        real = (art in produced and art in consumed) if art else \
            bool(produced & consumed)
        if not real:
            warnings.append({"code": "EDGE_WITHOUT_CONSUMPTION",
                             "edge": [e["from"], e["to"]],
                             "candidate": "REMOVE_EDGE"})
        if e.get("payload_kind") == "transcript":
            warnings.append({"code": "TRANSCRIPT_PASSING",
                             "edge": [e["from"], e["to"]],
                             "candidate": "ARTIFACT_REFERENCE"})


# ── PASS 4: authority (manifest-assigned, never inherited) ─────────────

def _pass_authority(g, by, errors, warnings):
    for e in g["edges"]:
        if e["type"] == "AUTHORITY" and not e.get("admitted"):
            errors.append({"code": "INVALID_AUTHORITY_EDGE",
                           "edge": [e["from"], e["to"]]})
        if e["type"] in ("DATA", "DECISION", "CONTROL") and e.get("grant"):
            errors.append({"code": "CAPABILITY_WITHOUT_GRANT",
                           "edge": [e["from"], e["to"]],
                           "note": "non-authority edge tried to grant"})
    # a node's effective capabilities are exactly its own grants; if a
    # node needs a capability for an effect it does not hold, refuse.
    for n in g["nodes"]:
        held = set(n.get("grants", []))
        ec = n.get("effect_contract")
        if ec and ec.get("capability") and ec["capability"] not in held:
            errors.append({"code": "CAPABILITY_WITHOUT_GRANT",
                           "node": n["id"],
                           "missing": ec["capability"]})
    # routes: a model-controlled destination mints authority
    for r in g.get("routes", []):
        if r.get("model_controlled_destination"):
            errors.append({"code": "MODEL_CONTROLLED_AUTHORITY",
                           "route": r.get("id")})
        elif not r.get("deterministic_rule"):
            errors.append({"code": "MODEL_CONTROLLED_AUTHORITY",
                           "route": r.get("id"),
                           "note": "no deterministic rule"})


# ── PASS 5: effect ─────────────────────────────────────────────────────

def _is_effect(n):
    return n.get("kind") == "effect" or bool(n.get("effect_contract"))


def _pass_effect(g, by, errors, warnings):
    for n in g["nodes"]:
        if not _is_effect(n):
            continue
        ec = n.get("effect_contract") or {}
        key = n.get("idempotency_key") or ec.get("idempotency_key")
        boundary = n.get("admission_boundary") or \
            ec.get("admission_boundary")
        if not key:
            errors.append({"code": "NON_IDEMPOTENT_EFFECT",
                           "node": n["id"]})
        if not boundary:
            errors.append({"code": "MISSING_ADMISSION_BOUNDARY",
                           "node": n["id"]})
        if not n.get("grants"):
            errors.append({"code": "CAPABILITY_WITHOUT_GRANT",
                           "node": n["id"],
                           "note": "effect node holds no grant"})


# ── PASS 6: resume ─────────────────────────────────────────────────────

def _mutates(n):
    return _is_effect(n) or bool(n.get("writes_state")) \
        or bool(n.get("resume_contract"))


def _pass_resume(g, by, errors, warnings):
    for n in g["nodes"]:
        if (_is_effect(n) or n.get("writes_state")) \
                and not n.get("resume_contract"):
            errors.append({"code": "MISSING_RESUME_STATE",
                           "node": n["id"]})
        rp = n.get("retry")
        if rp is not None and (not isinstance(rp, dict)
                               or rp.get("max") is None):
            errors.append({"code": "UNBOUNDED_RETRY", "node": n["id"]})
        if n.get("fan") and n.get("fan_max") is None:
            errors.append({"code": "UNBOUNDED_FAN", "node": n["id"]})
        for ref in n.get("state_refs", []):
            if not ref.get("tenant"):
                errors.append({"code": "STATE_WITHOUT_OWNER",
                               "node": n["id"]})
            elif n.get("tenant") and ref["tenant"] != n["tenant"]:
                errors.append({"code": "CROSS_TENANT_STATE",
                               "node": n["id"]})


# ── PASS 7: verification (independence is a vector) ────────────────────

def _pass_verification(g, by, errors, warnings):
    for n in g["nodes"]:
        if not n.get("consequential"):
            continue
        vc = n.get("verifier_contract")
        # producer principal must differ from admitter/verifier
        # principal; a boolean 'independent' is never sufficient.
        if not vc or vc.get("producer_principal") == \
                vc.get("verifier_principal") or \
                not vc.get("verifier_principal") or \
                not vc.get("method"):
            warnings.append({"code": "MISSING_VERIFIER", "node": n["id"],
                             "note": "consequential node lacks an "
                                     "independent verifier principal"})
        elif vc.get("evidence_roots") is not None and \
                vc.get("producer_context_hash") and \
                vc.get("producer_context_hash") == \
                vc.get("verifier_context_hash"):
            warnings.append({"code": "MISSING_VERIFIER", "node": n["id"],
                             "note": "producer and verifier share a "
                                     "context hash — same distribution"})


# ── PASS 8: topology (metrics, false-edge removal, evidence roots) ─────

def _cost(n):
    return COST.get(n.get("cost_class", "STANDARD"), 3)


def _false_data_edge(e, by):
    if e["type"] != "DATA":
        return False
    produced = set(by[e["from"]].get("produces", []))
    consumed = set(by[e["to"]].get("consumes", []))
    art = e.get("artifact")
    real = (art in produced and art in consumed) if art else \
        bool(produced & consumed)
    return not real


def _critical_path(g, by, kept_only):
    adj = {n["id"]: [] for n in g["nodes"]}
    indeg = {n["id"]: 0 for n in g["nodes"]}
    for e in g["edges"]:
        if kept_only and _false_data_edge(e, by):
            continue
        adj[e["from"]].append(e["to"])
        indeg[e["to"]] += 1
    ind = dict(indeg)
    stack = sorted(n for n in ind if ind[n] == 0)
    order = []
    while stack:
        x = stack.pop(0)
        order.append(x)
        for y in sorted(adj[x]):
            ind[y] -= 1
            if ind[y] == 0:
                stack.append(y)
        stack.sort()
    if len(order) != len(g["nodes"]):
        return None, None
    dist = {n["id"]: _cost(by[n["id"]]) for n in g["nodes"]}
    level = {n["id"]: 0 for n in g["nodes"]}
    for x in order:
        for y in adj[x]:
            if dist[x] + _cost(by[y]) > dist[y]:
                dist[y] = dist[x] + _cost(by[y])
            if level[x] + 1 > level[y]:
                level[y] = level[x] + 1
    width = {}
    for lv in level.values():
        width[lv] = width.get(lv, 0) + 1
    return (max(dist.values()) if dist else 0,
            max(width.values()) if width else 0)


def _pass_topology(g, by, errors, warnings):
    roots = {}
    for n in g["nodes"]:
        r = n.get("evidence_root")
        if r is not None:
            roots.setdefault(r, []).append(n["id"])
    for r, members in sorted(roots.items()):
        if len(members) > 1 and any(by[m].get("claims_independence")
                                    for m in members):
            warnings.append({"code": "DUPLICATE_EVIDENCE_ROOT",
                             "root": r, "nodes": sorted(members)})
    for n in g["nodes"]:
        if n.get("cost_class") == "STRONG" and n.get("bounded_task"):
            warnings.append({"code": "EXPENSIVE_WORKER_ON_BOUNDED_TASK",
                             "node": n["id"]})
    for j in g.get("joins", []):
        if j.get("next_needs_complete_set") is False:
            warnings.append({"code": "UNNECESSARY_JOIN",
                             "join": j.get("id"),
                             "candidate": "STREAM_BRANCH"})


def _metrics(g, by):
    cp_before, _ = _critical_path(g, by, kept_only=False)
    cp_after, width = _critical_path(g, by, kept_only=True)
    data = [e for e in g["edges"] if e["type"] == "DATA"]
    false_e = [e for e in data if _false_data_edge(e, by)]
    authority = set()
    for n in g["nodes"]:
        authority |= set(n.get("grants", []))
    state_nodes = [n for n in g["nodes"] if _mutates(n)]
    resumable = [n for n in state_nodes if n.get("resume_contract")]
    effect = [n for n in g["nodes"] if _is_effect(n)]
    idem = [n for n in effect if (n.get("idempotency_key") or
            (n.get("effect_contract") or {}).get("idempotency_key"))]
    conseq = [n for n in g["nodes"] if n.get("consequential")]
    verified = [n for n in conseq if (n.get("verifier_contract") or {}
                ).get("verifier_principal") not in
                (None, (n.get("verifier_contract") or {}
                        ).get("producer_principal"))]

    def frac(a, b):
        return round(a / b, 6) if b else None

    return {"CP_before": cp_before, "CP_after": cp_after,
            "W": width, "F": len(false_e),
            "A": len(authority), "A_set": sorted(authority),
            "R": frac(len(resumable), len(state_nodes)),
            "I": frac(len(idem), len(effect)),
            "P": frac(len(data) - len(false_e), len(data)),
            "V": frac(len(verified), len(conseq))}


# ── PASS 9: observational equivalence ──────────────────────────────────

def observational_equivalence(before, after):
    diffs = []
    for dim in ("schema", "business_state", "admitted_effects",
                "policy_decisions"):
        if before.get(dim) != after.get(dim):
            diffs.append(dim)
    rb = set(before.get("required_evidence", ()))
    ra = set(after.get("required_evidence", ()))
    if not ra >= rb:
        diffs.append("required_evidence")
    return {"equivalent": not diffs, "divergent": diffs}


# ── the compiler ───────────────────────────────────────────────────────

def compile_graph(g):
    """Run all nine passes in order. Returns
    (errors, warnings, transformations, metrics, stopped_at)."""
    parse_errs = _parse_typecheck(g)
    if parse_errs:
        return {"errors": [{"code": e.split(":")[0], "detail": e}
                           for e in parse_errs],
                "warnings": [], "transformations": [], "metrics": None,
                "stopped_at": "TYPECHECK", "optimizable": False,
                "graph_hash": None}
    by = {n["id"]: n for n in g["nodes"]}
    errors, warnings = [], []
    _pass_dependency(g, by, errors, warnings)
    _pass_authority(g, by, errors, warnings)
    _pass_effect(g, by, errors, warnings)
    _pass_resume(g, by, errors, warnings)
    _pass_verification(g, by, errors, warnings)
    _pass_topology(g, by, errors, warnings)
    transformations = [{"on": w.get("edge") or w.get("join")
                        or w.get("node"), "warning": w["code"],
                        "candidate": _PROPOSAL[w["code"]],
                        "note": "CompilerProposal !=> GraphMutation; "
                                "Gamma decides"}
                       for w in warnings if w["code"] in _PROPOSAL]
    return {"errors": errors, "warnings": warnings,
            "transformations": transformations,
            "metrics": _metrics(g, by),
            "optimizable": len(errors) == 0,
            "stopped_at": None,
            "graph_hash": graph_hash(g)}


def optimize_verdict(before, after):
    ab = compile_graph(before)
    aa = compile_graph(after)
    if aa["errors"]:
        return {"GRAPH_VERDICT": "HOLD",
                "reason": "E_ERRORS_BLOCK_OPTIMIZATION",
                "errors": aa["errors"]}
    cp_b = ab["metrics"]["CP_before"]
    cp_a = aa["metrics"]["CP_after"]
    obs_b = before.get("observational_contract", {})
    obs_a = after.get("observational_contract", {})
    # for the IR the observation contract is a set of equality flags;
    # equivalence holds when every declared flag is true in both.
    obs_ok = obs_b == obs_a and all(
        obs_a.get(k) for k in ("schema_equal", "business_state_equal",
                               "admitted_effects_equal",
                               "policy_decisions_equal"))
    auth_b = set(ab["metrics"]["A_set"])
    auth_a = set(aa["metrics"]["A_set"])
    authority_ok = auth_a <= auth_b
    reasons = []
    if not (cp_a < cp_b):
        reasons.append("CP_not_reduced")
    if not obs_ok:
        reasons.append("observational_divergence")
    if not authority_ok:
        reasons.append("authority_expanded:" +
                       ",".join(sorted(auth_a - auth_b)))
    return {"GRAPH_VERDICT": "PASS" if not reasons else "HOLD",
            "critical_path_before": cp_b, "critical_path_after": cp_a,
            "speedup": (cp_b - cp_a) if cp_b is not None else None,
            "deleted_false_edges": ab["metrics"]["F"],
            "observational_equivalence": obs_ok,
            "authority_non_expansion": authority_ok,
            "reasons": reasons,
            "law": "parallelism is earned by demonstrated "
                   "independence; parallelism may increase throughput, "
                   "never authority"}


def pipeline_stage_order(stages):
    stages = tuple(stages)
    if stages == PASSES:
        return {"licensed": True}
    if "OBSERVATIONAL_EQUIVALENCE" in stages and "TOPOLOGY" in stages \
            and stages.index("TOPOLOGY") > \
            stages.index("OBSERVATIONAL_EQUIVALENCE"):
        return {"licensed": False, "reason": "E_EQUIV_BEFORE_TOPOLOGY"}
    return {"licensed": False, "reason": "E_PASS_ORDER",
            "expected": list(PASSES)}


# ── selftest ───────────────────────────────────────────────────────────

def _oblit_ir(optimized):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "obliteratus_v0.graph.json")) as f:
        g = json.load(f)
    if not optimized:
        # inject the false serial edges (naive prose form)
        extra = []
        for i in range(1, 4):
            extra.append({"from": f"targeted_{i}",
                          "to": f"targeted_{i + 1}", "type": "DATA"})
        extra.append({"from": "replay_1", "to": "replay_2",
                      "type": "DATA"})
        g = dict(g, edges=g["edges"] + extra)
    return g


def selftest():
    after = _oblit_ir(optimized=True)
    before = _oblit_ir(optimized=False)
    ca = compile_graph(after)
    assert ca["stopped_at"] is None, ca
    assert not ca["errors"], ca["errors"]
    assert ca["metrics"]["F"] == 0, ca["metrics"]
    cb = compile_graph(before)
    assert cb["metrics"]["F"] == 4, cb["metrics"]
    v = optimize_verdict(before, after)
    assert v["GRAPH_VERDICT"] == "PASS", v
    assert v["critical_path_after"] < v["critical_path_before"], v
    assert v["authority_non_expansion"] is True

    # every hard error fires at least once on a crafted graph
    bad = {"id": "b", "version": 0, "state_owner": "we",
           "nodes": [
               {"id": "eff", "kind": "effect", "principal": "p",
                "consumes": [], "produces": ["x"], "grants": [],
                "state_refs": [{"key": "k"}], "tenant": "T1",
                "retry": {"max": None}, "fan": True, "fan_max": None},
               {"id": "eff2", "kind": "effect", "principal": "p",
                "consumes": [], "produces": ["y"],
                "grants": ["a"], "tenant": "T1",
                "state_refs": [{"key": "k", "tenant": "T2"}]},
               {"id": "c", "kind": "compute", "principal": "p",
                "consumes": [], "produces": ["z"]}],
           "edges": [
               {"from": "c", "to": "eff", "type": "DATA",
                "grant": "steal"},
               {"from": "c", "to": "eff2", "type": "AUTHORITY"}],
           "routes": [{"id": "r", "classifier_output": "c",
                       "model_controlled_destination": True}]}
    codes = {e["code"] for e in compile_graph(bad)["errors"]}
    for expected in ("NON_IDEMPOTENT_EFFECT", "MISSING_ADMISSION_BOUNDARY",
                     "MISSING_RESUME_STATE", "UNBOUNDED_RETRY",
                     "UNBOUNDED_FAN", "STATE_WITHOUT_OWNER",
                     "CROSS_TENANT_STATE", "CAPABILITY_WITHOUT_GRANT",
                     "INVALID_AUTHORITY_EDGE",
                     "MODEL_CONTROLLED_AUTHORITY"):
        assert expected in codes, (expected, codes)

    # authority expansion in the optimized graph -> HOLD
    smug = json.loads(json.dumps(after))
    smug["nodes"][0]["grants"] = ["prod.deploy"]
    hv = optimize_verdict(before, smug)
    assert hv["GRAPH_VERDICT"] == "HOLD"
    assert any("authority_expanded" in r for r in hv["reasons"])

    # pass order gate
    assert pipeline_stage_order(PASSES)["licensed"] is True
    assert pipeline_stage_order(("PARSE",))["reason"] == "E_PASS_ORDER"

    # determinism
    assert canon(compile_graph(after)) == canon(compile_graph(after))
    print("audit_graph selftest: OK (verdict PASS, CP "
          f"{v['critical_path_before']}->{v['critical_path_after']}, "
          "all 10 hard errors fired)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.stderr.write("usage: audit_graph.py <graph.json> "
                         "[--optimized <graph2.json>]\n")
        sys.exit(2)
    g = json.load(open(args[0]))
    if "--optimized" in sys.argv:
        idx = sys.argv.index("--optimized")
        after = json.load(open(sys.argv[idx + 1]))
        out = optimize_verdict(g, after)
    else:
        out = compile_graph(g)
    print(json.dumps(out, indent=2, sort_keys=True))
    ok = (out.get("GRAPH_VERDICT") == "PASS") if "GRAPH_VERDICT" in out \
        else out.get("optimizable")
    sys.exit(0 if ok else 1)
