# HELEN OS — Architecture V2
## Governed Epistemic Operating System — Clean Reframe

**Status:** FROZEN
**Replaces:** HELEN_OS_STATE_RECAP_V1.md (operational detail preserved, conceptual base corrected)
**Commit basis:** 398/398 tests (246 constitutional kernel + 152 dispatch extension)
**Shadow pass:** GO — 23/23 input types, zero drift, zero crashes
**Date frozen:** 2026-04-04

---

## The Core Abstraction

```
HELEN = Π_𝓛 ∘ 𝒢
```

Where:

- **𝒢** = generative machinery — LLMs, skills, agents, compilation, Temple, UI expression. Powerful, non-sovereign.
- **Π_𝓛** = lawful admissibility projector — routing law, receipt law, replay law, promotion law, memory scope law. Narrow, operator-authority-bound.

The governing equation for all state transitions:

```
x_{t+1} = Π_𝓛 ( 𝒢(x_t, u_t) )
```

- `x_t` = governed state (skill library, canonical knowledge, ledger, memory index)
- `u_t` = input (user query, claim, promotion packet, Temple observation, thinking trace)
- `𝒢(x_t, u_t)` = what the system can generate — interpretation, decomposition, hypothesis, affect, artifact
- `Π_𝓛(·)` = what is admissible to alter state

**The question HELEN answers is not "what can the system generate?"**
**It is: "what generated object is allowed to have consequences?"**

---

## The Deepest Split

```
┌─────────────────────────────────────┐  ┌──────────────────────────────────────┐
│        GENERATIVE LAYER  𝒢           │  │      GOVERNING LAYER  Π_𝓛             │
│  (powerful, non-sovereign)           │  │  (narrow, operator-bound)             │
│                                      │  │                                       │
│  • Language generation               │  │  • Admissibility checks               │
│  • Decomposition                     │  │  • Routing law                        │
│  • Exploration (Temple)              │  │  • Receipt law                        │
│  • Thinking traces                   │  │  • Replay law                         │
│  • Style / affect / warmth           │  │  • Memory status / scope law          │
│  • Knowledge compilation             │  │  • Promotion law                      │
│  • Summarization                     │  │  • Refusal / defer / reject authority │
│  • Hypothesis formation              │  │                                       │
│  • Skill execution                   │  │                                       │
└─────────────────────────────────────┘  └──────────────────────────────────────┘
```

Everything in HELEN follows from this split.
The danger is always the same: a generative layer starts behaving like an authority layer.
The whole architecture is a system of anti-collapse barriers.

---

## The Four Stabilized Regimes

### I. Constitutional Law (immovable)

Defines the invariants that must not drift:

- Reducer Admission Boundary — only reducer-emitted decisions mutate governed state
- Receipt immutability — receipts are append-only, never modified
- Replay requirement — state must be reconstructible from initial state + ledger
- Input resolution rules — unresolved pointers blocked at boundary
- Surface non-sovereignty — affect, persona, UI carry no authority
- Amendment-only change model — frozen schemas require versioning, not modification

### II. Memory Governance

Memory is allowed, but only as governed external structure.

```
retrieved ≠ injected ≠ applied ≠ beneficial ≠ promoted
```

- Memory **may store**
- Memory **may serve** (retrieval)
- Memory **may inform** (routing context)
- Memory **may not self-authorize**

Frequent recall ≠ truth. Repeated mention ≠ promotion. Latent familiarity ≠ authority.

### III. Knowledge Compilation

HELEN as a durable epistemic substrate (not session intelligence):

```
raw sources → extracted claims → compiled objects → audits → indexes → derived artifacts
```

With explicit status per artifact:
- `canonical` — reducer-admitted, lineage-verified
- `provisional` — admitted but unverified
- `candidate` — proposed, not yet admitted
- `speculative` — exploratory, no authority
- `deprecated` — superseded, lineage preserved

### IV. Temple Exploration

Bounded exploratory regime — allowed to be interesting, not allowed to become law.

