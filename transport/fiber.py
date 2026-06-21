"""Receipt fibers — [S]_R = { S' : R(S') = R(S) }.

A fiber is the pre-image of a single observation under R.
It is the set of states the observer cannot distinguish.
Trivial fiber (singleton) = R is injective at that point.
Non-trivial fiber = information loss at that point.
"""
from __future__ import annotations

from typing import Any


class FiberSet:
    """[S]_R — the equivalence class of state S under observation map R."""

    def __init__(
        self,
        observation: Any,
        members: list[Any],
        representative: Any | None = None,
    ) -> None:
        self.observation = observation          # the shared receipt ℓ = R(S)
        self.members = list(members)            # all S' with R(S') = ℓ
        self.representative = representative if representative is not None else (
            members[0] if members else None
        )

    def __len__(self) -> int:
        return len(self.members)

    def __contains__(self, state: Any) -> bool:
        return state in self.members

    def __iter__(self):
        return iter(self.members)

    def is_trivial(self) -> bool:
        """True iff R is injective at this fiber (no information loss here)."""
        return len(self.members) == 1

    def has_invisible_pair(self) -> bool:
        """True iff there exist S1 ≠ S2 in this fiber (witness to non-injectivity)."""
        return len(self.members) >= 2

    def witness_pair(self) -> tuple[Any, Any] | None:
        """Return (S1, S2) with S1 ≠ S2 and R(S1) = R(S2), or None if trivial."""
        if len(self.members) < 2:
            return None
        return (self.members[0], self.members[1])

    def __repr__(self) -> str:
        return (
            f"FiberSet(observation={self.observation!r}, "
            f"size={len(self.members)}, trivial={self.is_trivial()})"
        )
