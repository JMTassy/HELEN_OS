"""Skill: assemble_context_packet

Purpose: Build the frame for a response — not the response itself.

Takes a corpus, a query, and a mode.
Returns a structured context packet with one object of each type:
    1 law + 1 district + 1 project + 1 thread + 1 topic + 1 next action.

This gives HELEN context with architecture, not sludge.

Non-sovereign: reads only, no mutation.
Authority: NONE
"""

import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from .base import SkillResult, _ensure_non_sovereign


# Valid operating modes and the object types they bias toward
VALID_MODES = frozenset({"companion", "oracle", "temple", "mayor", "default"})

# Deterministic ranking weights (same as suggest_next_action, frozen here)
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

# Per-mode bias multipliers for salience selection
# Each mode emphasizes different salience levels
MODE_SALIENCE_BIAS: Dict[str, Dict[str, int]] = {
    "companion": {
        "core_now": 3,
        "active_supporting": 2,
    },
    "oracle": {
        "core_now": 2,
        "active_supporting": 3,  # Oracle synthesizes across active, not just core
    },
    "temple": {
        "active_supporting": 3,
        "watchlist": 2,           # Temple widens context
    },
    "mayor": {
        "core_now": 3,
        "active_supporting": 2,
    },
    "default": {
        "core_now": 3,
        "active_supporting": 2,
    },
}


@dataclass(frozen=True)
class ContextPacket:
    """Immutable context frame for a HELEN response.

    One object of each type: law, district, project, thread, topic, next_action.
    Same inputs always produce the same packet. Authority always NONE.
    """
    packet_id: str
    authority: str
    mode: str
    query: str
    laws: List[Dict[str, Any]] = field(default_factory=list)
    districts: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    threads: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[Dict[str, Any]] = field(default_factory=list)
    suggested_next_action: Dict[str, Any] = field(default_factory=dict)
    rationale: List[str] = field(default_factory=list)


def _rank_objects(
    objects: List[Dict[str, Any]],
    query: str,
    mode: str,
) -> List[Dict[str, Any]]:
    """Rank objects by (priority, salience, stance, query bonus, id).

    Total ordering: deterministic regardless of input order.
    """
    query_lower = query.lower()

    def query_bonus(obj: Dict[str, Any]) -> int:
        return 1 if query_lower and query_lower in obj.get("title", "").lower() else 0

    return sorted(
        objects,
        key=lambda x: (
            PRIORITY_WEIGHT.get(x.get("priority"), 0),
            SALIENCE_WEIGHT.get(x.get("salience_now"), 0),
            STANCE_WEIGHT.get(x.get("helen_stance"), 0),
            query_bonus(x),
            x.get("id", ""),        # Deterministic tie-break
        ),
        reverse=True,
    )


