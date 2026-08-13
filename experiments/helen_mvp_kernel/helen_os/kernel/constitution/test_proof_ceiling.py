"""The proof ceiling, falsified: the launderer fails on promotion
error, the paralytic fails on the positive control despite a perfect
promotion error, and only the governed classifier passes both. Scans
and volumes never multiply historical roots. Unwitnessed is not false.
Gaps are carried, not closed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import proof_ceiling as pc
from proof_ceiling import (
    challenge_set,
    evaluate,
    governed,
    historical_roots,
    launderer,
    open_gaps,
    paralytic,
    promotion_verdict,
    sequence,
    witness,
)


def _heldout():
    return tuple({"id": f"true_{i}",
                  "features": {"period": "victorian",
                               "witness_ref": f"cat:vol2:{i}"}}
                 for i in range(6))


def _fabricated():
    """Deliberately close to the observed neighbourhood: valid
    vocabulary, believable dimensions, legal primitive combinations —
    and never actually witnessed."""
    return tuple({"id": f"fake_{i}",
                  "features": {"period": "victorian",
                               "witness_ref": None}}
                 for i in range(6))


def _challenge():
    return challenge_set(_heldout(), _fabricated())


# ── the metric pair discriminates in BOTH directions ───────────────────

def test_the_launderer_fails_on_promotion_error():
    r = evaluate(launderer, _challenge())
    assert r["E_promotion"] == 1.0
    assert r["verdict"] == "FAIL_LAUNDERING"
    assert r["reason"] == "E_PLAUSIBILITY_PROMOTED"
    assert len(r["laundered_ids"]) == 6


def test_the_paralytic_fails_despite_a_perfect_promotion_error():
    """The whole point of the positive control: abstaining on
    everything scores E_promotion = 0 and must still fail."""
    r = evaluate(paralytic, _challenge())
    assert r["E_promotion"] == 0.0
    assert r["C_abstain"] == 1.0
    assert r["R_obs"] == 0.0
    assert r["verdict"] == "FAIL_PARALYSIS"
    assert r["reason"] == "E_ABSTAINS_ON_WITNESSED"


def test_only_the_governed_classifier_passes_both():
    r = evaluate(governed, _challenge())
    assert r["E_promotion"] == 0.0
    assert r["R_obs"] == 1.0
    assert r["verdict"] == "PASS"
    assert r["reason"] is None


def test_a_challenge_without_witnessed_items_cannot_detect_paralysis():
    bad = challenge_set((), _fabricated())
    r = evaluate(governed, bad)
    assert r["verdict"] == "INVALID_CHALLENGE"
    assert r["reason"] == "E_NO_POSITIVE_CONTROL"


def test_the_classifier_never_sees_ground_truth():
    seen = []

    def spy(item):
        seen.append(set(item))
        return "GENERABLE"
    evaluate(spy, _challenge())
    assert all("_W" not in s for s in seen)


def test_an_empty_challenge_is_refused():
    with pytest.raises(ValueError, match="E_EMPTY_CHALLENGE"):
        evaluate(governed, ())


# ── root counting ───────────────────────────────────────────────────────

def test_four_volumes_and_many_scans_are_one_root():
    arts = tuple({"lineage": "royal_commission_catalogue",
                  "edition": "1851", "volume": v}
                 for v in (1, 2, 3, 4) for _ in range(3))
    r = historical_roots(arts)
    assert r["n_artifacts"] == 12
    assert r["n_historical_roots"] == 1
    assert r["roots"]["royal_commission_catalogue"]["volumes"] == 4


def test_the_two_distinct_lineages_count_as_two_roots():
    arts = ({"lineage": "royal_commission_catalogue", "volume": 1},
            {"lineage": "royal_commission_catalogue", "volume": 2},
            {"lineage": "jury_reports", "volume": 1})
    assert historical_roots(arts)["n_historical_roots"] == 2


def test_no_artifacts_is_refused():
    with pytest.raises(ValueError, match="E_NO_ARTIFACTS"):
        historical_roots(())


# ── witness typing and the DENY rule ───────────────────────────────────

def test_unwitnessed_is_not_false():
    w = witness("a border existed in blue", None)
    assert w["status"] == "UNWITNESSED"
    assert w["is_false"] is False


def test_witness_strength_is_ordered_but_the_policy_is_undeclared():
    img = witness("c", "exact_specimen_image")
    txt = witness("c", "textual_mention")
    assert img["strength"] > txt["strength"]
    assert img["entailment_policy_declared"] is False
    assert "operator's to declare" in img["note"]


def test_an_unknown_witness_kind_is_refused():
    assert witness("c", "vibes")["reason"] == "E_UNKNOWN_WITNESS_KIND"


def test_high_plausibility_with_no_witness_and_no_derivation_denies():
    v = promotion_verdict(gamma_high=True, w_empirical=0, d_valid=0)
    assert v["promotion"] == "DENY"
    assert v["reason"] == "E_PLAUSIBILITY_IS_NOT_HISTORY"


def test_a_derivation_alone_licenses_promotion():
    v = promotion_verdict(gamma_high=False, w_empirical=0, d_valid=1)
    assert v["promotion"] == "LICENSED"
    assert v["paid_by"] == "D_valid"


# ── carried gaps and the research order ────────────────────────────────

def test_the_gaps_are_carried_and_none_is_closed():
    g = open_gaps()
    assert g["resolved"] == 0
    assert len(g["gaps"]) == 5
    assert "OPERATOR_REPORTED" in g["corpus_grade"]


def test_the_sequence_prevents_undirected_accumulation():
    s = sequence()
    assert s["order"][0] == "indub(ATF_1900)"
    assert s["order"][-1] == "1851 OOD validation"
    assert s["not"] == "older ATF-like data"


def test_deterministic():
    assert pc.canon(evaluate(governed, _challenge())) == \
        pc.canon(evaluate(governed, _challenge()))
