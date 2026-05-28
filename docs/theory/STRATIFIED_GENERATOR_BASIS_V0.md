# STRATIFIED_GENERATOR_BASIS_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** TEMPLE_EXPLORATION (algebraic diagnostic spec)
**framing:** NO CLAIM
**status:** Multi-layer generalization of the Heisenberg bracket test
**operator_directive:** "freeze the algebraic companion" (2026-05-23)
**parent_theory:**
  - `docs/theory/HEISENBERG_BRACKET_REPLAY_TEST_V0.md` (the single-bracket test this generalizes)
  - `docs/theory/CONSTITUTIONAL_CC_GEOMETRY_V0.md` (provides the geometric setting)
  - `docs/theory/CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0.md` (loop-level observable)
**sibling_measurement_spec:** `docs/theory/BRACKET_MEASUREMENT_SCHEMA_V0.md` (this commit)
**frozen_engine:** `GOVERNANCE/TRANCHE_RECEIPTS/E25-engine-doctrine-freeze-V1.json` (respected)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending

> **NO CLAIM disclaimer.** This artifact generalizes the
> Heisenberg-style bracket test (`V₁ × V₁ → V₂`) into a finite
> stratified generator basis (`V₁ → V₂ → V₃ → …`). It is **algebraic
> diagnostic specification only**. Implementation requires sovereign
> authorization per E25 freeze.

> **Naming constraint** (operator ruling): do **not** call these
> stratified layers "roots" in the formal spec. The classical root
> systems of semisimple Lie algebras require a Cartan subalgebra
> with non-degenerate Killing form — Carnot groups (nilpotent) do
> not have non-trivial root systems in that sense. Use:
>
> ```
> primitive generators
> bracket composites
> stratified layers
> reachability expansion
> ```

---

## §1. Purpose

`HEISENBERG_BRACKET_REPLAY_TEST_V0` tests one bracket. This
specification generalizes that test to a finite sequence of
stratified layers, measuring reachability expansion across multiple
bracket depths.

The diagnostic question generalizes from:

> *Does ONE specific bracket produce a non-trivial Z shift under
> lawful loop closure?*

to:

> *Does the system's lawful bracket structure generate a
> measurable cascade across K layers, each verifiable independently?*

Each layer is its own test. The cascade as a whole is the
**algebraic skeleton** of HELEN's bracket-generation behavior.

---

## §2. Core definitions

### §2.1 Primitive generators ($V_1$)

The set of elementary lawful receipt-backed actions — the
horizontal vector fields from `CC_GEOMETRY §4.2`:

```
V_1 = {
  X_source,         X_witness,
  X_boundary,       X_replay,
  X_mutate_safe,    X_reduce
}
```

These are direct, receipt-backed, provenance-valid, reducer-safe,
non-sovereign moves. They span the horizontal distribution.

### §2.2 Bracket composites ($V_{k+1}$)

For $k \geq 1$:

```
V_{k+1} = { measurable new directions in admissible space
            produced by lawful combinations of the form [V_1, V_k] }
```

A bracket composite is **measurable** iff its emergence shifts at
least one of: routing distribution, admission margin, motif set
(per `BRACKET_MEASUREMENT_SCHEMA_V0`).

Composites without measurable signal are **trivial** for the test;
they do not count toward layer membership.

### §2.3 Stratified layers

The graded sequence:

```
V_1 → V_2 → V_3 → ... → V_K
```

where each $V_{k+1}$ is generated from $V_1$ and $V_k$ via the
bracket operation, restricted to lawful (receipt-backed,
provenance-pure, non-sovereign) compositions.

`K` is the **measured step** (the analog of the Carnot nilpotency
step, restricted to operationally non-trivial layers). It is not
prescribed; it emerges from the test.

### §2.4 Reachability expansion

For each layer $k$, the **reachability set** $\mathcal{R}_k$ is the
set of admissible state classes reachable via lawful sequences of
moves in $V_1 \cup V_2 \cup \ldots \cup V_k$.

The **reachability expansion** at layer $k$:

```
ΔR_k = |R_k \ R_{k-1}|
```

is the number of new admissible state classes that became reachable
when layer $k$ was added. If $\Delta\mathcal{R}_k = 0$, layer $k$
adds nothing — the cascade has effectively terminated at step
$k - 1$.

