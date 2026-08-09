# ETA — Epistemic Transformation–Abstraction Calculus V0.1

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=false · admission=none · ledger_effect=none
class         : NON_SOVEREIGN_MATH · non-canonical theoretical baseline
status        : PROPOSAL — consolidated from ~15 upstream relay rounds
date_recorded : 2026-08-09
supersedes    : the scattered "Epistemic Galois" / ETA relay transcripts (metaphor-stage)
```

## 0. What this is — and what it is not

This is a **mathematical baseline**, not a theorem-of-victory and not a HELEN
canon claim. It consolidates a research program that converged from an informal
"Epistemic Galois Theory" metaphor into a typed calculus. Every result below is
stated **relative to declared assumptions**. Nothing here is admitted, sealed, or
sovereign.

The single load-bearing firewall, carried from the relay corpus, is:

```
ETAAdm(T)  ⇏  Permission(T)  ⇏  Execution(T)  ⇏  Admission(T)
```

Mathematical admissibility and institutional authority are **different types**.
ETA can certify that a transformation is sound, invariant-preserving, and
replay-natural. It cannot grant authority. The Gate calculus
(`experiments/helen_mvp_kernel/helen_os/kernel/promotion_gate.py`) remains the
only admission path.

The central question the program answers is a shift of frame:

```
NOT  "which transformations preserve invariants?"
BUT  "which structures survive transport between representations?"
```

---

## 1. The typed triple

```
ETA = ( GC_sem , GC_inv , R )
```

Three **distinct** structures. They are not one object until compatibility laws
connect them; writing `ETA = GC_sem + GC_inv + R` is mnemonic only.

**Semantic engine** — abstract interpretation:
```
GC_sem = (C, A, α, γ),    α ⊣ γ        (α: C⇄A :γ, monotone, adjoint)
```
`C` = concrete evidence domain, `A` = abstract claim domain.

**Symmetry engine** — transformation/invariant antitone polarity (FCA):
```
GC_inv = ( P(𝔗), P(𝔉), Φ, Ψ )
  Φ(S) = { f ∈ 𝔉 : f∘T = f  ∀T∈S }
  Ψ(Q) = { T ∈ 𝔗 : f∘T = f  ∀f∈Q }
  S ⊆ Ψ(Q)  ⟺  Q ⊆ Φ(S)
