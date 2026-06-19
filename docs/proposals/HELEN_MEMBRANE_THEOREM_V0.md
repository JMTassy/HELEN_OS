# HELEN MEMBRANE THEOREM V0

```
[🟠][⟂][🜁]◇ {🧪} 🧾#MEMBRANE_THEOREM_V0 <NO_CLAIM>

type:           PROPOSAL · THEOREM · MATHEMATICAL
layer:          GARDEN · TEMPLE · NON_SOVEREIGN
authority:      false
claim_status:   NO_CLAIM
register:       SPEC · HOLD_FOR_OPERATOR
lane:           GARDEN/TEMPLE · MATHEMATICAL
ledger_effect:  none
kernel_effect:  none
git_stage:      no
git_commit:     no
git_push:       no
final:          HOLD_FOR_OPERATOR
```

> The membrane does not censor symbols.
> It constrains crossings.
> SPEC may breathe. It may not ascend.

---

## Purpose

Prove that **SPEC cannot enter the admitted / sealed / replayable ranks without an
external receipt and operator authorization.**

*Scope note:* This is a proof about the **abstract model** — the rules as specified
in the axioms below. It proves a property of the abstract model the reducer is
**intended** to enforce. It does **not** verify that the live reducer implementation
(`src/wul_reducer.py`) realizes these axioms. That mapping requires a separate
read-only code inspection outside this lane. `MODEL ⊬ CODE`.

---

## 1. Formal Vocabulary

| Symbol | Name | Definition |
|--------|------|------------|
| `x` | Object | Any artifact, claim, persona output, or symbolic trace |
| `τ(x)` | Truth-rank | Epistemic state of `x` — element of the rank lattice |
| `SPEC` | Speculative register | Objects without external evidence; pre-membrane |
| `◌` | Appearance | `x` has been observed / surfaced — not yet claimed |
| `◇` | Claim | `x` has been proposed — `τ(x) = CLAIM` |
| `◆` | Admitted | `x` has passed the admission gate — `τ(x) = ADM` |
| `⬢` | Sealed | `x` is hash-bound and Χ-stable — `τ(x) = SEAL` |
| `∞` | Replayable | `x` survives replay under Χ — `τ(x) = REP` |
| `E(x)` | External receipt | Verifiable evidence bundle: hash-anchored, not self-reported |
| `Α(x)` | Operator authorization | Explicit admission act by the operator; not inferred |
| `Χ` | Invariant field | Set of preserved structural invariants at every transition |
| `Π` | Interpretation set | Family of projection functions `π_i : Objects → {PASS, FAIL}` |
| `R` | Reducer | `R : (claim, E, replay) → {ADMIT, REJECT}` — pure, deterministic, total |
| `F_Χ` | Transition function | `x_{t+1} = F_Χ(x_t, u_t, c_t)` — constrained by Χ |

### Truth-rank lattice

```
REP  (∞)   ←  survives replay + Χ
 ↑
SEAL (⬢)   ←  hash-bound + prior ◆ + Χ
 ↑
ADM  (◆)   ←  E ∧ Α ∧ R = ADMIT
 ↑
REV        ←  under reduction
 ↑
EVID       ←  evidence bundled
 ↑
CLAIM (◇)  ←  proposed

SPEC ─────── order-incomparable with ◆, ⬢, ∞
             (not below, not above — laterally isolated)
```

SPEC is not a low rung of the same ladder. It is a **separate register** — it
cannot climb the admitted chain because it cannot satisfy the admission predicate.

---

## 2. Core Axioms

