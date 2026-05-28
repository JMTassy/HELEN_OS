# IDENTITY_GATE_RECEIPT_V1

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** SCHEMA_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Schema specification, proposal only
**parent:** `docs/proposals/HELEN_IDENTITY_GATE_V1.md`
**parent_theory:** `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md`

---

## §1. Purpose

The Identity Gate Receipt is a first-class constitutional artifact. It records
the outcome of an Identity Gate evaluation for any generative output (image,
video frame, or sequence). Its primary purpose is to make identity integrity
**auditable, replayable, and decision-traceable**.

It serves three functions:

- **Proof** — documents that an identity evaluation occurred and what the
  result was.
- **Traceability** — links the rendered asset back to its mathematical
  manifold state and source.
- **Governance signal** — provides structured input for the Reducer and
  future automated systems.

It is **not** an admission decision. Only the Reducer can admit content into
trusted state.

---

## §2. Core principles

- `authority` is always `false`
- `claim` is always `NO_CLAIM`
- The receipt must be **deterministic** (same evaluation → same receipt)
- The receipt must be **replayable** (from chain inputs alone)
- The receipt must be **hashable** and linkable into the Ledger
- The receipt must support both single-frame and temporal evaluation

---

## §3. Full schema (`IDENTITY_GATE_RECEIPT_V1`)

```json
{
  "type": "IDENTITY_GATE_RECEIPT_V1",
  "gate_id": "string (unique identifier)",
  "timestamp": "ISO 8601 datetime",

  "asset": {
    "hash": "string (sha256 of the rendered asset)",
    "type": "image | video_frame | video_sequence",
    "uri": "string (optional reference)"
  },

  "canonical_identity": {
    "anchor_id": "string (e.g. HELEN_CANON_V1)",
    "version": "string"
  },

  "manifold_state": {
    "original_math_hash":     "string (hash of input mathematical state)",
    "reconstructed_math_hash":"string (hash after Face → Math → Face cycle)",
    "cycle_consistency_error":"float (normalized distance)"
  },

  "identity_metrics": {
    "identity_drift":   "float (distance from canonical anchor)",
    "style_drift":      "float",
    "expression_drift": "float",
    "pose_drift":       "float",
    "temporal_drift":   "float (only for sequences)"
  },

  "gate_evaluation": {
    "cycle_consistency":    "PASS | SOFT_FAIL | HARD_FAIL",
    "identity_persistence": "PASS | SOFT_FAIL | HARD_FAIL",
    "provenance_check":     "PASS | FAIL",
    "receipt_completeness": "PASS | FAIL",
    "overall_risk_score":   "float (0.0 – 1.0)"
  },

  "decision": {
    "verdict":        "PASS | REWORK | REJECT",
    "confidence":     "float (0.0 – 1.0)",
    "reason":         "string (concise justification)",
    "required_fixes": "array of strings"
  },

  "context": {
    "proposal_id":          "string (optional link to HER proposal)",
    "director_packet_hash": "string (optional)",
    "source_hashes":        "array of strings",
    "render_backend":       "string (e.g. Seedance, Kling, internal)"
  },

  "authority": false,
  "claim": "NO_CLAIM",

  "previous_receipts": "array of strings (hashes of related receipts)",
  "cumulative_hash":   "string (for chaining)"
}
```

---

## §4. Field explanations

| Field group           | Purpose                                                                 | Required    |
| --------------------- | ----------------------------------------------------------------------- | ----------- |
| `asset`               | Identifies the exact rendered output being evaluated                    | Yes         |
| `canonical_identity`  | Links to the authoritative identity anchor                              | Yes         |
| `manifold_state`      | Records the Math ↔ Face cycle consistency result                        | Yes         |
| `identity_metrics`    | Quantifies different types of drift from the canonical state            | Yes         |
| `gate_evaluation`     | Structured pass/fail results per evaluation dimension                   | Yes         |
| `decision`            | Final gate outcome + justification                                      | Yes         |
| `context`             | Links the evaluation back to its originating proposal / render process  | Recommended |
| `previous_receipts`   | Enables chaining of receipts for audit trails                           | Recommended |
| `cumulative_hash`     | Supports deterministic replay and ledger integration                    | Yes         |

---

## §5. Verdict logic

| Verdict    | Meaning                                  | Typical conditions                                       | Next step                       |
| ---------- | ---------------------------------------- | -------------------------------------------------------- | ------------------------------- |
| **PASS**   | Meets identity and consistency standards | Low drift + strong cycle consistency + complete receipts | Eligible for Reducer            |
| **REWORK** | Issues are correctable                   | Moderate drift or missing non-critical receipts          | Return with `required_fixes`    |
| **REJECT** | Fundamental identity failure             | High drift, failed cycle consistency, broken provenance  | Cannot proceed                  |

### §5.1 Verdict alignment with HELEN_IDENTITY_GATE_V1

The receipt verdicts map to the gate's constitutional verdicts (parent
doctrine §3):

| Receipt verdict | Gate verdict (parent §3) | Meaning                                  |
| --------------- | ------------------------ | ---------------------------------------- |
| `PASS`          | `ADMIT`                  | MAYOR may sign for canon                 |
| `REWORK`        | `QUARANTINE`             | Preserved unsigned, reviewable           |
| `REJECT`        | `BLOCK`                  | Fail-closed; no admission                |

`PASS` / `REWORK` / `REJECT` are the **receipt-level vocabulary** —
what the evaluation found. `ADMIT` / `QUARANTINE` / `BLOCK` are the
**constitutional verdicts** — what the gate authorizes downstream.
The two are co-defined and one-to-one.

