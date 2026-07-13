"""dirty_state.py — Pure dirty-state predicate for the two-stage autoresearch loop.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

All functions are pure: no I/O, no subprocess, no state mutation.

Contract:
  REPORTED packet_status  → dominates=False always (never fires on external evidence)
  Missing evidence        → no_receipt=True, dominates=False  (missing ≠ dirty)
  WITNESSED + violation   → dominates=True

The predicate fires ONLY on locally WITNESSED evidence because:
  - An external caller (REPORTED) may misclassify or omit fields.
  - Only code that actually ran the git reads can assert sovereign violations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observation_packet import ObservationPacket

PACKET_STATUS_WITNESSED = "WITNESSED"
PACKET_STATUS_REPORTED = "REPORTED"


@dataclass
class DirtyVerdict:
    """Result of the dirty-state predicate evaluation.

    dominates  — True  → route to DIRTY_STATE_DECISION_PACKET; skip surface ranking
                 False → proceed to rank allowed surfaces
    reasons    — human-readable list of what triggered dominates (empty when False)
    no_receipt — True when evidence is absent/unknown; signal to HOLD_FOR_OPERATOR
                 rather than declaring dirty
    reported_only — True when the packet was REPORTED; fires no checks at all
    """
    dominates: bool
    reasons: list[str] = field(default_factory=list)
    no_receipt: bool = False
    reported_only: bool = False


def evaluate(packet: "ObservationPacket") -> DirtyVerdict:
    """Evaluate the dirty-state predicate against an ObservationPacket.

    Returns a DirtyVerdict. Never mutates the packet.
    """
    # REPORTED evidence — never assert sovereign violations
    if packet.packet_status == PACKET_STATUS_REPORTED:
        return DirtyVerdict(dominates=False, reported_only=True)

    # WITNESSED from here on — check for missing evidence first
    evidence_absent = (
        packet.replay_status == "unknown"
        and not packet.protected_paths_touched
        and not packet.unauthorized_sovereign_diff
        and not packet.unknown_provenance_on_sovereign_paths
    )
    if evidence_absent and packet.latest_receipt_id is None:
        return DirtyVerdict(
            dominates=False,
            no_receipt=True,
            reasons=["replay_status=unknown and no receipt_id — insufficient evidence"],
        )

    # Evaluate each violation signal
    reasons: list[str] = []

    if packet.replay_status == "mismatch":
        reasons.append("replay_status=mismatch")

    if packet.protected_paths_touched:
        reasons.append(
            f"protected_paths_touched: {packet.protected_paths_touched[:3]}"
        )

    if packet.unauthorized_sovereign_diff:
        reasons.append("unauthorized_sovereign_diff=True")

    if packet.unknown_provenance_on_sovereign_paths:
        reasons.append("unknown_provenance_on_sovereign_paths=True")

    return DirtyVerdict(dominates=bool(reasons), reasons=reasons)


def summarize(verdict: DirtyVerdict) -> str:
    """One-line human-readable verdict summary."""
    if verdict.reported_only:
        return "REPORTED packet — dirty-state check skipped; proceed to ranking"
    if verdict.no_receipt:
        return "NO_RECEIPT: evidence absent/unknown — HOLD_FOR_OPERATOR"
    if verdict.dominates:
        return "DIRTY_DOMINATES: " + "; ".join(verdict.reasons)
    return "clean — proceed to rank allowed surfaces"
