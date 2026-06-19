# HELEN Language V1 — PhD Guide

```
type:           PROPOSAL
authority:      false
claim_status:   NO_CLAIM
parent:         HELEN_LANGUAGE_V1.md
final:          HOLD_FOR_OPERATOR
```

---

## The Structural Error This Language Addresses

Classical symbolic systems, religious frameworks, AI pipelines, and
hyperstitional architectures all share one failure mode:

```
S  ⟹  truth
```

A symbol that appears strongly enough, that circulates widely enough,
that compresses belief efficiently enough, is treated as self-authorizing.

HELEN refuses this implication. The correct form is:

```
S + τ + E + Π + Χ  ⟹  governed object candidate
```

An object is not admitted because it appears. It is admitted because it
carries an explicit epistemic status and a verifiable path.

---

## The Governed World-Object

```
𝕎 = (S, τ, E, Π, Χ)
```

### S — Symbolic / Perceptual Form

The WUL token tree. The shape, the glyph, the phrase. `S` carries no admission
weight on its own. `symbol ⊬ 𝕎`. The Garden emits S freely.

### τ — Epistemic Truth Status

An ordinal position on the admission ladder. Not binary. τ cannot be
self-conferred: `Authority_NonSov ≡ 0`.

### E — Evidence Bundle

```
E = { payload_hash, cum_hash, ledger_seq, MAYOR_seal, replay_verdict }
```

Core law: `E = ∅  ⟹  τ < EVID`.

### Π — Projection Family

Each π_i reads the object from one axis:

```
π_K8     : 𝕎 → {PASS, NO_SHIP}   (non-determinism)
π_Ktau   : 𝕎 → {PASS, NO_SHIP}   (coherence)
π_replay : 𝕎 → {ACTIVE, DRIFT}   (determinism)
π_R_R    : 𝕎 → received_reality
π_R_T    : 𝕎 → true_reality
```

`R_R ≠ R_T` = reference drift. HELEN measures this gap continuously.

Forbidden collapses:

```
π_sem(x)  ≠  x
π_spec(x) ≠  x
π_aff(x)  ≠  authority(x)
```

### Χ — Invariant Set

```
χ₁  E = ∅ → τ blocked                (NO RECEIPT = NO CLAIM)
χ₂  ND output never enters spine unhashed    (NO HASH = NO VOICE)
χ₃  proposer(u_t) ≠ validator(u_t)          (K2 Rule)
χ₄  Authority_NonSov ≡ 0                    (no self-authorization)
χ₅  additionalProperties: false             (schema ceiling)
χ₆  SHIP xor ABORT                          (termination is sacred)
χ₇  replay = truth                          (soundness re-proven, not owned)
```

---

## Truth-Status Ladder — Formal Definition

| Code | Name | Admission condition |
|------|------|---------------------|
| SPEC | Speculative | Garden register. Can inspire OBS. Cannot self-promote. |
| OBS  | Observed | Direct observation recorded. E may be empty. |
| CLAIM | Claimed | Proposed assertion. E partial or pending. |
| EVID | Evidenced | E ≠ ∅. K-gates can run. |
| REV  | Reviewed | Independent verification. π_proposer ≠ π_validator enforced. |
| ADM  | Admitted | Conjunctive gate passed. Operator-authorized. |
| SEAL | Sealed | Hash-chained. Human-sealed. Irreversible. |
| REP  | Replayable | ↻(x_t, u_t, c_t) yields identical output. |

### Non-Promotion Law

```
SPEC  ↛  ADM
SPEC  ↛  SEAL
SPEC  ↛  REP
```

The speculative can inspire a claim. It cannot cross the membrane alone.
Re-entry is lawful only as a fresh OBS with its own evidence bundle.

---

## τ as a Partial Order

Let `T = {◌, ◇, ◆, ⬢, ∞}` with the distinguished off-ladder register `SPEC`.

