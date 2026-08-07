# HELEN_OS_ROSE

Model-agnostic operating system for ROSE and CIELO IMPACT. It converts ideas
and opportunities into a disciplined priority stack, with evidence-linked
claims and Rose as the only source of approval.

Inherits the host repository's invariant: **NO RECEIPT = NO CLAIM.**

## What lives here

| Path | Purpose |
|---|---|
| `OPERATING_CONTRACT.md` | Sovereignty rules, roles, lifecycle, privacy partitions |
| `CURRENT_STATE.md` | What exists, what is wired, what is tested, what Rose has decided |
| `strategy/` | Thesis, priority stack, 90-day plan, assumptions, kill criteria, opportunity register |
| `execution/` | Execution packets (only from a Rose `GO`); template in this folder |
| `decisions/` | Rose decision template + append-only `decision_ledger.jsonl` |
| `research/` | Open questions, evidence register (E0–E5), research packet template |
| `receipts/` | Bootstrap receipt and future receipts |
| `domains/` | One folder per activity area, each with its own privacy class |
| `schemas/` | JSON schemas for decisions, packets, evidence, receipts |
| `prompts/` | Permanent role prompts: STRATEGY, EXECUTION, SOVEREIGN_REVIEW, weekly review |
| `scripts/` | Deterministic stdlib tooling (validator, packet creator, ledger appender, claim linter) |
| `tests/` | Test suite for the tooling and the sovereignty invariants |

## Daily commands

```bash
# validate the whole workspace (structure, ledger, packets, claims)
python3 HELEN_OS_ROSE/scripts/validate_workspace.py

# lint claims only
python3 HELEN_OS_ROSE/scripts/claim_linter.py

# record a Rose decision (the ONLY way a decision becomes real)
python3 HELEN_OS_ROSE/scripts/append_decision.py \
  --decision-id R-001 --subject "..." --outcome GO \
  --scope "..." --rationale "..." --authorized-by "ROSE"

# open an execution packet from a GO decision
python3 HELEN_OS_ROSE/scripts/create_execution_packet.py \
  --decision-id R-001 --outcome "..." --scope "..." \
  --owner ROSE --privacy-class INTERNAL_BUSINESS

# run the test suite
python3 -m unittest discover -s HELEN_OS_ROSE/tests
```

## Roles (functions, not identities)

The permanent system works through three neutral functions — any capable
operator, human or machine, can hold them:

- **STRATEGY** — diagnoses, compares at most three options, recommends one, never approves its own recommendation. Prompt: `prompts/strategy.md`
- **EXECUTION** — acts only on a Rose-authorized `GO`, inside a bounded packet. Prompt: `prompts/execution.md`
- **SOVEREIGN_REVIEW** — prepares decisions for Rose in plain language and requests exactly one outcome. Prompt: `prompts/sovereign_review.md`

## The one rule that matters

Nothing generated here is decided. A strategy, plan, or artifact remains
`PROPOSED` until Rose records an explicit decision in the ledger. See
`OPERATING_CONTRACT.md`.
