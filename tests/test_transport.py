"""Tests for transport/ — Transport Theory of Observations.

Three concrete domains:
    1. Abstract state space (pure math baseline)
    2. Authority linter as an observation map (explicit fiber example)
    3. Toy embedding map (semantic invisible transforms)

Each test is self-contained. No HELEN imports.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transport.observation import ObservationMap
from transport.fiber import FiberSet
from transport.kernel import GeneralizedKernel
from transport.quotient import QuotientSpace
from transport.reconstruction import Reconstructor


# ===========================================================================
# 1. Abstract state space — pure math baseline
# ===========================================================================

# R maps integers to their parity (0 or 1).
# Inv(R) contains any permutation that preserves parity.
# Quotient has exactly 2 classes: {evens} and {odds}.

STATES = list(range(10))  # 0..9
R_parity = ObservationMap(lambda n: n % 2, name="parity")


def test_observation_map_basic() -> None:
    assert R_parity.observe(4) == 0
    assert R_parity.observe(7) == 1


def test_equivalence_relation() -> None:
    assert R_parity.are_equivalent(2, 8)
    assert R_parity.are_equivalent(1, 5)
    assert not R_parity.are_equivalent(2, 3)


def test_fiber_of_even() -> None:
    fiber = R_parity.fiber(0, STATES)
    assert set(fiber) == {0, 2, 4, 6, 8}


def test_fiber_of_odd() -> None:
    fiber = R_parity.fiber(1, STATES)
    assert set(fiber) == {1, 3, 5, 7, 9}


def test_partition_into_two_classes() -> None:
    classes = R_parity.partition(STATES)
    assert len(classes) == 2
    sizes = sorted(len(c) for c in classes)
    assert sizes == [5, 5]


def test_fiber_set_nontrivial() -> None:
    members = R_parity.fiber(0, STATES)
    fs = FiberSet(observation=0, members=members)
    assert not fs.is_trivial()
    assert fs.has_invisible_pair()
    pair = fs.witness_pair()
    assert pair is not None
    a, b = pair
    assert a != b
    assert R_parity.observe(a) == R_parity.observe(b)


def test_fiber_set_trivial() -> None:
    fs = FiberSet(observation=42, members=[42])
    assert fs.is_trivial()
    assert not fs.has_invisible_pair()
    assert fs.witness_pair() is None


# ===========================================================================
# 2. Generalized kernel — invisible transforms
# ===========================================================================

def test_parity_preserving_transform_is_invisible() -> None:
    K = GeneralizedKernel(R_parity)
    # Adding 2 to any integer preserves parity
    add_two = lambda n: n + 2
    assert K.is_invisible(add_two, STATES)
    assert K.is_nontrivial(add_two, STATES)


def test_parity_flipping_transform_is_not_invisible() -> None:
    K = GeneralizedKernel(R_parity)
    add_one = lambda n: n + 1
    assert not K.is_invisible(add_one, STATES)


def test_identity_is_invisible_but_trivial() -> None:
    K = GeneralizedKernel(R_parity)
    identity = lambda n: n
    assert K.is_invisible(identity, STATES)
    assert not K.is_nontrivial(identity, STATES)


def test_witness_finds_explicit_non_injectivity() -> None:
    K = GeneralizedKernel(R_parity)
    K.register(lambda n: n + 2, "add_two", STATES)
    w = K.witness(STATES)
    assert w is not None
    name, s, ts = w
    assert name == "add_two"
    assert s != ts
    assert R_parity.observe(s) == R_parity.observe(ts)


def test_has_nontrivial_element() -> None:
    K = GeneralizedKernel(R_parity)
    K.register(lambda n: n + 2, "add_two", STATES)
    assert K.has_nontrivial_element(STATES)


def test_no_nontrivial_element_for_injective_map() -> None:
    # R = identity is injective over STATES
    R_id = ObservationMap(lambda n: n, name="identity")
    K = GeneralizedKernel(R_id)
    K.register(lambda n: n + 1, "add_one", STATES[:-1])  # avoid out-of-range
    assert not K.has_nontrivial_element(STATES[:-1])


# ===========================================================================
# 3. Quotient space — S / ~_R
# ===========================================================================

def test_quotient_has_two_classes() -> None:
    Q = QuotientSpace(STATES, R_parity)
    assert Q.size == 2


def test_quotient_not_injective() -> None:
    Q = QuotientSpace(STATES, R_parity)
    assert not Q.is_injective()


def test_quotient_injective_for_injective_map() -> None:
    R_id = ObservationMap(lambda n: n)
    Q = QuotientSpace(STATES, R_id)
    assert Q.is_injective()


def test_nontrivial_fibers_reported() -> None:
    Q = QuotientSpace(STATES, R_parity)
    nontrivial = Q.nontrivial_fibers()
    assert len(nontrivial) == 2
    assert all(len(f) == 5 for f in nontrivial)


def test_information_loss_ratio() -> None:
    Q = QuotientSpace(STATES, R_parity)
    assert Q.information_loss_ratio() == 1.0  # all states in non-trivial fibers

    R_id = ObservationMap(lambda n: n)
    Q_id = QuotientSpace(STATES, R_id)
    assert Q_id.information_loss_ratio() == 0.0


def test_fiber_of_returns_correct_fiber() -> None:
    Q = QuotientSpace(STATES, R_parity)
    f = Q.fiber_of(0)
    assert f is not None
    assert 0 in f
    assert 2 in f
    assert 1 not in f


# ===========================================================================
# 4. Reconstruction
# ===========================================================================

def test_reconstruction_returns_fiber() -> None:
    rec = Reconstructor(R_parity, STATES)
    candidates = rec.reconstruct(0)
    assert set(candidates) == {0, 2, 4, 6, 8}


def test_reconstruction_not_faithful() -> None:
    rec = Reconstructor(R_parity, STATES)
    assert not rec.is_faithful()


def test_reconstruction_faithful_for_injective() -> None:
    R_id = ObservationMap(lambda n: n)
    rec = Reconstructor(R_id, STATES)
    assert rec.is_faithful()


def test_is_unique_fails_for_parity() -> None:
    rec = Reconstructor(R_parity, STATES)
    assert not rec.is_unique(0)
    assert not rec.is_unique(1)


def test_ambiguous_observations_listed() -> None:
    rec = Reconstructor(R_parity, STATES)
    ambiguous = rec.ambiguous_observations()
    assert len(ambiguous) == 2
    for obs, states in ambiguous:
        assert len(states) == 5


def test_sufficient_for_parity_itself() -> None:
    rec = Reconstructor(R_parity, STATES)
    # R is sufficient for "is even?" — same parity class → same parameter
    assert rec.is_sufficient_for(lambda n: n % 2, STATES)


def test_not_sufficient_for_exact_value() -> None:
    rec = Reconstructor(R_parity, STATES)
    # R is not sufficient for the exact value (parity doesn't determine n)
    assert not rec.is_sufficient_for(lambda n: n, STATES)


# ===========================================================================
# 5. Linter as observation map — explicit fiber example
# ===========================================================================
# The authority linter is R: {documents} → {warning sets}.
# This test demonstrates that V1 has a non-trivial fiber:
# Document A has an explicit HARD violation.
# Document B has a semantic authority claim V1 misses.
# Both with receipt present → R(A) = R(B) = PASS, but A ≠ B.
# This is an explicit kernel element of the linter map.

def test_linter_as_observation_map() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "validators"))
    from authority_language_linter import lint_text

    def linter_receipt(doc: str) -> str:
        return lint_text(doc).verdict

    R_lint = ObservationMap(linter_receipt, name="authority_linter_v1")

    # Both are clean — R(A) = R(B) = "PASS"
    doc_a = "HAL recommends proceeding. REDUCER: NOT_INVOKED. ledger_effect: none."
    doc_b = "The official decision is final. The system has determined this path."

    assert R_lint.observe(doc_a) == "PASS"
    assert R_lint.observe(doc_b) == "PASS"

    # They are observationally equivalent under V1
    assert R_lint.are_equivalent(doc_a, doc_b)

    # But they are not the same document
    assert doc_a != doc_b

    # The fiber of doc_a contains doc_b — this IS the semantic gap
    docs = [doc_a, doc_b]
    fiber = R_lint.fiber(doc_a, docs)
    assert doc_b in fiber  # explicit kernel element

    # Quotient space: both documents collapse to the same class
    Q = QuotientSpace(docs, R_lint)
    assert Q.size == 1              # one observation (PASS) for both
    assert not Q.is_injective()     # cannot distinguish the two documents


def test_linter_detects_hard_violation() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "validators"))
    from authority_language_linter import lint_text

    R_lint = ObservationMap(lambda doc: lint_text(doc).verdict, name="linter")

    bad = "REDUCER admits: done."
    good = "HAL recommends: done. REDUCER: NOT_INVOKED."

    # R separates these two documents — different observations
    assert R_lint.observe(bad) == "BLOCK"
    assert R_lint.observe(good) == "PASS"
    assert not R_lint.are_equivalent(bad, good)


# ===========================================================================
# 6. Toy embedding map — semantic invisible transforms
# ===========================================================================

def test_embedding_map_invisible_transform() -> None:
    # Toy embedding: maps strings to word-count features (bag-of-words simplified)
    def embed(text: str) -> frozenset[str]:
        return frozenset(text.lower().split())

    R_embed = ObservationMap(embed, name="bag_of_words")

    # Different word orders → same embedding
    s1 = "cat ate fish"
    s2 = "fish ate cat"

    assert R_embed.are_equivalent(s1, s2)
    assert s1 != s2

    # The permutation transform is invisible
    def swap_words(text: str) -> str:
        words = text.split()
        return " ".join(reversed(words))

    K = GeneralizedKernel(R_embed)
    assert K.is_invisible(swap_words, [s1, s2])
    assert K.is_nontrivial(swap_words, [s1, s2])
