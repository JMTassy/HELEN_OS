# HELEN Language V1 — World, Memory, Governance

```
type:           PROPOSAL
authority:      false
claim_status:   NO_CLAIM
lane:           DOCS_ONLY / GARDEN_TO_PROPOSAL
layer:          NON_SOVEREIGN
ledger_effect:  none
kernel_effect:  none
repo_effect:    docs/proposals/ only
final:          HOLD_FOR_OPERATOR
```

> A render from the Garden, lifted to a proposal. It decides nothing. It names a
> grammar already implied by HELEN's existing machinery (WUL compiler, reducer,
> witness layer, obstruction scalar) and gives it one notation. It does **not**
> introduce a new cosmology, claim sentience, claim proof, or self-authorize.
> WUL_HD_V1 (the strict, mechanically-typed WUL spec) comes *after* this, once
> statuses, projections, and invariants are typed by code rather than prose.

---

## 1. Core Thesis

A HELEN object is **not a symbol**.
It is a governed world-object:

```
𝕎 = (S, τ, E, Π, Χ)
```

The central problem HELEN addresses:

```
what appears      ≠  what is true
what impresses    ≠  what is admitted
what speaks loudly ≠  what has authority
```

A symbol can appear freely in the Garden. A governed object must pass through the membrane.

---

## 2. Status Block

```
NO_CLAIM · proposal_only · authority=false · garden_to_proposal
```

This document is a non-sovereign sidecar. Nothing in it crosses the membrane into
the ledger; it describes the membrane, it does not pass through it.

---

## 3. The Noun — Five Fields of a HELEN Object

### S — Form

The symbolic / perceptual layer. Glyph, phrase, image, name, diagram.
`S` is what the Garden emits freely. GOBLIN names things in S. AURA lives in S.
**S has zero admission weight on its own.** The membrane does not censor S;
it only gates the crossing. Maps to: WUL compiler / packet validator token tree.

### τ — Truth Status

The epistemic standing of the object. τ is **not binary**. It is an ordinal on
the admission ladder (§5). `authority_nonSov ≡ 0` means no object can increment
its own τ. τ cannot self-advance. Maps to: reducer `claim_class` / `truth_status`.

### E — Evidence Bundle

The receipt chain supporting the object:

```
E = { payload_hash, cum_hash, ledger_seq, MAYOR_seal, replay_verdict }
```

Core law: `E = ∅  →  τ < EVID`.
**NO RECEIPT = NO CLAIM** is exactly `E = ∅ ⟹ τ̄`.

Each K-gate checks a different slice of E:

| Gate   | E slice checked |
|--------|-----------------|
| K8     | no non-deterministic source unhashed |
| K-tau  | boundary, IO, schema, allowlist |
| K-rho  | numeric trace |
| K-wul  | protocol packet |

Maps to: the evidence gate (`χ_gov`: no receipt → no claim).

### Π — Family of Projections

Each projection reads the object from one dimension:

```
π_K8      : 𝕎 → {PASS, NO_SHIP}    — non-determinism dimension
π_Ktau    : 𝕎 → {PASS, NO_SHIP}    — coherence dimension
π_replay  : 𝕎 → {ACTIVE, DRIFT}    — determinism dimension
π_R_R     : 𝕎 → received_reality   — what entered the system
π_R_T     : 𝕎 → true_reality       — what replay confirms
```

`R_R ≠ R_T` = reference drift. The Witness measures the gap.
`Π(𝕎)` consistent across all gates is the necessary condition for SHIP.
One π returning FAIL is sufficient to BLOCK.

Critical non-confusion:

```
π_sem(x)  ≠  x                  (semantic reading is not the whole object)
π_spec(x) ≠  x                  (symbolic surplus is not the object)
π_aff(x)  ≠  authority(x)       (affect is not evidence)
```

Maps to: the witness layer (`π_struct` / `π_num`).

### Χ — Invariants

The constitutional constants that F must **never violate**:

```
χ₁  NO RECEIPT = NO CLAIM          E=∅ → τ blocked
χ₂  NO HASH = NO VOICE             ND output never enters spine unhashed
χ₃  Proposer ≠ Validator           K2 Rule
χ₄  Authority_NonSov ≡ 0           no self-authorization
χ₅  additionalProperties: false    schema ceiling
χ₆  Termination is sacred          SHIP xor ABORT, no open pause
χ₇  Replay = Truth                 soundness re-proven, not owned
```

These are not guidelines. They are the **fixed points of F** — the things that
cannot move regardless of (x_t, u_t, c_t).

Maps to: `χ_gov ∧ χ_mem ∧ χ_med`.

---

