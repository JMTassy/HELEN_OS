# IDENTITY_GATE_RECEIPT_V1_SEQUENCE

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** SCHEMA_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Schema specification, proposal only
**version:** V1.1 (extends V1 for temporal sequences)
**parent_schema:** `docs/proposals/IDENTITY_GATE_RECEIPT_V1.md`
**parent_gate:** `docs/proposals/HELEN_IDENTITY_GATE_V1.md`
**parent_theory:** `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md`

---

## §1. Purpose

V1 evaluates a single rendered artifact: an image or a single frame.
V1.1 evaluates a **temporal sequence** — multiple frames that together
form a video, an animation, or a multi-shot composition.

A video that drifts character identity slowly across 600 frames may
have every individual frame pass V1 and still be ungoverned at the
sequence level. **Drift can be invisible per-frame and obvious in
aggregate.** V1.1 closes that gap.

The V1.1 receipt is a **wrapper** that references per-frame V1 receipts
and adds sequence-level metrics, shot-boundary structure, and a
sequence-level verdict.

---

## §2. New core principles (additive to V1)

In addition to V1 §2:

- A sequence receipt **never replaces** per-frame receipts. It composes
  them. Every frame still produces its own V1 receipt.
- The sequence verdict is **not** the min/max of frame verdicts. It has
  its own logic that accounts for trajectory shape and shot structure.
- **Shot boundaries are first-class.** A frame at a shot boundary can
  carry higher drift without failing if the boundary is annotated.
- **Intentional drift is allowed but must be declared.** Justified
  style/emotion/pose transitions are receipted, not silently absorbed.

---

## §3. Schema additions (`IDENTITY_GATE_RECEIPT_V1_SEQUENCE`)

```json
{
  "type": "IDENTITY_GATE_RECEIPT_V1_SEQUENCE",
  "sequence_id": "string (unique identifier)",
  "timestamp_start": "ISO 8601 datetime",
  "timestamp_end":   "ISO 8601 datetime",

  "asset": {
    "type":         "video_sequence",
    "hash":         "string (sha256 of the assembled sequence file)",
    "uri":          "string (optional reference)",
    "frame_count":  "integer",
    "fps":          "float",
    "duration_sec": "float"
  },

  "canonical_identity": {
    "anchor_id": "string (e.g. HELEN_CANON_V1)",
    "version":   "string"
  },

  "per_frame_receipts": [
    {
      "frame_index":  "integer (0-based)",
      "receipt_hash": "string (sha256 of the V1 receipt for this frame)",
      "verdict":      "PASS | REWORK | REJECT"
    }
  ],

  "trajectory": {
    "identity_drift_series":   "array<float>  (per-frame, length == frame_count)",
    "cycle_error_series":      "array<float>  (per-frame)",
    "style_drift_series":      "array<float>  (per-frame)",
    "expression_drift_series": "array<float>  (per-frame, optional)",
    "pose_drift_series":       "array<float>  (per-frame, optional)",
    "temporal_drift_series":   "array<float>  (inter-frame deltas, length == frame_count - 1)"
  },

  "trajectory_metrics": {
    "max_identity_drift":   "float",
    "mean_identity_drift":  "float",
    "p95_identity_drift":   "float",
    "drift_slope":          "float (d(drift)/d(frame), windowed)",
    "drift_variance":       "float",
    "cumulative_drift":     "float (Σ identity_drift_series)",
    "max_temporal_drift":   "float",
    "shot_continuity_score":"float (0.0–1.0)"
  },

  "shot_structure": {
    "shot_boundaries": [
      {
        "at_frame":            "integer",
        "kind":                "HARD_CUT | CROSSFADE | MORPH | UNKNOWN",
        "expected_drift_band": "float (allowed identity drift at this boundary)"
      }
    ],
    "shot_count": "integer"
  },

  "intentional_drift_annotations": [
    {
      "frame_index_range":      "[integer, integer]",
      "type":                   "EMOTION_TRANSITION | POSE_TRANSITION | STYLE_TRANSITION | LIGHTING_TRANSITION | AGING | OTHER",
      "reason":                 "string",
      "magnitude_allowed":      "float",
      "approving_operator":     "string",
      "justification_receipt":  "string (hash of JUSTIFIED_DEVIATION_V0 receipt)"
    }
  ],

  "sequence_evaluation": {
    "per_frame_summary": {
      "pass_count":   "integer",
      "rework_count": "integer",
      "reject_count": "integer"
    },
    "drift_band":       "STRICT | ADMIT | DRIFT | VIOLATION",
    "shot_consistency": "PASS | SOFT_FAIL | HARD_FAIL",
    "trajectory_shape": "STABLE | OSCILLATING | DRIFTING_UP | DRIFTING_DOWN | DIVERGENT",
    "overall_risk_score": "float (0.0–1.0)"
  },

  "decision": {
    "verdict":             "PASS | REWORK | REJECT",
    "confidence":          "float (0.0–1.0)",
    "reason":              "string",
    "required_fixes":      "array<string>",
    "rework_frame_ranges": "array<[integer, integer]> (frames to re-render if REWORK)"
  },

  "context": {
    "proposal_id":          "string (optional)",
    "director_packet_hash": "string (optional)",
    "storyboard_hash":      "string (optional)",
    "source_hashes":        "array<string>",
    "render_backend":       "string"
  },

  "authority": false,
  "claim": "NO_CLAIM",

  "previous_receipts": "array<string>",
  "cumulative_hash":   "string"
}
```

