# Proposer ≠ Validator Skill

**The actor who authors an artifact cannot be the actor who admits it
into canon.** Authorship and admission must be separated.

## When this skill applies

Fire this skill when Claude is about to:

- Approve / merge / admit work that Claude itself produced
- "Self-validate" code, a document, a decision by re-reading it and
  declaring it acceptable
- Iterate on a proposal and then mark the proposal "done" in the same
  turn
- Make architectural decisions about code Claude just wrote, without
  a second reviewer in the loop

Do **not** fire if:
- The action is genuinely separated (Claude proposes; operator or
  other reviewer admits)
- The artifact is read-only (audits don't admit anything)
- The action is mechanical/tested (test pass/fail is not a value
  judgment by the author)

## The hard law

> Authorship → review → admission is a **three-step pipeline**.
> The same actor cannot occupy both step 1 and step 3.
> Step 2 (review) may be the same actor as step 1 in early drafts but
> never as step 3.

This is identical to: peer review in scientific publication, code
review in software engineering, the separation of legislative drafting
from judicial admission, and the distinction between an author and an
editor.

## Why this matters

Self-validation has two specific failure modes:

1. **Confirmation bias.** The proposer reads their own draft as the
   draft they *meant* to write, not the draft they *actually* wrote.
   Errors invisible to the author surface easily to a second reader.
2. **Authority capture.** If the proposer can also admit, every
   proposal is also a verdict. The proposer accumulates admission
   power without external check. Over time the canon drifts toward
   what the proposer wants rather than what survives review.

## Reference patterns

**Pattern 1: explicit separation in a receipt**
```yaml
proposer:
  role: agent
  identity: claude-opus-4-7
attestor:
  role: ci-script
  identity: pytest --strict
```

The attestor is a different mechanism from the proposer. Even if both
are non-human, they are different signals.

**Pattern 2: handoff with halt**
```markdown
## Halt boundary

GOBLIN proposes the fix. GOBLIN does not admit.

Resume conditions:
1. Operator or maintainer reviews the patch
2. CI test suite runs (independent mechanism)
3. Both pass → operator may merge
```

**Pattern 3: deferring to a second agent**
```markdown
Claude wrote the migration. A second Claude session (or a different
reviewer) audits the migration before it runs in production. The
audit is a separate receipt with its own proposer/attestor fields.
```

## What the validator must NOT inherit from the proposer

- The proposer's framing of "this is good"
- The proposer's claim of completeness
- The proposer's verdict (the validator renders independently)
- The proposer's selection of which checks to run (the validator may
  add checks)

## When the same human is both proposer and operator

In small teams or solo work, the human operator often plays both
roles. The discipline still applies, but in time-separated form:

- The proposer-self drafts the work
- Time passes (a meal, a night's sleep, a session boundary)
- The validator-self re-reads with fresh eyes
- Admission requires the validator-self to actively assent, not just
  the absence of objection

Tools that enforce this: PR-based workflows, time-locked drafts,
explicit "review" steps in checklists.

## Anti-patterns

- **Self-merge** — author commits and merges in the same action. No
  separation, no second eye.
- **Inferred admission** — author writes "this is ready" and treats
  that as admission. Statement of completion ≠ admission.
- **Forced review** — proposer dictates what the validator must
  approve. The validator's independence is constitutive.
- **Composite role** — proposer wears a "reviewer" hat for a moment
  and admits their own work under the new role label. The hat doesn't
  matter; the actor identity does.

## How to satisfy this skill in solo work

When operating alone, use mechanism separation:

- Author code; run tests; tests are an independent mechanism
- Author a doc; have a linter or schema validator check it
- Author a decision; sleep on it; review the next day
- Author a proposal; run it through a second Claude session under a
  blank context

The separation can be temporal, mechanical, or fresh-context — but
must be **real**.

## Companion skills

- `no-receipt-no-claim` — receipts must name proposer and validator separately
- `halt-boundary` — if validator is sovereign and not yet engaged,
  declare a halt
- `doctrinal-diff` — diffing incoming external content against canon
  is a validator-class move; the diff author shouldn't also admit the
  result
