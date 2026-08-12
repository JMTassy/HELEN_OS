"""Falsifiers for the frozen 40-item benchmark: shape, grade
discipline, the two-hash separation, the orthogonal-credential
finding that falsified this seat's ladder reading, and the guard
that every item carries a forbidden promotion plus a falsifier.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import benchmark_40 as b40
from benchmark_40 import (
    BENCHMARK_40,
    ChiddushItem,
    cite_as,
    coherent_signatures,
    freeze_benchmark,
    grade_census,
)


# ── shape ───────────────────────────────────────────────────────────────

def test_forty_items_ten_per_volume_unique_ids():
    r = freeze_benchmark()
    assert r["verdict"] == "FROZEN"
    assert r["count"] == 40
    assert r["by_volume"] == {"A": 10, "B": 10, "C": 10, "D": 10}
    assert len({i.item_id for i in BENCHMARK_40}) == 40


def test_a_short_or_duplicated_packet_is_refused():
    assert freeze_benchmark(BENCHMARK_40[:-1])["reason"] == \
        "E_PACKET_SHAPE"
    dup = BENCHMARK_40[:-1] + (BENCHMARK_40[0],)
    assert freeze_benchmark(dup)["reason"] in ("E_PACKET_SHAPE",
                                               "E_DUPLICATE_ITEM_ID")


# ── every chiddush is guarded ───────────────────────────────────────────

def test_every_item_names_a_forbidden_promotion_and_a_falsifier():
    for it in BENCHMARK_40:
        assert it.forbidden_promotion and it.falsifier, it.item_id


def test_an_unguarded_chiddush_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNGUARDED_CHIDDUSH"):
        ChiddushItem("X-01", "A", "A", ("i", "g", "t", "o", "r"),
                     "a fine idea", forbidden_promotion="",
                     falsifier="")


def test_the_motif_must_be_a_five_tuple():
    with pytest.raises(ValueError, match="E_MOTIF_NOT_IGTOR"):
        ChiddushItem("X-02", "A", "A", ("i", "g", "t"), "c", "f", "x")


# ── grade discipline: C never passes as A ──────────────────────────────

def test_grade_census_matches_the_delivered_packet():
    c = grade_census()["by_grade"]
    assert c["A"] == 27 and c["B"] == 11 and c["C"] == 2
    assert sum(c.values()) == 40


def test_a_grade_c_item_cannot_be_cited_as_grade_a():
    jur09 = next(i for i in BENCHMARK_40 if i.item_id == "JUR-09")
    assert jur09.grade == "C"
    r = cite_as(jur09, required_grade="A")
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_GRADE_OVERCLAIM"
    assert cite_as(jur09, "C")["verdict"] == "CITABLE"


def test_a_grade_a_item_satisfies_a_weaker_requirement():
    pat08 = next(i for i in BENCHMARK_40 if i.item_id == "PAT-08")
    assert cite_as(pat08, "A")["verdict"] == "CITABLE"
    assert cite_as(pat08, "C")["verdict"] == "CITABLE"


# ── two hashes, never conflated ────────────────────────────────────────

def test_the_declared_other_lane_hash_is_recorded_unverified():
    r = freeze_benchmark()
    assert r["declared_by_other_lane"] == b40.DECLARED_PAYLOAD_HASH
    assert r["declared_hash_verified_here"] is False
    assert "not the other lane's JSON bytes" in r["declared_hash_status"]


def test_this_seats_freeze_hash_is_its_own_and_deterministic():
    a, b = freeze_benchmark(), freeze_benchmark()
    assert a["freeze_hash_here"] == b["freeze_hash_here"]
    assert a["freeze_hash_here"] != b40.DECLARED_PAYLOAD_HASH


def test_the_holdout_is_named_and_post_1851_patents_blocked():
    r = freeze_benchmark()
    assert r["holdout"] == "international_exhibition_1862"
    assert r["post_1851_patent_data"] == "BLOCKED"


# ── the headline finding: orthogonal credentials, not a ladder ─────────

def test_the_claim_corpus_carries_the_feedback_loop_the_demo_frames_lack():
    """PAT-08/09 in the <=1850 CLAIM corpus: closed negative feedback
    with a separate safety-escalation threshold. This is what kills
    the linear ladder reading."""
    pat08 = next(i for i in BENCHMARK_40 if i.item_id == "PAT-08")
    pat09 = next(i for i in BENCHMARK_40 if i.item_id == "PAT-09")
    assert "negative-feedback" in pat08.chiddush
    assert "distinct thresholds" in pat09.chiddush
    assert pat08.corpus_volume == "A" and pat08.grade == "A"
    f = b40.LADDER_FALSIFICATION
    assert f["witnesses"] == ("PAT-08", "PAT-09")
    assert "ordering of one" in f["kills"]


def test_items_carry_signature_vectors_not_ladder_rungs():
    pat = next(i for i in BENCHMARK_40 if i.item_id == "PAT-01")
    rail = next(i for i in BENCHMARK_40 if i.item_id == "RAIL-01")
    ps, rs = pat.signature(), rail.signature()
    assert ps["claimed"] == "WITNESSED"
    assert ps["demonstrated"] == "UNKNOWN"       # never inferred
    assert rs["operationally_survived"] == "WITNESSED"
    assert rs["claimed"] == "UNKNOWN"            # no ladder beneath it


def test_both_declared_coherent_signatures_are_representable():
    """A scalar ladder cannot hold either of these; the vector can."""
    claim_only, demo_judged_failed = coherent_signatures()
    assert claim_only["claim"] == "yes" and claim_only["demo"] == "unknown"
    assert demo_judged_failed["claim"] == "unknown"
    assert demo_judged_failed["robust"] == "failure"


def test_no_max_operator_collapses_a_signature():
    """There is deliberately no aggregate: sigma has no overall truth."""
    sig = next(i for i in BENCHMARK_40
               if i.item_id == "CP-01").signature()
    assert "overall" not in sig and "score" not in sig
    assert set(sig.values()) <= {"WITNESSED", "UNKNOWN"}


# ── determinism ─────────────────────────────────────────────────────────

def test_deterministic():
    import crystal_palace as cp
    assert cp.canon(freeze_benchmark()) == cp.canon(freeze_benchmark())
