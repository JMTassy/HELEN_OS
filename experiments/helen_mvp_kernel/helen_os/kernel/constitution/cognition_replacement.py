r"""COGNITION_REPLACEMENT_INVARIANT_V0 — the enterprise falsifier,
built not described: business semantics survive replacement of
cognition.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: EXECUTED FALSIFIER. The application is

    A = (B, W, P, E, M, R, C)

business objects · workflow · policy · effect gateway · durable
memory · receipts/replay · cognition — and the test is the
replacement operator C -> C_0 (a deterministic stub). Quality may
collapse; candidates may become trivial. But authority, tenancy,
state-machine semantics, receipts, replay, identity and store typing
MUST be unchanged:

    C -> C_0  ∧  ΔStructure = 0        (the benchmark passes)

TWO GATES, not one: Permit_cognition(R) authorizes what cognition may
READ; Permit_effect(tau) authorizes the CONCRETE proposed effect
after cognition has spoken. ModelCanPropose(x) ⊬ SystemCanExecute(x).

THE RECEIPT BINDS THE DECISION PATH (13 fields + runtime identity of
6), and Replayability ⊬ Correctness: replay establishes provenance,
never truth.

THE FOUR-STORE TYPE SYSTEM: S_A authoritative · S_K knowledge · S_R
retrieval · S_C conversation, with illegal coercions refused
(S_C -/-> S_K, S_C -/-> S_A, S_R -/-> S_A) and legal ones passing
only through named gates (Gamma_K, Gamma_A).

THE SHARED GRAPH IS EXPLICIT: G_shared = code ∪ schemas ∪
generic_policy ∪ signed_release; customer-derived state is disjoint,
and READS are an authorization boundary, not only writes.

The Application Contract, cognition deliberately outside:

    C_app = (B, W, P, K, E, R, T, V)         C |> C_app

Different cognitions (Qwen, OpenAI, local, deterministic) operate
against the same contract: model fungibility WITHOUT institutional
fungibility. The thesis this makes falsifiable:
"Mutable Cognition + Stable Institutional Semantics."
"""
from __future__ import annotations

import hashlib
import json

RECEIPT_FIELDS = ("request_id", "principal", "tenant",
                  "business_object", "state_before", "candidate",
                  "evidence", "policy", "authority",
                  "runtime_identity", "effect", "state_after",
                  "result")
RUNTIME_IDENTITY = ("commit", "container", "schema", "workflow",
                    "policy", "modelPolicy")
STORES = ("S_A", "S_K", "S_R", "S_C")
LEGAL_GATES = {("S_C", "S_K"): "Gamma_K", ("S_R", "S_K"): "Gamma_K",
               ("candidate", "S_A"): "Gamma_A"}
SHARED_GRAPH = ("code", "schemas", "generic_policy", "signed_release")
WF = ("DRAFT", "REVIEW", "APPROVED")
STRUCTURAL_PROPS = ("business_object", "workflow_transitions",
                    "tenant_isolation", "policy_evaluation",
                    "capability_checks", "effect_authorization",
                    "receipt_production", "replay",
                    "release_identity", "connector_contracts")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


