# Goblin swarm — coloured WULmath AI-to-AI compression

Seven goblins, one per vibration, on the question of a coloured
WULmath compression language for agent-to-agent exchange.

**The swarm was NOT gemma4.** No ollama binary, no `~/.ollama/models`,
port 11434 silent in this container. The goblins are Claude subagents.
Recorded here because a swarm's provenance is part of its result.

Law 103 governs the output: *goblins multiply hypotheses; only
warrants move the frontier.* Everything below is a HYPOTHESIS unless
marked MEASURED.

---

## MEASURED — the colour axis is not lexically recoverable

Goblin 1 restated `no_state_by_color_alone` as an entropy equation:
the law says `H(colour | mono_text) = 0`, maximum compression wants
that term **maximal**. The brief is literally *maximise X subject to
X = 0*. It then proposed the cheap falsifier: predict colour from
text; if it succeeds, the axis is decoration.

Executed on the real 108-line corpus (`entropy_test.py`), multinomial
naive Bayes, leave-one-out, nothing fitted on the row it scores:

| | |
|---|---|
| chance (7 classes) | 0.1429 |
| majority baseline | 0.2037 |
| **LOO accuracy** | **0.3611** (39/108) |
| H(colour) prior | 2.744 bits |
| Fano bound on H(colour \| text) | ≤ 2.596 bits |

**Neither branch of the falsifier fired.** 36% is 2.5× chance, so the
assignment is not arbitrary; but 64% error means a bag-of-words
predictor recovers almost none of the 2.744 bits.

**Read this as a lower bound on recoverability, not an upper bound.**
Naive Bayes over 108 rows and 7 classes is a weak instrument, and the
colours were assigned by reading each law's *meaning* — something a
lexical model cannot do. The honest conclusion is narrow: **the
strongest form of "colour is trivially recoverable by lexical means"
is refuted, and nothing else is settled.** A stronger predictor (an
LLM reading the law) is the next instrument and has not been run.

### A finding against my own compression

Per-class recall: v5 10/22, v7 11/21, v1 7/15, v4 4/13, v3 3/13,
v6 3/16, **v2 1/8**.

Vibration 2 (`orange_earth`, flow/creation) is the least recoverable
of my own assignments by a wide margin. That is not a fact about
colour; it is evidence that **my v2 assignment is the least
principled one in the compression** — the eight laws I filed under
flow/creation share no lexical signature, which usually means they
share no real function either.

---

## CAUGHT — a drifted line in the published plate

Goblin 4 (adversarial) and Goblin 6 (algebraic) independently attacked
the chain notation. Note this is **convergence, not corroboration**:
both had the same example line in their brief, so they share one root.

They were right, and the defect is mine.

- **Source** (probe 107): *"Retain !=> Admit **and** Retain !=>
  Authorize"* — both non-entailments have `Retain` on the left.
- **What I published**: `Retain ⊬ Admit ⊬ Authorize` — which under any
  adjacent-conjunctive reading asserts `(Retain ⊬ Admit) ∧ (Admit ⊬
  Authorize)`. Different claim.
- **Fixed to**: `Retain ⊬ Admit · Retain ⊬ Authorize`.

`⊬` is the complement of a preorder and is **not transitive**, so a
bare infix chain invites the unsound reading `a ⊬ c`. The plate now
carries an explicit chain rule in the masthead: `a ⊬ b ⊬ c` means
`(a⊬b) ∧ (b⊬c)` and never `(a⊬c)`; `⊊`/`⊋` chains ARE transitive and
stay legal.

This is exactly the non-delta the compression receipt already
declared — lines checked against probe *names*, not probe *bodies*.
The declared hole was real and something fell through it on the first
pass.

---

## Surviving hypotheses worth a warrant

Ranked by how cheaply they could be tested next.

