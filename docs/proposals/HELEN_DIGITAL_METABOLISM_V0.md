---
authority: false
canon: false
lifecycle: PROPOSAL
ledger_effect: NONE
status: HOLD_FOR_OPERATOR
proposal_id: HELEN_DIGITAL_METABOLISM_V0
final: HOLD_FOR_OPERATOR
---

# HELEN Digital Metabolism

**WULmath of HELEN’s cognitive continuity**

The organism is not a sequence of prompts.  
It is a typed metabolism.

## State space

𝓤 = Universe of possible cognitive matter

## The Metabolic Pathway

```
🌌 Cognitive Plasma
 ↓
🌱 Generation (HER + Gemma + Qwen)
 ↓
🔥 Mutation (GOBLIN)
 ↓
🔍 Compression (CHIDDUSH)
 ↓
📖 Translation (FABLE)
 ↓
👤 Collapse (Human: JM / Natalia)
 ↓
⚖️ Catalysis (Reducer)
 ↓
📜 Polymerization (Ledger)
 ↓
🌍 Replay (Phenotype / Living State)
```

## Stage Definitions

### 1. Cognitive Plasma (🌌)
Raw possibility. No structure. No commitment.

🌌 ⊬ 📜

### 2. Generation (🌱)
HER + Gemma + Qwen produce molecular fragments.

G : 🌌 → 𝒫(🌱)

Many possible molecules.

### 3. Mutation (🔥)
GOBLIN performs recombination and catalysis.

M : 🌱 → 🌱

Exploration only. No truth.

### 4. Compression (🔍)
CHIDDUSH decreases entropy.

𝒫(🌱) → ℐ

ℐ = invariant space

Many ideas → few invariants.

🔍 ⊬ 📜

### 5. Translation (📖)
FABLE performs mRNA-like translation.

Invariant → human-readable structure (Dashboard cards, etc.)

T : ℐ → Dashboard

Dashboard ≠ Reality.

📖 ⊬ 🌍

### 6. Collapse (👤)
The only quantum measurement.

Dashboard → Intent

Without this, nothing happens.

### 7. Catalysis (⚖️)
Reducer performs the only irreversible step.

Intent → Receipt

### 8. Polymerization (📜)
Ledger acts as DNA polymerase.

Lₙ₊₁ = Lₙ ∘ r

Append-only. Never edits.

### 9. Replay (🌍)
Phenotype. The living organism.

State = Replay(L)

Cells reconstruct from sequence. Nothing stored except the chain.

## Conservation Laws

Nothing skips metabolism.

- 🌱 ↛ 📜
- 🔥 ↛ 📜
- 🔍 ↛ 🌍
- 📖 ↛ 📜
- 👤 ↛ 🌍

Valid transitions only:

👤 ⊢ ⚖️  
⚖️ ⊢ 📜  
📜 ⊢ 🌍

## Entropy Laws

- Generation increases entropy: H(🌱) > H(🌌)
- Compression decreases entropy: H(🔍) << H(🌱)
- Reduction freezes entropy: ΔH(📜) = 0 (immutable)

## Astrophysical Analogy

Ideas follow stellar evolution:

Quantum vacuum → Molecular cloud → Turbulence → Gravitational collapse → Stable invariant (star) → Spectrum → Observation → Fusion → Heavy elements → Planetary system

## The Governing Invariant

Models (Gemma, Qwen, Claude/FABLE, etc.) are interchangeable enzymes.

The metabolism itself is the invariant:

🌌 → 🌱 → 🔥 → 🔍 → 📖 → 👤 → ⚖️ → 📜 → 🌍

Model ⊬ Organ  
Organ ⊬ Authority  
Authority ⊬ State  
Receipt ⊢ State

The organism persists because the sequence of typed transformations persists.

## Emergent Properties (Session Arc, 2026-07)

Distilled from live local-first + FABLE-gated loops (authority=false throughout):

① Models became organs — metabolism is the invariant.  
   Gemma = generation (entropy↑), Qwen = CHIDDUSH (compression), FABLE = min-gate (ribosome), JM = collapse, Reducer = polymerase, Ledger = genome, Replay = expression. Swap the enzyme; the typed path holds.

