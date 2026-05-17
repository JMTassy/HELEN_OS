"""
Tests for IDENTITY_GATE_RECEIPT_V1_SEQUENCE (V1.1 temporal).

HAL acceptance:
    IDENTITY_GATE_SEQUENCE_V1_1_TESTED
    tests_green=true
    authority=false
    canon=NO_SHIP

Binds the validator at helen_os/governance/identity_gate_receipt_sequence_validator.py
against the doctrine at docs/proposals/IDENTITY_GATE_RECEIPT_V1_SEQUENCE.md.
"""
import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from helen_os.governance.identity_gate_receipt_sequence_validator import (
    FRAME_LEDGER_PATH,
    SEQUENCE_LEDGER_PATH,
    validate_sequence_receipt,
)


# ─── Helpers ──────────────────────────────────────────────────────────────
def make_valid_receipt(frame_count: int = 4) -> dict:
    """A minimal, schema-valid, doctrinally-correct V1.1 receipt."""
    per_frame = [
        {
            "frame_index": i,
            "receipt_hash": f"sha256:frame{i:04d}",
            "verdict": "PASS",
        }
        for i in range(frame_count)
    ]
    return {
        "type": "IDENTITY_GATE_RECEIPT_V1_SEQUENCE",
        "sequence_id": "SEQ-TEST-0001",
        "timestamp_start": "2026-05-17T15:00:00Z",
        "timestamp_end":   "2026-05-17T15:00:10Z",
        "asset": {
            "type": "video_sequence",
            "hash": "sha256:seq-asset",
            "frame_count": frame_count,
            "fps": 24.0,
            "duration_sec": frame_count / 24.0,
        },
        "canonical_identity": {"anchor_id": "HELEN_CANON_V1", "version": "v1"},
        "per_frame_receipts": per_frame,
        "trajectory": {
            "identity_drift_series":  [0.04] * frame_count,
            "cycle_error_series":     [0.03] * frame_count,
            "style_drift_series":     [0.02] * frame_count,
            "temporal_drift_series":  [0.002] * (frame_count - 1),
        },
        "trajectory_metrics": {
            "max_identity_drift":    0.04,
            "mean_identity_drift":   0.04,
            "p95_identity_drift":    0.04,
            "drift_slope":           0.0,
            "drift_variance":        0.0,
            "cumulative_drift":      0.04 * frame_count,
            "max_temporal_drift":    0.002,
            "shot_continuity_score": 1.0,
        },
        "shot_structure": {"shot_boundaries": [], "shot_count": 1},
        "intentional_drift_annotations": [],
        "sequence_evaluation": {
            "per_frame_summary":   {"pass_count": frame_count, "rework_count": 0, "reject_count": 0},
            "drift_band":          "STRICT",
            "shot_consistency":    "PASS",
            "trajectory_shape":    "STABLE",
            "overall_risk_score":  0.12,
        },
        "decision": {
            "verdict":    "PASS",
            "confidence": 0.93,
            "reason":     "Stable trajectory, low drift.",
            "required_fixes": [],
            "rework_frame_ranges": [],
        },
        "context": {"source_hashes": ["sha256:src"], "render_backend": "test"},
        "authority": False,
        "claim": "NO_CLAIM",
        "previous_receipts": [],
        "cumulative_hash": "sha256:cum",
    }


# ─── Test 1 ────────────────────────────────────────────────────────────────
def test_1_valid_sequence_receipt_passes():
    """Valid receipt with all frame receipt hashes present → PASS."""
    receipt = make_valid_receipt(frame_count=4)
    frame_store = {fr["receipt_hash"]: True for fr in receipt["per_frame_receipts"]}
    result = validate_sequence_receipt(receipt, frame_receipt_store=frame_store)
    assert result["valid"], f"unexpected violations: {result['details']}"


# ─── Test 2 ────────────────────────────────────────────────────────────────
def test_2_all_frames_pass_but_drifting_up_must_reject():
    """trajectory_shape == DRIFTING_UP → decision.verdict must be REJECT, not PASS."""
    receipt = make_valid_receipt()
    receipt["sequence_evaluation"]["trajectory_shape"] = "DRIFTING_UP"
    # Receipt still claims PASS — that's the violation.
    result = validate_sequence_receipt(receipt)
    assert not result["valid"]
    assert "SHAPE_REQUIRES_REJECT" in result["violations"]


