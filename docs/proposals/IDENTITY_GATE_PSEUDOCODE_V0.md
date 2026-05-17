# IDENTITY_GATE_PSEUDOCODE_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** ALGORITHM_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Pseudocode specification, proposal only
**parent_gate:** `docs/proposals/HELEN_IDENTITY_GATE_V1.md`
**produces:** `docs/proposals/IDENTITY_GATE_RECEIPT_V1.md`
**parent_theory:** `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md`

---

## §1. Purpose

This document specifies **the algorithm** that produces an
`IDENTITY_GATE_RECEIPT_V1`. It is the bridge between:

- **The gate doctrine** (`HELEN_IDENTITY_GATE_V1.md`) — what the gate is
- **The receipt schema** (`IDENTITY_GATE_RECEIPT_V1.md`) — what the gate emits
- **The implementation** (not yet written) — what the gate does

Pseudocode lives between doctrine and code. It is **language-agnostic**
and **honest about which steps are structural vs which delegate to
scorers**. It does not pin Python, JS, Rust, or any specific runtime.

**Hard scope boundary:**

> This document specifies *what the gate computes*.
> It does **not** specify *how* to compute embedding scores, train models,
> or render assets. Those are downstream concerns.

---

## §2. Top-level algorithm

```
function identity_gate(render_artifact, identity_anchor, policy, receipt_store):
    """
    Run G1 → G2 → G3 → G4 in strict order with fail-fast.
    Emit a complete IDENTITY_GATE_RECEIPT_V1 regardless of verdict.

    Inputs:
        render_artifact     — the rendered output + its incoming bundle
        identity_anchor     — canonical HELEN identity (anchor_id + spec)
        policy              — tolerance bands ε_strict / ε_admit / ε_drift / τ_risk / τ_coh
        receipt_store       — prior receipts (for provenance lookup, hash verification)

    Output:
        receipt — a fully assembled IDENTITY_GATE_RECEIPT_V1
        side-effect — append receipt to ledgers/identity_gate_v1.ndjson
    """

    receipt = init_receipt(render_artifact, identity_anchor)

    # ── G1: PROVENANCE ────────────────────────────────────────────────────
    g1 = run_g1_provenance(render_artifact, receipt_store)
    receipt.stages.G1 = g1
    if not g1.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G1")

    # ── G2: RECEIPT COMPLETENESS ──────────────────────────────────────────
    g2 = run_g2_receipt_completeness(render_artifact)
    receipt.stages.G2 = g2
    if not g2.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G2")

    # ── G3: CYCLE CONSISTENCY ─────────────────────────────────────────────
    g3 = run_g3_cycle(render_artifact, identity_anchor, policy)
    receipt.stages.G3 = g3
    if g3.band == "VIOLATION":
        return finalize(receipt, verdict=BLOCK, first_violation="G3")
    # band STRICT, ADMIT, or DRIFT continues to G4

    # ── G4: RISK + COHERENCE ──────────────────────────────────────────────
    g4 = run_g4_risk_coherence(render_artifact, policy)
    receipt.stages.G4 = g4
    if not g4.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G4")

    # ── Verdict composition ───────────────────────────────────────────────
    if g3.band == "DRIFT":
        verdict = QUARANTINE   # drift detected, preserved unsigned
    else:  # STRICT or ADMIT
        verdict = ADMIT

    return finalize(receipt, verdict=verdict)
```

**Termination:** the algorithm always returns a receipt. There is no
silent fall-through. Skipped stages are explicitly marked in the receipt
(see §7).

---

## §3. G1 — Provenance verification

```
function run_g1_provenance(render_artifact, receipt_store):
    checks = {}

    # Source known
    checks.source_known = (
        render_artifact.source_hash in canonical_sources(receipt_store)
    )

    # Model signed
    checks.model_signed = (
        render_artifact.model_version is not None
        and verify_model_signature(render_artifact.model_version)
    )

    # Prompt resolved
    checks.prompt_resolved = (
        render_artifact.prompt_hash in receipt_store.prompt_receipts
    )

    # Backend allowed
    checks.backend_allowed = (
        render_artifact.backend in policy.allowed_backends
        or render_artifact.backend == "EXPERIMENTAL"  # requires operator approval flag
    )

    pass = all(checks.values())
    details = build_g1_details(checks, render_artifact)
    return GateStageResult(pass=pass, checks=checks, details=details)
```

**Fail codes** (return without continuing):

- `UNKNOWN_PROVENANCE` — `source_known == false`
- `UNSIGNED_MODEL` — `model_signed == false`
- `UNKNOWN_BACKEND` — `backend_allowed == false`

---

## §4. G2 — Receipt completeness

