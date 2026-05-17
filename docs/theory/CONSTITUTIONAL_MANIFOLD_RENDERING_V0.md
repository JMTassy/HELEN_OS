# Constitutional Manifold Rendering (CMR)
**Version:** V0
**Status:** Draft — Research Artifact
**Authority:** False
**Claim:** NO_CLAIM

---

## Core Claim

We extend observable manifold dynamics into **governed generative identity** by introducing bidirectional rendering (Math ↔ Face), identity gates, media receipts, and Reducer admission. The goal is not higher visual fidelity, but **persistent, provable, and constitutionally controlled generative identity**.

> **Operating Slogan**
> Not better pixels.
> Better persistence, proof, and control.

**Final Compression**
\[
\text{GMN} + \text{Math} \leftrightarrow \text{Face} + \text{Receipts} \;\longrightarrow\;
\text{Constitutional Manifold Rendering}
\]

---

## 1. Motivation: Black-Box Latent Identity Drift

Current generative systems treat identity as an emergent side-effect of latent space navigation. This creates several structural problems:

- Identity is **non-persistent** across sessions or model versions.
- There is no reliable mechanism to prove *what* identity was rendered or *why*.
- Latent drift is invisible until it becomes semantically or visually obvious.
- There is no constitutional boundary between exploration and committed identity.

HELEN's existing architecture (Goblin → Chiddush → Reducer) already provides governance for *actions* and *insights*. CMR extends this governance to **generative identity itself**.

---

## 2. Observable Manifold Identity

We treat generative identity as a point on an **observable manifold** rather than a hidden latent vector.

- The manifold is **observable** because both its mathematical coordinates and its rendered face can be inspected, receipted, and replayed.
- Identity is no longer a black-box embedding but a **governed trajectory** on this manifold.

This shifts the problem from "generate a convincing face" to "maintain a coherent, provable identity trajectory under constitutional constraints."

---

## 3. Face → Math Encoder

The encoder maps a rendered face (or media) back into the mathematical manifold:

- Input: Image / video frame / 3D render
- Output: Structured mathematical representation (GMN coordinates, manifold position, identity embedding)
- Properties: Deterministic, replayable, and linked to a media receipt

This closes the loop from visual output back to the governed mathematical substrate.

---

## 4. Math → Face Renderer

The renderer performs the inverse operation:

- Input: Mathematical coordinates on the manifold + identity parameters
- Output: Rendered face / media
- Constraints: Must be reproducible given the same mathematical input and rendering parameters

Together, the encoder and renderer form a **bidirectional rendering pair** that can be audited and receipted.

---

## 5. Visual Manifold Interaction Graph

We model interactions on the manifold as a graph:

- Nodes: Identity states (mathematical positions + rendered faces)
- Edges: Transformations, interpolations, or governed transitions
- Properties: Each edge can carry receipts, confidence scores, and reducer decisions

This graph makes identity trajectories explicit and queryable.

---

## 6. Temporal Identity Trajectory

Identity is not a static point but a **trajectory** over time:

- Each rendering step produces a new point on the manifold.
- The sequence of points forms a temporal identity path.
- This path can be replayed, audited, and governed.

The trajectory itself becomes a first-class governed artifact.

---

## 7. Identity Gate

Before any rendered identity can be admitted to sovereign state or
released externally, it must traverse a four-stage gate. The stages
run in fixed order and **fail closed at the first violation**.

### 7.1 Gate ordering

```
   render
     │
     ▼
  G1  provenance verification     ┐
     │                             │
     ▼                             │
  G2  receipt completeness         │  fail-fast:
     │                             │  any violation
     ▼                             │  → BLOCK with reason code
  G3  cycle consistency           │
     │                             │
     ▼                             │
  G4  risk + coherence scoring    ┘
     │
     ▼
   verdict ∈ { ADMIT, BLOCK, QUARANTINE }
```

### 7.2 Stage criteria

