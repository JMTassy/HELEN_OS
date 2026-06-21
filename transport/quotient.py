"""Observable quotient space S / ~_R.

The observer never sees S. They see only S / ~_R.
Each element of the quotient is an equivalence class [S]_R.

This is the observable universe induced by R.
"""
from __future__ import annotations

from typing import Any, Iterable

from transport.observation import ObservationMap, _hashable
from transport.fiber import FiberSet


class QuotientSpace:
    """S / ~_R — partition of state space into observational equivalence classes.

    Constructed from a state space and an observation map.
    """

    def __init__(
        self,
        state_space: Iterable[Any],
        R: ObservationMap,
    ) -> None:
        self.R = R
        self._fibers: dict[Any, FiberSet] = {}
        self._build(state_space)

    def _build(self, state_space: Iterable[Any]) -> None:
        buckets: dict[Any, list[Any]] = {}
        obs_for_key: dict[Any, Any] = {}
        for s in state_space:
            obs = self.R.observe(s)
            key = _hashable(obs)
            buckets.setdefault(key, []).append(s)
            obs_for_key[key] = obs
        for key, members in buckets.items():
            self._fibers[key] = FiberSet(
                observation=obs_for_key[key],
                members=members,
            )

    # ------------------------------------------------------------------
    # Properties

    @property
    def classes(self) -> list[FiberSet]:
        """All equivalence classes."""
        return list(self._fibers.values())

    @property
    def size(self) -> int:
        """Number of distinct observations (dimension of quotient)."""
        return len(self._fibers)

    # ------------------------------------------------------------------
    # Faithfulness / injectivity

    def is_injective(self) -> bool:
        """R is injective iff every fiber is a singleton.

        Equivalently: S / ~_R ≅ S (no information loss).
        """
        return all(f.is_trivial() for f in self._fibers.values())

    def nontrivial_fibers(self) -> list[FiberSet]:
        """Fibers with more than one member — sites of information loss."""
        return [f for f in self._fibers.values() if not f.is_trivial()]

    def information_loss_ratio(self) -> float:
        """Fraction of states that are in non-trivial fibers.

        0.0 = R is injective (no loss).
        1.0 = all states are indistinguishable.
        """
        total = sum(len(f) for f in self._fibers.values())
        if total == 0:
            return 0.0
        lost = sum(len(f) for f in self.nontrivial_fibers())
        return lost / total

    # ------------------------------------------------------------------
    # Lookup

    def fiber_of(self, state: Any) -> FiberSet | None:
        """Return the equivalence class containing state, or None."""
        obs = self.R.observe(state)
        key = _hashable(obs)
        return self._fibers.get(key)

    def __repr__(self) -> str:
        return (
            f"QuotientSpace(classes={self.size}, "
            f"injective={self.is_injective()}, "
            f"loss={self.information_loss_ratio():.2%})"
        )