```
function run_g2_receipt_completeness(render_artifact):
    required = [
        "prompt_receipt",
        "backend_receipt",
        "asset_hash",
        "identity_anchor_ref",
        "director_packet_ref",
        "ledger_position",
    ]
    fields_present = 0
    fields_required = len(required)
    hash_verifications = "all_pass"
    crossref_failures = []

    for field in required:
        value = render_artifact.bundle.get(field)
        if value is not None and value != "":
            fields_present += 1
        else:
            continue   # already counted as missing

        # Verify hash matches file content
        if is_hash_field(field) and not verify_content_hash(value, render_artifact):
            hash_verifications = "hash_mismatch_at:" + field

        # Verify cross-references resolve
        if is_crossref_field(field) and not resolve_crossref(value):
            crossref_failures.append(field)

    pass = (
        fields_present == fields_required
        and hash_verifications == "all_pass"
        and len(crossref_failures) == 0
    )

    return GateStageResult(
        pass=pass,
        fields_present=fields_present,
        fields_required=fields_required,
        hash_verifications=hash_verifications,
        crossref_failures=crossref_failures,
    )
```

**Fail codes:**

- `INCOMPLETE_RECEIPT` — `fields_present < fields_required`
- `HASH_MISMATCH` — `hash_verifications != "all_pass"`
- `BROKEN_CROSSREF` — `crossref_failures != []`

---

## §5. G3 — Cycle consistency

```
function run_g3_cycle(render_artifact, identity_anchor, policy):
    """
    Compute d_cycle per CMR §8. Map to tolerance band.
    """
    # T1: structural identity (manifold coordinate distance)
    math_original = render_artifact.manifold_state.original_math
    math_recovered = encode_face_to_math(render_artifact.rendered_face)   # ← delegates to encoder Φ
    d_T1 = norm2(math_original - math_recovered) / norm2(math_original)

    # T2: semantic identity (embedding cosine)
    emb_original = identity_anchor.embedding
    emb_rendered = embed(render_artifact.rendered_face)                   # ← delegates to non-sovereign scorer
    d_T2 = 1.0 - cosine_similarity(emb_original, emb_rendered)

    # T3: trajectory continuity (only for sequence context)
    d_T3 = render_artifact.trajectory_continuity or 0.0

    # Weighted total — weights are policy-admitted
    weights = policy.cycle_weights   # default (0.3, 0.5, 0.2)
    d_cycle = (
        weights[0] * d_T1
        + weights[1] * d_T2
        + weights[2] * d_T3
    )

    # Map to band
    if d_cycle <= policy.ε_strict:
        band = "STRICT"
    elif d_cycle <= policy.ε_admit:
        band = "ADMIT"
    elif d_cycle <= policy.ε_drift:
        band = "DRIFT"
    else:
        band = "VIOLATION"

    pass = band != "VIOLATION"   # DRIFT escalates verdict but doesn't block here

    return GateStageResult(
        pass=pass,
        d_cycle=d_cycle,
        tier_breakdown={"T1": d_T1, "T2": d_T2, "T3": d_T3},
        weights=weights,
        band=band,
        tolerance_ε_admit=policy.ε_admit,
        tolerance_ε_drift=policy.ε_drift,
    )
```

**Honesty about delegation:**

- `encode_face_to_math(...)` — implemented by the Math↔Face encoder (CMR §3).
  Until that exists, this returns a stub or a structural-only distance.
- `embed(...)` — implemented by a non-sovereign scorer (CLIP, face-rec API).
  The scorer is a **signal source**, not an authority (HELEN_IDENTITY_GATE_V1 §7).

**Fail codes:**

- `CYCLE_VIOLATION` — `band == "VIOLATION"`
- `DRIFT_DETECTED` — verdict-modifier, not a hard block (escalates to QUARANTINE)

---

## §6. G4 — Risk + coherence

```
function run_g4_risk_coherence(render_artifact, policy):
    risk_score = compute_risk_score(render_artifact, policy.risk_model)
    coherence_score = compute_coherence_score(render_artifact, policy.coherence_model)

    banned_matches = scan_for_banned_patterns(
        render_artifact,
        policy.banned_patterns,
    )

    pass = (
        risk_score <= policy.τ_risk
        and coherence_score >= policy.τ_coh
        and len(banned_matches) == 0
    )

    return GateStageResult(
        pass=pass,
        risk_score=risk_score,
        coherence_score=coherence_score,
        banned_matches=banned_matches,
        τ_risk=policy.τ_risk,
        τ_coh=policy.τ_coh,
    )
```

**Fail codes:**

- `RISK_THRESHOLD` — `risk_score > τ_risk`
- `COHERENCE_THRESHOLD` — `coherence_score < τ_coh`
- `BANNED_PATTERN` — `banned_matches != []`

---

## §7. Skipped stages

