"""
Validator for IDENTITY_GATE_RECEIPT_V1_SEQUENCE.

Binds the schema defined in docs/proposals/IDENTITY_GATE_RECEIPT_V1_SEQUENCE.md
into executable rules. RED-by-design until the gate it validates is itself
implemented; the tests are the spec.

Authority: NON_SOVEREIGN. Returns a structured verdict with codes; never
writes to any ledger, never mutates state.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


# ── Sub-ledger paths (V1.1 doctrine §11) ──────────────────────────────────
FRAME_LEDGER_PATH    = "ledgers/identity_gate_v1.ndjson"
SEQUENCE_LEDGER_PATH = "ledgers/identity_gate_v1_sequence.ndjson"

# Trajectory shapes that REQUIRE a REJECT verdict (V1.1 §5.1)
SHAPES_REQUIRING_REJECT = {"DRIFTING_UP", "DIVERGENT"}

# Valid shot-boundary kinds (V1.1 §7)
KNOWN_BOUNDARY_KINDS = {"HARD_CUT", "CROSSFADE", "MORPH"}
UNKNOWN_BOUNDARY_KIND = "UNKNOWN"


def _parse_iso(ts: str) -> datetime | None:
    """Parse an ISO 8601 timestamp. Returns None on failure."""
    if not isinstance(ts, str):
        return None
    try:
        # Handle "Z" suffix
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def validate_sequence_receipt(
    receipt: dict[str, Any],
    *,
    frame_receipt_store: dict[str, bool] | None = None,
    justification_receipt_store: dict[str, dict[str, Any]] | None = None,
    detected_boundaries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Validate an IDENTITY_GATE_RECEIPT_V1_SEQUENCE against the doctrine.

    Args:
        receipt: the receipt dict to validate
        frame_receipt_store: optional {hash: True} map of existing frame receipts.
            If provided, the validator checks that every per_frame_receipts[].receipt_hash
            exists in the store.
        justification_receipt_store: optional {hash: {"timestamp": str}} map of
            JUSTIFIED_DEVIATION_V0 receipts. Used to verify annotation linkage and
            timestamp-precedence.
        detected_boundaries: optional list of boundaries the validator auto-detected
            (independent of what's declared). Used to flag UNDECLARED_BOUNDARY.

    Returns:
        {
          "valid": bool,
          "violations": list[str],   # violation codes
          "details": list[str],      # human-readable explanations
        }
    """
    violations: list[str] = []
    details: list[str] = []

    def fail(code: str, msg: str) -> None:
        violations.append(code)
        details.append(f"{code}: {msg}")

    # ── Schema: required top-level fields (subset; we don't enforce every field) ─
    required_top = [
        "type", "sequence_id", "timestamp_start", "timestamp_end",
        "asset", "canonical_identity", "per_frame_receipts",
        "trajectory", "trajectory_metrics", "shot_structure",
        "intentional_drift_annotations", "sequence_evaluation",
        "decision", "authority", "claim",
    ]
    for k in required_top:
        if k not in receipt:
            fail("MISSING_FIELD", f"required field '{k}' missing")
    if violations:
        return {"valid": False, "violations": violations, "details": details}

    # ── §3 type discriminator ─────────────────────────────────────────────────
    if receipt["type"] != "IDENTITY_GATE_RECEIPT_V1_SEQUENCE":
        fail("WRONG_TYPE", f"type must be IDENTITY_GATE_RECEIPT_V1_SEQUENCE, got {receipt['type']!r}")

    # ── §12 rule 8: asset.type must be "video_sequence" ───────────────────────
    asset = receipt.get("asset", {})
    if asset.get("type") != "video_sequence":
        fail("WRONG_ASSET_TYPE", f"asset.type must be 'video_sequence', got {asset.get('type')!r}")

    frame_count = asset.get("frame_count")
    if not isinstance(frame_count, int) or frame_count < 1:
        fail("BAD_FRAME_COUNT", f"asset.frame_count must be positive int, got {frame_count!r}")
        return {"valid": False, "violations": violations, "details": details}

    # ── §12 rule 9: per_frame_receipts.length == asset.frame_count ────────────
    per_frame = receipt.get("per_frame_receipts", [])
    if len(per_frame) != frame_count:
        fail("FRAME_COUNT_MISMATCH",
             f"per_frame_receipts has {len(per_frame)} entries, asset.frame_count is {frame_count}")

    # ── §12 rule 10: trajectory series length checks ──────────────────────────
    traj = receipt.get("trajectory", {})
    required_series = ["identity_drift_series", "cycle_error_series", "style_drift_series"]
    for s in required_series:
        series = traj.get(s)
        if not isinstance(series, list):
            fail("MISSING_SERIES", f"trajectory.{s} must be a list")
        elif len(series) != frame_count:
            fail("SERIES_LENGTH_MISMATCH",
                 f"trajectory.{s} length {len(series)} != frame_count {frame_count}")
    tds = traj.get("temporal_drift_series")
    if not isinstance(tds, list):
        fail("MISSING_SERIES", "trajectory.temporal_drift_series must be a list")
    elif len(tds) != frame_count - 1:
        fail("SERIES_LENGTH_MISMATCH",
             f"trajectory.temporal_drift_series length {len(tds)} != frame_count - 1 ({frame_count - 1})")

    # ── §12 rule 11: shot_boundary frames in range, strictly increasing ───────
    shot_struct = receipt.get("shot_structure", {})
    boundaries = shot_struct.get("shot_boundaries", [])
    last_at = -1
    for b in boundaries:
        at = b.get("at_frame")
        if not isinstance(at, int) or at < 0 or at >= frame_count:
            fail("BOUNDARY_OUT_OF_RANGE", f"shot_boundary at_frame={at!r} not in [0, {frame_count})")
        elif at <= last_at:
            fail("BOUNDARY_NOT_INCREASING", f"shot_boundary at_frame={at} not > previous {last_at}")
        else:
            last_at = at
        kind = b.get("kind")
        if kind == UNKNOWN_BOUNDARY_KIND:
            fail("UNKNOWN_BOUNDARY_KIND",
                 f"shot_boundary at_frame={at} has kind UNKNOWN; must be classified before admission")
        elif kind not in KNOWN_BOUNDARY_KINDS and kind != UNKNOWN_BOUNDARY_KIND:
            fail("INVALID_BOUNDARY_KIND", f"shot_boundary kind={kind!r} not in known kinds")

    # ── §7: detected boundaries that aren't declared ──────────────────────────
    if detected_boundaries is not None:
        declared_frames = {b.get("at_frame") for b in boundaries}
        for det in detected_boundaries:
            if det.get("at_frame") not in declared_frames:
                fail("UNDECLARED_BOUNDARY",
                     f"detected shot boundary at frame {det.get('at_frame')} not declared in shot_structure")

    # ── §12 rule 12: annotation range + justification timestamp precedence ────
    seq_start = _parse_iso(receipt.get("timestamp_start", ""))
    annotations = receipt.get("intentional_drift_annotations", [])
    for ann in annotations:
        # Range
        rng = ann.get("frame_index_range")
        if (not isinstance(rng, (list, tuple)) or len(rng) != 2
                or not all(isinstance(x, int) for x in rng)
                or rng[0] < 0 or rng[1] >= frame_count or rng[0] > rng[1]):
            fail("ANNOTATION_RANGE_INVALID",
                 f"annotation frame_index_range={rng!r} not valid for frame_count={frame_count}")

        # Justification linkage
        jhash = ann.get("justification_receipt")
        if not jhash:
            fail("ANNOTATION_NO_JUSTIFICATION",
                 f"annotation in range {rng} has no justification_receipt — JUSTIFIED_DEVIATION_V0 required")
            continue
        if justification_receipt_store is not None:
            if jhash not in justification_receipt_store:
                fail("ANNOTATION_JUSTIFICATION_MISSING",
                     f"annotation references justification_receipt {jhash!r} but it is not in the store")
            else:
                # Timestamp precedence
                j = justification_receipt_store[jhash]
                jt = _parse_iso(j.get("timestamp", ""))
                if jt is None:
                    fail("ANNOTATION_JUSTIFICATION_BAD_TIMESTAMP",
                         f"justification_receipt {jhash!r} has unparseable timestamp")
                elif seq_start is None:
                    fail("SEQUENCE_BAD_TIMESTAMP",
                         "sequence timestamp_start is unparseable")
                elif jt >= seq_start:
                    fail("ANNOTATION_JUSTIFICATION_TOO_LATE",
                         f"justification_receipt {jhash!r} timestamp {jt.isoformat()} "
                         f"does not precede sequence timestamp_start {seq_start.isoformat()}")

        # Magnitude declared
        mag = ann.get("magnitude_allowed")
        if not isinstance(mag, (int, float)) or mag <= 0:
            fail("ANNOTATION_BAD_MAGNITUDE",
                 f"annotation magnitude_allowed={mag!r} must be a positive number")
        else:
            # Magnitude vs observed: the annotated drift must be actually present in the trajectory.
            # If the max observed drift in the range is much less than annotated, the annotation
            # may be padding-the-budget to mask other failures.
            id_series = traj.get("identity_drift_series", [])
            if isinstance(rng, (list, tuple)) and len(rng) == 2 and isinstance(id_series, list):
                lo, hi = rng[0], rng[1]
                if 0 <= lo <= hi < len(id_series):
                    window = id_series[lo:hi+1]
                    if window:
                        max_obs = max(window)
                        # Allow tolerance: observed must be at least 30% of declared
                        if max_obs < mag * 0.3:
                            fail("ANNOTATION_MAGNITUDE_MISMATCH",
                                 f"annotation in {rng} declares magnitude_allowed={mag}, "
                                 f"but max observed identity_drift in window is {max_obs} "
                                 f"(< 30% of declared) — annotation does not match actual drift")

    # ── §5.1: trajectory_shape requiring REJECT ──────────────────────────────
    seq_eval = receipt.get("sequence_evaluation", {})
    shape = seq_eval.get("trajectory_shape")
    decision = receipt.get("decision", {})
    verdict = decision.get("verdict")

    if shape in SHAPES_REQUIRING_REJECT and verdict != "REJECT":
        fail("SHAPE_REQUIRES_REJECT",
             f"trajectory_shape={shape!r} mandates decision.verdict=REJECT, got {verdict!r}")

    # ── §12 rule 13: REWORK requires non-empty rework_frame_ranges ────────────
    if verdict == "REWORK":
        ranges = decision.get("rework_frame_ranges", [])
        if not ranges:
            fail("REWORK_WITHOUT_RANGES",
                 "decision.verdict=REWORK requires non-empty decision.rework_frame_ranges")
        else:
            for r in ranges:
                if (not isinstance(r, (list, tuple)) or len(r) != 2
                        or not all(isinstance(x, int) for x in r)
                        or r[0] < 0 or r[1] >= frame_count or r[0] > r[1]):
                    fail("REWORK_RANGE_INVALID",
                         f"rework_frame_range {r!r} invalid for frame_count={frame_count}")

    # ── §12 rule 15: per_frame_summary counts match actual verdict distribution ─
    summary = seq_eval.get("per_frame_summary", {})
    if all(k in summary for k in ("pass_count", "rework_count", "reject_count")):
        actual = {"PASS": 0, "REWORK": 0, "REJECT": 0}
        for fr in per_frame:
            v = fr.get("verdict")
            if v in actual:
                actual[v] += 1
        if (summary["pass_count"]   != actual["PASS"]
                or summary["rework_count"] != actual["REWORK"]
                or summary["reject_count"] != actual["REJECT"]):
            fail("SUMMARY_MISMATCH",
                 f"per_frame_summary {summary} does not match actual verdict distribution {actual}")

    # ── Frame receipt existence (if store provided) ───────────────────────────
    if frame_receipt_store is not None:
        for fr in per_frame:
            h = fr.get("receipt_hash")
            if h and h not in frame_receipt_store:
                fail("MISSING_FRAME_RECEIPT",
                     f"per_frame_receipts references {h!r} but no such V1 frame receipt exists")

    # ── Authority discipline ──────────────────────────────────────────────────
    if receipt.get("authority") is not False:
        fail("AUTHORITY_VIOLATION", "authority must be false (NON_SOVEREIGN)")
    if receipt.get("claim") != "NO_CLAIM":
        fail("CLAIM_VIOLATION", f"claim must be 'NO_CLAIM', got {receipt.get('claim')!r}")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "details": details,
    }
