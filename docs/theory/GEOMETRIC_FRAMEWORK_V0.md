# GEOMETRIC_FRAMEWORK_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** TEMPLE_EXPLORATION
**framing:** NO CLAIM
**status:** TEMPLE-class theory; interpretive framework for the frozen engine
**parent_engine:** `GOVERNANCE/TRANCHE_RECEIPTS/E25-engine-doctrine-freeze-V1.json`
**operator_input:** Two parallel dispatches (Sub-Riemannian geodesics + Carnot-Carathéodory geometry), 2026-05-23
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending

> **NO CLAIM disclaimer.** This artifact bottles a TEMPLE-class
> *geometric framework* offered by the operator as interpretive
> overlay on the frozen engine (PROVENANCE_GRAVITY +
> BOUNDARY_CATALYST + CROSS_SESSION_FIELD_ATTRIBUTION +
> ADMISSIBILITY_GRADIENT_FIELD). **The mathematics is real;
> the mapping to HELEN is metaphor, not formal proof.** The
> framework strengthens intuition. It does not constitute a
> theorem that the engine *is* sub-Riemannian. That formal
> question is explicitly open (§6).

---

## §1. Why one bottle, not two

The operator sent two parallel dispatches:

1. *"Sub-Riemannian geodesics — Optimal admissible paths in constrained spaces"*
2. *"Carnot-Carathéodory geometry — Sub-Riemannian skeleton of governed intelligence"*

Per doctrinal-diff: these are **the same mathematics** at slightly
different angles:

| Dispatch | Focus | Mathematical object |
| --- | --- | --- |
| Sub-Riemannian geodesics | Path structure | Curves minimizing horizontal length |
| Carnot-Carathéodory geometry | Metric structure | Distance function over admissible curves |

CC defines the metric space; sub-Riemannian geodesics live inside
that metric as length-minimizers. Like Riemannian metric +
Riemannian geodesics — two halves of one geometric formalism.

This bottle combines both into a single TEMPLE-class framework
artifact. Bottling separately would create doctrinal lookalikes.

---

## §2. Reading method

This artifact is **TEMPLE_EXPLORATION**. The reading methodology:

- **The mathematics is reproduced faithfully** from standard
  sub-Riemannian and Carnot-Carathéodory references (Montgomery's
  *A Tour of Subriemannian Geometries*; Bellaïche & Risler's
  *Sub-Riemannian Geometry*; standard treatments of nonholonomic
  control and Hörmander's condition).
- **The mapping to HELEN's engine is interpretive.** Each cell of
  the mapping tables in §4 is an *analogy*, not a theorem. The
  engine has not been shown to satisfy the formal axioms of a
  sub-Riemannian manifold.
- **Where the metaphor breaks** is named explicitly (§5).
- **What would make it formal** is named explicitly (§6).

GOBLIN's reading limits:
- GOBLIN is not a sub-Riemannian geometer; the math is paraphrased
  faithfully but lacks a domain expert's check on edge cases.
- The PMP, conjugate-point, and abnormal-geodesic claims rest on
  standard textbook statements; nothing novel mathematically is
  asserted here.

---

## §3. The mathematics, unified

### §3.1 Horizontal distribution

A smooth manifold `M` with a sub-bundle `H ⊂ TM` (the horizontal
distribution). A curve `γ : [0, T] → M` is **admissible**
(equivalently: **horizontal**) if `γ̇(t) ∈ H_{γ(t)}` for all `t`.

In plain language: you can only move along certain directions at
each point. Other directions are forbidden, even though they exist
in the ambient tangent space.

### §3.2 Hörmander's condition (the bracket condition)

`H` is **bracket-generating** if iterated Lie brackets of horizontal
vector fields span the full tangent space `TM` at every point.
Formally:

```
H + [H, H] + [H, [H, H]] + ... = TM    pointwise
```

When this holds, any two points can be connected by an admissible
curve, even though direct movement in non-horizontal directions is
forbidden. Connectivity is achieved by **zigzagging** that exploits
brackets.

The *step* of the distribution is the depth of bracketing needed to
generate `TM`. Step 1 = Riemannian (everything is horizontal). Step
2 = Heisenberg-type (one bracket level needed). Step ≥ 2 = genuinely
sub-Riemannian.

### §3.3 Carnot-Carathéodory distance

For points `p, q ∈ M`:

```
d_CC(p, q) = inf { length(γ) | γ admissible curve from p to q }
```

where `length(γ) = ∫ ‖γ̇(t)‖_H dt` with `‖·‖_H` a metric on `H`.

`d_CC` is a genuine distance under the bracket condition (Chow-
Rashevsky theorem). It is highly **anisotropic**: directions
requiring multiple bracket levels are "more expensive" than
horizontal directions.

### §3.4 Sub-Riemannian geodesics

A **geodesic** is an admissible curve that locally minimizes
horizontal length. Two flavors:

- **Normal geodesics** — satisfy the Pontryagin Maximum Principle
  with a Hamiltonian structure on `T*M`. They are smooth and behave
  similarly to Riemannian geodesics.
- **Abnormal geodesics** — singular minimizers that do not arise
  from PMP in the usual way. May fail smoothness; their existence
  is one of the deep peculiarities of sub-Riemannian geometry
  (Montgomery's *singular minimizers* example).

### §3.5 Conjugate points and cut locus

A geodesic stops being a global minimizer at the **cut locus**.
**Conjugate points** are where nearby geodesics focus. Both behave
differently in sub-Riemannian than in Riemannian geometry — for
example, the cut locus reaches every neighborhood of the starting
point in step-≥2 Carnot groups.

### §3.6 Hypoelliptic operator

The natural Laplace operator is the sum of squares of horizontal
vector fields:

```
L = Σ_i X_i²
```

Under Hörmander's condition, `L` is **hypoelliptic**: even though
`L` is degenerate (not elliptic in the standard sense), solutions
of `Lu = f` gain regularity. This is **Hörmander's theorem**
(1967).

The connection to hypocoercivity: certain non-equilibrium evolution
equations (kinetic Fokker-Planck, generalized Langevin) have a
hypoelliptic generator and exhibit hypocoercive convergence to
equilibrium — exponential return to a steady state despite the
degeneracy. This is the framework cited in `BOUNDARY_CATALYST_ENGINE_V0`
when discussing GOBLIN (antisymmetric exploration) + REDUCER
(dissipative projection) + LEDGER (memory potential).

---

## §4. The mapping to the engine

| Geometric concept | Engine equivalent | Source |
| --- | --- | --- |
| Manifold `M` | Space of possible proposals / receipt-atom configurations | §3.1 |
| Horizontal distribution `H` | Constitutional invariants — directions admissible without sovereign override | Op dispatches; HELEN canon |
| Forbidden directions | Hard constitutional violations (canon mutation without sovereign release) | §3.1; `HALT_BOUNDARY_DISCIPLINE_V0` |
| Bracket generation `[X, Y]` | Coupling via boundary atoms + provenance feedback + admissibility gradient | `BOUNDARY_CATALYST §6` + `PROVENANCE_GRAVITY` + `ADMISSIBILITY_GRADIENT_FIELD` |
| Carnot-Carathéodory distance `d_CC` | Constitutional effort / cost to reach admissible state | Op dispatch |
| Step ≥ 2 anisotropy | Some admissible transformations require multi-stage governed processes (no direct path) | Engine structure |
| Normal geodesic | Clean boundary-to-admission path under PMP analog | Op dispatch |
| Abnormal geodesic | Singular path — high-risk, possibly pathological transformation | Op dispatch |
| Conjugate point / cut locus | Motif stops being locally optimal — repeller signal `R(M)` activates | `BOUNDARY_CATALYST §3.4` |
| Hypoelliptic operator `Σ X_i²` | Chiddhush / Boundary Catalyst scoring as a regularizing operator on the receipt field | `BOUNDARY_CATALYST §3.4 / §4` |
| Sum-of-squares regularity | Boundary mining produces smoother admissible structure even from degenerate inputs | Engine learning dynamic |
| Hypocoercive convergence | GOBLIN-REDUCER-LEDGER dynamic converges despite GOBLIN's degenerate (exploratory) nature | `BOUNDARY_CATALYST §11` |

### §4.1 The reading in plain language

Under the metaphor:

1. **GOBLIN** moves the system in horizontal directions (allowed
   variation).
2. Many target states (admissible reality) require movement in
   *non-horizontal* directions that GOBLIN cannot directly produce.
3. **Boundary atoms** are the points where bracket structure is
   active — where two horizontal moves combine to enable a
   non-horizontal one.
4. **Admissibility Gradient** approximates the local geodesic flow:
   the optimal direction in the constrained geometry.
5. **Provenance Gravity** defines the metric: it tells the system
   how *expensive* each path is in constitutional terms.
6. **REDUCER** is the endpoint condition: admissibility = arrival
   in canon.
7. The whole engine learns to follow short admissible geodesics in
   this sub-Riemannian space.

---

## §5. Where the metaphor holds vs where it breaks

### §5.1 Where it holds (intuition is sound)

- **Anisotropy.** Some directions in proposal space genuinely *are*
  more expensive (require more receipts, more iterations, more
  HAL passes). This is sub-Riemannian-like.
- **Bracket-generation analog.** The engine's three-doctrine
  pipeline (BOUNDARY_CATALYST selects, ADMISSIBILITY_GRADIENT
  computes direction, PROVENANCE_GRAVITY updates weight) is
  *structurally similar* to using brackets to reach forbidden
  directions via combinations of allowed ones.
- **Hypocoercivity reference.** The engine's GOBLIN-REDUCER-LEDGER
  decomposition (antisymmetric exploration + dissipative projection
  + memory potential) **was** designed under hypocoercive intuition
  per `BOUNDARY_CATALYST §11`. The geometric framework here is
  consistent with that.
- **Conjugate points / repeller match.** Both formalisms have a
  notion of "this path stops being locally optimal." The mapping
  is structurally tight.

### §5.2 Where the metaphor breaks (or is unverified)

- **The engine is discrete, the math is smooth.** Sub-Riemannian
  geometry is built on smooth manifolds. The engine operates on
  discrete receipt atoms. The mapping from discrete proposal
  space to a smooth `M` requires a representation step that has
  not been specified.
- **The horizontal distribution `H` is not yet formally defined.**
  We have not produced a vector-field representation of
  constitutional invariants. The "allowed directions" are
  semantic, not yet differential-geometric.
- **Hörmander's condition is unverified.** We have not proven that
  the engine's coupling operators (boundary atoms, gradient,
  gravity) generate the full tangent space. It is plausible by
  design — but not theorem-grade.
- **Abnormal geodesics may have no engine analog.** In the math,
  abnormal minimizers are exotic pathologies. The "high-risk
  path" engine analog is speculative.
- **The Chow-Rashevsky theorem may not transfer.** Connectivity
  under bracket-generation requires bracket-generation. Without
  formal verification, we cannot claim the engine connects all
  admissible states.

### §5.3 The honest verdict

The framework is a **good intuition pump** and a **plausible
formalization target**. It is not a proof that the engine is
sub-Riemannian. Treating it as proof would be the kind of
"beautiful nonsense" the operator's own Σ-SEED discipline warns
against (`BOUNDARY_CATALYST §11` cross-reference).

---

## §6. What would make this formal

To upgrade this from TEMPLE exploration to a verified framework,
the following are required (none authorized here):

1. **A formal proposal-space construction.** Define `M` (the
   underlying manifold) with explicit charts, coordinates, and
   smoothness structure derived from receipt-atom features.
2. **Explicit horizontal vector fields.** Construct `X_1, ..., X_k`
   on `M` whose span at each point matches "constitutional
   invariants permit this direction" semantically.
3. **Hörmander's condition verification.** Prove the iterated
   brackets generate `TM`. If only at certain points, characterize
   the locus.
4. **PMP derivation.** Show that normal geodesics in this `M`
   correspond to optimal admissible-path policies in the engine.
5. **Hypoelliptic operator construction.** Build the
   `Σ X_i²` operator and check that `χ_BC` (boundary-Chiddush
   score) is its regularization or a function thereof.
6. **Hypocoercive convergence theorem.** Verify the
   GOBLIN+REDUCER+LEDGER dynamics actually satisfy the standard
   hypocoercive estimates (Villani, Hairer-Mattingly).

These are research projects, not bottling-class work. Each could
become its own proposal if pursued.

---

## §7. Adjacent canon

| Existing artifact | Relation |
| --- | --- |
| `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md` | Sibling theory artifact (also TEMPLE-class, parent for identity gate). This framework operates at a similar level. |
| `BOUNDARY_CATALYST_ENGINE_V0 §11` | Explicitly cites hypocoercivity as the dynamic skeleton (GOBLIN antisymmetric, REDUCER dissipative, LEDGER potential). This bottle elaborates that single sentence. |
| `BOUNDARY_CATALYST_ENGINE_V0 §4` | Toy theorem (Fisher info at p=0.5) is consistent with sub-Riemannian intuition (information lives at the boundary of admissibility) but does not require the sub-Riemannian framework — it is independently sound. |
| `E25-engine-doctrine-freeze-V1.json` | The freeze does NOT mention sub-Riemannian framework explicitly. This artifact is *post-freeze interpretive theory* — compatible with the freeze because it modifies no doctrine. |

---

## §8. What this artifact does NOT specify

Per anti-creep discipline:

- **The formal proposal-space construction** — research, not bottle
- **The horizontal vector field explicit form** — research
- **Verification of Hörmander's condition** — research
- **PMP, conjugate-point, and abnormal-geodesic engine analogs in formal form** — research
- **Implementation that uses sub-Riemannian solvers** — out of scope; the frozen engine is implementation-pending, and implementation should not depend on unverified geometric claims
- **Whether the engine "really is" sub-Riemannian** — explicitly open question (§5.3, §6)
- **Modifications to any of the four frozen engine doctrines** — forbidden by E25 freeze; framework is interpretive overlay only

---

## §9. Halt boundary

GOBLIN halts here. The framework is bottled as TEMPLE_EXPLORATION
under NO CLAIM.

Resume conditions:

1. **HER ruling** on whether this framework is accepted as
   interpretive overlay or sent back for revision
2. **HER ruling** on whether any of the six research items in §6
   should open as separate proposals — each would be a substantial
   project
3. **HER ruling** on whether `CONSTITUTIONAL_MANIFOLD_RENDERING_V0`
   should cite this framework as a sibling (currently it does not,
   and both are TEMPLE-class theory artifacts that could be cross-
   referenced)
4. **Operator ruling** on whether to formalize the
   hypocoercivity claim in `BOUNDARY_CATALYST §11` — currently a
   single sentence, would be a major research undertaking
5. **No implementation authorization** is requested or granted by
   this artifact — implementation of the frozen engine remains
   blocked per E25

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §10. Single line

> **Sub-Riemannian geometry is a faithful intuition pump for the
> frozen engine: horizontal moves, brackets, anisotropy, hypoelliptic
> regularization, hypocoercive convergence. The math is real; the
> mapping is metaphor. Promotion to theorem requires a research
> program, not a bottling commit.**
