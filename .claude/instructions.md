# HELEN OS — Claude Instructions

Standing brief for every session. Read before engaging.

## Memory Protocol

Every time the operator shares major context about HELEN OS, the business, or architectural decisions, update `.claude/memory.md` with the key details.

Always reference past decisions in memory.md before making new recommendations.

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
