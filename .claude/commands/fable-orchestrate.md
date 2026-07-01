# HELEN Fable Orchestrator

Fable 5 master loop: orchestrate multi-skill workflows using the HELEN skill palette.

## Inputs

$ARGUMENTS — workflow name. Options:
- `weekly` — full weekly cycle (audit → review → garden → compost)
- `review-cycle` — code review sweep across all active directories
- `research-cycle` — autoresearch tranche → math garden → compost mining
- `governance-only` — audit all gates, patch what's auto-fixable
- `relay-batch` — prepare N relay prompts for ORNITH local dispatch
- `custom` — operator specifies skill sequence

## Workflows

### weekly (recommended cadence)
```
Phase 1: governance-audit full          # gates green?
Phase 2: code-review transport/ tools/  # bugs in active code?
Phase 3: math-garden all M{next}-M{next+20}  # 20 new epochs
Phase 4: compost-chiddush all           # mine the noise
```
Budget: ~12 agent calls. Estimated: 5 ORNITH + 5 Sonnet + 2 Fable.

### review-cycle
```
for dir in [transport/, tools/, scripts/, temple/gardens/, oracle_town/skills/]:
    code-review $dir
```
Serial — each directory's findings inform the next (e.g., a pattern found in transport/ is checked in tools/).

### research-cycle
```
autoresearch-tranche {frontier} 5   # 5 bounded epochs
math-garden {theme} M{next}-M{next+10}  # 10 garden epochs
compost-chiddush all                # mine everything
```
The autoresearch findings feed the math garden theme selection. The compost egregor mines the autoresearch output itself.

### governance-only
```
governance-audit full
# auto-patch: STALE_ALLOWLIST with citations
# report: everything else
```

### relay-batch
```
for task in operator_queue:
    relay-prompt $task
# Output: N relay packets ready for local dispatch
```

## Model Routing

| Role | Model | Cost | When |
|---|---|---|---|
| FABLE orchestrator | claude-fable-5 | $$ | Always (1 call per workflow) |
| GOBLIN miners | ORNITH local | FREE | Default for read-only mining |
| Code review | Sonnet 5 | $ | Needs code understanding |
| HAL gate | Sonnet 5 | $ | Adversarial verification |
| CHIDDUSH | Sonnet 5 | $ | Compression needs reasoning |
| Math garden | ORNITH local | FREE | Bounded epoch generation |
| Relay prep | Sonnet 5 | $ | Prompt engineering |

**Routing law**: ORNITH default, FABLE escalation only on evidence (2x failure or proof-grade reasoning).

## Loop Feedback

Each workflow run produces:
1. A receipt (what was done, what was found)
2. A sharpening delta (what to exclude/prioritize next time)
3. A cost report (API calls used, estimated tokens)

The sharpening delta feeds back into the skill files themselves — Fable updates the exclusion lists, priority rankings, and known-false-positive patterns.

## Constraints

- One tranche at a time (PULL-mode discipline)
- Never two governance audits in parallel (could race on kernel_guard)
- Sovereign firewall is absolute — no skill can override it
- Total agent budget per workflow: max 20 calls
- All outputs are NON_SOVEREIGN, authority=false until operator promotes