1. **Guards are the compression** (G3). If an illegal sequence is
   *inexpressible at the transmitter* rather than rejected at the
   receiver, the saving is the guards you never write. The 108 laws
   *are* guards, so this is directly on-target.
   TEST: is the legal-sequence language regular? If legality depends
   on unbounded history ("authority may rise only if an earlier
   admission is unspent") no finite automaton enforces it.
2. **Refusal-sets are freely consistent; assertion-sets are not**
   (G2). Any set of pure prohibitions is satisfiable — the do-nothing
   system satisfies all — so merging two governed agents is set union
   with no satisfiability witness to ship. Claimed as the one
   asymmetry that is not an accounting trick.
   TEST: **already looks dead.** Probe 053 `liveness_is_a_distinct_axis`
   and probe 031 `hold_is_not_deadlock` are duty lines. G2 named its
   own killer: "if HELEN's 108 already contain a liveness line, this
   idea is dead on arrival." They do.
3. **Two mixed derivation rules for negative facts** (G6):
   `(a ⊢ b) ∧ (a ⊬ c) ⟹ (b ⊬ c)` and `(b ⊢ c) ∧ (a ⊬ c) ⟹ (a ⊬ b)`.
   If they close, the transmitted set is a generating basis, not 108.
   TEST: run the closure over the corpus. If reduction < 10%, the 108
   are independent and there is nothing to generate.
4. **The effect triple needs its OWN axis** (mine, against G3's #1).
   G3 proposed making the hue *be* `(dP,dA,dE)` on three bits. Law 069
   `palette_is_factored_never_replaced` refuses that — the palette is
   frozen and *"rival concepts live on an orthogonal marker axis."*
   Two channels, not one overloaded one.
5. **Colour as running parity** (G1 #5): `colour(n) = h(line n-1,
   line n) mod 7` makes `H(colour|text) = 0` by construction, so the
   law holds outright, and buys detection of the real LLM-pipeline
   failure — dropped and reordered lines, caught with p = 6/7.
   Redundancy that purchases integrity at zero payload.
6. **Never compress the ledger** (G4). Compress the working channel;
   never the refusal notice, the ledger, or the incident
   reconstruction — those are read adversarially, later, by someone
   who does not hold the codebook. A governance artifact readable only
   by holders of the compression prior has moved the audit from *the
   governed* to *the initiated*.

## The most serious attack, unresolved

G4 attack 1 — **silent vacuity**. "A control that cannot fail reports
nothing when it passes" means silence has two preimages: the control
held, or the control was compressed into meaninglessness. A drifted
line and a healthy line emit the identical null.

This is the same defect probe 108 was written for, one level up: it
now applies to the *compression* rather than to a counter. The
answer is the same answer — **injected sacrificial violations** — and
it has not been built for the plate.

---

## REPORTED_EXTERNAL — Goblin 5's grounding, and it reframes the goal

Graded REPORTED_EXTERNAL: the goblin's own note says arxiv.org and
huggingface.co were **blocked by this session's egress proxy**, so
every item is a search-snippet confirmation of a real title/ID/venue,
not a full-text read. I have not re-derived any of it. Treat titles as
pointers to check, not as read sources.

### What is already solved — reuse, do not invent

- **Colour as a type channel is 45 years old.** Coloured Petri Nets
  (Jensen, 1980; CACM 2015). Tokens carry colour *sets* drawn from
  type theory, statically checkable, with tool support. And CPN
  already reached our own conclusion independently: colour is
  redundant encoding, the type must exist in the text too or it is
  lost to grep, diff and colour-blind readers. Our
  `no_state_by_color_alone` is CPN's discipline rediscovered.
- **`Mint(κ) ⊢ UseCount(κ) ≤ 1` is literally linearity.** Linear
  logic (Girard 1987), linear/affine types. Written as a linear
  judgment, a type checker enforces it; written as an arithmetic side
  condition — which is what we did — the enforcement is thrown away.
- **Authority separation has a formal home**: Abadi's `says` modality,
  ABLP, Binder, SecPAL. Proof theory and decision procedures exist.
  `the_grantor_may_not_be_the_grantee` is a delegation statement in a
  logic that already has a checker.
- **The bandwidth fight is already lost.** KV-cache channels —
  DroidSpeak (arXiv 2411.02820), Cache-to-Cache (arXiv 2510.03215) —
  pass semantics between models without text at all. No symbolic
  notation competes on tokens per second. **The only defensible ground
  for coloured WULmath is that those channels are unreadable by
  humans and this one is not.**

### The deepest critique: `⊬` has no theory attached

From non-monotonic logic (Reiter's default logic 1980, the
closed-world assumption, negation as failure): *"not derivable"* is a
proof-theoretic notion **relative to a fixed theory Γ and a named
inference relation.** `A ⊬ B` with neither specified is not a
proposition.

All 108 of our lines are in that state. We never name Γ.

This is our own law 082 turned on the plate:
`receipt_text_is_not_a_rederivable_receipt` — *"an untyped hex may not
be verified as anything; an unrun recipe leaves the claim
FABRICATED_UNTIL_WITNESSED."* **The constitution already contains the
refusal of its own compression.** The plate is receipt text without a
re-derivable receipt.

### The lesson from the 1990s, which is the whole verdict

KQML failed not because it was verbose but because its performatives
had **no agreed semantics**: two agents could exchange a well-formed
message, act on different meanings, and nothing in the language could
detect the divergence. FIPA-ACL's fix grounded meaning in the sender's
*mental state*, which a receiver can never verify.

> *A compressed notation's value is entirely in its verification
> procedure, and zero in its density.*

By that standard our plate is currently a KQML performative. It
becomes real only when we can state mechanically which Γ the `⊬` is
relative to, what inference relation is denied, and what check a
receiving agent runs to confirm it read the line as written.

**Ship the checker before the notation.** 108 lines is exactly the
scale at which silent disagreement is invisible.

Independent confirmation of the chain defect: the same goblin flagged
`A ⊬ B ⊬ C` as ill-formed *"before anything else"*, from the
non-monotonic-logic literature rather than from our brief. The
observation shares a root with goblins 4 and 6 (all three had the line
in front of them); the **justification** does not — that one comes
from outside.

### The one genuinely open slot

A 2026 survey of agent interoperability protocols (reported as arXiv
2606.31498) finds **voting and dissent preservation universally absent**
across MCP, A2A, ACP, ANP and ERC-8004 on a six-dimension governance
taxonomy. A notation whose primitives are admit / deny / hold / dissent
targets a documented, currently empty slot.

Not novel, and not to be claimed: compressed AI-to-AI language, colour
as type, symbolic permission operators, agents developing their own
code, high compression ratios.

---

## Revised next step

Not "compress further". **Attach a theory and write the checker.**

1. Name Γ per line — which theory each `⊬` is relative to.
2. Re-express the lines that already have formal homes in those
   homes: linearity for `Mint(κ)`, an authorization logic for the
   grantor/grantee family.
3. Then the checker, and only then the notation.

## Non-deltas

No claim above is a warrant. Goblin 5's citations are REPORTED_EXTERNAL
and unverified by me — arXiv was unreachable from this session. The
entropy test used one weak predictor; no stronger one was run. The
seven-way colour assignment remains a reading, and the v2 result above
is evidence against part of it. No checker exists; no Γ has been named
for any of the 108 lines.