| ID  | Stage                   | Pass condition                                                  | On fail                                                |
| --- | ----------------------- | --------------------------------------------------------------- | ------------------------------------------------------ |
| G1  | Provenance verification | `render.source_hash ∈ canonical_sources` AND model is signed    | `BLOCK · UNKNOWN_PROVENANCE`                           |
| G2  | Receipt completeness    | media_receipt has all fields (§9) AND `receipt.hash` verifies   | `BLOCK · INCOMPLETE_RECEIPT`                           |
| G3  | Cycle consistency       | `d_cycle ≤ ε_admit` (§8)                                        | `BLOCK · CYCLE_VIOLATION` or `QUARANTINE` if in drift  |
| G4  | Risk + coherence        | `risk ≤ τ_risk` AND `coherence ≥ τ_coh`                         | `BLOCK · POLICY_VIOLATION`                             |

Stages are independent — G3 does not look at G4's signal and vice versa.
Each stage produces its own typed sub-receipt.

### 7.3 Authority

The Identity Gate is **non-sovereign**. It does not write to the
sovereign ledger. It produces a typed verdict (ADMIT / BLOCK / QUARANTINE)
which the MAYOR may sign in a subsequent reducer admission step (§10).

### 7.4 Gate receipt

Every gate run emits a receipt regardless of verdict:

```json
{
  "gate": "IDENTITY_GATE_V0",
  "render_hash": "<sha256-of-rendered-output>",
  "stages": {
    "G1": { "pass": true,  "details": "source: docs/identity/helen_v2.json" },
    "G2": { "pass": true,  "details": "all 6 fields present" },
    "G3": { "pass": false, "d_cycle": 0.083, "tier_breakdown": {"T1": 0.04, "T2": 0.11, "T3": 0.02} },
    "G4": { "skipped": true, "reason": "G3_FAILED" }
  },
  "verdict": "QUARANTINE",
  "first_violation": "G3",
  "timestamp": "<utc-iso>",
  "kernel_hash": "<git-head>"
}
```

The receipt is hash-chained into a sub-ledger reserved for identity-gate
decisions. Even BLOCK verdicts leave receipts — the absence of a receipt
is itself a constitutional violation.

### 7.5 QUARANTINE semantics

QUARANTINE is a soft state. The render is preserved with its receipt
but is **not** admitted to sovereign state and **not** deleted. It can
be revisited (re-run with adjusted tolerances, escalated to MAYOR for
manual review, or used as a drift training sample). QUARANTINE exists
because identity drift is often the signal of interest — destroying
the evidence would destroy the diagnostic value.

---

## 8. Cycle Consistency

The cycle:

\[
\text{Math}_0 \xrightarrow{R} \text{Face} \xrightarrow{E} \text{Math}_1
\]

where R is the Math→Face renderer (§4) and E is the Face→Math encoder
(§3). We require `Math₀ ≈ Math₁` under a typed distance.

### 8.1 The distance metric

Cycle distance is tiered. Each tier measures a different aspect of
identity preservation:

| Tier | Quantity                              | Distance `d`                              | What it measures        |
| ---- | ------------------------------------- | ----------------------------------------- | ----------------------- |
| T1   | Manifold coordinate vector            | `‖Math₀ − Math₁‖₂ / ‖Math₀‖₂`             | structural identity     |
| T2   | Identity embedding (face vector)      | `1 − cos(emb₀, emb₁)`                     | semantic identity       |
| T3   | Trajectory continuity (over N steps)  | `Σᵢ d(Mathᵢ, M̂ᵢ) / N`                   | temporal identity       |

Total cycle distance:

\[
d_{\text{cycle}} \;=\; w_1 \cdot d_{T1} \;+\; w_2 \cdot d_{T2} \;+\; w_3 \cdot d_{T3}
\]

Default weights `(w₁, w₂, w₃) = (0.3, 0.5, 0.2)`. The weights live in
the policy ledger — changing them is itself a reducer-admitted event
with a receipt.

### 8.2 Tolerance bands

Four bands govern how the gate treats a given `d_cycle`:

| Band       | Range                       | Gate action                       |
| ---------- | --------------------------- | --------------------------------- |
| STRICT     | `d ≤ ε_strict = 0.02`       | ADMIT silently                    |
| ADMIT      | `ε_strict < d ≤ ε_admit = 0.05` | ADMIT with deviation note       |
| DRIFT      | `ε_admit < d ≤ ε_drift = 0.15`  | QUARANTINE (preserved, unsigned)|
| VIOLATION  | `d > ε_drift`               | BLOCK · `CYCLE_VIOLATION`         |

