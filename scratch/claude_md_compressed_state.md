# CLAUDE.md "Current State" — compressed replacement (PROPOSAL ONLY)

NON_SOVEREIGN · authority=false · ledger_effect=none · NOT APPLIED
Loop artifact: autoresearch iteration 1 (prompt-compression target, 2026-07-06).
Apply requires operator mark + `python3 scratchpad/generate_claude_index.py` regen.

---

## Measured verdict against the stated keep-rule — REJECT (honest)

- Rule (iteration 1): keep if **≥90 lines saved**, zero information orphaned.
- Measured: section spans **lines 333–384 = 52 lines** (assumption "~106 lines
  of snapshot mass" was wrong — the strata duplicate architecture sections
  more than they add length).
- Replacement below: **20 lines** → saving = **32 lines (6.4% less than 90)**.
- **Verdict: REJECT by the rule as stated.** Two lawful continuations for the
  operator: (a) re-rule the threshold (≥30 lines is realistic for this file's
  granularity), or (b) retarget the loop at the true mass — `Architecture
  Layers` (73 lines, heavy per-skill detail duplicating SKILL.md files) and
  `Running HELEN` (56 lines, command examples duplicating --help output).
- Hypothesis falsified cleanly: boot-context weight is in reference
  duplication, not in dated snapshots. That finding is the iteration's value.

---

## Replacement text (drop-in for lines 333–384)

```markdown
## Current State

**Do not trust dated state — run `git log` and `make test`.** Architecture
details live in the sections above; the strata below keep only facts stated
nowhere else.

- **2026-07-03** (`12ec35a`): `transport/` math program · AUTORESEARCH safe
  architecture V1 (outbox packets, always `authority=false`) ·
  authority-language linter · `do_next_v1` structural policy engine ·
  `temple/gardens/` layer (core law DREAMT ≠ CLAIMED). Gates and firewall
  unchanged.
- **2026-06-15** (`4d1e185`): skill-promotion admission LIVE — 6-gate
  `_handle_promote_skill()` + `_handle_seq_correction()`; NDJSONWriter
  `flock` + tail re-read closes the TOCTOU fork (seq=287 ANCHORED at
  seq=295, chain PASS); `hal_verdict_from_kernel()` now passes `mutations`
  through; Temple EXPLORE mechanic E026 unlocked.
- **2026-06-03**: operator surfaces (`apps/helen-surface/`) · SOURCEBOUND
  OBJECT OS · local HAL routing (`MODEL_ROUTING_V1`) · `helen_awakening` /
  portrait video lanes · GOBLIN_TEMPLE inner memory rooms + Akashic
  interface · Telegram `/her` (Groq fallback).
- **2026-05-06 uniques**: SKILL_REGISTRY_V1 audit (75 skills: 51 canonical /
  3 legacy / 3 dup / 18 external) · HELEN_CHARACTER_V2 consistency method ·
  HELEN OS v2 UX four-file suite (FOCUS | WITNESS, locked phrases) —
  PROPOSAL, never promoted. AUTORESEARCH E11/E12 reconciliation status:
  see Open Frontiers.
```

---

## Orphan check (every unique fact, where it survives)

| Fact appearing only in old strata | Survival |
|---|---|
| seq=287 anchored at 295, chain PASS | kept (2026-06-15 bullet) |
| `hal_verdict_from_kernel()` mutations fix | kept (2026-06-15 bullet) |
| EXPLORE E026 bootstrap-deadlock closure | kept (2026-06-15 bullet) |
| helen_awakening / portrait video lanes | kept (2026-06-03 bullet) |
| GOBLIN_TEMPLE inner rooms, Akashic, /her + Groq | kept (2026-06-03 bullet) |
| SKILL_REGISTRY_V1 75-skill audit split | kept (2026-05-06 bullet) |
| HELEN_CHARACTER_V2 method | kept (2026-05-06 bullet) |
| UX v2 four-file suite + locked phrases | kept, compressed (2026-05-06 bullet) |
| E11/E12 awaiting peer-review → MAYOR; E13 blocked | already in Open Frontiers (dedup, pointer kept) |
| "Kernel daemon currently down" (2026-05-06) | dropped — stale runtime status, never load-bearing |
| Per-lane detail (protocols list, test names, commit SHAs of merged work) | already duplicated in Architecture Layers / Governance Artifacts / git history |

---

## Loop bookkeeping (iteration 1 close-out)

- TARGET: prompt compression — CLAUDE.md dated snapshots ✔ executed
- METRIC: 52 → 20 lines (32 saved); doc-index regen required on apply
- RULE: ≥90 saved → **REJECT** (rule honored over outcome)
- NEXT (if operator re-rules or retargets): `Architecture Layers` section,
  same method — collapse per-skill detail to SKILL.md pointers; est. 73→~35.

HOLD_FOR_OPERATOR — apply step is yours. proposal ⊬ admission · 📜 ledger sleeps
