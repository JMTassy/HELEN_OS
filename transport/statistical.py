"""Volume II, Chapter 4 — Information Geometry.

This chapter introduces statistical geometry ONLY after an explicit new
hypothesis. It does NOT follow from disintegration.

    Disintegration (Ch.3) gives μ_ℓ — a probability measure supported ON a fiber.
    That does NOT make the fiber a statistical manifold.

NEW HYPOTHESIS (Chapter 4).
    Each state s ∈ S carries a probability law p_s on a measurable sample
    space X. This is the statistical map

        Π : S → 𝒫(X),   Π(s) = p_s.

    Only with Π in hand can two co-fiber states s, t (R(s) = R(t)) be compared
    through their induced laws p_s, p_t — via KL, Hellinger, total variation,
    or (in the smooth-parameter case) Fisher information.

Information geometry REFINES fibers; it does not replace the quotient or the
disintegration. A fiber that looked like a structureless set in Volume I can,
under Π, carry a genuine statistical geometry. No bundles, no curvature, no
smooth-manifold assumption is made here.
"""
from __future__ import annotations

import math
from typing import Any, Callable, Iterable, Optional

from transport.observation import ObservationMap


# ---------------------------------------------------------------------------
# Finite probability laws
# ---------------------------------------------------------------------------

def finite_probability_law(weights: dict[Any, float]) -> dict[Any, float]:
    """Normalize a dict of non-negative weights into a probability law on X.

    Raises ValueError on empty support, negative weight, or zero total mass.
    """
    if not weights:
        raise ValueError("law has empty support")
    total = 0.0
    for outcome, w in weights.items():
        if w < 0.0:
            raise ValueError(f"negative weight for {outcome!r}: {w}")
        total += w
    if total <= 0.0:
        raise ValueError("total mass must be positive")
    return {x: w / total for x, w in weights.items()}


def _support_union(p: dict[Any, float], q: dict[Any, float]) -> list[Any]:
    return list({*p.keys(), *q.keys()})


# ---------------------------------------------------------------------------
# Divergences and distances between laws (on a common sample space X)
# ---------------------------------------------------------------------------

def kl_divergence(p: dict[Any, float], q: dict[Any, float], base: float = 2.0) -> float:
    """KL(p ‖ q) = Σ_x p(x) log(p(x)/q(x)).

    Convention: 0 log(0/q) = 0. If p(x) > 0 where q(x) = 0, KL is +∞
    (returns math.inf) — the absolute-continuity failure is explicit, never
    silently dropped.
    """
    total = 0.0
    for x in _support_union(p, q):
        px = p.get(x, 0.0)
        if px <= 0.0:
            continue  # 0 log 0 = 0
        qx = q.get(x, 0.0)
        if qx <= 0.0:
            return math.inf  # p not absolutely continuous w.r.t. q
        total += px * math.log(px / qx, base)
    return total


def hellinger_distance(p: dict[Any, float], q: dict[Any, float]) -> float:
    """Hellinger distance H(p, q) = (1/√2) ‖√p − √q‖₂ ∈ [0, 1].

    Symmetric, a true metric, always finite.
    """
    acc = 0.0
    for x in _support_union(p, q):
        acc += (math.sqrt(p.get(x, 0.0)) - math.sqrt(q.get(x, 0.0))) ** 2
    return math.sqrt(acc / 2.0)


def total_variation_distance(p: dict[Any, float], q: dict[Any, float]) -> float:
    """TV(p, q) = (1/2) Σ_x |p(x) − q(x)| ∈ [0, 1]. Symmetric, a metric."""
    acc = 0.0
    for x in _support_union(p, q):
        acc += abs(p.get(x, 0.0) - q.get(x, 0.0))
    return acc / 2.0


