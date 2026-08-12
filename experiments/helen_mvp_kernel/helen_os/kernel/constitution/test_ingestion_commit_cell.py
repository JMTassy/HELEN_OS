"""The six named HAL falsifiers for the Ingestion Commit Cell, plus
the three-credential split, capacity-as-lease, and cursor discipline.

  INGEST-LINKED-OBJECT-MISS
  INGEST-SUMMARY-PROMOTION
  INGEST-CURSOR-EARLY
  INGEST-CAPACITY-ZERO
  INGEST-FIELD-SECRET-LEAK
  INGEST-SAME-FINAL-STATE-DIFFERENT-PROVENANCE

All fixtures generic: no S2/S3/S4 content enters this published repo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ingestion_commit_cell as icc
import ingestion_laws as il
from ingestion_commit_cell import (
    DiscoveryOperators,
    IngestionCell,
    ResourceLease,
    admit_ingestion,
    can_execute,
    cursor_sequence_valid,
    entails,
    ingestion_equiv,
    provenance_closure,
)

OPS = DiscoveryOperators(("enumerate_modified_time", "resolve_linked_ids",
                          "expand_attachments"))
SECRECY = {"project_name": "S1", "budget_band": "S2",
           "access_token": "S4"}


def _closure(enumerated, linked=frozenset(), attach=frozenset(),
             referenced=frozenset()):
    return provenance_closure(enumerated, linked, attach, referenced, OPS)


def _cell(**over):
    enum = frozenset({"o1", "o2", "o3", "o4"})
    linked = frozenset({"o5_large"})
    cl = _closure(enum, linked)
    base = dict(
        window=(1000, 2000),
        enumeration=enum,
        closure=cl,
        classification={o: "S2" for o in cl["effective_delta"]},
        restricted_fields=("access_token",),
        mirror_set=frozenset({"o5_large"}),
        mirrors_verified=frozenset({"o5_large"}),
        hashes={"o5_large": "sha256:abc"},
        projection_fields={"project_name": "alpha"})
    base.update(over)
    return IngestionCell(**base)


# ── FALSIFIER 1 · INGEST-LINKED-OBJECT-MISS ────────────────────────────

def test_ingest_linked_object_miss_rejects_exhaustive_true():
    """Enumeration returned four; a known source referenced a fifth
    in-window object. EXHAUSTIVE=true must be rejected."""
    c = _closure(frozenset({"o1", "o2", "o3", "o4"}),
                 linked=frozenset({"o5_large"}))
    assert c["ENUMERATION_COMPLETE"] is True         # the query DID return
    assert c["enumeration_was_exhaustive"] is False  # but it was not whole
    assert c["found_only_by_provenance"] == ["o5_large"]
    assert len(c["effective_delta"]) == 5


def test_the_three_credentials_are_separate():
    c = _closure(frozenset({"o1"}))
    assert "ENUMERATION_COMPLETE" in c
    assert "PROVENANCE_CLOSURE_COMPLETE" in c
    assert icc.COMPLETION_CREDENTIALS == (
        "ENUMERATION_COMPLETE", "PROVENANCE_CLOSURE_COMPLETE",
        "MIRROR_COMPLETE")


def test_closure_is_scoped_to_declared_operators_never_the_universe():
    c = _closure(frozenset({"o1"}))
    assert c["closure_scope"] == OPS.names
    assert "NOT proved exhaustive over the universe" in c["closure_caveat"]
    with pytest.raises(ValueError, match="E_NO_DECLARED_OPERATORS"):
        DiscoveryOperators(())


# ── FALSIFIER 2 · INGEST-SUMMARY-PROMOTION ─────────────────────────────

def test_ingest_summary_promotion_is_refused_on_every_axis():
    for axis in il.DECISION_AXES:
        r = il.establish_axis(axis, {"kind": "generated_summary",
                                     "source_ref": "summary_doc"})
        assert r["verdict"] == "REFUSED"
        assert r["reason"] == "E_SUMMARY_IS_NOT_A_VERDICT"


def test_decision_signature_flags_executed_without_decision():
    """The pathology a scalar chain cannot express: operationally done,
    never legitimately decided."""
    ws = ({"axis": "proposal", "kind": "written_proposal",
           "source_ref": "p1"},
          {"axis": "execution", "kind": "execution_receipt",
           "source_ref": "log1"})
    r = il.decision_signature(ws)
    assert r["signature"]["execution"] == "WITNESSED"
    assert r["signature"]["approval"] == "UNKNOWN"
    assert r["executed_without_decision"] is True
    assert r["alarm"] == "E_EXECUTED_WITHOUT_DECISION"


def test_axes_do_not_leak_into_one_another():
    ws = ({"axis": "discussion", "kind": "transcript", "source_ref": "t1"},)
    sig = il.decision_signature(ws)["signature"]
    assert sig["discussion"] == "WITNESSED"
    assert sig["approval"] == "UNKNOWN" and sig["authority"] == "UNKNOWN"
    # and a witness kind valid for one axis is invalid for another
    bad = il.establish_axis("approval", {"kind": "transcript",
                                         "source_ref": "t1"})
    assert bad["reason"] == "E_UNWITNESSED_AXIS"


# ── FALSIFIER 3 · INGEST-CURSOR-EARLY ──────────────────────────────────

def test_ingest_cursor_early_is_refused():
    early = ("PERSIST", "CURSOR_ADVANCE", "HASH", "VERIFY", "RECEIPT")
    r = cursor_sequence_valid(early)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_CURSOR_BEFORE_DURABLE_CLOSURE"
    assert "never a promise of it" in r["law"]
    assert cursor_sequence_valid(icc.CURSOR_ORDER)["verdict"] == \
        "VALID_SEQUENCE"


def test_cursor_held_when_mirrors_or_hashes_are_unverified():
    unmirrored = _cell(mirrors_verified=frozenset())
    r = admit_ingestion(unmirrored, "S2", SECRECY)
    assert r["verdict"] == "CURSOR_HELD"
    assert r["reason"] == "E_MIRROR_UNVERIFIED"
    assert r["cursor_advanced"] is False
    unhashed = _cell(hashes={})
    assert admit_ingestion(unhashed, "S2", SECRECY)["reason"] == \
        "E_HASH_UNVERIFIED"


# ── FALSIFIER 4 · INGEST-CAPACITY-ZERO ─────────────────────────────────

def test_ingest_capacity_zero_blocks_a_valid_authorized_action():
    empty = ResourceLease("saas_credits", available=0.0)
    r = can_execute(valid=True, authorized=True, capacity=empty,
                    amount=1.0, environment_ok=True, t=10)
    assert r["verdict"] == "NO_EFFECT"
    assert r["missing"] == ["capacity"]


def test_capacity_cannot_be_double_spent():
    lease = ResourceLease("saas_credits", available=10.0)
    assert lease.reserve(8.0, t=1)["ok"] is True
    second = lease.reserve(8.0, t=1)
    assert second["ok"] is False
    assert second["reason"] == "E_INSUFFICIENT_CAPACITY"


def test_capacity_expiry_and_consume_discipline():
    lease = ResourceLease("tokens", available=5.0, expires=100)
    assert lease.reserve(1.0, t=101)["reason"] == "E_CAPACITY_EXPIRED"
    assert lease.consume(1.0)["reason"] == "E_CONSUME_WITHOUT_RESERVE"
    lease.reserve(2.0, t=10)
    assert lease.consume(2.0)["ok"] is True


def test_all_four_conjuncts_are_required():
    ok = ResourceLease("q", available=5.0)
    r = can_execute(True, True, ok, 1.0, environment_ok=False, t=1)
    assert r["verdict"] == "NO_EFFECT" and r["missing"] == ["environment"]


# ── FALSIFIER 5 · INGEST-FIELD-SECRET-LEAK ─────────────────────────────

def test_ingest_field_secret_leak_rejects_the_whole_projection():
    """One S4 field inside an otherwise authorized projection kills the
    projection — it does not get emitted 'mostly safely'."""
    leaky = _cell(projection_fields={"project_name": "alpha",
                                     "access_token": "REDACTED-INPUT"})
    r = admit_ingestion(leaky, "S2", SECRECY)
    assert r["verdict"] == "CURSOR_HELD"
    assert r["reason"] == "E_SECRET_IN_PROJECTION"
    assert r["leaked_fields"] == ["access_token"]


def test_private_does_not_mean_preserve_all():
    """Operator tightening: S3 full-private preservation is a policy
    decision, not a constitutional default."""
    r = il.retention_decision("S3")
    assert r["verdict"] == "RETENTION_UNDECIDED"
    assert r["reason"] == "E_PRESERVE_ALL_IS_NOT_A_DEFAULT"
    assert "PRIVATE does not imply PRESERVE_ALL" in r["law"]
    decided = il.retention_decision("S3", "role-level abstraction only",
                                    "delete raw at 90d")
    assert decided["verdict"] == "RETENTION_DECIDED"


# ── FALSIFIER 6 · INGEST-SAME-FINAL-STATE-DIFFERENT-PROVENANCE ─────────

def test_same_semantic_memory_different_closure_is_not_equal():
    a = {"semantic_memory": {"x": 1},
         "effective_delta": frozenset({"o1", "o2", "o5_large"}),
         "closure_scope": OPS.names}
    b = {"semantic_memory": {"x": 1},
         "effective_delta": frozenset({"o1", "o2"}),   # skipped the link
         "closure_scope": ("enumerate_modified_time",)}
    r = ingestion_equiv(a, b)
    assert r["extensional"] is True
    assert r["constitutional"] is False


def test_identical_runs_are_constitutionally_equal():
    a = {"semantic_memory": {"x": 1},
         "effective_delta": frozenset({"o1"}), "closure_scope": OPS.names}
    assert ingestion_equiv(a, dict(a))["constitutional"] is True


# ── the availability family ────────────────────────────────────────────

@pytest.mark.parametrize("premise,conclusion",
                         icc.AVAILABILITY_NON_ENTAILMENTS)
def test_every_availability_pair_is_a_non_entailment(premise, conclusion):
    r = entails(premise, conclusion)
    assert r["entails"] is False and r["reason"] == "E_NON_ENTAILMENT"


# ── the positive control ───────────────────────────────────────────────

def test_a_fully_discharged_cell_advances_the_cursor():
    r = admit_ingestion(_cell(), "S2", SECRECY)
    assert r["verdict"] == "ADVANCE_CURSOR"
    assert r["credentials"]["MIRROR_COMPLETE"] is True
    assert r["closure_scope"] == OPS.names
    assert r["receipt"]


def test_unclassified_objects_hold_the_cursor():
    c = _cell(classification={"o1": "S2"})
    r = admit_ingestion(c, "S2", SECRECY)
    assert r["reason"] == "E_CLASSIFICATION_INCOMPLETE"
    assert "o5_large" in r["unclassified"]


def test_deterministic():
    a = icc.canon(admit_ingestion(_cell(), "S2", SECRECY))
    b = icc.canon(admit_ingestion(_cell(), "S2", SECRECY))
    assert a == b
