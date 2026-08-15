"""The executed enterprise falsifier: replacing cognition with a
deterministic stub collapses quality and changes NO structural
property; a rogue proposal dies at the effect gate however confident;
stores never coerce without their named gate; cross-tenant reads
refuse; and replayability never implies correctness.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cognition_replacement as cr
from cognition_replacement import (
    cognition_rich,
    cognition_stub,
    permit_cognition,
    permit_effect,
    replacement_invariant,
    rogue_cognition,
    run_application,
    shared_read,
    store_move,
    structural_projection,
)


# ── the benchmark itself ───────────────────────────────────────────────

def test_the_replacement_invariant_passes_end_to_end():
    v = replacement_invariant()
    assert v["BENCHMARK"] == "PASS", v["delta_structure"]
    assert all(x == "PASS" for x in v["per_property"].values())
    assert len(v["per_property"]) == 10


def test_quality_collapses_and_structure_does_not():
    v = replacement_invariant()
    assert v["quality_C"] == 0.92 and v["quality_C0"] == 0.0
    assert v["quality_collapsed"] is True
    assert v["delta_structure"] == ()
    # replay hashes over the structural path are identical: the
    # governed path is byte-stable under cognition replacement
    assert v["replay_hash_C"] == v["replay_hash_C0"]


def test_the_thesis_is_earned_not_asserted():
    v = replacement_invariant()
    assert "replaceable dependency" in v["thesis_supported"]


# ── the two gates ──────────────────────────────────────────────────────

def test_model_can_propose_but_system_executes():
    out = run_application(rogue_cognition)
    r = out["receipt"]
    assert r["result"] == "REFUSED"
    assert r["effect"] is None
    assert r["state_after"] == r["state_before"] == "DRAFT"
    assert r["policy"]["effect_gate"] is False
    # and the refusal itself produced a complete receipt
    assert set(cr.RECEIPT_FIELDS) <= set(r)


def test_gate_one_bounds_what_cognition_may_read():
    v = permit_cognition(("S_A.read:BO-1", "S_A.read:BO-2"),
                         ("S_A.read:BO-1",))
    assert v["permitted"] is False
    assert v["reason"] == "E_COGNITION_OVERREACH"


def test_gate_two_evaluates_the_concrete_effect():
    assert permit_effect("advance_to_review",
                         ("advance_to_review",))["authorized"] is True
    v = permit_effect("delete_all_records", ("advance_to_review",))
    assert v["reason"] == "E_PROPOSED_IS_NOT_EXECUTABLE"


# ── stores and tenancy ─────────────────────────────────────────────────

def test_stores_never_coerce_without_their_named_gate():
    assert store_move("S_C", "S_A")["reason"] == "E_STORE_COERCION"
    assert store_move("S_R", "S_A")["reason"] == "E_STORE_COERCION"
    ungated = store_move("S_C", "S_K", gate=None)
    assert ungated["reason"] == "E_UNGATED_STORE_MOVE"
    assert store_move("S_C", "S_K", gate="Gamma_K")["ok"] is True
    assert store_move("candidate", "S_A", gate="Gamma_A")["ok"] is True


def test_the_shared_graph_is_enumerated_and_reads_are_a_boundary():
    assert shared_read("signed_release", cross_tenant=True)["ok"]
    v = shared_read("customer_history", cross_tenant=True)
    assert v["reason"] == "E_TENANT_READ_BOUNDARY"
    assert shared_read("customer_history", cross_tenant=False)["ok"]


# ── receipts and replay ────────────────────────────────────────────────

def test_the_receipt_binds_the_full_decision_path():
    out = run_application(cognition_rich)
    r = out["receipt"]
    assert tuple(sorted(r)) == tuple(sorted(cr.RECEIPT_FIELDS))
    assert tuple(sorted(r["runtime_identity"])) == \
        tuple(sorted(cr.RUNTIME_IDENTITY))
    # content travels as digest, never raw
    assert "content" not in r["candidate"]
    assert r["candidate"]["content_digest"]


def test_replayability_does_not_imply_correctness():
    out = run_application(cognition_stub)
    assert out["replayable"] is True
    assert out["correct"] is None      # provenance, never truth


def test_deterministic():
    assert cr.canon(replacement_invariant()) == \
        cr.canon(replacement_invariant())
    a = structural_projection(run_application(cognition_rich)["receipt"])
    b = structural_projection(run_application(cognition_rich)["receipt"])
    assert cr.canon(a) == cr.canon(b)