```
A0  [EDGE-SET EXHAUSTIVENESS — CLOSED WORLD]
    The only admissible transition gates into {◆, ⬢, ∞} are:
      g₂: SPEC/◇ + E + Α → ◆
      g₄: ◆ + Χ → ⬢
      g₅: ⬢ + replay + Χ → ∞
    No hidden edge exists. No aesthetic, persona, repetition, centrality,
    or symbolic-intensity edge leads into {◆, ⬢, ∞}.
    Without A0, steps 7 and 9 of the proof do not close.

A1  [APPEARANCE ≠ TRUTH]
    ◌(x) ⇏ τ(x) ∈ {ADM, SEAL, REP}
    Surfacing an object does not advance its rank.

A2  [PERSUASION ≠ AUTHORITY]
    Argument(x, P) ⇏ Α(x)
    No argument, however compelling, constitutes operator authorization.

A3  [SYMBOLIC INTENSITY ≠ ADMISSION]
    Intensity(x) ⇏ E(x)
    Aesthetic force, symbolic density, or resonance carry zero evidential weight.

A4  [SPEC WITHOUT E REMAINS SPEC]
    SPEC(x) ∧ ¬E(x) ⇒ SPEC(x)
    Absence of evidence is a fixed point: SPEC does not escape without
    external receipt injection.

A5  [SPEC WITHOUT Α REMAINS NON-ADMITTED]
    SPEC(x) ∧ ¬Α(x) ⇒ ¬ADM(x)
    Authorization absence is a fixed point: the operator gate is not optional.

A6  [SEAL REQUIRES Χ PRESERVATION]
    ⬢(x) ⇒ ADM(x) ∧ (F_Χ ⊨ Χ at x)
    An object cannot be sealed without first being admitted and without the
    transition preserving all invariants in Χ.

A7  [REPLAY REQUIRES PRIOR SEAL + TRACE + Χ]
    ∞(x) ⇒ ⬢(x) ∧ ReplayTrace(x) ∧ (F_Χ ⊨ Χ at x under replay)
    Replayability is strictly downstream of sealing.
```

---

## 3. Transition Rules (the only admitted edges)

```
g₂  admission :  ◇ ∧ E → ◆
    guard:  E ≠ ∅  ∧  R(x,E) = ADMIT  ∧  Α

g₄  seal      :  ◆ ∧ Χ → ⬢
    guard:  prior ◆  ∧  Χ preserved                              (A6)

g₅  replay    :  ⬢ ∧ replay ∧ Χ → ∞
    guard:  prior ⬢  ∧  ReplayTrace  ∧  Χ preserved              (A7)
```

`Α` is mandatory in `g₂` because `Authority_NonSov ≡ 0` — no object advances its
own rank. Under **A0** (edge exhaustiveness), `◆` is the unique gateway: by
exhaustiveness, the only edge into `⬢` is `g₄` (which requires prior `◆`) and the
only edge into `∞` is `g₅` (which requires prior `⬢`). A6 and A7 alone do not
establish uniqueness — A0 is required. Without A0, uniqueness is not claimed.
Closing `g₂` therefore closes the whole chain.

---

## 4. The Membrane

```
SPEC ↛ ◆
SPEC ↛ ⬢
SPEC ↛ ∞
```

---

## 5. Theorem — Formal Statement

**HELEN Membrane Theorem (V0)**

```
∀x [
    SPEC(x) ∧ ¬E(x) ∧ ¬Α(x)
    ⇒
    ¬◆(x) ∧ ¬⬢(x) ∧ ¬∞(x)
]
```

For any object `x`: if `rank(x) = SPEC` and there is no external receipt `E(x)` and
no operator authorization `Α(x)`, then `x` cannot transition to `◆`, `⬢`, or `∞`.

The double-headed arrow `↛` denotes the absence of any admissible transition path
under `F_Χ` from a SPEC object to an admitted, sealed, or replayable one, given
`¬E ∧ ¬Α`.

**Stronger (disjunctive) form:**

```
∀x [
    SPEC(x) ∧ (¬E(x) ∨ ¬Α(x))
    ⇒
    ¬◆(x) ∧ ¬⬢(x) ∧ ¬∞(x)
]
```

Failure of **either** `E` or `Α` is sufficient to block admission. The conjunctive
antecedent above is a special case. In practice:
- A well-evidenced SPEC object lacking operator authorization is still blocked.
- An operator-authorized SPEC object lacking an evidence receipt is still blocked.
- Both conditions are necessary; neither alone is sufficient for admission.

---

## 6. Proof

```
1.  Assume rank(x) = SPEC.
2.  Assume ¬E(x)        (no external receipt).
3.  Assume ¬Α(x)        (no operator authorization).
4.  Admission rule (g₂) requires E(x) ≠ ∅ AND R(x,E)=ADMIT AND Α(x).
5.  By (2) and (3): both E(x) and Α(x) are absent ⇒ guard(g₂) fails
    ⇒ x cannot become ◆.                                         ☐ (SPEC ↛ ◆)
6.  Seal rule (g₄) requires prior ◆ and Χ preservation.           [A6]
7.  By (5): x is not ◆ ⇒ guard(g₄) is unreachable
    ⇒ x cannot become ⬢.                                         ☐ (SPEC ↛ ⬢)
8.  Replay rule (g₅) requires prior ⬢, a replay trace, and Χ.     [A7]
9.  By (7): x is not ⬢ ⇒ guard(g₅) is unreachable
    ⇒ x cannot become ∞.                                         ☐ (SPEC ↛ ∞)
10. Therefore:
    SPEC(x) ∧ ¬E(x) ∧ ¬Α(x) ⇒ ¬◆(x) ∧ ¬⬢(x) ∧ ¬∞(x).         □
```