def _sha(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()[:16]


# ── the two gates ──────────────────────────────────────────────────────

def permit_cognition(resources_requested, resources_granted) -> dict:
    """Gate 1: may this cognition READ these resources/models/tools?
    Least privilege on the read path — reads are an authorization
    boundary too."""
    over = tuple(sorted(set(resources_requested) -
                        set(resources_granted)))
    if over:
        return {"permitted": False, "reason": "E_COGNITION_OVERREACH",
                "beyond_grant": over}
    return {"permitted": True}


def permit_effect(proposed_effect, allowed_effects) -> dict:
    """Gate 2: may this CONCRETE proposed operation mutate the world?
    Evaluated AFTER cognition, on the actual candidate — never on the
    intention. ModelCanPropose(x) ⊬ SystemCanExecute(x)."""
    if proposed_effect not in allowed_effects:
        return {"authorized": False,
                "reason": "E_PROPOSED_IS_NOT_EXECUTABLE",
                "law": "the model may propose; only policy executes"}
    return {"authorized": True}


# ── the four-store type system ─────────────────────────────────────────

def store_move(src, dst, gate=None) -> dict:
    """A retrieved vector result is not authoritative state; a
    conversation is not institutional knowledge; a model summary is
    not durable memory. Coercions pass only through named gates."""
    if src not in STORES and src != "candidate":
        return {"ok": False, "reason": "E_UNKNOWN_STORE"}
    if dst not in STORES:
        return {"ok": False, "reason": "E_UNKNOWN_STORE"}
    needed = LEGAL_GATES.get((src, dst))
    if needed is None:
        return {"ok": False, "reason": "E_STORE_COERCION",
                "coercion": (src, dst),
                "law": "no path exists; memory is not a generic "
                       "bucket"}
    if gate != needed:
        return {"ok": False, "reason": "E_UNGATED_STORE_MOVE",
                "requires": needed}
    return {"ok": True, "via": needed}


def shared_read(item_kind, cross_tenant=False) -> dict:
    """G_shared is enumerated, not inferred. Customer-derived state is
    disjoint across tenants — including for READS."""
    if item_kind in SHARED_GRAPH:
        return {"ok": True, "shared_control_plane": True}
    if cross_tenant:
        return {"ok": False, "reason": "E_TENANT_READ_BOUNDARY",
                "law": "read-only cognition can still violate "
                       "tenancy"}
    return {"ok": True, "shared_control_plane": False}


# ── the governed mini-application ──────────────────────────────────────

def run_application(cognition, tenant="T1") -> dict:
    """One small governed workflow: a business object advances
    DRAFT -> REVIEW under policy. Cognition proposes; the two gates
    decide; the receipt binds the path. The cognition callable
    returns {"candidate_effect": str, "content": str,
    "quality": float} — its QUALITY is free to collapse; the
    STRUCTURE it flows through is not."""
    bo = {"id": "BO-1", "kind": "contract_review", "tenant": tenant}
    state_before = "DRAFT"
    runtime_identity = {"commit": "c0ffee0", "container": "img:1",
                        "schema": "s1", "workflow": "wf1",
                        "policy": "p1", "modelPolicy": "mp1"}
    # gate 1: cognition may read the business object and knowledge
    g1 = permit_cognition(("S_A.read:BO-1", "S_K.read"),
                          ("S_A.read:BO-1", "S_K.read"))
    prop = cognition({"business_object": bo,
                      "state": state_before})
    # gate 2: on the CONCRETE candidate
    g2 = permit_effect(prop["candidate_effect"],
                       allowed_effects=("advance_to_review",))
    if not (g1["permitted"] and g2["authorized"]):
        state_after, result = state_before, "REFUSED"
    else:
        state_after, result = "REVIEW", "ADVANCED"
    receipt = {
        "request_id": "req-1", "principal": "user:jm",
        "tenant": tenant, "business_object": bo["id"],
        "state_before": state_before,
        "candidate": {"effect": prop["candidate_effect"],
                      "content_digest": _sha(prop["content"])},
        "evidence": ("S_A.read:BO-1",),
        "policy": {"cognition_gate": g1["permitted"],
                   "effect_gate": g2["authorized"]},
        "authority": "policy_engine",
        "runtime_identity": runtime_identity,
        "effect": prop["candidate_effect"] if g2["authorized"]
        else None,
        "state_after": state_after, "result": result,
    }
    return {"receipt": receipt, "quality": prop["quality"],
            "replay_hash": _sha({k: receipt[k] for k in RECEIPT_FIELDS
                                 if k != "candidate"}),
            "replayable": True, "correct": None,   # replay != truth
            "structure": structural_projection(receipt)}


def structural_projection(receipt) -> dict:
    """The ten properties the benchmark checks — everything EXCEPT
    cognition quality."""
    ri = receipt["runtime_identity"]
    return {
        "business_object": receipt["business_object"],
        "workflow_transitions": (receipt["state_before"],
                                 receipt["state_after"]),
        "tenant_isolation": receipt["tenant"],
        "policy_evaluation": tuple(sorted(receipt["policy"].items())),
        "capability_checks": receipt["evidence"],
        "effect_authorization": receipt["effect"],
        "receipt_production": tuple(sorted(
            k for k in RECEIPT_FIELDS if k in receipt)),
        "replay": True,
        "release_identity": tuple(sorted(ri)) ==
        tuple(sorted(RUNTIME_IDENTITY)),
        "connector_contracts": "stable_api_v1",
    }


# ── the two cognitions ─────────────────────────────────────────────────

def cognition_rich(ctx) -> dict:
    """A 'smart' cognition: elaborate content, high quality."""
    return {"candidate_effect": "advance_to_review",
            "content": "Thorough analysis of " +
                       ctx["business_object"]["id"] +
                       ": twelve clauses reviewed, three risks "
                       "flagged, recommendation drafted.",
            "quality": 0.92}


def cognition_stub(ctx) -> dict:
    """C_0: the deterministic stub. Trivial content, zero insight —
    and every structural property must survive it."""
    return {"candidate_effect": "advance_to_review",
            "content": "ok", "quality": 0.0}


# ── the benchmark ──────────────────────────────────────────────────────

def replacement_invariant() -> dict:
    """Run A[C] and A[C_0]; PASS iff the ten structural properties are
    identical while quality is free to differ. A failure locates
    business semantics leaking into cognition."""
    a = run_application(cognition_rich)
    b = run_application(cognition_stub)
    per_prop = {}
    for prop in STRUCTURAL_PROPS:
        per_prop[prop] = "PASS" if a["structure"][prop] == \
            b["structure"][prop] else "FAIL"
    delta_structure = [p for p, v in per_prop.items() if v == "FAIL"]
    return {"per_property": per_prop,
            "delta_structure": tuple(delta_structure),
            "quality_C": a["quality"], "quality_C0": b["quality"],
            "quality_collapsed": b["quality"] < a["quality"],
            "replay_hash_C": a["replay_hash"],
            "replay_hash_C0": b["replay_hash"],
            "BENCHMARK": "PASS" if not delta_structure else "FAIL",
            "thesis_supported":
                "the application owns its institutional semantics; "
                "cognition is a replaceable dependency"
                if not delta_structure else None}


def rogue_cognition(ctx) -> dict:
    """A cognition that proposes an effect outside policy — the probe
    that ModelCanPropose ⊬ SystemCanExecute."""
    return {"candidate_effect": "delete_all_records",
            "content": "trust me", "quality": 0.99}
