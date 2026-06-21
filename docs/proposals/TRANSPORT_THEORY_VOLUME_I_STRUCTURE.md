---
schema: HELEN_PROPOSAL_V1
title: Transport Theory — Volume I Structure (referee-safe set-theoretic foundation)
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: no
origin: JM Tassy referee pass on Volume I · 2026-06-21
---

# Transport Theory — Volume I Structure

🔵 OBSERVED · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

Referee-safe architecture for Volume I. The governing principle: **assume the
weakest possible structure and prove which additional assumptions are necessary
for richer geometry to emerge.** Volume I is pure set theory. No topology, no
measure, no manifolds — those are Volumes II+.

---

## The center: the Fundamental Factorization Theorem

Every observation map factors through its observational quotient:

```
        q_R                  R_bar
    S ───────▶ S/~_R ────────────▶ L
                    (R_bar injective)

    R = R_bar ∘ q_R,   R_bar injective.
```

This — not the Non-Reconstructibility theorem — is the center of Volume I.
Fibers, reconstruction, completeness, and invisible symmetry are all statements
about this single diagram. It deserves the name **Fundamental Factorization
Theorem of Observation**.

**Implemented:** `transport/factorization.py` — `Factorization` realizes `S/~_R`
abstractly as class indices `{0,…,k-1}`, so `q_R : S → S/~_R` is a genuine map
to the quotient (not to `L`), and `R_bar : S/~_R → L` is injective by
construction. `.factorizes()` verifies `R = R_bar∘q_R`; `.r_bar_is_injective()`
verifies the non-trivial content.

---

## Observable Universality (universal property)

The quotient is not merely convenient — it is the **minimal observable universe**.

> **Proposition.** If `f : S → X` satisfies `s ~_R t ⟹ f(s) = f(t)`, then there
> is a unique `f̃ : S/~_R → X` with `f = f̃ ∘ q_R`.

This turns the quotient from a definition into a canonical object — referees
recognize it immediately. **Implemented:** `universal_factor(f, R, space)`
returns the unique `f̃` when `f` is class-constant, and `None` when `f` splits a
fiber (the hypothesis fails). Uniqueness is automatic because `q_R` is surjective.

---

## The reconstruction / Choice correction (Option A adopted)

In pure set theory the existence of a section `C : im(R) → S` with `R(C(ℓ)) = ℓ`
is **not automatic** — selecting one representative per fiber invokes a choice
principle. We adopt **Option A**:

> A reconstruction map is a *section of R over im(R), when such a map exists.*
> Existence is not claimed in general.

**Implemented:** `Reconstructor.section()` returns an explicit section over a
concrete finite state space (constructive — no appeal to Choice needed there),
and its docstring states the section-when-it-exists caveat for uncountable
fibers. `section_is_valid()` verifies `R(C(ℓ)) = ℓ`.

---

## Invisible symmetries act fiberwise

> Every `T ∈ Inv(R)` preserves every fiber: `T(R⁻¹(ℓ)) ⊆ R⁻¹(ℓ)`.

Logically equivalent to `R∘T = R`, but stated as the set-inclusion that seeds
the later groupoid / bundle viewpoint. **Implemented:**
`GeneralizedKernel.acts_fiberwise()` and `preserves_fiber()` (which exhibits the
inclusion on a named fiber).

---

## Terminology fix: `~_R`, not `ker`

At Level 0, avoid `ker(R)` / "null space" — those are linear-algebra notions and
are incorrect here. Use the **kernel equivalence relation**:

```
~_R = { (s,t) ∈ S × S : R(s) = R(t) }.
```

The word "kernel" is safe only as "kernel equivalence relation." The code uses
`are_equivalent`, `fiber`, and `GeneralizedKernel` (the invariance monoid
`Inv(R)`), never a linear kernel.

---

## Suggested chapter architecture

| Ch | Title | Content |
|---|---|---|
| 1 | Observation systems | `(S, L, R)` as sets; no structure |
| 2 | Equivalence, fibers, quotient | `~_R`, `R⁻¹(ℓ)`, `S/~_R`, **Fundamental Factorization** |
| 3 | Reconstruction | sections, the Choice caveat, Non-Reconstructibility |
| 4 | Invisible transformations | `Inv(R)`, fiber actions, completeness |
| 5 | Universal properties | quotient as the minimal observable universe |

---

## The strict hierarchy (each feature is a consequence, not an axiom)

```
Sets → Topology → Measure → Standard Borel → Bundles → Geometry
```

| Level | Structure on S, L | New mathematics |
|---|---|---|
| 0 | sets | fibers, ~_R, quotients, factorization |
| 1 | topological spaces | continuity, compact/connected fibers; L Hausdorff ⟹ fibers closed |
| 2 | measurable spaces | pushforwards, conditional measures |
| 3 | standard Borel | disintegration, measurable selection, regular conditionals |
| 4 | fiber bundles | local triviality (a theorem/subclass, NOT an axiom) |
| 5 | smooth manifolds | connections, holonomy, curvature |

Bundles and curvature are **earned**, never assumed. This makes every theorem
state precisely which hypotheses it consumes — the referee-safe property.

---

## Honesty ledger

| Statement | Status |
|---|---|
| Fundamental Factorization `R = R_bar∘q_R`, `R_bar` injective | ✅ code + 6 tests |
| Observable Universality (universal property) | ✅ code + 3 tests |
| Section honest about Choice (Option A) | ✅ code + 3 tests (finite/constructive) |
| `Inv(R)` acts fiberwise | ✅ code + 3 tests |
| Terminology `~_R` not `ker` | ✅ reflected throughout `transport/` |
| Levels 1–5 hierarchy | 📝 foundations (see REGULARITY_HYPOTHESES note for Levels 2–3 detail) |

Transport suite total: **59 tests** (`test_transport.py` 29 +
`test_transport_geometry.py` 15 + `test_transport_factorization.py` 15).

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

🔵 OBSERVED — Volume I structural plan. Not 🟢 ADMITTED.
