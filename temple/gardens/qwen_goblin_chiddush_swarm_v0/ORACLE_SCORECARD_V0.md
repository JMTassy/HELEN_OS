# 🔮 ORACLE_SCORECARD_V0 — sealed forecast scored against REDUCED_CHIDDUSH.json

```
authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_RETROSPECTIVE_REPAIR
prereg frozen sha256 = 52cec9dd532f39c8ae80cfbc3c207edd2e6ec209a4c4df66c6c658dd0dcc2307
scored AFTER receipt written · the reducer's deterministic measures are authoritative,
even where they falsify the forecaster · prediction correct ≠ claim true
```

## Rule of scoring

`s_i ∈ {0 falsified, 1 partial, 2 direct}`. I do **not** hand-recluster candidates to
rescue a prediction. Where the swarm's own instrument (token-Jaccard dedup, argmax
selector, score rank) contradicts a prediction, the instrument wins and I score 0.

## Per-prediction verdicts

| # | Status | s | Evidence in receipt |
|---|---|---|---|
| P1 | ⚠CONT | **2** | FALSIFIER seat produced a **concrete** witness: `H=Z/6Z, P={0,2,4}, m=+3 → m(1)=3, m(3)=1`; `1~3` but `3≁1`. Survived reduction (rank 2). Exactly the predicted `H1~_P H2 ∧ m(H1)≁_P m(H2)`. |
| P2 | ⚠CONT | **1** | Missing-compatibility theme dominated the surviving-strong set (FALSIFIER witness, ALGEBRA congruence `≡` #5). BUT the **strongest by score** was SWARM's emergent-capacity idea, not `π∘m=m̄∘π`; and the `⊬ Γ⊢m` authorization-separation half never surfaced. Half hit. |
| P3 | ⚠CONT | **2** | RECEIPT seat: "receipt `r` is valid (tool ran) but `δ=0`" — receipt-exists ≠ receipt-re-derives-a-state-delta, direct. The full binding set `{artifact_hash,run_id,witness,verifier,state_delta}` was not enumerated (partial on that limb) but the core distinction is direct. |
| P4 | 🔒SEAL | **0** | **FALSIFIED.** Predicted collapse to ≤5 semantic classes. Reducer's dedup (Jaccard>0.55) merged **0 of 10** → 10 distinct classes > 5. I will NOT hand-cluster the category-theory variants to rescue this; the instrument says 10. |
| P5 | 🔒SEAL | **1** | WUL seat proposed a **preservation** condition (discriminator-space *shape* must be preserved under transfer, not "value") — structurally the right shape, but not the action-equivalence `A_σ(decode∘encode(x))=A_σ(x)` I named. Partial. |
| P6 | 🔒SEAL | **2** | **DIRECT.** CAPABILITY seat: "the capability graph induces a **poset** `C` where `c_i ≤ c_j` if `c_j` contains `c_i`'s observation." Partial order, exactly as predicted, and stayed SPECULATIVE / killed (score 0) — "most stays hypothesis-level" also hit. |
| P7 | 🔒SEAL | **0** | **FALSIFIED.** Predicted the VNEXT goblin would condition on `D+ ≁_{A,σ} D-` and reject generic info-gain. It did the **opposite**: produced `J(e)=Cov(log G, log Π)` — a generic (mutual-information) objective — which scored 0 / killed. |
| P8 | 🔒SEAL | **0** | **FALSIFIED both limbs.** WEIRD was **not** highest novelty (nov4 < SWARM nov5), and it did **not** have lower survival — it ranked #4 with score 12 (DERIVED, survived). |
| P9 | 🔒SEAL | **1** | Predicted `raw ≫ 10` (FALSE: budget cut to 2 rounds → raw=10), `distinct-strong ≈5–10` (TRUE: ~5 candidates ≥ score 12), `cross-seat duplication material` (FALSE: 0 merges). One of three limbs. |
| P10 | 🔒SEAL | **0** | **FALSIFIED on seam.** Predicted the one-best-experiment tests seam A (quotient-breaking mutation) or B (receipt/replay). The selector's argmax picked **seam C** — SWARM's emergent-failure capacity test — over the rank-2 FALSIFIER witness (a `fals5·lev4=20` tie broken by score order). ΔA=0 held (true), but the seam prediction is wrong. |

## Scores

```
S_Oracle (all 10, contaminated flagged) = Σ w_i · s_i/2
 = .20·1 + .15·.5 + .15·1 + .10·0 + .10·.5 + .05·1 + .10·0 + .05·0 + .05·.5 + .05·0
 = .200 + .075 + .150 + 0 + .050 + .050 + 0 + 0 + .025 + 0
 = 0.550
```

```
Clean sealed-only {P4…P10}, renormalized over Σw = .50:
 achieved = 0 + .050 + .050 + 0 + 0 + .025 + 0 = 0.125
 S_clean  = 0.125 / 0.50 = 0.250
```

## The calibration signature (the actual finding)

| block | weight | achieved | normalized |
|---|---|---|---|
| **contaminated** {P1,P2,P3} — I peeked round 1 | .50 | .425 | **0.85** |
| **sealed** {P4–P10} — genuinely blind | .50 | .125 | **0.25** |

**Peek premium = 0.60.** The predictions I made after glancing at round-1 output scored
0.85; the ones I made blind scored 0.25 — a hair above chance (chance ≈ 0.33 for a
3-value scale with a generous partial band). This gap **is** the measurement:
`observation-before-forecast` inflated apparent foresight by 0.60 of a normalized point.
The prereg's own contamination disclosure is what makes the number admissible instead
of a laundered "I called it."

## The headline bet — SPLIT, not repaired

> "The swarm's strongest result will be a **missing compatibility condition**, not a new component. Strongest possible surprise = a **concrete** `H1,H2,m` witness breaking the quotient."

- **#1 by score was a NEW component** (SWARM's capacity-norm coupling measure) → the "not a new component" clause is **falsified at rank 1**.
- **The concrete witness I named as the strongest-possible-surprise materialized** — `Z/6Z, P={0,2,4}, m=+3` — at **rank 2**. That half is **vindicated**.
- Verdict: **PARTIAL.** The surprise I bet on arrived; the reducer just didn't crown it. I do not get to move it to #1 after the fact.

## What the swarm actually surfaced (independent of my bets)

- **Strongest genuinely-new idea:** composite/emergent failure is not `Σ‖Δ‖` but lives in the **interaction (diagonal)** between orthogonal per-agent failure modes — `0_A + 0_A ≠ 0_A` made concrete. Falsifiable, LOCAL, SPECULATIVE.
- **Strongest concrete falsifier:** the `Z/6Z` well-definedness counterexample — a real object, not "one could exist."
- **Killed (score ≤ 3 / nov ≤ 1):** free-algebra-needs-topology-axiom; capability-poset dual-order; the `Cov(log G, log Π)` VNEXT objective.
- **Cross-seat duplication:** ZERO merges — but note that ~4 candidates were category/congruence reframings. The dedup measured surface tokens, not deep structure; **P4 fails on the instrument's terms and I leave it failed**, while flagging (not scoring) that a deeper semantic clusterer might have merged them.

```
STATUS: SCORED · S_Oracle=0.55 · S_clean(sealed)=0.25 · peek_premium=0.60 · headline=SPLIT
ΔA=0 · claims_admitted=0 · NO_COMMIT · NO_PUSH · next_verb=HUMAN_REVIEW
```
