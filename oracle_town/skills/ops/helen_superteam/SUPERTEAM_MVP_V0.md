# HELEN SUPERTEAM EGREGOR — MVP V0

**Status**: NON_SOVEREIGN · NO_SHIP · PROPOSAL  
**Authority**: false · Canon: false · Ledger effect: none  
**Path**: `oracle_town/skills/ops/helen_superteam/`  
**Schemas**: `schemas/helen_superteam/`

---

## One-line doctrine

> Goblins may dream. HER may distill. HAL may frame. MAYOR may validate. JM/reducer may admit. Kernel only moves by receipt and replay.

---

## The Hard Boundaries

```
DreamSeed           ≠  InsightCandidate
InsightCandidate    ≠  ClaimCandidate
ClaimCandidate      ≠  ValidatedClaim
ValidatedClaim      ≠  KernelTruth
ReceiptCandidate    ≠  LedgerReceipt
```

Each step produces a distinct artifact type. Promotion between types requires a distinct actor.

---

## Pipeline

```
RAW INPUT (pdf, tweet, article, noise, failure, fragment, dream, any signal)
    │
    ▼  [GOBLIN stage]
DreamSeed           — compost/         claim_status: NO_CLAIM
    │
    ▼  [HER stage — blind to GOBLIN deliberation, sees DreamSeed artifact only]
InsightCandidate    — insights/         claim_status: CANDIDATE
    │
    ▼  [HAL stage — blind to HER deliberation, sees InsightCandidate artifact only]
ClaimCandidate      — claims/           claim_status: CLAIM_CANDIDATE
    │
    ▼  [MAYOR stage — blind to all prior deliberation, sees ClaimCandidate artifact only]
ValidationReceiptCandidate — validation/  claim_status: VALIDATED_CLAIM_CANDIDATE
    │
    ▼  [JM + HELEN OS — admission review, human in loop]
AdmissionProposal   — admission/        (future: ADMISSION_PROPOSAL_V0 schema)
    │
    ▼  [Reducer → Ledger — existing sovereign pipeline]
LedgerReceipt                           claim_status: ADMITTED
```

---

## Role Stack

### 1. GOBLIN — Free lateral spirits

**Can ingest**: pdf, tweet, article, noise, failure, fragment, dream, JSON, ndjson — anything.  
**Output**: DreamSeed  
**Rule**: GOBLINs may dream everything, but prove nothing.  
**Blindness**: none — GOBLINs see raw input directly.

### 2. HER — Deep sensemaker

**Can ingest**: DreamSeed artifacts only. Never raw input. Never GOBLIN deliberation notes.  
**Output**: InsightCandidate  
**Rule**: HER may distill meaning, but resonance is not evidence.  
**Chiddush criterion**: Does this seed contain something genuinely new, something that wasn't obvious in the input?  
**Blindness**: HER sees the DreamSeed artifact. Not the raw input. Not GOBLIN's process.

### 3. HAL — Serious administrator

**Can ingest**: InsightCandidate artifacts only. Never DreamSeeds. Never GOBLIN/HER process.  
**Output**: ClaimCandidate  
**Rule**: HAL may frame a claim, but cannot validate truth.  
**HAL requires**: claim sentence · source refs · evidence needed · risk if wrong · test/review path  
**Blindness**: HAL sees the InsightCandidate artifact. Not the seeds. Not HER's process.

### 4. MAYOR — Independent civic reviewer

**Can ingest**: ClaimCandidate artifact only. Never insights, seeds, or process notes.  
**Output**: ValidationReceiptCandidate (YES / NO / HOLD)  
**Rule**: MAYOR may validate the candidate packet, but cannot admit into kernel truth.  
**Blindness**: MAYOR sees the ClaimCandidate. Nothing upstream. This is the blindness protocol's hardest constraint.

### 5. HELEN OS + JM — Final admission review

**Can ingest**: ValidationReceiptCandidate where mayor_verdict = YES  
**Output**: AdmissionProposal (future schema) → existing sovereign promotion pipeline  
**Rule**: Validated claim ≠ kernel truth. JM chooses. Reducer admits. Kernel moves only through receipt and replay.

---

## Daily MVP Cadence

```
GOBLIN   — ingest up to 10 raw inputs → produce up to 20 DreamSeeds
HER      — read all seeds → keep up to 5 InsightCandidates
HAL      — read all insights → keep up to 2 ClaimCandidates
MAYOR    — read all claims → validate at most 1
JM       — review at most 1 ValidationReceiptCandidate (YES only) for admission path
```

**Why these limits**: compost must not become a swamp. Each gate is a filter, not a funnel.

---

## Blindness Protocol

The egregor works because each agent is blind to the previous agent's deliberation — it sees only the output artifact. This is not a courtesy; it is architectural:

- GOBLIN's chaos is metabolized into a DreamSeed. HER never sees the chaos.
- HER's intuition is crystallized into an InsightCandidate. HAL never sees the intuition.
- HAL's framing is formalized into a ClaimCandidate. MAYOR never sees the framing.
- The egregor forms because each agent brings full character to a narrow, typed input.

When implementing: the pipeline MUST NOT pass GOBLIN reasoning to HER. MUST NOT pass HER process to HAL. MUST NOT pass anything except the ClaimCandidate artifact to MAYOR.

---

## Storage Layout

```
oracle_town/skills/ops/helen_superteam/
├── SUPERTEAM_MVP_V0.md          ← this file (doctrine)
├── superteam_pipeline.py         ← MVP pipeline runner
├── compost/                      ← DreamSeed artifacts (GOBLIN output)
│   └── SEED-<hash8>.json
├── insights/                     ← InsightCandidate artifacts (HER output)
│   └── INS-<hash8>.json
├── claims/                       ← ClaimCandidate artifacts (HAL output)
│   └── CLM-<hash8>.json
├── validation/                   ← ValidationReceiptCandidate artifacts (MAYOR output)
│   └── VAL-<hash8>.json
└── admission/                    ← AdmissionProposal staging (JM review queue)
    └── (future)
```

---

## What this is NOT

- This is not a sovereign autoresearch loop. It produces no ledger entries.
- MAYOR validation is not admission. A YES verdict is a green light for JM to review, not a kernel write.
- The pipeline runner is not an LLM orchestrator. It manages artifact handoff and enforces cadence limits. LLM calls happen separately (via `helen talk`, scaffold, or external tooling).
- DreamSeeds are not receipts. They are compost. Compost is not evidence.

---

## Relationship to Existing Pipelines

This is a **parallel epistemic track**, not a replacement for the execution pipeline:

| Pipeline | Purpose | Output |
|---|---|---|
| RALPH / DAN | Build things (code, artifacts) | git commits, receipts |
| AUTORESEARCH | Evaluate existing code/state | AUTORESEARCH_PACKET_V1 |
| **SUPERTEAM MVP** | Generate knowledge from any input | CLAIM_CANDIDATE → ADMISSION_PROPOSAL |

The three can coexist. SUPERTEAM produces ClaimCandidates that may inform future RALPH stories or AUTORESEARCH hypotheses, but the pipelines do not share state directly.
