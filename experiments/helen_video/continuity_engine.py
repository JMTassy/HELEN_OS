"""Continuity Engine V1 — deterministic clip-to-clip coherence scorer.

Hard invariants:
  - Pure function. No IO, no API calls, no subprocess, no ML.
  - Never calls Remotion, gate, or ledger.
  - Never mutates input clips.
  - Returns float in [0, 1].

Score = identity(0.4) + scene(0.3) + duration(0.2) + style(0.1)
"""
from __future__ import annotations


def continuity_score(prev_clip: dict, next_clip: dict) -> float:
    """Deterministic coherence score between two adjacent clips.

    Args:
        prev_clip:  The clip immediately before in the timeline.
        next_clip:  The candidate clip to follow it.

    Returns:
        Float in [0, 1]. Higher = more coherent transition.
        0.6 is the gate admission floor.
    """
    score = 0.0

    if prev_clip.get("character") == next_clip.get("character"):
        score += 0.4

    if prev_clip.get("scene") == next_clip.get("scene"):
        score += 0.3

    prev_dur = prev_clip.get("duration", 0) or 0
    next_dur = next_clip.get("duration", 0) or 0
    if abs(prev_dur - next_dur) < 2:
        score += 0.2

    if prev_clip.get("style") == next_clip.get("style"):
        score += 0.1

    return round(min(1.0, max(0.0, score)), 10)