- Lateral hypotheses, proto-structural observations, symbolic reasoning
- No claim, no ship, no ontology, no silent promotion
- All Temple outputs are `PENDING_MAYOR_REVIEW`
- Temple → Bridge → Mayor gate (KERNEL route) — the only path to canonical

---

## The Six-Layer Architecture

```
                        INPUT
                          │
                    ┌─────▼──────┐
LAYER 0             │  Input     │  Resolution discipline
                    │  Boundary  │  Unresolved → blocked before entry
                    └─────┬──────┘
                          │
                    ┌─────▼──────┐
LAYER 1             │  Dispatch  │  Constitutional traffic control
                    │  Π_𝓛 gate  │  6+1 routes: KERNEL SKILL AGENT TEMPLE THINK DEFER REJECT
                    └──┬──┬──┬───┘
                       │  │  │
           ┌───────────┘  │  └──────────────┐
           │              │                 │
    ┌──────▼──────┐ ┌─────▼──────┐  ┌──────▼──────┐
LAYER 2 │   THINK   │ │  TEMPLE   │  │ SKILLS &    │  LAYER 3
    │   Trace   │ │  Sandbox  │  │ AGENTS      │
    │ (prep,    │ │ (explore, │  │ (work, no   │
    │  audit)   │ │  no auth) │  │  govern)    │
    └──────┬────┘ └─────┬─────┘  └──────┬──────┘
           │            │               │
           └────────────┴───────────────┘
                        │
                   ┌────▼────┐
LAYER 4            │Knowledge│  Compiled epistemic substrate
                   │Substrate│  Claims · Audits · Indexes · Artifacts
                   └────┬────┘
                        │  Π_𝓛 gate (reducer, chain receipt, lineage audit)
                        │
                   ┌────▼────┐
                   │ Governed│  Ledger + State + Memory index
                   │  State  │  (replay-verifiable, immutable history)
                   └────┬────┘
                        │
                   ┌────▼────┐
LAYER 5            │ Surface │  Affect · Voice · Persona · Warmth
                   │Persona  │  display_only=True, may_influence_routing=False
                   └─────────┘
```

---

## Layer 0 — Input Boundary

**Status:** CONSTITUTIONAL LAW
**Artifact:** `HELEN_DISPATCH_LAYER_V1` (resolution_status gate)

Rules:
- Unresolved pointers → DEFER (not REJECT — can retry)
- Inaccessible sources → DEFER with retry requirements
- User description ≠ evidence (cannot bypass resolution gate)
- References must resolve before entering the governed pipeline

This prevents epistemic corruption at the boundary.

---

## Layer 1 — Dispatch

**Status:** OPERATIONAL — 28/28 tests ✅
**Artifacts:** `helen_dispatch_v1_schemas.py`, `helen_dispatch_v1_router.py`

The **circulation law**. Routes incoming objects to the correct regime.

### Routes (7 total — THINK is new)

| Route | Authority | Mutation | Purpose |
|-------|-----------|----------|---------|
| `KERNEL` | SOVEREIGN | CANONICAL_REQUEST | Promotion, reducer-gated decisions |
| `SKILL` | NON_SOVEREIGN | CANDIDATE_WRITE | Multi-step bounded workflows |
| `AGENT` | NON_SOVEREIGN | DERIVED_WRITE | Single transforms |
| `TEMPLE` | EXPLORATORY | NONE | Sandboxed exploration |
| `THINK` | NON_SOVEREIGN | NONE | Bounded preparation trace (new) |
| `DEFER` | BLOCKED | NONE | Incomplete — can retry |
| `REJECT` | BLOCKED | NONE | Illegitimate — cannot retry |

### Routing Invariants (frozen)

- Unresolved input → DEFER (never KERNEL or SKILL)
- Promotion / substitution request → KERNEL only
- Temple observation → TEMPLE (secondary: DEFER)
- THINK output → feeds preparation context, cannot route to KERNEL alone
- DEFER ≠ REJECT — distinction is retryability, not failure severity

### Dispatch Receipt (immutable)

