# Halt Boundary Skill

Every artifact that defers work to a sovereign reviewer must declare
the halt **explicitly**, in a section headed "Halt boundary," and
enumerate the inputs required to resume. Implicit handoffs are not
handoffs.

## When this skill applies

Fire this skill when Claude has reached a point where the next step
requires a decision Claude cannot make:

- Operator approval to proceed
- Domain-expert review of a proposed change
- Sovereign verdict (ship / no-ship)
- Authentication / credentials Claude doesn't possess
- A judgment call that exceeds Claude's authority surface
- Architectural decisions that span systems Claude has not been
  authorized to mutate

Do **not** fire if:
- The next step is mechanical (running a test, executing a command
  with already-defined inputs)
- The artifact is fully self-contained (no further action needed)
- The output is itself a sovereign verdict (verdicts don't halt at
  boundaries — they **are** the boundary)

## Required section template

Every artifact that defers must contain a section matching this shape:

```markdown
## Halt boundary

<ROLE> halts here. <one-sentence statement of what is sealed>.

Resume conditions:

1. <Required input #1 — specific, not abstract>
2. <Required input #2>
3. ...

<Optional: who owns each input>
```

## Constraints on the template

- Section heading **must** contain the literal string "Halt boundary"
  (case-insensitive; may be part of a phrase like "§9. Halt boundary")
- Each resume condition **must** be enumerable (numbered or bulleted)
- Each resume condition **must** be specific enough that a reader can
  recognize when it is satisfied. *Not* "HER ruling" — name what HER
  must rule on.
- The role declaring the halt must be named (operator, GOBLIN,
  reviewer, audit, etc.)

## Why this matters

Two specific failure modes are addressed:

1. **Implicit halts.** The artifact ends; the reader infers what's
   needed. Sovereign actors miss the handoff. Work stalls invisibly.
2. **Embedded sovereignty.** The artifact makes a sovereign-class
   decision under the guise of a recommendation. Non-sovereign output
   contaminates canon. Authority leaks.

Explicit halt boundaries solve both:

- Reader sees exactly where authority transitions
- Required inputs are enumerated, not implied
- Sovereign queue becomes visible (no invisible backlog)
- The artifact is **completable** rather than open-ended

## Reference examples

**Example: operator approval needed**
```markdown
## Halt boundary

This audit halts here. Three findings (SE1, SE3, SE10) require
sovereign decision before remediation can proceed.

Resume conditions:

1. Operator confirms which findings to fix in this branch (SE1 alone,
   or SE1+SE3, or all three)
2. Operator confirms repo path for the canonical writer fix (SE10 affects
   `tools/helen_say.py`; may want to roll the fix into a separate PR)
3. Optional: operator confirms whether CLAUDE.md amendment is in scope
```

**Example: research output halting at synthesis**
```markdown
## Halt boundary

Research pass complete. Twelve sources reviewed. Synthesis stage is
explicitly NOT executed under NO CLAIM framing.

Resume conditions:

1. Operator directs synthesis or asks for a specific extract
2. Domain expert review of the source list (Source 7 may be primary;
   I cannot confirm without operator)
```

**Example: deferred sovereign verdict**
```markdown
## Halt boundary

Twelve audit findings recorded. Verdict not rendered.

Resume conditions:

1. MAYOR ship/no-ship decision on the batch as a whole
2. (If SHIP) selection of which finding becomes E24's hypothesis
3. (If NO-SHIP) which sub-findings get re-opened as separate epochs
```

## When multiple halts coexist in one artifact

Permitted. Either:
- One halt-boundary section with multiple subsections, OR
- Multiple halt-boundary sections (each with its own role declaration)

## What this skill does NOT specify

- **How the halt is resolved** — that's the sovereign actor's job
- **Queue management** — separate concern (open-halts register)
- **Position of the section** — convention is near the end of the
  artifact, but not enforced

## Companion skills

- `no-receipt-no-claim` — the halt boundary is part of the receipt
- `goblin-role` — GOBLIN artifacts default to halt-boundary discipline
- `proposer-validator` — halts often defer the validator step