---

## §4. New field explanations

| Field group                       | Purpose                                                          | Required |
| --------------------------------- | ---------------------------------------------------------------- | -------- |
| `asset.frame_count` / `fps` / `duration_sec` | Temporal extent of the sequence                       | Yes      |
| `per_frame_receipts[]`            | Reference list of V1 receipts that compose the sequence          | Yes      |
| `trajectory.*_series`             | Per-frame drift/error arrays; the actual identity time-series    | Yes (identity_drift_series, cycle_error_series, style_drift_series, temporal_drift_series); others optional |
| `trajectory_metrics`              | Aggregate stats over the trajectory (max, mean, p95, slope, etc.)| Yes      |
| `shot_structure.shot_boundaries[]`| Where shot cuts occur + what drift is expected at each            | Yes if any boundaries exist; empty array is valid for single-shot |
| `intentional_drift_annotations[]` | Declared, justified drift spans (e.g. character changes emotion) | Optional; empty array means "no intentional drift declared" |
| `sequence_evaluation.trajectory_shape` | High-level shape diagnostic                                | Yes      |
| `decision.rework_frame_ranges`    | Specific frame ranges to re-render if verdict is REWORK          | Required when verdict == REWORK |

---

## §5. Sequence verdict logic

The sequence verdict is **not** the min/max of frame verdicts. It is
computed from three independent signals:

```
SequenceVerdict = compose(
  frame_pass_ratio,
  trajectory_metrics.drift_slope,
  trajectory_shape,
  shot_consistency,
  annotated_drift_coverage
)
```

### §5.1 Verdict rules

| Conditions                                                                             | Sequence verdict |
| -------------------------------------------------------------------------------------- | ---------------- |
| All frames PASS · `drift_slope ≤ δ_strict` · shape ∈ {STABLE, OSCILLATING}             | **PASS**         |
| ≤ 5% frames REWORK · slope bounded · all drift covered by annotations or shot bounds   | **PASS** with deviation note |
| 5–25% frames REWORK · slope bounded · `rework_frame_ranges` finite and contiguous     | **REWORK** (re-render listed ranges) |
| Any frame REJECT · OR `drift_slope > δ_drift` · OR shape == DIVERGENT                  | **REJECT**       |
| > 25% frames REWORK · OR shape == DRIFTING_UP unbounded                                | **REJECT** (sequence-level identity loss) |
| Any shot boundary with `drift_at_boundary > expected_drift_band + tolerance`           | **REJECT** unless annotated |
| Drift in a window where intentional drift was declared, within `magnitude_allowed`    | does **not** count toward failure |

**Critical rule:** an annotation must cover the actual drift, not the
other way around. Annotating "EMOTION_TRANSITION at frames 100–120
allowing 0.20 drift" does **not** retroactively license drift at frames
100–120 if no transition actually occurred. The annotation declares
intent; the trajectory must match it. Mismatch → REJECT.

---

## §6. Trajectory shape classification

`trajectory_shape` is one of:

| Shape           | Definition                                                              | Significance                          |
| --------------- | ----------------------------------------------------------------------- | ------------------------------------- |
| `STABLE`        | drift variance < σ_stable; slope ≈ 0                                    | Healthy: identity holds across time   |
| `OSCILLATING`   | bounded variance; slope ≈ 0; spectrum has dominant frequency            | Acceptable: emotion / pose periodicity |
| `DRIFTING_UP`   | slope > 0 sustained over > 25% of sequence                              | Warning: identity slowly lost         |
| `DRIFTING_DOWN` | slope < 0 sustained                                                     | Rare: identity tightening (often OK)  |
| `DIVERGENT`     | drift exceeds VIOLATION band at any point; slope unbounded              | Constitutional failure: identity gone |

