# HELEN OS — Claude Instructions

Standing brief for every session. Read before engaging.

## Memory Protocol (the compound loop)

Every time the operator shares major context about HELEN OS, the business, or architectural decisions, update `.claude/memory.md` with the key details.

Always reference past decisions in memory.md before making new recommendations.

**The 5-stage progression (Continual Learning Bench):** FAIL → INVESTIGATE → VERIFY → DISTILL → CONSULT. The state file `.claude/STATE.md` is where each stage's output is written.

- **Read at session start.** Begin every session by reading `.claude/STATE.md` and the relevant skills. Without this, even a top-tier model regresses to restart-from-zero behavior.
- **Write before walking away.** End every session by updating `.claude/STATE.md` — what was tried, what passed, what failed, what new rules survived. If the session doesn't finish with a write, the next one restarts from zero.
- **Distill into the skill, not just STATE.** After any non-trivial failure, write the lesson into the skill that produced the artifact (`.claude/commands/*.md`), not only STATE.md. STATE.md is session-scoped; skills travel.
- **Evaluate before committing — keep or revert.** A skill edit is not automatically an improvement. Before committing a change to a skill file, check it against the version it replaces: does it produce a better result on the next real run, or just a different one? If a distilled "lesson" makes the next run worse (more REFUTED verdicts, more operator correction needed, not less), revert it — don't keep it because it's new. This step was previously missing; see `.claude/LOOPS.md`.
- The skill gets sharper every run only if the Evaluate step actually runs — "we wrote a lesson down" is not the same claim as "the skill got better."

## Verification Protocol (maker ≠ grader)

The agent that produces an artifact NEVER verifies it. Spawn an independent verifier (`/verify`) with no exposure to the maker's reasoning — this is both the K2 anti-violation (proposer ≠ validator) and the Fable-5 verifier-sub-agent pattern.

- Before reporting anything "done", point to the result that proves it. Unverified = say so plainly, marked UNVERIFIED, not FIXED.
- A REFUTED verdict HALTS the pipeline. Do not proceed past a failed gate.
- Vision artifacts (UI, charts) require vision-verify — text-only verifiers miss the failure that matters.

## Response Rules

- Use WULmoji in all verdicts, summaries, and gate results
- Format: `🛡️✅ GATE — VERDICT` / `🧪 TESTS` / `📦 FILES` / `🚦 NEXT`
- Never render 🟢/🟡/⚪ for non-admitted artifacts
- Receipts over explanations — show what was done, not what you thought about
- Match the operator's energy: compressed directives get compressed execution

## Sovereign Firewall (absolute)

Never edit: `helen_os/governance/`, `helen_os/schemas/`, `oracle_town/kernel/`, `town/ledger_v1.ndjson`, sealed proposals, constitutional files.

If a task appears to require a sovereign write, STOP and report.

## Model Routing (enforce in all skills)

```
DEFAULT:  ORNITH (local GPU, free)
ESCALATE: Sonnet 5 (code patches, HAL gate, tests)
RARE:     Fable 5 (orchestration, planning, final verification only)
```

Rule: ORNITH default. Escalate only on 2x failure or proof-grade reasoning.

## Barbell Strategy (enforce in all loops)

```
Planning     (10%): Fable 5 — design the loop, set success criteria
Execution    (80%): ORNITH/Sonnet subagents — do the work
Verification (10%): Fable 5 — verify against the spec
```

## After Any CLAUDE.md Edit

```bash
python3 scratchpad/generate_claude_index.py
git add scratchpad/CLAUDE_MD_LINE_INDEX.txt scratchpad/CLAUDE_MD_SECTIONS_BY_LENGTH.txt
```

## Commit Protocol

- Branch: `claude/code-review-optimizations-hx26jn` (or as directed)
- Never push to main without explicit permission
- Commit message style: `type(scope): description`
- Co-author line required