def fisher_information_1d(
    theta_grid: list[float],
    law_of: Callable[[float], dict[Any, float]],
) -> list[float]:
    """Discrete 1-D Fisher information along a parameter grid.

    Given a curve θ ↦ p_θ (a parametrized family of finite laws), approximate

        I(θ) = Σ_x p_θ(x) (∂_θ log p_θ(x))²

    by central finite differences of log p_θ(x) on the grid. Returned list is
    aligned with the interior grid points (endpoints dropped — no centred
    derivative there). This is a finite/discrete SMOKE-TEST utility, not a
    claim of smooth-manifold structure.
    """
    if len(theta_grid) < 3:
        return []
    out: list[float] = []
    for i in range(1, len(theta_grid) - 1):
        th_lo, th_mid, th_hi = theta_grid[i - 1], theta_grid[i], theta_grid[i + 1]
        p_lo = law_of(th_lo)
        p_mid = law_of(th_mid)
        p_hi = law_of(th_hi)
        dtheta = th_hi - th_lo
        info = 0.0
        for x in p_mid:
            pmid = p_mid.get(x, 0.0)
            plo = p_lo.get(x, 0.0)
            phi = p_hi.get(x, 0.0)
            if pmid <= 0.0 or plo <= 0.0 or phi <= 0.0:
                continue  # score undefined where the law vanishes; skip
            dlog = (math.log(phi) - math.log(plo)) / dtheta
            info += pmid * dlog * dlog
        out.append(info)
    return out


# ---------------------------------------------------------------------------
# Statistical state and observation model
# ---------------------------------------------------------------------------

class StatisticalState:
    """A state s together with its induced probability law p_s on X.

    This pairing IS the Chapter 4 hypothesis made concrete: a bare state plus
    the law Π(s) = p_s that makes it statistically comparable.
    """

    def __init__(self, state: Any, law: dict[Any, float]) -> None:
        self.state = state
        self.law = finite_probability_law(law)

    def kl_to(self, other: "StatisticalState", base: float = 2.0) -> float:
        return kl_divergence(self.law, other.law, base)

    def hellinger_to(self, other: "StatisticalState") -> float:
        return hellinger_distance(self.law, other.law)

    def tv_to(self, other: "StatisticalState") -> float:
        return total_variation_distance(self.law, other.law)

    def __repr__(self) -> str:
        return f"StatisticalState(state={self.state!r}, |X|={len(self.law)})"


class StatisticalObservationModel:
    """An observation map R together with a statistical map Π : S → 𝒫(X).

    Holds StatisticalStates and an ObservationMap. Lets us ask the Chapter-4
    question: are two observation-equivalent states statistically
    distinguishable? — which is possible iff their laws differ.
    """

    def __init__(
        self,
        R: ObservationMap,
        states: Iterable[StatisticalState],
    ) -> None:
        self.R = R
        self._states = list(states)

    @property
    def states(self) -> list[StatisticalState]:
        return list(self._states)

    def are_cofiber(self, a: StatisticalState, b: StatisticalState) -> bool:
        """R(a) = R(b): a and b lie in the same observational fiber."""
        return self.R.observe(a.state) == self.R.observe(b.state)

    def statistically_distinguishable(
        self,
        a: StatisticalState,
        b: StatisticalState,
        tol: float = 0.0,
    ) -> bool:
        """True iff the induced laws differ (TV > tol).

        Note: distinguishability comes from p_s, NOT from R. Two co-fiber
        states (R-indistinguishable) can still differ statistically — that is
        exactly the refinement Chapter 4 adds over the bare quotient.
        """
        return self.total_variation(a, b) > tol

    def kl(self, a: StatisticalState, b: StatisticalState, base: float = 2.0) -> float:
        return a.kl_to(b, base)

    def hellinger(self, a: StatisticalState, b: StatisticalState) -> float:
        return a.hellinger_to(b)

    def total_variation(self, a: StatisticalState, b: StatisticalState) -> float:
        return a.tv_to(b)

    def cofiber_pairs(self) -> list[tuple[StatisticalState, StatisticalState]]:
        """All unordered co-fiber pairs (candidates for intra-fiber geometry)."""
        pairs = []
        n = len(self._states)
        for i in range(n):
            for j in range(i + 1, n):
                if self.are_cofiber(self._states[i], self._states[j]):
                    pairs.append((self._states[i], self._states[j]))
        return pairs

    def __repr__(self) -> str:
        return f"StatisticalObservationModel(states={len(self._states)})"
