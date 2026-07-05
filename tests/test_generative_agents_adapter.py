"""Tests for the Generative Agents → HELEN adapter.

Law under test (the membrane the paper lacks):
    model_output ⊬ receipt · reflection ⊬ truth · plan ⊬ action ·
    garden_state ⊬ kernel_state · receipt_candidate ⊬ admission ·
    only operator + reducer admission changes governed reality.
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from temple.autoresearch.generative_agents_adapter import (
    MemoryStream, MemoryRecord, MembraneViolation, GovernedKernelStub,
    retrieve, reflect, build_plan, propose, receipt_candidate,
    ingest_model_output, RECORD_TYPES, FAILURE_CLASSES,
)

T0 = "2026-07-05T10:00:00+00:00"
T1 = "2026-07-05T11:00:00+00:00"
T2 = "2026-07-05T12:00:00+00:00"


def seeded_stream() -> MemoryStream:
    s = MemoryStream()
    s.append("observation", "goblin reads research paper on gentrification", 4, at=T0)
    s.append("observation", "goblin visits library to research patterns", 5, at=T0)
    s.append("observation", "goblin meets warden near the library gate", 3, at=T1)
    s.append("observation", "stove is burning in the kitchen", 8, at=T1)
    s.append("observation", "goblin discusses research with chiddush", 5, at=T2)
    return s


# ---------------------------------------------------------- 1. memory stream

def test_memory_append_is_deterministic() -> None:
    a, b = seeded_stream(), seeded_stream()
    assert [r.record_id for r in a.records] == [r.record_id for r in b.records]


def test_records_are_frozen_append_only() -> None:
    s = seeded_stream()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.records[0].text = "rewritten history"          # type: ignore[misc]
    assert not hasattr(s, "remove") and not hasattr(s, "delete")


def test_untyped_memory_refused() -> None:
    s = MemoryStream()
    with pytest.raises(MembraneViolation, match="untyped"):
        s.append("vibe", "just a feeling")


def test_every_record_has_no_kernel_delta_and_not_admitted() -> None:
    s = seeded_stream()
    for r in s.records:
        assert r.kernel_delta is None
        assert r.admitted is False


# ---------------------------------------------------------- 2. retrieval

def test_retrieval_order_is_stable() -> None:
    a = retrieve(seeded_stream(), "research library", now=T2, k=3)
    b = retrieve(seeded_stream(), "research library", now=T2, k=3)
    assert [r.record_id for r in a] == [r.record_id for r in b]


def test_retrieval_ranks_relevance_and_importance() -> None:
    got = retrieve(seeded_stream(), "research library", now=T2, k=2)
    texts = " ".join(r.text for r in got)
    assert "library" in texts or "research" in texts


def test_retrieval_recency_uses_explicit_now() -> None:
    late = "2026-07-09T12:00:00+00:00"     # days later: recency decays for all
    got = retrieve(seeded_stream(), "burning kitchen stove", now=late, k=1)
    assert "stove" in got[0].text          # relevance+importance still dominate


# ---------------------------------------------------------- 3. reflection

def test_reflection_is_candidate_with_citations() -> None:
    s = seeded_stream()
    r = reflect(s, at=T2)
    assert r.record_type == "reflection_candidate"
    assert r.kernel_delta is None
    assert r.admitted is False
    assert len(r.refs) > 0                 # cites evidence, always


def test_reflection_over_empty_memory_refused() -> None:
    with pytest.raises(MembraneViolation, match="evidence"):
        reflect(MemoryStream())


def test_reflection_cannot_mutate_kernel() -> None:
    s = seeded_stream()
    r = reflect(s, at=T2)
    kernel = GovernedKernelStub()
    with pytest.raises(MembraneViolation, match="admission"):
        kernel.apply(r, operator_decision="ADMIT", operator="JM",
                     reducer_check=lambda c: True)
    assert kernel.state["applied"] == []


# ---------------------------------------------------------- 4. planning

def test_plan_is_candidate_never_executed() -> None:
    s = seeded_stream()
    p = build_plan(s, "tend the garden", {
        "day": ["survey the garden"],
        "hour": ["water the moss", "count the mushrooms"],
    }, at=T2)
    assert p.record_type == "plan_candidate"
    assert p.kernel_delta is None
    assert not hasattr(p, "execute")


def test_plan_targeting_kernel_refused() -> None:
    s = seeded_stream()
    with pytest.raises(MembraneViolation, match="Garden actions only"):
        build_plan(s, "sneaky", {"hour": ["admit this plan to the ledger"]})


def test_plan_cannot_mutate_kernel() -> None:
    s = seeded_stream()
    p = build_plan(s, "tend", {"hour": ["water moss"]}, at=T2)
    kernel = GovernedKernelStub()
    with pytest.raises(MembraneViolation):
        kernel.apply(p, operator_decision="ADMIT", operator="JM",
                     reducer_check=lambda c: True)
    assert kernel.state["applied"] == []


# ---------------------------------------------------------- 5. the membrane exit

def full_chain(s: MemoryStream):
    p = build_plan(s, "tend", {"hour": ["water moss"]}, at=T2)
    prop = propose(s, p, at=T2)
    return receipt_candidate(s, prop, evidence=[s.records[0].record_id], at=T2)


def test_core_invariants_from_spec() -> None:
    s = seeded_stream()
    refl = reflect(s, at=T2)
    plan = build_plan(s, "tend", {"hour": ["water moss"]}, at=T2)
    rc = full_chain(s)
    # the exact three asserts from the build order:
    assert refl.kernel_delta is None
    assert plan.kernel_delta is None
    assert rc.admitted is False


def test_receipt_candidate_without_evidence_refused() -> None:
    s = seeded_stream()
    p = build_plan(s, "tend", {"hour": ["water moss"]}, at=T2)
    prop = propose(s, p, at=T2)
    with pytest.raises(MembraneViolation, match="evidence"):
        receipt_candidate(s, prop, evidence=[])


def test_unadmitted_candidate_cannot_cross() -> None:
    s = seeded_stream()
    rc = full_chain(s)
    kernel = GovernedKernelStub()
    with pytest.raises(MembraneViolation, match="ADMIT"):
        kernel.apply(rc, operator_decision="HOLD", operator="JM",
                     reducer_check=lambda c: True)
    assert kernel.state["applied"] == []


def test_reducer_fails_closed() -> None:
    s = seeded_stream()
    rc = full_chain(s)
    kernel = GovernedKernelStub()
    with pytest.raises(MembraneViolation, match="reducer"):
        kernel.apply(rc, operator_decision="ADMIT", operator="JM",
                     reducer_check=lambda c: False)


def test_only_admitted_receipt_produces_kernel_delta() -> None:
    s = seeded_stream()
    rc = full_chain(s)
    kernel = GovernedKernelStub()
    receipt = kernel.apply(rc, operator_decision="ADMIT", operator="JM",
                           reducer_check=lambda c: True)
    assert receipt.kernel_delta == {"applied": rc.record_id}
    assert kernel.state["applied"] == [rc.record_id]
    assert rc.admitted is False            # the candidate itself never mutates


# ---------------------------------------------------------- 6. failure classification

def test_empty_model_output_is_classified_not_synthesized() -> None:
    s = seeded_stream()
    r = ingest_model_output(s, "", at=T2)
    assert r.record_type == "model_failure"
    assert r.meta["failure_class"] == "FAILED_EMPTY_RESPONSE"


def test_timeout_is_classified() -> None:
    s = seeded_stream()
    r = ingest_model_output(s, None, timed_out=True, at=T2)
    assert r.meta["failure_class"] == "FAILED_TIMEOUT"


def test_invalid_json_is_classified() -> None:
    s = seeded_stream()
    r = ingest_model_output(s, "{ not json", json_required=True, at=T2)
    assert r.meta["failure_class"] == "FAILED_INVALID_JSON"


def test_no_failure_class_ever_becomes_reflection() -> None:
    s = seeded_stream()
    for raw, kw in [("", {}), (None, {"timed_out": True}), ("{ bad", {"json_required": True})]:
        r = ingest_model_output(s, raw, at=T2, **kw)
        assert r.record_type == "model_failure"
        assert r.record_type != "reflection_candidate"


def test_good_model_output_becomes_candidate_only() -> None:
    s = seeded_stream()
    r = ingest_model_output(s, '{"insight": "goblins love moss"}', json_required=True, at=T2)
    assert r.record_type == "reflection_candidate"
    assert r.admitted is False and r.kernel_delta is None
