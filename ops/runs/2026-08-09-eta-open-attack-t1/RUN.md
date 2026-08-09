# AUTORESEARCH RUN — ETA_OPEN_ATTACK_T1

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=0 · admission=none · ledger_effect=none
class         : AUTORESEARCH_TRANCHE (bounded, non-sovereign)
run_id        : 2026-08-09-eta-open-attack-t1
head_at_run   : 30b5269f2cbede4f041d913c55a70881ca163c95
branch        : claude/doctrine-proposals
date          : 2026-08-09
mission       : attack the OPEN list of docs/proposals/ETA_CALCULUS_V0_1.md
```

## Contract (bounded — declared at launch)

```
candidate_budget      : 3 epochs (finite, checkable math targets only)
stopping_condition    : all 3 epochs emitted + HAL-arithmetic recompute → STOP
admission             : FORBIDDEN (autoresearch may discover, may not admit)
self_KEEP_REJECT      : FORBIDDEN (RALPH violation) — promotion verdict is operator/MAYOR's
per_epoch_receipt     : required (receipts.jsonl)
authority             : 0 on every candidate and receipt
ledger_effect         : NONE · kernel/governance/schema paths untouched
evaluation            : dual read (HER-style context + HAL-style recompute), neither admits
```

## Epoch results

| epoch | candidate | target (ETA OPEN item) | HAL arithmetic | status |
|---|---|---|---|---|
| E1 | AT-CE-01 | AT — Abstraction Transport not automatic | VERIFIED (all 6 adjunction rows, Stab_C, B, β∘B recomputed) | CANDIDATE · **conditional on β:=f∘γ** |
| E2 | RT-LIFT-01 | replay faithfulness is a real assumption | VERIFIED (fold recomputed; R(a)=R(aa)=1; \|Λ(id)\|>1) | CANDIDATE · clean |
| E3 | RHO-NEC-01 | ρ-stability sufficient-not-necessary | VERIFIED arithmetic; **OUT-OF-CLASS** (T1 non-monotone) | CANDIDATE · scope-limited |

## HAL verdicts (my independent recompute — verification, not admission)

**E1 / AT-CE-01 — VERIFIED-CONDITIONAL.**
`C={0<1<2}`, `A={0<1}`, `α=(0→0,1→1,2→1)`, `γ=(0→0,1→2)`. Adjunction: all 6 rows
`α(X)≤q ⟺ X≤γ(q)` agree ✓ (and `αγ=id_A`, so insertion). `f=(0,0,1)`,
`T_C=(1,1,2)` monotone, `f∘T_C=f` ✓. `B(T_C)=αT_Cγ=(0→1,1→1)` = const 1.
`β(f)=f∘γ=(0,1)`; `β(f)(B(0))=1 ≠ 0=β(f)(0)` ✓ — AT fails.
CAVEAT (goblin-flagged, confirmed load-bearing): `β` is **undefined in ETA V0.1**.
The witness assumes `β:=f∘γ`. Under this β, AT fails *because* `f∘ρ≠f`
(`f(ρ(1))=f(2)=1≠0`). This does not break ETA — it sharpens it: the defensible
theorem is conditional AT ("holds when `f∘ρ=f`"), which is already the doc's
anti-laundering condition. **Feeds §8 OPEN "AT" and §5 anti-laundering, not a refutation.**

**E2 / RT-LIFT-01 — VERIFIED-CLEAN.**
`E={a}`, `S={0,1}`, `s0=0`, `δ(0,a)=1`, `δ(1,a)=1`. `R(ε)=0`, `R(aⁿ)=1` (n≥1).
Non-injective: `R(a)=R(aa)=1` ✓. `T=id`; `T̃₁(a)=a`, `T̃₂(a)=aa` are distinct monoid
endomorphisms, both satisfy `T∘R=R∘T̃` (need `R(aⁿ)=R(a^{kn})`: n=0→0=0, n≥1→1=1) ✓.
So `|Λ(id)|>1` (infinite: all k≥1) with `R` non-faithful.
**Confirms the doc's conditional theorem `HistoryFaithful(R) ⇒ |Λ(T)|≤1` is non-vacuous** —
`ReplayStateEquality ⇏ HistoryEquality` is real (§6, §9).

**E3 / RHO-NEC-01 — VERIFIED-ARITHMETIC / OUT-OF-CLASS.**
`C={0<1<2}`, `A={0,2}`, `γ=(0→0,2→2)`, `α=(0→0,1→2,2→2)`, insertion ✓. `ρ=(0→0,1→2,2→2)`,
`Fixρ={0,2}`. `T2=(0→0,1→2,2→2)` monotone. LHS `αT2T1γ` and RHS `αT2ρT1γ` both `{0→2,2→2}` ✓
— composition exact despite non-ρ-stable `T1`.
**HAL CATCH (not in goblin output):** `T1=(0→1,1→0,2→2)` is **not monotone** (`0<1` but
`T1(0)=1 > 0=T1(1)`). ETA transformers are monotone throughout (§3). So this establishes
"ρ-stability sufficient but not necessary" **only in the non-monotone class**. The
extracted sufficient condition — `α(T2(ρ(z)))=α(T2(z))` for all `z∈Im(T1∘γ)` — is
interesting and monotonicity-independent, but the necessity question **stays OPEN for
monotone maps**. Weaker than the goblin claimed; recorded honestly.

## Tranche verdict

```
STOP           : budget reached (3/3 epochs)
NET SIGNAL     : 2 clean falsifiers (E1 conditional, E2 clean) + 1 scope-limited (E3)
ADMITTED       : nothing (autoresearch never admits)
SELF-DECIDED   : nothing (no KEEP/REJECT — that is operator/MAYOR)
LEDGER         : untouched · KERNEL/GOVERNANCE/SCHEMA : untouched
```

## Escalation to operator / MAYOR

These are PROPOSALS. Recommended (not decided) routing:
1. **E2 (RT-LIFT-01)** is the strongest — a clean non-vacuity witness for the §6 replay
   theorem. Candidate to cite in ETA V0.1 §6 as the worked example behind "faithfulness
   is a real assumption." Needs one fresh validator recompute (proposer≠validator).
2. **E1 (AT-CE-01)** is conditional on defining `β`. Real next action is upstream:
   **ETA V0.1 must define the predicate-transport map `β`** before AT can be stated,
   let alone attacked. This tranche surfaced a *gap in the doc*, which is the useful find.
3. **E3 (RHO-NEC-01)** — hold; re-run inside the monotone class before any claim. The
   sufficient condition it extracted is worth keeping as a HYPOTHESIS.

No file under `docs/proposals/ETA_CALCULUS_V0_1.md` was modified. Folding any of these in
is a separate explicit verb.

```
authority=0 · canon=FALSE · ledger_effect=NONE
🌿 novelty increased · authority remained exactly zero
```
