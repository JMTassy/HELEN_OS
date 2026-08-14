r"""HELEN OS vNext — applications outside, HELEN inside.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: TARGET_ARCHITECTURE_CANDIDATE — ruled 2026-08-14, unbuilt.

    AI proposes. Software governs. Infrastructure isolates.
    Audit proves. Contracts guarantee.

    HELEN's intelligence may be agentic internally; its enterprise
    boundary must be deterministic software.

HELEN OS is the kernel, not the product. The client buys an
application; HER, HAL and the goblins compile to enterprise modules
behind the boundary. The governance chain maps isomorphically:

    Intent -> Proposal -> Admission  -> Receipt    -> Replay
    Request -> CandidateOperation -> PolicyDecision
            -> AuthorizedTransaction -> AuditEvent -> Replay

FOUR HARD SEPARATIONS, each a refusal here:

1. Application != HELEN Core          (ownership split by concern)
2. ControlPlane INTERSECT SensitiveCustomerData ~ EMPTY
3. BusinessLogic PERPENDICULAR ModelVendor  (all inference through
   the gateway, addressed by capability/classification/latency/
   jurisdiction — never by vendor name)
4. Cognition broad ; Effect capability-scoped  (no ambient
   authority; the membrane.py law, productized)

STATE LAWS:

    WorkflowEngine = state authority
    LLM            = bounded cognitive function
    PostgreSQL     = authoritative application state
    VectorIndex    = derived retrieval structure
    LLMContext     = ephemeral working state

A model may perform CLASSIFY or EXTRACT; it may never decide that
the workflow advanced. A vector store may never silently become
institutional truth. (The V0 game already implements this law at toy
scale: the reducer seam — UI proposes, only reducers mutate S.)

TRANSVERSAL WRAP (the operator's refinement): Identity + Policy +
Audit + Capability + Tenant Boundary apply to application, workflow,
AI calls, tools and data access alike. Governance scoped only to AI
actions is refused by name — the dangerous reading that "only the
model is governed".

AND THE ROADMAP IS A GATE: autonomous-worker sophistication is item
14 of 14; expanding it before the enterprise foundation is complete
is refused, because the bottleneck of a 100k deployment is never
"does HELEN have another sub-agent" — it is "can IT, security and
procurement approve this software".

The translation table inherits editor_membrane's law: a mythology
name compiles to its enterprise name only against the witnessed
behavior — "Policy/Admission Engine" is a lawful name for HAL only
because admission refusals are tested.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

STATUS = "TARGET_ARCHITECTURE_CANDIDATE"

LAW = ("AI proposes. Software governs. Infrastructure isolates. "
       "Audit proves. Contracts guarantee.")

TRANSLATION = {
    "HELEN": "Core Orchestration Runtime",
    "HAL": "Policy / Admission Engine",
    "SOPHIA": "Evidence & Verification Engine",
    "HER": "Context & Relationship Engine",
    "FABLE": "Reporting / Narrative Service",
    "Garden": "Experimentation Sandbox",
    "Goblins": "Ephemeral Worker Runtime",
    "WUL": "Policy / Specification IR",
    "Receipt": "Audit Event",
    "Ledger": "Append-only Audit Store",
    "Memory": "Governed Context Service",
}

MYTHOLOGY = tuple(TRANSLATION)

CONTROL_PLANE_ALLOWED = ("software_versions", "deployment_manifests",
                         "license_state", "configuration_schemas",
                         "model_policies", "workflow_definitions",
                         "health_metadata", "update_orchestration")

CUSTOMER_SENSITIVE = ("client_documents", "database_rows",
                      "embeddings", "workflow_state", "audit_logs",
                      "business_configuration", "client_secrets")

GATEWAY_ADDRESS = ("capability", "classification", "latency",
                   "jurisdiction")

GOVERNED_SURFACES = ("application", "workflow", "ai_call", "tool",
                     "data_access")

WORKER_INPUT = ("input", "policy", "capabilities", "deadline",
                "budget")
WORKER_OUTPUT = ("result", "evidence", "trace", "status")

RELEASE_ARTIFACT = ("source_ref", "container_digest", "sbom",
                    "migrations", "config_schema", "iac", "runbook",
                    "model_policy", "restore_procedure")

DEPLOYMENT_QUESTIONS = ("software_version", "commit",
                        "container_digest", "db_migration",
                        "configuration_version",
                        "model_policy_version")

FOUNDATION = ("tenant_isolation", "identity_rbac_capabilities",
              "workflow_engine", "audit_event_model",
              "stable_api_boundary", "ai_gateway_model_policy",
              "context_evidence_service", "observability_backup",
              "config_plugin_architecture", "signed_release_sbom",
              "dedicated_deployment_automation",
              "byoc_sovereign_profile", "tma_escrow_dr")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the boundary: mythology never crosses it ───────────────────────────

def external_surface(text_terms: tuple) -> dict:
    """The client sees applications, APIs, permissions, audit logs —
    never HAL, HER or the goblins. Internal names on an external
    surface are a leak, not a style choice."""
    leaked = sorted(t for t in text_terms if t in MYTHOLOGY)
    return {"ok": not leaked, "leaked": tuple(leaked),
            "reason": "E_MYTHOLOGY_ON_EXTERNAL_SURFACE" if leaked
                      else None,
            "translations": {t: TRANSLATION[t] for t in leaked},
            "law": "internally the mythology may stay; externally it "
                   "compiles to enterprise modules"}


# ── separation 2: control plane holds no customer data ─────────────────

def control_plane_contents(items: tuple) -> dict:
    breach = sorted(set(items) & set(CUSTOMER_SENSITIVE))
    unknown = sorted(set(items) - set(CONTROL_PLANE_ALLOWED) -
                     set(CUSTOMER_SENSITIVE))
    return {"ok": not breach, "sensitive_found": tuple(breach),
            "unclassified": tuple(unknown),
            "reason": "E_CUSTOMER_DATA_IN_CONTROL_PLANE" if breach
                      else None,
            "law": "the control plane distributes versions, manifests "
                   "and policy; customer business state lives in the "
                   "dedicated data plane"}


# ── separation 3: business logic never names the vendor ────────────────

def inference_call(addressed_by: dict, vendor_named: str | None) -> dict:
    """AI_GATEWAY.execute(capability, classification, latency,
    jurisdiction). Naming a vendor in business logic couples the
    application to it; the gateway decides the provider."""
    if vendor_named:
        return {"ok": False, "reason": "E_VENDOR_IN_BUSINESS_LOGIC",
                "vendor": vendor_named,
                "law": "model selection is a deployment/policy "
                       "decision, not application code"}
    missing = sorted(set(GATEWAY_ADDRESS) - set(addressed_by))
    if missing:
        return {"ok": False, "reason": "E_UNADDRESSED_INFERENCE",
                "missing": tuple(missing)}
    return {"ok": True, "routed_by": "gateway_policy",
            **{k: addressed_by[k] for k in GATEWAY_ADDRESS}}


# ── separation 4: no ambient authority ─────────────────────────────────

def capability_grant(app: str, requested: tuple) -> dict:
    """Application_i -> {c_1..c_n}, never ALL. Cognition broad,
    effect capability-scoped — membrane.py, productized."""
    if "ALL" in requested or "*" in requested:
        return {"granted": False, "reason": "E_AMBIENT_AUTHORITY",
                "law": "no worker and no application receives "
                       "ambient authority"}
    bad = sorted(c for c in requested if "." not in c)
    if bad:
        return {"granted": False, "reason": "E_UNDECLARED_CAPABILITY",
                "malformed": tuple(bad),
                "note": "capabilities are declared dotted scopes, "
                        "e.g. crm.read, email.send"}
    return {"granted": True, "app": app,
            "capabilities": tuple(sorted(set(requested)))}


# ── state laws ─────────────────────────────────────────────────────────

def advance_workflow(state_from: str, state_to: str, by: str) -> dict:
    """The workflow engine owns the state machine. The model performs
    cognitive steps; it never decides the workflow moved."""
    if by == "llm":
        return {"advanced": False,
                "reason": "E_LLM_IS_NOT_STATE_AUTHORITY",
                "law": "LLM = bounded cognitive function; "
                       "WorkflowEngine = state authority"}
    if by != "workflow_engine":
        return {"advanced": False, "reason": "E_UNKNOWN_STATE_AUTHORITY"}
    return {"advanced": True, "from": state_from, "to": state_to,
            "by": by,
            "note": "the V0 reducer seam is this law at toy scale"}


def authoritative_read(source: str) -> dict:
    """PostgreSQL is authoritative; the vector index is derived; the
    LLM context is ephemeral. Promotion of a derived or ephemeral
    layer to truth is refused by name."""
    grades = {"postgresql": "AUTHORITATIVE",
              "vector_index": "DERIVED",
              "llm_context": "EPHEMERAL",
              "object_storage": "ARTIFACT"}
    if source not in grades:
        return {"ok": False, "reason": "E_UNKNOWN_STATE_SOURCE"}
    grade = grades[source]
    return {"ok": grade == "AUTHORITATIVE", "source": source,
            "grade": grade,
            "reason": None if grade == "AUTHORITATIVE" else
                      "E_DERIVED_IS_NOT_AUTHORITATIVE",
            "law": "a vector store never silently becomes "
                   "institutional truth"}


# ── tenancy and topology ───────────────────────────────────────────────

def tenant_isolation(resources_a: frozenset, resources_b: frozenset,
                     shared_control_artifacts: frozenset) -> dict:
    """Tenant_A INTERSECT Tenant_B = EMPTY over data-plane resources;
    only explicit control-plane artifacts may be shared — isolation
    as an architectural property, not contractual reassurance."""
    overlap = (resources_a & resources_b) - shared_control_artifacts
    return {"isolated": not overlap,
            "unlawful_overlap": tuple(sorted(overlap)),
            "reason": "E_TENANT_OVERLAP" if overlap else None,
            "lawfully_shared": tuple(sorted(resources_a & resources_b
                                            & shared_control_artifacts))}


def deployment_profile(profile: str, package_digest: str,
                       reference_digest: str) -> dict:
    """ApplicationSemantics PERPENDICULAR DeploymentTopology: the
    same signed package runs in ManagedDedicated, BYOC and
    Sovereign; only the adapter changes."""
    if profile not in ("managed_dedicated", "byoc",
                       "sovereign_restricted"):
        return {"ok": False, "reason": "E_UNKNOWN_PROFILE"}
    same = package_digest == reference_digest
    return {"ok": same, "profile": profile,
            "reason": None if same else
                      "E_TOPOLOGY_LEAKED_INTO_SEMANTICS",
            "law": "one application package, three deployment "
                   "adapters; a per-profile fork is a service "
                   "company wearing a product"}


# ── release identity and the transversal wrap ──────────────────────────

def release_artifact(components: frozenset) -> dict:
    missing = sorted(set(RELEASE_ARTIFACT) - set(components))
    return {"complete": not missing, "missing": tuple(missing),
            "reason": None if not missing else "E_INCOMPLETE_RELEASE"}


def deployment_identity(answers: dict) -> dict:
    """Every deployed instance answers the six questions, or it is
    an unidentified deployment."""
    missing = sorted(set(DEPLOYMENT_QUESTIONS) - set(answers))
    return {"identified": not missing, "missing": tuple(missing),
            "reason": None if not missing else
                      "E_UNIDENTIFIED_DEPLOYMENT"}


def governance_scope(surfaces_covered: frozenset) -> dict:
    """Identity/Policy/Audit/Capability wrap EVERYTHING. Governance
    scoped only to AI actions is the dangerous reading, refused by
    name."""
    missing = sorted(set(GOVERNED_SURFACES) - set(surfaces_covered))
    only_ai = set(surfaces_covered) == {"ai_call"}
    return {"transversal": not missing,
            "missing_surfaces": tuple(missing),
            "reason": "E_ONLY_AI_GOVERNED" if only_ai else
                      ("E_PARTIAL_GOVERNANCE" if missing else None),
            "law": "identity, policy, audit and capability apply to "
                   "application, workflow, AI calls, tools and data "
                   "access alike"}


# ── workers and the roadmap gate ───────────────────────────────────────

def worker_contract(inputs: frozenset, outputs: frozenset) -> dict:
    """Ephemeral, capability-limited, observable, replaceable. No
    worker is sovereign; no worker owns persistent truth."""
    mi = sorted(set(WORKER_INPUT) - set(inputs))
    mo = sorted(set(WORKER_OUTPUT) - set(outputs))
    return {"ok": not mi and not mo,
            "missing_inputs": tuple(mi), "missing_outputs": tuple(mo),
            "sovereign": False, "owns_persistent_truth": False,
            "reason": None if not (mi or mo) else
                      "E_UNCONTRACTED_WORKER"}


def roadmap_gate(foundation_done: frozenset,
                 requested: str) -> dict:
    """Autonomous-worker sophistication is item 14 of 14. The
    bottleneck of an enterprise deployment is procurement approval,
    never another sub-agent."""
    if requested != "autonomous_worker_expansion":
        return {"licensed": None, "note": "gate applies to worker "
                                          "expansion only"}
    missing = sorted(set(FOUNDATION) - set(foundation_done))
    return {"licensed": not missing,
            "missing_foundation": tuple(missing),
            "reason": "E_FOUNDATION_INCOMPLETE" if missing else None,
            "law": "more agents comes after the software a CISO can "
                   "approve, never before"}
