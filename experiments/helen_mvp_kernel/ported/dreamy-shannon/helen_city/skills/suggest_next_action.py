"""Skill: suggest_next_action

Purpose: Recommend the next move from centrality + unresolved tension, not vibes.

Uses deterministic weighting with query influence (light, no embeddings).
Non-sovereign: reads only, no mutation.
Authority: NONE
"""

from typing import Any, Dict, List
from .base import SkillResult, _ensure_non_sovereign


# Deterministic ranking weights
PRIORITY_WEIGHT = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}

SALIENCE_WEIGHT = {
    "core_now": 3,
    "active_supporting": 2,
    "watchlist": 1,
    "dormant": 0,
    "archive": -1,
}

STANCE_WEIGHT = {
    "deep_helen_interest": 2,
    "moderate_interest": 1,
    "low_interest": 0,
    "utility_only": -1,
}


def suggest_next_action(
    objects: List[Dict[str, Any]],
    query: str,
) -> SkillResult:
    """Suggest the next action using structured judgment.

    Ranking factors (in order):
    1. Priority (critical > high > medium > low)
    2. Salience (core_now > active_supporting > watchlist > dormant > archive)
    3. HELEN stance (deep > moderate > low > utility)
    4. Query relevance (light bonus, no embeddings)
    5. ID (deterministic tie-break)

    Args:
        objects: List of corpus objects
        query: User query (used for light title matching, not semantic)

    Returns:
        SkillResult with suggested next action, or ok=False if no candidates
    """
    # Filter to actionable salience levels
    candidates = [
        obj for obj in objects
        if obj.get("salience_now") in {"core_now", "active_supporting"}
    ]

    if not candidates:
        result = SkillResult(
            skill_id="suggest_next_action",
            authority="NONE",
            ok=False,
            output={},
            errors=["no active candidates available"],
        )
        return _ensure_non_sovereign(result)

    # Light query influence: bonus if query appears in title
    query_lower = query.lower()
    def query_bonus(obj: Dict[str, Any]) -> int:
        """Return 1 if query matches object title, else 0."""
        title = obj.get("title", "").lower()
        return 1 if query_lower in title else 0

    # Deterministic ranking: no ties via input order
    candidates.sort(
        key=lambda x: (
            PRIORITY_WEIGHT.get(x.get("priority"), 0),
            SALIENCE_WEIGHT.get(x.get("salience_now"), 0),
            STANCE_WEIGHT.get(x.get("helen_stance"), 0),
            query_bonus(x),
            x.get("id", ""),  # Deterministic tie-break
        ),
        reverse=True,
    )

    best = candidates[0]

    result = SkillResult(
        skill_id="suggest_next_action",
        authority="NONE",
        ok=True,
        output={
            "suggested_object_id": best["id"],
            "title": best["title"],
            "reason": best["relevance"],
            "suggested_next_move": f"Continue work on {best['title']}.",
        },
    )
    return _ensure_non_sovereign(result)
