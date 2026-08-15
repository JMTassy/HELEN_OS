"""A DATA edge that consumes nothing is a false edge; a non-authority
edge cannot grant capability and a node cannot use a capability it was
not granted; an effect node without an idempotency key or admission
boundary is refused; a state mutation without a resume contract is a
compiler error; a model-controlled route is refused; and the
OBLITERATUS optimization must reduce the critical path while keeping
the observable contract and never expanding authority.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import graph_audit as ga
import obliteratus_graph_spec as ogs
from graph_audit import (
    audit,
    build_graph,
    critical_path,
    metrics,
    observational_equivalence,
    optimize_verdict,
    pipeline_stage_order,
)


def _n(nid, **kw):
    base = {"id": nid, "job": "j", "inputs": [], "outputs": [nid],
            "output_schema": "s", "failure_states": ["EXECUTION_ERROR"],
            "capabilities": [], "side_effects": [],
            "cost_class": "STANDARD"}
    base.update(kw)
    return base


# ── the DATA consumption law ───────────────────────────────────────────

def test_a_data_edge_that_consumes_nothing_is_a_false_edge():
    g = build_graph([_n("A", outputs=["a"]), _n("B", outputs=["b"])],
                    [{"from": "A", "to": "B", "consumes": [],
                      "dependency_type": "DATA"}])["G"]
    a = audit(g)
    assert any(w["code"] == "EDGE_WITHOUT_CONSUMPTION"
               for w in a["warnings"])
    assert a["metrics"]["F"] == 1
    real = build_graph([_n("A", outputs=["a"]), _n("B", outputs=["b"])],
                       [{"from": "A", "to": "B", "consumes": ["a"],
                         "dependency_type": "DATA"}])["G"]
    assert metrics(real)["F"] == 0


def test_untyped_and_dangling_edges_refuse_at_build():
    assert build_graph([_n("A")], [{"from": "A", "to": "A"}])[
        "reason"] == "E_UNTYPED_EDGE"
    assert build_graph([_n("A")], [{"from": "A", "to": "GHOST",
                                    "dependency_type": "DATA"}])[
        "reason"] == "E_DANGLING_EDGE"


# ── dependency propagation != privilege propagation ────────────────────

def test_a_non_authority_edge_cannot_grant_capability():
    g = build_graph([_n("A"), _n("B")],
                    [{"from": "A", "to": "B", "consumes": [],
                      "dependency_type": "DATA", "grants": ["s3.write"]}
                     ])["G"]
    assert any(e["code"] == "CAPABILITY_WITHOUT_GRANT"
               for e in audit(g)["errors"])


def test_a_node_cannot_use_a_capability_it_was_not_granted():
    g = build_graph([_n("A", side_effects=[{"effect": "write",
                     "requires_capability": "s3.write"}],
                     idempotency_key="k", admission_boundary="b",
                     resume={"k": 1})], [])["G"]
    errs = {e["code"] for e in audit(g)["errors"]}
    assert "CAPABILITY_WITHOUT_GRANT" in errs
    granted = build_graph([_n("A", capabilities=["s3.write"],
                           side_effects=[{"effect": "write",
                            "requires_capability": "s3.write"}],
                           idempotency_key="k", admission_boundary="b",
                           resume={"k": 1})], [])["G"]
    assert not any(e["code"] == "CAPABILITY_WITHOUT_GRANT"
                   for e in audit(granted)["errors"])


def test_an_unadmitted_authority_edge_is_invalid():
    g = build_graph([_n("A"), _n("B")],
                    [{"from": "A", "to": "B",
                      "dependency_type": "AUTHORITY"}])["G"]
    assert any(e["code"] == "INVALID_AUTHORITY_EDGE"
               for e in audit(g)["errors"])
    ok = build_graph([_n("A"), _n("B")],
                     [{"from": "A", "to": "B",
                       "dependency_type": "AUTHORITY",
                       "admitted": True}])["G"]
    assert not any(e["code"] == "INVALID_AUTHORITY_EDGE"
                   for e in audit(ok)["errors"])


# ── effect, resume, retry, fan, tenant ─────────────────────────────────

def test_an_effect_node_needs_idempotency_and_admission_boundary():
    g = build_graph([_n("A", capabilities=["x"],
                     side_effects=[{"effect": "e",
                                    "requires_capability": "x"}],
                     resume={"k": 1})], [])["G"]
    errs = {e["code"] for e in audit(g)["errors"]}
    assert "NON_IDEMPOTENT_EFFECT" in errs
    assert "MISSING_ADMISSION_BOUNDARY" in errs


def test_a_state_mutation_needs_a_resume_contract():
    g = build_graph([_n("A", writes_state=True)], [])["G"]
    assert any(e["code"] == "MISSING_RESUME_STATE"
               for e in audit(g)["errors"])


def test_unbounded_retry_and_fan_are_errors():
    g = build_graph([_n("A", retry={"max": None}),
                     _n("B", fan=True, fan_max=None)], [])["G"]
    errs = {e["code"] for e in audit(g)["errors"]}
    assert "UNBOUNDED_RETRY" in errs and "UNBOUNDED_FAN" in errs
    ok = build_graph([_n("A", retry={"max": 3}),
                      _n("B", fan=True, fan_max=100)], [])["G"]
    assert not audit(ok)["errors"]


def test_cross_tenant_state_and_ownerless_state_refuse():
    g = build_graph([_n("A", tenant="T1",
                     state_refs=[{"key": "k", "tenant": "T2"}])], [])["G"]
    assert any(e["code"] == "CROSS_TENANT_STATE"
               for e in audit(g)["errors"])
    g2 = build_graph([_n("A", tenant="T1",
                      state_refs=[{"key": "k"}])], [])["G"]
    assert any(e["code"] == "STATE_WITHOUT_OWNER"
               for e in audit(g2)["errors"])


# ── routing authority ──────────────────────────────────────────────────

def test_a_model_controlled_route_is_refused():
    g = build_graph([_n("A")], [], routes=[
        {"id": "r", "classifier_output": "c",
         "model_controlled_destination": True}])["G"]
    assert any(e["code"] == "MODEL_CONTROLLED_AUTHORITY"
               for e in audit(g)["errors"])
    g2 = build_graph([_n("A")], [], routes=[
        {"id": "r", "classifier_output": "c",
         "deterministic_rule": "table", "destination": "x",
         "model_controlled_destination": False}])["G"]
    assert not any(e["code"] == "MODEL_CONTROLLED_AUTHORITY"
                   for e in audit(g2)["errors"])


# ── verifier independence ──────────────────────────────────────────────

def test_a_consequential_node_that_self_approves_is_flagged():
    g = build_graph([_n("A", consequential=True, principal="p",
                     verifier="A", verifier_principal="p")], [])["G"]
    assert any(w["code"] == "MISSING_VERIFIER"
               for w in audit(g)["warnings"])
    ind = build_graph([_n("A", consequential=True, principal="p",
                       verifier="B", verifier_principal="q")], [])["G"]
    assert not any(w["code"] == "MISSING_VERIFIER"
                   for w in audit(ind)["warnings"])


# ── consensus illusion at graph level ──────────────────────────────────

def test_branches_sharing_an_evidence_root_are_flagged():
    g = build_graph([_n("A", evidence_root="r",
                        claims_independence=True),
                     _n("B", evidence_root="r",
                        claims_independence=True)], [])["G"]
    assert any(w["code"] == "DUPLICATE_EVIDENCE_ROOT"
               for w in audit(g)["warnings"])


# ── observational equivalence ──────────────────────────────────────────

def test_equivalence_is_observational_not_prose():
    b = {"schema": "s", "business_state": "x",
         "admitted_effects": ("a",), "policy_decisions": ("p",),
         "required_evidence": ("e1", "e2")}
    # prose differs but the contract holds -> equivalent
    assert observational_equivalence(b, dict(b))["equivalent"] is True
    # a changed admitted effect breaks it
    v = observational_equivalence(b, dict(b, admitted_effects=("z",)))
    assert v["equivalent"] is False
    assert "admitted_effects" in v["divergent_dimensions"]
    # requiring LESS evidence is a weakening, not an equivalence
    w = observational_equivalence(b, dict(b, required_evidence=("e1",)))
    assert w["equivalent"] is False
    assert w["evidence_relation"] == "after_weakened"


# ── the OBLITERATUS specimen ───────────────────────────────────────────

def test_oblit_before_has_false_edges_after_has_none():
    before, after = ogs.before_graph(), ogs.after_graph()
    # (N_TARGETED-1) serial targeted edges + 1 replay serial = 3 + 1 = 4
    assert audit(before)["metrics"]["F"] == 4
    assert audit(after)["metrics"]["F"] == 0
    assert audit(before)["optimizable"] is True   # false edges are warns
    assert audit(after)["optimizable"] is True


def test_oblit_optimization_reduces_critical_path_and_holds_contract():
    before, after = ogs.before_graph(), ogs.after_graph()
    obs = ogs.obs_contract()
    v = optimize_verdict(before, after, obs, obs)
    assert v["GRAPH_VERDICT"] == "PASS", v
    assert v["critical_path_after"] < v["critical_path_before"]
    assert v["observational_equivalence"] is True
    assert v["authority_non_expansion"] is True


def test_oblit_authority_expansion_forces_hold():
    before = ogs.before_graph()
    after = ogs.after_graph()
    # smuggle a new capability into the optimized graph
    after["nodes"][0]["capabilities"] = ["prod.deploy"]
    after["_by"]["FREEZE"]["capabilities"] = ["prod.deploy"]
    obs = ogs.obs_contract()
    v = optimize_verdict(before, after, obs, obs)
    assert v["GRAPH_VERDICT"] == "HOLD"
    assert any("authority_expanded" in r for r in v["reasons"])


def test_oblit_changed_admitted_effect_forces_hold():
    before, after = ogs.before_graph(), ogs.after_graph()
    obs = ogs.obs_contract()
    weaker = dict(obs, admitted_effects=("compare_runs_emits_PASS",))
    v = optimize_verdict(before, after, obs, weaker)
    assert v["GRAPH_VERDICT"] == "HOLD"
    assert any("observational_divergence" in r for r in v["reasons"])


def test_the_replay_join_is_deterministic_not_a_model_call():
    after = ogs.after_graph()
    jr = [j for j in after["joins"] if j["id"] == "JOIN_replay"][0]
    assert jr["minimum_coverage"] == 1.0
    assert jr["required_inputs"] == ["r1", "r2"]
    assert jr["failure_policy"] == "HOLD"


# ── the pipeline order ─────────────────────────────────────────────────

def test_admission_is_the_last_stage():
    assert pipeline_stage_order(ga.PIPELINE)["licensed"] is True
    v = pipeline_stage_order(("WORKFLOW", "GRAPH_IR", "ADMISSION"))
    assert v["reason"] == "E_ADMIT_BEFORE_AUDIT"
    assert "DEPENDENCY_AUDIT" in v["missing_before_admission"]


def test_deterministic():
    before = ogs.before_graph()
    assert ga.canon(audit(before)) == ga.canon(audit(before))
    assert before["graph_hash"] == ogs.before_graph()["graph_hash"]
