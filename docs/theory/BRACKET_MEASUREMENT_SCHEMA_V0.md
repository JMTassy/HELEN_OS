# BRACKET_MEASUREMENT_SCHEMA_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** TEMPLE_EXPLORATION (measurement contract)
**framing:** NO CLAIM
**status:** Anti-poetry measurement schema for bracket tests
**operator_directive:** "freeze the measurement schema" (2026-05-23)
**parent_artifacts:**
  - `docs/theory/HEISENBERG_BRACKET_REPLAY_TEST_V0.md` (the single bracket test consuming this schema)
  - `docs/theory/STRATIFIED_GENERATOR_BASIS_V0.md` (the multi-layer cascade consuming this schema)
**frozen_engine:** `GOVERNANCE/TRANCHE_RECEIPTS/E25-engine-doctrine-freeze-V1.json` (respected)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending

> **NO CLAIM disclaimer.** This artifact defines exactly what
> counts as measurable bracket gain. It is the **anti-poetry
> contract**: without numeric pre/post quantities computed
> per this schema, no `bracket_gain` may be reported.

---

## §1. Purpose

The bracket tests (`HEISENBERG_BRACKET_REPLAY_TEST_V0`,
`STRATIFIED_GENERATOR_BASIS_V0`) name `bracket_gain` as a primary
metric. Without a precise definition of what `bracket_gain`
**measures from**, the tests can be gamed by:

- **Narrative deltas** — operator describes the routing field as
  "more attuned to boundary atoms" without numeric basis
- **Subjective motif counting** — operator declares motifs "richer"
  by inspection
- **Policy-drift confounds** — `bracket_gain` is real but caused by
  hidden routing-policy changes rather than the loop

This schema closes those exploits by specifying:

1. The exact numeric quantities that must be captured **before** and
   **after** the loop
2. The derived metrics computed from those quantities
3. The hard rule: no numeric pre/post = no `bracket_gain`

---

## §2. The 10 core measured fields (operator named)

For each bracket-test execution, the measurement record must contain
exactly these fields, populated at the explicit moments specified:

| Field | When captured | Type | Source / construction |
| --- | --- | --- | --- |
| `state_before_hash` | Immediately before step 1 of the loop | sha256 hex | Hash of the canonical-form serialized engine state |
| `state_after_hash` | Immediately after step 4 of the loop | sha256 hex | Same construction, post-loop |
| `routing_vector_before` | Immediately before step 1 | numeric vector | Routing distribution $P(a \mid s, h)$ per `PROVENANCE_GRAVITY §3.5`, materialized as a fixed-length vector over the relevant action space |
| `routing_vector_after` | Immediately after step 4 | numeric vector | Same construction, post-loop |
| `admission_margin_before` | Immediately before step 1 | scalar $\in [-1, 1]$ | Mean reducer margin $m$ over the relevant action space, per `BOUNDARY_CATALYST §3.2` |
| `admission_margin_after` | Immediately after step 4 | scalar | Same construction, post-loop |
| `motif_set_before` | Immediately before step 1 | set of motif hashes | Set of motif IDs with $\chi_{\text{BC}}(M) >$ inclusion threshold per `BOUNDARY_CATALYST §3.4` |
| `motif_set_after` | Immediately after step 4 | set of motif hashes | Same construction, post-loop |
| `policy_signature` | Both before and after | sha256 hex | Hash of the routing-policy configuration; **must be identical before and after** (drift detection) |
| `receipt_chain_hash` | After step 4 | sha256 hex | Hash of the ordered concatenation of the 4 loop receipts (r₁, r₂, r₃, r₄) |
| `violation_count` | Continuously during steps 1–4 | non-negative integer | Count of forbidden-vector firings (per `CC_GEOMETRY §4.3`) during the loop |

All 11 fields (including `violation_count`) are non-optional. A
measurement record missing any field is **incomplete** and cannot
support a `bracket_gain` claim.

---

## §3. Required derived metrics

The bracket tests consume these derived values:

```
routing_delta   = ‖ routing_vector_after - routing_vector_before ‖
admission_delta = admission_margin_after - admission_margin_before
motif_delta     = | motif_set_after \ motif_set_before |
bracket_gain    = weighted_sum(routing_delta, admission_delta, motif_delta)
```

