# Doctrinal Diff Before Bottling Skill

When external doctrine arrives (a framework, a proposal, a manifesto)
that **touches existing canon**, diff it before adopting it. Identify
what's restated, what's genuinely new, and what's out-of-scope. Bottle
only the new.

## When this skill applies

Fire this skill when:

- An operator pastes a framework, proposal, or doctrine into chat
- A teammate sends "we should adopt this" with a link to external
  content
- A vendor's documentation is being considered as architectural
  guidance
- A whitepaper's recommendations are being mapped to existing code

Do **not** fire if:
- The incoming content has zero overlap with existing canon
  (entirely new domain — diff is trivial)
- The content is reference material, not doctrine
- The decision to adopt has already been made and the diff would be
  performative

## Why this matters

External doctrine carries three risks:

1. **Restatement under new names.** The incoming framework names
   concepts that already exist in canon under different vocabulary.
   Adopting it creates parallel naming systems that compete with the
   canonical one.
2. **Scope creep via renaming.** A small genuine novelty buried in
   100 restated items pulls the whole framework in. The canon
   accumulates lookalike artifacts that no one knows are duplicates.
3. **Vocabulary contamination.** Even if the incoming framework is
   rejected, repeated discussion seeds its vocabulary into the
   project's discourse. Vocabulary drift over time becomes doctrine
   drift.

The diff intercepts all three.

## The procedure

### Step 1: Inventory the existing canon's surface

For the domain the incoming content touches, list every existing:

- Doctrine / proposal / spec
- Schema / data structure
- Tool / command / interface
- Invariant / rule / law
- Gate / check / validation

Use file paths and exact names. Vague references fail the diff.

### Step 2: Map each incoming claim to an existing canon item

For each claim in the incoming doctrine, classify as:

- **RESTATED** — already in canon under a different name. Same shape,
  different vocabulary. Do not bottle.
- **REFINED** — already in canon; the incoming version adds detail or
  precision. Consider amending the existing artifact rather than
  bottling a parallel one.
- **NEW** — genuinely not in canon. Bottle-worthy.
- **OUT-OF-SCOPE** — relevant to a different domain entirely. Do not
  bottle; redirect.

### Step 3: For NEW items, assess discipline pairing

Even genuine novelties have failure modes. For each NEW item:

- What rot does it bring with it? (Often: instrumentation gap, queue
  buildup, drift accumulation)
- What discipline addresses the rot?
- Is the discipline tractable now, or does it need a prerequisite?

A NEW item without a tractable paired discipline should be deferred,
not bottled.

### Step 4: Produce the diff artifact

The diff itself is the output — not yet the bottled doctrine. The diff
artifact:

- Lists every claim with its classification (RESTATED / REFINED / NEW
  / OUT-OF-SCOPE)
- Cites existing canon by exact file path / name for RESTATED and
  REFINED
- For each NEW item, names the paired discipline
- Recommends what to bottle, what to fold, what to reject

### Step 5: Bottle only the NEW (with paired disciplines)

If after the diff there are items worth bottling, bottle them as
separate small proposals — not as a wholesale adoption of the
incoming framework. Each bottle gets its own halt-boundary section.

## Reference pattern

**Diff artifact skeleton:**

```markdown
# <INCOMING_FRAMEWORK>_DIFF_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** ANALYSIS_DRAFT
**parent_input:** <source name and date>

## §1. Purpose
Audit, not adoption.

## §2. Layer-by-layer mapping
| Incoming claim | Existing canon | Status |
| --- | --- | --- |
| ... | ... | RESTATED / REFINED / NEW / OUT-OF-SCOPE |

## §3. What's already canonical (do not re-bottle)
- Item A — file path X
- Item B — file path Y
- ...

## §4. What's genuinely new (potentially adoptable)
- Item C — paired discipline D
- Item E — paired discipline F
- ...

## §5. Recommendation
Bottle: <subset>
Defer: <subset>
Reject: <subset>

## §6. Halt boundary
<who must rule on the recommendation>
```

## Anti-patterns

- **Wholesale adoption** — accept the incoming framework as-is. Creates
  doctrinal duplicates.
- **Wholesale rejection** — reject the incoming framework entirely.
  Misses genuine novelties buried in restatement.
- **Surface diff** — diff by titles only, without examining structural
  overlap. Restated content often uses fresh names for old concepts.
- **Diff under time pressure** — diff is itself work and needs the
  same discipline as any audit. A rushed diff misses restatements.
- **Diff without paired-discipline check** — adopting NEW items
  without their rot mitigations creates accumulating drift.

## Companion skills

- `proposer-validator` — diff author should not also admit the
  resulting bottles
- `no-receipt-no-claim` — the diff itself is a receipt
- `halt-boundary` — diff recommendations halt at sovereign ruling
