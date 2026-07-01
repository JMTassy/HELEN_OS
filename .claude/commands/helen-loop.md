# HELEN Loop Patterns

Pre-built loop configurations for `/goal` and `/loop` commands.

## Inputs

$ARGUMENTS — loop pattern name. Options below.

## Available Loops

### 1. `review-and-fix` (/goal)
Single-pass: review all Python files changed in last N days, fix what's safe, report the rest.
```
/goal Review all Python files changed in the last 14 days using /code-review.
Fix CRASH and SECURITY findings immediately. Run make test after each fix.
Report PERF/DEAD/DETERMINISM findings for operator decision.
Stop when all files are reviewed and tests pass.
```

### 2. `governance-watch` (/loop)
Recurring: run governance audit every interval, auto-fix stale allowlists.
```
/loop every 60 minutes, run /governance-audit full.
If kernel_guard has STALE_ALLOWLIST violations with filed authorizations, auto-patch.
For all other failures, log to .claude/memory.md and alert me.
```

### 3. `garden-grow` (/goal)
Single-pass: generate N math garden epochs, rank by mechanization feasibility.
```
/goal Generate 20 new math garden epochs using /math-garden.
Distribute across all 9 themes. Rank the outputs by mechanization feasibility
(does a finite witness exist? can it be tested in <50 lines of Python?).
Stop when 20 epochs are written with honest receipts.
```

### 4. `compost-mine` (/goal)
Single-pass: run the full compost chiddush egregor.
```
/goal Run /compost-chiddush all.
Phase 1: 5 GOBLIN lanes in parallel (route to ORNITH if available).
Phase 2: CHIDDUSH compression (Sonnet).
Phase 3: HAL adversarial gate (Sonnet).
Write the receipt to scratchpad. Stop after HAL verdict.
```

### 5. `surface-polish` (/goal)
Single-pass: vision-audit all surfaces, fix violations, verify.
```
/goal Run /vision-audit on all 10 HELEN surfaces.
For any surface scoring below 8.0, run /surface-iterate to fix violations.
Re-audit after fixes. Stop when all surfaces score >= 8.0 or plateau.
Present before/after screenshots for each changed surface.
```

### 6. `relay-dispatch` (/goal)
Single-pass: prepare relay prompts for ORNITH, output for operator paste.
```
/goal Using /relay-prompt, prepare relay packets for these tasks: [task list].
Route each to ORNITH or FABLE based on complexity.
Output all ORNITH packets formatted for terminal paste.
Flag any FABLE-escalation tasks separately.
```

### 7. `weekly-cycle` (/goal)
Full weekly workflow via the orchestrator.
```
/goal Run /fable-orchestrate weekly.
Phase 1: governance-audit (fix what's auto-fixable)
Phase 2: code-review (all active directories)
Phase 3: math-garden (20 new epochs)
Phase 4: compost-chiddush (mine the noise)
Produce a weekly receipt with per-phase verdicts and total cost.
```

### 8. `pr-watch` (/loop)
Recurring: monitor a PR for CI and review comments.
```
/loop Watch PR #N for CI failures and review comments.
On CI failure: diagnose, fix, push.
On review comment: assess, fix if clear, ask me if ambiguous.
Stop when PR is merged or I tell you to stop.
```

## Barbell Cost Pattern

Every loop applies the barbell by default:
- **Fable plans** the loop (this file, read once)
- **Subagents execute** each iteration (Sonnet/ORNITH, cheap per call)
- **Fable verifies** the final output (one check at the end)

Estimated costs per loop type:
| Loop | Fable calls | Sonnet calls | ORNITH calls | Total API |
|---|---|---|---|---|
| review-and-fix | 1 plan + 1 verify | ~10 per dir | 0 | ~12 |
| governance-watch | 1 per interval | 0 | 0 | ~1/hr |
| garden-grow | 1 plan + 1 verify | 0 | 20 | ~2 |
| compost-mine | 1 plan + 1 verify | 2 (CHIDDUSH+HAL) | 5 (GOBLINs) | ~9 |
| surface-polish | 1 plan + 1 verify | ~5 fixes | 0 | ~7 |
| weekly-cycle | 2 (plan+verify) | ~15 | ~5 | ~22 |

## Constraints

- `/loop` intervals: governance-watch is the only recommended recurring loop. All others are `/goal` (run once, stop when done).
- Never run two governance audits in parallel.
- PULL-mode discipline: one tranche at a time for autoresearch loops.
- All loop outputs are NON_SOVEREIGN until operator promotes.
