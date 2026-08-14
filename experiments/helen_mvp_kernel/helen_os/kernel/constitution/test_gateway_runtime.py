"""Phase A item 6, adversarially tested: naming a vendor dies at the
gateway; an empty policy intersection refuses and never widens;
"we refuse Anthropic" is a policy edit and the same request re-routes;
confidential data cannot reach an uncleared provider; the meter is the
gateway's; and every response is a non-promotional representation.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gateway_runtime as gw
from gateway_runtime import (
    boot,
    execute,
    gateway_invariant,
    refuse_provider,
    register_provider,
    set_policy,
)

REQ = {"capability": "reasoning", "classification": "confidential",
       "latency": "interactive", "jurisdiction": "EU"}


def _platform():
    s = boot()
    s, _ = register_provider(s, "mistral_eu", ("EU",),
                             "confidential", ("reasoning",),
                             local=False, wire_shape="flat_effort")
    s, _ = register_provider(s, "bedrock_eu", ("EU", "US"),
                             "internal", ("reasoning", "vision"),
                             local=False, wire_shape="nested_reasoning")
    s, _ = register_provider(s, "local_gemma", ("EU", "US", "ANY"),
                             "restricted", ("reasoning",),
                             local=True, wire_shape="enable_thinking")
    s, _ = set_policy(s, "T1", ("mistral_eu", "bedrock_eu",
                                "local_gemma"),
                      external_permitted=True, budget_tokens=1000)
    return s


def _run(s, req=REQ, tokens=100, vendor=None):
    return execute(s, "T1", req, requested_effort="medium",
                   tokens_est=tokens, prompt_digest="sha:p",
                   vendor_named=vendor)


# ── the vendor law at the runtime ──────────────────────────────────────

def test_naming_a_vendor_dies_at_the_gateway():
    _, r = _run(_platform(), vendor="Claude")
    assert r["ok"] is False
    assert r["reason"] == "E_VENDOR_IN_BUSINESS_LOGIC"


def test_all_four_axes_or_no_inference():
    _, r = execute(_platform(), "T1", {"capability": "reasoning"},
                   "medium", 10, "sha:p")
    assert r["reason"] == "E_UNADDRESSED_INFERENCE"
    assert "jurisdiction" in r["missing"]


# ── policy intersection, never widened ─────────────────────────────────

def test_confidential_cannot_reach_an_uncleared_provider():
    """bedrock_eu is cleared only to 'internal': a confidential
    request must not route there even though it matches every other
    axis."""
    s = _platform()
    s, r = _run(s)
    assert r["ok"] is True
    assert r["routed_to"] != "bedrock_eu"


def test_an_empty_intersection_refuses_and_never_widens():
    s = _platform()
    _, r = _run(s, req={**REQ, "jurisdiction": "MARS"})
    assert r["ok"] is False
    assert r["reason"] == "E_NO_LAWFUL_ROUTE"


def test_no_external_llm_routes_to_the_local_model():
    s = _platform()
    s, _ = set_policy(s, "T1", ("mistral_eu", "local_gemma"),
                      external_permitted=False, budget_tokens=1000)
    s, r = _run(s)
    assert r["ok"] is True
    assert r["routed_to"] == "local_gemma"


def test_we_refuse_a_vendor_is_a_policy_edit_and_reroutes():
    s = _platform()
    s, r1 = _run(s)
    first = r1["routed_to"]
    s, ref = refuse_provider(s, "T1", first)
    assert ref["cost"] == "policy_change"
    s, r2 = _run(s)
    assert r2["ok"] is True
    assert r2["routed_to"] != first          # same request, new route


def test_routing_is_deterministic():
    a = _run(_platform())[1]["routed_to"]
    b = _run(_platform())[1]["routed_to"]
    assert a == b


# ── the meter is the gateway's ─────────────────────────────────────────

def test_budget_exhaustion_is_enforced_in_the_data_path():
    s = _platform()
    s, r1 = _run(s, tokens=900)
    assert r1["ok"] is True
    _, r2 = _run(s, tokens=200)
    assert r2["ok"] is False
    assert r2["reason"] == "E_BUDGET_EXHAUSTED"
    assert r2["spent"] == 900


# ── the wire receipt and the response grade ────────────────────────────

def test_the_wire_receipt_records_requested_and_emitted_shapes():
    """The Qwen lesson: what was SENT, not what was meant."""
    s = _platform()
    _, r = _run(s)
    wr = r["wire_receipt"]
    assert wr["requested_effort"] == "medium"
    assert wr["emitted_wire_shape"] in ("flat_effort",
                                        "nested_reasoning",
                                        "enable_thinking")
    assert wr["requested_config_digest"]


def test_every_response_is_a_non_promotional_representation():
    s = _platform()
    _, r = _run(s)
    assert r["response_grade"] == "REPRESENTATION"
    assert r["emits_world_claim"] is False
    assert (r["dP"], r["dA"], r["dE"]) == (0, 0, 0)


def test_the_ledger_carries_digests_never_content():
    s = _platform()
    s, _ = _run(s)
    ev = s["ledger"]["T1"][-1]
    assert ev["prompt_digest"] == "sha:p"
    assert "prompt" not in ev and "response" not in ev


# ── invariant, purity, determinism ─────────────────────────────────────

def test_the_gateway_invariant_is_rederivable_on_real_state():
    s = _platform()
    s, _ = _run(s)
    v = gateway_invariant(s)
    assert v["holds"] is True
    assert v["ghost_providers"] == ()


def test_no_operation_mutates_its_input_state():
    s = _platform()
    frozen = gw.canon(s)
    _run(s)
    refuse_provider(s, "T1", "mistral_eu")
    assert gw.canon(s) == frozen


def test_deterministic_replay():
    assert gw.canon(_platform()) == gw.canon(_platform())
