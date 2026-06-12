"""Skill library state updater.

Law: Only reducer-emitted, ledger-bound decisions may change active skill state.

Single responsibility:
- Receive SKILL_PROMOTION_DECISION_V1
- Atomically update active_skills list
- Return new state
"""
from __future__ import annotations

from typing import Any, Mapping


def apply_skill_promotion_decision(
    state: Mapping[str, Any],
    decision: Mapping[str, Any],
    packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Only reducer-emitted, ledger-bound decisions may change active skill state.

    Rules:
    - Only ADMITTED decisions mutate state
    - Other decisions return state unchanged
    - New state is immutable copy of old state
    - When packet is provided, manifest provenance fields are stored with the skill
    """
    active_skills = state.get("active_skills", {})
    if isinstance(active_skills, dict):
        active_skills_copy = {k: dict(v) for k, v in active_skills.items()}
    else:
        active_skills_copy = {}

    new_state = {
        "schema_name": state["schema_name"],
        "schema_version": state["schema_version"],
        "law_surface_version": state.get("law_surface_version"),
        "active_skills": active_skills_copy,
    }

    if decision.get("schema_name") != "SKILL_PROMOTION_DECISION_V1":
        return new_state

    if decision.get("decision_type") != "ADMITTED":
        return new_state

    skill_id = decision["skill_id"]
    candidate_version = decision["candidate_version"]
    decision_id = decision["decision_id"]

    skill_entry: dict[str, Any] = {
        "active_version": candidate_version,
        "status": "ACTIVE",
        "last_decision_id": decision_id,
    }

    # Sovereign promotion flag: set only when decision carries sovereign_promotion: true.
    # Absence of the flag means skill_local_admission only — not sovereign.
    if decision.get("sovereign_promotion") is True:
        skill_entry["sovereign"] = True

    # Manifest provenance: sourced from admission packet when present
    if packet is not None:
        manifest_id = packet.get("manifest_id")
        manifest_hash = packet.get("manifest_hash")
        domain_category = packet.get("domain_category")
        provider_class = packet.get("provider_class")
        if manifest_id is not None:
            skill_entry["manifest_id"] = manifest_id
        if manifest_hash is not None:
            skill_entry["manifest_hash"] = manifest_hash
        if domain_category is not None:
            skill_entry["domain_category"] = domain_category
        if provider_class is not None:
            skill_entry["provider_class"] = provider_class

    new_state["active_skills"][skill_id] = skill_entry
    return new_state