If G1 fails, G2/G3/G4 must be marked as skipped:

```
function mark_skipped_stages(receipt, first_violation):
    later_stages = stages_after(first_violation)   # e.g. G1 fail → [G2, G3, G4]
    for stage_id in later_stages:
        receipt.stages[stage_id] = {
            "skipped": true,
            "reason": first_violation + "_FAILED",
        }
    return receipt
```

This makes the receipt complete and self-describing even on early
termination. The auditor sees exactly which checks ran and which were
skipped because of an earlier failure.

---

## §8. Receipt finalization

```
function finalize(receipt, verdict, first_violation=null):
    receipt.verdict = verdict
    receipt.first_violation = first_violation

    # Compose modifiers from stage results
    receipt.modifiers = []
    if receipt.stages.G3 and receipt.stages.G3.band == "DRIFT":
        receipt.modifiers.append("DRIFT_DETECTED")

    # Mark skipped stages
    if first_violation is not null:
        receipt = mark_skipped_stages(receipt, first_violation)

    # Stamp time + chain anchors
    receipt.timestamp_utc = now_utc_iso()
    receipt.kernel_hash = git_head()
    receipt.policy_hash = sha256_canonical(policy)
    receipt.previous_cum_hash = read_previous_cum_hash(FRAME_LEDGER_PATH)

    # Compute cumulative hash over canonical form WITHOUT cum_hash field
    canonical = canonicalize(omit(receipt, "cum_hash"))
    receipt.cum_hash = sha256(canonical + receipt.previous_cum_hash)

    # Append to sub-ledger (the only side effect)
    append_line(FRAME_LEDGER_PATH, canonical_json(receipt) + "\n")

    return receipt
```

**Side-effect discipline:** the only write the gate performs is the
append to its own sub-ledger. No other state is mutated.

---

## §9. Verdict composition table

| G3 band      | G4 pass | Verdict     | Modifiers          |
| ------------ | ------- | ----------- | ------------------ |
| STRICT       | ✓       | `ADMIT`     | (none)             |
| ADMIT        | ✓       | `ADMIT`     | (none)             |
| DRIFT        | ✓       | `QUARANTINE`| `DRIFT_DETECTED`   |
| VIOLATION    | —       | `BLOCK`     | (G4 skipped)       |
| any          | ✗       | `BLOCK`     | (G3-pass irrelevant)|
| G1 fail      | —       | `BLOCK`     | (G2/G3/G4 skipped) |
| G2 fail      | —       | `BLOCK`     | (G3/G4 skipped)    |

The composition is **monotone**: no path admits a render that has any
hard failure. DRIFT is the only soft state.

---

## §10. Phase 2 reference: the Manual Gate

Per `HELEN_IDENTITY_GATE_V1.md` §9, **Phase 2** is a manual gate. It
allows the gate to start enforcing receipts before any ML / encoder
exists. The pseudocode:

```
function manual_gate(render_artifact, identity_anchor, operator_input):
    """
    Phase 2 reference implementation.
    G1 + G2 run automatically (structural).
    G3 + G4 are decided by an operator looking at the render.
    The output is still a valid IDENTITY_GATE_RECEIPT_V1.
    """
    receipt = init_receipt(render_artifact, identity_anchor)

    # G1 + G2 are structural — automatic
    g1 = run_g1_provenance(render_artifact, receipt_store=...)
    receipt.stages.G1 = g1
    if not g1.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G1")

    g2 = run_g2_receipt_completeness(render_artifact)
    receipt.stages.G2 = g2
    if not g2.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G2")

    # G3 + G4 are delegated to the operator
    display_render(render_artifact)
    display_anchor(identity_anchor)
    operator_verdict = prompt(
        "Identity preserved? (ADMIT / QUARANTINE / BLOCK): "
    )
    operator_estimated_drift = prompt(
        "Estimated identity drift (0.0 = identical, 1.0 = unrecognizable): "
    )
    operator_reason = prompt("One-line reason: ")

    # Synthesize a G3 result from the operator's drift estimate
    band = band_from_drift(operator_estimated_drift, policy)
    receipt.stages.G3 = GateStageResult(
        pass=(band != "VIOLATION"),
        d_cycle=operator_estimated_drift,
        tier_breakdown={"T1": null, "T2": null, "T3": null},   # not computed
        weights=null,
        band=band,
        manual=true,
        operator_reason=operator_reason,
    )

    # Synthesize a G4 result (operator's overall judgment)
    receipt.stages.G4 = GateStageResult(
        pass=(operator_verdict != "BLOCK"),
        risk_score=null,
        coherence_score=null,
        banned_matches=[],
        manual=true,
        operator_verdict=operator_verdict,
    )

    # Verdict is the operator's call, constrained by G3
    if not receipt.stages.G3.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G3")
    if not receipt.stages.G4.pass:
        return finalize(receipt, verdict=BLOCK, first_violation="G4")

    if receipt.stages.G3.band == "DRIFT":
        verdict = QUARANTINE
    else:
        verdict = ADMIT

    return finalize(receipt, verdict=verdict)
```

