"""Tests for Volume II Chapter 4 — Information Geometry.

The 10 required cases:
    1.  KL(p,p) = 0
    2.  Hellinger(p,p) = 0
    3.  total variation symmetry
    4.  KL non-symmetry example
    5.  co-fiber states can have different p_s
    6.  observation-equivalent states distinguishable only if p_s differs
    7.  no geometry is produced without p_s
    8.  zero-probability KL handled explicitly
    9.  finite Fisher information smoke test
    10. Chapter 3 disintegration tests still pass (imported + re-run marker)

No HELEN imports.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from transport.observation import ObservationMap
from transport.statistical import (
    StatisticalState,
    StatisticalObservationModel,
    finite_probability_law,
    kl_divergence,
    hellinger_distance,
    total_variation_distance,
    fisher_information_1d,
)


P = finite_probability_law({"h": 0.5, "t": 0.5})
Q = finite_probability_law({"h": 0.9, "t": 0.1})
Pa = finite_probability_law({"a": 0.7, "b": 0.2, "c": 0.1})


# ===========================================================================
# 1. KL(p,p) = 0
# ===========================================================================

def test_kl_self_is_zero() -> None:
    assert math.isclose(kl_divergence(P, P), 0.0, abs_tol=1e-12)
    assert math.isclose(kl_divergence(Pa, Pa), 0.0, abs_tol=1e-12)


# ===========================================================================
# 2. Hellinger(p,p) = 0
# ===========================================================================

def test_hellinger_self_is_zero() -> None:
    assert math.isclose(hellinger_distance(P, P), 0.0, abs_tol=1e-12)
    assert math.isclose(hellinger_distance(Pa, Pa), 0.0, abs_tol=1e-12)


# ===========================================================================
# 3. total variation symmetry
# ===========================================================================

def test_tv_symmetry() -> None:
    assert math.isclose(
        total_variation_distance(P, Q), total_variation_distance(Q, P)
    )


def test_tv_value_and_range() -> None:
    # TV between {.5,.5} and {.9,.1} = 0.5*(0.4+0.4) = 0.4
    assert math.isclose(total_variation_distance(P, Q), 0.4)
    assert 0.0 <= total_variation_distance(P, Q) <= 1.0


# ===========================================================================
# 4. KL non-symmetry example
# ===========================================================================

def test_kl_is_not_symmetric() -> None:
    forward = kl_divergence(P, Q)
    backward = kl_divergence(Q, P)
    assert not math.isclose(forward, backward)
    assert forward > 0.0 and backward > 0.0


# ===========================================================================
# 5. co-fiber states can have different p_s
# ===========================================================================

def test_cofiber_states_can_differ_statistically() -> None:
    # Both states observe to the SAME receipt under R, but carry different laws.
    R = ObservationMap(lambda s: "same", name="collapse_all")
    s1 = StatisticalState("s1", {"h": 0.5, "t": 0.5})
    s2 = StatisticalState("s2", {"h": 0.9, "t": 0.1})
    model = StatisticalObservationModel(R, [s1, s2])
    assert model.are_cofiber(s1, s2)        # R-indistinguishable
    assert model.total_variation(s1, s2) > 0.0  # but laws differ


# ===========================================================================
# 6. observation-equivalent states distinguishable only if p_s differs
# ===========================================================================

def test_cofiber_identical_laws_are_indistinguishable() -> None:
    R = ObservationMap(lambda s: "same", name="collapse_all")
    s1 = StatisticalState("s1", {"h": 0.5, "t": 0.5})
    s2 = StatisticalState("s2", {"h": 0.5, "t": 0.5})  # same law
    model = StatisticalObservationModel(R, [s1, s2])
    assert model.are_cofiber(s1, s2)
    assert not model.statistically_distinguishable(s1, s2)
    assert math.isclose(model.total_variation(s1, s2), 0.0, abs_tol=1e-12)


def test_distinguishability_comes_from_law_not_R() -> None:
    R = ObservationMap(lambda s: "same", name="collapse_all")
    same = StatisticalState("x", {"h": 0.4, "t": 0.6})
    diff = StatisticalState("y", {"h": 0.6, "t": 0.4})
    base = StatisticalState("z", {"h": 0.4, "t": 0.6})
    model = StatisticalObservationModel(R, [base, same, diff])
    # all three are co-fiber; only the one with a different law is distinguishable
    assert model.statistically_distinguishable(base, diff)
    assert not model.statistically_distinguishable(base, same)


# ===========================================================================
# 7. no geometry is produced without p_s
# ===========================================================================

def test_no_law_means_no_state_constructed() -> None:
    # A StatisticalState cannot exist without a law — empty law is rejected.
    with pytest.raises(ValueError):
        StatisticalState("s", {})


def test_bare_observation_map_has_no_metric() -> None:
    # The plain ObservationMap exposes no statistical distance — geometry is an
    # added hypothesis, not a property of R.
    R = ObservationMap(lambda s: s % 2, name="parity")
    assert not hasattr(R, "kl_divergence")
    assert not hasattr(R, "fisher_information")


# ===========================================================================
# 8. zero-probability KL handled explicitly
# ===========================================================================

def test_kl_infinite_when_not_absolutely_continuous() -> None:
    # p puts mass where q has none → KL = +∞, returned explicitly.
    p = finite_probability_law({"a": 0.5, "b": 0.5})
    q = finite_probability_law({"a": 1.0})  # q(b) = 0
    assert kl_divergence(p, q) == math.inf


def test_kl_zero_times_log_zero_is_zero() -> None:
    # p(b) = 0 where q(b) > 0 contributes 0, not NaN.
    p = finite_probability_law({"a": 1.0})
    q = finite_probability_law({"a": 0.5, "b": 0.5})
    val = kl_divergence(p, q)
    assert math.isfinite(val)
    assert math.isclose(val, math.log(2.0, 2.0))  # = 1 bit


# ===========================================================================
# 9. finite Fisher information smoke test
# ===========================================================================

def test_fisher_information_1d_smoke() -> None:
    # Bernoulli family p_θ = {1: θ, 0: 1-θ}. True Fisher info = 1/(θ(1-θ)).
    def law_of(theta: float) -> dict[int, float]:
        return {1: theta, 0: 1.0 - theta}

    grid = [0.3, 0.4, 0.5, 0.6, 0.7]
    info = fisher_information_1d(grid, law_of)
    assert len(info) == len(grid) - 2  # interior points only
    assert all(v > 0.0 for v in info)
    # at θ=0.5 the analytic Fisher info is 1/(0.5*0.5) = 4 (nats);
    # in bits the finite-difference estimate is positive and finite — smoke only
    assert all(math.isfinite(v) for v in info)


def test_fisher_information_short_grid_returns_empty() -> None:
    assert fisher_information_1d([0.5], lambda t: {1: t, 0: 1 - t}) == []
    assert fisher_information_1d([0.4, 0.6], lambda t: {1: t, 0: 1 - t}) == []


# ===========================================================================
# 10. Chapter 3 disintegration still intact (regression guard)
# ===========================================================================

def test_chapter_3_disintegration_still_works() -> None:
    from transport.disintegration import FiniteDisintegration

    R = ObservationMap(lambda s: 0 if s in ("a", "b") else 1, name="pair")
    dis = FiniteDisintegration(R, {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25})
    assert dis.reconstructs()
    assert dis.satisfies_chain_rule()
    assert math.isclose(dis.conditional_entropy(), 1.0)
