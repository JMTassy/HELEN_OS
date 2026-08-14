"""vNext falsified: mythology never crosses the boundary; the control
plane holds no customer data; business logic may not name a vendor; no
ambient authority; the LLM cannot advance a workflow; a vector index
is never truth; tenants do not overlap; one package per three
profiles; and worker expansion waits for the foundation.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vnext_architecture as vn
from vnext_architecture import (
    advance_workflow,
    authoritative_read,
    capability_grant,
    control_plane_contents,
    deployment_identity,
    deployment_profile,
    external_surface,
    governance_scope,
    inference_call,
    release_artifact,
    roadmap_gate,
    tenant_isolation,
    worker_contract,
)


# ── the boundary ───────────────────────────────────────────────────────

def test_mythology_on_an_external_surface_is_a_leak():
    v = external_surface(("HAL", "workflow", "SOPHIA"))
    assert v["ok"] is False
    assert v["reason"] == "E_MYTHOLOGY_ON_EXTERNAL_SURFACE"
    assert v["leaked"] == ("HAL", "SOPHIA")
    assert v["translations"]["HAL"] == "Policy / Admission Engine"


def test_enterprise_vocabulary_passes_the_boundary():
    v = external_surface(("application", "audit log", "workflow"))
    assert v["ok"] is True


def test_every_mythology_name_has_a_translation():
    for name in vn.MYTHOLOGY:
        assert vn.TRANSLATION[name]
    assert vn.TRANSLATION["Goblins"] == "Ephemeral Worker Runtime"
    assert vn.TRANSLATION["Ledger"] == "Append-only Audit Store"


# ── control plane ──────────────────────────────────────────────────────

def test_customer_data_in_the_control_plane_is_refused():
    v = control_plane_contents(("software_versions", "embeddings",
                                "client_secrets"))
    assert v["ok"] is False
    assert v["reason"] == "E_CUSTOMER_DATA_IN_CONTROL_PLANE"
    assert v["sensitive_found"] == ("client_secrets", "embeddings")


def test_the_lawful_control_plane_distributes_and_holds_nothing():
    v = control_plane_contents(vn.CONTROL_PLANE_ALLOWED)
    assert v["ok"] is True and v["sensitive_found"] == ()


# ── the gateway ────────────────────────────────────────────────────────

def test_naming_a_vendor_in_business_logic_is_refused():
    v = inference_call({"capability": "reasoning"}, vendor_named="Claude")
    assert v["ok"] is False
    assert v["reason"] == "E_VENDOR_IN_BUSINESS_LOGIC"


def test_inference_is_addressed_by_the_four_axes():
    partial = inference_call({"capability": "reasoning"}, None)
    assert partial["reason"] == "E_UNADDRESSED_INFERENCE"
    assert "jurisdiction" in partial["missing"]
    full = inference_call({"capability": "reasoning",
                           "classification": "confidential",
                           "latency": "interactive",
                           "jurisdiction": "EU"}, None)
    assert full["ok"] is True and full["routed_by"] == "gateway_policy"


# ── capabilities ───────────────────────────────────────────────────────

def test_ambient_authority_is_refused():
    assert capability_grant("app", ("ALL",))["reason"] == \
        "E_AMBIENT_AUTHORITY"
    assert capability_grant("app", ("crm.read", "*"))["reason"] == \
        "E_AMBIENT_AUTHORITY"


def test_capabilities_are_declared_dotted_scopes():
    assert capability_grant("app", ("write",))["reason"] == \
        "E_UNDECLARED_CAPABILITY"
    v = capability_grant("app", ("crm.read", "email.send"))
    assert v["granted"] is True
    assert v["capabilities"] == ("crm.read", "email.send")


# ── state laws ─────────────────────────────────────────────────────────

def test_the_llm_cannot_advance_a_workflow():
    v = advance_workflow("CLASSIFY", "EXTRACT", by="llm")
    assert v["advanced"] is False
    assert v["reason"] == "E_LLM_IS_NOT_STATE_AUTHORITY"


def test_only_the_workflow_engine_advances_state():
    assert advance_workflow("CLASSIFY", "EXTRACT",
                            by="workflow_engine")["advanced"] is True
    assert advance_workflow("A", "B", by="operator")["reason"] == \
        "E_UNKNOWN_STATE_AUTHORITY"


def test_a_vector_index_is_never_institutional_truth():
    v = authoritative_read("vector_index")
    assert v["ok"] is False and v["grade"] == "DERIVED"
    assert v["reason"] == "E_DERIVED_IS_NOT_AUTHORITATIVE"
    assert authoritative_read("llm_context")["grade"] == "EPHEMERAL"
    assert authoritative_read("postgresql")["ok"] is True


# ── tenancy and topology ───────────────────────────────────────────────

def test_tenants_may_share_only_control_plane_artifacts():
    v = tenant_isolation(frozenset({"db_a", "release_v3"}),
                         frozenset({"db_a", "release_v3"}),
                         shared_control_artifacts=frozenset(
                             {"release_v3"}))
    assert v["isolated"] is False
    assert v["unlawful_overlap"] == ("db_a",)
    assert v["lawfully_shared"] == ("release_v3",)


def test_disjoint_tenants_are_isolated():
    v = tenant_isolation(frozenset({"db_a"}), frozenset({"db_b"}),
                         frozenset())
    assert v["isolated"] is True


def test_one_package_across_three_profiles():
    for p in ("managed_dedicated", "byoc", "sovereign_restricted"):
        assert deployment_profile(p, "sha:x", "sha:x")["ok"] is True
    fork = deployment_profile("byoc", "sha:forked", "sha:x")
    assert fork["reason"] == "E_TOPOLOGY_LEAKED_INTO_SEMANTICS"
    assert deployment_profile("vps", "s", "s")["reason"] == \
        "E_UNKNOWN_PROFILE"


# ── release identity ───────────────────────────────────────────────────

def test_a_release_is_the_nine_tuple_or_incomplete():
    assert release_artifact(frozenset(vn.RELEASE_ARTIFACT))[
        "complete"] is True
    v = release_artifact(frozenset({"source_ref"}))
    assert v["reason"] == "E_INCOMPLETE_RELEASE"
    assert "sbom" in v["missing"]


def test_a_deployment_answers_the_six_questions():
    full = {q: "x" for q in vn.DEPLOYMENT_QUESTIONS}
    assert deployment_identity(full)["identified"] is True
    partial = deployment_identity({"commit": "abc"})
    assert partial["reason"] == "E_UNIDENTIFIED_DEPLOYMENT"
    assert "model_policy_version" in partial["missing"]


# ── the transversal wrap ───────────────────────────────────────────────

def test_governing_only_ai_actions_is_the_dangerous_reading():
    v = governance_scope(frozenset({"ai_call"}))
    assert v["transversal"] is False
    assert v["reason"] == "E_ONLY_AI_GOVERNED"


def test_partial_coverage_is_named_and_full_coverage_passes():
    part = governance_scope(frozenset({"ai_call", "application"}))
    assert part["reason"] == "E_PARTIAL_GOVERNANCE"
    assert governance_scope(frozenset(vn.GOVERNED_SURFACES))[
        "transversal"] is True


# ── workers and the roadmap gate ───────────────────────────────────────

def test_a_worker_without_its_contract_is_refused():
    v = worker_contract(frozenset({"input"}), frozenset({"result"}))
    assert v["ok"] is False and v["reason"] == "E_UNCONTRACTED_WORKER"
    assert "budget" in v["missing_inputs"]
    assert "evidence" in v["missing_outputs"]


def test_no_worker_is_sovereign_even_when_fully_contracted():
    v = worker_contract(frozenset(vn.WORKER_INPUT),
                        frozenset(vn.WORKER_OUTPUT))
    assert v["ok"] is True
    assert v["sovereign"] is False
    assert v["owns_persistent_truth"] is False


def test_worker_expansion_waits_for_all_thirteen_foundations():
    v = roadmap_gate(frozenset({"tenant_isolation"}),
                     "autonomous_worker_expansion")
    assert v["licensed"] is False
    assert v["reason"] == "E_FOUNDATION_INCOMPLETE"
    assert len(v["missing_foundation"]) == 12
    done = roadmap_gate(frozenset(vn.FOUNDATION),
                        "autonomous_worker_expansion")
    assert done["licensed"] is True


def test_the_five_verb_law_is_the_module_constant():
    assert vn.LAW == ("AI proposes. Software governs. Infrastructure "
                      "isolates. Audit proves. Contracts guarantee.")


def test_deterministic():
    assert vn.canon(governance_scope(frozenset(vn.GOVERNED_SURFACES))) \
        == vn.canon(governance_scope(frozenset(vn.GOVERNED_SURFACES)))
