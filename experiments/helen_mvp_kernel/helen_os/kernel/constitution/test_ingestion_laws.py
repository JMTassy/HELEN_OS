"""Falsifiers for the six ingestion laws (CH-0812-01..06). All
fixtures generic — the source packet's business content never enters
this published repository.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ingestion_laws as il
from ingestion_laws import (
    capacity_gate,
    decision_signature,
    effective_delta,
    establish_axis,
    improvement_scope,
    preservation_class,
    reconcile_modalities,
    semantic_projection,
)


# ── CH-01 (CORRECTED): the decision signature is partially ordered ─────

def test_a_generated_summary_establishes_no_axis():
    r = establish_axis("approval", {"kind": "generated_summary",
                                    "source_ref": "meeting_summary_doc"})
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_SUMMARY_IS_NOT_A_VERDICT"


def test_each_axis_needs_its_own_witness_kind():
    unwitnessed = establish_axis("receipt", {"kind": "vibes",
                                             "source_ref": "x"})
    assert unwitnessed["reason"] == "E_UNWITNESSED_AXIS"
    ok = establish_axis("receipt", {"kind": "payment_receipt",
                                    "source_ref": "bank:stmt:2026-08"})
    assert ok["verdict"] == "ESTABLISHED"


def test_unknown_axes_are_refused_at_the_type():
    with pytest.raises(ValueError, match="E_UNKNOWN_DECISION_AXIS"):
        establish_axis("vibes_axis", {})


def test_the_signature_has_six_independent_axes():
    sig = decision_signature(())["signature"]
    assert len(sig) == 6
    assert all(v == "UNKNOWN" for v in sig.values())


# ── CH-03: conservative modality wins ───────────────────────────────────

def test_summary_above_transcript_is_overstated_and_loses():
    """The generic form of the equity-split contradiction: transcript
    says PROPOSED, summary presents OPERATOR_DECIDED. The resolved
    state is the transcript's."""
    r = reconcile_modalities("PROPOSED", "OPERATOR_DECIDED")
    assert r["resolved"] == "PROPOSED"
    assert r["summary_status"] == "OVERSTATED"


def test_consistent_or_conservative_summaries_pass():
    assert reconcile_modalities("DISCUSSED",
                                "DISCUSSED")["summary_status"] == \
        "CONSISTENT"
    r = reconcile_modalities("EXECUTED", "DISCUSSED")
    assert r["resolved"] == "DISCUSSED"          # min still wins
    assert r["summary_status"] == "CONSISTENT"


# ── CH-02: provenance-expanded delta ────────────────────────────────────

def test_an_object_found_only_by_provenance_falsifies_enumeration():
    """The generic 488MB case: search returned four IDs; a linked ID
    exposed a fifth that was in-window all along."""
    enumerated = frozenset({"obj1", "obj2", "obj3", "obj4"})
    linked = frozenset({"obj5_large_recording"})
    r = effective_delta(enumerated, linked, frozenset())
    assert r["enumeration_exhaustive"] is False
    assert r["found_only_by_provenance"] == ["obj5_large_recording"]
    assert len(r["effective_delta"]) == 5


def test_clean_enumeration_is_only_provisionally_exhaustive():
    r = effective_delta(frozenset({"a"}), frozenset({"a"}),
                        frozenset({"a"}))
    assert r["enumeration_exhaustive"] is True
    assert "certificate" in r["law"]             # the law rides anyway


# ── CH-04: capacity precondition ────────────────────────────────────────

def test_valid_configured_workflow_without_quota_does_not_run():
    r = capacity_gate(workflow_configured=True, logic_valid=True)
    assert r["verdict"] == "EXECUTION_DISABLED"
    assert r["reason"] == "E_NO_CAPACITY"
    assert "not a quota receipt" in r["law"]
    ok = capacity_gate(True, True, capacity_receipt="plan:credits:2026-09")
    assert ok["verdict"] == "RUNNABLE"


# ── CH-05: field-level secrecy ──────────────────────────────────────────

FIELDS = {"project_name": "S1", "role_needed": "S1",
          "budget_range": "S2", "candidate_phone": "S3",
          "meeting_access_token": "S4"}
VALUES = {"project_name": "alpha", "role_needed": "analytics",
          "budget_range": "mid", "candidate_phone": "REDACTED-INPUT",
          "meeting_access_token": "REDACTED-INPUT"}


def test_object_class_is_the_sup_of_field_classes():
    assert preservation_class(FIELDS) == "S4"
    with pytest.raises(ValueError, match="E_UNKNOWN_SECRECY_CLASS"):
        preservation_class({"x": "S9"})


def test_projection_keeps_the_remainder_and_names_the_withheld():
    p = semantic_projection(FIELDS, VALUES, max_class="S2")
    assert set(p["projected"]) == {"project_name", "role_needed",
                                   "budget_range"}
    assert p["withheld_fields"] == ["candidate_phone",
                                    "meeting_access_token"]
    assert p["withheld_count"] == 2
    assert p["object_class"] == "S4"             # class stays honest
    # an S4 subfield did not poison the whole object
    assert p["projected"]["project_name"] == "alpha"


# ── CH-06: engine-first ─────────────────────────────────────────────────

def test_the_two_improvement_moves_are_distinct_types():
    inst = improvement_scope("instance_repair")
    gen = improvement_scope("generator_improvement")
    assert inst["distributional_effect"] is False
    assert gen["distributional_effect"] is True
    with pytest.raises(ValueError, match="E_UNKNOWN_IMPROVEMENT_MOVE"):
        improvement_scope("just_make_it_better")


# ── determinism ─────────────────────────────────────────────────────────

def test_deterministic():
    a = il.canon(semantic_projection(FIELDS, VALUES, "S2"))
    b = il.canon(semantic_projection(FIELDS, VALUES, "S2"))
    assert a == b
