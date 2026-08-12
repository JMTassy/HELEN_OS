"""Falsifiers for the possibility-space triple: O_t (subsetneq) P_t,
absence != prohibition, and Generable(x) does not entail
HistoricallyObserved(x).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import possibility_space as ps
from possibility_space import (
    Generated,
    Operator,
    PossibilitySpace,
    absence_verdict,
    assert_observed_exhausts_possible,
    claim_historically_observed,
    generate,
)


# ── 1. O_t (subsetneq) P_t ──────────────────────────────────────────────

def test_observed_is_a_proper_subset_of_possible():
    s = PossibilitySpace(observed=frozenset({"fill", "scale"}),
                         possible=frozenset({"fill", "scale", "repeat",
                                             "corner"}))
    assert s.is_proper() is True
    assert s.unobserved_possible() == frozenset({"repeat", "corner"})


def test_observed_exceeding_possible_is_incoherent():
    with pytest.raises(ValueError, match="E_OBSERVED_EXCEEDS_POSSIBLE"):
        PossibilitySpace(observed=frozenset({"a", "b"}),
                         possible=frozenset({"a"}))


def test_a_catalogue_cannot_declare_itself_the_whole_grammar():
    with pytest.raises(ValueError, match="E_UNWITNESSED_CLOSURE"):
        PossibilitySpace(observed=frozenset({"a", "b"}),
                         possible=frozenset({"a", "b"}))
    # ...unless a closure witness is supplied
    closed = PossibilitySpace(frozenset({"a"}), frozenset({"a"}),
                              closure_witness="finite-grammar-proof#1")
    assert closed.is_proper() is False


def test_asserting_observed_exhausts_possible_is_refused():
    s = PossibilitySpace(frozenset({"fill"}),
                         frozenset({"fill", "repeat"}))
    r = assert_observed_exhausts_possible(s)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_CLOSURE_UNWITNESSED"
    assert r["unobserved"] == ["repeat"]


# ── 2. absence != prohibition ───────────────────────────────────────────

def test_an_absent_operator_is_unknown_not_forbidden():
    observed = frozenset({"fill", "scale"})
    r = absence_verdict("gradient_mesh", observed)
    assert r["verdict"] == "UNKNOWN"
    assert "absence is not prohibition" in r["law"]


def test_prohibition_requires_a_witness():
    observed = frozenset({"fill"})
    r = absence_verdict("gradient_mesh", observed,
                        prohibition_witness="1902-spec-excludes-it")
    assert r["verdict"] == "FORBIDDEN"
    assert r["witness"] == "1902-spec-excludes-it"


def test_a_present_item_reads_present():
    assert absence_verdict("fill", frozenset({"fill"}))["verdict"] == \
        "PRESENT"


# ── 3. Generable(x) does not entail HistoricallyObserved(x) ────────────

CORPUS = frozenset({"fill", "scale", "repeat", "corner"})


def test_generation_over_the_grammar_yields_a_hypothesis():
    ops = (Operator("fill", "ATF p.12"), Operator("repeat", "ATF p.12"))
    r = generate("fleur", ops, CORPUS)
    assert r["verdict"] == "GENERATED"
    assert r["state"] == "HYPOTHESIS"
    assert "not a historical fact" in r["law"]


def test_an_operator_outside_the_corpus_is_unsupported_invention():
    ops = (Operator("gradient_mesh", "modern tool"),)
    r = generate("fleur", ops, CORPUS)
    assert r["verdict"] == "REJECT"
    assert r["reason"] == "E_UNSUPPORTED_INVENTION"
    assert r["operators_outside_corpus"] == ["gradient_mesh"]


def test_an_uncited_operator_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNWITNESSED_OPERATOR"):
        Operator("fill", "")


def test_a_generated_form_is_not_historically_observed():
    g = Generated("gen:fleur", ("fill", "repeat"), "HYPOTHESIS")
    r = claim_historically_observed(g)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_GENERABLE_IS_NOT_OBSERVED"
    assert "the generator is not a witness to history" in r["law"]


def test_a_historical_witness_promotes_it():
    g = Generated("gen:fleur", ("fill",), "HYPOTHESIS")
    r = claim_historically_observed(g, historical_witness="dated-artifact#9")
    assert r["verdict"] == "OBSERVED_WITH_WITNESS"


# ── the triple maps onto the ceiling algebra ───────────────────────────

def test_the_triple_is_ceiling_shaped():
    m = ps.TRIPLE_CEILING_MAP
    assert m["E_CLOSURE_UNWITNESSED"] == "SCOPE"
    assert m["E_GENERABLE_IS_NOT_OBSERVED"] == "PROOF"


def test_deterministic():
    ops = (Operator("fill", "ATF"),)
    assert ps.canon(generate("fleur", ops, CORPUS)["state"]) == \
        ps.canon(generate("fleur", ops, CORPUS)["state"])
