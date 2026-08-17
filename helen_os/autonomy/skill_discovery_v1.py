"""Skill Discovery — Non-sovereign detector of repeated failure clusters.

Law of skill.discovery:
- Observation only, no authority
- Detects repeated typed failures in bounded batches
- Proposes NEW skill via governance, never creates it directly
- All discoveries feed through MAYOR gate (admission required)
- If ADMITTED: new skill is created by state updater
- If REJECTED/QUARANTINED: discovery becomes lesson, not skill

This is Layer 3 autonomy (bounded, exploratory).
Governance remains in the reducer + state updater.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Mapping
from collections import defaultdict
from dataclasses import dataclass

from helen_os.governance.canonical import sha256_prefixed


@dataclass(frozen=True)
class FailureCluster:
    """A group of similar typed failures."""

    failure_type: str
    occurrence_count: int
    affected_task_ids: List[str]
    common_context: Dict[str, Any]


def detect_failure_clusters(
    batch_result: Dict[str, Any],
    min_occurrences: int = 2,
) -> List[FailureCluster]:
    """
    Analyze batch result for repeated typed failures.

    Rules:
    - Look at all entries with decision_type != ADMITTED
    - Group by failure_reason_code
    - Only emit clusters with >= min_occurrences

    Args:
        batch_result: Result from autoresearch_batch_v1
        min_occurrences: Minimum repeats to constitute a cluster (default 2)

    Returns:
        List of FailureCluster objects (empty if no patterns found)
    """
    clusters: Dict[str, FailureCluster] = {}

    # Extract all failures from batch
    for entry in batch_result.get("ledger", {}).get("entries", []):
        decision = entry.get("decision", {})
        decision_type = decision.get("decision_type")

        # Only look at rejections/failures
        if decision_type == "ADMITTED":
            continue

        failure_reason = decision.get("reason_code")
        if not failure_reason:
            continue

        # Get task context
        task_id = entry.get("task_id", "unknown")

        # Create cluster key
        key = failure_reason

        # Initialize or update cluster
        if key not in clusters:
            clusters[key] = {
                "failure_type": failure_reason,
                "task_ids": [],
                "contexts": [],
            }

        clusters[key]["task_ids"].append(task_id)
        clusters[key]["contexts"].append(
            {
                "task_id": task_id,
                "decision": decision,
            }
        )

    # Filter to only significant clusters
    result = []
    for failure_type, cluster_data in clusters.items():
        task_ids = cluster_data["task_ids"]
        if len(task_ids) >= min_occurrences:
            # Extract common context (shared properties)
            common = _extract_common_context(cluster_data["contexts"])
            result.append(
                FailureCluster(
                    failure_type=failure_type,
                    occurrence_count=len(task_ids),
                    affected_task_ids=task_ids,
                    common_context=common,
                )
            )

    return result


def _extract_common_context(contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract shared properties across contexts."""
    if not contexts:
        return {}

    # For now, simple extraction of common fields
    common = {}
    first_decision = contexts[0].get("decision", {})

    # Collect potentially shared fields
    for key in ["failure_type", "skill_id", "error_class"]:
        values = [c.get("decision", {}).get(key) for c in contexts]
        if values and all(v == values[0] for v in values):
            common[key] = values[0]

    return common


def compute_deterministic_discovery_id(
    batch_id: str, failure_type: str, task_ids: List[str]
) -> str:
    """
    Compute deterministic discovery_id.

    Same batch + same failure_type + same task set → same discovery_id (idempotent).
    """
    preimage = {
        "batch_id": batch_id,
        "failure_type": failure_type,
        "affected_tasks": sorted(task_ids),
    }
    hash_val = sha256_prefixed(preimage)
    # Take first 12 chars of hash suffix
    hex_part = hash_val.split(":")[1][:12]
    return f"discovery_{hex_part}"


