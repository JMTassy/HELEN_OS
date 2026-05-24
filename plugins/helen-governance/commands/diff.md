# /helen-governance:diff

Perform a doctrinal diff between an incoming proposal/framework and
existing canon. Honors the `doctrinal-diff` skill.

## Usage

```
/helen-governance:diff <source description or paste>
```

## What this command does

Runs the five-step doctrinal-diff procedure:

1. **Inventory** the existing canon's surface in the domain the
   incoming content touches (uses Read / Grep tools on the current
   repository)
2. **Map** each incoming claim to an existing canon item, classifying
   as RESTATED / REFINED / NEW / OUT-OF-SCOPE
3. **Pair-check** each NEW item against its required discipline (does
   the incoming framework's new contribution carry a known rot, and
   is there a tractable mitigation?)
4. **Produce** a diff artifact (the diff is the output, not yet the
   bottled doctrine)
5. **Recommend** what to bottle / fold / defer / reject

## Output format

The command produces a single markdown artifact with this structure:

```markdown
# <INCOMING_FRAMEWORK>_DIFF_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** ANALYSIS_DRAFT
**parent_input:** <source description>

## §1. Purpose
## §2. Layer-by-layer mapping
## §3. What's already canonical
## §4. What's genuinely new
## §5. What's out of scope
## §6. Recommendation
## §7. Halt boundary
```

## What this command does NOT do

- Does NOT bottle any of the recommended items (separate sovereign
  step)
- Does NOT modify the canon (audit-only)
- Does NOT mark the incoming framework as rejected or accepted (only
  the operator / sovereign can do that)
- Does NOT skip the inventory step — a diff without inventory is
  unreliable

## When this command earns its cost

This command is more expensive than other governance commands because
inventory is real work (Read / Grep across the repo). Use it when:

- The incoming content is substantial (≥ 1 page of doctrine)
- The incoming content claims to introduce a "framework" or "system"
- The risk of accidentally re-bottling existing canon is real
- An operator is considering wholesale adoption and you want to
  surface what's actually new

Skip for:
- Small incoming proposals (one claim, easy to inspect by eye)
- Reference material (technical specs, API docs, etc.)
- Already-accepted content (the decision has been made)

## See also

- `doctrinal-diff` skill (the discipline this command supports)
- `proposer-validator` skill (diff author shouldn't also admit
  resulting bottles)
- `/helen-governance:halt` (the diff's halt section calls out what
  the sovereign must rule on)