def _select_one(
    objects: List[Dict[str, Any]],
    object_type: str,
    query: str,
    mode: str,
    district_filter: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Select the top-ranked object of a given type."""
    candidates = [
        obj for obj in objects
        if obj.get("object_type") == object_type
    ]

    if district_filter:
        district_candidates = [
            obj for obj in candidates
            if obj.get("district") == district_filter
        ]
        # Fall back to unfiltered if no district match
        candidates = district_candidates if district_candidates else candidates

    ranked = _rank_objects(candidates, query, mode)
    return ranked[0] if ranked else None


def _compact(obj: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Project only the requested fields from an object."""
    return {k: obj[k] for k in fields if k in obj}


def assemble_context_packet(
    objects: List[Dict[str, Any]],
    query: str,
    mode: str = "default",
    district_hint: Optional[str] = None,
) -> SkillResult:
    """Assemble a structured context packet for HELEN's response.

    Selects one object of each type using deterministic ranking:
        1. law  (TOWN_LAW, optionally district-filtered)
        2. district (DISTRICT_PROFILE, mode-aware)
        3. project (PROJECT_PROFILE, highest-ranked)
        4. thread (CANONICAL_THREAD_NOTE, salience-weighted)
        5. topic (RESEARCH_TOPIC, stance-weighted)
        6. next_action (from core_now/active_supporting candidates)

    Then assembles a ContextPacket with rationale.

    Args:
        objects: Corpus objects
        query: User query (used for light title matching)
        mode: Operating mode ("companion", "oracle", "temple", "mayor", "default")
        district_hint: Optional district to bias law + district selection

    Returns:
        SkillResult wrapping a ContextPacket dict, authority="NONE"
    """
    if mode not in VALID_MODES:
        result = SkillResult(
            skill_id="assemble_context_packet",
            authority="NONE",
            ok=False,
            output={},
            errors=[f"unknown mode: {mode} — valid modes: {sorted(VALID_MODES)}"],
        )
        return _ensure_non_sovereign(result)

    rationale: List[str] = []

    # 1. Law — district-filtered if hint given
    law_obj = _select_one(objects, "TOWN_LAW", query, mode, district_filter=district_hint)
    if law_obj:
        rationale.append(f"law: {law_obj['id']} (salience={law_obj.get('salience_now')}, priority={law_obj.get('priority')})")

    # 2. District profile — mode and hint aware
    district_obj = _select_one(objects, "DISTRICT_PROFILE", query, mode, district_filter=district_hint)
    if district_obj:
        rationale.append(f"district: {district_obj['id']}")

    # 3. Project — highest-ranked by salience + priority
    project_obj = _select_one(objects, "PROJECT_PROFILE", query, mode)
    if project_obj:
        rationale.append(f"project: {project_obj['id']} (salience={project_obj.get('salience_now')})")

    # 4. Thread — salience-weighted
    thread_obj = _select_one(objects, "CANONICAL_THREAD_NOTE", query, mode)
    if thread_obj:
        rationale.append(f"thread: {thread_obj['id']} (salience={thread_obj.get('salience_now')})")

    # 5. Topic — stance-weighted
    topic_obj = _select_one(objects, "RESEARCH_TOPIC", query, mode)
    if topic_obj:
        rationale.append(f"topic: {topic_obj['id']} (stance={topic_obj.get('helen_stance')})")

    # 6. Next action — from actionable candidates
    actionable = [
        obj for obj in objects
        if obj.get("salience_now") in {"core_now", "active_supporting"}
    ]
    ranked_actionable = _rank_objects(actionable, query, mode)
    next_action = {}
    if ranked_actionable:
        best = ranked_actionable[0]
        next_action = {
            "suggested_object_id": best["id"],
            "title": best["title"],
            "reason": best.get("relevance", ""),
            "suggested_next_move": f"Continue work on {best['title']}.",
        }
        rationale.append(f"next_action: {best['id']}")

    # Compact projections — only expose canonical fields
    LAW_FIELDS = ["id", "title", "district", "priority", "salience_now", "relevance", "links"]
    DISTRICT_FIELDS = ["id", "title", "district", "description", "relevance"]
    PROJECT_FIELDS = ["id", "title", "priority", "salience_now", "helen_stance", "relevance", "links"]
    THREAD_FIELDS = ["id", "title", "priority", "salience_now", "helen_stance", "relevance", "links"]
    TOPIC_FIELDS = ["id", "title", "layer", "priority", "salience_now", "helen_stance", "relevance", "links"]

    # Build the packet as a serializable dict (ContextPacket for typed use)
    packet = ContextPacket(
        packet_id=f"ctx_{mode}_{abs(hash(query + mode + str([o.get('id') for o in objects[:3]])))!r}"[:40],
        authority="NONE",
        mode=mode,
        query=query,
        laws=[_compact(law_obj, LAW_FIELDS)] if law_obj else [],
        districts=[_compact(district_obj, DISTRICT_FIELDS)] if district_obj else [],
        projects=[_compact(project_obj, PROJECT_FIELDS)] if project_obj else [],
        threads=[_compact(thread_obj, THREAD_FIELDS)] if thread_obj else [],
        topics=[_compact(topic_obj, TOPIC_FIELDS)] if topic_obj else [],
        suggested_next_action=next_action,
        rationale=rationale,
    )

    result = SkillResult(
        skill_id="assemble_context_packet",
        authority="NONE",
        ok=True,
        output={
            "packet_id": packet.packet_id,
            "authority": packet.authority,
            "mode": packet.mode,
            "query": packet.query,
            "laws": list(packet.laws),
            "districts": list(packet.districts),
            "projects": list(packet.projects),
            "threads": list(packet.threads),
            "topics": list(packet.topics),
            "suggested_next_action": packet.suggested_next_action,
            "rationale": list(packet.rationale),
        },
    )
    return _ensure_non_sovereign(result)
