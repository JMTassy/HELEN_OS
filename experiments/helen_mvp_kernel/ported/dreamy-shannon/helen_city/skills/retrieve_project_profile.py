"""Skill: retrieve_project_profile

Purpose: Return a project's structured significance (not a prose blob).

Non-sovereign: reads only, no mutation.
Authority: NONE
"""

from typing import Any, Dict, List
from .base import SkillResult, _ensure_non_sovereign


def retrieve_project_profile(
    objects: List[Dict[str, Any]],
    project_id: str,
) -> SkillResult:
    """Retrieve a project by ID with structured fields.

    Args:
        objects: List of corpus objects (loaded from registry)
        project_id: Target project ID (e.g., "project_helen_os")

    Returns:
        SkillResult with ok=True and selected fields, or ok=False with errors
    """
    matches = [
        obj for obj in objects
        if obj.get("object_type") == "PROJECT_PROFILE" and obj.get("id") == project_id
    ]

    if not matches:
        result = SkillResult(
            skill_id="retrieve_project_profile",
            authority="NONE",
            ok=False,
            output={},
            errors=[f"project_id not found: {project_id}"],
        )
        return _ensure_non_sovereign(result)

    obj = matches[0]

    # Controlled projection: expose only canonical fields
    result = SkillResult(
        skill_id="retrieve_project_profile",
        authority="NONE",
        ok=True,
        output={
            "id": obj["id"],
            "title": obj["title"],
            "status": obj["status"],
            "priority": obj["priority"],
            "salience_now": obj["salience_now"],
            "helen_stance": obj["helen_stance"],
            "relevance": obj["relevance"],
            "links": obj.get("links", []),
        },
    )
    return _ensure_non_sovereign(result)
