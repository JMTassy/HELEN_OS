---
schema: HELEN_PROPOSAL_V1
title: Transport Theory — Volume I Regularity Hypotheses (anti-pathology axioms)
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: no
origin: JM Tassy question — minimal structure on S, L · 2026-06-21
---

# Volume I — Regularity Hypotheses

🔵 OBSERVED · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

> **Question (JM):** to make the bundle projection `R : S → L` viable in
> Volume I — local triviality, curvature later — what *minimal* topological
> or measure-theoretic structure must `S` and `L` carry to prevent the fibers
> from becoming pathological?

Answer: the hypotheses are **tiered**. Each downstream construction buys in only
the structure it actually needs. The strength of Volume I is that the *core*
(fibers, quotient, reconstruction, completeness) needs **nothing**; structure is
added only when geometry or measure is invoked.

---

## Tier 0 — Set level (V0 core): no hypothesis

Fibers, `~_R`, the quotient `S/~_R`, injectivity, sufficiency, `Inv(R)` — all
pure set theory. `R : S → L` as a bare function suffices. **Keep it that way.**
The Non-Reconstructibility theorem must never acquire a hypothesis it doesn't
use. This hypothesis-freedom is exactly what lets RH, control theory, and
embeddings all instantiate the same core.

---

## Tier 1 — Measurable level: **standard Borel** (the load-bearing axiom)

To make "the fiber inherits a measure / a statistical manifold" a *theorem*
rather than a wish, assume:

```
S, L  are standard Borel spaces        (Polish, with Borel σ-algebra)
R     is Borel measurable
```

Payoff — three things become canonical:

1. **Fibers are measurable.** `{ℓ}` is Borel in a standard Borel `L`, so
   `R⁻¹(ℓ)` is Borel in `S`.

2. **Each fiber carries a canonical conditional law (Rokhlin disintegration).**
   Given a probability measure `μ` on `S` with `ν = R_*μ`, there is a
   `ν`-a.e.-unique family `{μ_ℓ}` of probability measures with
   `μ_ℓ(R⁻¹(ℓ)) = 1` and `μ = ∫ μ_ℓ dν(ℓ)`. This is precisely the
   "fiber inherits a measure" claim — and it **requires standardness**. Drop it
   and the conditionals can fail to exist measurably.

3. **The information geometry is induced, not chosen.** With each state's law in
   hand, the intra-fiber distance is Fisher–Rao / KL / Wasserstein — no
   arbitrary probe `P`. This is the rigorous form of your rejection of the
   extrinsic `d_P`.

### The sharp characterization (the actual cliff edge)

The single condition that prevents fiber pathology is:

```
~_R  must be a SMOOTH Borel equivalence relation
     (concretely: ~_R = ker of a Borel map into a standard Borel space).
```

This is automatic when `L` is standard Borel and `R` is Borel — *that is the
whole point of demanding it*. The boundary is the **Glimm–Effros dichotomy**: a
Borel equivalence relation is either smooth, or it Borel-reduces `E₀` (eventual
equality on `2^ℕ`). In the second case `S/~_R` is **not** standard — no Borel
section, no disintegration, fibers cannot be coherently coordinatized. Ergodic
orbit equivalence relations live here; that is the exact face of "pathological
fiber."

So: **the minimal anti-pathology hypothesis is that the observation be a genuine
Borel map into a standard Borel base.** Everything else (entropy of the quotient,
sufficiency à la Lehmann–Scheffé, Fisher metric on fibers) follows.

### Consistency axiom — the base IS the quotient

`L` is not a free coordinate system. For "the fiber varies with `ℓ`" to mean
anything, the realized base must be

```
R(S)  ≅  S/~_R     (carry the final/quotient Borel structure across R)
```

If `L` carries structure `R` cannot see, "nearby receipts" references coordinates
outside the observation — a category error. Volume I should fix `L := S/~_R` with
the quotient structure and treat any larger ambient `L` as a chosen embedding
(extrinsic, exactly the thing to avoid).

---

## Tier 2 — Topological level: continuous **quotient map**, Hausdorff base

For "nearby receipts" and local-triviality questions:

```
S, L  topological
R     continuous AND a quotient map   (L gets the quotient topology = S/~_R)
L     Hausdorff (≥ T1)                (⟹ fibers R⁻¹(ℓ) are closed)
```

Local triviality is **not** automatic. A continuous surjection with varying fiber
type is in general a **stratified** space (Thom–Mather): fiber type is locally
constant on strata and jumps on a closed lower-dimensional locus. So the honest
Volume I/II default is *stratified bundle*; *locally trivial* is the good special
case (e.g. `R` a fibration, or — smooth case — a proper submersion via Ehresmann).

---

## Tier 3 — Smooth level (Volume II): proper submersion + connection

Only here do curvature and holonomy acquire their literal meaning:

```
S, L  smooth manifolds
R     proper smooth submersion        (Ehresmann ⟹ locally trivial fiber bundle,
                                        constant fiber diffeomorphism type)
V = ker(dR)                           vertical bundle
H                                     Ehresmann connection (horizontal complement)
κ_R = Frobenius obstruction of H      curvature; holonomy = transport around loops in L
```

This is where your `κ_R`-as-holonomy identification is exactly correct — but it
is a Volume II object, because it needs the submersion + connection that Tier 1–2
do not assume.

---

## Tie-in to the Observation Axiom

The observer-class axiom (`~_R = ~_G`) and the standardness axiom are **the same
guardrail seen twice**:

- the **observer axiom** kills *trivial* maps (constant: fiber = all of `S`;
  identity: fiber = a point) by relativizing to a resolution `G`;
- the **standardness axiom** kills *wild* quotients (non-smooth `~_R`, the
  Glimm–Effros regime).

Together: `R` is a Borel observation, admissible for an observer class `O` whose
ground `G` maps into a standard Borel `F`. Then `~_R = ~_G` is smooth, `S/~_R` is
standard Borel, and every fiber is a coherent, measure-bearing object. That pair
is the complete minimal hypothesis set for Volume I.

---

## Honesty ledger

| Statement | Status |
|---|---|
| Tier 0 core needs no hypothesis | ✅ already reflected in `transport/` (pure-set code) |
| Standard Borel ⟹ disintegration ⟹ fiber laws | 📝 foundations (math fact; cited Rokhlin) |
| `~_R` smooth ⟺ Borel into standard Borel; Glimm–Effros boundary | 📝 foundations (descriptive set theory) |
| base = quotient consistency axiom | 📝 foundations |
| curvature = holonomy needs submersion+connection (Vol II) | 📝 foundations |

**No test accompanies this note, by design.** The pathology it rules out is
genuinely infinitary (it appears only on uncountable spaces — `E₀`, ergodic
orbit relations). The finite state spaces in `tests/test_transport*.py` are
*all* smooth and standard, so a finite "smoothness checker" would pass
vacuously and misrepresent the depth. The honest record is: this tier is
mathematics, not code.

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

🔵 OBSERVED — Volume I regularity appendix. Not 🟢 ADMITTED.
