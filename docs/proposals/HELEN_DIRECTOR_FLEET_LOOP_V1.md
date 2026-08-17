---
schema: HELEN_PROPOSAL_V1
title: HELEN Director Fleet Loop V1
authority: false
sovereign: false
canon: false
ledger_effect: none
reducer_required: true
git_stage: no
git_commit: no
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
---

# HELEN Director Fleet Loop V1

🟣 CLAIM · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

> **STATUS:** PROPOSAL — extends `oracle_town/skills/video/helen-director/SKILL.md`
> §15.1 (parallel submission, live). Does not replace or amend any live section.
> **HARD GATE:** `AGENTS.md` forbids scaling render generation without explicit
> approval. Nothing in this document executes without an operator `GO FLEET`.
> **PROVENANCE:** loop-engineering pattern observed in external field practice
> (operator-routed, 2026-07-29); mechanisms below are re-derived against
> HELEN's existing receipt discipline, not imported verbatim.

---

## 1. Purpose

§15.1 already runs one cut's shots in parallel (submit all, poll one loop,
~6–8 min for 10 shots). The fleet loop is the layer above it: a full shot
list covered by **shot-family subagents**, throttled against provider
concurrency, iterating per shot under a one-variable rule, every generation
bound to a receipt sidecar. It turns "render this cut" into "cover this
production overnight" — under operator budget, never autonomously.

## 2. Three nested loops

| Loop | Owner | Terminal condition |
|---|---|---|
| Shot loop | subagent | shot has ≤4 candidates and 1 winner, or is marked BLOCKED |
| Fleet loop | orchestrator | every shot in the list is WON or BLOCKED |
| Session loop | ledger | receipts written; next production reads them |

No loop is open-ended. Termination is sacred: each loop exits on its
condition or on budget exhaustion — SHIP the winners collected so far, or
ABORT with receipts. No idle waiting states.

## 3. Fleet loop specification

### 3.1 Orchestration
- One orchestrator session owns the shot list (STORYBOARD_V1 order).
- Shots are grouped into families (e.g. presence / water / interior /
  motion-climax). One subagent per family. Each subagent inherits the
  style contract and character sheets by reference — pasted verbatim,
  never paraphrased (consistency comes from repeated language, not seeds).

### 3.2 Concurrency (the load-bearing rule)
- `FLEET_CONCURRENCY_CAP = 6` (conservative; §15.1 observed ≥10 accepted,
  higher untested — cap raises only by operator decision, never by probe).
- The orchestrator tracks active jobs across ALL subagents; a subagent
  submits only when `active < CAP`. A throttled fleet finishes overnight;
  a naive loop dies on rate limits and burns credits on abandoned jobs.
- Queue-stall abort per §15.2 discipline: any job in `queued` > 3 min is
  abandoned (it may still bill — log it as `COST_ORPHAN` in the sidecar).

### 3.3 Iteration discipline
- 3–4 candidates per shot, then STOP — winner or BLOCKED.
- Between candidates change exactly ONE variable: camera, lighting, or
  speed. Never a full prompt rewrite. A fail with five changed variables
  teaches nothing; a fail with one changed variable is a measurement.
- Resolution ladder: 720p while exploring, 1080p for keepers, 4K upscale
  once, on the final assembled cut only. Never upscale individual clips.

### 3.4 Receipt sidecar (per generation, mandatory)

```json
{
  "schema": "FLEET_GENERATION_RECEIPT_V1",
  "shot_id": "<storyboard id>",
  "family": "<subagent family>",
  "candidate_index": "<1-4>",
  "prompt_sha256": "<hash of exact submitted prompt>",
  "model": "<endpoint id>",
  "variable_changed": "camera|lighting|speed|NONE(first)",
  "result_url_sha256": "<hash>",
  "status": "WON|KILLED|FAILED|COST_ORPHAN",
  "operator_rating": null
}
```

- `operator_rating` stays `null` until Telegram rating per SKILL.md §rating
  rule — absence of rating = BLOCK, unchanged. The fleet never rates.
- NO RECEIPT = NO CLAIM: a clip without a sidecar does not exist for
  montage purposes, whatever is on disk.

### 3.5 What the fleet may NOT do
- Start without an explicit operator `GO FLEET <shot-list> <credit-budget>`.
- Exceed the credit budget (hard stop; ships partial winners + receipts).
- Pick winners. Subagents nominate ≤2 candidates per shot; the operator's
  rating decides. Taste is not delegated.
- Write to any ledger directly. Receipts route through `helen_say.py` only.
- Raise its own concurrency cap or retry a `COST_ORPHAN`.

## 4. Session loop

After each fleet run, the sidecar set is the production database: which
prompt shapes WON per family, which variables mattered, orphan cost total.
The next production's subagent briefs are seeded from WON receipts only —
KILLED prompts are negative examples, FAILED are provider evidence.
This is the article-pattern "log everything" made admissible: same loop,
hash-bound, replayable.

## 5. Admission path

1. This document: 🟣 CLAIM, staged for operator review (🟠 REVIEW on read).
2. Operator rules on: cap value, budget mechanism, family taxonomy.
3. If admitted: spec merges into SKILL.md as §15.3 by explicit operator
   commit; `FLEET_GENERATION_RECEIPT_V1` registers via schema authority.
4. First fleet run is a bounded pilot: ONE family, ≤6 shots, explicit
   budget, operator present. Overnight autonomy only after the pilot's
   receipts are reviewed.

## 6. Non-goals

No model routing changes, no new provider integrations, no montage changes
(pilot_v8f ffmpeg path is untouched), no autonomous taste, no sovereignty.
The fleet is throughput under governance — HELEN suggests, you decide,
everything is recorded.
