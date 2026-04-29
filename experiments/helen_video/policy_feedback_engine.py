"""Policy Feedback Engine — non-sovereign weight proposal from ledger traces.

HELEN can learn from history while remaining non-sovereign because:
  - This module reads ledger traces (read-only).
  - It proposes weight updates as POLICY_CANDIDATE only.
  - It never activates, promotes, or writes any policy.
  - Reducer admission is required before a candidate can become active.
  - Every output is receipted: hash(canonical(trace_ids) + canonical(weights)).

Pipeline:
  ledger entries (ACCEPTED / REJECTED / REVIEW)
    → analyze_traces()      — extract learning signal (read-only)
    → propose_weights()     — compute candidate weights (pure function)
    → make_policy_candidate() — wrap as POLICY_CANDIDATE + receipt

Hard invariants:
  - Status is always POLICY_CANDIDATE. Never ACTIVE, ACCEPTED, or APPROVED.
  - Input ledger entries are never mutated.
  - Active policy weights are never read or modified by this module.
  - Reducer admission (external, not here) is required before activation.
  - Output receipt binds: sha256(trace_digest + weight_digest).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

# ── default policy baseline (mirrors sequence_optimizer V1) ──────────────────

DEFAULT_WEIGHTS = {
    "pipeline_weight": 0.5,
    "output_weight": 0.5,
    "continuity_multiplier": 5.0,
    "failure_penalty": 0.0,  # V1: not yet active
}

POLICY_CANDIDATE_STATUS = "POLICY_CANDIDATE"
AUTHORITY = "NON_SOVEREIGN_POLICY_PROPOSAL"

# Clamp bounds — proposed weights stay in safe range
_WEIGHT_BOUNDS = {
    "pipeline_weight":      (0.1, 0.9),
    "output_weight":        (0.1, 0.9),
    "continuity_multiplier": (1.0, 20.0),
    "failure_penalty":      (0.0, 10.0),
}


# ── hash helpers ──────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _trace_digest(entries: list[dict]) -> str:
    """Stable hash over the entry_hashes of the input traces."""
    ids = sorted(e.get("entry_hash", "") for e in entries)
    return _sha256(_canonical(ids))


def _weight_digest(weights: dict) -> str:
    return _sha256(_canonical(weights))


def policy_receipt(entries: list[dict], proposed_weights: dict) -> dict:
    """Build a verifiable receipt over (traces, weights).

    Binding: receipt_hash = sha256(trace_digest + weight_digest)
    This proves exactly which traces produced exactly these weights.
    """
    td = _trace_digest(entries)
    wd = _weight_digest(proposed_weights)
    receipt_hash = _sha256(td + wd)
    return {
        "receipt_hash": receipt_hash,
        "trace_digest": td,
        "weight_digest": wd,
        "authority": AUTHORITY,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def verify_policy_receipt(receipt: dict, entries: list[dict], weights: dict) -> bool:
    """Check that a policy receipt is bound to given traces and weights."""
    td = _trace_digest(entries)
    wd = _weight_digest(weights)
    expected = _sha256(td + wd)
    return (
        receipt.get("receipt_hash") == expected
        and receipt.get("trace_digest") == td
        and receipt.get("weight_digest") == wd
        and receipt.get("authority") == AUTHORITY
    )


# ── analysis ──────────────────────────────────────────────────────────────────

def analyze_traces(entries: list[dict]) -> dict:
    """Extract learning signal from ledger entries. Read-only. No IO.

    Args:
        entries: List of VideoLedger entry dicts. Each entry is expected
                 to have 'status' (ACCEPTED/REJECTED/PENDING) and optionally
                 a 'receipt' sub-dict with scores.

    Returns:
        Analysis dict with aggregate statistics by status.
    """
    buckets: dict[str, list[dict]] = {"ACCEPTED": [], "REJECTED": [], "PENDING": []}

    for e in entries:
        status = e.get("status", "")
        receipt = e.get("receipt", {}) or {}
        record = {
            "pipeline_score": float(receipt.get("pipeline_score") or 0.0),
            "output_score":   float(receipt.get("output_score") or 0.0),
            "visual_coherence":   float(receipt.get("visual_coherence") or 0.0),
            "temporal_alignment": float(receipt.get("temporal_alignment") or 0.0),
            "failure_class": receipt.get("failure_class") or e.get("decision_reason"),
        }
        if status in buckets:
            buckets[status].append(record)
        # REVIEW maps to PENDING bucket for learning signal
        elif status == "REVIEW":
            buckets["PENDING"].append(record)

    def _mean(records: list[dict], key: str) -> float:
        vals = [r[key] for r in records if r.get(key) is not None]
        return sum(vals) / len(vals) if vals else 0.0

    return {
        "n_accepted": len(buckets["ACCEPTED"]),
        "n_rejected": len(buckets["REJECTED"]),
        "n_review":   len(buckets["PENDING"]),
        "accepted_mean_pipeline": _mean(buckets["ACCEPTED"], "pipeline_score"),
        "accepted_mean_output":   _mean(buckets["ACCEPTED"], "output_score"),
        "rejected_mean_pipeline": _mean(buckets["REJECTED"], "pipeline_score"),
        "rejected_mean_output":   _mean(buckets["REJECTED"], "output_score"),
        "accepted_mean_vc":   _mean(buckets["ACCEPTED"], "visual_coherence"),
        "rejected_mean_vc":   _mean(buckets["REJECTED"], "visual_coherence"),
        "failure_classes": [
            r["failure_class"] for r in buckets["REJECTED"]
            if r["failure_class"]
        ],
    }


# ── weight proposal ───────────────────────────────────────────────────────────

def _clamp(value: float, key: str) -> float:
    lo, hi = _WEIGHT_BOUNDS[key]
    return max(lo, min(hi, value))


def propose_weights(
    analysis: dict,
    current_weights: dict | None = None,
) -> dict:
    """Propose new sequence scoring weights from an analysis dict.

    Pure function. Does not read or write any state.
    Does not activate, promote, or replace the active policy.

    Strategy (V1 heuristic):
      - If accepted entries have higher pipeline scores than rejected → increase
        pipeline_weight slightly; decrease output_weight to compensate.
      - If rejection rate is high (> 50%) → increase failure_penalty.
      - Continuity multiplier stays stable in V1 (no continuity scores in ledger yet).
      - All proposals are clamped to safe bounds.
      - pipeline_weight + output_weight is always normalised to 1.0.

    Args:
        analysis:        Output of analyze_traces().
        current_weights: Active weights (read for delta reference only).
                         If None, defaults to DEFAULT_WEIGHTS.

    Returns:
        Proposed weight dict. Never mutates current_weights.
    """
    base = dict(current_weights) if current_weights else dict(DEFAULT_WEIGHTS)

    total = analysis["n_accepted"] + analysis["n_rejected"] + analysis["n_review"]
    if total == 0:
        return dict(base)

    pw = base["pipeline_weight"]
    ow = base["output_weight"]
    fp = base["failure_penalty"]
    cm = base["continuity_multiplier"]

    # Pipeline signal: if accepted clips score much higher on pipeline than rejected → boost
    pipeline_gap = (
        analysis["accepted_mean_pipeline"] - analysis["rejected_mean_pipeline"]
    )
    if pipeline_gap > 0.2:
        pw = _clamp(pw + 0.05, "pipeline_weight")
    elif pipeline_gap < -0.1:
        pw = _clamp(pw - 0.03, "pipeline_weight")

    # Output signal: complementary
    output_gap = (
        analysis["accepted_mean_output"] - analysis["rejected_mean_output"]
    )
    if output_gap > 0.2:
        ow = _clamp(ow + 0.05, "output_weight")
    elif output_gap < -0.1:
        ow = _clamp(ow - 0.03, "output_weight")

    # Normalize so pipeline + output = 1.0
    total_w = pw + ow
    if total_w > 0:
        pw = round(pw / total_w, 6)
        ow = round(ow / total_w, 6)

    # Failure penalty: scale with rejection rate
    rejection_rate = analysis["n_rejected"] / total if total else 0.0
    if rejection_rate > 0.5:
        fp = _clamp(fp + 1.0, "failure_penalty")
    elif rejection_rate < 0.2 and fp > 0:
        fp = _clamp(fp - 0.5, "failure_penalty")

    return {
        "pipeline_weight":       pw,
        "output_weight":         ow,
        "continuity_multiplier": _clamp(cm, "continuity_multiplier"),
        "failure_penalty":       fp,
    }


# ── POLICY_CANDIDATE assembly ─────────────────────────────────────────────────

def make_policy_candidate(
    entries: list[dict],
    current_weights: dict | None = None,
    policy_id: str | None = None,
) -> dict:
    """Analyze traces and produce a POLICY_CANDIDATE.

    The candidate is never active. It requires reducer admission before
    any system component may use the proposed weights.

    Args:
        entries:         Ledger entries to learn from (read-only).
        current_weights: Active weights for delta reference (read-only).
        policy_id:       Stable ID for this proposal; generated if not provided.

    Returns:
        POLICY_CANDIDATE dict with receipt. Status is always POLICY_CANDIDATE.
    """
    analysis = analyze_traces(entries)
    proposed = propose_weights(analysis, current_weights)
    receipt = policy_receipt(entries, proposed)
    pid = policy_id or str(uuid.uuid4())

    return {
        "policy_id": pid,
        "status": POLICY_CANDIDATE_STATUS,
        "authority": AUTHORITY,
        "proposed_weights": proposed,
        "analysis_summary": {
            "n_accepted": analysis["n_accepted"],
            "n_rejected": analysis["n_rejected"],
            "n_review":   analysis["n_review"],
            "failure_classes": list(set(analysis["failure_classes"])),
        },
        "receipt": receipt,
        "activation_requires": "REDUCER_ADMISSION",
    }