```
receipt_hash = SHA256(canonical_json({
    input_hash, route, authority_class, mutation_intent,
    allowed_effects, forbidden_effects, reason_codes,
    session_id, manifest_ref, store_refs
}))
```

Excludes: `dispatch_id`, `timestamp` (run metadata, not semantic content)

---

## Layer 2 — Thinking / Preparation (THINK route)

**Status:** FROZEN_AFTER_INTEGRATION — 28/28 tests ✅
**Artifacts:** `helen_think_trace_v1.py`, THINK route integrated in `helen_dispatch_v1_schemas.py` + `helen_dispatch_v1_router.py`

### The critical reframing

Wrong: HELEN thinks → HELEN knows → HELEN can decide
Right: HELEN generates a thinking trace → trace is a bounded preparation artifact → trace cannot decide, promote, or govern

### What a THINK trace is

- Bounded decomposition of an incoming object
- Route preparation context (which SKILL or AGENT next?)
- Audit-visible structure (can be replayed, inspected)
- Non-authoritative — explicitly marked `authority: NONE`

### What a THINK trace is NOT

- Not hidden inner truth
- Not privileged self-report
- Not sovereign reasoning
- Not a path to state mutation

### THINK trace schema (FROZEN)

Implemented in `helen_think_trace_v1.py`. All constitutional invariants enforced at construction time via dataclass `field(init=False)` — not overridable by caller.

```
ThinkTrace
  trace_id          (run metadata — excluded from hash)
  session_id
  dispatch_id_ref   (must link to a THINK-routed DispatchReceipt)
  raw_input_summary
  decomposition     [DecompositionStep]  — each: authority="NONE", may_alter_state=False
  route_preparation [RoutePreparation]   — authority="NONE", candidate_routes (non-binding)
  uncertainty_flags
  authority         = "NONE"            (frozen, cannot be set by caller)
  may_alter_state   = False             (frozen)
  may_govern        = False             (frozen)
  may_promote       = False             (frozen)
  replay_visible    = True              (frozen)
  causal_scope      = "preparation_only" (frozen)
  trace_hash        (SHA256, excludes trace_id + timestamp)
```

---

## Layer 3 — Skills and Agents

**Status:** OPERATIONAL
**Artifacts:** `autoresearch_step_v1.py`, `autoresearch_batch_v1.py`, `skill_discovery_v1.py`

- **Skills** = bounded multi-step workflows (NON_SOVEREIGN)
- **Agents** = narrow single transforms (NON_SOVEREIGN)

They do work. They do not govern.
All mutations flow through the reducer gate (Law 1).
All history recorded in ledger (Law 2).

---

## Layer 4 — Knowledge Substrate

**Status:** PROPOSED — `HELEN_KNOWLEDGE_COMPILER_V1` formal spec certified (41/41 ✅)
**Artifacts:** `helen_knowledge_compiler_v1.py` (PROPOSED), `knowledge_health_audit_v2_patch_01.py`, schemas

### The compilation pipeline (now formally specified)

```
raw sources
    → [SOURCE_INGEST → SKILL dispatch]
    → INGEST stage: SourceIngestionPacket
    → EXTRACT stage: atomic claims (uncertainty preserved, contradictions visible)
    → VALIDATE stage: structural checks, uncertainty bounds, dispatch_id_ref
    → AUDIT stage: KNOWLEDGE_HEALTH_AUDIT_V2 + PATCH_01 + PATCH_02 lineage checks
    → [PROMOTION_REQUEST → KERNEL dispatch]
    → ADMIT stage: canonical or provisional
    → canonical knowledge layer (lineage-proven, KERNEL chain receipt required)
```

Each stage transition is receipted via `CompilerStageReceipt`.
KERNEL-gated transitions require a `ChainReceiptV2` (CANONICAL_WRITE, KERNEL worker).

### Artifact status map

