"""Drift algebra Δ — V0, the finite computable core.

NON_SOVEREIGN · authority=false · no ledger effect · AR-DRIFT-001

Motivation. Governance work in this repo repeatedly produces the same shape:
two finite representations of one law (doc vs impl, impl vs guard, spec vs
validator) and a detector asserting they agree. This module names that shape.

A finite projection is modelled as a Mapping[key, value] — the extensional
content of a normative table (P_doc), an implementation table (P_impl), or a
guard's decision table (P_guard). Drift between two projections is not a
boolean but a structured object:

    Δ(A, B) = (only_left, only_right, disagreements)

with a size |Δ| = |only_left| + |only_right| + |disagreements|.

LAWS (each witnessed in tests/test_transport_drift.py):

  D1 (identity)   Δ(A, A) = 0
  D2 (symmetry)   |Δ(A, B)| = |Δ(B, A)|, with only_left/only_right swapped
  D3 (triangle)   |Δ(A, C)| ≤ |Δ(A, B)| + |Δ(B, C)|
  D4 (soundness)  Δ(A, B) = 0  ⟺  A and B are extensionally equal

Proof sketch for D3 (per-key): if A and C differ at key k (by absence or by
value), then B cannot agree with both at k, so k contributes at least one
discrepancy to Δ(A,B) or Δ(B,C). Summing over keys gives the inequality.

The Self-Governance Principle instance: a guard G is itself a projection, so
Δ(P_doc, P_guard) is a first-class object — a guard that enforces a coarser
law than the doctrine states has Δ > 0 even while its CI run is green.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Drift:
    """Δ(A, B) as a structured discrepancy object.

    only_left      — keys present in A but absent from B
    only_right     — keys present in B but absent from A
    disagreements  — keys present in both, mapped to different values
    """

    only_left: frozenset
    only_right: frozenset
    disagreements: frozenset

    def is_zero(self) -> bool:
        """Δ = 0 — extensional agreement."""
        return not (self.only_left or self.only_right or self.disagreements)

    def size(self) -> int:
        """|Δ| — total discrepancy count (a premetric, see D1–D3)."""
        return len(self.only_left) + len(self.only_right) + len(self.disagreements)

    def transpose(self) -> "Drift":
        """Δ(B, A) from Δ(A, B) — swaps the asymmetric components."""
        return Drift(self.only_right, self.only_left, self.disagreements)

    def __repr__(self) -> str:
        if self.is_zero():
            return "Drift(0)"
        return (
            f"Drift(|Δ|={self.size()}, only_left={sorted(map(repr, self.only_left))}, "
            f"only_right={sorted(map(repr, self.only_right))}, "
            f"disagreements={sorted(map(repr, self.disagreements))})"
        )


def drift(left: Mapping[Any, Any], right: Mapping[Any, Any]) -> Drift:
    """Compute Δ(left, right) between two finite projections."""
    lk, rk = set(left), set(right)
    common = lk & rk
    return Drift(
        only_left=frozenset(lk - rk),
        only_right=frozenset(rk - lk),
        disagreements=frozenset(k for k in common if left[k] != right[k]),
    )


def guard_projection(
    law_cases: Mapping[Any, Any],
    guard: "callable",
) -> dict[Any, Any]:
    """Extensionalize a guard over the doctrine's own case table.

    Given the normative table (case → mandated verdict) and a guard function
    (case → actual verdict), returns the guard's decision table over exactly
    the doctrine's cases — so Δ(law_cases, guard_projection(law_cases, guard))
    measures doc↔guard drift on the doctrine's own domain. This is the
    Self-Governance Principle made computable: the guard is evaluated as
    just another projection.
    """
    return {case: guard(case) for case in law_cases}
