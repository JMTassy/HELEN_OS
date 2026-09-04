<!-- authority=false · claim=NO_CLAIM · FROZEN_CANDIDATE (not canon) -->
<!-- Captured 2026-08-22 · commit authorized by operator verb 2026-08-22 -->

# SUPERTEAM_MINCOVER_ROUTER_V0 — frozen candidate

**Family:** Minimum-Cost **Typed** Constitutional **Multi-Cover** with
Precedence, Seat Resolution, and Typed Admission.

    SUPERTEAM = TypedMultiCover ⊕ SeatResolver ⊕ PrecedenceScheduler ⊕ TypedAdmission
    Routing chooses cognition. Routing never mints permission.
    Redundant cognition is allowed; redundant authority is not inferred.

## Core optimization (typed multicover — the two corrections applied)

Obligations `Q(x) = {q_j}` with **contribution classes** `c ∈ 𝒞_j` and
required multiplicities `k_jc` (not "exactly once" — coverage, typed):

    min_{z,y}  Σ_{r,s} C(r,s)·y_rs
    s.t.  Σ_r a_rjc·z_r ≥ k_jc          ∀ q_j, ∀ c ∈ 𝒞_j     (typed multicover)
          Σ_s y_rs = z_r · y_rs ≤ Qual(s,r)                    (seat eligibility)
          precedence DAG P respected                            (schedule)

- `k_jc` encodes heterogeneity: security validity may require
  `k_{j,builder}=1 ∧ k_{j,falsifier}=1` — never "two workers looked".
- `k_j = 0`: don't buy cognition for an irrelevant obligation.
- Cost is **role-seat specific**: `C(r,s) = αT + βL + γP_retry + δP_fail
  + ηC_verification` — a cheap seat needing four retries loses to one
  expensive call (receipt-witnessed: think-channel budget failures).
- `Multiplicity ≠ Independence ≠ Authority`.

## Four operators, non-collapsing

    Cover:    (Q,K,B) → R*            who is worth asking
    Resolve:  (R*,𝒮_t) → SeatAssign   which replaceable substrate (Role ≠ Seat)
    Schedule: (R*,P) → π*             legal causal order
    Γ:        (τ,w,σ) → ADMIT|HOLD|REJECT   the ONLY transition seam

    Cover ≠ Resolve ≠ Schedule ≠ Γ
    Selected(r) ⊬ Assigned(r,s) ⊬ Scheduled(r) ⊬ Credentialed(τ) ⊬ Executed(τ)

RoleGraph stable; SeatAssignment_t replaceable — Qwen/Gemma/future seats
may die without changing constitutional topology (receipt: DAY_ONE rebirth;
ResolveSeat T1–T5; role contracts ≠ seat identity).

## FABLE above the optimizer

FABLE does not pick models. It parameterizes: `(K_t, O_t, B_t) ↦
(Q_t, w_t, k_t, B'_t)`; the deterministic router solves the allocation.
Objective: **licensed marginal information value**

    max E[ΔF*_licensed] / E[C_total]   s.t. Γ-constraints ∧ ΔAuthority=0

A loud role with no discriminating value is economically dominated by a
quiet one (receipt: two-cells η; JESTER option-pricing entry).

## The JESTER clause (incident-derived, load-bearing)

Role selection ≠ transition authorization. `HALPass ⊬ Execute ·
MayorReady ⊬ Execute · OptimizationGain ⊬ Execute`. Execution needs the
typed admission conjunction — receipted 8/8 in
REPAIR_EXECUTION_ADMISSION_SEAM_V0 (~/helensh):

    ExecEligible = ObligationsSatisfied ∧ ArtifactBinding ∧ RunBinding
                   ∧ ScopeBinding ∧ GrantValid ∧ ¬Consumed(Grant)
    H_C = H_A = H_G · r_C = r_A = r_G · grants single-use · audits run-bound
    OperatorUtterance → AuthorityResolver → TypedGrant  (never LLM-inferred)

## Invariants before canon (I1–I6) + falsifiers (F1–F6)

    I1 coverage completeness (typed, preregistered multiplicity)
    I2 cost minimality (no cheaper valid typed cover in frozen candidate set)
    I3 precedence integrity (fit score cannot override sequencing)
    I4 admission independence (a completed cognitive plan mints nothing)
    I5 seat substitutability (same role contract ⇒ role graph + lineage survive)
    I6 authority non-amplification (Authority(R*) never rises with |R*|)

    F1 missing obligation → no complete team returned
    F2 cheaper valid cover exists → selection non-optimal → FAIL
    F3 high-fit role violates precedence → must not execute early
    F4 all cognitive obligations PASS, grant missing → calls after seam = 0
       (receipted: seam F2)
    F5 seat swap under same contract → obligations + lineage survive
       (receipted: DAY_ONE, critical-reading manifest reuse)
    F6 multiplicity without heterogeneity: two same-class workers satisfy
       numeric k=2 → CoverageNumeric=PASS ∧ TypedCoverage=FAIL
       (kin to: consensus ⊬ evidence, M3)

## Routing tables (candidates, replaceable)

    proposal:      HER → HAL → CHRONOS → MAYOR
    claim:         HAL → CHRONOS → MAYOR
    optimization:  HAL → CHRONOS → AUTORESEARCH → MAYOR
    replay:        CHRONOS → HAL
    execution:     Preconditions → Audit → ExplicitGrant → Executor
    JESTER:        escape edge at STOP boundary only (option-priced, never resident)

## WUL kernel

    🧩 x → 🔎 Q(x) → 💎 MINCOVER → 🔗 precedence → 🧠 seats → 🧪 work
    → 🧾 typed outputs → 🛡 seam → 🔑 credential → ⚡ transition
    🧠 ≠ 🧪 ≠ 🛡 ≠ 🔑 ≠ ⚡ · 💎Selected ⊬ 🔑Granted
    🧪 PASS ⊬ 🛡 AUDITED ⊬ 🔑 GRANTED ⊬ ⚡ RUN unless bound

## Receipt anchors (capture addition — clauses witnessed before named)

Two-cells run = hand-instantiated cover with one *uncovered obligation*
(HAL killed 0 — exactly what F1 detects). Admission conjunction = seam
receipt 8/8. Seat substitutability = DAY_ONE + ResolveSeat. Heterogeneous
coverage = Gemma/Qwen critical-reading (SameEvidence + DifferentCognition).
Option-priced JESTER = saturation-escape receipts (O₂ quarantined,
diagnostic ESCAPE).

None self-promotes. NEEDS_OPERATOR verb for build (deterministic router
V0, zero model calls testable) or canon routing (via Γ, never this shell).
