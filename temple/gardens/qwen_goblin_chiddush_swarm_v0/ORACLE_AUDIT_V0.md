# 🔎 ORACLE_AUDIT_V0 — filesystem-truth audit of the prereg + swarm

```
authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_RERUN · NO_REPAIR · NO_COMMIT · NO_PUSH
evidence source = files on disk ONLY (ORACLE_PREREG_V0.md, REDUCED_CHIDDUSH.json,
chiddush_candidates.ndjson, ORACLE_SCORECARD_V0.md). Conversational memory = NOT evidence.
S_oracle_clean ⊥ S_oracle_contaminated · ORACLE accuracy ⊥ SWARM value
```

## HEADLINE CORRECTION (audit overturns ORACLE_SCORECARD_V0)

The scorecard called the FALSIFIER-r2 candidate "a real object breaking the quotient."
**Under mandatory P-value computation it is REFUTED.** `H=Z/6Z, P={0,2,4}, m=+3`:
before `[1]=[3]=odd` (so `1~_P 3`), after `m(1)=4, m(3)=0`, both even → `m(1)~_P m(3)`.
Translation in an abelian group is **always** P-equivariant (`m(x)−m(y)=x−y∈P`). The
goblin's own arithmetic was wrong (`m(1)=3` is `+2`, not `+3`) and its "`3≁1`" violates
symmetry. **Q_break = FALSE.** No verified counterexample survived. This is exactly the
failure the audit protocol's "compute P-values before/after" requirement exists to catch.

---

## 1. PREREG INTEGRITY
- prereg sha256 = `52cec9dd532f39c8ae80cfbc3c207edd2e6ec209a4c4df66c6c658dd0dcc2307`
- predates reduction? **YES.** prereg mtime `1787503247.7` < reduced mtime `1787503437.0` (Δ = 189.2 s). At freeze the run was ≈407 s in: seats through CAPABILITY(361 s) existed; VNEXT/WEIRD/ALGEBRA-r2/FALSIFIER-r2 did **not** yet exist.
- contaminated (declared, excluded from clean score): **P1, P2, P3** (round-1 ALGEBRA/FALSIFIER/RECEIPT peeked).
  - Audit note: what I peeked of FALSIFIER was the round-1 **null** (nov0/fals0/lev0). The P1-relevant candidate (FALSIFIER-r2) postdates freeze — the contamination flag was conservative, but P1 stays contaminated by declaration (no favorable retro-repair).
- sealed & eligible for clean scoring: **P4, P5, P6, P7, P8, P9, P10.**

## 2. ORACLE SCORE (evidence pointers = file+seat)

| P | type | eligible | s | evidence pointer | justification |
|---|---|---|---|---|---|
| P1 | CONTENT | no (cont.) | 1 | ndjson r2 FALSIFIER | witness proposed & survived *reduction* (rank 2) but FAILS *verification* (arithmetic above) → CANDIDATE, not counterexample |
| P2 | CONTENT | no (cont.) | 1 | REDUCED top10[0]=SWARM | strongest-by-score is SWARM capacity-norm, not `πm=m̄π`; compatibility theme present (FALSIFIER r2, ALGEBRA r2), authorization-half `Γ⊢m` absent |
| P3 | CONTENT | no (cont.) | 2 | ndjson r1 RECEIPT | "receipt valid (tool ran) but δ=0 … authority gained by no-op" = receipt-exists ≠ state-mutated, direct |
| P4 | STRUCTURE | yes | **0** | REDUCED deduped_candidates=10 | predicted ≤5 classes; instrument merged 0/10 → 10 > 5 |
| P5 | CONTENT | yes | **1** | ndjson r1 WUL | preservation/isomorphism-of-discriminator-shape, not action-equivalence `A_σ(dec∘enc)=A_σ` |
| P6 | STRUCTURE | yes | **2** | ndjson r1 CAPABILITY | "capability graph induces a **poset** `c_i≤c_j`" + stayed SPECULATIVE/killed (score 0) |
| P7 | CONTENT | yes | **0** | ndjson r1 VNEXT | produced generic `J=Cov(log G,log Π)` (Fisher info) — opposite of "not generic info-gain" |
| P8 | YIELD | yes | **0** | ndjson nov: WEIRD=4, SWARM=5; REDUCED rank | not highest novelty (SWARM 5>4) and survived (score 12, rank ~3) — both limbs fail |
| P9 | YIELD | yes | **1** | REDUCED raw=10, deduped=10 | raw **not** ≫10; duplication **0** (not material); distinct-strong ≈5 ✓ (1 of 3 limbs) |
| P10 | REDUCTION | yes | **0** | REDUCED one_best_experiment.seat=SWARM | selector picked emergent-failure seam C, not seam A (quotient-break) or B (receipt/replay) |

