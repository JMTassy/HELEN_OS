# BAKEOFF_V1 — AMENDMENT 3 (eligibility-first optimization)

STATUS: FROZEN AMENDMENT · operator relay 2026-08-20 · anti-Goodhart closure
of the θ* objective. authority=false · canon=false · ledger_effect=none.

## THE CORRECTION
The scalar objective θ* = argmax_θ E[N_earned(θ)]/CognitiveCost(θ) is
REPLACED by optimization conditional on experimental admissibility:

Eligible(θ) = Evaluable(θ) ∧ HardGatesPass(θ) ∧ SwarmComplete(θ)
              ∧ Stability(θ) ≥ S_min ∧ Review(θ) ≤ R_max ∧ Cost(θ) ≤ C_max

θ* = argmax_{θ : Eligible(θ)} E[N_earned(θ)] / CognitiveCost(θ)

## LAWS
- **Efficiency is a selector, not an admissibility criterion.**
  Efficiency ranks eligible configurations; it does not make configurations
  eligible.
- **NOT_EVALUABLE is outside the optimization domain, not zero.**
  NOT_EVALUABLE ≠ ZERO_EFFICIENCY. W_swarm=∅ ⇒ Evaluable(θ)=0 ⇒
  θ ∉ Dom(argmax) — never scored, never "repaired to be scorable".
- **HardGateFailure ⇒ θ ∉ Dom(Optimization).**
  No earned-novelty gain, low cost, or spectacular ratio compensates for
  incompleteness, instability, authority violation, failed hard gates, or
  excessive review/cost.
- **Ordering: VALIDATE → FILTER → COMPARE → SELECT.**
  Never: SCORE EVERYTHING → PICK MAX.
- **Rescue = new attempt with new identity.** No retroactive repair of a
  sealed run; any retry is a distinct configuration with its own record.

## PIPELINE FORM
1. VALIDATE — campaign complete? task_hash unchanged? isolation preserved?
   no authority violation? no forbidden mutation? (PASS only continues)
2. ELIGIBILITY — Evaluable ∧ HardGatesPass ∧ Stability≥S_min ∧
   Review≤R_max ∧ Cost≤C_max (eligible configurations only)
3. COMPARE — Efficiency = E[N_earned(θ)]/CognitiveCost(θ)
4. SELECT — θ*

## WORKED EXAMPLE (why behavior changes)
C1: earned 3, cost 10k, ratio .00030, Complete PASS → eligible
C3: earned 7, cost 20k, ratio .00035, Complete PASS → eligible
C5: earned 15, cost 30k, ratio .00050, Complete FAIL → C5 ∉ ℰ
Naive scalar optimization picks C5. HELEN compares only {C1, C3} → C3.
The A/E run: Complete(A)=Complete(E)=0 ⇒ Evaluable=false ⇒ outside Dom —
not Efficiency=0, and never repaired to become scorable.

## WHY THIS IS THE MISSING ANTI-GOODHART
Γ_C defines the space of acceptable experiments FIRST; the optimizer may
only search for an optimum INSIDE that space. Governance defines the domain
of optimization; efficiency operates strictly within it.

## CANONICAL STATUS BLOCK (operator-consolidated 2026-08-20)
ParadigmStatus     = ACCEPTED
ExperimentalStatus = CANDIDATE
ScalingLawStatus   = NOT_ADMITTED
A/E (irreversible): Configuration=INFORMATIVE · Epistemic=NOT_EVALUABLE ·
Governance=CLEAN · NOT_EVALUABLE ≠ 0 · no retroactive rescue.
Frozen separations: N_P↑ ⊬ N_E↑ · ArchitecturalCoverage ⊬
ExperimentalCoverage ⊬ EpistemicQuality · Γ_C ⊬ Γ_A.
V1 = SYSTEM_LEVEL_SCALING_BENCHMARK on N_earned = N(k,B,O,D); not causal
∂N/∂k. Next gate unchanged: freeze BOUNDED_QUESTION, corpus, budgets, role
openness, HAL — then mint first task_hash.
