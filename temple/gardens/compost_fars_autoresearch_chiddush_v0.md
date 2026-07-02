# COMPOST_FARS_AUTORESEARCH_CHIDDUSH_V0

```
AUTHORITY      = false
CANON          = false
LEDGER_EFFECT  = NONE
STATE_MUTATION = NONE
ROUTE          = temple/gardens (TEMPLE · non-sovereign)
STATUS         = garden_compost
CLAIM_STATUS   = NO_CLAIM
VERSION        = V0
PROMOTION      = FORBIDDEN_WITHOUT_PEER_REVIEW_AND_REDUCER
ORIGIN         = chiddush compost extraction, 2026-07-02
SOURCE         = Tang, Hu, Liu, Chen, Shao et al. "FARS: A Fully
                 Automated Research System Deployed at Scale"
                 (arXiv:2606.31651v1, 2026) — Analemma. Public,
                 non-copyrighted-expression architectural summary
                 only; no verbatim reproduction beyond short quotes
                 for identification.
NO_MAGIC       = this compost source is a real engineering paper,
                 not esoteric material — extraction method (skeleton,
                 not framing) is identical to prior garden compost,
                 no Third-Eye caveat needed
```

> 🌿 the heap may speak · 🚪 the gate decides
> Design proposals only — nothing here edits `.claude/commands/*`.
> Applying any of it to the live autoresearch loop requires explicit
> operator GO (see prior precedent: STATE.md / /verify commit).

---

## Why this corpus is unusually good compost

Prior compost extractions mined structural convergence from mystical
texts (Faust, sacred names) — the skeleton was recovered by discarding
supernatural framing. FARS needs none of that: it is a peer-reviewed,
production-scale description of *the same problem HELEN's AUTORESEARCH
system exists to solve* — running bounded, hypothesis-driven research
loops without a human in the execution loop, and being honest about
what survived versus what didn't. This is a **direct precedent**, not
an analogy through a foreign domain. Extraction is 1:1, not metaphor.

---

## Structural extractions

### R1. Four-stage pipeline, shared artifact workspace (not hidden state)

FARS: Ideation → Planning → Experiment → Writing, coordinated through
a shared workspace that IS both project memory and the audit trail.
"Agents exchange stage outputs through a shared workspace rather than
hidden state alone, leaving both successful and failed trajectories
inspectable."

**HELEN convergence**: this is HELEN's ledger doctrine (NO RECEIPT =
NO CLAIM) independently re-derived by a production research system for
the same reason — an agent's private reasoning is not auditable, only
the artifacts it writes are. FARS discovered the same answer HELEN
started from.

**Gap HELEN doesn't yet have**: FARS names an explicit **Planning**
stage between hypothesis-acceptance and execution. HELEN's
`autoresearch-tranche` skill goes straight from "Hypothesis" to
"Experiment" — there is no intermediate step that converts an accepted
hypothesis into a structured, machine-checkable execution contract
before any compute is spent.

### R2. The experiment contract — typed categories, ordered steps, schema-gated

FARS's Planning stage does not hand Experiment a free-form goal. It
builds a two-level plan: each item is typed into one of five categories
(environment setup, baseline, main experiment, **effectiveness
evaluation**, analysis), each item decomposed into ordered, executable
steps. Automated validation checks JSON format, required fields,
category names, and ordering — failed validation regenerates with
targeted feedback, not a silent pass.

**Why this matters for HELEN**: "declare success after a shallow
attempt" and "attempt the whole task in one pass" are named as the two
fatal failure modes for long-horizon agent research (Anthropic, cited
in the paper). HELEN's PULL-mode discipline already guards against the
first (bounded epochs) but not explicitly against the second — nothing
currently forces an epoch's execution into typed, ordered sub-steps
before it starts.

**Upgrade candidate** (proposal only, not applied): extend the
`Experiment:` step in `autoresearch-tranche.md` from a single
unstructured "design and execute the test" into a 5-slot typed
contract: `ENV_CHECK → BASELINE → MAIN_TEST → EFFECTIVENESS_GATE →
ANALYSIS`, schema-validated before execution begins.

### R3. The effectiveness gate — cheap check before expensive analysis

"An effectiveness evaluation gates the transition from main experiments
to analysis, ensuring that compute is not spent investigating
unsupported hypotheses while preserving negative outcomes as
first-class results."