The manual gate produces a **fully schema-valid** receipt. The
`manual: true` flag in stage results tells the auditor "this was
operator-driven, not algorithmic." That's a feature, not a regression:
it lets us start enforcing the gate while the ML stack is built.

---

## §11. What this pseudocode does NOT specify

To prevent scope creep:

- **Implementation language** — Python, Rust, OCaml, JS — out of scope
- **Encoder Φ details** — left to CMR §3 / Phase 5 implementation
- **Scorer implementation** — CLIP, face-rec, custom — left to operator
- **Render API** — Seedance, HeyGen, Kling, internal — out of scope
- **Storage backend** — NDJSON, SQLite, S3 — implementation choice
- **Concurrency model** — single-thread, async, parallel — implementation choice
- **Caching strategy** — cold call, memoized, batched — implementation choice
- **Failure recovery** — retries, dead-letter queues — implementation choice

This document specifies **the flow**, not **the engineering**.

---

## §12. Tests this pseudocode should pass

Future implementation tests (when the algorithm is built):

| # | Test                                                                 |
| - | -------------------------------------------------------------------- |
| 1 | `identity_gate(valid_render, anchor, policy)` returns `ADMIT`        |
| 2 | G1 fail → returns immediately with verdict BLOCK, G2/G3/G4 skipped   |
| 3 | G2 fail → returns BLOCK, G3/G4 skipped                               |
| 4 | G3 in DRIFT band → returns QUARANTINE, G4 still runs                 |
| 5 | G3 in VIOLATION band → BLOCK, G4 skipped                             |
| 6 | G4 fail → BLOCK                                                       |
| 7 | Every code path produces a schema-valid receipt                       |
| 8 | The only side effect is one append to `ledgers/identity_gate_v1.ndjson` |
| 9 | `cum_hash` chain is monotone over a multi-call session                |
| 10 | Manual gate produces schema-valid receipt with `manual: true` flags  |

Test pointer: `tests/test_identity_gate_pseudocode_v0.py` (to be
written when the algorithm is implemented).

---

## §13. Stack position

The pseudocode is the **algorithm contract** that sits between doctrine
and implementation:

```
HELEN_IDENTITY_GATE_V1             ← what the gate IS (doctrine)
        ▲
        │ describes
        │
IDENTITY_GATE_PSEUDOCODE_V0        ← what the gate COMPUTES (this doc)
        │
        │ implements
        ▼
[concrete code in any language]    ← what the gate RUNS (not yet written)
        │
        │ emits
        ▼
IDENTITY_GATE_RECEIPT_V1           ← what the gate PRODUCES
        │
        │ aggregated by
        ▼
IDENTITY_GATE_RECEIPT_V1_SEQUENCE  ← per-sequence wrapper
        │
        │ wrapped by
        ▼
MEDIA_RECEIPT_V1                   ← parent envelope
        │
        │ presented to
        ▼
MAYOR / REDUCER                    ← admission (reducer-only)
```

The HAL stack lock is now complete:

```
✅ HELEN_IDENTITY_GATE_V1                doctrine bottled
✅ IDENTITY_GATE_RECEIPT_V1              schema bottled
✅ IDENTITY_GATE_RECEIPT_V1_SEQUENCE     schema + validator + 12/12 tests
✅ MEDIA_RECEIPT_V1                      schema + validator + 10/10 tests
✅ IDENTITY_GATE_PSEUDOCODE_V0           algorithm bottled (this doc)
```

The Identity Gate layer is now **doctrinally and schematically complete**.
Implementation (Phase 1–5 per HELEN_IDENTITY_GATE_V1 §9) is the next
frontier and unblocks Seedance/HeyGen video pipelines.

---

## §14. Admission sidecar

When/if REDUCER admits this pseudocode:

```
sha256: <pending>
test_pointer: tests/test_identity_gate_pseudocode_v0.py
parent_gate: HELEN_IDENTITY_GATE_V1
produces_schema: IDENTITY_GATE_RECEIPT_V1
parent_theory: CONSTITUTIONAL_MANIFOLD_RENDERING_V0
proposer: HER
attestor: REDUCER (pending)
ledger_receipt: <pending>
```

Until then: ALGORITHM_DRAFT, NO_SHIP, APPEND_ONLY proposal.

---

## §15. The single line

> **Pseudocode is the bridge between doctrine and code.
> It specifies what the gate computes, not how to compute it.
> Implementation is downstream; this is the contract.**