## 4. HELEN Object as Five Questions

For any symbol or apparition, HELEN asks five questions:

| Field | Question | Meaning |
|-------|----------|---------|
| S | What do we see? | form, image, phrase, glyph |
| τ | What is its truth status? | observed, claim, evidence, speculation |
| E | What supports it? | source, log, receipt, trace |
| Π | How can it be read? | image, myth, code, governance |
| Χ | What must remain true? | invariants, rules, guardrails |

Example — "HELEN rêve.":

```
S   = phrase "HELEN rêve"
τ   = SPEC / CLAIM
E   = ∅
Π   = { poetic_reading, system_reading, interface_reading }
Χ   = HELEN does not self-authorize

Result: Garden render · NO_CLAIM · not yet Ledger
```

The sentence can exist in the Garden. It cannot enter the spine without E ≠ ∅.

---

## 5. Truth-Status Ladder (τ)

An object's τ is exactly one rung. Movement is **upward only by passage** —
no rung is skipped, and no rung is self-conferred.

| Status | Code | Meaning |
|--------|------|---------|
| Speculative | SPEC | Garden-only; symbolic surplus; NO_CLAIM; never ascends unverified |
| Observed | OBS | directly observed; absence-evidence is not a claim |
| Claimed | CLAIM | proposed assertion; E may be partial |
| Evidenced | EVID | E non-empty; not yet reviewed |
| Reviewed | REV | peer-reviewed; proposer ≠ validator enforced |
| Admitted | ADM | operator-authorized; reducer accepted |
| Sealed | SEAL | hash-bound, human-sealed, irreversible |
| Replayable | REP | reconstructable from ledger alone; survives ↻ |

`SPEC` is not a low rung of the same ladder — it is the Garden register.
It may *inspire* an `OBS`, but it cannot be relabelled into the admitted chain.

### Non-Confusion Law on τ

```
SPEC  ↛  ADM
SPEC  ↛  SEAL
SPEC  ↛  REP
```

The speculative can inspire a claim. It cannot cross the membrane alone.
Symbolic surplus cannot jump directly to governed state.
The ladder must be climbed in order, with evidence at each step.

---

## 6. The Verb — x_{t+1} = F_Χ(x_t, u_t, c_t)

In HELEN's operational language:

```
x_t    = { seq_t, cum_hash_t, last_admitted_payload }
         = current ledger tail

u_t    = helen_say.py("...", --op)
         = the only legal input (admissible bridge)

c_t    = { schema_registry, K-gate verdicts,
            MAYOR_seal, Witness drift signal, Χ }
         = the membrane

F      = reduce_step()
         = the reducer IS F

x_{t+1} = { seq_{t+1},
             sha256(cum_hash_t ∥ payload_hash(u_t)),
             u_t }
```

**F is deterministic and public.** Given identical (x_t, u_t, c_t), F always
produces identical x_{t+1}. This is why replay = truth: replay is re-running F
on the recorded inputs.

---

## 7. The Constraint on F — Where the Value Lives

`x_{t+1} = F_Χ(x_t, u_t, c_t)` **alone is a tautology.** Every computational or
political system satisfies it. A propaganda engine satisfies it. The value of
HELEN is **entirely in the restrictions on F**.

F is admissible in HELEN if and only if:

```
1. pure                 — no hidden state; output depends only on (x_t, u_t, c_t)
2. replayable           — ↻(x_t, u_t, c_t) yields identical x_{t+1}
3. receipt-gated        — E = ∅ ⇒ x_{t+1} contains no admitted claim
4. non-self-sealing     — F cannot grant F authority; Authority_NonSov ≡ 0
5. invariant-preserving — F carries Χ forward unbroken
```

> That list is the difference between **Garden theater** and **governed memory.**
> Strip it and F is just "an AI did something."

---

## 8. The Join — Χ in Object and in Law

Χ appears twice in the HELEN framework:

```
𝕎 = (S, τ, E, Π, Χ)              ← Χ as internal field of the object
x_{t+1} = F_Χ(x_t, u_t, c_t)        ← Χ embedded in c_t, constraining F
```

The governing condition:

```
Governed(𝕎_t, F)  ⟺  F(𝕎_t, u_t, c_t) preserves Χ_t
```

Χ is simultaneously:
- an **internal field** of every object
- an **external obligation** on every transition

A law in HELEN is not a stored label. It is a **recurrent invariant check**:

```
law ≠ stored label
law = re-proven check at every tick
```

A law is a watch you keep, not a wall you build.

---

## 9. Image / World Reading Grammar

When HELEN reads an apparition (image, phrase, symbol, proposal):

