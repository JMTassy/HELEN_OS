"""
assemble_context_packet.py — Context Assembler (HELEN_AGENT_STACK_V1, Law 0)

Role: compile the mental frame before HELEN speaks.
This is NOT reasoning. This is NOT deciding. This is composition.

Constitutional position:
    Context is compositional, not sovereign.

Contract (non-negotiable):
    - Input:  request (str), mode (str), objects (List[dict])
    - Output: ContextPacket (frozen, deterministic, auditable)
    - authority: always "NONE"
    - Zero side effects: no memory writes, no reducer calls, no ledger writes
    - Invariant: same inputs → same packet (bit-for-bit)

Output structure:
    {
      "law":           1 TOWN_LAW
      "district":      1 DISTRICT_PROFILE
      "project":       1 PROJECT_PROFILE
      "active_thread": 1 CANONICAL_THREAD_NOTE  (core_now preferred)
      "topic":         1 RESEARCH_TOPIC
      "next_action":   {what, why, linked}
      "rationale":     str  (explicit selection reasoning)
      "authority":     "NONE"
      "packet_hash":   str  (SHA256 of canonical JSON)
    }

What this file must never do:
    - Return a response to the user
    - Mutate the corpus, sessions, ledger, or companion_state
    - Call the Reducer
    - Invent objects not in the corpus
    - Emit prose longer than the rationale field
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .ranking import _rank_object
from .skills.suggest_next_action import NextActionResult, suggest_next_action

# ── Target types (one per slot) ───────────────────────────────────────────────

_SLOT_TYPES = [
    "TOWN_LAW",
    "DISTRICT_PROFILE",
    "PROJECT_PROFILE",
    "CANONICAL_THREAD_NOTE",
    "RESEARCH_TOPIC",
]

_EMPTY_OBJECT: Dict[str, Any] = {
    "id": "none",
    "object_type": "UNKNOWN",
    "title": "—",
    "description": "",
    "salience_now": "",
    "priority": "",
    "authority_class": "",
    "helen_stance": "",
    "source_of_truth": "",
    "score": 0.0,
}


# ── Output types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PacketSlot:
    """One ranked corpus object assigned to a typed slot."""

    id: str
    object_type: str
    title: str
    description: str
    salience_now: str
    priority: str
    authority_class: str
    helen_stance: str
    source_of_truth: str
    score: float


@dataclass(frozen=True)
class ContextPacketNextAction:
    what: str
    why: str
    linked: str          # "project / law" or "—"
    source_id: str
    authority: str = "NONE"


@dataclass(frozen=True)
class ContextPacket:
    """
    Frozen, deterministic context frame for one HELEN response.

    All fields are sourced from the corpus. Nothing is generated.
    authority is always "NONE". packet_hash certifies determinism.
    """

    request: str
    mode: str

    # Typed slots — one object each
    law: PacketSlot
    district: PacketSlot
    project: PacketSlot
    active_thread: PacketSlot
    topic: PacketSlot

    # Derived action (from suggest_next_action skill)
    next_action: ContextPacketNextAction

    # Explicit selection rationale — no prose, just slot→id→score→reason
    rationale: str

    # Constitutional guarantee
    authority: str        # always "NONE"
    packet_hash: str      # SHA256 of canonical JSON (proves determinism)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request,
            "mode": self.mode,
            "law": asdict(self.law),
            "district": asdict(self.district),
            "project": asdict(self.project),
            "active_thread": asdict(self.active_thread),
            "topic": asdict(self.topic),
            "next_action": asdict(self.next_action),
            "rationale": self.rationale,
            "authority": self.authority,
            "packet_hash": self.packet_hash,
        }


# ── Internal helpers ──────────────────────────────────────────────────────────


def _score_and_sort(
    query: str, mode: str, objects: List[Dict[str, Any]]
) -> List[tuple[float, Dict[str, Any]]]:
    """Score all objects deterministically. Same inputs → same order."""
    ranked = [(_rank_object(query, mode, obj), obj) for obj in objects]
    # Sort by score DESC, then id ASC for deterministic tie-breaking
    ranked.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    return ranked


def _pick_slot(
    slot_type: str,
    ranked: List[tuple[float, Dict[str, Any]]],
    used_ids: set[str],
    prefer_salience: Optional[str] = None,
) -> tuple[float, Dict[str, Any]]:
    """
    Pick the highest-scoring unused object of slot_type.

    If prefer_salience is set, objects with that salience_now are tried first.
    Falls back to any object of slot_type if no preferred-salience object exists.
    Returns (0.0, _EMPTY_OBJECT) if none found.
    """
    candidates = [
        (score, obj) for score, obj in ranked
        if obj.get("object_type") == slot_type and obj.get("id") not in used_ids
    ]
    if not candidates:
        return (0.0, _EMPTY_OBJECT)

    if prefer_salience:
        preferred = [
            (score, obj) for score, obj in candidates
            if obj.get("salience_now") == prefer_salience
        ]
        if preferred:
            return preferred[0]

    return candidates[0]


def _project_slot(score: float, obj: Dict[str, Any]) -> PacketSlot:
    return PacketSlot(
        id=obj.get("id", "none"),
        object_type=obj.get("object_type", "UNKNOWN"),
        title=obj.get("title", "—"),
        description=obj.get("description", ""),
        salience_now=obj.get("salience_now", ""),
        priority=obj.get("priority", ""),
        authority_class=obj.get("authority_class", ""),
        helen_stance=obj.get("helen_stance", ""),
        source_of_truth=obj.get("source_of_truth", ""),
        score=round(score, 4),
    )


def _build_rationale(
    law: PacketSlot,
    district: PacketSlot,
    project: PacketSlot,
    active_thread: PacketSlot,
    topic: PacketSlot,
    action: ContextPacketNextAction,
) -> str:
    """
    Build a compact, explicit selection rationale.
    One line per slot: slot→id→score→salience.
    No prose. No generation.
    """
    lines = [
        f"law={law.id} score={law.score} salience={law.salience_now}",
        f"district={district.id} score={district.score} salience={district.salience_now}",
        f"project={project.id} score={project.score} salience={project.salience_now}",
        f"thread={active_thread.id} score={active_thread.score} salience={active_thread.salience_now}",
        f"topic={topic.id} score={topic.score} salience={topic.salience_now}",
        f"next_action→{action.source_id} linked={action.linked}",
    ]
    return " | ".join(lines)


def _canonical_bytes(data: Any) -> bytes:
    """Deterministic JSON bytes — sorted keys, no whitespace."""
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def _packet_hash(packet_dict: Dict[str, Any]) -> str:
    """SHA256 over canonical JSON of the packet (excluding packet_hash itself)."""
    without_hash = {k: v for k, v in packet_dict.items() if k != "packet_hash"}
    return "sha256:" + hashlib.sha256(_canonical_bytes(without_hash)).hexdigest()


# ── Public entry point ────────────────────────────────────────────────────────


def assemble_context_packet(
    request: str,
    mode: str,
    objects: List[Dict[str, Any]],
) -> ContextPacket:
    """
    Assemble a deterministic context packet from corpus objects.

    Args:
        request: the current user request or context signal
        mode:    district mode (companion / temple / oracle / mayor / conquest)
        objects: all registry objects (List[dict])

    Returns:
        ContextPacket — frozen, deterministic, authority=NONE

    Invariant: same (request, mode, objects) → same ContextPacket.
    Zero side effects.
    """
    # 1. Score all objects once (shared ranked list)
    ranked = _score_and_sort(request, mode, objects)
    used_ids: set[str] = set()

    # 2. Pick one object per slot type
    #    CANONICAL_THREAD_NOTE: prefer core_now
    law_score, law_obj = _pick_slot("TOWN_LAW", ranked, used_ids)
    used_ids.add(law_obj.get("id", "none"))

    district_score, district_obj = _pick_slot("DISTRICT_PROFILE", ranked, used_ids)
    used_ids.add(district_obj.get("id", "none"))

    project_score, project_obj = _pick_slot("PROJECT_PROFILE", ranked, used_ids)
    used_ids.add(project_obj.get("id", "none"))

    thread_score, thread_obj = _pick_slot(
        "CANONICAL_THREAD_NOTE", ranked, used_ids, prefer_salience="core_now"
    )
    used_ids.add(thread_obj.get("id", "none"))

    topic_score, topic_obj = _pick_slot("RESEARCH_TOPIC", ranked, used_ids)
    used_ids.add(topic_obj.get("id", "none"))

    # 3. Project to frozen slots
    law_slot      = _project_slot(law_score, law_obj)
    district_slot = _project_slot(district_score, district_obj)
    project_slot  = _project_slot(project_score, project_obj)
    thread_slot   = _project_slot(thread_score, thread_obj)
    topic_slot    = _project_slot(topic_score, topic_obj)

    # 4. Next action (from existing skill — deterministic, no inference)
    raw_action: Optional[NextActionResult] = suggest_next_action(objects, mode=mode)
    if raw_action:
        linked_parts = [p for p in [raw_action.project, raw_action.law] if p]
        action = ContextPacketNextAction(
            what=raw_action.what,
            why=raw_action.why,
            linked=" / ".join(linked_parts) if linked_parts else "—",
            source_id=raw_action.source_id,
        )
    else:
        action = ContextPacketNextAction(
            what="No active thread",
            why="Registry has no core_now CANONICAL_THREAD_NOTE",
            linked="—",
            source_id="none",
        )

    # 5. Build explicit rationale (no prose, no generation)
    rationale = _build_rationale(
        law_slot, district_slot, project_slot, thread_slot, topic_slot, action
    )

    # 6. Assemble provisional dict for hashing (authority must precede hash)
    provisional: Dict[str, Any] = {
        "request": request,
        "mode": mode,
        "law": asdict(law_slot),
        "district": asdict(district_slot),
        "project": asdict(project_slot),
        "active_thread": asdict(thread_slot),
        "topic": asdict(topic_slot),
        "next_action": asdict(action),
        "rationale": rationale,
        "authority": "NONE",
    }

    # 7. Compute hash over canonical JSON (excludes hash itself)
    p_hash = _packet_hash(provisional)

    return ContextPacket(
        request=request,
        mode=mode,
        law=law_slot,
        district=district_slot,
        project=project_slot,
        active_thread=thread_slot,
        topic=topic_slot,
        next_action=action,
        rationale=rationale,
        authority="NONE",
        packet_hash=p_hash,
    )
