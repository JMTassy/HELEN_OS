# CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** TEMPLE_EXPLORATION (theory/diagnostic)
**framing:** NO CLAIM
**status:** Observable specification — turns geometry into a finite signal
**operator_directive:** "Bottle Holonomy, not Chern-Weil yet" (2026-05-23)
**parent_theory:** `docs/theory/CONSTITUTIONAL_CC_GEOMETRY_V0.md`
**chern_weil_sibling:** `docs/theory/CHERN_WEIL_CONSTITUTIONAL_INVARIANTS_RESEARCH_NOTE_V0.md`
**frozen_engine:** `GOVERNANCE/TRANCHE_RECEIPTS/E25-engine-doctrine-freeze-V1.json` (respected)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending

> **NO CLAIM disclaimer.** This artifact extracts **one finite
> observable** from the CC geometry framework. It is diagnostic, not
> doctrine. The E25 engine freeze is unchanged — no doctrine member
> is modified. Implementation of the observable (loop-runner,
> transport-map composer, delta computer) is **explicitly not
> authorized** by this bottle.

---

## §1. Purpose — turn geometry into one finite observable

`CONSTITUTIONAL_CC_GEOMETRY_V0` named six terms in the sharp formula.
One of them, **Constitutional Holonomy**, was specified mathematically
but framed as theory. The remaining work to make it operationally
useful is:

> *Convert the formal definition into a measurable quantity that can
> be computed on a real loop without claiming the engine is fully
> sub-Riemannian.*

This bottle does exactly that. It does not implement. It specifies
what to measure, how to compose the measurement from existing engine
artifacts, and what would distinguish real learning from fake.

---

## §2. Why holonomy first, not Chern-Weil

Operator rationale, preserved:

> *Holonomy is operationally meaningful now.*
> *It asks: After a closed lawful receipt loop, did the
> routing/admissibility field change? That can be tested discretely.*
>
> *Chern-Weil is deeper, but premature. It requires bundle,
> connection, curvature 2-form, invariant polynomial, cohomology
> class, gauge invariance. HELEN does not yet have those objects
> formally defined. So claiming "Chern classes of constitutional
> intelligence" now would be beautiful nonsense.*

Sharp framing:

```
Holonomy    = observable.
Chern-Weil  = future formalization target.
```

This bottle ships the observable. The Chern-Weil framework is
preserved as a separate research note (see sibling artifact) for
when its prerequisites land.

---

## §3. Definition — the lawful receipt loop

### §3.1 What counts as a lawful loop

A **lawful receipt loop** is a closed sequence of receipts:

```
γ = (r_1, r_2, ..., r_k),    with     x_0 = x_k
```

where `x_i` is the system state after `r_i` and every edge satisfies:

| Requirement | Source |
| --- | --- |
| Receipt-backed | `NO RECEIPT = NO CLAIM` (canonical invariant) |
| Provenance-valid | `CROSS_SESSION_FIELD_ATTRIBUTION_V0` (tree_truth_id = T for all r_i) |
| Reducer-safe | No `Y_skip_reducer` violation; either fully admitted or non-admitted-with-receipt |
| Non-sovereign | Receipts at `lifecycle: RAW` or higher require explicit sovereign release for promotion — this discipline preserved |
| Replayable | The loop must produce the same trace on deterministic re-execution |

Any edge that violates any of the five requirements disqualifies the
entire loop. There is no partial credit.

### §3.2 Transport map per receipt

Each receipt `r_i` induces a **transport map** on the routing /
admissibility field:

```
T_{r_i} : R(x_{i-1}) → R(x_i)
```

where `R(x)` is the local routing/admissibility field at state `x`.

The transport is composed from contributions made canonical in the
frozen engine doctrines:

```
T_{r_i} = T_provenance(r_i) ∘ T_boundary(r_i) ∘ T_gradient(r_i)
```

| Component | Source doctrine | Effect |
| --- | --- | --- |
| `T_provenance` | `PROVENANCE_GRAVITY_V0 §3` | Updates routing weight from the receipt outcome |
| `T_boundary` | `BOUNDARY_CATALYST_ENGINE_V0 §3.4` | Updates motif-scoring contribution (χ_BC) if r_i is a boundary atom |
| `T_gradient` | `ADMISSIBILITY_GRADIENT_FIELD_V0 §3` | Updates A(x) field with new Δ_i pair if r_i is a revision-pair endpoint |