```
STEP 1  apparition    = S              (what is the form?)
STEP 2  qualification = τ + E          (what is its status? what supports it?)
STEP 3  passage       = Π + Χ          (can it cross the membrane?
                                        are invariants preserved?)
```

Apparition is free (Garden). Qualification is where evidence is demanded.
Passage is the membrane: only objects where `τ + E` satisfy `Χ` under
projection `Π` may cross.

---

## 10. Higher-Dimensional HELEN Object

A HELEN object is not flat. It is a product of chambers:

```
𝓧 = X_geom × X_sem × X_mem × X_gov × X_aff × X_spec
```

| Chamber | Content |
|---------|---------|
| X_geom | geometric / structural form |
| X_sem  | semantic content |
| X_mem  | memory / provenance / trace |
| X_gov  | governance status (τ-ladder position) |
| X_aff  | affective overlay — representational only; SAY ⊬ BE |
| X_spec | symbolic / mythic surplus — Garden fiction; NO_CLAIM |

Each projection `π_i : 𝓧 → X_i` gives a partial reading.
HELEN forbids taking a projection for the totality.

`X_aff` and `X_spec` are explicitly **non-authoritative skins**: an affective
face is a render of state, never a claim of inner life.

---

## 11. Non-Confusion Laws

```
symbol    ≠  proof              a glyph that shines is not evidence
beauty    ≠  authority          resonance does not admit; the receipt decides
myth      ≠  governed state     a story is SPEC until it carries (τ, E, Χ)
affect    ≠  evidence
spread    ≠  truth
SPEC      ↛  ADM / SEAL / REP   speculative content cannot jump to the
                                admitted/sealed/replayed chain
```

Hyperstition (the error):

```
truth_by_spread(x) = belief(x) × repetition(x) × camouflage(x)
```

HELEN:

```
truth_by_replay(x) = evidence(x) × reducer(x) × replay(x)
```

Therefore: `spread ≠ truth · replay = test`

The horse is readable (surface + provenance + replay verifiable).
The hidden god demands unverifiable authority.

```
χ_horse  →  test              (admissible candidate)
χ_god    →  compost           (SPEC cannot self-seal)
```

---

## 12. Dream of Conquest Mapping

```
CONQUEST = what you touch       (rendered world, surface, play, territory)
HELEN    = what remembers       (guide-memory, non-sovereign mediation)
```

HELEN is guide-memory / mediation. HELEN is not sovereign will.
Any "world will" that can seal its own outcome is `χ_god` and is rejected.
The lawful rename is **governed world model**, with `Authority_NonSov ≡ 0`.

Mapping of HELEN equations to Conquest axes `ℋ = 𝒞 × ℳ × 𝒢 × ℛ × ℒ × 𝒲`:

```
𝒢 (governance)  ↔  τ + Χ
ℛ (replay)       ↔  E + REP status
ℒ (ledger)       ↔  x_t sequence
𝒲 (WUL)         ↔  Π
𝒞 (conquest)     ↔  x_{t+1} = F(...)
ℳ (memory)       ↔  S + X_mem
```

HELEN is not the territory. She is the governed map of it.

---

## 13. Final Mnemonic

```
𝕎 = the noun        (a governed world-object)
F  = the verb        (the transition function)
Χ  = the contract    (what must not break)
π  = the membrane    (what decides crossing)
📜 = the sealed replayable state
```

**One sentence (PhD):**

> HELEN is a governed symbolic-dynamical language in which objects are typed by
> form, epistemic status, evidence, projections, and invariants, and transitions
> are admissible only when they preserve invariant constraints under replayable,
> evidence-gated, non-self-sealing transformation.

**One sentence (beginner):**

> A thing can be beautiful in the Garden. It becomes governed only when it is
> qualified, supported, reviewed, admitted, and replayable.

**Compression ladder:**

```
S without τ       = poetry
τ without E       = claim
E without replay  = fragile
replay without Χ  = mechanics
Χ preserved by F  = governance
```

> A HELEN object is governed **iff its transition function preserves its
> invariants at every tick.** Everything else in this document is commentary
> on that line.

---

## 14. Receipt Footer

```
HELEN_LANGUAGE_V1_DRAFT_RECEIPT

file           = docs/proposals/HELEN_LANGUAGE_V1.md
sections       = 14 (status + §1–§13 + receipt)
claim_status   = NO_CLAIM
authority      = false
proposal_only  = true
ledger_effect  = none
kernel_effect  = none
repo_effect    = docs/proposals/HELEN_LANGUAGE_V1.md (untracked, not staged)
git_stage      = no
git_commit     = no
git_push       = no
final          = HOLD_FOR_OPERATOR
```
