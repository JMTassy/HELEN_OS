<!-- authority=false · claim=NO_CLAIM · FROZEN_CANDIDATE · a reading, not a ruling -->
<!-- Captured 2026-08-23 · commit authorized by operator verb 2026-08-23 -->

# STRATEGY_REOPENING_V0 — the missing operator for RSI

**Corpus status:** the triggering paper (submitted 2026-08-19; ~2.1% of adjacent
training-experiment pairs were strategy changes; experience scaffold gave +12.6
GSM8K / +40.8 HumanEval but did not break strategic lock-in) is REPORTED — carried
from an upstream relay, not verified here. The doctrine below is grounded on a
WITNESSED session instance (SWARM_TOPOLOGY_PROBE: idea diversity without decision
or strategy diversity).

## The two search geometries

    execution search:  θ ∈ Θ(H)      (local, inside a fixed strategy)
    strategy search:   H ∈ 𝓗          (over strategy classes)

A system can be highly competent on Θ(H) while nearly immobile on 𝓗. That is the
lock-in failure mode. Naive loop: H_0 → θ_1 → θ_2 → … (optimizes inside H_0's basin).
Wanted: an endogenous, evidence-triggered `Reopen(𝓗_t)`.

    RSI ≠ repeated self-improvement.
    RSI requires the ability to falsify the improvement regime itself.

## SSR-VNEXT loop (stages structurally distinct)

    H_t --E--> R_t --C--> Z_t --R--> {H_t, H'_1..H'_m} --J--> H_{t+1}
    EXECUTOR ⊥ STRATEGY_CRITIC ⊥ REOPENER ⊥ JUDGE
    (the executor NEVER decides unilaterally whether its own strategy stays incumbent
     — else structural persistence bias)

## Operational definitions (no informal basins)

    σ(H) = (objective, decomposition, search_operator, evidence_policy,
            resource_allocation, stopping_rule)          -- frozen strategy fingerprint
    d_strat(H_i,H_j) = Σ_k w_k · 1[σ_k(H_i) ≠ σ_k(H_j)]
    F_escape(H_i,H_j) = 1[d_strat ≥ τ_escape]
    → "change learning rate" = execution; "replace gradient search with
       decompose+synthesize" can qualify as strategy.

    Lock metric with a FROZEN denominator (reopen opportunities, not all steps):
    O_t = 1[reopen predicate satisfied at t]
    L*_strat = 1 − ( Σ_t O_t·F_escape,t ) / ( Σ_t O_t )
    (failure to escape WHEN evidence warranted reconsideration)

## Switching ≠ improvement (same discipline as decision diversity)

    I_switch = 1[d_strat(H_t,H_{t+1}) ≥ τ]
    I_strat  = 1[J(H_{t+1}) > J(H_t) + δ]
    strongest event = I_switch ∧ I_strat

    Hierarchy (constitutional):
    different tokens ⊬ different propositions ⊬ different decisions
      ⊬ different strategies ⊬ better strategies

## REOPEN is receipt-grounded, not a free-form LLM call

    REOPEN_t = S_t ∨ C_t ∨ A_t
    S_t = 1[marginal-utility slope < ε for k trials]     (stagnation)
    C_t = 1[a falsifier survives k repairs]              (persistent contradiction)
    A_t = 1[LCB(U(H') − U(H_t)) > δ]                     (challenger has warranted edge)
    → continuation itself becomes evidence-bearing; else lock-in just moves up a layer.

## Laws (extend SPECIALIZATION_DISCOVERY L1–L5)

    L9   Local improvement does not license continuation of the current strategy.
    L10  Strategy persistence requires fresh comparative evidence.
    L11  No optimization regime may obtain indefinite tenure from improvements
         measured only by its own local objective.
    ⇒ H_t persists only while its continuation remains COMPETITIVELY WARRANTED
      (Continue(H_t) ⟺ W_t(H_t)=1). Persistence is a promoted claim, not a default.

## Strategy lock-in IS a counterfeit (converges with GAIN_COUNTERFEIT_PAIR)

    H_t ∥ H̃_t   where H̃_t is locally-improving, short-horizon-persuasive,
                globally inferior. Research object = discriminator D(H_t, H̃_t)
                that exposes the gap BEFORE budget exhaustion.
    COUNTERFEIT SEARCH  = seductive alternatives + discriminators
    STRATEGY REOPENING  = detect when local evidence stops discriminating the
                          incumbent + force comparative search

## Extended evaluation vector

    χ = (N, D, I^decision, I^improve, F^strategy, I^strategy, T^escape, C^escape)
    T^escape = min{t : H_t ∉ 𝓑(H_0)};  C^escape = compute before useful escape
    (an architecture escaping 90% at 100× cost may not dominate one escaping 70% cheap)

## STRATEGY_TRANSITION_RECEIPT_V1 (proposed)

    incumbent_fingerprint · challenger_fingerprint · frozen d_strat def ·
    reopen_trigger + evidence_refs · incumbent_best_local · challenger_score ·
    same_budget_normalization · judge_hash · F_escape · I_switch · I_strat · promotion

## STRATEGY_REOPEN_PROBE_V0 (next experiment, local-first, buildable)

Construct a task with a deliberate local optimum: plausible H_0, several
small-gain local mods, a qualitatively different H* requiring H_0's abandonment,
discoverable only after several iterations. Measure P_escape, T_escape,
ΔU_escape, C_escape across A1 single / A2 same-model-resample / A3 hetero-swarm /
A4 swarm+critic / A5 explicit REOPENER. Asks the real question:

    Which architecture escapes a seductively-improving but globally-inferior
    research strategy? — the prerequisite for useful RSI.

## REFINEMENT (2026-08-23): frozen judge, four laws, non-recursive authority

**Lead correction:** Reconsider(U) may PROPOSE successor objectives but must not
alter the operative judge in the same experimental lineage. Promotion stays under
an externally frozen evaluation constitution. State gains J_t:

    𝒳_t = (H_t, θ_t, 𝒞_t challengers, W_t, R_t, B_t, J_t)
    INVARIANT: J_t cannot be mutated by the strategy currently being judged.
    (else the system escapes falsification by changing the scoreboard)
    Authority split: proposal ≠ comparison ≠ promotion authority.

**REOPEN is not one bit** — split search from replace, and keep an exogenous audit:

    R_t^search  = S_t ∨ C_t ∨ P_t ∨ Q_t     R_t^replace = (LCB(ΔU) > δ) ∧ warranted
    Q_t = small SCHEDULED control challenge (audit sampling). Rationale:
    absence of detected failure ⊬ global competitiveness — a deeply wrong
    incumbent controls which observations it generates and may never emit its
    own contradiction. Freeze B_challenge ≥ B_min > 0; budget_policy_hash in
    every transition receipt (else "strategic intelligence" is just 10× challenger compute).

**Continuation is a promoted hypothesis, not the absence of an event:**

    W^continue_t = Verify(R^incumbent, R^challenge, J_t, B_t)
    ΔU_local > 0 is evidence about θ ∈ Θ(H_t), NOT about H_t ∈ 𝓗.

**Lock-in and thrashing are dual pathologies:**

    R_switch = switches/opportunities · R_useful = validated-improvement-switches/switches
    R_switch≈0 ⇒ LOCK-IN ; R_switch≫0 ∧ R_useful≈0 ⇒ THRASHING
    target = evidence-responsive strategic mobility (neither extreme)

**Typed RSI ladder — each level needs a strictly stronger witness, no upward
authority inheritance** (`W_{L_k} ⊬ W_{L_{k+1}}`):

    L0 θ        ← execution receipts
    L1 H        ← comparative strategy receipts
    L2 Θ(H)     ← cross-strategy failure evidence
    L3 D        ← discriminator-inadequacy evidence
    L4 U        ← external objective-conflict evidence
    self-reference depth ↑ ⇒ externalization of adjudication ↑
    (the deeper the system reconsiders itself, the less it may certify that reconsideration)

**Escape needs structural difference, not just a hash diff:**

    F^strategy(H_i,H_j) = 1[ d_strat ≥ τ_escape ∧ Δ_structural = 1 ]
    (≥1 meaningful coordinate — objective/decomposition/search-op/evidence-policy/
     stopping-rule — must differ; fid≠fid alone ⊬ basin escape)

**Four laws (supersede/extend L9–L11):**

    L11  No regime gets indefinite tenure from improvements measured only by its
         own local objective.
    L12  Reconsideration may APPEND new evaluative structure but may not erase or
         rewrite the evidence under which prior regimes were judged.
         (executable: R_t ⊆ R_{t+1}; append interpretation, never rewrite observation)
    L13  Execution-level evidence cannot silently discharge a strategy-level
         comparison obligation. (strategy-level authority non-amplification)
    L14  No regime may simultaneously propose a higher-order evaluation change,
         enact it, and certify itself under that change.

**A₆ sham-reopen control** (causal isolation, lifting MV(Q₂|G₁) vs MV(G₂|G₁) from
model to architecture): VNEXT + reopener that emits ONLY local variants
(d_strat < τ_escape). Key contrast Ψ(A₅) − Ψ(A₆) = value of GENUINE strategy-class
reopening at comparable orchestration overhead.

**Receipt split (witness ≠ promotion):**

    STRATEGY_TRANSITION_RECEIPT → comparison_verdict + promotion_eligible
    → PROMOTION_PROPOSAL → Γ → STATE_TRANSITION   (authority=false throughout;
    the strategy experiment never acquires write authority)

**Master distinction:**

    recursive self-improvement ≠ recursive self-reconsideration
                              ≠ recursive self-authorization
    first two = research capabilities; third = what HELEN PROHIBITS.
    SHARPENED CHIDDUSH: RSI requires recursive falsifiability under
                        NON-RECURSIVE authority.

None self-promotes. NEEDS_OPERATOR verb for: STRATEGY_REOPEN_PROBE_V0 build,
or committing this doc.
