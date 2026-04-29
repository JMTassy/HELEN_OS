"""Sequence Optimizer V1 — deterministic best-sequence selector.

Moves from clip-level admissibility to sequence-level optimality.

Hard invariants:
  - Deterministic. No IO, no API calls, no ML.
  - Never mutates input clips.
  - Respects operator_decision: any non-KEEP clip → sequence score = -inf.
  - Uses continuity_score for transition quality.
  - Brute-force permutation search (V1 — small sets only).

Score formula per sequence:
  Σ [ 0.5 * pipeline_score + 0.5 * output_score ]
  + Σ [ continuity_score(seq[i-1], seq[i]) * 5 ]   for i > 0
  Returns -inf if any clip has operator_decision != "KEEP".
"""
from __future__ import annotations

from itertools import permutations

from helen_video.continuity_engine import continuity_score


def sequence_score(sequence: list[dict]) -> float:
    """Score a candidate sequence of clips.

    Args:
        sequence: Ordered list of clip dicts. Each clip is expected to have:
                  - operator_decision: str  ("KEEP" required)
                  - pipeline_score:    float  [0, 1]
                  - output_score:      float  [0, 1]
                  Plus any fields used by continuity_score (character, scene, etc.)

    Returns:
        A float score. Higher is better.
        Returns -inf if any clip has operator_decision != "KEEP".
        Returns 0.0 for an empty sequence.
    """
    if not sequence:
        return 0.0

    total = 0.0
    for i, clip in enumerate(sequence):
        if clip.get("operator_decision") != "KEEP":
            return -float("inf")
        total += 0.5 * float(clip.get("pipeline_score", 0.0))
        total += 0.5 * float(clip.get("output_score", 0.0))
        if i > 0:
            total += continuity_score(sequence[i - 1], clip) * 5.0

    return total


def best_sequence(clips: list[dict]) -> list[dict] | None:
    """Find the highest-scoring permutation of clips.

    Brute-force V1 — suitable for small sets (≤ 8 clips).
    Any sequence containing a non-KEEP clip is scored -inf and skipped.

    Args:
        clips: List of clip dicts.

    Returns:
        The best-ordered list of clips, or None if no admissible sequence exists
        (i.e., all permutations score -inf — at least one clip is non-KEEP).
    """
    best: list[dict] | None = None
    best_score = -float("inf")

    for seq in permutations(clips):
        score = sequence_score(list(seq))
        if score > best_score:
            best = list(seq)
            best_score = score

    return best if best_score > -float("inf") else None
