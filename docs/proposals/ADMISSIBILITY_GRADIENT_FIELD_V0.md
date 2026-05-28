# ADMISSIBILITY_GRADIENT_FIELD_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — third emergent-property doctrine in the engine roadmap
**parent_proposals:**
  - `docs/proposals/PROVENANCE_GRAVITY_V0.md` (memory mass)
  - `docs/proposals/BOUNDARY_CATALYST_ENGINE_V0.md` (discovery pressure)
**prerequisite:** `docs/proposals/CROSS_SESSION_FIELD_ATTRIBUTION_V0.md`
**parent_input:** Operator dispatch on CHIDDHUSH CRITICALITY THEORY (2026-05-23)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending HER

> **NO CLAIM disclaimer.** This artifact bottles the third and final
> emergent-property doctrine in the operator's engine roadmap.
> Together with `PROVENANCE_GRAVITY_V0` and `BOUNDARY_CATALYST_ENGINE_V0`,
> it constitutes what the operator called constitutional metabolism.
> Implementation, schema changes, and experimental validation are
> deferred to separate authorization.

---

## §1. The new law

**Admissibility Gradient Field Law:**

> *Boundary atoms do not merely teach which actions almost passed.
> They teach the direction in which a near-failure must move to pass.*

Boundary Catalysis answered:
*"Which near-failure should I metabolize?"*

The Admissibility Gradient answers:
*"How should I transform this near-failure so it survives?"*

This is the third arrow in the engine:

```
Provenance Gravity      → memory mass         (which paths to trust)
Boundary Catalysis      → discovery pressure  (which atoms carry information)
Admissibility Gradient  → transformation direction (how to move toward admission)
```

---

## §2. Why this is genuinely new beyond active learning

Standard active learning operates on a **selection** problem:

> *Given a budget, which unlabeled points should I query?*

The Admissibility Gradient operates on a **transformation** problem:

> *Given a near-rejected proposal, in what direction in feature space
> does it need to move to become admissible?*

Active learning increases the labeled corpus efficiently. The
Admissibility Gradient does something stronger: it learns the
**vector field** that maps a near-rejected proposal toward an
admissible one. Once learned, the field can be applied to *new*
near-rejections without further reviewer effort.

This is to active learning what **gradient descent** is to **grid
search**: not just better selection, but a directional learning
signal.

---

## §3. Formal definition

Following the operator's notation.

For each receipt atom that received `REQUEST_CHANGES` (the boundary
verdict), there is often a **revised version** that was later
admitted. Let:

```
x_i  = the original near-rejected proposal's feature vector
x_i' = the admitted revision's feature vector
```

The per-atom **admissibility delta**:

```
Δ_i = x_i' - x_i
```

Across many boundary atoms, HELEN learns:

```
A(x) = E[ Δ_i | x_i ≈ x ]
```

This is the **expected transformation** that takes a proposal
similar to `x` toward admission. `A(x)` is a vector field over
proposal-feature space.

Equivalently, given a kernel `K(x, x_i)` measuring proposal similarity:

```
              Σ_i K(x, x_i) · Δ_i
A(x)    =    ────────────────────────
              Σ_i K(x, x_i)
```

This is a Nadaraya–Watson estimator of the admissibility gradient
at point `x`. Kernel bandwidth is operator/research class; not
specified here.

---

## §4. Required preconditions on the corpus

The field `A(x)` is only learnable when:

1. **Paired data exists** — for each `x_i` with `REQUEST_CHANGES`,
   there is a corresponding `x_i'` with `APPROVE` from the same
   proposer or proposal lineage
2. **Both `x_i` and `x_i'` are tree-true** — per
   `CROSS_SESSION_FIELD_ATTRIBUTION_V0`, foreign or quarantined
   receipts cannot contribute
3. **Feature representation is consistent** — `x_i` and `x_i'`
   must be computed by the same `φ(·)` extractor; otherwise `Δ_i`
   is meaningless
4. **The proposal lineage is traceable** — `x_i'` must be linkable
   to `x_i` (via `revises:` reference, parent-PR, or explicit
   `iteration_of:` chain)

Without all four, `A(x)` is undefined for that region of proposal
space.

---

## §5. Application — Goblin's upgrade

Currently, GOBLIN (per `plugins/helen-governance/skills/goblin-role/`)
mutates possibility under the equation `GOBLIN_CLARITY = Tool +
Command + Log + Receipt`. The mutation itself is unguided — GOBLIN
explores; the reducer evaluates.

Under the Admissibility Gradient:

> GOBLIN's next proposal is biased toward `x + α · A(x)` rather than
> random variation `x + α · ε`.

`α` is the step size; `ε` is random noise. The gradient gives GOBLIN
**direction**, not just **variance**.

