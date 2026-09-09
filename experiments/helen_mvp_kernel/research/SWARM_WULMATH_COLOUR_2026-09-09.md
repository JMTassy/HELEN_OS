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

## Non-deltas

Goblin 5 (prior art: KQML, FIPA-ACL, LLMLingua, emergent
communication) had not returned when this receipt was written; nothing
here reflects its findings. No claim above is a warrant. The entropy
test used one weak predictor; no stronger one was run. The seven-way
colour assignment remains a reading, and the v2 result above is
evidence against part of it.