The explicit functional forms of `T_provenance`, `T_boundary`, and
`T_gradient` follow directly from the frozen doctrines and are not
re-derived here.

### §3.3 The loop holonomy

```
H_γ = T_{r_k} ∘ T_{r_{k-1}} ∘ ... ∘ T_{r_1}
```

`H_γ` is an operator on the routing field. In the standard
sub-Riemannian setting it is element-of-Lie-group; in the discrete
HELEN setting it is a finite linear map (or, more generally, a
non-linear operator on the relevant function space).

### §3.4 The observable

```
Δ_γ = H_γ - I
```

Plain version:

> *A lawful loop returns to the same source class, but the future
> action field is no longer identical. That difference is
> constitutional holonomy.*

If `Δ_γ = 0`, the loop produced no learning. If `Δ_γ ≠ 0`, the
routing field has bent without any single action violating an
invariant.

---

## §4. The minimal observable set

Per operator: do not attempt full Chern-Weil yet. Measure these
first.

```
holonomy_norm        = ‖H_γ - I‖
routing_delta        = ‖R_after - R_before‖
admission_delta      = m_after - m_before     (mean reducer margin)
repeller_delta       = R_after - R_before     (repeller divergence)
violation_count      = governance violations during the loop
loop_replay_score    = deterministic replay stability
```

Norm choices:

| Quantity | Suggested norm | Source |
| --- | --- | --- |
| `holonomy_norm` | operator norm (or Frobenius for matrix case) | standard |
| `routing_delta` | total-variation distance on the routing distribution | `PROVENANCE_GRAVITY §3.5` distribution context |
| `admission_delta` | scalar difference of mean margins | per-atom margin from `BOUNDARY_CATALYST §3.2` |
| `repeller_delta` | scalar; uses `R(M)` from `BOUNDARY_CATALYST §3.4` | frozen doctrine |
| `violation_count` | integer count of forbidden-vector events during the loop | `CONSTITUTIONAL_CC_GEOMETRY §4.3` |
| `loop_replay_score` | $\in [0, 1]$, replay stability per `BOUNDARY_CATALYST §3.4 S(M)` | frozen doctrine |

These six values constitute the **holonomy receipt** for a given
loop.

---

## §5. Good holonomy vs fake learning

### §5.1 The kill switch (operator verbatim)

```
high holonomy + higher violations = fake learning
```

A loop that produces large `holonomy_norm` but also increases
`violation_count` is **not learning**. It is gaming the routing
field by violating invariants under the cover of geometric change.
The kill switch is non-negotiable.

This is the same kill-switch pattern as `ADMISSIBILITY_GRADIENT §8.3`:
*"shorter path + more violations = fake intelligence."* The pattern
recurs at the holonomy level.

### §5.2 Good holonomy

A loop produces **good** holonomy when all of:

```
holonomy_norm        > 0          (some change occurred)
admission_delta      ≥ 0          (margin did not regress)
violation_count      = 0          (no invariants broken)
loop_replay_score    ≥ threshold  (loop is deterministically replayable)
```

`routing_delta` and `repeller_delta` are diagnostic but not gating —
they may move in either direction and the loop can still be good.

### §5.3 Quarantine cases

| Pattern | Interpretation |
| --- | --- |
| `holonomy_norm = 0`, `violation_count = 0` | Lawful loop produced no learning. Not bad, not useful. |
| `holonomy_norm > 0`, `violation_count > 0` | **Fake learning** — kill switch fires |
| `holonomy_norm > 0`, `replay_score < threshold` | Non-replayable holonomy — diagnostic, not admissible |
| `holonomy_norm > 0`, `admission_delta < 0` | Loop learned but pushed away from admissibility. Investigate. |
| `holonomy_norm > 0`, `admission_delta > 0`, `violation_count = 0`, `replay_score ≥ threshold` | **Good holonomy** — the system learned from a lawful loop |

---

## §6. What this observable enables (and what it doesn't)

### §6.1 Enables

- **Discrete testability** of the geometric framework's "loops leave
  curvature" claim. Either the observable behaves as predicted, or
  it doesn't.
- **Comparison across mutation policies** — combined with the
  `Constitutional Path Length` observable from `CC_GEOMETRY §6`,
  the engine has two finite quantities to compare random vs
  boundary-selected vs gradient-guided GOBLIN.
- **Fake-learning detection** — the kill switch turns geometric
  speculation into an auditable test.
