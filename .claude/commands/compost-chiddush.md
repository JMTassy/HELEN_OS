# HELEN Compost Chiddush Egregor

Mine any HELEN data corpus for Chiddush insight using the compost/noise as evidence.

## Inputs

$ARGUMENTS — corpus target. Examples: "proposals", "math_garden", "conquest_garden", "knowledge", "gardening_control", or "all".

## Recipe

### Phase 1: GOBLIN Swarm (5 lanes, parallel)
Each GOBLIN lane gets one data pile and one question:
"What does this pile's own material reveal about what survives review pressure vs what stays permanently unresolved?"

Lane assignment:
- **GOBLIN-1 PROPOSAL_GRAVEYARD**: `docs/proposals/` + `temple/autoresearch/outbox/` — fate census (APPROVED / BOUNDARY / REJECTED-by-silence), survivor signature extraction
- **GOBLIN-2 MATH_GARDEN**: `temple/gardens/math_garden/` — structural doom criteria, theme-level survival patterns
- **GOBLIN-3 CONQUEST_QUARANTINE**: `temple/gardens/goblin_garden_conquest_avalon/` — enforcement gap audit, dead-field detection
- **GOBLIN-4 KNOWLEDGE_CORPUS**: `helen_os/knowledge/` — hardening rate (how many candidate patterns became live lint)
- **GOBLIN-5 GARDENING_CONTROL**: `temple/gardens/gardening_garden/` — zero-pressure baseline, template invariance measurement

Each GOBLIN: read-only, bounded to ~30 file reads, one tranche, halt before opening a second.

### Phase 2: CHIDDUSH Compression (1 agent)
Takes all 5 GOBLIN outputs. Compresses into a single original law. Must run its own circularity self-check. Must name 2+ test predictions the law makes about specific artifacts.

### Phase 3: HAL Adversarial Gate (1 agent)
Re-verifies every claim against fresh metal (re-reads the actual files, does NOT trust prior reports). Looks for:
- Near-falsifiers and genuine counterexamples
- Scope overstatements (universal claims that only hold for a subclass)
- Weak test cases (created same day, cycle=0)
- Force-fitted lanes (different failure mode dressed as the same pattern)

Verdict: CONFIRMED / CONFIRMED_WITH_CORRECTION / REFUTED.

### Phase 4: Output
Write receipt to scratchpad (NOT repo). Format: `COMPOST_CHIDDUSH_V{N}.md` with YAML frontmatter:
```yaml
authority: false
canon: false
claim_status: NO_CLAIM
ledger_effect: none
admission_status: NOT_ADMITTED
```

## Constraints

- Read-only throughout — no file in the repo is edited by this egregor.
- Total agent budget: 8 calls max (5 GOBLIN + 1 CHIDDUSH + 1 HAL + 1 FABLE overhead).
- PULL-mode: one tranche, halt per discipline.
- No authority leak — compression stays descriptive, never prescriptive.

## Loop Engineering (Fable)

Fable orchestrates the 3-phase pipeline. Feedback loop: HAL corrections from run N become GOBLIN constraints for run N+1. The law gets sharper each iteration.
