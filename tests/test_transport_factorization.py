"""Tests for the Fundamental Factorization Theorem and Volume I refinements.

Covers:
    - Factorization: R = R_bar ∘ q_R with R_bar injective (the center of Vol I)
    - universal_factor: Observable Universality (universal property of S/~_R)
    - GeneralizedKernel.acts_fiberwise / preserves_fiber (Inv(R) acts fiberwise)
    - Reconstructor.section / section_is_valid (section honest about Choice)

No HELEN imports.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transport.observation import ObservationMap
from transport.kernel import GeneralizedKernel
from transport.reconstruction import Reconstructor
from transport.factorization import Factorization, universal_factor


STATES = list(range(10))  # 0..9
R_parity = ObservationMap(lambda n: n % 2, name="parity")
R_id = ObservationMap(lambda n: n, name="id")


# ===========================================================================
# Fundamental Factorization Theorem
# ===========================================================================

def test_factorization_identity() -> None:
    fac = Factorization(R_parity, STATES)
    assert fac.factorizes(STATES)  # R(s) = R_bar(q_R(s))


def test_r_bar_is_injective() -> None:
    fac = Factorization(R_parity, STATES)
    assert fac.r_bar_is_injective()


def test_quotient_size_matches_distinct_observations() -> None:
    fac = Factorization(R_parity, STATES)
    assert fac.quotient_size == 2  # even, odd

    fac_id = Factorization(R_id, STATES)
    assert fac_id.quotient_size == 10  # all distinct


def test_q_sends_equivalent_states_to_same_class() -> None:
    fac = Factorization(R_parity, STATES)
    assert fac.q(0) == fac.q(2) == fac.q(4)
    assert fac.q(1) == fac.q(3) == fac.q(5)
    assert fac.q(0) != fac.q(1)


def test_r_bar_recovers_observation() -> None:
    fac = Factorization(R_parity, STATES)
    cls_even = fac.q(0)
    cls_odd = fac.q(1)
    assert fac.r_bar(cls_even) == 0
    assert fac.r_bar(cls_odd) == 1


def test_factorization_is_universal_for_identity_map() -> None:
    # When R is injective, the quotient is S itself and R_bar is a bijection.
    fac = Factorization(R_id, STATES)
    assert fac.factorizes(STATES)
    assert fac.r_bar_is_injective()
    assert fac.quotient_size == len(STATES)


# ===========================================================================
# Observable Universality (universal property)
# ===========================================================================

def test_universal_factor_exists_for_class_constant_f() -> None:
    # f(n) = "even"/"odd" is constant on parity classes → factors through quotient
    f = lambda n: "even" if n % 2 == 0 else "odd"
    f_tilde = universal_factor(f, R_parity, STATES)
    assert f_tilde is not None
    fac = Factorization(R_parity, STATES)
    # f = f_tilde ∘ q_R
    for s in STATES:
        assert f_tilde(fac.q(s)) == f(s)


def test_universal_factor_none_when_f_splits_a_fiber() -> None:
    # f(n) = n is NOT constant on parity classes → no factorization
    f = lambda n: n
    f_tilde = universal_factor(f, R_parity, STATES)
    assert f_tilde is None


def test_universal_factor_uniqueness_is_automatic() -> None:
    # q_R is surjective, so f_tilde is uniquely determined on every class.
    f = lambda n: (n % 2) * 100
    f_tilde = universal_factor(f, R_parity, STATES)
    assert f_tilde is not None
    fac = Factorization(R_parity, STATES)
    # every class index gets exactly one value
    values = {fac.q(s): f_tilde(fac.q(s)) for s in STATES}
    assert values[fac.q(0)] == 0
    assert values[fac.q(1)] == 100


# ===========================================================================
# Inv(R) acts fiberwise
# ===========================================================================

def test_invisible_transform_acts_fiberwise() -> None:
    K = GeneralizedKernel(R_parity)
    add_two = lambda n: n + 2  # parity-preserving
    assert K.acts_fiberwise(add_two, STATES)


def test_preserves_fiber_inclusion() -> None:
    K = GeneralizedKernel(R_parity)
    add_two = lambda n: n + 2
    # the even fiber {0,2,4,6,8} maps into the even fiber under +2
    assert K.preserves_fiber(add_two, 0, STATES)
    assert K.preserves_fiber(add_two, 1, STATES)


def test_observable_transform_does_not_preserve_fiber() -> None:
    K = GeneralizedKernel(R_parity)
    add_one = lambda n: n + 1  # flips parity
    assert not K.acts_fiberwise(add_one, STATES)
    assert not K.preserves_fiber(add_one, 0, STATES)


# ===========================================================================
# Section (reconstruction map) — honest about Choice
# ===========================================================================

def test_section_satisfies_identity() -> None:
    rec = Reconstructor(R_parity, STATES)
    assert rec.section_is_valid()  # R(C(ℓ)) = ℓ


def test_section_picks_one_representative_per_fiber() -> None:
    rec = Reconstructor(R_parity, STATES)
    sec = rec.section()
    assert len(sec) == 2  # one rep per observation
    # each representative observes back to its key
    for key, rep in sec.items():
        assert (rep % 2) == key


def test_section_valid_for_injective_map() -> None:
    rec = Reconstructor(R_id, STATES)
    assert rec.section_is_valid()
    sec = rec.section()
    assert len(sec) == 10  # singleton fibers — section is the inverse
