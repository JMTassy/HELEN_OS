"""Tests for finite disintegration — Volume II Chapter 3 (computable shadow).

Covers:
    - pushforward ν = R_*μ
    - conditional μ_ℓ supported on the fiber, a pmf
    - the disintegration identity μ = Σ_ℓ ν(ℓ) μ_ℓ (finite form of ∫ μ_ℓ dν)
    - conditional entropy H(S|R) = Σ_ℓ ν(ℓ) H(μ_ℓ)
    - the information-loss chain rule H(S) = H(ν) + H(S|R)
    - boundary cases: injective R (no loss), constant R (total loss)

No HELEN imports.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transport.observation import ObservationMap
from transport.disintegration import FiniteDisintegration, shannon_entropy


# Worked example: S = {a,b,c,d} uniform; R groups {a,b}→0, {c,d}→1.
STATES4 = {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}
R_pair = ObservationMap(lambda s: 0 if s in ("a", "b") else 1, name="pair")
R_id4 = ObservationMap(lambda s: s, name="id4")
R_const4 = ObservationMap(lambda s: "*", name="const4")


# ===========================================================================
# Entropy helper
# ===========================================================================

def test_entropy_uniform_two_is_one_bit() -> None:
    assert math.isclose(shannon_entropy({"x": 0.5, "y": 0.5}), 1.0)


def test_entropy_point_mass_is_zero() -> None:
    assert shannon_entropy({"x": 1.0}) == 0.0


def test_entropy_uniform_four_is_two_bits() -> None:
    pmf = {k: 0.25 for k in "abcd"}
    assert math.isclose(shannon_entropy(pmf), 2.0)


# ===========================================================================
# Pushforward
# ===========================================================================

def test_pushforward_is_a_pmf() -> None:
    dis = FiniteDisintegration(R_pair, STATES4)
    nu = dis.pushforward()
    assert math.isclose(sum(nu.values()), 1.0)


def test_pushforward_masses() -> None:
    dis = FiniteDisintegration(R_pair, STATES4)
    nu = dis.pushforward()
    assert math.isclose(nu[0], 0.5)
    assert math.isclose(nu[1], 0.5)


# ===========================================================================
# Conditionals
# ===========================================================================

def test_conditional_is_supported_on_fiber() -> None:
    dis = FiniteDisintegration(R_pair, STATES4)
    mu0 = dis.conditional(0)
    assert set(mu0.keys()) == {"a", "b"}
    assert math.isclose(sum(mu0.values()), 1.0)


def test_conditional_values() -> None:
    dis = FiniteDisintegration(R_pair, STATES4)
    mu0 = dis.conditional(0)
    assert math.isclose(mu0["a"], 0.5)
    assert math.isclose(mu0["b"], 0.5)


# ===========================================================================
# Disintegration identity  μ = Σ_ℓ ν(ℓ) μ_ℓ
# ===========================================================================

def test_reconstructs_uniform() -> None:
    dis = FiniteDisintegration(R_pair, STATES4)
    assert dis.reconstructs()


def test_reconstructs_nonuniform() -> None:
    weights = {"a": 0.1, "b": 0.4, "c": 0.2, "d": 0.3}
    dis = FiniteDisintegration(R_pair, weights)
    assert dis.reconstructs()


# ===========================================================================
# Conditional entropy + the information-loss chain rule
# ===========================================================================

def test_conditional_entropy_worked_example() -> None:
    # μ_0, μ_1 each uniform on 2 → H = 1 bit each; H(S|R) = 1 bit.
    dis = FiniteDisintegration(R_pair, STATES4)
    assert math.isclose(dis.conditional_entropy(), 1.0)


def test_chain_rule_worked_example() -> None:
    # H(S)=2, H(ν)=1, H(S|R)=1 → 2 = 1 + 1.
    dis = FiniteDisintegration(R_pair, STATES4)
    assert math.isclose(dis.entropy_total(), 2.0)
    assert math.isclose(dis.entropy_observed(), 1.0)
    assert dis.satisfies_chain_rule()


def test_chain_rule_holds_for_nonuniform() -> None:
    weights = {"a": 0.1, "b": 0.4, "c": 0.2, "d": 0.3}
    dis = FiniteDisintegration(R_pair, weights)
    assert dis.satisfies_chain_rule()


# ===========================================================================
# Boundary cases
# ===========================================================================

def test_injective_map_has_zero_information_loss() -> None:
    dis = FiniteDisintegration(R_id4, STATES4)
    assert math.isclose(dis.conditional_entropy(), 0.0)
    # all the entropy is observed
    assert math.isclose(dis.entropy_observed(), dis.entropy_total())
    assert dis.satisfies_chain_rule()


def test_constant_map_loses_everything() -> None:
    dis = FiniteDisintegration(R_const4, STATES4)
    # observer sees nothing: H(ν) = 0
    assert math.isclose(dis.entropy_observed(), 0.0)
    # all uncertainty is residual: H(S|R) = H(S)
    assert math.isclose(dis.conditional_entropy(), dis.entropy_total())
    assert dis.satisfies_chain_rule()


def test_constant_map_single_fiber_is_full_space() -> None:
    dis = FiniteDisintegration(R_const4, STATES4)
    mu = dis.conditional("*")
    assert set(mu.keys()) == set("abcd")
    assert math.isclose(sum(mu.values()), 1.0)
