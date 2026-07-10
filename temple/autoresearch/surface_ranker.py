"""surface_ranker.py — Pure surface-ranking module for the two-stage autoresearch loop.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

All functions are pure: no I/O, no subprocess, no state mutation.

Score formula (operator-confirmed):
  score = (leverage × evidence_quality × reversibility) / (10 × (cost + blast_radius))

Calibration from operator example:
  sandbox_visual_grammar: L=8, E=7, R=10, C=2, B=1 → 560/30 = 18.67 ✓

Default rankings ensure init_ranking_weights scores highest (24.0) so the loop
defaults to the safest non-sovereign improvement path.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Allowed surfaces — must match observation_packet.ALLOWED_SURFACES exactly
ALLOWED_SURFACES: frozenset[str] = frozenset({
    "init_ranking_weights",
    "context_ranking",
    "prompt_compression",
    "skill_routing",
    "summarization_weights",
    "sandbox_visual_grammar",
})

# Surfaces that must never appear as candidates — sovereign or evaluator-touching
FORBIDDEN_SURFACES: frozenset[str] = frozenset({
    "ledger",
    "kernel",
    "replay",
    "identity",
    "governance",
    "schema",
    "sovereign_memory",
    "evaluator",
    "oracle_town",
    "mayor",
    "reducer",
    "admission",
})

# Default surface parameters (operator-calibrated).
# Each entry: (leverage, evidence_quality, reversibility, cost, blast_radius)
# Formula: score = (L × E × R) / (10 × (C + B))
_DEFAULT_PARAMS: dict[str, tuple[int, int, int, int, int]] = {
    #                              L   E   R   C   B
    "init_ranking_weights":       (9,  8, 10,  2,  1),  # score=24.0  (default highest)
    "context_ranking":            (8,  8,  9,  2,  1),  # score=19.2
    "sandbox_visual_grammar":     (8,  7, 10,  2,  1),  # score=18.67 (matches operator example)
    "prompt_compression":         (7,  7,  9,  3,  1),  # score=11.025
    "summarization_weights":      (5,  6,  9,  2,  1),  # score=9.0
    "skill_routing":              (6,  6,  8,  2,  2),  # score=7.2
}


@dataclass
class SurfaceScore:
    """Score record for a single allowed surface."""
    surface: str
    score: float
    leverage: int
    evidence_quality: int
    reversibility: int
    cost: int
    blast_radius: int
    evidence_override: bool  # True when packet supplied a ranking for this surface


@dataclass
class RankingResult:
    """Output of rank()."""
    ranked: tuple[SurfaceScore, ...]   # descending by score
    selected: str                       # highest-scoring allowed surface
    selected_score: float
    authority: bool = False
    ledger_effect: str = "none"


def _score(l: int, e: int, r: int, c: int, b: int) -> float:
    """Core score formula."""
    denom = 10 * (c + b)
    if denom == 0:
        return 0.0
    return round((l * e * r) / denom, 4)


def _blend_evidence(
    surface: str,
    observed: Optional[float],
) -> tuple[int, int, int, int, int]:
    """Return (L, E, R, C, B) blending observed ranking signal into default params.

    If the packet supplies a ranking for this surface (0-1 float), it adjusts
    the evidence_quality dimension only, leaving structural params unchanged.
    """
    l, e, r, c, b = _DEFAULT_PARAMS.get(
        surface,
        (5, 5, 8, 3, 2),  # conservative fallback for unknown-but-allowed surfaces
    )
    if observed is not None:
        # Map 0-1 observed score to 1-10 evidence_quality scale
        e_observed = max(1, min(10, round(observed * 10)))
        # Weight observed signal at 60%, default at 40%
        e = round(0.4 * e + 0.6 * e_observed)
    return l, e, r, c, b


def rank(
    observed_rankings: dict[str, Optional[float]],
    *,
    anti_loop_targets: list[str] | None = None,
) -> RankingResult:
    """Rank allowed surfaces given observed ranking signals from the observation packet.

    Parameters
    ----------
    observed_rankings:
        surface → 0-1 float from the packet, or None if no evidence for that surface.
        Only keys in ALLOWED_SURFACES are considered; others are silently ignored.
    anti_loop_targets:
        Recent targets from loop_state; surfaces appearing here are penalized
        so the loop is nudged toward fresh targets. Surfaces are not removed —
        the anti-loop halt (same_target_count ≥ 2) is enforced by the orchestrator.

    Returns
    -------
    RankingResult with all allowed surfaces ranked and the highest selected.
    """
    repeat_penalty = set(anti_loop_targets or [])
    scores: list[SurfaceScore] = []

    # sorted() iteration + name tie-break below: frozenset order is
    # PYTHONHASHSEED-dependent, and the 0.80 anti-loop penalty can produce
    # exact score ties (e.g. init_ranking_weights 24.0*0.8 == context_ranking
    # 19.2). Ranking must be a pure function of its inputs (mu_DETERMINISM).
    for surface in sorted(ALLOWED_SURFACES):
        observed = observed_rankings.get(surface)
        l, e, r, c, b = _blend_evidence(surface, observed)

        raw = _score(l, e, r, c, b)

        # Light penalty for recently-targeted surfaces (nudge, not veto)
        if surface in repeat_penalty:
            raw = round(raw * 0.80, 4)

        scores.append(SurfaceScore(
            surface=surface,
            score=raw,
            leverage=l,
            evidence_quality=e,
            reversibility=r,
            cost=c,
            blast_radius=b,
            evidence_override=(observed is not None),
        ))

    scores.sort(key=lambda s: (-s.score, s.surface))

    return RankingResult(
        ranked=tuple(scores),
        selected=scores[0].surface,
        selected_score=scores[0].score,
    )


def assert_not_forbidden(surface: str) -> None:
    """Raise ValueError if surface touches a forbidden domain."""
    lower = surface.lower()
    for forbidden in FORBIDDEN_SURFACES:
        if forbidden in lower:
            raise ValueError(
                f"FORBIDDEN SURFACE: {surface!r} matches forbidden domain {forbidden!r}. "
                "This loop must not touch kernel truth, identity, ledger, replay, "
                "sovereign memory, or the evaluator."
            )
