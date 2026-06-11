---
name: project-helen-hermes-split
description: Two-agent separation: HELEN-CLAUDE (gate/architect) vs HERMES (executor) — non-interchangeable prompts, anti-K2-violation pattern
metadata:
  type: project
---

HELEN and HERMES are not the same agent with the same prompt. They are complementary halves.

| Agent | Role | Prompt core |
|---|---|---|
| HELEN-CLAUDE | Architect / Reviewer / Gatekeeper | JURISDICTION BEFORE COGNITION — locate surface, epoch, authority, claim type before thinking |
| HERMES | Executor / Operator / Runner | RECEIPT BEFORE CLAIM — do the work, produce evidence, then speak |

**Why:** A single agent that thinks + acts + verifies + self-validates recreates the K2 violation (proposer = validator). HELEN narrates; HERMES executes; HELEN verifies. Never collapse these into one.

**Architecture:**
```
HELEN (Jurisdiction Gate)
  → APPROVE / DENY
  → HERMES (Execution Engine)
  → RECEIPT
  → HELEN (Verification)
```

Maps to existing HELEN doctrine: MAYOR=gate, RALPH/DAN=executors, ledger=receipt layer.

**How to apply:** When designing multi-agent workflows in HELEN OS, assign the gate/review role to a fresh HELEN context and the execution role to a separate HERMES context. Never let Claude analyze AND execute AND verify in the same context chain without a human gate between.

**Signal that the split is needed:** An agent claiming "file written", "ledger updated", "grep executed" without a corresponding receipt — this is the K2 violation the split prevents.

**Observed 2026-06-11:** Operator identified this pattern after a trace showed hallucinated actions in a TRACE_ONLY session. Source: AUTORESEARCH_E2E_REAL_INIT precheck discussion.

**Related:** [[project-action-surface-drift]], [[project-helen-kernel-canon]]
