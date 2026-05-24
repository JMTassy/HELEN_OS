# /helen-governance:halt

Emit a "Halt boundary" section template for when current work defers
to a sovereign reviewer. Honors the `halt-boundary` discipline.

## Usage

```
/helen-governance:halt <one-line description of what's being sealed>
```

## What this command does

Produces a `## Halt boundary` section ready to paste into the current
artifact. The section is filled with:

- Role declaration (the role of whoever is halting — defaults to
  GOBLIN if unspecified)
- A one-sentence "sealed statement" of what work is complete
- An enumerated list of resume conditions, populated based on the
  conversation context

Claude examines the recent conversation to identify what specifically
is being deferred and to whom, then drafts specific resume conditions
(not vague ones like "operator ruling").

## Template

```markdown
## Halt boundary

<ROLE> halts here. <one-sentence statement of what is sealed>.

Resume conditions:

1. <Specific input or decision #1>
2. <Specific input or decision #2>
3. ...

<Optional: role-owner of each input if not obvious>
```

## Quality checklist

A good halt-boundary section satisfies:

- [ ] Section heading literally contains "Halt boundary"
- [ ] Role is named (operator, GOBLIN, audit, reviewer, etc.)
- [ ] Each resume condition is specific — a reader can recognize when
      it is satisfied
- [ ] No condition reads as just "approval" — each names what is being
      approved
- [ ] Optional: ownership is attributed for non-obvious cases

## Anti-patterns the command refuses to produce

- "Resume conditions: HER ruling" (vague — name what HER must rule on)
- "Resume conditions: continue when ready" (no specificity)
- "Resume conditions: as appropriate" (no exit criterion)

## When to use this command vs. inline halt sections

Use the command when:
- Starting from scratch on an artifact's halt section
- The conversation has been long and you need a focused recap of what
  needs to defer

Skip the command when:
- The halt is trivially obvious from context (one-line halt suffices)
- The artifact format doesn't support markdown sections (use the
  equivalent structured field in JSON / YAML)

## See also

- `halt-boundary` skill (the discipline this command supports)
- `/helen-governance:receipt` (the parent receipt often contains the
  halt section)
- `goblin-role` skill (GOBLIN artifacts default to including halt
  boundaries)
