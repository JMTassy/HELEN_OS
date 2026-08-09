# AUTORESEARCH RUN — ETA_FABLE_SWARM_T2

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=0 · admission=none · ledger_effect=none
class         : AUTORESEARCH_TRANCHE (bounded, FABLE-visioned, non-sovereign)
run_id        : 2026-08-09-eta-fable-swarm-t2
workflow      : wf_cabbe6ea-78a · task w3xg6i7tf
head_at_run   : 54e06d472eeb81d87fc6bee50e21194f9dabeb70
branch        : claude/doctrine-proposals
date          : 2026-08-09
mission       : attack the OPEN list of docs/proposals/ETA_CALCULUS_V0_1.md
scale         : 20 epochs · 42 agents · 2,110,567 subagent tokens · ~12.7 min
```

## Honest-labelling note (load-bearing)

The workflow's verify stage is an **LLM agent** recomputing finite arithmetic. For
≤4-element posets / tiny monoids that recompute is legitimate and independent, but
it is **not** the external deterministic HAL, not Γ, and not a χ_med witness.
Therefore every verdict below is labelled `l2_arithmetic_recheck`, and:
```
EXTERNAL_HAL    : NOT_RUN
GAMMA           : NOT_RUN
CAPABILITY      : NONE
MUTATION        : NONE
MEMBRANE_STATUS : UNVERIFIED
CHI_MED         : NOT_WITNESSED
```
Nothing here is admitted. Nothing is self-promoted into the ETA doc. `l2_recheck
VERIFIED ⊬ ADMIT`; `is_real=false ⊬ ¬h`.

## Epoch table

| epoch | OPEN target (short) | l2_recheck | is_real |
|---|---|---|---|
| E01 | FC characterization | VERIFIED | ✅ (counterexample; characterization still OPEN) |
| E02 | FC sufficient cond. `T_C(C)⊆γ(A)` | FAILED | ❌ conjecture refuted (10 counterexamples) |
| E03 | AT: define β (doc gap) | VERIFIED | ❌ defines 3 incompatible β, selects none |
| E04 | AT under β=b1 | VERIFIED | ❌ conditional on β:=f∘γ |
| E05 | AT under β=b3 (closure) | UNKNOWN | ❌ closure makes AT strictly worse |
| E06 | AT min counterexample size | UNKNOWN | ❌ β-conditional |
| E07 | RT counterexample search | VERIFIED | ❌ minimal object can't refute RT |
| **E08** | **RT sufficient condition** | **VERIFIED** | **✅ one-step T-equivariance; naive conjecture refuted** |
| E09 | ICT counterexample | OUT_OF_CLASS | ❌ collapse from non-insertion γ, not dynamics |
| E10 | ICT under GI | VERIFIED | ❌ degenerate (|A|=2 forces B(T)=id) |
| E11 | ICT minimal poset size | VERIFIED | ❌ GI object undefined |
| **E12** | **RIT: `T̃∈Λ(T) ⇒ T̃⁻¹∈Λ(T⁻¹)`** | **VERIFIED** | **✅ THEOREM in V0.1 free-monoid model (0 mismatches ≤nS,nE=3)** |
| E13 | RIT sufficient condition | UNKNOWN | ❌ substituted premise, degenerate |
| E14 | FCA-BCA compatibility | OUT_OF_CLASS | ❌ admits antitone map; 𝔉 undefined |
| E15 | BCA image FCA-closed? | UNKNOWN | ✅* proper-inclusion counterexample (𝔉-conditional) |
| **E16** | **replay faithfulness: R injective?** | **VERIFIED** | **✅ NO in general; pigeonhole `\|S\|≥1+k+k²`** |
| **E17** | **sufficient cond. for faithful R** | **VERIFIED** | **✅ (under disclosed reinterpretation)** |
| **E18** | **π_S injectivity** | **VERIFIED** | **✅ non-faithful R compatible with non-unique lift** |
| E19 | nontrivial reversible core exists? | VERIFIED | ❌ conditional on undefined δ/ρ/Q_I |
| **E20** | **ρ-stability necessity (monotone)** | **VERIFIED** | **✅ necessary in monotone class — repairs T1's out-of-class gap** |

## Six citable results (l2_recheck VERIFIED + is_real, under ETA's stated assumptions)

- **E08 — RT sufficient condition.** State-invariance lifts to ledger-invariance iff
  **one-step T-equivariance on relevant generators** (`T∘δ_e = δ_e∘T`), *not* mere
  T̃-fixes-relevant-symbols (that naive conjecture refuted with a contrast witness).
- **E12 — RIT is a theorem (V0.1).** In the free-monoid model with `T̃∈AutMon(E*)≅Sym(E)`,
  `T̃∈Λ(T) ⟺ T̃⁻¹∈Λ(T⁻¹)`. Exhaustive to nS,nE=3, 0 mismatches. Scope caveat: V0.1 only;
  V0.2 trace-monoid / V0.3 DAG could break it.
- **E16 — replay faithfulness answered: NO.** `R` is not injective per state in general
  (2-state counterexample). Pigeonhole bound: needs `|S| ≥ 1+k+k²`.
- **E17 — sufficient condition for faithful replay** (append/prefix-tree carrier), under a
  disclosed reinterpretation to "faithful monoid action" (the literal finite reading is
  impossible — see doc errors).
- **E18 — π_S non-injective.** Non-faithful `R` is compatible with non-unique lifts, so
  faithfulness **cannot be dropped** from any `|Λ(T)|≤1` guarantee.
- **E20 — ρ-stability necessity, repaired.** A **monotone** witness (`T1=[1,1,1]`,
  constant, which *is* monotone) breaks composition ⇒ ρ-stability is necessary **in the
  monotone class**. This corrects tranche-T1's `RHO-NEC-01`, which I had marked
  OUT_OF_CLASS for using a non-monotone T1.

## Two documentation errors the swarm proved (pure doc fixes, unblock the citable set)

1. **`HistoryFaithful(R)` as "R injective per state" is impossible on any finite S**
   (pigeonhole, E16/E17). Restate as *faithful monoid action*, or exclude ε / grow the
   carrier.
2. **The constant map is monotone** — ETA V0.1 (and my T1 receipt) mislabelled it
   non-monotone. This is the class-membership error that produced the original
   out-of-class ρ-necessity counterexample. E20 fixes it.

## Doc gaps (blockers, ranked)

1. **β (predicate/abstraction-transport map) UNDEFINED** — blocks the entire AT axis
   (E03/E04/E05/E06) and FCA-BCA (E14/E15). Six VERIFIED-arithmetic epochs stranded at
   `is_real=false` purely because they had to interpolate their own β.
2. `Q_C` (transported invariant family) never fixed (E03/E05/E06).
3. `𝔉 / F_A` (observable value-family for Φ/Ψ) undefined (E14/E15).
4. AT typing mismatch: `Stab_C/Stab_A` range over invariant sets, but `β=b3` closes over
   transformation sets (E05).
5. `Λ(T)` vs `Λ_str(T)` — raw `|Λ(swap)|=9`; the §6 uniqueness holds only after
   intersecting with `AutMon(E*)` (E13).
6. GI's concrete object (closure/`Fix(ρ)` realization) undefined (E11); `R` signature
   ambiguous (header `R:L→E` vs §6 `R:S×E*→S`) (E18/E16).

## FABLE synthesis (readiness only — RECOMMEND, not ADMIT)

> The replay/RIT axis (E08, E12, E16, E17, E18) is the maturest and most citable; the
> AT/β axis is blocked upstream by an undefined transport map.

**Recommendation (FABLE, authority=0):** fix **β** first in an ETA V0.2 (with `Q_C`,
`F_A`, and the invariant-set-vs-transformation-set typing) — one undefined object gates
six epochs. E03 already enumerates the three natural β candidates (pullback `b1`,
existential `b2`, universal/closure `b3`); E04/E05 show `b1` fails AT and `b3` makes it
worse — decision-ready input for the operator/Γ to *select* the canonical β. Cheap
independent wins: apply the two proven doc-error fixes, which unblock the mature
replay/RIT results for citation.

## Escalation

```
STOP            : budget reached (20/20 epochs)
ADMITTED        : nothing (autoresearch never admits)
SELF-DECIDED    : nothing (no KEEP/REJECT — operator/MAYOR only)
EXTERNAL_HAL/Γ  : NOT_RUN · MEMBRANE : UNVERIFIED · χ_med : NOT_WITNESSED
LEDGER/KERNEL/GOVERNANCE/SCHEMA : untouched
NEXT (operator verb required):
  - FOLD REPLAY AXIS  → cite E08/E12/E16/E17/E18/E20 into ETA §6/§8 (guarded, proposer≠validator)
  - DEFINE BETA       → open ETA_CALCULUS_V0_2 with a canonical β (unblocks AT/FCA-BCA)
  - FIX DOC ERRORS    → restate HistoryFaithful + reclassify constant map (pure doc fixes)
```

```
authority=0 · canon=FALSE · ledger_effect=NONE
🌿 novelty increased · authority remained exactly zero
```