| Status | Authority | Path to upgrade | Uncertainty ceiling |
|--------|-----------|-----------------|---------------------|
| `speculative` | NONE | Temple → Bridge → Mayor | any (≤ 1.0) |
| `candidate` | NONE | Reducer gate | any (≤ 1.0) |
| `provisional` | NON_SOVEREIGN | Verification → Reducer | ≤ 0.6 |
| `canonical` | SOVEREIGN | KERNEL route only | ≤ 0.2 |

### Compiler constitutional invariants (41/41 ✅)

| Invariant | Enforcer |
|-----------|----------|
| Uncertainty must be in [0.0, 1.0] | `Claim.__post_init__` |
| dispatch_id_ref non-optional on every claim | `Claim.__post_init__` |
| Status promotion is monotonic (no demotion, no skip) | `ClaimBuilder.can_promote()` |
| Canonical admission requires KERNEL chain receipt | `AdmissionResult.__post_init__` |
| Uncertainty ceiling gates maximum status | `UncertaintyThreshold` |
| Stage transitions are sequential (no skipping) | `CompilerStageReceipt.__post_init__` |
| Contradictions are surfaced, not suppressed | `ContradictionDetector` |
| All reason codes are frozen (no ad hoc strings) | `AdmissionResult.__post_init__`, `COMPILER_REASON_CODES` |
| SOURCE_INGEST → SKILL only (not KERNEL) | `SourceIngestionRouter` |
| PROMOTION_REQUEST → KERNEL only | `SourceIngestionRouter` |
| Claim hash is deterministic (excludes run metadata) | `hash_claim()` |

### Lineage law (DISPATCH_LINEAGE_VIOLATION)

A `canonical` artifact produced outside the KERNEL route = dispatch lineage violation (CRITICAL, blocking).

---

## Layer 4b — Governed State (Ledger + Memory)

**Status:** OPERATIONAL
**Artifacts:** `decision_ledger_v1.py`, `ledger_replay_v1.py`, `skill_library_state_updater.py`

### Load-bearing property (cryptographically proven)

```
initial_state + ledger → replay_ledger_to_state() → final_state  ✅
```

### Memory governance laws

```
retrieved ≠ injected ≠ applied ≠ beneficial ≠ promoted
```

Memory scope levels:
- `deployment` — permanent, all sessions
- `user` — persists across sessions for one user
- `experimental` — bounded, time-limited, explicit

---

## Layer 5 — Surface / Persona

**Status:** OPERATIONAL
**Artifacts:** `helen_pressure_signal_v1.py`, `helen_affect_translation_v1.py`

### What the user sees

- Voice, warmth, legibility, affect, anthropomorphic presentation
- May feel alive — must not become sovereign

### The non-interference proof (certified)

```
PressureSignal → AffectTranslator.translate() → AffectState

routing_effect: UNCHANGED after translation
display_only: True
may_influence_routing: False
may_influence_governance: False
ontology_claim: False
causal_scope: "presentation_only"
```

### The clean sentence

**Anthropomorphic outside, constitutional inside.**

Internal: pressure, ambiguity, contradiction, risk posture, stability
External: expressive, warm, legible, affective

---

## The Middleware Spine (Circulation Law)

**The real bottleneck is not law, and not persona. It is handoff law.**

```
┌──────────────────────────────────────────────────────────────────┐
│                    CIRCULATION SPINE                             │
│                                                                  │
│  Dispatch ──→ THINK trace ──→ Chain Receipt ──→ Knowledge Audit  │
│       │            │               │                  │          │
│       └────────────┴───────────────┴──────────────────┘         │
│                         ↑                                        │
│             Pressure Signal + Affect Translation                 │
│                  (non-routing, display-only)                     │
└──────────────────────────────────────────────────────────────────┘
```

