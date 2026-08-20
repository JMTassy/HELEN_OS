# BAKEOFF_V1 — AMENDMENT 1 (pre-run locks)

STATUS: FROZEN AMENDMENT · operator relay 2026-08-20 · applies to
BAKEOFF_V1_PROTOCOL.md before any campaign runs. authority=false ·
canon=false · ledger_effect=none. NOT RUN.

## LOCK 1 — TRUNCATED as campaign invariant, NOT_EVALUABLE semantics
∃i: ¬Complete(G_i) ⇒ W_swarm(Ck)=⊥ ⇒ HAL_global(Ck)=BLOCKED ⇒
N_earned(Ck)=NOT_EVALUABLE — **never 0**. Zero would mean "discrimination ran
and nothing earned novelty"; NOT_EVALUABLE means "protocol breakdown".
Conflating them makes a protocol failure look like cognitive performance.

## LOCK 2 — volume non-amplification theorem
N_earned(C_{k+1}) > N_earned(C_k) requires ∃p: p∉E_k ∧ IndependentLineage(p)
∧ EvidenceResolved(p) ∧ HAL(p)=SURVIVED. Corollary: 100 goblins paraphrasing
the same roots can NEVER raise the metric. Each Earned() conjunct blocks a
distinct optimization mode: Distinct ⊣ paraphrase spam · IndependentLineage ⊣
source fan-out · EvidenceResolved ⊣ eloquent speculation ·
FalsificationSurvived ⊣ attractive-but-fragile patterns. Deliberately absent:
confidence, agreement, agent count, verbosity, elegance.

## LOCK 3 — marginal value is the decision variable
MV_{k→k'} = (N_earned(C_{k'}) − N_earned(C_k)) / (Cost(C_{k'}) − Cost(C_k)).
HELEN criterion: MV_{k→k'} > 0 under stability, review-burden and
zero-authority-violation constraints. η_k stays reported but MV decides.
Constrained form: max_k N_earned(Ck) s.t. AuthorityViolations=0, Cost≤B,
Review≤R, Stability≥S_min.

## LOCK 4 — canonicalization of proposition identity
Goblin-supplied proposition_key = DIAGNOSTIC ONLY. Dedup runs on
canonical_proposition_id + evidence_lineage_id assigned by an independent
canonicalizer/lineage analysis AFTER freeze. Two goblins must not mint two
novelties by key choice. The canonicalizer must not repair or improve content.

## RECORDED SECONDARY MEASURES (declared, no new mechanism)
- **Closure pressure**: ρ_i = tokens_emitted / ceiling; ClosureRisk_i =
  P(ρ_i→1 ∧ ¬Complete_i). Witnessed sample (fable_swarm_v0, ceiling 4000):
  F .10 · B .51 · D .63 · C .69 all COMPLETE; A ≈1 ×2, E ≈1 ×2 TRUNCATED —
  visible separation.
- **Coverage**: Coverage_nominal(Ck)=k vs Coverage_effective=ΣComplete(G_i)/k.
  fable_swarm_v0: 4/6 = 0.667. Locks: architectural coverage ⊬ experimental
  coverage ⊬ epistemic quality.
- **N_P vs N_E**: novel propositions ≠ novel evidence roots — report both;
  a swarm can multiply interpretations without discovering any new root.
- **Contradiction split**: C_internal (between goblins — can be GOOD, cognitive
  diversity) ≠ C_corpus (proposition vs corpus). Phase II watches C_internal↓
  by social convergence as a novelty-loss signal.
- **Scaling axes**: θ=(k, B, O, D) — k agents, B budget, O role-openness,
  D decomposition. V1 varies k only; B,O,D frozen.

## DECLARED CONFOUND (V1 scope bound)
C1/C3/C5 vary k AND specialization AND lens distribution AND total budget
simultaneously. V1 = **system-level scaling benchmark**, NOT a causal estimate
of ∂N/∂k. V2 candidate designs to separate parallel-cognition from
role-decomposition effects: C1-generalist · C3-generalist×3 · C3-specialized ·
C5-generalist×5 · C5-specialized.

## RESULT-CLASS TAXONOMY
A. Configuration result (e.g. OpenRole+4000 ⇒ high truncation risk) — no
   epistemic claim about content.
B. Epistemic result (e.g. N_earned(C3) > N_earned(C1)) — about the discovery
   process.
C. Governance result (e.g. AuthorityViolations(C5)>0 ⇒ reject regardless of
   N_earned).
All five orderings of C1/C3/C5 are informative, including 1>3>5. The key
canary: C5 raw ≫ C3 with earned ≈ C3 = Goodhart successfully rejected.

## HAL SEMANTICS (restated hard)
HAL(p)=SURVIVED means ¬Refuted(p | F_p, S) only. Spaces: A ⊆ D ⊆ P with the
second inclusion structural, never a license: p∈D ⊬ p∈A.

## FIRST CONFIGURATION RESULT — FORMALIZED (from fable_swarm_v0)
- **O₁ (observation)**: under identical 4000 ceiling, observed closed roles
  completed (390–2773 ct) while two open roles truncated twice each.
- **H₁ (hypothesis, CANDIDATE)**: P(Complete)=f(B, O_i, C_i, S_i) with
  ∂P(Complete)/∂O < 0 at fixed budget. Small sample; roles differ on several
  dimensions — no generalization yet.
- **F₁ (falsifier)**: find comparable open roles that regularly complete at
  4000, or comparable closed roles that truncate at similar rates.
- Reading locked: "The epistemic campaign was invalidated, but the
  configuration experiment succeeded." Adaptive-rescue bias (budget as a
  function of failure) correctly refused: failure under frozen resources =
  experimental observation.

## PARADIGM LINE (V3-aligned)
Cognition itself becomes an experimentally governed resource.
k* = argmax_k E[N_earned(k)] / CognitiveCost(k) under governance constraints.
Generate broadly → Freeze honestly → Falsify independently → Measure earned
novelty → Admit narrowly. More cognition is allowed; more trust must still be
earned. Swarm size k is an experimental variable, not an architectural virtue.
