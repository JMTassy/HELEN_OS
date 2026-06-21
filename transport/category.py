"""The category Obs of observation maps.

Objects: observation maps R : S → L.
Morphisms: pairs (F, G) of maps making the square commute:

        F
    S ─────▶ S'
    │         │
   R│         │R'
    ▼         ▼
    L ─────▶ L'
        G

    commutes iff   R' ∘ F = G ∘ R.

A morphism transports one observation system into another while respecting
the receipt structure. This opens the door to limits, colimits, adjunctions,
and functorial transport between observation systems.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable

from transport.observation import ObservationMap


class ObservationMorphism:
    """A morphism (F, G) : R → R' in the category Obs.

    F : S → S'  acts on states.
    G : L → L'  acts on receipts.
    The morphism is valid iff R' ∘ F = G ∘ R on the tested state space.
    """

    def __init__(
        self,
        source: ObservationMap,
        target: ObservationMap,
        F: Callable[[Any], Any],
        G: Callable[[Any], Any],
        name: str = "phi",
    ) -> None:
        self.source = source
        self.target = target
        self.F = F
        self.G = G
        self.name = name

    def commutes_on(self, state_space: Iterable[Any]) -> bool:
        """Check R'(F(s)) == G(R(s)) for every s in state_space."""
        for s in state_space:
            lhs = self.target.observe(self.F(s))
            rhs = self.G(self.source.observe(s))
            if lhs != rhs:
                return False
        return True

    def violation(self, state_space: Iterable[Any]) -> tuple[Any, Any, Any] | None:
        """Return (state, R'(F(s)), G(R(s))) for the first non-commuting state.

        None if the square commutes everywhere on state_space.
        """
        for s in state_space:
            lhs = self.target.observe(self.F(s))
            rhs = self.G(self.source.observe(s))
            if lhs != rhs:
                return (s, lhs, rhs)
        return None

    def __repr__(self) -> str:
        return (
            f"ObservationMorphism(name={self.name!r}, "
            f"{self.source.name} → {self.target.name})"
        )


def identity_morphism(R: ObservationMap) -> ObservationMorphism:
    """The identity morphism id_R : R → R, given by (id_S, id_L)."""
    return ObservationMorphism(
        source=R,
        target=R,
        F=lambda s: s,
        G=lambda l: l,
        name=f"id_{R.name}",
    )


def compose(
    second: ObservationMorphism,
    first: ObservationMorphism,
) -> ObservationMorphism:
    """Compose morphisms (second ∘ first), as in standard category notation.

    first  : R  → R'
    second : R' → R''
    result : R  → R''   with F = second.F ∘ first.F, G = second.G ∘ first.G.
    """
    return ObservationMorphism(
        source=first.source,
        target=second.target,
        F=lambda s: second.F(first.F(s)),
        G=lambda l: second.G(first.G(l)),
        name=f"{second.name}∘{first.name}",
    )