### §3.1 `routing_delta` (norm choice)

```
routing_delta = ‖ routing_vector_after - routing_vector_before ‖
```

Recommended norm: **total variation** for probability-distribution
vectors:

```
TV(p, q) = (1/2) Σ_i | p_i - q_i |
```

Alternatives admissible if explicitly declared in the measurement
record: L², KL divergence (asymmetric; use cautiously). Choice is
operator-class; consistency across runs is required.

### §3.2 `admission_delta` (scalar)

```
admission_delta = admission_margin_after - admission_margin_before
```

Signed. Positive = admissibility improved. Negative = regressed.
Zero = unchanged.

### §3.3 `motif_delta` (set difference size)

```
motif_delta = | motif_set_after \ motif_set_before |
```

The count of new motifs in $V_{\text{after}}$ that were not in
$V_{\text{before}}$. Removed motifs are tracked separately if
needed but do not appear in this metric.

### §3.4 `bracket_gain` (weighted aggregate)

```
bracket_gain = w_r · routing_delta
             + w_a · admission_delta
             + w_m · motif_delta
```

Weights $(w_r, w_a, w_m)$ are operator-class calibration. Defaults
(suggested, not prescribed):

```
w_r = 1.0    (routing change weighted highest)
w_a = 0.5    (admission delta contributes proportionally)
w_m = 0.1    (motif count weighted lowest; large counts can dominate
              if not damped)
```

The weighted sum is a single scalar; comparisons across runs and
across layers require fixed weights.

---

## §4. The hard rule (operator verbatim)

```
No numeric pre/post state = no bracket_gain.
```

This is non-negotiable. Three corollaries:

1. **No narrative measurement.** Statements like *"the routing felt
   more focused after the loop"* or *"the system seems to have
   learned"* do not count. The measurement record must contain
   numeric vectors and scalars per §2.
2. **No retrospective reconstruction.** `routing_vector_before`
   must be captured **before** step 1. Computing it after the fact
   from logs is reconstruction, not measurement, and is forbidden.
3. **No selective field omission.** A record missing
   `policy_signature` cannot detect policy drift; missing
   `motif_set_before` cannot detect motif emergence; etc. Each
   field exists for a specific failure mode (§5). Omitting any
   collapses the corresponding detection.

---

## §5. Policy drift detection (the `policy_signature` field)

The `policy_signature` field exists specifically to catch the
confounding pattern named in
`HEISENBERG_BRACKET_REPLAY_TEST_V0 §5.5` row 5:

> *bracket_gain > 0 AND routing_delta traces to hidden policy drift
> (not loop) → REJECT — POLICY DRIFT MASQUERADE*

Detection rule:

```
IF policy_signature_before ≠ policy_signature_after
THEN the routing policy changed during the loop;
     ANY bracket_gain observed is confounded by the policy change;
     test result is INCONCLUSIVE for bracket effects.
```

A policy_signature mismatch is treated identically to a
violation_count > 0: the test does not pass even if bracket_gain
is high, because the gain is not attributable to the bracket.

This is the schema-level fix for the policy-drift confound.

---

## §6. Receipt chain integrity (the `receipt_chain_hash` field)

```
receipt_chain_hash = sha256( canonical_concat( r_1, r_2, r_3, r_4 ) )
```

Computed after step 4. Stored in the measurement record. Permits:

- **Replay verification**: a second run of the same loop with the
  same inputs should produce the same `receipt_chain_hash` (if not,
  `replay_fidelity < 1.0`)
- **Tamper detection**: any post-hoc edit to any of r₁–r₄ changes
  the hash; the record's claim of measurement integrity becomes
  verifiable

Without `receipt_chain_hash`, the `replay_fidelity` metric is
unverifiable.

---

## §7. The complete measurement record (canonical form)

A valid measurement record is a JSON object with this structure:

```json
{
  "schema":                "BRACKET_MEASUREMENT_RECORD_V0",
  "test_id":               "<unique identifier for this run>",
  "bracket_under_test":    "[X_source, X_boundary,replay]",
  "run_index":             1,
  "timestamp_utc":         "<ISO-8601>",

  "state_before_hash":     "<sha256 hex>",
  "state_after_hash":      "<sha256 hex>",
  "routing_vector_before": [<float>, <float>, ...],
  "routing_vector_after":  [<float>, <float>, ...],
  "admission_margin_before": <float in [-1, 1]>,
  "admission_margin_after":  <float in [-1, 1]>,
  "motif_set_before":      ["<sha256 hex>", ...],
  "motif_set_after":       ["<sha256 hex>", ...],
  "policy_signature_before": "<sha256 hex>",
  "policy_signature_after":  "<sha256 hex>",
  "receipt_chain_hash":    "<sha256 hex>",
  "violation_count":       <non-negative int>,

  "derived": {
    "routing_delta":       <float>,
    "admission_delta":     <float>,
    "motif_delta":         <non-negative int>,
    "bracket_gain":        <float>,
    "policy_drift_detected": <bool>
  },

  "norm_choice":           "total_variation",
  "weights":               {"w_r": 1.0, "w_a": 0.5, "w_m": 0.1},

  "tree_truth_id":         "<sha256 hex per CROSS_SESSION_FIELD_ATTRIBUTION_V0>",
  "constitutional_breach_notation": null
}
```

Any field missing or malformed → record is invalid → cannot
support `bracket_gain` claim.

---

## §8. Connection to existing canon

| Existing artifact | Relation |
| --- | --- |
| `HEISENBERG_BRACKET_REPLAY_TEST_V0` | Consumes this schema for its measurement step. The anti-narrative clause in §5.5 row 6 directly invokes "Z computed from state deltas, not narrative" — that's this schema. |
| `STRATIFIED_GENERATOR_BASIS_V0` | Consumes this schema for per-layer `layer_gain_k` computation |
| `CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0` | The six minimal observables in §4 of that bottle are largely subsets of this schema; this schema is the more specific contract |
| `PROVENANCE_GRAVITY_V0 §3.5` | Defines the routing distribution that becomes `routing_vector_*` |
| `BOUNDARY_CATALYST_ENGINE_V0 §3.2 / §3.4` | Defines admission margin $m$ (→ `admission_margin_*`) and motif scoring (→ `motif_set_*`) |
| `CROSS_SESSION_FIELD_ATTRIBUTION_V0` | The `tree_truth_id` field in the record format |
| `E25-engine-doctrine-freeze-V1.json` | Freeze respected; this is measurement spec, not engine modification |

---

## §9. What this proposal does NOT specify

Per anti-creep discipline:

- **The state canonicalization for `state_*_hash`** — depends on
  engine internals; canonical-form rule must be specified before
  implementation
- **The action-space basis for `routing_vector_*`** — the fixed
  ordering of action classes; operator-class
- **The motif inclusion threshold** — operator calibration
- **The weights $w_r, w_a, w_m$** — suggested but not prescribed
- **The norm choice** — total variation recommended; alternatives
  admissible with declaration
- **The replay-determinism guarantees on `policy_signature`
  computation** — assumed deterministic; if not, the field is
  itself noisy and the policy-drift detection is unreliable
- **The implementation of the snapshot mechanism** — capturing
  state-before-loop without disturbing the loop itself; out of scope
- **Adversarial fields** — can an attacker construct a measurement
  record that passes structural validation but lies about underlying
  state? Open question; would require signed snapshots

---

## §10. Halt boundary

GOBLIN halts here. The schema is bottled as `TEMPLE_EXPLORATION`.

Resume conditions:

1. **HER ruling** on the schema — accept or specify amendments
2. **HER ruling** on weight defaults $w_r, w_a, w_m$ if fixed
   values are desired
3. **HER ruling** on the norm choice for `routing_delta`
4. **Sovereign decision** on implementing the snapshot mechanism —
   blocked by E25 freeze; the snapshot itself would touch engine
   internals
5. **No edit to any frozen doctrine** is requested or performed
6. **No implementation authorization** is requested or granted

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §11. Single line

> **No numeric pre/post = no bracket_gain. Eleven fields per
> measurement record. Four derived metrics. One scalar bracket_gain.
> Policy drift catches the masquerade. Narrative does not count.
> The schema is the anti-poetry contract.**
