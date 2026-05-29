"""Skill promotion reducer: pure decision function."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .reason_codes import ReasonCode
from .validators import validate_schema, verify_hash


@dataclass(frozen=True)
class ReductionResult:
    """Immutable reduction outcome."""

    decision: str  # ADMITTED | REJECTED | QUARANTINED | ROLLED_BACK
    reason_code: str
    explanation: str | None = None


def reduce_promotion_packet(
    packet: Mapping[str, Any], active_state: Mapping[str, Any]
) -> ReductionResult:
    """
    Pure reduction function: packet + state → decision.

    Enforces exactly 8 gates in order:
    1. Schema validity
    2. Receipt presence
    3. Receipt integrity
    4. Parent capability
    5. Doctrine match
    6. Evaluation pass threshold
    7. Override forbidden (clean admission requires override: false)
    8. Human seal present (non-null operator initials required)
    """
    # Gate 1: Schema validity
    valid, err = validate_schema("SKILL_PROMOTION_PACKET_V1", "1.0.0", packet)
    if not valid:
        return ReductionResult(
            "REJECTED", ReasonCode.ERR_SCHEMA_INVALID.value, err
        )

    # Gate 2: Receipt presence
    receipts = packet.get("receipts", [])
    if not receipts:
        return ReductionResult("REJECTED", ReasonCode.ERR_RECEIPT_MISSING.value)

    # Gate 3: Receipt integrity (hash verification)
    for receipt in receipts:
        if not verify_hash(receipt, receipt.get("sha256", ""), exclude={"sha256"}):
            return ReductionResult(
                "REJECTED", ReasonCode.ERR_RECEIPT_HASH_MISMATCH.value
            )

    # Gate 4: Parent capability drift
    parent_id = packet["lineage"]["parent_skill_id"]
    if parent_id not in active_state.get("active_skills", {}):
        return ReductionResult(
            "REJECTED", ReasonCode.ERR_CAPABILITY_DRIFT.value
        )

    # Gate 5: Doctrine match
    if (
        packet["doctrine_surface"]["law_surface_version"]
        != active_state.get("law_surface_version")
    ):
        return ReductionResult(
            "REJECTED", ReasonCode.ERR_DOCTRINE_CONFLICT.value
        )

    # Gate 6: Evaluation threshold
    if not packet["evaluation"]["passed"]:
        return ReductionResult(
            "REJECTED", ReasonCode.ERR_THRESHOLD_NOT_MET.value
        )

    # Gate 7: Override forbidden — clean admission cannot use override path
    if packet.get("override", False):
        return ReductionResult(
            "REJECTED", ReasonCode.ERR_OVERRIDE_FORBIDDEN.value
        )

    # Gate 8: Human seal required — operator initials must be present and non-null
    if not packet.get("human_seal"):
        return ReductionResult(
            "REJECTED", ReasonCode.ERR_HUMAN_SEAL_MISSING.value
        )

    # Bonus gate: Transfer requirement
    if (
        packet["doctrine_surface"]["transfer_required"]
        and not packet.get("transfer_evidence")
    ):
        return ReductionResult(
            "QUARANTINED", ReasonCode.OK_QUARANTINED.value
        )

    # All gates pass
    return ReductionResult("ADMITTED", ReasonCode.OK_ADMITTED.value)