---

## 7. Non-Compensation Lemma

**Beauty, intensity, centrality, repetition, persona force, and symbolic resonance
do not substitute for `E` or `Α`.**

```
∀x ∀P [
    P(x) ∈ { Beauty(x), Intensity(x), Centrality(x),
              Repetition(x), PersonaForce(x), Resonance(x) }
    ⇒
    P(x) ⇏ E(x)  ∧  P(x) ⇏ Α(x)
]
```

*Proof sketch:* Each property `P` describes a relationship between `x` and its
conversational or aesthetic context — not between `x` and an external verifiable
state. The guard of `g₂` is `( E ≠ ∅ ∧ R=ADMIT ∧ Α )`. None of these components
are functions of `P`.

```
D(x) = Centrality(x) · 𝟙{ E(x) = ∅ }   (indicator drift mass)
D(x) may be arbitrarily large while guard(g₂) stays false.
∴ no quantity of centrality opens the membrane.

SCORE ⊬ ADMISSION
Σ(beauty, intensity, repetition, centrality) ⊬ E(x)
```

Witnessed example: a maximally-central, zero-lineage object (a fluent state report
whose named files were absent on disk) has `D(x) ≫ 0` and `E(x) = ∅` — rejected
by `ls`, not by argument. □

---

## 8. Π-Projection Corollary

The interpretation set `Π = {π_1, …, π_n}` provides internal validity checks —
consistency, coherence, symbolic well-formedness. These are necessary for admission
but not sufficient:

```
Conjunctive gate law:
  ∃i [ π_i(x) = FAIL ] ⇒ ¬ADM(x)   (one failing projection blocks — necessary)
  ∧_i [ π_i(x) = PASS ] ⇏ ADM(x)   (all passing does NOT imply admission)
```

Internal coherence checks from within the Garden or TEMPLE cannot supply `E` or
`Α`. `Π` gates against admission of broken objects; it does not authorize admission
of sound ones. The path from internal coherence to admission requires an external
crossing that `Π` alone cannot perform.

---

## 9. Governed Transition Corollary

From A6 and A7, every upward transition in the admitted chain must preserve Χ:

```
Governed(𝕎_t, F_Χ) ⟺ F_Χ(𝕎_t, u_t, c_t) ⊨ Χ_t   for every t
```

SPEC objects do not participate in governed transitions — they have not entered the
admitted chain and therefore cannot be subject to Χ-preservation rules that govern
it. This is a second, independent barrier: even if the receipt condition were somehow
relaxed, SPEC objects have no position in the chain for `F_Χ` to evolve under `g₄`
or `g₅`.

---

## 10. WULmoji Compression

```
[🟠][⟂][🜁]◇ {🧪}            ← theorem under review; not yet admitted

SPEC ≡ ◇ ∧ ¬E ∧ ¬Α

🟣 ≠ 🟢          claim ≠ admitted
🟣 ≠ 🟡          claim ≠ sealed
🟣 ↛ ◆
🟣 ↛ ⬢
🟣 ↛ ∞

PROOF CHAIN:
  ¬E ∧ ¬Α  →  ¬◆  →  ¬⬢  →  ¬∞

CONJUNCTIVE GATE:
  E ∧ Α ∧ R=ADMIT  =  the only key
  E alone     ⇏ ◆
  Α alone     ⇏ ◆
  beauty      ⇏ E
  intensity   ⇏ Α
  repetition  ⇏ E or Α

GOBLIN / JESTER LAW:
  🧌🃏 → 🟣 only
  🃏 ≠ 🟢   (Jester cannot admit)
  🧌 ≠ 🟡   (Goblin cannot seal)
  wild proposer ≠ validator
  mirror ≠ proof
  friction ≠ seal

AUTHORITY:
  authority_non_sov ≡ 0
  SCORE(x) ⊬ ADMISSION
  ∧_i [ π_i(x) = PASS ] ⊬ ADM(x)
```

---

## 11. Final Form

```
SPEC may appear.          ◌
SPEC may be named.        ◇
SPEC may inspire claims.  ◇ → ◇'

SPEC cannot become ◆.     (admission gate requires E ∧ Α — both external)
SPEC cannot become ⬢.     (seal requires prior ◆ — impossible by above)
SPEC cannot become ∞.     (replay requires prior ⬢ — impossible by above)

Only receipt + authorization + invariant preservation may cross the membrane.

The crossing is always:
  External receipt arrives ..................... E(x) ≠ ∅
  Operator authorizes ......................... Α(x)
  Reducer returns ADMIT ....................... R(x, E, replay) = ADMIT
  Χ is preserved .............................. F_Χ ⊨ Χ
  ─────────────────────────────────────────────────────
  ◆ is emitted. Not before.
```