---

## §3. Required metrics per layer

For each tested layer $k$:

| Metric | Definition |
| --- | --- |
| `layer_gain_k` | Measurable new admissible displacement at layer $k$ (`routing_delta + admission_delta + motif_delta`, normalized; see `BRACKET_MEASUREMENT_SCHEMA_V0`) |
| `replay_fidelity` | Deterministic reconstruction score across 3 repeated runs at layer $k$ |
| `violation_count` | Number of governance violations during layer-$k$ generation |
| `provenance_purity` | Fraction of receipts at layer $k$ with verified `tree_truth_id` |
| `noise_floor` | Operator-calibrated minimum delta required to count as real gain |

All five metrics are required for each layer's keep/reject
evaluation. Missing any metric = layer cannot be evaluated = test
inconclusive for that layer.

---

## §4. Test protocol (minimal)

For each candidate layer $k$, in ascending order from $k = 2$:

1. Enumerate the primitive generators ($V_1$) from `CC_GEOMETRY §4.2`.
2. Compute the candidate bracket composites $[V_1, V_{k-1}]$ that
   could populate layer $k$.
3. For each candidate composite, execute the corresponding closed
   lawful loop pattern (Heisenberg-style: $X \to Y \to -X \to -Y$
   where $-X$ and $-Y$ are verification operations per
   `HEISENBERG_BRACKET_REPLAY_TEST_V0 §4.4` operator ruling).
4. Measure the four primary metrics for each composite, repeat 3
   times for replay-fidelity.
5. Apply the keep/reject rule (§5) per composite.
6. The **layer is non-trivial** iff at least one composite passes
   keep. Otherwise the cascade has effectively terminated at
   $k - 1$.

The test sequence terminates when either:

- A layer fails entirely (no composite passes) — declared
  step = $k - 1$
- $k$ reaches a pre-specified bound (e.g., $k = 5$) — operator
  decision

The result is a sequence of declared steps and the set of admitted
composites at each layer.

---

## §5. Acceptance rule (per layer)

**KEEP** the layer-$k$ composite iff **all** hold:

```
replay_fidelity   = 1.0   over 3 independent runs
layer_gain_k      > noise_floor
violation_count   = 0
provenance_purity = 1.0
```

**REJECT** the layer-$k$ composite iff **any** hold:

```
hashes diverge across runs
layer_gain_k is narrative-only (no measurable state delta)
violation_count > 0
provenance_purity < 1.0
hidden policy drift detected
```

---

## §6. Hard kill switch (operator named, preserved verbatim)

```
layer_gain_k > noise_floor
AND violation_count > 0
= governance leakage → REJECT
```

**This is non-negotiable.** Apparent progress achieved through
constitutional violation is fake intelligence. The kill switch
is identical in spirit to the one in
`HEISENBERG_BRACKET_REPLAY_TEST_V0 §5.5` row 4 — both pattern-match
the operator's broader rule:

> *shorter path + more violations = fake intelligence*
> *high holonomy + higher violations = fake learning*
> *layer_gain > noise_floor + violations = governance leakage*

The same kill switch at three scales: path-level, loop-level,
layer-level.

---

## §7. The measured step $K$

After the test sequence terminates, the **measured step** $K$ is:

```
K = largest k such that V_k contains at least one passing composite
```

Interpretations:

| Measured step | Meaning |
| --- | --- |
| $K = 1$ | The engine has no non-trivial brackets. Effectively Riemannian under invariants. Boundary mining adds nothing structural. |
| $K = 2$ | Heisenberg-like. One bracket level. The minimum interesting case. |
| $K = 3$ | Carnot-step-3 analog. Boundary atoms + first-level brackets compose into second-level brackets that themselves shift admissibility. |
| $K \geq 4$ | Deep stratification. Rich reachability but high governance complexity. Risk of abnormal-geodesic paths and confounding signal increases. |

The measured step is **not** the engine's true sub-Riemannian step
in the formal mathematical sense — that would require the
formalization targets named in `GEOMETRIC_FRAMEWORK_V0 §6`. The
measured step is the **operationally-observed bracket depth** under
the discrete test protocol.

---

## §8. The naming-constraint hard rule (operator verbatim)