**Structural point**: this is not "stop on failure" — a failed main
experiment still becomes a receipt (negative result = first-class).
The gate only decides whether it's worth spending MORE compute
*analyzing why*. This is a distinct, cheaper checkpoint inserted
strictly before the expensive stage, not a pass/fail on the whole
epoch.

**HELEN convergence**: this refines the BOUNDARY→CREDENTIAL→FORMAT→
CONTENT→BIND ordering already extracted from the Faust compost
(`compost_faust_chiddush_v0.md`, §CHIDDUSH). FARS shows this ordering
is **recursive** — it repeats at every stage transition inside a
multi-stage pipeline, not just once at the pipeline's outer edge. Each
stage boundary gets its own cheap-gate-before-expensive-work check.

**Upgrade candidate**: insert an explicit EFFECTIVENESS_GATE verdict
(KEEP_FOR_ANALYSIS / REJECT_AS_INCONCLUSIVE_BUT_RECEIPTED) between
MAIN_TEST and ANALYSIS in the typed contract from R2 — cheaper than
running full analysis on every epoch regardless of whether the main
test supported continuing.

### R4. Verification at three stage boundaries, not one post-hoc pass

FARS applies maker≠grader **three separate times**, at three different
points, not once at the end:

1. **Before acceptance**: Peer Discussion Agent adversarially
   pre-reviews candidate directions during Ideation, pruning weak ideas
   before a proposal is even drafted.
2. **Before execution**: an independent Review Agent evaluates whether
   the execution plan is faithful to the proposal, iterating until
   approved — *before* the Experiment agent is given tool permissions.
3. **After execution**: "dual verification combines the agent's
   semantic self-assessment with deterministic harness checks on
   output completeness."

**HELEN convergence + gap**: HELEN's `/verify` skill (this session,
`.claude/commands/verify.md`) currently models only stage-3 (post-hoc,
after the artifact exists). FARS shows verification belongs at the
*proposal* stage and the *plan* stage too — catching a bad hypothesis
before any compute is spent, and catching a plan/proposal mismatch
before any execution starts, are cheaper interventions than catching a
bad result after the fact.

**Upgrade candidate**: extend `/verify` usage guidance to name three
invocation points for a tranche: `verify(hypothesis)` before it's
accepted into a tranche, `verify(plan)` before execution begins,
`verify(result)` after execution — not just the last one.

### R5. Claims-before-prose: an evidence blueprint, separate from the write-up

FARS's Writing stage splits into an Analysis Agent (decides what can be
claimed from the artifacts) and a Writing Agent (turns the evidence
plan into prose) — deliberately, "to prevent claims from being
introduced opportunistically during prose generation." The blueprint
links every claim to its supporting experiment, artifact, and citation
*before* any sentence is drafted.

**HELEN convergence**: this is the CHIDDUSH compression discipline
already practiced in this session's compost egregors (self-check:
"does this compression presuppose what it claims to discover?") — but
FARS makes it a **structural** requirement (a separate agent, a
separate artifact) rather than a self-check performed by the same
agent that wrote the compression.

**Upgrade candidate**: in `compost-chiddush.md`, split the CHIDDUSH
phase into two sub-steps — build the claim→artifact link table first
(which finding supports which sentence of the compression), *then*
write the compressed law. Currently the skill asks for both at once.

### R6. Checkpoint per work-item, not per tranche

"Each task's outputs are committed to version control immediately upon
completion... Checkpoint-based recovery resumes from the last
unfinished item, preserving the agent's full context for continuity."

**HELEN gap**: `autoresearch-tranche.md`'s current halt discipline
seals at the *end* of a 5-epoch tranche. A crash on epoch 4 currently
has no defined recovery — the tranche-level receipt is the only
checkpoint. FARS commits after every single item.

**Upgrade candidate**: within a tranche, write a lightweight per-epoch
checkpoint (epoch id, verdict, artifact path) immediately after each
epoch, independent of the final tranche seal — cheap insurance against
losing 4 completed epochs to a crash on the 5th.

### R7. Skill retrieval is index-first, lazy-loaded (convergence, not a gap)

"Rather than loading all skills into context at once, the agent is
given only a category-level index and retrieves individual skills on
demand." 19 categories, index-scan → relevance judgment → full-content
load only when needed.