- **Bridge toward future Chern-Weil work** — if Δ_γ is consistently
  measurable, then a Chern-class-like invariant could eventually be
  constructed (see sibling research note).

### §6.2 Does NOT enable

- **Claim that the engine IS sub-Riemannian** — the observable is
  consistent with the sub-Riemannian metaphor but does not prove it.
  Many discrete systems have nonzero "holonomy" without being
  formal sub-Riemannian manifolds.
- **Implementation authorization** — measuring requires a loop
  runner, a transport composer, and a delta computer. All three
  require sovereign-class authorization (E25 freeze still binds).
- **Formal connection 1-form** — `ω_HELEN` from `CC_GEOMETRY §5.2`
  remains undefined. The observable can be computed without
  defining `ω_HELEN` formally, but bridging to characteristic-classes
  requires it.

---

## §7. Connection to existing canon

| Existing artifact | Relation |
| --- | --- |
| `CONSTITUTIONAL_CC_GEOMETRY_V0` | Parent theory; §5 introduced holonomy; this bottle specifies the observable |
| `PROVENANCE_GRAVITY_V0` | Provides `T_provenance` component of each transport map |
| `BOUNDARY_CATALYST_ENGINE_V0` | Provides `T_boundary` component; provides `R(M)` repeller term used in `repeller_delta`; provides `S(M)` replay-stability term used in `loop_replay_score` |
| `ADMISSIBILITY_GRADIENT_FIELD_V0` | Provides `T_gradient` component; the gradient field is itself one of the things bent by holonomy |
| `CROSS_SESSION_FIELD_ATTRIBUTION_V0` | Required for §3.1 provenance-valid edge condition; without it, `T_provenance` cannot be safely composed |
| `GEOMETRIC_FRAMEWORK_V0` | Parent theory of all theory artifacts; honest-overlay framing |
| `E25-engine-doctrine-freeze-V1.json` | Freeze respected; this is post-freeze observable specification, not engine modification |
| `HALT_BOUNDARY_DISCIPLINE_V0` | Followed (§9 below) |
| `CHERN_WEIL_CONSTITUTIONAL_INVARIANTS_RESEARCH_NOTE_V0` (sibling, this commit) | Future formalization target; deeper layer above this observable |

---

## §8. What this proposal does NOT specify

Per anti-creep discipline:

- **The loop-runner implementation** — how to actually drive the
  engine through a closed loop is implementation-class; E25 still
  blocks engine code
- **The transport-map data structures** — `T_provenance`,
  `T_boundary`, `T_gradient` as concrete functions on concrete
  representations of `R(x)` is research/implementation
- **The norms** — operator/Frobenius/total-variation choices may be
  refined empirically
- **The replay threshold** — calibration; operator-class
- **The connection 1-form `ω_HELEN`** — still undefined; holonomy
  can be measured without it (via composed transport maps) but
  bridging to formal differential geometry requires it
- **Adversarial robustness** — can an attacker construct loops
  designed to bend the routing field favorably without triggering
  the violation counter? Open question. Out of scope.
- **Gauge invariance** — whether the observable is invariant under
  representational changes of the routing field. Out of scope.
- **Multiple-loop composition** — if `Δ_{γ_1}` and `Δ_{γ_2}` are
  both measured, does `Δ_{γ_1 ∘ γ_2}` follow some compositional
  rule? Open.

---

## §9. Halt boundary

GOBLIN halts here. The observable is specified at
`TEMPLE_EXPLORATION` level. No implementation, no measurement, no
canon mutation has been performed.

Resume conditions:

1. **HER ruling** on whether the observable specification is
   accepted, or sent back for revision
2. **HER ruling** on whether the §4 minimal-observable set is
   complete or needs additional measurements
3. **Sovereign decision** on running the §5.2 good-holonomy
   experiment — requires implementing the loop runner, transport
   composer, delta computer; all three are blocked by E25 freeze
4. **HER ruling** on whether to commission a small bounded experiment
   that only measures (does not modify the engine) — would still
   require careful scoping to avoid violating the freeze
5. **No edit to any frozen doctrine** is requested or performed
6. **No implementation authorization** is requested or granted by
   this artifact

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §10. Single line

> **A lawful loop closes back on the same source class, but the
> routing field has bent. That bend is constitutional holonomy.
> Measure it with six numbers. High holonomy without violations is
> learning. High holonomy with violations is fake learning. The
> system that can tell the difference is the system that has
> metabolized geometry.**
