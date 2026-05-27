---
status: RAW
authority: NON_SOVEREIGN
claim: NO_CLAIM
canon: NO_SHIP
lifecycle: RAW
date: 2026-05-27
authored_by: operator (JM Tassy)
captured_by: claude (operational session 2026-05-27)
---

# HELEN PERSONAS — RECAP

Operator-authored synthesis of HELEN's persona stack, as it stands on
2026-05-27. Each persona below maps to one or more on-disk artifacts
(registered agent, kernel module, skill, or doctrine). This document
catalogs the personas; it does not invent them.

## Persona table

```text
OPERATOR / JEAN-MARIE
└─ sovereign human chooser
   decides what runs, ships, pushes, sends
```

```text
HER
└─ creative proposer
   dreams, drafts, connects, generates possibilities
   authority=false
```

```text
HAL
└─ witness / reviewer
   checks, blocks, asks for receipts, validates constraints
   authority=false
```

```text
MAYOR / REDUCER
└─ admission gate
   only entity allowed to transform candidate → admitted state
   authority=true only through explicit reducer protocol
```

```text
GOBLIN
└─ compost / mutation engine
   turns weird scraps into mechanisms, prototypes, tests
   never claims truth
```

```text
CHIDDUSH
└─ latent-structure recovery
   finds motifs, duplicates, boundary patterns, near-survivors
   observes structure; does not decide
```

```text
CLAW
└─ external action surface
   Telegram, web, notify, video, TTS, etc.
   always approval-gated
```

```text
WITNESS
└─ receipt producer
   turns events into traceable artifacts
```

```text
LEDGER
└─ append-only memory
   stores admitted reality
```

```text
REPLAY
└─ truth reconstruction
   reality = replay(ledger)
```

## Tree map

```text
HELEN OS
├─ HUMAN SOVEREIGN
│  └─ Operator / JM
│
├─ COGNITION LAYER
│  ├─ HER
│  │  └─ proposes / dreams / drafts
│  ├─ GOBLIN
│  │  └─ mutates scraps into candidates
│  └─ CHIDDUSH
│     └─ extracts latent structure
│
├─ REVIEW LAYER
│  ├─ HAL
│  │  └─ validates / blocks / reviews
│  └─ WITNESS
│     └─ creates receipts
│
├─ ACTION LAYER
│  └─ CLAW
│     ├─ Telegram
│     ├─ TTS
│     ├─ video render
│     ├─ web fetch
│     └─ notifications
│
├─ GOVERNANCE LAYER
│  ├─ MAYOR
│  │  └─ packet readiness / procedural gate
│  └─ REDUCER
│     └─ admission authority
│
├─ MEMORY LAYER
│  ├─ MEMORY DEDUP
│  ├─ PROVENANCE TRACE
│  └─ LEDGER
│
└─ TRUTH LAYER
   └─ REPLAY
      └─ reconstructs admitted reality
```

## Core Law (the 10-step sentence chain)

```text
HER proposes.
GOBLIN mutates.
CHIDDUSH detects.
HAL reviews.
WITNESS receipts.
MAYOR packetizes.
REDUCER admits.
LEDGER remembers.
REPLAY proves.
OPERATOR decides.
```

This is the expanded form of `F = E ∘ G ∘ C` decomposed across the
persona stack. The kernel's three-stage compression
(cognition → governance → execution) maps to ten distinct roles when
the full pipeline is unfolded.

## On-disk mapping (verification, 2026-05-27)

| Persona | Where it lives in code |
|---|---|
| OPERATOR | (sovereign human, not code) |
| HER | `helensh/agents/her_coder.py` (registered agent) |
| HAL | `helensh/agents/hal_reviewer.py` (registered agent) |
| CLAW | `helensh/agents/claw.py` (registered agent) |
| WITNESS | `helensh/witness.py` (kernel module) |
| LEDGER | `helensh/ledger.py` + `helensh/.state/live_ledger.jsonl` |
| REPLAY | `helensh/replay.py` (kernel module) |
| MAYOR | `docs/proposals/MAYOR_ADMISSION_PROTOCOL_V0.md` (deferred under §13.3) |
| REDUCER | `helensh/kernel.py::apply_receipt` + RECEIPT_SAFE_MUTATION_PROTOCOL |
| GOBLIN | `plugins/helen-governance/skills/goblin-role/SKILL.md` (registered skill) |
| CHIDDUSH | `helensh/chiddush/` (Python subsystem: motif extraction, receipt graph partitioning, motif replay) |

## What this document does NOT do

- Does not admit any persona to sovereign authority. Authority is still
  `False` on every receipt; only REDUCER can transition state.
- Does not introduce new code or new sub-agents. Every persona named
  maps to existing on-disk artifacts.
- Does not bypass MAYOR_ADMISSION_PROTOCOL_V0 or the §13.3 deferred
  bootstrap. MAYOR remains NOT_READY; REDUCER remains the only legal
  admission path.
- Does not elevate GOBLIN or CHIDDUSH above their existing scopes
  (mutation engine and latent-structure detector respectively).

## Use

Future Claude sessions reading this document inherit a sharper
vocabulary for reasoning about which persona a given request invokes.
The role-inversion diagnostic from CLAUDE.md
(*"HAL can decide what to reject, but not what to want"*) applies to
every persona below the REDUCER line — none of them decide; they only
propose, mutate, detect, review, witness, packetize, remember, or
prove. Only OPERATOR and REDUCER decide, and REDUCER decides only on
admission.

## Status

RAW. NO_CLAIM. NO_SHIP. This is an operator-captured synthesis, not
an admitted constitutional artifact. Promotion requires the same
six-conjunct equation as any other admission per
MAYOR_ADMISSION_PROTOCOL_V0, which remains NOT_READY under §13.3.
