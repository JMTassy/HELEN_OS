# WARREN COMPOST CALCULUS — the Law of the Unforgetting Garden

```yaml
artifact:   WARREN_COMPOST_CALCULUS_V1
derives_from: THEOREM_PHI_CONTRACTION_FLOOR_V1 (same repo, proved, tested 7/7)
consumer:   apps/goblin-warren (spec only — this file writes no app code)
discipline: helen-theorem-forge
authority:  false · canon: false · ship: false · ledger_effect: none
claims:     Tier I (three laws, proved) · Tier II (design predictions)
            · Tier III (goblin flavor, labeled)
```

## 1. One state, one flow (the whole theory in four lines)

Every remembered thing in the Warren — a choice, a bug named Gerald, an
argument, a toxicity spike — is a **trace** with two coordinates:

    s = (ℓ, w)      ℓ = lesson mass (what the Receipt Forge extracted)
                    w = detail mass (the vivid, decaying rest)

Between player actions the trace evolves under the φ-schedule of the
math_to_face scaffold, with the lesson subspace as anchor (Π):

    ℓ̇ = 0,        ẇ = −φ^(−t) · w            (t = age of the trace)

By the φ-Contraction Floor theorem this has the **closed form**

    ℓ(t) = ℓ₀
    w(t) = w₀ · exp( −(1 − φ^(−t)) / ln φ )   →   w(∞) = c_φ · w₀

    c_φ = e^(−1/ln φ) = 0.125169442295…   (the floor: ≈ 1/8 survives forever)

## 2. The three player verbs as operators (Tier I)

The Warren's choice triad maps onto the algebra:

| Verb | Operator on (ℓ, w) | Meaning |
|---|---|---|
| **HOLD IT**    | identity — let the flow run | "It stays inert." Detail fades to its floor, never to zero. |
| **TRY IT**     | (ℓ, w) → (ℓ, w + β·w) then spawn child trace | Realization re-excites detail and creates consequences. |
| **COMPOST IT** | (ℓ, w) → (ℓ + κ·w, ρ·w), 0 ≤ ρ < 1, κ > 0 | Detail is *transferred* into lesson. The only floor-breaking move. |

## 3. The three laws (Tier I — each is a two-line corollary of the Floor)

**LAW 1 — Callback Guarantee ("Receipt Glows" is always possible).**
Under HOLD, salience σ(t) = ℓ₀ + w(t) ≥ ℓ₀ + c_φ·w₀ for all t.
Hence any trace with initial salience s₀ ≥ θ/c_φ stays forever above a
callback threshold θ. *Test gate T9 ("second event references first") is
satisfiable at ANY later time, not just soon after* — the Warren's promise
"your small choices matter" is a theorem, not a hope.
*Proof:* w(t) is decreasing with limit c_φ w₀ > 0 (Floor thm (c)); ℓ constant. ∎

**LAW 2 — Compost Necessity ("the garden does not clean itself").**
A toxicity trace (pure detail, w₀ > 0) can never fall below c_φ·w₀ by
waiting. Only COMPOST reduces it below the floor: after k composts with
ratio ρ, the residue is bounded by ρᵏ·w₀. Passive decay is capped at an
8× reduction; active goblins are mathematically required.
*Proof:* HOLD's factor is bounded below by c_φ (Floor thm); COMPOST multiplies
w by ρ each application; compose. ∎

**LAW 3 — Lesson Monotonicity + a backed currency ("mistakes melt into lessons").**
ℓ is non-decreasing under all three verbs, so total extracted wisdom only
grows. Define ZOL issuance as λ × (detail mass moved through compost):

    ΔZOL = λ · κ · w_at_compost

**Conservation condition (required):** κ ≤ 1 − ρ — compost may transfer at
most the detail it destroys. (κ = 1 − ρ is *mass-conserving compost*:
ℓ + w exactly invariant under the verb.) Under this condition, cumulative
ZOL ≤ λ · (total detail ever deposited): **ZOL is backed by composted
detail — no learning, no minting, no inflation.** The wallet is an audit of
the compost heap.
*Proof:* each compost removes (1−ρ)w from the detail pool and credits κw ≤
(1−ρ)w of lesson; total credits ≤ total detail removed ≤ total deposited. ∎

