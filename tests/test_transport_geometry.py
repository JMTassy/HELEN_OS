"""Tests for transport geometry/category/observer extensions (V1).

Covers:
    - ObserverClass + the Observation Axiom (rules out constant/identity)
    - ObservationMorphism (commuting squares in the category Obs)
    - ObservationBundle (fiber-size invariants, discrete curvature)

No HELEN imports.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transport.observation import ObservationMap
from transport.observer import ObserverClass, is_pathological
from transport.category import (
    ObservationMorphism,
    identity_morphism,
    compose,
)
from transport.bundle import ObservationBundle


STATES = list(range(10))  # 0..9
R_parity = ObservationMap(lambda n: n % 2, name="parity")
R_mod3 = ObservationMap(lambda n: n % 3, name="mod3")
R_const = ObservationMap(lambda n: 0, name="const")
R_id = ObservationMap(lambda n: n, name="id")


# ===========================================================================
# Observation Axiom — observer classes
# ===========================================================================

def test_parity_admissible_for_parity_observer() -> None:
    O = ObserverClass(lambda n: n % 2, name="parity_observer")
    assert O.is_admissible(R_parity, STATES)


def test_parity_sound_but_incomplete_for_full_observer() -> None:
    # Observer that can distinguish everything (ground = identity)
    O_full = ObserverClass(lambda n: n, name="full_observer")
    # parity never distinguishes states the full observer holds identical
    assert O_full.is_sound(R_parity, STATES)
    # but parity cannot distinguish everything the full observer can
    assert not O_full.is_complete(R_parity, STATES)
    assert not O_full.is_admissible(R_parity, STATES)


def test_constant_map_fails_completeness() -> None:
    # Against any non-trivial observer, the constant map sees nothing.
    O = ObserverClass(lambda n: n % 2, name="parity_observer")
    assert not O.is_complete(R_const, STATES)
    assert not O.is_admissible(R_const, STATES)


def test_identity_map_fails_soundness_for_limited_observer() -> None:
    # A limited observer (parity-resolution) — identity distinguishes too much.
    O = ObserverClass(lambda n: n % 2, name="parity_observer")
    assert not O.is_sound(R_id, STATES)
    assert not O.is_admissible(R_id, STATES)


def test_identity_map_admissible_for_full_observer() -> None:
    O_full = ObserverClass(lambda n: n, name="full_observer")
    assert O_full.is_admissible(R_id, STATES)


def test_is_pathological_flags_constant_and_identity() -> None:
    assert is_pathological(R_const, STATES)
    assert is_pathological(R_id, STATES)


def test_is_pathological_passes_genuine_observation() -> None:
    assert not is_pathological(R_parity, STATES)
    assert not is_pathological(R_mod3, STATES)


# ===========================================================================
# Category Obs — commuting squares
# ===========================================================================

def test_identity_morphism_commutes() -> None:
    idm = identity_morphism(R_parity)
    assert idm.commutes_on(STATES)


def test_commuting_square_parity_refines_to_const() -> None:
    # F = id on states, G collapses both parities to a single receipt.
    # R_const = G ∘ R_parity   where G(anything) = 0.
    morphism = ObservationMorphism(
        source=R_parity,
        target=R_const,
        F=lambda s: s,
        G=lambda l: 0,
        name="collapse",
    )
    assert morphism.commutes_on(STATES)


def test_non_commuting_square_detected() -> None:
    # F = id, G = id, but target is mod3 while source is parity — won't commute.
    morphism = ObservationMorphism(
        source=R_parity,
        target=R_mod3,
        F=lambda s: s,
        G=lambda l: l,
        name="broken",
    )
    assert not morphism.commutes_on(STATES)
    v = morphism.violation(STATES)
    assert v is not None
    state, lhs, rhs = v
    assert lhs != rhs


def test_morphism_composition_commutes() -> None:
    # parity → parity (id) then parity → const (collapse); composite must commute.
    m1 = identity_morphism(R_parity)
    m2 = ObservationMorphism(
        source=R_parity,
        target=R_const,
        F=lambda s: s,
        G=lambda l: 0,
        name="collapse",
    )
    comp = compose(m2, m1)
    assert comp.source is R_parity
    assert comp.target is R_const
    assert comp.commutes_on(STATES)


# ===========================================================================
# Bundle invariants + curvature
# ===========================================================================

def test_parity_bundle_is_size_trivial() -> None:
    # parity over 0..9: two fibers of size 5 each → size-trivial.
    bundle = ObservationBundle(STATES, R_parity)
    assert bundle.is_size_trivial()
    assert bundle.base_size() == 2


def test_uneven_bundle_not_size_trivial() -> None:
    # threshold map: {0,1,2} → "low", rest → "high" over 0..9 → sizes 3 and 7.
    R_thresh = ObservationMap(lambda n: "low" if n < 3 else "high", name="thresh")
    bundle = ObservationBundle(STATES, R_thresh)
    assert not bundle.is_size_trivial()
    profile = bundle.fiber_size_profile()
    assert sorted(profile.values()) == [3, 7]


def test_curvature_zero_for_equal_neighbors() -> None:
    bundle = ObservationBundle(STATES, R_parity)
    # both fibers size 5; neighbour of 0 is 1 and vice versa → |5-5| = 0
    neighbors = lambda ell: [1 - ell]  # 0↔1
    assert bundle.curvature(0, neighbors) == 0.0


def test_curvature_positive_for_uneven_neighbors() -> None:
    R_thresh = ObservationMap(lambda n: "low" if n < 3 else "high", name="thresh")
    bundle = ObservationBundle(STATES, R_thresh)
    neighbors = lambda ell: ["high"] if ell == "low" else ["low"]
    # |3 - 7| = 4
    assert bundle.curvature("low", neighbors) == 4.0
