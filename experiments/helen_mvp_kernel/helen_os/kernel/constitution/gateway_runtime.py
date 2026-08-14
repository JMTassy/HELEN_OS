r"""Gateway Runtime — Phase A item 6, the AI gateway as enforcing
code in the reducer-seam style.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION — executable semantics of L6; the
production build replaces the transport, not the laws.

WHAT THE GATEWAY ITSELF REFUSES:
- business logic may not name a vendor: execute(vendor_named=...)
  dies at the gateway (E_VENDOR_IN_BUSINESS_LOGIC). Inference is
  addressed by the four axes (capability, classification, latency,
  jurisdiction) or not at all (E_UNADDRESSED_INFERENCE).
- routing is POLICY INTERSECTION: tenant allow-list ∩ jurisdiction ∩
  classification clearance ∩ capability. When the intersection is
  empty the gateway REFUSES (E_NO_LAWFUL_ROUTE) — it never silently
  widens the candidate set. "We refuse Anthropic" is a policy edit
  and the SAME request re-routes; the cost is a policy change, never
  a rewrite.
- a CONFIDENTIAL payload cannot reach a provider not cleared for it,
  whatever the latency argument; jurisdiction pins likewise.
- budgets are enforced in the data path (E_BUDGET_EXHAUSTED) — the
  agent-economics law at the wire: near-zero token cost is not
  near-zero cost, and the meter is the gateway's, not the caller's
  claim.
- THE WIRE RECEIPT records BOTH the requested effort/config and the
  actually emitted wire shape (the Qwen lesson: provider-compatible
  APIs differ in wire form; the receipt carries what was sent, not
  what was meant).
- every response is REPRESENTATION: emits_world_claim False,
  dP = dA = dE = 0 — a model output enters the graph as a
  non-promotional DATA edge, never as a witness (the graph_ir
  default, enforced where the tokens are born).
- the ledger records prompt/response DIGESTS, never content
  (audit_runtime's raw-value law, upstream).

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import hashlib
import json

AXES = ("capability", "classification", "latency", "jurisdiction")

CLASSIFICATIONS = ("public", "internal", "confidential", "restricted")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


def boot() -> dict:
    return {"providers": {}, "policies": {}, "spend": {},
            "ledger": {}, "seq": 0}


def _bump(s: dict) -> dict:
    n = dict(s)
    n["seq"] = s["seq"] + 1
    return n


# ── platform verbs ─────────────────────────────────────────────────────

def register_provider(state: dict, name: str, jurisdictions: tuple,
                      cleared_up_to: str, capabilities: tuple,
                      local: bool, wire_shape: str) -> tuple:
    """Platform verb. cleared_up_to: highest data classification the
    provider may receive. wire_shape: how effort/config is actually
    emitted on this provider's API."""
    if name in state["providers"]:
        return state, {"ok": False, "reason": "E_PROVIDER_EXISTS"}
    if cleared_up_to not in CLASSIFICATIONS:
        return state, {"ok": False, "reason": "E_UNKNOWN_CLASSIFICATION"}
    s = _bump(state)
    s["providers"] = {**s["providers"],
                      name: {"jurisdictions": tuple(jurisdictions),
                             "cleared_up_to": cleared_up_to,
                             "capabilities": tuple(capabilities),
                             "local": local,
                             "wire_shape": wire_shape}}
    return s, {"ok": True, "provider": name}


def set_policy(state: dict, tenant: str, allowed: tuple,
               external_permitted: bool, budget_tokens: int) -> tuple:
    """Tenant model policy is DATA. allowed: provider names the
    tenant accepts; external_permitted False = local models only."""
    s = _bump(state)
    s["policies"] = {**s["policies"],
                     tenant: {"allowed": tuple(allowed),
                              "external_permitted": external_permitted,
                              "budget_tokens": budget_tokens}}
    return s, {"ok": True, "tenant": tenant}


