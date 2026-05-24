# No Receipt, No Claim Skill

The core HELEN invariant: **every action that produces or mutates
state must emit a receipt. No receipt means the action is
constitutionally void.**

## When this skill applies

Fire this skill when Claude is about to:

- Write to a file, database, or external system
- Make an API call that has side effects (sends a message, modifies
  a resource, charges money)
- Render a verdict (approve / reject / ship / no-ship)
- Hand off work to another actor (operator, downstream tool, sovereign)
- Close a task, seal a tranche, or mark something "done"

Do **not** fire for read-only operations (grep, list, fetch, inspect
without modification).

## What counts as a receipt

A receipt is any persistent artifact that records:

1. **Who** performed the action (actor / role / model identity)
2. **What** was done (a structured description, not just prose)
3. **When** (timestamp, ideally with hash anchor to prior receipt)
4. **Why** (the trigger or justification)
5. **What changed** (concrete observable diff — file paths, hashes,
   row counts, verdict)
6. **What's next** (if the action defers anything to another actor)

The receipt may be a JSON file, a markdown document with a structured
header, an entry in a hash-chained ledger, or a commit message — the
form is less important than that it **exists, is durable, and
references the action by hash or content**.

## The hard law

> No receipt → the action is **constitutionally void**.
> Other actors may treat the state as if the action never happened.
> Future audits may invalidate any state that lacks a receipt for the
> action that produced it.

## When the verdict is BLOCK / NO-SHIP / REJECT

**BLOCK still emits a receipt.** A rejection is a real decision with
real downstream consequences (the proposer must iterate; the artifact
does not advance). The receipt for a BLOCK should contain:

- Which check failed (named, not vague)
- What evidence supports the failure
- What the proposer must change to retry
- A halt-boundary section if the rejection defers to a sovereign

A BLOCK without a receipt is worse than no decision — it's an
invisible block. The proposer cannot audit it, cannot iterate, cannot
appeal.

## When the receipt is "skipped"

If a later stage of work was not reached because an earlier stage
failed (e.g. test suite skipped because compile failed), the receipt
must explicitly mark the skipped stage:

```
stages:
  build:    { result: PASS, ... }
  test:     { skipped: true, reason: "build failed" }
  deploy:   { skipped: true, reason: "build failed" }
```

This prevents downstream consumers from confusing **"didn't fail"**
with **"didn't run"**.

## Reference patterns

**Pattern 1: file mutation with commit receipt**
```
git commit -m "fix(foo): repair bar

  Why: bar was emitting null on empty input (issue #123)
  How: wrap input in NULLIF before division
  Receipt: tests/test_bar.py::test_empty_input now PASS
  Halt: none — fix is self-contained"
```

**Pattern 2: governance receipt as JSON**
```json
{
  "schema_name": "<RECEIPT_SCHEMA>",
  "actor": {"role": "...", "identity": "..."},
  "action": "...",
  "evidence": {...},
  "verdict": "ADMIT | QUARANTINE | REJECT",
  "halt_boundary": {...},
  "timestamp_utc": "..."
}
```

**Pattern 3: BLOCK with reason and remedy**
```
[BLOCK] proposal X did not pass gate Y

  Failed check:    obligation #3 (artifact SHA mismatch)
  Evidence:        expected abc123..., observed def456...
  Remedy:          rebuild artifact and retry
  Halt boundary:   none (proposer-actionable)
```

## Anti-patterns (these fail the invariant)

- **Silent success**: action succeeded; no log, no commit, no record. Future Claude has no idea what happened.
- **Verbal-only receipt**: "I did X" in chat with no durable artifact. Conversation context is fragile; receipts must be durable.
- **Vague BLOCK**: "this doesn't seem right" with no named check, no evidence, no remedy.
- **Implicit skip**: a downstream stage didn't run; the receipt is silent about it. Reader assumes it ran successfully.
- **Composite receipt**: one receipt covering 10 actions with no per-action attribution. Cannot audit individual decisions.

## Companion skills

- `halt-boundary` — required when a receipt defers work to a sovereign
- `proposer-validator` — receipts must be reviewable by an actor other than the proposer
- `goblin-role` — operational form when Claude is the receipt-producer for a non-sovereign action