---

## 12. Scope and Limits

This theorem governs the HELEN OS constitutional layer. It does not claim:

- That SPEC objects have no value — they are seeds, not admitted claims
- That SPEC must be deleted — SPEC lives in the Garden; the Garden is the
  sovereign-protected space for exploration (`NO_CLAIM(x) ⇒ x ⊬ Truth ∧ x ⊬ State ∧ x ⊬ Canon`)
- That the theorem itself is admitted — it carries `authority=false`

**Self-application:** The theorem applies to itself.

```
SELF-APPLICATION:
  this_document = SPEC   (authority=false, no external receipt yet)
  ¬E(this_document) currently
  ¬Α(this_document) currently
  ∴ this_document ↛ ◆   (by the theorem it states)
```

The document cannot admit itself. That would violate A2 (persuasion ≠ authority).
It may become `◆` only through the process it describes.

---

## 13. HAL Review Note — Patch V0.1

`HAL_MEMBRANE_THEOREM_REVIEW_RECEIPT_V0` returned `PASS_WITH_CAVEATS`.
Caveats resolved by this patch at **abstract-model level only**:

| # | HAL caveat | Fix applied |
|---|-----------|-------------|
| 1 | A0 missing — steps 7, 9 required closed-world assumption | A0 added to §2 |
| 2 | "reducer already enforces" — overclaim, no code inspection | §Purpose reworded: "abstract model intended to enforce" |
| 3 | Uniqueness of ◆ not derivable from A6/A7 alone | §3 now derives uniqueness explicitly from A0 |
| 4 | Proof shows stronger disjunctive form | §5 now states both `¬E∧¬Α` and `¬E∨¬Α` forms |

**Remaining open caveat — RESOLVED by Patch V0.2 (CODE_MAPPING_RECEIPT_V0):**

Read-only inspection of `src/wul_reducer.py` (331 lines, WUL_REDUCER_V0) executed.
16 of 17 abstract rungs match directly. One structural split resolved:

> `◆ (ADM)` in this theorem maps to `canon_admit()` in `src/wul_reducer.py` —
> the conjunction of `admit()` (E: receipt + hash + gate-green) and
> `verify_external_seal()` (Α: external operator seal, un-self-conferrable).
> The intermediate code state `S5_ADMITTED` (E without Α) is a non-sovereign
> staging rung below the membrane with no direct truth-rank analog.
> `Admit ≠ Canon` — the code's own docstring confirms this split.

Confirmed by independent JESTER lane: `JESTER_GARDEN_NO_CLAIM_SAFETY_THEOREM_V0.1`
(modus ponens over membrane axioms · VALID_REFERENCE_ONLY · authority=false).

```
CODE_MAPPING_OPEN → CLOSED
MODEL ⊬ CODE      → RESOLVED: model is sound · naming clarification added above
```

Truth-rank remains `◇` after this patch. HAL's verdict (`PASS_WITH_CAVEATS`) does
not constitute operator authorization (`Α`). The theorem is still SPEC.

---

## Receipt Footer

```
MEMBRANE_THEOREM_RECEIPT_V1 (patch V0.1 applied)

file           = docs/proposals/HELEN_MEMBRANE_THEOREM_V0.md
claim_status   = NO_CLAIM · SPEC · authority = false
register       = GARDEN · MATHEMATICAL · HOLD_FOR_OPERATOR
proof_status   = COMPLETE (10-step + A0; closes at step 5 → 7 → 9 under A0)
hal_review     = PASS_WITH_CAVEATS (HAL_MEMBRANE_THEOREM_REVIEW_RECEIPT_V0)
patch_status   = V0.2 applied — CODE_MAPPING_OPEN resolved
code_mapping   = CODE_MAPPING_RECEIPT_V0 · 16/17 direct match · 1 split resolved
                 ◆ ADM = canon_admit() · S5_ADMITTED = non-sovereign staging rung
open_caveat    = none
truth_rank     = ◇ (claim; not ◆, not sealed, not admitted)
authority      = false
ledger_effect  = none
kernel_effect  = none
git_stage      = no
git_commit     = no
git_push       = no
final          = HOLD_FOR_OPERATOR
```