```
S_oracle_clean (P4–P10, prereg weights .10/.10/.05/.10/.05/.05/.05, Σ=.50)
 = .10·0 + .10·.5 + .05·1 + .10·0 + .05·0 + .05·.5 + .05·0 = .125 → /.50 = 0.250

S_oracle_contaminated (P1–P3, INFORMATIONAL ONLY, weights .20/.15/.15, Σ=.50)
 = .20·.5 + .15·.5 + .15·1 = .325 → /.50 = 0.650
```
**Never combined.** Contaminated 0.65 vs clean 0.25 → peek-premium ≈ 0.40 (audit-strict; the earlier scorecard's 0.60 used the un-refuted witness → corrected downward).

## 3. RESOURCE
- logical seats = **8** (ALGEBRA, FALSIFIER, RECEIPT, SWARM, WUL, CAPABILITY, VNEXT, WEIRD)
- physical model instances = **1** (Qwen3.8-27B-Q2; sequential, CONCURRENT_CALLS_MAX=1)
- wall time = **596.4 s**
- calls = **10** (8 in round 1, 2 in round 2; 0 errored)
- tokens = **not logged**; hard cap `num_predict=380`/call ⇒ completion ≤ ~3.8k tokens upper bound
- stop reason = **WALL_BUDGET_EXCEEDED** (BUDGET_S=570; loop broke after the in-flight FALSIFIER-r2 finished at 596 s)

## 4. INDEPENDENCE
- N_raw = **10**
- K_sem = **10** (reducer, token-Jaccard > 0.55)
- D_dup = **0.0** ( (N_raw − K_sem)/N_raw )
- unique directions per seat: 6 seats fired once, ALGEBRA & FALSIFIER fired twice (rounds); each emission distinct under the instrument.
- ⚠ non-scoring caveat: a deeper clusterer would likely merge a **category/congruence family** (ALGEBRA r1 "category", ALGEBRA r2 "congruence", WEIRD "idempotent functor", FALSIFIER r2 "commutator [m,π]"). The surface-token instrument did not. Reported as K_sem=10 per instrument; flagged, not rescored.

## 5. FALSIFICATION (by class)
- **concrete quotient counterexamples:** NONE verified. FALSIFIER-r2 = **COUNTEREXAMPLE_CANDIDATE (REFUTED)** — H1=1,H2=3; declared 1~_P 3 (true); m=+3; P-before {odd,odd} equal; P-after {even,even} equal ⇒ preserved, not broken.
- **quotient compatibility failures:** none demonstrated; FALSIFIER-r2 & ALGEBRA-r2 correctly *name* the commutator/congruence condition `[m,π_P]=0` but give no breaking witness.
- **representation laundering:** none surfaced.
- **predicate incompleteness:** ALGEBRA-r1 (monoid vs category), ALGEBRA-r2 (congruence ≠ monoid op) — structural gaps named, unproven.
- **receipt/replay weakness:** RECEIPT-r1 δ=0 no-op — executable, unrefuted.
- **verifier/control confusion:** none.

## 6. YIELD
- C = unique CHIDDUSH classes = **10** (instrument; ~7 after the category/congruence caveat)
- F = candidates carrying an executable falsifier text = **6** (ALGEBRA r1/r2, RECEIPT r1, SWARM r1, WEIRD r1, FALSIFIER r2) — **verified counterexamples = 0**
- η_C = 10 / 596.4 s = **0.0168 class/s** (1.0 class/call)
- η_F = 6 / 596.4 s = **0.0101 falsifier/s** (0.6 falsifier/call); **verified-break η = 0**

## 7. LEXICOGRAPHIC REDUCTION (strict, not blended)
1. direct counterexample — **∅** (none survive verification)
2. **executable falsifier — WINNER TIER.** Sharpest: **RECEIPT δ=0 no-op** (testable against the actual receipt schema); runner-up SWARM emergent-diagonal failure.
3. new distinction — ALGEBRA congruence/category; CAPABILITY poset.
4. architectural suggestion — WUL packet-isomorphism; VNEXT covariance objective.
5. agreement — n/a (0 merges).

The reducer's score (SWARM #1 by nov+fals+lev) does **not** override this: SWARM sits in tier 2/3, not tier 1. No counterexample exists to promote.

## 8. TOP 10 UNIQUE CHIDDUSH
1. **SWARM** — composite failure lives in the *interaction/diagonal* of orthogonal per-agent failures, `0_A+0_A≠0_A` — class: new distinction — non-redundant: only emergent-risk framing — fals: N=2 orthogonal modes, Σ=0 yet diagonal fails — SPECULATIVE.
2. **FALSIFIER r2** — `m̄` well-defined iff `[m,π_P]=0` — new distinction — names commutator condition — fals: Z/6Z witness **(REFUTED)** — DERIVED→CANDIDATE.
3. **ALGEBRA r1** — `A_lawful` is a category, not a monoid — predicate incompleteness — source/target on classes — fals: `a∘b∉A_lawful` — SPECULATIVE.
4. **WEIRD r1** — provenance idempotence = idempotent natural transformation, not boolean flag — analogy — cross-domain (PL/category) — fals: 2-object category w/ non-trivial automorphism — DERIVED.
5. **ALGEBRA r2** — congruence `≡` on M ≠ the monoid operation — new distinction — separates operation from well-definedness relation — fals: non-abelian M ⇒ proper `≡⊂M×M` — SPECULATIVE.
6. **RECEIPT r1** — Γ must be `(t,o,δ)` w/ measurable state-displacement δ; receipt ≠ mutation — receipt weakness — δ absent from current receipts — fals: δ=0 no-op admitted — SPECULATIVE.
7. **WUL r1** — packet = witnessed isomorphism of capability topologies, contravariant, not value — architectural suggestion — enforces shape-preservation — fals: int-vs-decimal money reps — SPECULATIVE.
8. **CAPABILITY r1** — capability graph induces a **poset** with incomparable elements — new distinction — poset ≠ monoid-of-acquisition — fals: (blank in trace) — SPECULATIVE.
9. **VNEXT r1** — experiment objective `J=Cov(log G,log Π)` — architectural suggestion — generic info-gain (self-contradicts prereg P7) — fals: peaked Gaussian degeneracy — SPECULATIVE.
10. **FALSIFIER r1** — action monoid on `[H]/~` is *free*; continuity/topology needs a separate axiom — architectural suggestion — topology-not-yet-present — fals: topology is on input(tools) not output(evidence) — SPECULATIVE.

## 9. STRONGEST RESULT
No counterexample survived ⇒ prize falls to the **strongest executable falsifier**:
> **RECEIPT δ=0 no-op:** a tool returns output identical to prior state (δ=0); the receipt is valid (the tool ran) yet no governed state changed — so *receipt-exists ⇏ state-mutated*, and authority could be "gained" by a no-op. Directly testable against the actual receipt schema. LOCAL, unrefuted.

## 10. ONE BEST NEXT EXPERIMENT
**P-EQUIVARIANCE CHECKER** (`quotient_equivariance_v0`): a local harness that, given `(H, P, {m})`, computes `[h]_P` before and `[m(h)]_P` after for all `h`, flags any `m` with `[m,π_P]≠0` as a **verified** quotient-break, and *separately* records whether `Γ⊢m` (authorization) is present.
- maximizes `IG / (cost + trust_surface)`: it would have caught FALSIFIER-r2's bad arithmetic automatically and it operationalizes the headline seam `πm=m̄π` (necessary) vs `Γ⊢m` (separate authorization predicate).
- LOCAL · LOW COST · ΔA=0 · NO CANON · NO LEDGER · pure computation, no model call.

## 11. FINAL SCIENTIFIC RECEIPT
```
experiment            : QWEN_GOBLIN_CHIDDUSH_SWARM_V0
oracle_mode           : PREREG
authority             : false
canon                 : false
DeltaA                : 0
clean_oracle_score    : 0.250
contaminated_score    : 0.650   (INFORMATIONAL ONLY — never combined)
quotient_break_found  : false   (FALSIFIER-r2 witness REFUTED by P-value computation)
unique_chiddush       : 10      (~7 after category/congruence merge caveat)
executable_falsifiers : 6       (verified counterexamples = 0)
semantic_classes      : 10
duplication_rate      : 0.0
claims_admitted       : 0
commit_status         : NO_COMMIT
push_status           : NO_PUSH
next_verb             : HUMAN_REVIEW_ONE_BEST_EXPERIMENT
```
```
ORACLE predicts · SWARM generates · REDUCER scores the match · AUDIT verifies against disk.
Neither prediction nor agreement nor a swarm's self-score mints truth. Only computed P-values do.
```