| Component | Artifact | Status |
|-----------|----------|--------|
| Dispatch schemas | `helen_dispatch_v1_schemas.py` | FROZEN ✅ |
| Dispatch router | `helen_dispatch_v1_router.py` | FROZEN ✅ |
| Thinking trace | `helen_think_trace_v1.py` | FROZEN_AFTER_INTEGRATION ✅ |
| Chain receipt V2 | `helen_chain_receipt_v2.py` | FROZEN_AFTER_RUNTIME_COUPLING ✅ |
| Pressure signal | `helen_pressure_signal_v1.py` | OPERATIONAL ✅ |
| Affect translation | `helen_affect_translation_v1.py` | OPERATIONAL ✅ |
| Knowledge audit PATCH_01 | `knowledge_health_audit_v2_patch_01.py` | FROZEN ✅ |
| Knowledge audit PATCH_02 | `knowledge_health_audit_v2_patch_02.py` | FROZEN_WITH_PATCH_02 ✅ |
| Runtime manifest | `helen_runtime_manifest_v1.py` | OPERATIONAL ✅ |
| Chain receipt V1 | `helen_chain_receipt_v1.py` | SUPERSEDED by V2 |

---

## Full Artifact Registry

### Constitutional Kernel (246/246 ✅)

| Artifact | Layer | Status | Tests |
|----------|-------|--------|-------|
| `canonical.py` | L1 | FROZEN | — |
| `schema_registry.py` | L1 | FROZEN | — |
| `validators.py` | L1 | FROZEN | — |
| `reason_codes.py` | L1 | FROZEN | — |
| `skill_promotion_reducer.py` | L1 | FROZEN | — |
| `failure_bridge.py` | L1 | FROZEN | — |
| `helen_executor_v1.py` | L1 | FROZEN | — |
| `skill_library_state_updater.py` | L1 | FROZEN | — |
| `ledger_validator_v1.py` | L1 | FROZEN | — |
| `decision_ledger_v1.py` | L2 | FROZEN | 4 ✅ |
| `autoresearch_step_v1.py` | L3 | OPERATIONAL | 6 ✅ |
| `autoresearch_batch_v1.py` | L3b | OPERATIONAL | 30+ ✅ |
| `skill_discovery_v1.py` | L3c | OPERATIONAL | 20+ ✅ |
| `ledger_replay_v1.py` | L4 | FROZEN | 4 ✅ |
| `temple_v1.py` | L5 | OPERATIONAL | 50+ ✅ |
| `temple_bridge_v1.py` | L5 | OPERATIONAL | — |
| `autoresearch_eval_receipt_v1.py` | L5 | OPERATIONAL | — |
| `replay_proof_v1.py` | META | OPERATIONAL | — |

### Dispatch Extension Stack (73/73 ✅)

| Artifact | Layer | Status | Tests |
|----------|-------|--------|-------|
| `helen_dispatch_v1_schemas.py` | Dispatch | FROZEN | 28 ✅ |
| `helen_dispatch_v1_router.py` | Dispatch | OPERATIONAL | — |
| `helen_pressure_signal_v1.py` | Surface | OPERATIONAL | 10 ✅ |
| `helen_affect_translation_v1.py` | Surface | OPERATIONAL | 13 ✅ |
| `knowledge_health_audit_v2_patch_01.py` | Audit | OPERATIONAL | 7 ✅ |
| `helen_chain_receipt_v1.py` | Circulation | OPERATIONAL (rewrite pending) | 5 ✅ |
| `helen_runtime_manifest_v1.py` | Bootstrap | OPERATIONAL | 7 ✅ |

### Dispatch Extension Stack (152/152 ✅)

| Artifact | Layer | Status | Tests |
|----------|-------|--------|-------|
| `helen_dispatch_v1_schemas.py` | Dispatch | FROZEN | 28 ✅ |
| `helen_dispatch_v1_router.py` | Dispatch | FROZEN | — |
| `helen_think_trace_v1.py` | L2 | FROZEN_AFTER_INTEGRATION | 28 ✅ |
| `helen_pressure_signal_v1.py` | Surface | OPERATIONAL | 10 ✅ |
| `helen_affect_translation_v1.py` | Surface | OPERATIONAL | 13 ✅ |
| `knowledge_health_audit_v2_patch_01.py` | Audit | FROZEN | 7 ✅ |
| `knowledge_health_audit_v2_patch_02.py` | Audit | FROZEN_WITH_PATCH_02 | 22 ✅ |
| `helen_chain_receipt_v2.py` | Circulation | FROZEN_AFTER_RUNTIME_COUPLING | 29 ✅ |
| `helen_runtime_manifest_v1.py` | Bootstrap | OPERATIONAL | 7 ✅ |