```

**Replay engine** — historical realization:
```
R : L → E        (histories → reconstructed epistemic states)
```

---

## 2. Bridge Soundness  —  PROVED

For monotone `T_C: C→C`, `T_A: A→A` under `α ⊣ γ`:

```
T_C γ ≤ γ T_A   ⟺   α T_C ≤ T_A α                                    (B)
```

Proof uses the unit `1_C ≤ γα` (forward, via monotonicity of `T_C`) and the
counit `αγ ≤ 1_A` (reverse, via monotonicity of `T_A`) — the two directions use
the monotonicities asymmetrically. This is standard adjunction machinery, not an
open HELEN conjecture.

```
BRIDGE_SOUND = PROVED  (relative to declared posets, adjunction, monotonicity)
```

---

## 3. Canonical Best Correct Approximation  —  PROVED

For fixed monotone `T_C`, the canonical abstract transformer is
```
T_C♯ := α T_C γ                    (notation exposes dependency on T_C)
```
It is **sound** (`α T_C ≤ T_C♯ α`, via the unit) and **least** among sound
abstract transformers (`α T_C ≤ T_A α ⇒ T_C♯ ≤ T_A`, via the counit). Hence
`α T_C γ` = the least sound abstract transformer of `T_C`.

**Four-tier typology** (BCA and exactness are *not* interchangeable):
```
α T_C ⋠ T_A α    → UNSOUND
α T_C ≤ T_A α    → SOUND
T_A = α T_C γ    → BEST CORRECT APPROXIMATION
α T_C = T_A α    → FORWARD EXACT
```
For the canonical transformer, exactness reduces to
```
α T_C = α T_C γ α                                                     (FC)   [OPEN characterization]
```

**Terminology correction (referee-safe):** the order relations
`c ≤ γα(c)` and `α T_C(c) ≤ T_A α(c)` witness *possible imprecision / non-exactness*,
they do **not** quantify information loss.
```
order non-exactness  ≠  quantified precision loss
```
A scalar loss needs extra structure (metric, valuation, lattice rank, measure,
information functional). Absent that, "imprecision" is the safe term. Likewise
any "thermodynamic" reading (entropy/dissipation) is **interpretive analogy
only** — ETA defines closure and non-exact transport, not entropy.

---

## 4. Internal composition  —  PROVED (three axes, separately)

Each axis composes internally, under compatible typing and a compositionally
closed ambient class:

- **Semantic soundness composes.** `α T_1 ≤ A_1 α`, `α T_2 ≤ A_2 α` (with `A_2`
  monotone) ⇒ `α T_2T_1 ≤ A_2A_1 α`.
- **Institutional invariance composes.** `f∘(T_2T_1) = f∘T_1 = f`, so
  `Ψ(Q_I)` is a **stabilizer submonoid** (contains `id`, closed under `∘`).
- **Strict replay naturality composes** (see §6).

The retired false problem: internal composition is *not* the frontier.
```
InternalClosure  ⇏  CrossStructureTransport
```
That implication-gap is the actual research object.

---

## 5. ρ-stability, Galois insertion, and the composition obstruction

Write the concrete closure `ρ := γα = K_C`. In general `B = α(–)γ` is **not**
a functor:
```
B(T_2 T_1) = α T_2 T_1 γ      vs      B(T_2) B(T_1) = α T_2 (γα) T_1 γ
```
The inserted `ρ` is the obstruction ⇒ `BCA ⇏ Functoriality` (referee-safe form:
"not guaranteed by the Galois connection alone").

**Galois insertion (GI)** — `αγ = id_A` (α surjective / γ injective) — removes
the *identity* problem: `B(id_C) = αγ = id_A`. It does **not** remove the
composition obstruction; `ρ` still sits between `T_1` and `T_2`.

**ρ-stability class** (the earned bridge):
```
𝔗_ρ = { T : T(Fix ρ) ⊆ Fix ρ }          Fix ρ = A♯ = { c : ρ(c)=c }
```
Under GI, `B` restricted to ρ-stable transformations **is a functor**:
representable semantics stay representable, so the closure is observationally
invisible after abstraction.

**Anti-laundering condition** for invariant transport: an institutional
observable `f` transports iff `f∘ρ = f` — if closing under `ρ` changes `f`, the
abstraction is destroying an institutionally relevant fact.

**Counterexample — PROVED as existence-of-failure (not necessity).**
`C={0,1,2}`, `A={0,2}`, GI with `Fix ρ={0,2}`; `T_1(c)=1` (violates ρ-stability),
`T_2=(0↦0,1↦0,2↦2)`. Then `α T_2 T_1 γ(0)=0` but `α T_2 ρ T_1 γ(0)=2`. This
proves composition can fail *outside* ρ-stability on 3 states; it does **not**
prove ρ-stability is universally necessary (a fixed pair may satisfy the
observational equality without it — that needs a separation hypothesis).

---

## 6. Replay: free-monoid baseline and the paired algebra  —  PROVED

**Ledger model V0.1** = free monoid `L₀ = E*` (append-only, total order):
```
R(s,ε)=s,   R(s,we)=δ(R(s,w),e),   R(s,uv)=R(R(s,u),v)              (monoid action)
```

**Replay naturality (strengthened):** `T` is replay-natural iff there exists a
**monoid endomorphism** `T̃ ∈ EndMon(E*)` with
```
T ∘ R = R ∘ T̃                  (unpointed: T·R = R·(T×T̃) separates
                                 ReplayCompatibility from GenesisPreservation)