def analyze_capability_gap(
    cluster: FailureCluster,
    active_state: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Analyze whether a failure cluster indicates a genuine capability gap.

    Returns capability gap analysis:
    {
      "class": "FILTER" | "TRANSFORM" | "VALIDATE" | "RECONCILE" | "OPTIMIZE",
      "description": str,
      "existing_skill_candidates": [skill_ids],
      "why_existing_insufficient": str,
    }
    """
    # Map failure types to likely skill categories
    failure_to_class = {
        "ERR_UNRESOLVED_SOURCE_CONFLICT": "RECONCILE",
        "ERR_DUPLICATE_DETECTION_FAILED": "FILTER",
        "ERR_RANKING_INCONSISTENT": "OPTIMIZE",
        "ERR_SCHEMA_TRANSFORMATION_FAILED": "TRANSFORM",
        "ERR_VALIDATION_FAILED": "VALIDATE",
        # self_improve_loop_v1 error codes (were silently defaulting to TRANSFORM)
        "ERR_SCHEMA_INVALID": "VALIDATE",
        "ERR_RECEIPT_MISSING": "VALIDATE",
        "ERR_RECEIPT_HASH_MISMATCH": "VALIDATE",
        "ERR_CAPABILITY_DRIFT": "RECONCILE",
        "ERR_DOCTRINE_CONFLICT": "VALIDATE",
        "ERR_THRESHOLD_NOT_MET": "OPTIMIZE",
    }

    skill_class = failure_to_class.get(cluster.failure_type, "TRANSFORM")

    # Get existing skills of this class from state
    active_skills = active_state.get("active_skills", {})
    existing_candidates = [
        skill_id
        for skill_id in active_skills
        if _get_skill_class(skill_id) == skill_class
    ]

    # Construct analysis
    return {
        "class": skill_class,
        "description": f"Capability gap: {cluster.failure_type} repeated {cluster.occurrence_count} times",
        "existing_skill_candidates": existing_candidates,
        "why_existing_insufficient": (
            f"Existing skills [{', '.join(existing_candidates)}] failed "
            f"to handle {cluster.failure_type}"
        ),
    }


def _get_skill_class(skill_id: str) -> str:
    """Infer skill class from skill_id."""
    # Heuristic: skill.filter → FILTER, skill.rank → OPTIMIZE, etc.
    if "filter" in skill_id.lower():
        return "FILTER"
    elif "rank" in skill_id.lower() or "optimize" in skill_id.lower():
        return "OPTIMIZE"
    elif "reconcile" in skill_id.lower():
        return "RECONCILE"
    elif "validate" in skill_id.lower() or "check" in skill_id.lower():
        return "VALIDATE"
    else:
        return "TRANSFORM"


def emit_discovery_proposal(
    batch_id: str,
    cluster: FailureCluster,
    active_state: Mapping[str, Any],
    confidence: float = 0.7,
) -> Dict[str, Any]:
    """
    Emit a NEW_SKILL_DISCOVERY_V1 proposal for a failure cluster.

    Args:
        batch_id: Source batch ID
        cluster: FailureCluster detected
        active_state: Current state (to check existing skills)
        confidence: Detector confidence (0.0-1.0)

    Returns:
        NEW_SKILL_DISCOVERY_V1 proposal object
    """
    discovery_id = compute_deterministic_discovery_id(
        batch_id, cluster.failure_type, cluster.affected_task_ids
    )

    capability_gap = analyze_capability_gap(cluster, active_state)

    # Propose a new skill name based on the gap class
    skill_name = _propose_skill_name(capability_gap["class"], cluster.failure_type)

    return {
        "schema_name": "NEW_SKILL_DISCOVERY_V1",
        "schema_version": "1.0.0",
        "discovery_id": discovery_id,
        "batch_id": batch_id,
        "failure_cluster": {
            "failure_type": cluster.failure_type,
            "occurrence_count": cluster.occurrence_count,
            "affected_task_ids": cluster.affected_task_ids,
            "common_context": cluster.common_context,
        },
        "capability_gap": capability_gap,
        "proposed_skill": {
            "skill_name": skill_name,
            "version": "1.0.0",
            "parent_skill_id": (
                capability_gap["existing_skill_candidates"][0]
                if capability_gap["existing_skill_candidates"]
                else "skill.base"
            ),
            "signature": {
                "input_type": "Any",
                "output_type": "Result",
            },
        },
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authority": "NONE",
    }


def _propose_skill_name(skill_class: str, failure_type: str) -> str:
    """Propose a skill name based on class and failure."""
    # Map class to base name
    class_to_base = {
        "FILTER": "skill.filter",
        "TRANSFORM": "skill.transform",
        "VALIDATE": "skill.validate",
        "RECONCILE": "skill.reconcile",
        "OPTIMIZE": "skill.optimize",
    }

    base = class_to_base.get(skill_class, "skill.unknown")

    # Add a suffix based on failure type
    if "CONFLICT" in failure_type:
        suffix = "conflict"
    elif "DUPLICATE" in failure_type:
        suffix = "dedup"
    elif "RANKING" in failure_type:
        suffix = "ranking"
    else:
        suffix = "enhanced"

    return f"{base}_{suffix}"


def discover_skills_in_batch(
    batch_result: Dict[str, Any],
    batch_id: str,
    active_state: Mapping[str, Any],
    min_occurrences: int = 2,
    confidence_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Full discovery pipeline: batch → clusters → gap analysis → proposals.

    Args:
        batch_result: Result from autoresearch_batch_v1
        batch_id: Batch identifier
        active_state: Current skill state
        min_occurrences: Min repeats to form a cluster
        confidence_threshold: Min confidence to emit proposal

    Returns:
        List of NEW_SKILL_DISCOVERY_V1 proposals (may be empty)
    """
    # Step 1: Detect clusters
    clusters = detect_failure_clusters(batch_result, min_occurrences)

    if not clusters:
        return []

    # Step 2: Emit proposals
    proposals = []
    for cluster in clusters:
        proposal = emit_discovery_proposal(
            batch_id, cluster, active_state, confidence=0.7
        )

        if proposal["confidence"] >= confidence_threshold:
            proposals.append(proposal)

    return proposals
