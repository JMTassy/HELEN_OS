"""The Fundamental Factorization Theorem of Observation.

Every observation map factors through its observational quotient:

        q_R                 R_bar
    S ───────▶ S/~_R ───────────▶ L
                   (R_bar injective)

    R = R_bar ∘ q_R,    with R_bar injective.

This is the center of Volume I. Fibers, reconstruction, completeness, and
invisible symmetries are all statements about this one diagram.

The quotient S/~_R is realized abstractly as the set {0, 1, ..., k-1} of class
indices (assigned by first appearance), so that:
    - q_R : S → S/~_R is genuinely a map to an abstract quotient (not to L),
    - R_bar : S/~_R → L is injective by construction (distinct classes carry
      distinct observations).

Companion: the universal property (Observable Universality) — every map
constant on ~_R-classes factors uniquely through q_R.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Optional

from transport.observation import ObservationMap, _hashable


class Factorization:
    """R = R_bar ∘ q_R, the universal factorization through S/~_R."""

    def __init__(self, R: ObservationMap, state_space: Iterable[Any]) -> None:
        self.R = R
        self._index_of_key: dict[Any, int] = {}   # obs-key → class index
        self._obs_of_index: dict[int, Any] = {}    # class index → observation ℓ
        self._next = 0
        for s in state_space:
            obs = R.observe(s)
            key = _hashable(obs)
            if key not in self._index_of_key:
                self._index_of_key[key] = self._next
                self._obs_of_index[self._next] = obs
                self._next += 1

    # ------------------------------------------------------------------
    # The two factors

    def q(self, state: Any) -> int:
        """q_R : S → S/~_R. Sends a state to its observational class index."""
        return self._index_of_key[_hashable(self.R.observe(state))]

    def r_bar(self, cls: int) -> Any:
        """R_bar : S/~_R → L. Sends a class to its (unique) observation."""
        return self._obs_of_index[cls]

    @property
    def quotient_size(self) -> int:
        """|S/~_R| — the number of observational classes."""
        return self._next

    # ------------------------------------------------------------------
    # The theorem, as verifiable predicates

    def factorizes(self, state_space: Iterable[Any]) -> bool:
        """Verify R(s) = R_bar(q_R(s)) for every s — the factorization identity."""
        return all(self.r_bar(self.q(s)) == self.R.observe(s) for s in state_space)

    def r_bar_is_injective(self) -> bool:
        """R_bar is injective: distinct classes carry distinct observations.

        This is the non-trivial content of the factorization theorem.
        """
        keys = [_hashable(o) for o in self._obs_of_index.values()]
        return len(set(keys)) == len(keys)

    def __repr__(self) -> str:
        return (
            f"Factorization(quotient_size={self.quotient_size}, "
            f"injective={self.r_bar_is_injective()})"
        )


def universal_factor(
    f: Callable[[Any], Any],
    R: ObservationMap,
    state_space: Iterable[Any],
) -> Optional[Callable[[int], Any]]:
    """Observable Universality (universal property of the quotient).

    If f : S → X is constant on ~_R-classes (s ~_R t ⟹ f(s) = f(t)), return the
    unique f_tilde : S/~_R → X with f = f_tilde ∘ q_R.

    Returns None if f is NOT constant on ~_R-classes — then no factorization
    exists (the universal property's hypothesis fails).

    The returned f_tilde takes a class index (output of Factorization.q).
    """
    fac = Factorization(R, state_space)
    table: dict[int, Any] = {}
    for s in state_space:
        c = fac.q(s)
        v = f(s)
        if c in table and table[c] != v:
            return None  # f distinguishes states within a fiber — no factorization
        table[c] = v
    return lambda cls: table[cls]