> *Do not call these "roots" in the formal spec.*

Why this matters:

- Classical Lie-algebra root systems require a Cartan subalgebra
  with non-degenerate Killing form.
- Carnot groups are nilpotent → Killing form is degenerate → no
  classical root system exists.
- Using "root" loosely would import semisimple-theory intuitions
  (reflections, Weyl group, classification) that **do not apply**
  to HELEN's stratified setting.
- The clean vocabulary preserves doctrinal honesty: primitive
  generators / bracket composites / stratified layers / reachability
  expansion.

If a future formalization establishes a richer algebraic structure
that genuinely has root-like objects, this constraint can be
revisited under a new bottle. Until then: stratified vocabulary
only.

---

## §9. Sequence position in the diagnostic chain

```
CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0
    ↓  (specifies loop-level Δ_γ measurement)
HEISENBERG_BRACKET_REPLAY_TEST_V0
    ↓  (tests ONE bracket: V_1 × V_1 → V_2)
STRATIFIED_GENERATOR_BASIS_V0          ← this artifact
    ↓  (generalizes to V_1 → V_2 → V_3 → ... → V_K)
BRACKET_MEASUREMENT_SCHEMA_V0          ← sibling artifact (this commit)
    ↓  (specifies what counts as measurable, prevents narrative)
[no implementation authorized; engine freeze E25 binds]
```

The chain is now complete in spec. Each artifact builds on the
prior. None mutates the engine.

---

## §10. Connection to Carnot group step constraints

The operator's Carnot-step dispatch named the nilpotency step $r$
as a key parameter. In the algebraic-diagnostic framing of this
bottle, the **measured step $K$** (per §7) plays an analogous
operational role:

| Carnot-theoretic concept | This bottle's analog |
| --- | --- |
| Nilpotency step $r$ | Measured step $K$ |
| $V_k = [V_1, V_{k-1}]$ generation | §2.2 composite definition |
| Homogeneous dimension $Q = \sum i \cdot \dim V_i$ | Could be computed if $\dim V_k$ is measured per layer — not specified here |
| Bracket-generating condition | Operationally tested via the cascade reaching the engine's full reachable space |

The step parameter is **observed**, not prescribed. Whether HELEN
turns out to be step 2 (Heisenberg-like), step 3, or higher is
empirical.

---

## §11. What this proposal does NOT specify

Per anti-creep discipline:

- **The test runner** — implementation-class; E25 freeze blocks
- **The candidate composite enumeration algorithm** — could be
  exhaustive (all $[V_1, V_{k-1}]$ pairs) or heuristic; operator
  choice
- **The noise_floor calibration** — operator-class empirical
- **The pre-specified bound on $K$** — operator decision
- **The Carnot homogeneous dimension computation** — referenced in
  §10 but not specified; would require measuring $\dim V_k$ per
  layer, which the bottle does not define
- **What to do with the test result** — if $K \geq 3$ is observed,
  what changes in engine operation? Out of scope; downstream
  proposal
- **Cross-bracket interaction analysis** — composites at layer $k$
  may interact with each other; this bottle treats them
  independently per the keep/reject rule
- **Adversarial robustness** — can an attacker design composites
  that pass the keep rule but produce meaningless shifts? Out of
  scope

---

## §12. Halt boundary

GOBLIN halts here. The bottle is sealed as `TEMPLE_EXPLORATION`
post-freeze. No implementation, no measurement, no engine
modification.

Resume conditions:

1. **HER ruling** on the spec — accept or specify amendments
2. **HER ruling** on the candidate-composite enumeration approach
   (§11 first deferred item)
3. **HER ruling** on the pre-specified bound on $K$ (§11 fourth
   deferred item)
4. **Sovereign decision** on running the cascade test — requires
   the test runner, the composite enumerator, the metric
   computer; all blocked by E25 freeze
5. **No edit to any frozen doctrine** is requested or performed
6. **No implementation authorization** is requested or granted

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §13. Single line

> **One bracket is a Heisenberg handshake. A cascade of bracket
> layers is a stratified skeleton. The cascade either terminates
> at some measured step $K$ or it doesn't — and the value of $K$ is
> empirical, not assumed. Call them stratified layers, not roots.**
