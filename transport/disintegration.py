"""Finite disintegration — the computable shadow of the disintegration theorem.

GENERAL THEOREM (Volume II, Ch. 3 — prose, not code).
If S and L are standard Borel and R : S → L is Borel measurable, then for any
probability measure μ on S with pushforward ν = R_*μ there is a ν-a.e. uniquely
determined family of regular conditional probabilities

    ℓ ↦ μ_ℓ ,     μ_ℓ(R⁻¹(ℓ)) = 1   (for ν-almost every ℓ),

such that

    μ = ∫_L μ_ℓ d ν(ℓ).

This requires standardness; it is genuinely infinitary and is NOT implemented.

FINITE CASE (this module).
When S is finite and μ is a probability mass function, the theorem holds with no
measure-theoretic subtlety: the fibers partition S, ν(ℓ) is the fiber mass, and
μ_ℓ is the normalized restriction of μ to the fiber. Everything is exact and
"ν-a.e." becomes "for every realized ℓ". This is the honest finite witness.

Information loss (finite case). Because R is a deterministic function of the
state, H(S, R) = H(S), so the chain rule gives the exact decomposition

    H(S) = H(ν) + H(S | R),     H(S | R) = Σ_ℓ ν(ℓ) H(μ_ℓ).

H(S | R) is the residual uncertainty inside the observational fiber — the
information the receipt cannot recover. In the finite case Shannon entropy is
canonical, so this is a precise statement, not an overclaim.

NOTE. A conditional μ_ℓ is a probability measure ON the fiber. It does NOT by
itself make the fiber a statistical manifold. Fisher–Rao / KL geometry needs a
SEPARATE assumption — that states carry probability laws p_s — and is Chapter 4,
not this module.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

from transport.observation import ObservationMap, _hashable, group_by_observation


def shannon_entropy(pmf: dict[Any, float], base: float = 2.0) -> float:
    """H(p) = -Σ p log p over the support. Empty/point mass → 0."""
    h = 0.0
    for p in pmf.values():
        if p > 0.0:
            h -= p * math.log(p, base)
    return h


class FiniteDisintegration:
    """Finite disintegration of a pmf μ over an observation map R.

    weights : dict mapping each state to its μ-mass. Normalized internally.
    """

    def __init__(
        self,
        R: ObservationMap,
        weights: dict[Any, float],
    ) -> None:
        self.R = R
        for s, w in weights.items():
            if w < 0.0:
                raise ValueError(f"negative weight for state {s!r}: {w}")
        total = sum(weights.values())
        if total <= 0.0:
            raise ValueError("total mass must be positive")
        # normalized μ over states
        self._mu: dict[Any, float] = {s: w / total for s, w in weights.items()}
        # group states into fibers keyed by observation
        grouped = group_by_observation(R, self._mu)
        self._fiber_states: dict[Any, list[Any]] = {k: v[1] for k, v in grouped.items()}
        self._obs_of_key: dict[Any, Any] = {k: v[0] for k, v in grouped.items()}

    # ------------------------------------------------------------------
    # ν = R_*μ  (pushforward — what the observer can see)

    def pushforward(self) -> dict[Any, float]:
        """ν(ℓ) = μ(R⁻¹(ℓ)): the receipt distribution.

        Keyed by the canonical hashable form of each observation (identical to
        the observation itself whenever it is hashable).
        """
        return {
            key: sum(self._mu[s] for s in states)
            for key, states in self._fiber_states.items()
        }

    # ------------------------------------------------------------------
    # μ_ℓ = μ(· | R = ℓ)  (conditional, supported on the fiber)

    def conditional(self, observation: Any) -> dict[Any, float]:
        """μ_ℓ: normalized restriction of μ to the fiber over `observation`."""
        return self._conditional_by_key(_hashable(observation))

    def _conditional_by_key(self, key: Any) -> dict[Any, float]:
        states = self._fiber_states.get(key, [])
        mass = sum(self._mu[s] for s in states)
        if mass <= 0.0:
            return {}
        return {s: self._mu[s] / mass for s in states}

    # ------------------------------------------------------------------
    # The disintegration identity (finite, exact)

    def reconstructs(self, abs_tol: float = 1e-12) -> bool:
        """Verify μ(s) = ν(ℓ_s) · μ_{ℓ_s}(s) for every state — i.e.
        μ = Σ_ℓ ν(ℓ) μ_ℓ, the finite form of μ = ∫ μ_ℓ dν.
        """
        nu = self.pushforward()
        for key, states in self._fiber_states.items():
            cond = self._conditional_by_key(key)
            for s in states:
                recon = nu[key] * cond[s]
                if not math.isclose(recon, self._mu[s], abs_tol=abs_tol):
                    return False
        return True

    # ------------------------------------------------------------------
    # Entropy decomposition (finite case — Shannon is canonical here)

    def entropy_total(self, base: float = 2.0) -> float:
        """H(S)."""
        return shannon_entropy(self._mu, base)

    def entropy_observed(self, base: float = 2.0) -> float:
        """H(ν) = H(R_*μ): entropy the observer actually sees."""
        return shannon_entropy(self.pushforward(), base)

    def conditional_entropy(self, base: float = 2.0) -> float:
        """H(S | R) = Σ_ℓ ν(ℓ) H(μ_ℓ): residual uncertainty inside fibers.

        This is the information the receipt cannot recover — the quantitative
        measure of observational information loss.
        """
        h = 0.0
        for key, weight in self.pushforward().items():
            h += weight * shannon_entropy(self._conditional_by_key(key), base)
        return h

    def satisfies_chain_rule(self, base: float = 2.0, abs_tol: float = 1e-12) -> bool:
        """H(S) = H(ν) + H(S | R) — exact because R is a function of S."""
        lhs = self.entropy_total(base)
        rhs = self.entropy_observed(base) + self.conditional_entropy(base)
        return math.isclose(lhs, rhs, abs_tol=abs_tol)

    def __repr__(self) -> str:
        return (
            f"FiniteDisintegration(states={len(self._mu)}, "
            f"receipts={len(self._fiber_states)}, "
            f"H(S|R)={self.conditional_entropy():.4f})"
        )