The shape is computed from the trajectory series; it is not an opinion.
A canonical algorithm (linear regression over windowed identity drift,
+ variance analysis) will be specified in the Phase 0 validator.

---

## §7. Shot boundaries

A shot boundary is a frame index where the rendered subject is
expected to discontinuously change. Standard kinds:

| Kind         | Allowed identity drift at boundary                                 |
| ------------ | ------------------------------------------------------------------ |
| `HARD_CUT`   | Up to `ε_cut_drift = 0.10` (same subject, new camera/light)        |
| `CROSSFADE`  | Up to `ε_fade_drift = 0.06` (blended subject)                      |
| `MORPH`      | Up to `ε_morph_drift = 0.20` (deliberate identity transformation) |
| `UNKNOWN`    | Treated as VIOLATION until classified                              |

If the sequence has detected shot boundaries that are not declared in
`shot_structure.shot_boundaries[]`, the validator flags
`UNDECLARED_BOUNDARY` and the verdict becomes `REWORK` (re-evaluate
with boundaries declared) or `REJECT` (if drift exceeds even the most
permissive band).

---

## §8. Intentional drift annotations

Declared drift is constitutional drift. To declare it:

```json
{
  "frame_index_range":     [240, 280],
  "type":                  "EMOTION_TRANSITION",
  "reason":                "HELEN shifts from contemplative to alert when the kernel daemon restarts",
  "magnitude_allowed":     0.12,
  "approving_operator":    "JMT",
  "justification_receipt": "sha256:<JUSTIFIED_DEVIATION_V0-receipt-hash>"
}
```

Within `[240, 280]`, identity drift up to `0.12` does **not** count
toward the failure rule. Outside that range, normal V1 thresholds
apply.

An annotation without a matching `JUSTIFIED_DEVIATION_V0` receipt is
schema-invalid. Annotations cannot be added retroactively to mask
drift that wasn't declared at render time (the receipt's timestamp
must precede the sequence receipt's `timestamp_start`).

---

## §9. Example (single-shot, healthy)

```json
{
  "type": "IDENTITY_GATE_RECEIPT_V1_SEQUENCE",
  "sequence_id": "SEQ-20260517-0042",
  "timestamp_start": "2026-05-17T15:00:00Z",
  "timestamp_end":   "2026-05-17T15:00:10Z",

  "asset": {
    "type": "video_sequence",
    "hash": "sha256:a1b2c3...",
    "frame_count": 240,
    "fps": 24.0,
    "duration_sec": 10.0
  },

  "canonical_identity": {
    "anchor_id": "HELEN_CANON_V1",
    "version": "v1"
  },

  "per_frame_receipts": [
    { "frame_index": 0,   "receipt_hash": "sha256:f0...", "verdict": "PASS" },
    { "frame_index": 1,   "receipt_hash": "sha256:f1...", "verdict": "PASS" },
    "... (238 more) ..."
  ],

  "trajectory": {
    "identity_drift_series":  [0.041, 0.043, 0.040, "..."],
    "cycle_error_series":     [0.028, 0.030, 0.027, "..."],
    "style_drift_series":     [0.018, 0.019, 0.018, "..."],
    "temporal_drift_series":  [0.002, 0.001, 0.002, "..."]
  },

  "trajectory_metrics": {
    "max_identity_drift":    0.049,
    "mean_identity_drift":   0.042,
    "p95_identity_drift":    0.047,
    "drift_slope":           0.00002,
    "drift_variance":        0.00004,
    "cumulative_drift":      10.08,
    "max_temporal_drift":    0.004,
    "shot_continuity_score": 0.98
  },

  "shot_structure": {
    "shot_boundaries": [],
    "shot_count": 1
  },

  "intentional_drift_annotations": [],

  "sequence_evaluation": {
    "per_frame_summary":   { "pass_count": 240, "rework_count": 0, "reject_count": 0 },
    "drift_band":          "ADMIT",
    "shot_consistency":    "PASS",
    "trajectory_shape":    "STABLE",
    "overall_risk_score":  0.15
  },

  "decision": {
    "verdict":    "PASS",
    "confidence": 0.93,
    "reason":     "Stable trajectory, low drift, single-shot, no boundary issues.",
    "required_fixes": [],
    "rework_frame_ranges": []
  },

  "authority": false,
  "claim": "NO_CLAIM",
  "cumulative_hash": "sha256:9c4d7e..."
}
```

---

## §10. Example (multi-shot, REWORK with rework_frame_ranges)