# ─── Test 3 ────────────────────────────────────────────────────────────────
def test_3_all_frames_pass_but_divergent_must_reject():
    """trajectory_shape == DIVERGENT → decision.verdict must be REJECT."""
    receipt = make_valid_receipt()
    receipt["sequence_evaluation"]["trajectory_shape"] = "DIVERGENT"
    result = validate_sequence_receipt(receipt)
    assert not result["valid"]
    assert "SHAPE_REQUIRES_REJECT" in result["violations"]


# ─── Test 4 ────────────────────────────────────────────────────────────────
def test_4_undeclared_hard_cut_flagged():
    """A detected shot boundary not present in shot_structure → UNDECLARED_BOUNDARY."""
    receipt = make_valid_receipt(frame_count=10)
    detected = [{"at_frame": 5, "kind": "HARD_CUT"}]
    # shot_structure is empty — the boundary is undeclared
    result = validate_sequence_receipt(receipt, detected_boundaries=detected)
    assert not result["valid"]
    assert "UNDECLARED_BOUNDARY" in result["violations"]


# ─── Test 5 ────────────────────────────────────────────────────────────────
def test_5_unknown_boundary_kind_rejected():
    """A declared boundary with kind=UNKNOWN → UNKNOWN_BOUNDARY_KIND violation."""
    receipt = make_valid_receipt(frame_count=10)
    receipt["shot_structure"]["shot_boundaries"] = [
        {"at_frame": 5, "kind": "UNKNOWN", "expected_drift_band": 0.10}
    ]
    receipt["shot_structure"]["shot_count"] = 2
    result = validate_sequence_receipt(receipt)
    assert not result["valid"]
    assert "UNKNOWN_BOUNDARY_KIND" in result["violations"]


# ─── Test 6 ────────────────────────────────────────────────────────────────
def test_6_annotation_without_justification_rejected():
    """Annotation lacking a justification_receipt → ANNOTATION_NO_JUSTIFICATION."""
    receipt = make_valid_receipt(frame_count=10)
    receipt["intentional_drift_annotations"] = [{
        "frame_index_range": [2, 5],
        "type": "EMOTION_TRANSITION",
        "reason": "test",
        "magnitude_allowed": 0.12,
        "approving_operator": "test",
        # No justification_receipt!
    }]
    result = validate_sequence_receipt(receipt)
    assert not result["valid"]
    assert "ANNOTATION_NO_JUSTIFICATION" in result["violations"]


# ─── Test 7 ────────────────────────────────────────────────────────────────
def test_7_annotation_with_late_justification_rejected():
    """A justification receipt that timestamps AFTER the sequence start → REJECT.
    Cannot retroactively justify drift."""
    receipt = make_valid_receipt(frame_count=10)
    # Make actual observed drift in the window meet the magnitude (so we test only
    # the timestamp rule and not the magnitude-mismatch rule)
    for i in range(2, 6):
        receipt["trajectory"]["identity_drift_series"][i] = 0.15
    receipt["intentional_drift_annotations"] = [{
        "frame_index_range": [2, 5],
        "type": "EMOTION_TRANSITION",
        "reason": "test late justification",
        "magnitude_allowed": 0.20,
        "approving_operator": "test",
        "justification_receipt": "sha256:late-justification",
    }]
    just_store = {
        "sha256:late-justification": {
            # Sequence starts at 15:00:00Z; this is AFTER
            "timestamp": "2026-05-17T15:00:05Z",
        }
    }
    result = validate_sequence_receipt(receipt, justification_receipt_store=just_store)
    assert not result["valid"]
    assert "ANNOTATION_JUSTIFICATION_TOO_LATE" in result["violations"]