`ε_strict`, `ε_admit`, `ε_drift` are **policy values**. They live in
the policy ledger and must be admitted by REDUCER before they take
effect. Tightening them is reversible; loosening them requires explicit
justification and an expiry.

### 8.3 Justified deviations

A deviation in the DRIFT band may be **explicitly receipted and
justified** rather than auto-quarantined. The justification receipt
must specify:

- **source** — what caused the deviation (model drift, intentional
  re-style, version bump, sensor noise, etc.)
- **operator** — the identity authorizing the deviation
- **scope** — single render? this trajectory? this model version?
  (narrower scope is preferred)
- **expiry** — UTC after which the deviation must be re-evaluated

A justified deviation produces a `JUSTIFIED_DEVIATION_V0` receipt
which the MAYOR may sign for ADMIT-with-justification. The original
gate-receipt's QUARANTINE verdict is preserved; the justification does
not overwrite it, it composes with it.

### 8.4 Drift detection over trajectory

For a trajectory of N steps, cumulative drift is:

\[
D_N \;=\; \sum_{i=1}^{N} d_{\text{cycle}}(i)
\]

A trajectory is **drifting** when:

\[
\frac{dD_N}{dN} \;>\; \delta_{\text{drift}}
\]

i.e. the per-step cycle distance is trending upward over a sliding
window. This is the signal that the model is losing the identity even
when each individual step passes the gate.

Drift detection runs as a batch process across recent trajectories
and emits a `TRAJECTORY_DRIFT_ALERT_V0` receipt when the slope
threshold is crossed. The alert does not block any single render; it
flags the trajectory as a whole for MAYOR review.

### 8.5 What "≈" means in practice

"≈" is not a single number. It is:

- a **typed** comparison under three tiers (structural / semantic / temporal),
- gated by **four tolerance bands** (STRICT / ADMIT / DRIFT / VIOLATION),
- scored by a **weighted distance** with policy-admitted weights,
- evaluated both **per-step** and **trajectory-wise**,
- and producing **receipts whether it passes or fails**.

The constitutional value of cycle consistency is not that it always
passes. It is that every passage and every failure is recorded with
the same rigor as a verdict.

---

## 9. Media Receipt

Every rendered output must be accompanied by a **Media Receipt** containing:

- Source mathematical coordinates
- Rendering parameters and model version
- Encoder output (reconstructed math)
- Cycle consistency metrics
- Timestamp and provenance hash
- Linked governance decisions (if any)

This receipt makes the generative act auditable and replayable.

---

## 10. Reducer Admission

Rendered identities do not become part of sovereign state by default. They must pass through the **Reducer Gate**:

- Only identities with complete media receipts are considered.
- The Reducer evaluates coherence, risk, and policy compliance.
- Admission results in a governed identity record in the Ledger.

This maintains the invariant: **generative output ≠ admitted reality**.

---

## 11. Limits and Non-Claims

- CMR does **not** claim to solve identity in latent space.
- It does **not** assert that rendered faces are "true" identities.
- It provides a **governed interface** between mathematical manifolds and visual media.
- All claims remain within the scope of HELEN's constitutional model (receipts, reducer, replay).

---

## 12. HELEN Benchmark Plan

Proposed evaluation axes:

- **Cycle Consistency Score**: How reliably does Math → Face → Math recover the original coordinates?
- **Receipt Completeness**: Percentage of renders that produce valid, linked media receipts.
- **Trajectory Coherence**: Stability and replayability of identity trajectories over multiple steps.
- **Reducer Admission Rate**: How many rendered identities successfully pass governance gates.
- **Drift Detection**: Ability to surface identity drift before it becomes semantically obvious.

---

## Summary

Constitutional Manifold Rendering extends HELEN's governance model into the domain of generative identity. By making the Math ↔ Face relationship bidirectional, receipted, and reducer-gated, we move from uncontrolled latent generation toward **persistent, provable, and constitutionally controlled identity**.

> Not better pixels.
> Better persistence, proof, and control.
