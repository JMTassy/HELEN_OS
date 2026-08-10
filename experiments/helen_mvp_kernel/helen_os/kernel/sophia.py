"""SOPHIA — compost + consequence discipline. 🔵 OBSERVED · NON_SOVEREIGN sandbox.

Type fence by ABSENT CONSTRUCTORS: nothing in this module can produce a
TypedAdmissionReceipt, a Capability, or a ledger event. Compost yields Seeds;
Seeds carry authority 0 as a structural constant, not a mutable field.

  Reject(h) ⊬ ¬h        — failure is not falsification
  Consequence partial   — defined only when justified by the failure's Δ
  A(Consequence) = 0    — even justified consequences carry no authority
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class FailureReceipt:
    failure_id: str
    hypothesis: str
    kind: str            # e.g. "REJECT", "UNSUPPORTED", "POLICY_DENIED", "FALSIFIED"
    delta: tuple = ()    # evidence deltas actually observed


@dataclass(frozen=True)
class Seed:
    """Garden seed grown from compost. Authority is 0 by construction."""
    seed_id: str
    grown_from: str

    @property
    def authority(self) -> int:
        return 0  # structural constant — there is no setter, no field, no override


def compost(f: FailureReceipt) -> Seed:
    return Seed(seed_id=f"seed_{f.failure_id}", grown_from=f.failure_id)


@dataclass(frozen=True)
class Consequence:
    """A licensed, narrow claim derived from a failure's observed Δ. Authority 0."""
    claim: str
    supported_by: tuple

    @property
    def authority(self) -> int:
        return 0


def consequence_of(f: FailureReceipt) -> Optional[Consequence]:
    """Partial map: defined only when the failure's Δ justifies a narrow claim.
    Empty Δ ⇒ undefined (None) — no claim may be manufactured from bare failure.
    A REJECT kind never yields a negation claim: Reject(h) ⊬ ¬h."""
    if not f.delta:
        return None
    if f.kind == "REJECT":
        return None  # rejection is procedural; it licenses no claim about h
    return Consequence(
        claim=f"narrow consequence of {f.failure_id} limited to observed delta",
        supported_by=tuple(f.delta),
    )


def negation_licensed(f: FailureReceipt) -> bool:
    """¬h may only be asserted from an explicit FALSIFIED justification with Δ."""
    return f.kind == "FALSIFIED" and bool(f.delta)
