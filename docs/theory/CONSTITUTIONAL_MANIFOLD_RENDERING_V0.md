# CONSTITUTIONAL_MANIFOLD_RENDERING_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** THEORY_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal only

---

## Core Claim

We extend observable manifold dynamics into **governed generative identity** by adding bidirectional rendering, identity gates, receipts, and reducer admission.

This document serves as the parent theory for `HELEN_IDENTITY_GATE_V1` and `IDENTITY_GATE_PSEUDOCODE_V0`.

---

## 1. Motivation: black-box latent identity drift

Current generative systems treat identity as an emergent property of latent space navigation. This creates structural problems:

- Identity is non-persistent across renders, models, and sessions.
- There is no reliable way to verify that a generated face or video still represents the intended identity.
- Latent drift occurs silently until it becomes visually or semantically obvious.
- Generated media has no constitutional relationship to its source or its own history.

The result is **beautiful but ungoverned** output. HELEN requires identity to be observable, constrained, and governed.

---

## 2. Observable manifold identity

Instead of treating identity as a hidden latent vector, we model it as a point on an **observable manifold**.

An identity state is defined as a structured position that can be:
- Encoded from visual input
- Evolved through dynamics
- Rendered back into visual form
- Verified through gates and receipts

This makes identity inspectable rather than purely emergent.

---

## 3. Face → Math encoder

The encoder transforms visual input (face, frame, or render) into a structured mathematical representation on the manifold (`Φ`).

It produces a measurable state that can be compared, evolved, and audited.
**Note:** In early phases this may be a stub or non-sovereign signal source (see `IDENTITY_GATE_PSEUDOCODE_V0` §4–5).

---

## 4. Math → Face renderer

The renderer performs the inverse operation: it projects a mathematical manifold state back into visual form (`R`).

The renderer is treated as **neutral**. It generates candidates but does not confer truth or authority.

---

## 5. Visual manifold interaction graph

Multiple manifolds interact (identity, emotion, pose, style, lighting, camera, etc.).

These interactions are modeled as a graph `A`. Edges represent dependencies and constraints between different aspects of identity.

This structure allows coherent evolution across multiple visual dimensions.

---

## 6. Temporal identity trajectory

Identity is not static. It evolves over time as a trajectory on the manifold (`Γ`).

Each render or transformation produces a new point `M_{t+1}`. The sequence of points forms a temporal identity path that can be tracked, constrained, and replayed.

---

## 7. Identity gate

Before any rendered output can be considered governed, it must pass through an **Identity Gate** (detailed in `HELEN_IDENTITY_GATE_V1` and implemented via the algorithm in `IDENTITY_GATE_PSEUDOCODE_V0`).

The gate evaluates:
- Distance from canonical identity anchor
- Cycle consistency
- Presence of required provenance and receipts

Only outputs that pass the gate proceed to reducer consideration.
Even `BLOCK` verdicts must emit a receipt.

---

## 8. Cycle consistency

A core requirement is bidirectional consistency:

```
F_t → Φ → M_t → Γ → M_{t+1} → R → F_{t+1}
```

The system checks whether re-encoding a rendered output recovers a state close to the original mathematical input (within defined ε thresholds). Significant deviation indicates loss of identity coherence.

---

## 9. Media receipt

Every candidate render must be accompanied by a **Media Receipt** (`MEDIA_RECEIPT_V1`) containing at minimum:
- Source reference and hashes
- Director / composition parameters
- Render metadata
- Identity Gate result (including per-stage verdicts and `skipped` markers)
- Timestamp and provenance

A render without a complete media receipt remains ungoverned.

---

## 10. Reducer admission

Even after passing the Identity Gate and possessing a media receipt, an output is **not** yet part of trusted state.

Only the **Reducer** can admit a render into the governed record. The Reducer evaluates the full set of obligations, receipts, and policy compliance.

**Hard law:**
Only reducer admission mutates trusted state.

---

## 11. Limits and non-claims

This document is a theory draft. It does not claim:

- That mathematical coordinates directly equal facial identity
- That current renderers preserve identity without additional gates
- That receipt existence equals admissibility
- That this framework is currently implemented

It proposes a direction for governing generative identity through observable manifolds, bidirectional rendering, and constitutional gates. Implementation details (language, scorer choice, storage, concurrency) are explicitly out of scope (see `IDENTITY_GATE_PSEUDOCODE_V0` §11).

---

## 12. HELEN benchmark plan

Future evaluation should measure:

- Identity drift across multiple renders, angles, emotions, and renderers
- Cycle consistency error (Math → Face → Math)
- Receipt completeness rate (including explicit `skipped` stages)
- Gate pass/fail behavior under controlled variation (monotone verdict composition)
- Reducer admission decisions based on identity coherence
- Phase 2 Manual Gate effectiveness as a bridge to full automation

The goal is measurable persistence and governance of identity rather than visual quality alone.

---

## Key Equations

**Core flow:**
```
F_t → Φ → M_t → Γ → M_{t+1} → R → F_{t+1} → Gates → Receipt → Reducer
```

**Admission condition:**
```
A_{t+1} = 1  iff  Receipt(F_{t+1})
                AND IdentityGate(F_{t+1})
                AND CycleConsistency(F_{t+1})
                AND ReducerPass(F_{t+1})
```

---

## Hard Laws

- **Latent(x) does not imply Truth(x).**
- **Embedding(x) does not imply Identity(x).**
- **Renderer(x) does not imply Admission(x).**
- Receipt does not imply admissibility.
- Only reducer admission mutates trusted state.
- Always emit a receipt — even on `BLOCK`.

---

## Positioning

**Not better pixels.**
**Better persistence, proof, and control.**

---

*This document is a theory proposal only. It carries no implementation authority. It is the parent theory referenced by `HELEN_IDENTITY_GATE_V1` and `IDENTITY_GATE_PSEUDOCODE_V0`.*
