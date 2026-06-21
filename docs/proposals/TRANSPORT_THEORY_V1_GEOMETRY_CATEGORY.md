---
schema: HELEN_PROPOSAL_V1
title: Transport Theory V1 — Intrinsic Geometry, Bundles, Category, and the Observation Axiom
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: no
origin: JM Tassy refinement of TRANSPORT_THEOREM_V0 · 2026-06-21
---

# Transport Theory V1 — Geometry, Bundles, Category, Axiom

🔵 OBSERVED · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

Refinement of `TRANSPORT_THEOREM_V0.md` and `TRANSPORT_THEORY_PAPER_V0.tex`.
Four structural advances. Each either closes a gap in V0 or upgrades a fiber
from a bare set to a mathematical object.

---

## 1. The fiber metric `d_P` is extrinsic — and that is a limitation

V0 (paper §10) measures the semantic leak inside a fiber by

```
d_P(s₁, s₂) = d_M(P(s₁), P(s₂))
```

for a secondary observation map `P : S → M`. This is an **extrinsic** metric:
it measures the fiber by how it sits inside `M`. It is exactly analogous to
measuring distance on a curved surface by the straight-line distance through
the ambient Euclidean space.

The deeper question: **can a fiber carry an intrinsic geometry**, defined
without reference to any external embedding?

This shifts the object of study from `([S]_R, d_P)` to `([S]_R, 𝒢)` where `𝒢`
is *any* structure the fiber carries in its own right:

```
topology · metric · measure · graph · simplicial complex · manifold ·
category · probability space
```

A fiber is then a genuine mathematical object, not a bag of indistinguishable
points. The extrinsic `d_P` becomes one *instance* of fiber structure (the one
induced by a chosen probe), not the definition.

---

## 2. Fiber-bundle interpretation

The triple `(S, R, L)` is precisely the data of a bundle projection:

```
        R
    S ─────▶ L            fiber over ℓ  =  R⁻¹(ℓ)
```

This is `E →π B` from differential geometry. Established questions transfer
directly:

| Bundle question | Observation meaning |
|---|---|
| Is the bundle **trivial**? | Do all fibers look the same (S ≅ L × F)? |
| **Locally trivial**? | Do nearby receipts have isomorphic fibers? |
| **Stratified**? | Does fiber type jump on a lower-dimensional locus of L? |
| **Singular**? | Are there receipts where the fiber degenerates? |

**Implemented (coarse, V0-grade):** `transport/bundle.py` computes the
fiber-size profile and a *size-trivial* check (all fibers equinumerous — the
first necessary condition for local triviality).

**Fiber curvature.** When nearby receipts `ℓ` and `ℓ+δ` have very different
fibers, the observation map has curvature. A discrete version is implemented:

```
κ_R(ℓ) = mean over neighbours ℓ' of  |#fiber(ℓ) − #fiber(ℓ')|
```

This is size-based (coarse). A finer curvature compares fiber *structure*, not
cardinality. Both are application-free.

---

## 3. Information geometry — geometry induced, not chosen

If every state induces a probability law `p_s`, each fiber inherits a
**statistical manifold**. Then the geometry is canonical rather than chosen:

```
Fisher–Rao metric · KL divergence · Wasserstein geometry
```

This removes the arbitrariness of picking `P` in §1: the probe is the
state-to-law assignment, and the metric follows from the laws. This is the
preferred route whenever states carry distributions (statistics, ML, QM).

---

## 4. The category Obs

Study not a single `R` but the **category of all observation maps**.

- **Objects:** observation maps `R : S → L`.
- **Morphisms:** pairs `(F, G)` making the square commute:

```
        F
    S ─────▶ S'
    │         │
   R│         │ R'
    ▼         ▼
    L ─────▶ L'
        G

    commutes  ⟺  R' ∘ F = G ∘ R
```

**Implemented:** `transport/category.py` — `ObservationMorphism.commutes_on()`,
`identity_morphism()`, `compose()`. A morphism transports one observation
system into another while respecting receipt structure. This is the home of
limits, colimits, adjunctions, and functorial transport.

---

## 5. The Missing Axiom — Observation Axiom (closes a real V0 hole)

V0 lets `R` be *any* function. Two pathological maps trivialize the theory:

- **Constant** `R(s) = c`: one fiber covering all of `S`. Sees nothing.
- **Identity** `R = id`: only singletons. Distinguishes states no real
  observer could tell apart.

**Observation Axiom.** An observation map is *admissible* only relative to an
**observer class** `O`, given by a ground-resolution map `G : S → F` stating
exactly what that observer can distinguish. Then:

```
O-sound      ~_G ⊆ ~_R     R makes no distinction the observer can't (no hallucination)
O-complete   ~_R ⊆ ~_G     R makes every distinction the observer can
O-admissible ~_R = ~_G     R preserves EXACTLY the observer's information
```

Consequences (proved by test):

- the **constant** map fails *completeness* against any non-trivial observer;
- the **identity** map fails *soundness* against any limited observer;
- a map matched to its observer (parity-R for a parity-observer) is admissible.

The theory studies `(S, O)` — a state space together with an observer class —
not a lone arbitrary map. **Implemented:** `transport/observer.py`
(`ObserverClass`, `is_pathological`).

---

## 6. Volume progression

| Volume | Title | Contents | Status |
|---|---|---|---|
| I | Foundations | observation maps · fibers · quotients · reconstruction · completeness | V0 paper + module |
| II | Geometry of Observation | fiber metrics · topology · bundles · curvature · stability | this doc + bundle.py (coarse) |
| III | Category of Observation | morphisms · universal properties · functorial transport · equivalence | category.py (seed) |
| IV | Applications | inverse problems · control · QM measurement · ML embeddings · proof systems · number theory (finite-band) | examples only |

Crucial property: **the foundations depend on no unproven conjecture.** RH,
HELEN, embeddings, finite-band operators, and gauge symmetry are *case studies
that test the framework*, never axioms it rests on.

---

## 7. What is code vs what is prose (honesty ledger)

| Claim | Status |
|---|---|
| Observer class + admissibility (Axiom) | ✅ code + 7 tests |
| Constant/identity ruled out | ✅ proved by test |
| Category morphism + commuting square | ✅ code + 4 tests |
| Bundle size-triviality + discrete curvature | ✅ code + 4 tests (coarse) |
| Intrinsic fiber geometry (topology/manifold) | 📝 prose — not yet formalized |
| Information-geometric induction (Fisher/Wasserstein) | 📝 prose — not yet formalized |
| Local triviality (beyond equal cardinality) | 📝 prose — only the necessary cardinality check exists |

`transport/` modules and `tests/test_transport_geometry.py` carry the ✅ rows.
The 📝 rows are research directions, not implemented claims.

---

## Status

```
authority:     false
sovereign:     false
canon:         false
ledger_effect: none
claim_status:  NO_CLAIM
final:         HOLD_FOR_OPERATOR
git_stage:     no
```

🔵 OBSERVED — mathematical refinement. Not 🟢 ADMITTED.
