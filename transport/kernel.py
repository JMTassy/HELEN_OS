"""Generalized kernel — invisible transformations and Inv(R).

"Kernel" here is generalized beyond the linear-algebra sense.

In linear algebra: ker(R) = { v : R(v) = 0 }.
Here: Inv(R) = { T : R∘T = R } — transformations invisible to R.

These are related. If R is linear and T is a shift by v ∈ ker(R), then
R(T(s)) = R(s+v) = R(s) + R(v) = R(s). So shifts by kernel elements are
invisible transforms. But Inv(R) is more general: no linearity required.

Theorem (Receipt Non-Reconstructibility):
    If Inv(R) contains T ≠ id, then R is not injective.
    Proof: ∃S with T(S) ≠ S but R(T(S)) = R(S). □
"""
from __future__ import annotations

from typing import Any, Callable, Iterable

from transport.observation import ObservationMap


class GeneralizedKernel:
    """Inv(R) = { T : S → S | R∘T = R }.

    Detects invisible transformations: those that leave all observations unchanged.
    """

    def __init__(self, R: ObservationMap) -> None:
        self.R = R
        self._generators: list[tuple[str, Callable]] = []

    def is_invisible(
        self,
        transform: Callable[[Any], Any],
        state_space: Iterable[Any],
    ) -> bool:
        """Check R(T(s)) = R(s) for every s in state_space.

        A transform is invisible if no observation can detect it.
        """
        return all(
            self.R.observe(transform(s)) == self.R.observe(s)
            for s in state_space
        )

    def is_nontrivial(
        self,
        transform: Callable[[Any], Any],
        state_space: list[Any],
    ) -> bool:
        """True iff T is invisible AND T ≠ id (moves at least one state)."""
        return self.is_invisible(transform, state_space) and any(
            transform(s) != s for s in state_space
        )

    def register(
        self,
        transform: Callable[[Any], Any],
        name: str,
        state_space: list[Any],
    ) -> bool:
        """Register a transform if it is invisible under R.

        Returns True if registered (invisible), False otherwise.
        """
        if self.is_invisible(transform, state_space):
            self._generators.append((name, transform))
            return True
        return False

    def has_nontrivial_element(self, state_space: list[Any]) -> bool:
        """True iff any registered transform is non-trivial.

        Receipt Non-Reconstructibility: if True, R is not injective.
        """
        return any(
            self.is_nontrivial(t, state_space) for _, t in self._generators
        )

    def acts_fiberwise(
        self,
        transform: Callable[[Any], Any],
        state_space: list[Any],
    ) -> bool:
        """Every invisible transform preserves every fiber.

        If T ∈ Inv(R) then T(R⁻¹(ℓ)) ⊆ R⁻¹(ℓ) for all ℓ: invisible symmetries
        act fiberwise. This is logically equivalent to R∘T = R, but stated as
        the set-inclusion that seeds the later groupoid/bundle viewpoint.
        """
        return self.is_invisible(transform, state_space)

    def preserves_fiber(
        self,
        transform: Callable[[Any], Any],
        state: Any,
        state_space: list[Any],
    ) -> bool:
        """Exhibit T(R⁻¹(ℓ)) ⊆ R⁻¹(ℓ) for the fiber through `state`.

        Checks that T maps every member of the fiber back into the same fiber.
        """
        target = self.R.observe(state)
        fiber = self.R.fiber(state, state_space)
        return all(self.R.observe(transform(x)) == target for x in fiber)

    def witness(
        self, state_space: list[Any]
    ) -> tuple[str, Any, Any] | None:
        """Return (transform_name, S, T(S)) where S ≠ T(S) but R(S) = R(T(S)).

        This is an explicit proof that R is not injective.
        """
        for name, transform in self._generators:
            for s in state_space:
                ts = transform(s)
                if ts != s and self.R.observe(ts) == self.R.observe(s):
                    return (name, s, ts)
        return None

    def __repr__(self) -> str:
        names = [n for n, _ in self._generators]
        return f"GeneralizedKernel(generators={names})"