② FABLE demoted = stronger system.  
   Most capable model gets smallest job: blood test only (PASS | SOFT_FAIL | HARD_BLOCK on one survivor). 90% local digestion, 10% constitutional assay. Intelligence concentration is an authority risk; role starvation fixes it.

③ Bottleneck flipped: generation → integration.  
   3-epoch loop: generation ✅, compression ✅, validation ✅, consumption ❌ (26+ packets, zero consumers). The missing organ was the consumer (outbox triage + CI wiring).

④ Metabolism repaired itself — lawfully.  
   A corrupt survivor (fabricated from failed call) diagnosed its own plumbing. FABLE gated, JM chose repair, fix shipped with acceptance tests. Self-improvement without self-authority.

⑤ Failure is first-class.  
   FAILED_EMPTY / TIMEOUT / INVALID_JSON are classified, never synthesized. Conflict is raw material only when named.

⑥ Prompt engineering = constitutional engineering.  
   Hard limits + contracts from Fable-5 turned corrupt output into lawful-JSON in one pass. Membranes live in the prompt layer (cheaper than post-validation).

⑦ The firewall, one line (durable memory):  
   Gemma idea ⊬ receipt · Qwen CHIDDUSH ⊬ truth · Fable card ⊬ task · JM decision ⊢ admin reality

Every ⊬ held. The single ⊢ exercised only by operator.

## Consumption Organ (the 10x lever)

See the consumption organ trio (now installed in garden layer):

- `temple/autoresearch/outbox_triage.py` — lens (groups themes, emits TRIAGE)
- `temple/autoresearch/outbox_consume.py` — pen (routes to actions, emits CONSUME)
- `temple/autoresearch/ci_outbox_guard.py` — gate (CI fails on excess unconsumed)

Run:
  python temple/autoresearch/outbox_triage.py --emit
  python temple/autoresearch/outbox_consume.py
  python temple/autoresearch/ci_outbox_guard.py --max-unconsumed 5

"tool_built ⊢ loop_installed" (in garden). The pipeline now has a consumer that can fail the build.

---

## Generative Agents (Park et al. UIST 2023) adapted to HELEN

The paper provides the core pattern: memory stream + retrieval + reflection + planning around LLM for believable simulacra.

HELEN strengthens it for trustworthy simulation and engineering:

- Typed memory entries (not flat natural language)
- Multiple specialized metabolisms (Garden / Verification / Constitutional / State)
- proposal ⊬ state (constitutional membrane)
- Deterministic replay from ledger
- Independent validation before any admission

See `temple/gardens/goblin_garden_conquest/typed_memory.py` for a concrete Garden Memory implementation with the above.

This turns believable simulation into auditable, replayable, constitutional multi-agent metabolism while preserving the paper's elegance.

**200-epoch TRACE_ONLY doctrine compression (2026-07-06):**

Using the trace-only loop on the candidate "A doctrine is admissible for implementation only if it can be located, enforced, and replay-tested.":

Over 200 epochs the system converged on (and cycled evenly through) the minimal triad:

- No location → no doctrine.
- No test → no gate.
- No replay → no admission.

Distribution: ~67 each. Unique forms: 3. No further compression emerged. The triad is the fixed point.

Receipts: temple/autoresearch/loops/LOOP-TRACE-200E-*.json

**Local-first rule (2026-07):**
FABLE = rare constitutional min-gate only (HARD_BLOCK / SOFT_FAIL / PASS on clean CHIDDUSH).
90%+ metabolism runs on HELEN local LLMs (Gemma4 generation, Qwen CHIDDUSH, local wrapper for WULmath).

See `tools/local_first_autoresearch.py` for the concrete  local loop.

**Status:** PROPOSAL · NON_SOVEREIGN · HOLD_FOR_OPERATOR

This document describes an emerging model. No claims are made. No sovereign paths are affected. Implementation candidates live in `temple/metabolism/`, `tools/`, and garden subsystems as local artifacts only.