Define the strict covering relation and its transitive closure as the chain:

```
◌ ⋖ ◇ ⋖ ◆ ⋖ ⬢ ⋖ ∞
```

so `(T, ≤)` is a finite total order on the admitted ladder. `SPEC` is **not
comparable** to any rung in `{◆, ⬢, ∞}`: for all `r ∈ {◆, ⬢, ∞}`,
`SPEC ≰ r` and `r ≰ SPEC`.

This incomparability **is** the speculative firewall — a structural theorem,
not merely a rule.

Monotonicity law (no self-advance):

```
τ_{t+1}(x) ⊒ τ_t(x)   only via an admissible transition
¬( x raises its own τ )
```

i.e. `Authority_NonSov ≡ 0`.

---

## The Transition Function — Full Constraint

The generic equation:

```
x_{t+1} = F(x_t, u_t, c_t)
```

is insufficient. Every system, including a propaganda engine, satisfies it.
The HELEN-specific form is:

```
x_{t+1} = F_Χ(x_t, u_t, c_t)
```

where `F_Χ` denotes a transition **already constrained by** Χ. Not a general
F with Χ added on top — the filtration is prior.

### Admissibility Conditions on F_Χ

```
1. deterministic / replayable     ↻(x_t, u_t, c_t) = x_{t+1}
2. evidence-gated                 E = ∅ ⇒ no admitted claim in x_{t+1}
3. non-self-sealing               F_Χ ⊬ authority(F_Χ)
4. authority-bounded              Authority_NonSov(u_t) ≡ 0
5. invariant-preserving           F_Χ(𝕎_t, ·, ·) preserves Χ_t
```

---

## Reducer R and the Admission Gate

Admission is the verdict of a pure reducer:

```
R : (claim, E, replay) → {ADMIT, REJECT}
```

`R` is total, deterministic, and side-effect-free: identical inputs yield
identical verdicts. This is what makes replay meaningful — replaying R on
recorded inputs must reproduce the same verdict.

The ladder transitions as guarded rewrites:

```
g₁ : ◌ → ◇                                     (formulation)
g₂ : ◇ ∧  E → ◆         gated by R(·,E,·)=ADMIT      (admission)
g₃ : ◇ ∧ ¬E → SPEC                              (speculative collapse)
g₄ : ◆ ∧ Χ → ⬢           gated by invariant preservation    (seal)
g₅ : ⬢ ∧ replay ∧ Χ → ∞  gated by replay ∧ invariant preservation   (durable truth)
```

The gate is **conjunctive and non-compensatory**:

```
ADM  ⟺  Typed ∧ Evidenced ∧ Reviewed ∧ InvariantPreserving ∧ Replayable
SCORE  ⊬  ADMISSION        (no weighted sum compensates a failed conjunct)
```

Speculative firewall as theorem: since SPEC is order-incomparable with
`{◆, ⬢, ∞}` and every path into the admitted chain factors through `g₂`
(which requires `E ≠ ∅`), **there is no admissible path SPEC → ◆ / ⬢ / ∞**.

---

## The Governing Condition — Key Theorem

```
Governed(𝕎_t, F_Χ)  ⟺  F_Χ(𝕎_t, u_t, c_t) ⊨ Χ_t   for every t
```

**Χ appears in two positions simultaneously:**

```
𝕎 = (S, τ, E, Π, Χ)              Χ as internal field
x_{t+1} = F_Χ(x_t, u_t, c_t)     Χ as external law on F
```

This is the structural core. A law in HELEN is not a property stored once.
It is a predicate F_Χ must **re-prove at every step**.

```
law ≠ stored label
law = recurrent invariant check
```

The watch model, not the wall model:
*A wall is built once. A watch is kept indefinitely.*

---

## High-Dimensional Reading Space

A HELEN object is projectable onto independent axes:

```
𝓧 = X_geom × X_sem × X_mem × X_gov × X_aff × X_spec

X_geom  structural / geometric form
X_sem   semantic content
X_mem   memory / provenance / lineage
X_gov   governance status (τ-ladder position)
X_aff   affective overlay   — representational; SAY ⊬ BE; FACE ⊬ FEELING
X_spec  speculative surplus — Garden; NO_CLAIM; non-authoritative
```

Each projection `π_i : 𝓧 → X_i` is a partial reading. Two structural laws:

**Non-totality:** `π_i(x) ≠ x` for every `i` — no single projection is the
object. Taking a projection for the totality is the canonical error (e.g.
mistaking the affective skin `π_aff` for authority).

**Joint-consistency / SHIP condition:**

```
necessary(SHIP)  :  ⋀_i π_i(𝕎) = PASS
sufficient(BLOCK):  ∃ i . π_i(𝕎) = FAIL
```

`π_aff` and `π_spec` are explicitly **non-authoritative**: they range over
representational skins, not evidence (`SAY ⊬ BE`). The governance axis
`X_gov` is orthogonal to `X_aff` and `X_spec`.

---

## Hyperstition vs HELEN

Hyperstition:

```
truth_by_spread(x) = belief(x) × repetition(x) × camouflage(x)
```

HELEN:

```
truth_by_replay(x) = evidence(x) × reducer(x) × replay(x)
```

The distinction in one line: `spread ≠ truth · replay = test`.

Applied to symbolic types:

```
χ_horse  →  test              (surface + provenance + replay verifiable)
χ_god    →  compost           (hidden interior + demand for unverifiable authority)
```

The governed object is the horse. The self-sealing authority claim is the god.
HELEN promotes the first and composts the second.

---

## HELEN in Operational Terms

```
x_t     = { seq_t, cum_hash_t, last_admitted_payload }
u_t     = helen_say.py("...", --op)          (only legal input)
c_t     = { schema_registry, K-gate verdicts,
             MAYOR_seal, Witness drift, Χ }   (the membrane)
F_Χ     = reduce_step()                      (the reducer IS F_Χ)
x_{t+1} = { seq_{t+1}, sha256(cum_hash_t ∥ payload_hash(u_t)), u_t }
```

F_Χ is deterministic and public. Replay is re-running F_Χ on recorded inputs.
That is why soundness is re-proven, not owned.

---

## Non-Confusion Laws (Formal)

```
existence   ⊬  admission
persuasion  ⊬  authority
replay      ⊬  governance      unless ⊨ Χ
SCORE       ⊬  ADMISSION       (conjunctive gate — no compensation)
SPEC        ↛  ADM / SEAL / REP
```

The anti-relabelling constraint:

Speculative content cannot launder itself into the spine by
acquiring force, repetition, affective charge, or narrative authority.
Re-entry is lawful only with a fresh evidence bundle.

---

## One-Sentence Definition

> HELEN is a governed symbolic-dynamical language whose world-objects are typed
> by `(S, τ, E, Π, Χ)` over a chain order on τ with an order-incomparable
> speculative register, whose admissions are the verdicts of a pure deterministic
> reducer `R` under a conjunctive, non-compensatory gate, and whose transitions
> `F_Χ` are admissible only when pure, replayable, receipt-gated, non-self-sealing,
> and invariant-preserving — so that *governed* reduces exactly to *`F_Χ` ⊨ `Χ`
> at every tick*.

---

## Compression

```
S without τ         =  poetry
τ without E         =  claim
E without replay    =  fragile
replay without Χ    =  mechanics
Χ preserved by F_Χ  =  governance
```

```
𝕎 = the noun         (S, τ, E, Π, Χ)
F_Χ = the verb        x_{t+1} = F_Χ(x_t, u_t, c_t)
Χ = the contract      GOVERNED(𝕎) ⟺ F_Χ preserves Χ each tick
π = the membrane      what decides crossing
📜 = the sealed replayable state
```