---

## §6. Example (filled receipt)

```json
{
  "type": "IDENTITY_GATE_RECEIPT_V1",
  "gate_id": "IG-20260517-0087",
  "timestamp": "2026-05-17T14:32:11Z",

  "asset": {
    "hash": "sha256:7f3a9b2c...",
    "type": "image"
  },

  "canonical_identity": {
    "anchor_id": "HELEN_CANON_V1",
    "version": "v1"
  },

  "manifold_state": {
    "original_math_hash":      "sha256:4e2f1a...",
    "reconstructed_math_hash": "sha256:4e2f1a...",
    "cycle_consistency_error": 0.031
  },

  "identity_metrics": {
    "identity_drift":   0.048,
    "style_drift":      0.022,
    "expression_drift": 0.015
  },

  "gate_evaluation": {
    "cycle_consistency":    "PASS",
    "identity_persistence": "PASS",
    "provenance_check":     "PASS",
    "receipt_completeness": "PASS",
    "overall_risk_score":   0.19
  },

  "decision": {
    "verdict":        "PASS",
    "confidence":     0.91,
    "reason":         "Strong cycle consistency and low identity drift from canonical anchor.",
    "required_fixes": []
  },

  "authority": false,
  "claim": "NO_CLAIM",
  "cumulative_hash": "sha256:9c4d7e..."
}
```

---

## §7. Integration points

- **Media Receipt** — The Identity Gate Receipt is referenced inside the
  broader Media Receipt (one Media Receipt may contain many Identity
  Gate Receipts, e.g. one per frame in a sequence).
- **Reducer** — Uses `decision.verdict` and `gate_evaluation.overall_risk_score`
  as inputs for admission. The Reducer does **not** override a `REJECT`
  except via an explicit, justified, operator-signed deviation receipt
  (`JUSTIFIED_DEVIATION_V0`, see CMR §8.3).
- **Replay Engine** — Can reconstruct the exact gate evaluation using
  `cumulative_hash` and linked hashes (asset, anchor, manifold state).
- **HAL** — May reference previous gate receipts when auditing new proposals
  for the same identity (drift trends, recurring failure modes).
- **HELEN_DIRECTOR** — Calls the gate before SHIP; the receipt determines
  whether the storyboard proceeds.

---

## §8. Design notes

- The schema is intentionally **verbose** to maximize auditability. Brevity
  comes at the cost of replay precision; we choose replay.
- `cumulative_hash` enables chaining multiple gate evaluations over time
  (essential for video sequences and drift trend analysis).
- `required_fixes` provides actionable feedback when the verdict is
  `REWORK`. An empty array on `REWORK` is a schema violation.
- All numeric drift and error values should be **normalized** (typically
  0.0–1.0) for consistency across asset types and renderers.
- Optional fields are explicitly marked. Absence of a recommended field
  is allowed; absence of a required field is a schema violation that
  itself produces a `REJECT` at G2 (receipt completeness).
- The receipt is **append-only** in the sub-ledger. Corrections produce
  a new receipt that references the prior via `previous_receipts`.

---

## §9. Sequence and temporal extension (deferred)

For video sequences, the receipt's `asset.type` is `video_sequence` and
`identity_metrics.temporal_drift` becomes required. A separate doctrine
(`IDENTITY_GATE_RECEIPT_V1_SEQUENCE`) will specify:

- per-frame sub-receipts vs aggregated sequence-level receipt
- drift trajectory storage (`identity_drift_series`, `cycle_error_series`)
- shot-boundary handling
- intentional drift annotation (justified style transitions)

For now: single-frame evaluations only. Sequence support is V1.1 work.

---

## §10. Storage and chaining

Receipts are written append-only to:

```
ledgers/identity_gate_v1.ndjson
```

Each line is one complete receipt. `cumulative_hash` of each receipt is
computed from `sha256(canonicalize(receipt_without_cum_hash) + previous_cum_hash)`.
This makes the sub-ledger replayable and tamper-evident.

Cross-references to the sovereign ledger (`town/ledger_v1.ndjson`) occur
only when MAYOR signs a `PASS` receipt into a canon admission event.

---

## §11. Validator contract (Phase 0)

A receipt is **schema-valid** iff:

1. All required fields are present and typed correctly.
2. All `*_hash` fields match `^sha256:[0-9a-f]{64}$` (or the literal "sha256:..." in examples).
3. `gate_evaluation.overall_risk_score ∈ [0.0, 1.0]`.
4. `decision.confidence ∈ [0.0, 1.0]`.
5. If `decision.verdict == "REWORK"` then `decision.required_fixes.length > 0`.
6. If `asset.type == "video_sequence"` then `identity_metrics.temporal_drift` is present.
7. `cumulative_hash` verifies against the canonical hash function.

Validator implementation lives at (when written):

```
helen_os/governance/identity_gate_receipt_validator.py
tests/test_identity_gate_receipt_v1.py
```

---

## §12. Admission sidecar

When/if REDUCER admits this schema:

```
sha256: <pending>
test_pointer: tests/test_identity_gate_receipt_v1.py
validator_pointer: helen_os/governance/identity_gate_receipt_validator.py
parent_proposal: HELEN_IDENTITY_GATE_V1
parent_theory: CONSTITUTIONAL_MANIFOLD_RENDERING_V0
proposer: HER
attestor: REDUCER (pending)
ledger_receipt: <pending>
```

Until then: SCHEMA_DRAFT, NO_SHIP, APPEND_ONLY proposal.

---

## §13. The single line

> **A render without a complete, schema-valid Identity Gate Receipt
> is ungoverned media — observable, but not admissible.**
