"""aura_score.py — AuraMetrics: receptive score for video composite readiness.

Consumes complexity_extractor.ComplexityMetrics (specifically clutter and
overcomplexity_flag) and produces a bounded AuraScore.

Design rules:
  - No ML, no subprocess, no ffmpeg invocation. Pure arithmetic.
  - authority: NON_SOVEREIGN · canon: NO_SHIP
  - Does not mutate canon, reducer, kernel, ledger, or schemas.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AuraVerdict(str, Enum):
    CLEAR     = "CLEAR"       # composite is safe to proceed
    CAUTION   = "CAUTION"     # proceed with awareness; score degraded
    VETO      = "VETO"        # operator veto likely; do not render


@dataclass(frozen=True)
class AuraMetrics:
    """Scored readiness envelope for a video composite.

    Fields
    ------
    clutter : float ∈ [0, 1]
        Normalised overlay density from complexity_extractor.
    overcomplexity : float ∈ [0, 1]
        Composite complexity score from complexity_extractor.
    overcomplexity_flag : bool
        True when graph would trigger operator veto.
    aura_score : float ∈ [0, 1]
        Receptive score: 1.0 = fully clear, 0.0 = fully vetoed.
    verdict : AuraVerdict
        CLEAR / CAUTION / VETO
    notes : tuple[str, ...]
        Human-readable reasons for degradation.
    """
    clutter:             float
    overcomplexity:      float
    overcomplexity_flag: bool
    aura_score:          float
    verdict:             AuraVerdict
    notes:               tuple[str, ...]


# Thresholds
_CLUTTER_CAUTION  = 0.5   # clutter above this → CAUTION
_CLUTTER_VETO     = 1.0   # clutter at cap → flag considered
_OVERC_CAUTION    = 0.4   # overcomplexity above this → CAUTION
_OVERC_VETO       = 0.6   # overcomplexity above this → VETO
_SCORE_VETO_CEIL  = 0.25  # aura_score at or below this → VETO
_SCORE_CAUTION    = 0.60  # aura_score at or below this → CAUTION


def evaluate(
    clutter: float,
    overcomplexity: float,
    overcomplexity_flag: bool,
    extra_penalty: float = 0.0,
) -> AuraMetrics:
    """Compute AuraMetrics from complexity_extractor output fields.

    Parameters
    ----------
    clutter : float ∈ [0, 1]
    overcomplexity : float ∈ [0, 1]
    overcomplexity_flag : bool
        From ComplexityMetrics.flag (operator veto signal).
    extra_penalty : float ∈ [0, 1]
        Optional caller-supplied penalty (e.g. from RAI scorer).
    """
    if not (0.0 <= clutter <= 1.0):
        raise ValueError(f"clutter must be in [0, 1], got {clutter}")
    if not (0.0 <= overcomplexity <= 1.0):
        raise ValueError(f"overcomplexity must be in [0, 1], got {overcomplexity}")
    if not (0.0 <= extra_penalty <= 1.0):
        raise ValueError(f"extra_penalty must be in [0, 1], got {extra_penalty}")

    notes: list[str] = []

    # Base score: 1 - weighted penalty
    raw = 1.0 - (0.40 * clutter + 0.40 * overcomplexity + 0.20 * extra_penalty)
    raw = max(0.0, min(1.0, raw))

    # Hard flag: overcomplexity_flag forces a floor at 0
    if overcomplexity_flag:
        raw = min(raw, 0.20)
        notes.append("overcomplexity_flag: operator veto risk")

    if clutter >= _CLUTTER_CAUTION:
        notes.append(f"clutter={clutter:.3f} >= {_CLUTTER_CAUTION}")

    if overcomplexity >= _OVERC_CAUTION:
        notes.append(f"overcomplexity={overcomplexity:.3f} >= {_OVERC_CAUTION}")

    aura_score = round(raw, 4)

    if aura_score <= _SCORE_VETO_CEIL or overcomplexity_flag:
        verdict = AuraVerdict.VETO
    elif aura_score <= _SCORE_CAUTION:
        verdict = AuraVerdict.CAUTION
    else:
        verdict = AuraVerdict.CLEAR

    return AuraMetrics(
        clutter=clutter,
        overcomplexity=overcomplexity,
        overcomplexity_flag=overcomplexity_flag,
        aura_score=aura_score,
        verdict=verdict,
        notes=tuple(notes),
    )


def from_complexity(metrics: object, extra_penalty: float = 0.0) -> AuraMetrics:
    """Convenience wrapper accepting a ComplexityMetrics instance directly.

    Parameters
    ----------
    metrics : ComplexityMetrics
        Output of complexity_extractor.extract().
    extra_penalty : float ∈ [0, 1]
        Optional additional penalty.
    """
    return evaluate(
        clutter=metrics.clutter,
        overcomplexity=metrics.overcomplexity,
        overcomplexity_flag=metrics.flag,
        extra_penalty=extra_penalty,
    )
