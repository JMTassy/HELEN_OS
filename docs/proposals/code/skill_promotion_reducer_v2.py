"""Skill promotion reducer: pure decision function.

STAGED GOVERNANCE PATCH — copy to helen_os/governance/skill_promotion_reducer.py
Requires: reason_codes_additions.py to be promoted first.
Tests: helen_os/tests/test_reducer_manifest_gate_v2.py (currently red)
"""
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

    Enforces 7 gates in order:
    1. Schema validity
    2. Manifest legitimacy (if manifests registry present)
    3. Receipt presence
    4. Receipt integrity
    5. Parent capability
    6. Doctrine match
    7. Evaluation pass threshold
    """
    # Gate 1: Schema validity
    valid, err = validate_schema("SKILL_PROMOTION_PACKET_V1", "1.0.0", packet)
    if not valid:
        return ReductionResult("REJECTED", ReasonCode.ERR_SCHEMA_INVALID.value, err)

    # Gate 2: Manifest legitimacy
    manifests = active_state.get("manifests")
    if manifests is not None:
        manifest_id = packet.get("manifest_id", "")
        manifest_hash = packet.get("manifest_hash", "")
        # Look up by hash (canonical registry key)
        entry = manifests.get(manifest_hash)
        if entry is None:
            return ReductionResult(
                "REJECTED", ReasonCode.ERR_MANIFEST_NOT_FOUND.value
            )
        allowed = entry.get("allowed_skills", [])
        if packet.get("skill_id") not in allowed:
            return ReductionResult(
                "REJECTED", ReasonCode.ERR_MANIFEST_SKILL_UNAUTHORIZED.value
            )

    # Gate 3: Receipt presence
    receipts = packet.get("receipts", [])
    if not receipts:
        return ReductionResult("REJECTED", ReasonCode.ERR_RECEIPT_MISSING.value)

    # Gate 4: Receipt integrity (hash verification)
    for receipt in receipts:
        if not verify_hash(receipt, receipt.get("sha256", ""), exclude={"sha256"}):
            return ReductionResult(
                "REJECTED", ReasonCode.ERR_RECEIPT_HASH_MISMATCH.value
            )

    # Gate 5: Parent capability drift
    parent_id = packet["lineage"]["parent_skill_id"]
    if parent_id not in active_state.get("active_skills", {}):
        return ReductionResult("REJECTED", ReasonCode.ERR_CAPABILITY_DRIFT.value)

    # Gate 6: Doctrine match
    if (
        packet["doctrine_surface"]["law_surface_version"]
        != active_state.get("law_surface_version")
    ):
        return ReductionResult("REJECTED", ReasonCode.ERR_DOCTRINE_CONFLICT.value)

    # Gate 7: Evaluation threshold
    if not packet["evaluation"]["passed"]:
        return ReductionResult("REJECTED", ReasonCode.ERR_THRESHOLD_NOT_MET.value)

    # Bonus gate: Transfer requirement
    if (
        packet["doctrine_surface"]["transfer_required"]
        and not packet.get("transfer_evidence")
    ):
        return ReductionResult("QUARANTINED", ReasonCode.OK_QUARANTINED.value)

    return ReductionResult("ADMITTED", ReasonCode.OK_ADMITTED.value)
