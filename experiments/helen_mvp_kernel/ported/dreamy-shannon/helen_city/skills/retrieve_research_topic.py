"""Skill: retrieve_research_topic

Purpose: Surface active research framing with salience and stance.

Non-sovereign: reads only, no mutation.
Authority: NONE
"""

from typing import Any, Dict, List
from .base import SkillResult, _ensure_non_sovereign


def retrieve_research_topic(
    objects: List[Dict[str, Any]],
    topic_id: str,
) -> SkillResult:
    """Retrieve a research topic by ID with structured fields.

    Args:
        objects: List of corpus objects
        topic_id: Target topic ID (e.g., "topic_memory_spine")

    Returns:
        SkillResult with ok=True and selected fields, or ok=False with errors
    """
    matches = [
        obj for obj in objects
        if obj.get("object_type") == "RESEARCH_TOPIC" and obj.get("id") == topic_id
    ]

    if not matches:
        result = SkillResult(
            skill_id="retrieve_research_topic",
            authority="NONE",
            ok=False,
            output={},
            errors=[f"topic_id not found: {topic_id}"],
        )
        return _ensure_non_sovereign(result)

    obj = matches[0]

    # Controlled projection
    result = SkillResult(
        skill_id="retrieve_research_topic",
        authority="NONE",
        ok=True,
        output={
            "id": obj["id"],
            "title": obj["title"],
            "layer": obj.get("layer"),
            "district": obj.get("district"),
            "status": obj["status"],
            "priority": obj["priority"],
            "salience_now": obj["salience_now"],
            "helen_stance": obj["helen_stance"],
            "relevance": obj["relevance"],
            "links": obj.get("links", []),
        },
    )
    return _ensure_non_sovereign(result)