```
Requiring `T̃` be a monoid endomorphism forbids arbitrary history rewriting.
Pointed form forces `T(s₀)=s₀` (genesis immutability) via `T̃(ε)=ε`.

**Paired transformation monoid** — the correct object is `(T, T̃)`, not `T` alone:
```
𝔗̂_ETA = { (T,T̃) : T ∈ 𝔗_ρ ∩ Ψ(Q_I),  T̃ ∈ EndMon(E*),  T·R = R·(T×T̃) }
(T_2,T̃_2)·(T_1,T̃_1) = (T_2T_1, T̃_2 T̃_1)          closed; id = (id_S, id_{E*})
```

**ETA-admissible monoid** = intersection of three separately-defined submonoids
(not "orthogonal" — no independence relation is proved):
```
𝔗_ETA = 𝔗_ρ  ∩  Ψ(Q_I)  ∩  𝔗_R              is a submonoid
```

**Strict units / reversible core.** `(T,T̃) ∈ U(𝔗̂_ETA)` requires
`T ∈ Aut(S)` AND `T̃ ∈ AutMon(E*)`, with both inverses preserving all three
membranes. For the free monoid `AutMon(E*) ≅ Sym(E)` — reversible history maps
**relabel primitive event symbols bijectively, preserving word order**; they
cannot reorder events, delete, or compress.
```
Strict V0.1 reversibility forbids lossy compression inside the free monoid E*.
(scoped to this representation — NOT "all compression is irreversible")
```

**Lift uniqueness — PROVED (conditional).** With
`Λ(T) = { T̃ : T·R = R·(T×T̃) }` and history-faithful replay:
```
HistoryFaithful(R)  ⇒  |Λ(T)| ≤ 1
```
(Replay faithfulness itself is **not** assumed — it is an OPEN property to test.)

---

## 7. Category first, groupoid second

Do **not** postulate an ETA groupoid. Build the category, extract its core:
```
𝓔_ETA        objects = typed epistemic states; morphisms = ETA-admissible T
𝒢_ETA = Core(𝓔_ETA)                    canonical groupoid (invertible core)
Γ_I(x) = Aut_{𝒢_I}(x)                  local symmetry (isotropy) at x
x ~_I y ⟺ 𝒢_I(x,y) ≠ ∅   →  π₀(𝒢_I)   reversible equivalence classes
```
`EGA` (Epistemic Galois Algebra) is the **name of the target**, an emergent
reversible structure — **not** an ETA axiom.
```
ETA metaphor → ETA calculus → transport theory → ETA category → core groupoid → local Aut groups
```

---

## 8. Status table

**PROVED (relative to stated assumptions):**

| Result | Note |
|---|---|
| Bridge Soundness `(B)` | adjunction + monotonicity |
| Canonical BCA `T_C♯ = α T_C γ` | least sound abstract transformer |
| Semantic soundness composition | compatible typing |
| Institutional stabilizer `Ψ(Q_I)` submonoid | `f∘T=f` closure |
| Strict / paired replay composition | typed history endomorphisms |
| Identity preservation by `B` under GI | `αγ = id_A` |
| `B` functor on ρ-stable transformations (GI) | closure observationally invisible |
| Invariant transport under ρ-stability + GI | anti-laundering `f∘ρ=f` |
| Finite counterexample to BCA composition | existence-of-failure only |
| Free-monoid replay action | `R(s,uv)=R(R(s,u),v)` |
| `AutMon(E*) ≅ Sym(E)` | strict history core = relabelling |
| `HistoryFaithful(R) ⇒ |Λ(T)|≤1` | conditional on faithfulness |

**OPEN:**

| Target | Statement |
|---|---|
| Canonical forward exactness | characterize `α T_C = α T_C γ α` |
| `AT` — Abstraction Transport | `T_C ∈ Stab_C(Q_C) ⇒ α T_C γ ∈ Stab_A(β Q_C)`? |
| `RT` — Replay Transport | state-invariant `⇒` ledger-invariant under `R`? |
| `ICT` — Invertible-Core Transport | `T,T⁻¹ ∈ 𝒢_C ⇒ B(T),B(T⁻¹) ∈ 𝒢_A`, `B(T⁻¹)=B(T)⁻¹`? |
| `RIT` — Replay Invertibility Transport | `T̃ ∈ Λ(T) ⇒ T̃⁻¹ ∈ Λ(T⁻¹)`? |
| FCA–BCA compatibility | relate `Ψ∘Φ` closure to `α(–)γ` |
| Replay faithfulness | is `R` injective (per state)? |
| `π_S` injectivity | when does `T` determine a unique `(T,T̃)`? |
| Nontrivial reversible core | do nonidentity two-sided ETA units exist? |
| ρ-stability necessity | separation hypothesis for universal exact composition |

---

## 9. Non-promotion firewall (carried, explicit)

```
InternalClosure     ⇏  CrossStructureTransport
BCA                 ⇏  Exactness
BCA                 ⇏  Functoriality
T invertible        ⇏  B(T)=αTγ invertible
ReplayStateEquality ⇏  HistoryEquality  (unless faithfulness proved)
ETAAdm              ⇏  Authority
```

The sharpest defensible thesis:
```
Sound abstraction does not guarantee structural transport.
```
The next real theorem is a **classification**, not another closure lemma:
which transformations transport through abstraction and replay, and why.

## 10. Scope notes

- The RIEMANN / `H_SCT` spectral material from the same relay corpus is a
  **separate** research testbed, not part of ETA V0.1. It is deliberately
  excluded here; it needs its own falsifier doc, not folding into the calculus.
- Staged roadmap for the ledger model: `V0.1 = E*` (free monoid) →
  `V0.2 = trace monoid` (partial commutation) → `V0.3 = causal DAG` (true
  concurrency + convergent merge). Only V0.1 is consolidated above.

## 11. Status

```
NON_SOVEREIGN_MATH · authority=false · canon=NO_SHIP · ledger_effect=none
Promotion to anything stronger requires an external proof/counterexample pass,
not a prompt asserting the theorem.
🌿 novelty may increase · authority must remain exactly zero
```
