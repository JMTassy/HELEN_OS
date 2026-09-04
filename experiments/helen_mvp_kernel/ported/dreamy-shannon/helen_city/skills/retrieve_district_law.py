"""Skill: retrieve_district_law

Purpose: Return the most relevant law for a district.

Uses deterministic weighting to avoid tie-breaking by input order.
Non-sovereign: reads only, no mutation.
Authority: NONE
"""

from typing import Any, Dict, List
from .base import SkillResult, _ensure_non_sovereign


# Deterministic ranking weights (no boolean ties)
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


def retrieve_district_law(
    objects: List[Dict[str, Any]],
    district: str,
) -> SkillResult:
    """Retrieve the most relevant law for a district.

    Ranking factors (in order):
    1. Salience (core_now > active_supporting > watchlist > dormant > archive)
    2. Priority (critical > high > medium > low)
    3. ID (deterministic tie-break)

    Args:
        objects: List of corpus objects
        district: Target district name (e.g., "Companion")

    Returns:
        SkillResult with the ranked law, or ok=False if none found
    """
    candidates = [
        obj for obj in objects
        if obj.get("object_type") == "TOWN_LAW" and obj.get("district") == district
    ]

    if not candidates:
        result = SkillResult(
            skill_id="retrieve_district_law",
            authority="NONE",
            ok=False,
            output={},
            errors=[f"no district law found for: {district}"],
        )
        return _ensure_non_sovereign(result)

    # Deterministic ranking: no ties via input order
    candidates.sort(
        key=lambda x: (
            SALIENCE_WEIGHT.get(x.get("salience_now"), 0),
            PRIORITY_WEIGHT.get(x.get("priority"), 0),
            x.get("id", ""),  # Deterministic tie-break
        ),
        reverse=True,
    )

    obj = candidates[0]

    # Controlled projection
    result = SkillResult(
        skill_id="retrieve_district_law",
        authority="NONE",
        ok=True,
        output={
            "id": obj["id"],
            "title": obj["title"],
            "district": obj.get("district"),
            "status": obj["status"],
            "priority": obj["priority"],
            "salience_now": obj["salience_now"],
            "relevance": obj["relevance"],
            "links": obj.get("links", []),
        },
    )
    return _ensure_non_sovereign(result)
