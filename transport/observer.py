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

from transport.observation import ObservationMap, _hashable


def _implies_equal(
    A: Callable[[Any], Any],
    B: Callable[[Any], Any],
    space: list[Any],
) -> bool:
    """True iff A(s)=A(s') implies B(s)=B(s') for all pairs in space.

    Equivalently: ~_A ⊆ ~_B  (the A-partition refines the B-partition).
    Values are compared through their canonical hashable forms, one pass:
    each A-class must map to a single B-class.
    """
    b_of_a: dict[Any, Any] = {}
    for s in space:
        a_key = _hashable(A(s))
        b_key = _hashable(B(s))
        if a_key in b_of_a:
            if b_of_a[a_key] != b_key:
                return False
        else:
            b_of_a[a_key] = b_key
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
    distinct_states = len({_hashable(s) for s in space})
    if distinct_states < 2:
        return False
    distinct = len({_hashable(R.observe(s)) for s in space})
    is_constant = distinct == 1
    is_injective = distinct == distinct_states
    return is_constant or is_injective
