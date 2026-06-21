"""Reconstruction — can we recover state from observation?

Given R : S → L and an observation ℓ ∈ L, reconstruction asks:
    which states S ∈ R⁻¹(ℓ) are consistent with ℓ?

If R⁻¹(ℓ) is a singleton: unique reconstruction possible.
If R⁻¹(ℓ) has multiple members: reconstruction is ambiguous.
If R⁻¹(ℓ) is empty: observation ℓ has no pre-image in the given space.

Faithfulness criterion: R is faithful iff reconstruction is unique everywhere.
"""
from __future__ import annotations

from typing import Any, Iterable

from transport.observation import ObservationMap, _hashable
from transport.fiber import FiberSet


class Reconstructor:
    """Attempt state reconstruction from observations.

    Builds an inverse index R⁻¹ over the provided state space.
    """

    def __init__(self, R: ObservationMap, state_space: Iterable[Any]) -> None:
        self.R = R
        self._index: dict[Any, list[Any]] = {}
        self._obs_map: dict[Any, Any] = {}
        self._build(state_space)

    def _build(self, state_space: Iterable[Any]) -> None:
        for s in state_space:
            obs = self.R.observe(s)
            key = _hashable(obs)
            self._index.setdefault(key, []).append(s)
            self._obs_map[key] = obs

    # ------------------------------------------------------------------
    # Reconstruction

    def reconstruct(self, observation: Any) -> list[Any]:
        """Return all states consistent with observation.

        Empty list if observation has no pre-image in the state space.
        """
        key = _hashable(observation)
        return list(self._index.get(key, []))

    def fiber_for(self, observation: Any) -> FiberSet:
        """Return the FiberSet for a given observation."""
        key = _hashable(observation)
        members = self._index.get(key, [])
        return FiberSet(observation=observation, members=members)

    # ------------------------------------------------------------------
    # Faithfulness

    def is_unique(self, observation: Any) -> bool:
        """True iff the observation uniquely determines a state."""
        return len(self.reconstruct(observation)) == 1

    def is_faithful(self) -> bool:
        """True iff every observation has exactly one pre-image.

        Equivalent to R being injective over the state space.
        """
        return all(len(v) == 1 for v in self._index.values())

    def ambiguous_observations(self) -> list[tuple[Any, list[Any]]]:
        """Return (observation, states) pairs where reconstruction is ambiguous.

        Each entry is a witness that R is not injective at that observation.
        """
        return [
            (self._obs_map[key], members)
            for key, members in self._index.items()
            if len(members) > 1
        ]

    # ------------------------------------------------------------------
    # Minimal sufficient receipt

    def is_sufficient_for(
        self,
        parameter_fn: Any,
        state_space: Iterable[Any],
    ) -> bool:
        """Test if R is sufficient for parameter_fn.

        R is sufficient for θ = parameter_fn(S) iff R(S) determines θ(S):
        i.e., S1 ~_R S2 ⟹ parameter_fn(S1) = parameter_fn(S2).

        If False, the receipt cannot determine the parameter — information lost.
        """
        states = list(state_space)
        for key, members in self._index.items():
            params = {parameter_fn(s) for s in members}
            if len(params) > 1:
                return False
        return True

    def __repr__(self) -> str:
        n_obs = len(self._index)
        n_states = sum(len(v) for v in self._index.values())
        return (
            f"Reconstructor(observations={n_obs}, states={n_states}, "
            f"faithful={self.is_faithful()})"
        )
