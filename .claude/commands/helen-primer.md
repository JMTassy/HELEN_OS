# HELEN Primer — for a model with zero prior context

Not a copy of `CLAUDE.md` (425 lines, comprehensive reference — read
that for depth) or `instructions.md` (71 lines, procedural rules for
every session). This is what a model with *no* prior HELEN OS context
needs to not make a catastrophic mistake in its first five minutes,
ranked by consequence, written to explain *why* — because a rule you
understand the reason for is one you generalize correctly to a case
that isn't explicitly written down, and a rule you were just handed
isn't.

Written once, at Fable-tier reasoning, specifically so an everyday
model reading this doesn't have to independently re-derive what
actually matters from 425 lines of reference doctrine every time.

## Inputs

None — this is read, not parameterized. Invoke it once, at the start
of any HELEN OS work, if you have no memory of this repo from a prior
session.

## The five things that actually matter, ranked by what breaks if you get them wrong

### 1. The sovereign firewall — never edit these, no exception

```
helen_os/governance/**    helen_os/schemas/**    oracle_town/kernel/**
town/ledger_v1.ndjson     GOVERNANCE/CLOSURES/**  sealed constitutional files
```

**Why**: this is the actual governance guarantee the entire system
exists to provide. Everything else in HELEN — the skills, the gardens,
the audits, the agents — sits on top of an assumption that this layer
is untouched except through its own admitted, receipted process. Edit
it directly and you haven't broken a feature, you've broken the reason
anything here is trustworthy. If a task seems to require touching one
of these paths, that's not a task to complete creatively — stop and
report it. There is no version of "just this once, it's a small fix"
that doesn't apply to every future violation too.

### 2. NO RECEIPT = NO CLAIM

**Why**: an agent claiming "fixed," "tested," "verified" without
pointing at the artifact that proves it is indistinguishable, from the
outside, from an agent that just wants the conversation to feel
finished. This session's own audits (steelman, AR-TERMINATION-002)
found this exact failure mode already live in the repo — 931 PROPOSED
governance objects, zero with a review date, because "PROPOSED" started
functioning as a place to put things rather than a state something
passes through. Before reporting anything done: point to the test
output, the file diff, the git log entry. If you didn't check, say
`UNVERIFIED`, not a confident sentence that implies you did.

### 3. Maker never grades its own work

**Why**: a model evaluating its own output prefers conclusions
consistent with its own reasoning trail — not from bad faith, from
structure. This repo's own K2 rule (proposer ≠ validator) and this
session's Parameter-Golf-derived verifier-subagent pattern are the same
finding from two directions. Concretely: if you build something, don't
be the one who signs off that it's correct. Spawn a separate pass
(`/verify`, a reviewer agent, HAL) with no exposure to your reasoning,
only the artifact and the spec.

### 4. Garden content can be wild; it can never leave the garden quietly

`temple/gardens/` is an explicit NO_CLAIM zone — fiction, myth, sacred
geometry, whatever, all permitted, per `GARDEN_NO_CLAIM_RULE_V0.md`.
**Why this is safe**: because it's locational, not lexical — the
content itself is never judged, only whether it tries to cross out
(claim real effect, carry `authority=true`, leave the garden into
canon). **Why the WULMOJI rendering rule matters as the enforcement
mechanism**: never render 🟢 (admitted) / 🟡 (sealed) / ⚪ (replayable)
on anything that hasn't actually passed an operator admission receipt,
a hash-lock, or replay validation — regardless of how confident or
well-formatted the content looks. A garden artifact dressed up in
admitted-looking color is the crossing this rule exists to prevent.

### 5. Termination is sacred — bounded retry, not open-ended

**Why**: AR-TERMINATION-002 found 87.6% of this repo's governance
objects sitting in a parking state with zero deletions across the
entire visible git history. Unbounded accumulation looks like progress
(more receipts, more PROPOSED files, more analysis) while actually
being the opposite — output without termination is exactly what a
Governance Yield metric of zero looks like. Concretely: 2 strikes on a
retry, then escalate or stop. One hypothesis per autoresearch epoch,
sealed before the next opens. If you're not sure whether something is
done, that uncertainty itself is information — say so and stop, don't
generate another paragraph hoping the next one resolves it.

## What to do with this

Read `.claude/STATE.md` next (compounding memory — what's actually
open right now) and `.claude/instructions.md` (the procedural rules:
WULmoji formatting, the Memory Protocol, the Verification Protocol).
Read `CLAUDE.md` in full only when you need the depth this primer
deliberately left out — architecture layers, schema authority, the
full gate table. This primer's job is done once you know *why* the
five rules above exist; everything else is detail you can look up when
a specific task actually requires it.