*Correction receipt (Law 5, caught pre-commit by the witness test):* the
first draft omitted the condition and claimed the bound for any κ. With
κ > 1−ρ the same detail is double-counted and the bound FAILS — the witness
suite keeps this as an explicit negative test. The condition is load-bearing.

## 4. Why this is a gift to the implementation (Tier II)

The closed form makes the whole memory field **lazy and backend-free** —
exactly what the iPhone V1 tech stack (localStorage, no backend, no ticks)
requires. Store only `(ℓ, w₀, born_at, composts[])`; compute on read:

```js
// Warren memory field — evaluate salience on demand; no timers, no ticks.
const LN_PHI = Math.log((1 + Math.sqrt(5)) / 2);          // 0.4812118250596…
const C_PHI  = Math.exp(-1 / LN_PHI);                     // 0.1251694422953…
const detailAt = (w0, ageSec, T = 60) =>                  // T: game-time scale
  w0 * Math.exp(-(1 - Math.pow(1/1.6180339887498949, ageSec / T)) / LN_PHI);
const salience = (tr, now) =>
  tr.lesson + tr.composts.reduce((w, c) => w * c.rho,
              detailAt(tr.w0, (now - tr.born_at) / 1000));
```

Predictions this spec makes checkable (Tier II, falsifiable in the app):
1. With θ = 0.10·s₀ as the "Receipt Glows" threshold, **every** trace stays
   callback-eligible forever (since c_φ ≈ 0.125 > 0.10). Set θ = 0.15·s₀ and
   only traces with ℓ₀ ≥ 0.025·s₀ (some lesson extracted) remain eligible —
   a tunable design dial with an exact formula: eligible ⇔ ℓ₀ ≥ θ − c_φ·w₀.
2. Garden toxicity after a spike of size w₀, left alone, plateaus at
   ≈ 0.125·w₀ — visibly non-zero on the status board. One compost at
   ρ = 0.3 drops the plateau to ≈ 0.038·w₀. Players will discover the floor
   empirically; the tooltip can then teach the real theorem.
3. ZOL supply curve is bounded by λκ × Σ deposits — the economy cannot run
   away regardless of play pattern.

## 5. Goblin flavor (Tier III — for Lulu's post-it corner, no claims)

> The Tree keeps an eighth of everything, forever.
> Waiting fades a memory to its seed; only compost turns it into soil.
> ZOL does not grow on trees — it grows on what you composted.
> The Warren remembers, because the mathematics cannot forget.

## 6. Honest boundaries

- The Warren is a **playable sandbox** (its own banner: NO CLAIM · NO SHIP ·
  NO ADMISSION · NO LEDGER EFFECT). This calculus is game law, not world law.
- Nothing here claims pedagogy outcomes, psychology, or memory science.
  It claims: *if* the app uses this field, *then* Laws 1–3 hold exactly.
- localStorage is not the HELEN ledger. Salience is not a receipt.

## 7. Witnesses

    mathematical : Laws 1–3 proofs above (two-liners over the Floor theorem)
    artifact     : test_warren_compost_calculus.py — 6/6 stdlib checks
                   (floor plateau, compost breaks floor, callback eligibility
                   formula, lesson monotonicity, ZOL backing bound,
                   closed-form ≡ Euler product agreement)
    external     : none — required before any promotion beyond spec

## 8. Ledger line

```
[ARTIFACT] WARREN_COMPOST_CALCULUS_V1
tier-I  : three laws (callback guarantee / compost necessity / lesson
          monotonicity + backed ZOL), proved from the phi-contraction floor
tier-II : thresholds & plateaus as falsifiable app predictions; lazy
          closed-form evaluation (no backend, no ticks) fits iPhone V1 stack
tier-III: goblin flavor, labeled
status  : reported · operator seal : pending
```

*One theorem upstream, three laws downstream, zero new axioms. The compost
heap is the proof state.*
