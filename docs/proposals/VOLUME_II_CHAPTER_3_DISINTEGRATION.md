---
schema: HELEN_PROPOSAL_V1
title: Transport Theory — Volume II Chapter 3, Disintegration (the bridge)
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: no
origin: JM Tassy — the bridge chapter between set-theoretic Vol I and geometric Vol II+ · 2026-06-21
---

# Volume II · Chapter 3 — Disintegration

🔵 OBSERVED · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

This chapter is the bridge between the set-theoretic world of Volume I and the
geometric world that follows. One equation carries the whole transition:

```
μ = ∫_L μ_ℓ d(R_*μ)(ℓ).
```

**Reality decomposes into observable receipts plus invisible fiber uncertainty.**
Bayesian inference, information geometry, observability, inverse problems, and
quantum measurement are all built on this decomposition.

Volume I gave the *factorization* `R = R̄ ∘ q_R`. Volume II Ch.3 gives the
*conditional decomposition* `μ = ∫ μ_ℓ dν`. Those are the two pillars.

---

## The level ladder (each feature earned, not assumed)

```
Set theory          →  indistinguishability        (~_R, fibers, quotient)
Topology            →  continuity & closed fibers
Measurability       →  pushforward uncertainty      (ν = R_*μ)
Standard Borel      →  disintegration               (μ = ∫ μ_ℓ dν)
Information geometry →  only when fibers carry statistical structure
```

---

## §3.1 Topology — closed fibers (corrected statement)

> **Proposition.** If `S, L` are topological, `R` continuous, and `L` is `T1`,
> then every fiber `R⁻¹(ℓ)` is a **closed** observational indistinguishability
> class.

Caveat (referee-safe): *closed does not mean non-pathological.* Closedness
removes some examples but is not by itself a regularity guarantee — it is exactly
the statement that `{ℓ}` closed in `L` pulls back to a closed fiber. Nothing more
is claimed.

---

## §3.2 Measurability — pushforward (what the observer can see)

> Assume `(S, Σ_S)`, `(L, Σ_L)` measurable and `R` measurable. For a probability
> measure `μ` on `S`, the **pushforward**
> ```
> ν = R_*μ,    ν(B) = μ(R⁻¹(B))
> ```
> is the first rigorous definition of *what the observer can actually see.*

No conditionals yet — measurability alone gives the receipt distribution `ν`, not
the fiber decomposition.

---

## §3.3 Standard Borel — the disintegration theorem (corrected statement)

> **Theorem (Disintegration).** Let `S, L` be **standard Borel** and `R` **Borel
> measurable**, `μ` a probability measure on `S`, `ν = R_*μ`. Then there exists a
> `ν`-a.e. uniquely determined family of regular conditional probabilities
> ```
> ℓ ↦ μ_ℓ ,    with    μ_ℓ(R⁻¹(ℓ)) = 1   for ν-almost every ℓ,
> ```
> such that
> ```
> μ = ∫_L μ_ℓ dν(ℓ).
> ```

Two caveats stated explicitly (this is where drafts overreach):

1. **Standardness is required.** Drop it and regular conditionals can fail to
   exist measurably (Glimm–Effros regime; see the Regularity Hypotheses note).
2. **`μ_ℓ(R⁻¹(ℓ)) = 1` holds only `ν`-a.e.**, and `μ_ℓ` is unique only `ν`-a.e.

---

## §3.4 Information loss — conditional entropy (weakened, correct form)

The risky line is "the entropy of `μ_ℓ` strictly quantifies the information lost."
Entropy is **not** always canonically defined — it depends on discrete structure,
a reference measure, or a chosen functional. Safe form:

> When an entropy functional is available, the **conditional entropy**
> ```
> H(S | R) = ∫_L H(μ_ℓ) dν(ℓ)
> ```
> provides a quantitative measure of residual uncertainty inside the fiber.

**Finite case (canonical).** When `S` is finite, Shannon entropy *is* canonical,
and because `R` is a deterministic function of the state (`H(S,R) = H(S)`), the
chain rule gives an exact decomposition:

```
H(S) = H(ν) + H(S | R).
```

`H(S | R)` is precisely the information the receipt cannot recover.
This is **implemented and tested** — see `transport/disintegration.py`.

---

## §3.5 Disintegration is NOT information geometry (the key separation)

A conditional `μ_ℓ` is a probability measure **on** the fiber. It does **not** by
itself make the fiber a statistical manifold. For Fisher–Rao / KL / Hellinger /
Wasserstein geometry, add a **separate** assumption:

> Each state `s` (or each fiber point) is parametrized by a probability law
> `p_s` on a sample space `(X, 𝒜)`, via a statistical map `Π : S → 𝒫(X)`.

Only then does Chapter 4 (Information Geometry) become legitimate, and the
intra-fiber metric is *induced by the model*, not chosen. Disintegration (Ch.3)
and information geometry (Ch.4) are different assumptions and must stay separate.

---

## §3.6 Volume II chapter order (geometry delayed until earned)

| Ch | Title | Hypothesis added |
|---|---|---|
| 1 | Topological observation systems | continuity, T1 → closed fibers |
| 2 | Measurable observation systems | measurability → `ν = R_*μ` |
| 3 | **Disintegration** | standard Borel → `μ = ∫ μ_ℓ dν` |
| 4 | Information geometry | states carry laws `p_s` → Fisher/KL/Wasserstein |
| 5 | When is `R` a bundle? | local triviality (a theorem, not an axiom) |
| 6 | Smooth observation systems | submersion + connection → curvature, holonomy |

The temptation `fiber ⟹ bundle` is **false in general**: local triviality must be
proved first. Curvature/holonomy live only in Ch.6.

---

## Honesty ledger

| Statement | Status |
|---|---|
| Finite pushforward `ν = R_*μ` | ✅ code + 2 tests |
| Finite conditionals `μ_ℓ` on the fiber | ✅ code + 2 tests |
| Finite disintegration identity `μ = Σ_ℓ ν(ℓ) μ_ℓ` | ✅ code + 2 tests |
| Conditional entropy + chain rule `H(S)=H(ν)+H(S|R)` | ✅ code + 4 tests |
| Injective ⟹ zero loss; constant ⟹ total loss | ✅ code + 3 tests |
| General standard-Borel disintegration theorem | 📝 foundations (infinitary; not code) |
| Information geometry (Fisher/KL on fibers) | 📝 Chapter 4 — needs the separate `p_s` assumption |
| Bundles / curvature / holonomy | 📝 Chapters 5–6 — earned, not assumed |

Transport suite total: **74 tests**
(`test_transport.py` 29 + `_geometry` 15 + `_factorization` 15 + `_disintegration` 15).

---

## Status

```
authority:     false
sovereign:     false
canon:         false
ledger_effect: none
claim_status:  NO_CLAIM
final:         HOLD_FOR_OPERATOR
```

🔵 OBSERVED — the bridge chapter. Not 🟢 ADMITTED.