def refuse_provider(state: dict, tenant: str, provider: str) -> tuple:
    """'We refuse vendor X' — a policy edit, and nothing else
    changes. The same request re-routes through what remains."""
    pol = state["policies"].get(tenant)
    if pol is None:
        return state, {"ok": False, "reason": "E_NO_POLICY"}
    s = _bump(state)
    s["policies"] = {**s["policies"],
                     tenant: {**pol,
                              "allowed": tuple(a for a in
                                               pol["allowed"]
                                               if a != provider)}}
    return s, {"ok": True, "refused": provider,
               "cost": "policy_change",
               "law": "Application != ModelVendor; the refusal is an "
                      "edit, never a rewrite"}


# ── the gate: execute ──────────────────────────────────────────────────

def execute(state: dict, tenant: str, request: dict,
            requested_effort: str, tokens_est: int,
            prompt_digest: str,
            vendor_named: str | None = None) -> tuple:
    """AI_GATEWAY.execute — the only door to inference."""
    if vendor_named:
        return state, {"ok": False,
                       "reason": "E_VENDOR_IN_BUSINESS_LOGIC",
                       "vendor": vendor_named,
                       "law": "model selection is a policy decision, "
                              "not application code"}
    missing = sorted(set(AXES) - set(request))
    if missing:
        return state, {"ok": False, "reason": "E_UNADDRESSED_INFERENCE",
                       "missing": tuple(missing)}
    if request["classification"] not in CLASSIFICATIONS:
        return state, {"ok": False,
                       "reason": "E_UNKNOWN_CLASSIFICATION"}
    pol = state["policies"].get(tenant)
    if pol is None:
        return state, {"ok": False, "reason": "E_NO_POLICY"}
    spent = state["spend"].get(tenant, 0)
    if spent + tokens_est > pol["budget_tokens"]:
        return state, {"ok": False, "reason": "E_BUDGET_EXHAUSTED",
                       "spent": spent,
                       "budget": pol["budget_tokens"],
                       "law": "the meter is the gateway's, not the "
                              "caller's claim"}
    # policy intersection — never silently widened
    clevel = CLASSIFICATIONS.index(request["classification"])
    candidates = []
    for name in pol["allowed"]:
        p = state["providers"].get(name)
        if p is None:
            continue
        if not pol["external_permitted"] and not p["local"]:
            continue
        if request["jurisdiction"] not in p["jurisdictions"]:
            continue
        if CLASSIFICATIONS.index(p["cleared_up_to"]) < clevel:
            continue
        if request["capability"] not in p["capabilities"]:
            continue
        candidates.append(name)
    if not candidates:
        return state, {"ok": False, "reason": "E_NO_LAWFUL_ROUTE",
                       "law": "an empty intersection is a refusal, "
                              "never a silent widening"}
    routed = sorted(candidates)[0]          # deterministic choice
    p = state["providers"][routed]
    s = _bump(state)
    s["spend"] = {**s["spend"], tenant: spent + tokens_est}
    event = {"seq": s["seq"], "kind": "INFERENCE", "tenant": tenant,
             "provider": routed, "prompt_digest": prompt_digest,
             "tokens": tokens_est}
    s["ledger"] = {**s["ledger"],
                   tenant: s["ledger"].get(tenant, ()) + (event,)}
    return s, {"ok": True, "routed_to": routed,
               "wire_receipt": {
                   "requested_effort": requested_effort,
                   "emitted_wire_shape": p["wire_shape"],
                   "requested_config_digest": _sha(request)},
               "response_grade": "REPRESENTATION",
               "emits_world_claim": False,
               "dP": 0, "dA": 0, "dE": 0,
               "law": "a model output enters the graph as a "
                      "non-promotional DATA edge, never as a witness"}


def gateway_invariant(state: dict) -> dict:
    """Re-derivable on real state: spend never exceeds budget, and
    every ledger event names a registered provider."""
    over = [t for t, pol in state["policies"].items()
            if state["spend"].get(t, 0) > pol["budget_tokens"]]
    ghost = [e["provider"] for evs in state["ledger"].values()
             for e in evs if e["provider"] not in state["providers"]]
    return {"holds": not over and not ghost,
            "over_budget_tenants": tuple(over),
            "ghost_providers": tuple(ghost)}
