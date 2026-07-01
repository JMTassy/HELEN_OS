"""Fiber-bundle structure of an observation map.

The triple (S, R, L) is exactly the data of a bundle projection

    S ──R──▶ L,     fiber over ℓ  =  R^{-1}(ℓ).

This module computes coarse bundle invariants without assuming any topology
beyond what R provides:

    - the fiber-size profile (cardinality of each fiber)
    - whether the bundle is "size-trivial" (all fibers equinumerous)
    - a discrete curvature κ_R(ℓ): how much the fiber varies between a receipt
      and its neighbours under a supplied neighbourhood relation on L.

These are V0 invariants. Intrinsic fiber geometry (metric, topology, measure,
manifold structure) is a richer program — see TRANSPORT_THEORY_V1 notes.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable

from transport.observation import ObservationMap, _hashable, group_by_observation


class ObservationBundle:
    """Bundle (S, R, L) with fiber-cardinality invariants."""

    def __init__(self, state_space: Iterable[Any], R: ObservationMap) -> None:
        self.R = R
        grouped = group_by_observation(R, state_space)
        self._fibers: dict[Any, list[Any]] = {k: v[1] for k, v in grouped.items()}
        self._obs: dict[Any, Any] = {k: v[0] for k, v in grouped.items()}

    # ------------------------------------------------------------------
    # Cardinality invariants

    def fiber_size_profile(self) -> dict[Any, int]:
        """Map each observation (canonical hashable form) to its fiber size."""
        return {k: len(v) for k, v in self._fibers.items()}

    def is_size_trivial(self) -> bool:
        """True iff all fibers have equal cardinality.

        A locally-trivial bundle has isomorphic fibers; equal cardinality is
        the coarsest necessary condition (a first obstruction check).
        """
        sizes = {len(v) for v in self._fibers.values()}
        return len(sizes) <= 1

    def base_size(self) -> int:
        """Number of distinct receipts (cardinality of the realized base)."""
        return len(self._fibers)

    # ------------------------------------------------------------------
    # Discrete curvature

    def curvature(
        self,
        observation: Any,
        neighbors: Callable[[Any], Iterable[Any]],
    ) -> float:
        """κ_R(ℓ): mean |#fiber(ℓ) − #fiber(ℓ')| over neighbours ℓ' of ℓ.

        `neighbors(ℓ)` supplies the neighbourhood relation on L. Curvature is
        zero where adjacent fibers have equal size, large where the fiber
        changes abruptly between nearby receipts.

        This is a size-based (coarse) curvature. A finer curvature would
        compare fiber structure, not just cardinality.
        """
        key = _hashable(observation)
        here = len(self._fibers.get(key, []))
        diffs = []
        for nb in neighbors(observation):
            nb_key = _hashable(nb)
            there = len(self._fibers.get(nb_key, []))
            diffs.append(abs(here - there))
        if not diffs:
            return 0.0
        return sum(diffs) / len(diffs)

    def __repr__(self) -> str:
        return (
            f"ObservationBundle(base={self.base_size()}, "
            f"size_trivial={self.is_size_trivial()})"
        )
