"""HAL — invariant lattice with the Witness Law. 🔵 OBSERVED · NON_SOVEREIGN.

    h_i(x) = FAIL     if Live(W_i,x) ∧ ¬P_i(x)
             PASS     if Live(W_i,x) ∧  P_i(x)
             UNKNOWN  if ¬Live(W_i,x)          — never ∅ ⇒ PASS

Live(W,x) = Bind ∧ Coverage ∧ Activity ∧ Consistency, RECOMPUTED by HAL from
the witness's coverage receipt — never read from a self-reported boolean.
A canary discrimination check additionally proves the witness CAN fail:
engagement without discrimination is still blindness.

HAL_PASS ⊬ ADMIT. HAL protects the typing of transitions; Γ protects the world.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from helen_os.ledger.hash_chain import canonical_json, sha256_hex

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


@dataclass(frozen=True)
class CoverageReceipt:
    input_hash: str
    predicate_id: str
    predicate_version: str
    required_item_ids: tuple
    checked_item_ids: tuple
    evidence_refs: tuple          # each ref must be derivable from x
    witness_code_hash: str = ""


@dataclass(frozen=True)
class HALCheckResult:
    invariant: str
    verdict: str
    input_hash: str
    witness_id: str
    witness_version: str
    required_units: int
    observed_units: int
    checked_units: int
    evidence_hash: str
    live: bool
    reason_code: Optional[str] = None

    def __post_init__(self) -> None:
        # Witness Law, structural: PASS requires liveness + full coverage;
        # a non-live result may never carry PASS or FAIL.
        if self.verdict == PASS and not self.live:
            raise TypeError("WITNESS_LAW: PASS without liveness is unconstructible")
        if not self.live and self.verdict != UNKNOWN:
            raise TypeError("WITNESS_LAW: non-live verdicts must be UNKNOWN")
        if self.verdict == PASS and self.checked_units != self.required_units:
            raise TypeError("WITNESS_LAW: PASS with partial coverage is unconstructible")


def recompute_live(
    receipt: Optional[CoverageReceipt],
    x,
    surface_ids: Callable,
    derivable_refs: Callable,
) -> tuple[bool, Optional[str]]:
    """Live = RecomputeCoverage(receipt) — HAL derives every condition itself."""
    if receipt is None:
        return False, "NO_EVIDENCE"
    if receipt.input_hash != h_v(x):
        return False, "WITNESS_NOT_BOUND"                       # B_bind
    required = tuple(sorted(surface_ids(x)))
    if tuple(sorted(set(receipt.required_item_ids))) != required:
        return False, "SURFACE_MISMATCH"
    if tuple(sorted(set(receipt.checked_item_ids))) != required:
        return False, "INCOMPLETE_COVERAGE"                     # B_coverage (dups collapse)
    if len(receipt.evidence_refs) == 0 and len(required) > 0:
        return False, "WITNESS_NOT_LIVE"                        # B_activity
    if not set(receipt.evidence_refs) <= set(derivable_refs(x)):
        return False, "FABRICATED_EVIDENCE"                     # B_consistency
    return True, None


def check(
    invariant: str,
    x,
    witness: Callable,            # x -> (predicate_holds: bool, CoverageReceipt)
    surface_ids: Callable,        # x -> iterable of item ids (required surface)
    derivable_refs: Callable,     # x -> iterable of legal evidence refs
    *,
    witness_id: str,
    witness_version: str = "1.0.0",
    canary: Optional[Callable] = None,   # x -> poisoned twin the witness MUST fail
) -> HALCheckResult:
    def result(verdict, live, reason, receipt=None):
        required = len(set(surface_ids(x)))
        return HALCheckResult(
            invariant=invariant, verdict=verdict, input_hash=h_v(x),
            witness_id=witness_id, witness_version=witness_version,
            required_units=required,
            observed_units=len(set(receipt.checked_item_ids)) if receipt else 0,
            checked_units=len(set(receipt.checked_item_ids)) if receipt else 0,
            evidence_hash=sha256_hex(canonical_json(list(receipt.evidence_refs)))
            if receipt else "",
            live=live, reason_code=reason,
        )

    if canary is not None:  # discrimination: engagement alone is not liveness
        try:
            poisoned_holds, _ = witness(canary(x))
        except Exception:
            poisoned_holds = False  # crashing on poison counts as detecting it
        if poisoned_holds:
            return result(UNKNOWN, False, "WITNESS_NOT_DISCRIMINATING")

    try:
        predicate_holds, receipt = witness(x)
    except Exception:
        return result(UNKNOWN, False, "WITNESS_ERROR")

    live, reason = recompute_live(receipt, x, surface_ids, derivable_refs)
    if not live:
        return result(UNKNOWN, False, reason, receipt)
    return result(PASS if predicate_holds else FAIL, True, None, receipt)


def summarize(results: list[HALCheckResult]) -> str:
    for r in results:  # structural re-assert: no PASS may be non-live
        assert not (r.verdict == PASS and not r.live)
    if any(r.verdict == FAIL for r in results):
        return FAIL
    if any(r.verdict == UNKNOWN for r in results):
        return UNKNOWN
    return PASS  # still non-sovereign: HAL_PASS ⊬ ADMIT
