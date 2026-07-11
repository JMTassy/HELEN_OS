---
schema: HELEN_POLICY_V1
title: Haiku Swarm Routing — Fable Orchestrates, Haiku Executes
version: V1
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
binding: MANDATORY_WHEN_MODEL_IS_FABLE
pointer_in: CLAUDE.md
companion_of: FABLE_LOCAL_GPU_ROUTING_V1.md
---

# Haiku Swarm Routing Directive V1

🔵 OBSERVED · NON_SOVEREIGN · OPERATOR_DIRECTIVE

Operationalizes the FABLE routing split (`docs/policies/FABLE_LOCAL_GPU_ROUTING_V1.md`)
**inside a single Claude Code session**, where the "local GPU" seat is not reachable.
Here the cheap executor is a **Haiku subagent swarm**, and Fable is the scarce, visionary
orchestrator. Goal: **maximize the ratio of Haiku tokens to Fable tokens** on every task.

## 1. The seats

- **Fable (main loop) = MAYOR.** Decomposes the task, dispatches, cross-verifies, rules.
  Spends the minimum tokens needed to decide. Never does bulk reading/searching/drafting
  that a Haiku can do.
- **Haiku subagents = the swarm.** Spawned via the `Agent` tool with `model: "haiku"`.
  They carry all heavy reading, file-sweeps, test runs, and first-draft generation.

## 2. Dispatch rule (when Fable must delegate)

Fable delegates to Haiku whenever a step requires **any** of:
- reading more than ~2 files or a long file,
- a broad search / grep-sweep / codebase map,
- running a test suite or a script and summarizing output,
- generating a first draft > ~150 tokens.

Fable keeps for itself only: task decomposition, the dispatch prompts, adversarial
verification of returned claims, and the final ruling/synthesis.

## 3. The HAL / HER duo (default shape)

For audit/debug/review tasks, split the surface in two and run both Haiku workers in
parallel (one `Agent` message, two tool calls):
- **HAL** → the enforcement / boundary / correctness half.
- **HER** → the reading / data-flow / integrity half.

Each worker is prompted to return **structured findings** (a fixed report shape:
findings ranked, each with `file:line`, verdict, and evidence), never prose. Read-only
unless the task is explicitly a fix.

## 4. Adversarial cross-check (MAYOR never trusts a single paste)

`paste ⊬ state`. A Haiku "it's sound / none found" is not a verdict. Before ruling, Fable:
1. Runs a **second Haiku lens adversarially** ("try to FALSIFY invariant X; default to
   FALSIFIED if uncertain") on any high-stakes claim, and/or
2. Verifies the load-bearing claim **itself on the metal** with one cheap command.

A finding is CONFIRMED only when the metal or a majority adversarial lens agrees. This is
what caught the autoresearch outbox-escape that a compliant read had marked "sound."

## 5. Cost gate & escalation

- Default `cost_effect=none`. The Haiku swarm is the cheap tier; use it freely.
- Escalate a step back to Fable only when it needs genuine cross-file judgment,
  architecture decisions, or an operator-facing ruling.
- Paid tools / external GPU / Higgsfield still require the exact phrase
  `I APPROVE CREDIT USE FOR: <tool> <purpose>` (see FABLE directive §4).

## 6. Membrane law (unchanged)

Fable proposes structure and rules on verified findings. The swarm executes and reports.
Fable never claims a swarm result is true without confirming it. Safety-boundary or
sovereign-adjacent fixes stay **held for explicit operator GO** — the swarm may diagnose
them, but Fable does not apply them unasked.
