"""Admissibility Gate — receipt-required filter between Ralph and delivery.

Rules (in order):
  1. No receipt                     → REJECT
  2. Missing required fields         → REJECT
  3. Receipt binding mismatch        → REJECT  (pipeline_hash ≠ sha256(content_hash+salt))
  4. Continuity score < 0.6         → REJECT  (if prev_clip supplied)
  5. visual_coherence < 0.6         → REJECT  (if present)
  6. temporal_alignment < threshold → REJECT  (if present)
  7. Unknown/absent metrics         → PENDING  (not enough evidence to admit)
  8. All checks pass                → ACCEPT

No fake metrics. An absent metric is never treated as passing.
PENDING means "insufficient evidence" — not deliverable until re-evaluated.

Receipt binding (rule 3) upgrades the gate from policy filter to verifiable
admission system: ACCEPT ⟹ cryptographic binding between content and pipeline.

Ralph cannot call deliver(). Only ACCEPTED ledger entries reach delivery.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Literal

from helen_video.continuity_engine import continuity_score

CONTINUITY_MIN = 0.6

Decision = Literal["ACCEPT", "REJECT", "PENDING"]

VISUAL_COHERENCE_MIN = 0.6
TEMPORAL_ALIGNMENT_MIN = 0.5
PIPELINE_SALT = "helen_video_v1"

REQUIRED_RECEIPT_FIELDS = {"content_hash", "pipeline_hash"}


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def verify_receipt_binding(receipt: dict, salt: str = PIPELINE_SALT) -> bool:
    """Check that pipeline_hash is cryptographically bound to content_hash.

    Binding: pipeline_hash == sha256(content_hash + salt)
    A receipt where these are independent strings fails this check.
    """
    expected = _sha256(receipt["content_hash"] + salt)
    return receipt["pipeline_hash"] == expected


@dataclass(frozen=True)
class GateVerdict:
    decision: Decision
    reason: str
    receipt: dict | None


def evaluate(
    candidate: dict,
    receipt: dict | None,
    prev_clip: dict | None = None,
) -> GateVerdict:
    """Evaluate a Ralph candidate against its receipt.

    Args:
        candidate:  dict produced by ralph_generator.
        receipt:    Provenance receipt. None → immediate REJECT.
        prev_clip:  Optional preceding clip dict. When supplied, continuity
                    score < 0.6 → REJECT (coherence filter V1).

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

    if not verify_receipt_binding(receipt):
        return GateVerdict(
            decision="REJECT",
            reason="receipt binding mismatch: pipeline_hash not derived from content_hash",
            receipt=receipt,
        )

    if prev_clip is not None:
        cs = continuity_score(prev_clip, candidate)
        if cs < CONTINUITY_MIN:
            return GateVerdict(
                decision="REJECT",
                reason=f"continuity score {cs:.3f} < threshold {CONTINUITY_MIN}",
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