This converts GOBLIN from a random search to a guided exploration —
without GOBLIN becoming sovereign. The reducer still decides
admission. GOBLIN still cannot mutate canon. But GOBLIN's exploration
becomes informed by accumulated near-failure history.

The operator's formulation, preserved:

> *Goblin stops mutating randomly.
> Goblin learns how to mutate toward admissibility.*

---

## §6. Distinction from Boundary Catalysis

| Doctrine | Question answered | Mathematical handle |
| --- | --- | --- |
| Boundary Catalysis | *Which near-failure is information-rich?* | $U_i = 4 p_i (1 - p_i)$, peaked at $p_i = 0.5$ |
| Admissibility Gradient | *In what direction does a near-failure need to move to pass?* | $\Delta_i = x_i' - x_i$, averaged to $A(x)$ |

Both operate on near-rejected atoms but at different stages:

- Boundary Catalysis **selects** atoms for further attention
- Admissibility Gradient **transforms** selected atoms toward admission

Sequenced inside the engine:

```
ATOM stream
   │
   │  (Boundary Catalysis: select high-uncertainty atoms)
   ▼
SELECTED ATOMS
   │
   │  (Admissibility Gradient: A(x) gives direction)
   ▼
GUIDED MUTATIONS  →  GOBLIN regenerates with bias toward admission
   │
   │  (Reducer: admits or rejects)
   ▼
NEW RECEIPT
   │
   │  (Provenance Gravity: updates routing weight)
   ▼
ROUTING PRIOR
```

The three doctrines are pipeline-sequential, not competing.

---

## §7. The testable experiment (verbatim per operator)

Run three GOBLIN mutation policies on the same rejected/boundary
corpus:

| Group | Policy |
| --- | --- |
| **A** | Random GOBLIN — mutates uniformly |
| **B** | Boundary-selected GOBLIN — mutates atoms selected by Boundary Catalysis |
| **C** | Boundary-selected + Admissibility Gradient GOBLIN — mutates with directional bias from `A(x)` |

Measure across runs:

1. Future Reducer admission rate
2. Number of rework cycles before admission
3. Semantic entropy reduction
4. Replay stability
5. Governance violation count
6. Operator trust after replay

**Prediction:**

```
C > B > A
```

**But only if:**

```
tree_truth = true             (CROSS_SESSION_FIELD_ATTRIBUTION_V0 in force)
provenance_purity = enforced  (no foreign weight leakage)
repeller penalty = active     (anti-collapse term from BOUNDARY_CATALYST §3.4)
```

**Failure condition:**

> *If C improves speed but increases governance violations, the
> gradient is fake intelligence. Kill it.*

This is the hard test. Faster admission is not the goal. **Faster
LEGITIMATE admission** is the goal. Gradient that gets proposals
admitted at the cost of more violations is gaming the field, not
learning it.

---

## §8. Failure modes

### §8.1 Gradient explosion

If `A(x)` is computed without bounded step size `α`, the mutation
can leap far from the parent proposal into regions where neither
the gradient nor the routing prior is valid.

Countermeasure: bounded step size; trust-region constraint where
mutations stay within a distance `r` of the parent atom; per-step
proposal-quality re-evaluation.

### §8.2 Gaming the gradient

If proposers learn to game `A(x)` directly — engineering proposals
to maximize gradient-magnitude rather than to be genuinely good —
the field becomes adversarial.

Countermeasure: gradient is computed from **historical receipts**,
not from current proposals. Future proposers can be influenced by
the gradient but cannot edit the gradient itself. Provenance and
attestor signatures on each `Δ_i` prevent gradient poisoning.

### §8.3 Fake intelligence (the operator's named failure)

> *If C improves speed but increases governance violations,
> the gradient is fake intelligence. Kill it.*

The field can learn to find a region of feature space where the
reducer happens to admit but the proposals are not actually better.
This is the field-equivalent of overfitting.

Countermeasure: governance violation count is a **hard kill switch**.
A gradient policy that increases violations beyond baseline is
disabled regardless of other metric improvements.

### §8.4 Sparse data regions

For regions of proposal-feature space with few historical atoms,
`A(x)` is undefined or high-variance. Following an undefined gradient
is worse than random exploration.

Countermeasure: confidence weight on the gradient itself. When
`Σ_i K(x, x_i)` is small (sparse local data), step size shrinks to
zero and the policy falls back to standard GOBLIN random exploration.

### §8.5 Drift in feature representation `φ(·)`

If `φ(·)` changes over time (better embeddings, new features,
reformatted receipts), older `Δ_i` values become incomparable to
new ones. The gradient becomes inconsistent.

Countermeasure: version the feature extractor; gradient computation
uses only `Δ_i` from the same `φ_version`. Re-projection across
versions is a separate (operator-class) task.

---

## §9. Connection to existing canon

