"""Skill: summarize_active_thread

Purpose: Summarize a live thread through salience, not chronology.

Non-sovereign: reads only, no mutation.
Authority: NONE
"""

from typing import Any, Dict, List
from .base import SkillResult, _ensure_non_sovereign


def summarize_active_thread(
    objects: List[Dict[str, Any]],
    thread_id: str,
) -> SkillResult:
    """Retrieve and summarize a canonical thread note.

    Reorganizes the object around significance (salience, stance, priority)
    rather than chronological order.

    Args:
        objects: List of corpus objects
        thread_id: Target thread ID (e.g., "thread_init_helen_wedge")

    Returns:
        SkillResult with salience-weighted summary, or ok=False if not found
    """
    matches = [
        obj for obj in objects
        if obj.get("object_type") == "CANONICAL_THREAD_NOTE" and obj.get("id") == thread_id
    ]

    if not matches:
        result = SkillResult(
            skill_id="summarize_active_thread",
            authority="NONE",
            ok=False,
            output={},
            errors=[f"thread_id not found: {thread_id}"],
        )
        return _ensure_non_sovereign(result)

    obj = matches[0]

    # Reorganized summary: salience-first, not chronological
    summary = {
        "thread_id": obj["id"],
        "title": obj["title"],
        "salience_now": obj["salience_now"],
        "priority": obj["priority"],
        "helen_stance": obj["helen_stance"],
        "status": obj["status"],
        "why_it_matters": obj["relevance"],
        "linked_objects": obj.get("links", []),
    }

    result = SkillResult(
        skill_id="summarize_active_thread",
        authority="NONE",
        ok=True,
        output=summary,
    )
    return _ensure_non_sovereign(result)