```json
{
  "sequence_evaluation": {
    "per_frame_summary":  { "pass_count": 540, "rework_count": 60, "reject_count": 0 },
    "drift_band":         "DRIFT",
    "shot_consistency":   "SOFT_FAIL",
    "trajectory_shape":   "DRIFTING_UP",
    "overall_risk_score": 0.42
  },
  "decision": {
    "verdict":    "REWORK",
    "confidence": 0.82,
    "reason":     "Identity drift trends upward across shot 3 (frames 360-420). Shot boundary at frame 360 has higher drift than declared (0.18 actual vs 0.10 allowed for HARD_CUT). Re-render frames 360-420 with reinforced identity anchor.",
    "required_fixes": [
      "Re-render frames 360-420 with identity_anchor_weight increased to 1.5",
      "Add intentional_drift_annotation if the drift is desired",
      "Re-evaluate with this V1.1 receipt"
    ],
    "rework_frame_ranges": [[360, 420]]
  }
}
```

---

## §11. Storage

Sequence receipts are written append-only to:

```
ledgers/identity_gate_v1.ndjson         ← V1 frame receipts
ledgers/identity_gate_v1_sequence.ndjson ← V1.1 sequence receipts
```

The sequence sub-ledger references frame receipts by hash; the two
sub-ledgers stay separate so that frame-level replay does not require
parsing sequence aggregates and vice versa.

Cross-references to the sovereign ledger occur only when MAYOR signs
a `PASS` sequence verdict into a canon admission event.

---

## §12. Validator extensions (Phase 0)

In addition to V1's 7 rules:

8. `asset.type` must equal `"video_sequence"`.
9. `per_frame_receipts.length == asset.frame_count`.
10. All `trajectory.*_series` arrays must have the documented lengths
    (`frame_count` for per-frame series; `frame_count - 1` for temporal).
11. Every `shot_boundary.at_frame` ∈ `[0, frame_count)` and strictly
    increasing.
12. Every `intentional_drift_annotation.frame_index_range` is within
    `[0, frame_count)` and the corresponding `justification_receipt`
    must exist and timestamp-precede `timestamp_start`.
13. If `decision.verdict == "REWORK"` then `rework_frame_ranges` is
    non-empty AND all ranges ⊆ `[0, frame_count)`.
14. `trajectory_shape` must match the computed shape from the series
    (validator recomputes; mismatch is `SHAPE_MISMATCH` violation).
15. `sequence_evaluation.per_frame_summary` counts must equal the
    actual verdict distribution in `per_frame_receipts[]`.

Validator implementation pointer:

```
helen_os/governance/identity_gate_receipt_sequence_validator.py
tests/test_identity_gate_receipt_v1_sequence.py
```

---

## §13. Integration with V1

A V1.1 sequence receipt **contains** V1 frame receipts. It does not
replace them. The relationship:

```
Render video
   │
   ▼
For each frame:
   produce V1 receipt
   append to ledgers/identity_gate_v1.ndjson
   │
   ▼
Compute trajectory from frame receipts + raw drift signals
Compute shot boundaries (auto-detect or read from director packet)
Compute trajectory shape
   │
   ▼
Produce V1.1 sequence receipt
   references all V1 frame receipts by hash
   adds trajectory + shot_structure + sequence_evaluation
   issues sequence-level verdict
   │
   ▼
Append to ledgers/identity_gate_v1_sequence.ndjson
   │
   ▼
MAYOR sees the sequence verdict (not the 240 frame verdicts)
MAYOR signs or refuses canon admission
```

A frame receipt is necessary but not sufficient to admit a video. The
sequence receipt is the unit of admission for temporal media.

---

## §14. Admission sidecar

When/if REDUCER admits this schema:

```
sha256: <pending>
test_pointer: tests/test_identity_gate_receipt_v1_sequence.py
validator_pointer: helen_os/governance/identity_gate_receipt_sequence_validator.py
parent_schema: IDENTITY_GATE_RECEIPT_V1
parent_gate: HELEN_IDENTITY_GATE_V1
parent_theory: CONSTITUTIONAL_MANIFOLD_RENDERING_V0
proposer: HER
attestor: REDUCER (pending)
ledger_receipt: <pending>
unblocks: HELEN_SEEDANCE_BACKEND_V0, HELEN_HEYGEN_BACKEND_V0 (for video output)
```

Until then: SCHEMA_DRAFT, NO_SHIP, APPEND_ONLY proposal.

---

## §15. The single line

> **A video that passed frame-by-frame can still fail as a video.
> The sequence receipt is what makes temporal identity admissible.**