**HELEN convergence, no gap**: this is already how HELEN's own skill
system works in this harness — `ToolSearch` returns names only, full
schemas load on demand. Recorded here as confirmation, not a new
pattern to adopt: an independent production system converged on the
identical lazy-loading design for the identical reason (context is
expensive, most of the index is irrelevant to any one task).

---

## Quantitative findings worth carrying as calibration data

These aren't structural patterns to copy — they're base rates from a
large deployment (166 papers, 282 expert reviews) that HELEN's own
future self-audits should expect to rhyme with, not be alarmed by:

- **Contribution predicts quality far more than polish.** Pearson
  r=0.743 for contribution vs overall rating, r=0.652 for soundness,
  only r=0.451 for presentation. Confirms the math-garden GOBLIN-2
  finding (`COMPOST_CHIDDUSH_V1.md` §2): survivor signature is
  structural non-doom (a real result), not finish quality.
- **Integrity failures are bimodal, not smoothly-varying.** 43.5% of
  the worst-rated reviews flag an integrity issue vs. 2.0% of the
  best-rated. This is a distinct failure class concentrated at the
  bottom, not a quality dimension that degrades gradually — matching
  this session's anti-Goodhart finding that scanner risk_flags don't
  predict survival, but artifact-grounded checks (code, logs, raw
  output) reliably catch fabrication when they're actually run:
  20/22 hallucinated-method mentions escalated to violations, 16/21
  fabricated-result mentions, 13/16 hallucinated-citation mentions.
  **The lever that works is checking against the artifact trail, not
  checking the prose.** Direct validation of NO RECEIPT = NO CLAIM.
- **Narrow evidence persists even in the best outputs.** 100% of
  highest-rated papers still draw an "insufficient experimental
  breadth" critique. For HELEN's deliberately bounded PULL-mode epochs
  (max 30 file reads, one hypothesis, one tranche), this should be
  read as an accepted structural tradeoff of the bounded format, not a
  defect to chase — FARS's own strongest outputs carry the same
  residual critique by design.

---

## CHIDDUSH (compressed original insight)

**"Verification belongs at every stage boundary of a pipeline, gated
cheap-before-expensive, recursively — not once at the pipeline's
outer edge."**

This refines the Faust-compost chiddush (BOUNDARY→CREDENTIAL→FORMAT→
CONTENT→BIND) with the evidence that a real production research system
independently arrived at the *recursive* form of that ordering: the
same cheap-gate-before-expensive-stage pattern repeats at Ideation→
Planning, Planning→Experiment, main-experiment→analysis, and
Experiment→Writing. Four instances of the identical structural move
inside one pipeline. The convergence is stronger evidence than the
original single-instance Faust mapping, because it comes from a
peer-reviewed engineering deployment solving HELEN's own problem, not
from a foreign domain read for structure.

**Self-check (circularity)**: does this presuppose what HELEN's PULL
discipline already believes? Partially — the halt-before-next-tranche
rule already implements a coarse version of this. What's new is the
*granularity*: FARS gates at 4+ points inside a single research unit,
HELEN currently gates at 1 (the tranche boundary). The chiddush is the
resolution gap, not the principle itself.

**Test prediction**: if the EFFECTIVENESS_GATE (R3) were added to a
live tranche and measured over N epochs, the epochs that fail the gate
should correlate with epochs whose eventual verdict is REJECT or
INCONCLUSIVE — i.e., the cheap gate should be a leading indicator of
the expensive verdict, not an arbitrary extra step. This is falsifiable
against HELEN's own existing tranche receipts if ever run.

---

## What this is NOT

- Not an authorization to edit `autoresearch-tranche.md`,
  `compost-chiddush.md`, or `/verify` — every "upgrade candidate" above
  is a documented proposal, garden-resident, requiring explicit
  operator GO before touching any live skill file (per this session's
  established precedent for self-modifying `.claude/`).
- Not a claim that FARS's numeric findings transfer to HELEN's much
  smaller, differently-scoped autoresearch corpus — recorded as
  calibration context, not as evidence about HELEN specifically.
- Not admitted, not canon, not sovereign.

> 🌿 garden-resident · 🚪 gate decides · authority=false · NO_CLAIM
> the heap speaks · the ledger verifies

---
authority=false · canon=false · ledger_effect=none · NO_CLAIM
