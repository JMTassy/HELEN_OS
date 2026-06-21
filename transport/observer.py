"""Observer classes and the Observation Axiom.

V0 defined R : S → L as an arbitrary function. That admits pathological maps:

    - the CONSTANT map (R(s) = c for all s) sees nothing — every state collapses
      to one fiber. It trivially satisfies "is an observation map" but observes
      no distinction at all.
    - the IDENTITY map (R = id) sees everything — it distinguishes states no
      real observer could tell apart.

The Observation Axiom rules both out by relativizing R to an observer class.

An observer class is given by a ground-resolution map

    G : S → F

describing EXACTLY what that observer can in principle distinguish. R is then
judged against G:

    O-sound      ~_G ⊆ ~_R   (R never distinguishes states the observer holds
                              identical — R does not hallucinate distinctions)
    O-complete   ~_R ⊆ ~_G   (R distinguishes everything the observer can)
    O-admissible sound AND complete, i.e. ~_R = ~_G
                 (R "preserves exactly the information accessible to O")

Under this axiom:
    - the constant map fails completeness against any non-trivial observer
    - the identity map fails soundness against any limited observer

So neither trivializes the theory.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable

from transport.observation import ObservationMap


def _implies_equal(
    A: Callable[[Any], Any],
    B: Callable[[Any], Any],
    space: list[Any],
) -> bool:
    """True iff A(s)=A(s') implies B(s)=B(s') for all pairs in space.

    Equivalently: ~_A ⊆ ~_B  (the A-partition refines the B-partition).
    """
    n = len(space)
    for i in range(n):
        ai = A(space[i])
        bi = B(space[i])
        for j in range(i + 1, n):
            if ai == A(space[j]) and bi != B(space[j]):
                return False
    return True


class ObserverClass:
    """An observer defined by its ground-resolution map G : S → F.

    F is the space of distinctions the observer can in principle make.
    """

    def __init__(self, ground: Callable[[Any], Any], name: str = "O") -> None:
        self._ground = ground
        self.name = name

    def resolve(self, state: Any) -> Any:
        return self._ground(state)

    def is_sound(self, R: ObservationMap, state_space: Iterable[Any]) -> bool:
        """R distinguishes no more than the observer can (no phantom distinctions)."""
        space = list(state_space)
        return _implies_equal(self._ground, R.observe, space)

    def is_complete(self, R: ObservationMap, state_space: Iterable[Any]) -> bool:
        """R distinguishes everything the observer can."""
        space = list(state_space)
        return _implies_equal(R.observe, self._ground, space)

    def is_admissible(self, R: ObservationMap, state_space: Iterable[Any]) -> bool:
        """Observation Axiom: R preserves exactly the observer's information.

        ~_R = ~_G  (sound and complete).
        """
        space = list(state_space)
        return self.is_sound(R, space) and self.is_complete(R, space)

    def __repr__(self) -> str:
        return f"ObserverClass(name={self.name!r})"


def is_pathological(R: ObservationMap, state_space: Iterable[Any]) -> bool:
    """True iff R is constant (sees nothing) or injective (sees everything).

    A constant map has a single fiber covering all of S.
    An injective map has only singleton fibers.
    Both are degenerate as observations of a non-trivial reality.
    """
    space = list(state_space)
    if len(space) < 2:
        return False
    observations = [R.observe(s) for s in space]
    distinct = len(set(_freeze(o) for o in observations))
    is_constant = distinct == 1
    is_injective = distinct == len(space)
    return is_constant or is_injective


def _freeze(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return frozenset(value)
    if isinstance(value, dict):
        return tuple(sorted((k, _freeze(v)) for k, v in value.items()))
    return value