# ─── Test 8 ────────────────────────────────────────────────────────────────
def test_8_annotation_magnitude_mismatch_rejected():
    """An annotation declaring magnitude_allowed=0.20 over a window where
    actual observed drift is ~0.04 → ANNOTATION_MAGNITUDE_MISMATCH.
    Annotations must cover real drift, not pad the budget."""
    receipt = make_valid_receipt(frame_count=10)
    # Trajectory still uses default ~0.04 drift everywhere
    receipt["intentional_drift_annotations"] = [{
        "frame_index_range": [2, 5],
        "type": "STYLE_TRANSITION",
        "reason": "padding the budget",
        "magnitude_allowed": 0.20,  # but observed window max is ~0.04
        "approving_operator": "test",
        "justification_receipt": "sha256:proper-justification",
    }]
    just_store = {
        "sha256:proper-justification": {
            # Timestamp BEFORE sequence start
            "timestamp": "2026-05-17T14:55:00Z",
        }
    }
    result = validate_sequence_receipt(receipt, justification_receipt_store=just_store)
    assert not result["valid"]
    assert "ANNOTATION_MAGNITUDE_MISMATCH" in result["violations"]


# ─── Test 9 ────────────────────────────────────────────────────────────────
def test_9_rework_without_frame_ranges_invalid():
    """decision.verdict=REWORK without rework_frame_ranges → REWORK_WITHOUT_RANGES."""
    receipt = make_valid_receipt(frame_count=10)
    receipt["decision"]["verdict"] = "REWORK"
    receipt["decision"]["rework_frame_ranges"] = []
    receipt["decision"]["required_fixes"] = ["something"]
    # We also need a frame to actually carry the REWORK verdict for summary to match
    receipt["per_frame_receipts"][3]["verdict"] = "REWORK"
    receipt["sequence_evaluation"]["per_frame_summary"] = {
        "pass_count": 9, "rework_count": 1, "reject_count": 0,
    }
    result = validate_sequence_receipt(receipt)
    assert not result["valid"]
    assert "REWORK_WITHOUT_RANGES" in result["violations"]


# ─── Test 10 ───────────────────────────────────────────────────────────────
def test_10_rework_with_exact_frame_range_valid():
    """REWORK with valid rework_frame_ranges → valid."""
    receipt = make_valid_receipt(frame_count=10)
    receipt["decision"]["verdict"] = "REWORK"
    receipt["decision"]["rework_frame_ranges"] = [[3, 5]]
    receipt["decision"]["required_fixes"] = ["re-render frames 3-5"]
    # Mark some frames as REWORK to make summary consistent
    for i in (3, 4, 5):
        receipt["per_frame_receipts"][i]["verdict"] = "REWORK"
    receipt["sequence_evaluation"]["per_frame_summary"] = {
        "pass_count": 7, "rework_count": 3, "reject_count": 0,
    }
    result = validate_sequence_receipt(receipt)
    assert result["valid"], f"unexpected violations: {result['details']}"


# ─── Test 11 ───────────────────────────────────────────────────────────────
def test_11_missing_frame_receipt_hash_invalid():
    """Reference to a frame receipt hash that doesn't exist → MISSING_FRAME_RECEIPT."""
    receipt = make_valid_receipt(frame_count=4)
    # Build a store that's missing one of the referenced receipts
    frame_store = {fr["receipt_hash"]: True for fr in receipt["per_frame_receipts"]}
    del frame_store["sha256:frame0002"]
    result = validate_sequence_receipt(receipt, frame_receipt_store=frame_store)
    assert not result["valid"]
    assert "MISSING_FRAME_RECEIPT" in result["violations"]


# ─── Test 12 ───────────────────────────────────────────────────────────────
def test_12_sequence_ledger_path_distinct_from_frame_ledger():
    """V1.1 §11: sequence receipts go to ledgers/identity_gate_v1_sequence.ndjson,
    NOT to the frame receipt ledger. Keeping them separate keeps frame-level
    replay clean from sequence aggregates."""
    assert SEQUENCE_LEDGER_PATH == "ledgers/identity_gate_v1_sequence.ndjson"
    assert FRAME_LEDGER_PATH    == "ledgers/identity_gate_v1.ndjson"
    assert SEQUENCE_LEDGER_PATH != FRAME_LEDGER_PATH
