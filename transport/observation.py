"""Observation map R : S → L.

An observation map takes states to observations (receipts, measurements, outputs).
No linearity, coordinates, or application-specific structure assumed.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable


class ObservationMap:
    """R : S → L.

    Wraps any callable that maps states to observations.
    The callable is the only required input — everything else follows.
    """

    def __init__(self, fn: Callable[[Any], Any], name: str = "R") -> None:
        self._fn = fn
        self.name = name

    def observe(self, state: Any) -> Any:
        """R(state)."""
        return self._fn(state)

    def are_equivalent(self, s1: Any, s2: Any) -> bool:
        """S1 ~_R S2 ⟺ R(S1) = R(S2)."""
        return self._fn(s1) == self._fn(s2)

    def fiber(self, state: Any, state_space: Iterable[Any]) -> list[Any]:
        """[S]_R = { S' ∈ state_space : R(S') = R(S) }.

        Returns all states observationally equivalent to state.
        """
        target = self._fn(state)
        return [s for s in state_space if self._fn(s) == target]

    def partition(self, state_space: Iterable[Any]) -> list[list[Any]]:
        """Partition state_space into observational equivalence classes.

        Returns list of fibers (each fiber is a list of equivalent states).
        """
        classes: dict[Any, list[Any]] = {}
        for s in state_space:
            key = _hashable(self._fn(s))
            classes.setdefault(key, []).append(s)
        return list(classes.values())

    def __repr__(self) -> str:
        return f"ObservationMap(name={self.name!r})"


def _hashable(value: Any) -> Any:
    """Canonical hashable form of a value, for use as a dict key.

    Lists/tuples freeze to tuples (recursively), sets to frozensets, dicts to
    sorted (key, value) tuples. Idempotent: _hashable(_hashable(v)) == _hashable(v).
    """
    if isinstance(value, (list, tuple)):
        return tuple(_hashable(v) for v in value)
    if isinstance(value, set):
        return frozenset(value)
    if isinstance(value, dict):
        return tuple(sorted((k, _hashable(v)) for k, v in value.items()))
    return value


def group_by_observation(
    R: ObservationMap, state_space: Iterable[Any]
) -> dict[Any, tuple[Any, list[Any]]]:
    """Group states into fibers keyed by the canonical form of R(s).

    Returns {key: (observation, [states])} in first-appearance order.
    The single place where the fiber-bucketing loop lives.
    """
    fibers: dict[Any, tuple[Any, list[Any]]] = {}
    for s in state_space:
        obs = R.observe(s)
        key = _hashable(obs)
        if key in fibers:
            fibers[key][1].append(s)
        else:
            fibers[key] = (obs, [s])
    return fibers
