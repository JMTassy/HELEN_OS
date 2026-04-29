"""Admissibility Gate — receipt-required filter between Ralph and delivery.

Rules (in order):
  1. No receipt            → REJECT
  2. Missing required fields → REJECT
  3. visual_coherence < 0.6  → REJECT  (if present)
  4. temporal_alignment < threshold → REJECT  (if present)
  5. Unknown/absent metrics  → PENDING  (not enough evidence to admit)
  6. All checks pass         → ACCEPT

No fake metrics. An absent metric is never treated as passing.
PENDING means "insufficient evidence" — not deliverable until re-evaluated.

Ralph cannot call deliver(). Only ACCEPTED ledger entries reach delivery.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Decision = Literal["ACCEPT", "REJECT", "PENDING"]

VISUAL_COHERENCE_MIN = 0.6
TEMPORAL_ALIGNMENT_MIN = 0.5

REQUIRED_RECEIPT_FIELDS = {"content_hash", "pipeline_hash"}


@dataclass(frozen=True)
class GateVerdict:
    decision: Decision
    reason: str
    receipt: dict | None


def evaluate(candidate: dict, receipt: dict | None) -> GateVerdict:
    """Evaluate a Ralph candidate against its receipt.

    Args:
        candidate: dict produced by ralph_generator (ignored for gate logic
                   except to extract video_id for traceability).
        receipt:   dict extracted from the candidate's provenance chain.
                   None → immediate REJECT.

    Returns:
        GateVerdict with decision, human-readable reason, and the receipt.
    """
    if receipt is None:
        return GateVerdict(
            decision="REJECT",
            reason="no receipt — candidate has no provenance chain",
            receipt=None,
        )

    missing = REQUIRED_RECEIPT_FIELDS - set(receipt.keys())
    if missing:
        return GateVerdict(
            decision="REJECT",
            reason=f"receipt missing required fields: {sorted(missing)}",
            receipt=receipt,
        )

    vc = receipt.get("visual_coherence")
    ta = receipt.get("temporal_alignment")

    if vc is not None and not isinstance(vc, (int, float)):
        return GateVerdict(
            decision="REJECT",
            reason=f"visual_coherence must be numeric, got {type(vc).__name__}",
            receipt=receipt,
        )
    if ta is not None and not isinstance(ta, (int, float)):
        return GateVerdict(
            decision="REJECT",
            reason=f"temporal_alignment must be numeric, got {type(ta).__name__}",
            receipt=receipt,
        )

    if vc is not None and vc < VISUAL_COHERENCE_MIN:
        return GateVerdict(
            decision="REJECT",
            reason=f"visual_coherence {vc:.3f} < threshold {VISUAL_COHERENCE_MIN}",
            receipt=receipt,
        )

    if ta is not None and ta < TEMPORAL_ALIGNMENT_MIN:
        return GateVerdict(
            decision="REJECT",
            reason=f"temporal_alignment {ta:.3f} < threshold {TEMPORAL_ALIGNMENT_MIN}",
            receipt=receipt,
        )

    if vc is None or ta is None:
        missing_metrics = [m for m, v in [("visual_coherence", vc), ("temporal_alignment", ta)] if v is None]
        return GateVerdict(
            decision="PENDING",
            reason=f"insufficient evidence — missing metrics: {missing_metrics}",
            receipt=receipt,
        )

    return GateVerdict(
        decision="ACCEPT",
        reason="all receipt checks passed",
        receipt=receipt,
    )