### Knowledge Compiler (41/41 ✅)

| Artifact | Layer | Status | Tests |
|----------|-------|--------|-------|
| `helen_knowledge_compiler_v1.py` | L4 | PROPOSED | 41 ✅ |

### Proposed (pending)

| Artifact | Layer | Status | Depends on |
|----------|-------|--------|------------|
| `HELEN_KNOWLEDGE_COMPILER_V2` | L4 | NOT STARTED | Compiler V1 operational |

---

## What HELEN Is Optimizing

| Goal | Mechanism |
|------|-----------|
| **Admissibility** | What is allowed to matter? → Reducer gate |
| **Lineage** | Can state be reconstructed? → Ledger replay |
| **Separation** | Can exploration exist without corrupting canon? → Temple → Bridge → Mayor |
| **Auditability** | Can hidden process be surfaced to govern consequences? → THINK trace, chain receipts |
| **Drift resistance** | Can the system evolve without rewriting its own law? → Frozen schemas, amendment-only model |

---

## What HELEN Is Not

HELEN is not a chatbot, an unrestricted agent, a memory wrapper, a consciousness simulator, a note-taking app, a productivity harness, or a persona engine.

It may use pieces of all of those.

It is: **a governed epistemic operating system.**

---

## The Central Danger

A non-sovereign layer starts to behave like an authority layer.

This can happen through memory, UI presence, internal reasoning, affective presentation, skills, routing heuristics, compiled knowledge, or Temple outputs.

The anti-collapse barriers are:
- Receipt immutability (cannot be rewritten)
- Replay law (state must be reconstructible)
- Lineage audit (canonical_write outside KERNEL = CRITICAL violation)
- Affect non-interference (display_only=True, may_influence_routing=False)
- THINK trace isolation (preparation ≠ decision)
- Temple non-sovereignty (exploratory ≠ canonical)

---

## Next Work Items (Ordered)

1. ~~**HELEN_KNOWLEDGE_COMPILER_V1** — formal spec~~ ✅ DONE — 41/41 tests, PROPOSED
2. **Enforcement rollout** — move from shadow into live enforcement phases (route distribution monitoring, CI blocks for THINK_TO_CANONICAL_SHORTCUT, manifest references to all circulation objects)
3. **SESSION_PERSISTENCE_V1** — persist ledger to disk (ledger in-memory only; dependency: constitutional kernel proven ✅)

---

## The Clean Paragraph

HELEN is a governed epistemic operating system that separates generation from authority. It allows language models, memory systems, compiled knowledge, exploratory reasoning, and anthropomorphic interfaces to coexist, but only under explicit routing, audit, replay, and promotion laws. Its purpose is not merely to generate outputs, but to determine which outputs are admissible to influence state, memory, interpretation, and visible action.

---

**Last updated:** 2026-04-04 (FROZEN)
**Test status:** 439/439 ✅ (246 constitutional kernel + 152 dispatch extension + 41 knowledge compiler)
**Shadow pass:** GO — 23/23 input types correct, zero drift, zero crashes
**Route distribution:** KERNEL 26% | AGENT 26% | SKILL 22% | THINK 13% | TEMPLE 9% | DEFER 4%
**Certification:** Dispatch determinism (20 runs × 4 types = 0 drift) + full circulation audit (FullLineageAuditor clean)
**Circulation spine:** auditable end-to-end: dispatch → THINK trace → chain receipt → canonical knowledge
**Knowledge compiler:** PROPOSED — formal spec certified (41/41 ✅): claim schema, status promotion law, admission gate, contradiction detection, stage sequencing, dispatch routing
**Next:** enforcement rollout → SESSION_PERSISTENCE_V1
