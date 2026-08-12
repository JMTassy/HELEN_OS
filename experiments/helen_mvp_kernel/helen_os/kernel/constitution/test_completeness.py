"""Falsifiers for the ceiling completeness harness: the census is
total over the safety axis, liveness is a distinct axis (not an
unmapped safety rule), the ontology-effect theorem, and the
adversarial completeness probe that refuses to claim PROVEN.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import completeness as cp
from completeness import (
    CEILING_BASIS,
    CandidateDelta,
    census_is_total,
    compile_to_ceiling,
    completeness_probe,
    is_counterexample,
    ontology_effect,
)


# ── the census is total over the safety axis ──────────────────────────

def test_every_safety_prohibition_maps_to_one_of_four_ceilings():
    r = census_is_total()
    assert r["total"] is True
    assert r["all_four_used"] is True
    assert r["unmapped"] == []
    assert set(r["ceilings_used"]) == set(CEILING_BASIS)


@pytest.mark.parametrize("prohibition,ceiling", [
    ("projection != evidence", "PROOF"),
    ("Generable != HistoricallyObserved", "PROOF"),
    ("NotObserved != Impossible", "PROOF"),
    ("Observed(A) & Observed(B) != Observed(A.B)", "PROOF"),
    ("partial verdict scope", "SCOPE"),
    ("name != identity (merge)", "SCOPE"),
    ("captured != lawfully captured", "AUTHORITY"),
    ("capability != authority", "AUTHORITY"),
    ("state != lawful history", "REPLAY"),
    ("court judgment != world history", "REPLAY"),
])
def test_specific_prohibitions_compile_to_expected_ceiling(prohibition,
                                                           ceiling):
    r = compile_to_ceiling(prohibition)
    assert r["ceiling"] == ceiling and r["axis"] == "SAFETY"
    assert r["question"] == cp.CEILING_QUESTION[ceiling]


def test_the_possibility_space_triple_is_three_proof_instances():
    """The operator's point: Generable/NotObserved/composition are not
    new primitives; they are PROOF-ceiling instances."""
    for p in ("Generable != HistoricallyObserved",
              "NotObserved != Impossible",
              "Observed(A) & Observed(B) != Observed(A.B)"):
        assert compile_to_ceiling(p)["ceiling"] == "PROOF"


# ── liveness is a distinct axis, not an unmapped safety rule ───────────

def test_liveness_prohibitions_are_the_dual_axis_not_unmapped():
    r = compile_to_ceiling("HOLD != DEADLOCK")
    assert r["axis"] == "LIVENESS"
    assert r["ceiling"] is None
    assert "cannot represent a MUST-eventually" in r["note"]


def test_a_genuinely_unmapped_safety_rule_is_diagnostic():
    r = compile_to_ceiling("some future archive falsifier")
    assert r["axis"] == "UNMAPPED"
    assert r["reason"] == "E_UNMAPPED"
    assert "constitution must grow" in r["law"]


def test_the_two_axes_are_named():
    r = census_is_total()
    assert r["axes"] == (cp.SAFETY_AXIS, cp.LIVENESS_AXIS)
    assert r["liveness_prohibitions"] >= 4


# ── the ontology-effect theorem ────────────────────────────────────────

def test_merge_changes_cardinality_so_it_is_an_effect():
    r = ontology_effect("merge", entities_before=2, entities_after=1)
    assert r["has_effect"] is True
    assert r["ceiling"] == "SCOPE"
    assert r["requires_admission"] is True
    assert r["delta_cardinality"] == -1


@pytest.mark.parametrize("op", ["dedup", "alias_collapse",
                                "identity_stitch", "canonicalize_entity",
                                "record_linkage", "event_coalesce"])
def test_all_ontology_ops_require_admission_even_at_equal_count(op):
    # named ontology ops require admission by kind, even if this
    # particular call happened not to drop a row
    r = ontology_effect(op, entities_before=5, entities_after=5)
    assert r["requires_admission"] is True and r["ceiling"] == "SCOPE"


def test_a_pure_representation_transform_needs_no_admission():
    r = ontology_effect("reformat", entities_before=5, entities_after=5)
    assert r["has_effect"] is False and r["requires_admission"] is False


# ── the adversarial completeness probe ─────────────────────────────────

def test_a_delta_passing_all_ceilings_yet_invalid_is_a_counterexample():
    c = CandidateDelta("d", proof_ok=True, scope_ok=True,
                       authority_ok=True, replay_ok=True,
                       independently_invalid=True)
    assert is_counterexample(c) is True
    r = completeness_probe((c,))
    assert r["verdict"] == "ALGEBRA_INCOMPLETE"
    assert "d" in r["counterexamples"]


def test_a_delta_failing_any_ceiling_is_not_a_counterexample():
    c = CandidateDelta("d", proof_ok=False, scope_ok=True,
                       authority_ok=True, replay_ok=True,
                       independently_invalid=True)
    assert is_counterexample(c) is False


def test_no_counterexample_reports_unknown_never_proven():
    """The reflexive possibility-space law: absence of a witnessed
    counterexample does not prove completeness."""
    valid = CandidateDelta("v", True, True, True, True,
                           independently_invalid=False)
    r = completeness_probe((valid,))
    assert r["verdict"] == "NO_COUNTEREXAMPLE_WITNESSED"
    assert r["completeness"] == "UNKNOWN"
    assert "never PROVEN" in r["law"]


def test_the_probe_names_the_corpora_it_has_searched():
    assert len(cp.CORPORA_SEARCHED) >= 4
    assert "prize_papers_hca32" in cp.CORPORA_SEARCHED


def test_deterministic():
    valid = CandidateDelta("v", True, True, True, True, False)
    assert cp.canon(completeness_probe((valid,))) == \
        cp.canon(completeness_probe((valid,)))
