---
schema: HELEN_PROPOSAL_V1
title: Transport Theory — Volume II Chapter 4, Information Geometry
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: no
origin: JM Tassy — BUILD_VOLUME_II_CHAPTER_4_INFORMATION_GEOMETRY_V1 · 2026-06-21
---

# Volume II · Chapter 4 — Information Geometry

🔵 OBSERVED · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

Statistical geometry enters **only after an explicit new hypothesis**. It does
not follow from disintegration.

---

## The boundary this chapter must not cross

```
Volume I       R = R̄ ∘ q_R                 (set theory — indistinguishability)
Volume II Ch.3 μ = ∫ μ_ℓ d(R_*μ)(ℓ)         (standard Borel — disintegration)
Volume II Ch.4 Π : S → 𝒫(X), s ↦ p_s        (statistical hypothesis — geometry)
```

**Core rule (non-negotiable):** `μ_ℓ` is a probability measure supported on a
fiber. It does **not** automatically make the fiber a statistical manifold.
Disintegration produces conditionals; it does not produce geometry.

---

## §4.1 The new hypothesis

> **Statistical hypothesis.** Each state `s ∈ S` carries a probability law `p_s`
> on a measurable sample space `X`. This is the statistical map
> ```
> Π : S → 𝒫(X),   Π(s) = p_s.
> ```

With `Π` in hand, two **co-fiber** states `s, t` (i.e. `R(s) = R(t)`) may be
compared through their induced laws `p_s, p_t`. Without `Π`, they are merely
two points of an unstructured fiber — there is nothing to measure.

---

## §4.2 Induced divergences and distances

All are functions of the laws, **not** of `R`:

| Quantity | Definition | Properties |
|---|---|---|
| KL divergence | `KL(p‖q) = Σ p log(p/q)` | asymmetric; ≥ 0; `+∞` if `p ⋘̸ q` |
| Hellinger | `H(p,q) = (1/√2)‖√p − √q‖₂` | metric; symmetric; `∈ [0,1]` |
| Total variation | `TV(p,q) = ½ Σ|p−q|` | metric; symmetric; `∈ [0,1]` |
| Fisher information (1-D) | `I(θ) = Σ p_θ (∂_θ log p_θ)²` | local; needs a parametrized curve `θ ↦ p_θ` |

These are **induced by the probability model itself** — no externally chosen
embedding `P` is required. That is the whole point: the intra-fiber metric is
canonical relative to `Π`, not arbitrary.

**Implemented:** `transport/statistical.py` —
`kl_divergence`, `hellinger_distance`, `total_variation_distance`,
`fisher_information_1d`, plus `StatisticalState` / `StatisticalObservationModel`.

---

## §4.3 Information geometry REFINES fibers; it does not replace them

A fiber that looked structureless in Volume I can, under `Π`, carry a genuine
statistical geometry. But:

- the **quotient** `S/~_R` is unchanged (Ch.4 adds no observational distinctions);
- the **disintegration** `μ = ∫ μ_ℓ dν` is unchanged (Ch.4 adds no conditionals);
- Ch.4 only equips each fiber with intra-fiber distances between co-fiber states.

So two observation-equivalent states are **statistically distinguishable iff
their laws differ** (`TV(p_s, p_t) > 0`). The distinguishing power comes from
`Π`, never from `R`. This is the precise sense in which information geometry is a
*refinement*: it sees inside a fiber that the receipt collapses to a point.

---

## §4.4 Explicit handling of degeneracies

- **Zero-probability / absolute continuity.** `KL(p‖q) = +∞` exactly when
  `p(x) > 0` while `q(x) = 0` — returned as `math.inf`, never silently dropped.
  The convention `0·log(0/q) = 0` is applied for `p(x) = 0`.
- **Empty law rejected.** `StatisticalState` cannot be built without a law:
  no `Π`, no geometry (tested).
- **Fisher only on adequate grids.** `fisher_information_1d` needs ≥ 3 grid
  points and returns interior estimates only; it is a finite/discrete
  **smoke-test** utility, NOT a claim of smooth-manifold structure.

---

## §4.5 What this chapter does NOT assume

```
✗ no bundles
✗ no curvature
✗ no holonomy
✗ no connections
✗ no smooth-manifold structure
```

Those require the proper-submersion + connection hypotheses of Chapters 5–6 and
must be earned separately. Chapter 4 stops at: *states carry laws ⟹ fibers carry
intra-fiber statistical distances.* Nothing more.

---

## Honesty ledger

| Statement | Status |
|---|---|
| KL/Hellinger/TV on finite laws, self-distance 0 | ✅ code + tests (cases 1–3) |
| KL asymmetry | ✅ code + test (case 4) |
| Co-fiber states may carry different `p_s` | ✅ code + test (case 5) |
| Distinguishable iff laws differ | ✅ code + tests (case 6) |
| No geometry without `p_s` | ✅ code + tests (case 7) |
| Zero-probability KL = `+∞`, explicit | ✅ code + tests (case 8) |
| Finite Fisher information (1-D) | ✅ code + smoke tests (case 9) |
| Chapter 3 disintegration still passes | ✅ regression test (case 10) |
| Smooth Fisher–Rao manifold geometry | 📝 Chapters 5–6 — needs submersion/connection |
| Bundles / curvature / holonomy | 📝 Chapters 5–6 — earned, not assumed |

Transport suite total: **89 tests**
(`test_transport.py` 29 + `_geometry` 15 + `_factorization` 15 +
`_disintegration` 15 + `_information_geometry` 15).

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

🔵 OBSERVED — Chapter 4. Not 🟢 ADMITTED.