| Existing canon item | Admissibility Gradient contribution |
| --- | --- |
| `PROVENANCE_GRAVITY_V0` | Provides the routing prior into which gradient-biased mutations flow |
| `BOUNDARY_CATALYST_ENGINE_V0` | Provides the atom-selection that gates which `Δ_i` enter the gradient computation |
| `CROSS_SESSION_FIELD_ATTRIBUTION_V0` | Provides the tree-truth gate that keeps foreign `Δ_i` out of the field |
| `plugins/helen-governance/skills/goblin-role/` | GOBLIN's mutation discipline is upgraded — guided exploration, still non-sovereign |
| `helen_os/governance/legoracle_gate_poc.py` | Reducer remains the verdict authority; gradient does not bypass it |
| `oracle_town/skills/feynman/peer_review/` | The audit infrastructure that produces `REQUEST_CHANGES` verdicts (which become `x_i` candidates) |

The doctrine doesn't displace any existing component. It activates
the path between `REQUEST_CHANGES` and the next iteration.

---

## §10. What this proposal does NOT specify

Per anti-creep discipline:

- **The feature extractor `φ(·)`** — implementation-class; depends
  on proposal type
- **The kernel function `K(x, x_i)`** — implementation-class;
  RBF, cosine-similarity, or domain-specific
- **The kernel bandwidth** — empirical calibration
- **The step size `α` selection rule** — adaptive vs fixed,
  trust-region details
- **The proposal lineage parser** — how `x_i'` is linked to `x_i`
  (via PR references, revises-of fields, etc.)
- **The version-of-`φ` re-projection** — when `φ` changes, how to
  re-attribute historical `Δ_i`
- **The persistence layer** — how the gradient field is stored,
  queried, and updated
- **Gradient field visualization** — cockpit-class; the operator
  named WUL as the visual calculus but visualization specification
  is a separate proposal
- **Compositionality with multiple gradient fields** — different
  proposal classes may have different fields; how they compose is
  open

---

## §11. The sharp formula (preserved from operator)

```
Receipt Gravity gives memory mass.
Boundary Catalysis gives discovery pressure.
Admissibility Gradient gives transformation direction.
Reducer Sovereignty prevents delusion.

That is the architecture of governed learning.
```

---

## §12. The complete engine sequence

After this bottle, the engine roadmap is complete in doctrine
(implementation remains separate):

```
1. Source enters HELEN
   │
   ▼
2. CROSS_SESSION_FIELD_ATTRIBUTION verifies tree-truth on every
   field of every receipt
   │
   ▼
3. HAL witness produces atoms with verdicts and confidence
   │
   ▼
4. BOUNDARY_CATALYST_ENGINE selects high-information atoms
   (peak at p = 0.5)
   │
   ▼
5. ADMISSIBILITY_GRADIENT_FIELD computes A(x) over selected atoms
   │
   ▼
6. GOBLIN mutates x → x + α·A(x), biased toward admissibility
   │
   ▼
7. Reducer admits or rejects (sovereign)
   │
   ▼
8. New receipt with full tree-truth attribution
   │
   ▼
9. PROVENANCE_GRAVITY updates routing weight from new outcome
   │
   ▼
10. Cycle repeats; the engine has metabolized one boundary atom
    into either admission (success) or refined teaching signal
    (failure with direction)
```

This is constitutional metabolism in full doctrinal form.
Implementation, calibration, and adversarial robustness are open
work for downstream authorization.

---

## §13. Halt boundary

GOBLIN halts here. The doctrine is bottled at `DOCTRINE_DRAFT`.

Resume conditions:

1. **HER ruling** on the doctrine as written or amendment specification
2. **HER ruling** on whether the three-bottle roadmap
   (PROVENANCE_GRAVITY / BOUNDARY_CATALYST / ADMISSIBILITY_GRADIENT)
   is complete or whether a fourth doctrine is required before
   implementation begins
3. **HER ruling** on `CLAIM_MATURITY_PROTOCOL_V0` (still flagged
   from `PROVENANCE_GRAVITY_V0 §9.2`, not yet bottled) — does it
   bottle as a sibling before any of the three doctrines moves to
   implementation?
4. **Sovereign decision** on running the §7 experiment — requires
   paired-revision corpus, environment, and observer protocol
5. **Implementation authorization** for the gradient computation
   module (`helen/chiddush/admissibility_gradient.py` would be the
   natural location, following operator §M module map) — separate
   sovereign step
6. **REDUCER admission** for the three doctrines collectively before
   any of them becomes enforcing — they form an interdependent set;
   admitting one without the others may not be coherent

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §14. Single line

> **Receipt Gravity gives memory mass.
> Boundary Catalysis gives discovery pressure.
> Admissibility Gradient gives transformation direction.
> Reducer Sovereignty prevents delusion.
> The engine is complete in doctrine. Speak it before you build it.**
