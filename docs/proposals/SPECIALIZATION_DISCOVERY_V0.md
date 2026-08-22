<!-- authority=false · claim=NO_CLAIM · FROZEN_CANDIDATE · a reading grounded in receipts -->
<!-- Captured 2026-08-22 · commit authorized by operator verb 2026-08-22 -->

# SPECIALIZATION_DISCOVERY_V0 — persona ≠ model, seat is inferred

**Grounding receipts (witnessed this session, ~/helensh/state/smart_probe/):**
comparison_routing.json (Qwen routing value NOT established) and
comparison_jester.json (Qwen frame-break FALSIFIED+REVERSED; Gemma χ=(1,1,1),
abliterated-Q2_K Qwen χ=(1,0,0) degenerate). Both: CHEAPEST_SUFFICIENT_TEAM =
GEMMA_ONLY on this hardware. These falsified "Qwen = JESTER."

## Reconciling "HELEN is a Mixture of Experts"

The MoE / quantum-garden vision is RIGHT — with one correction the probes force:

    the experts are PERSONAS (operation classes / prompting strategies),
    NOT model identities.

    HAL, HER, DAN, AURA, GOBLINS, JESTER = operation classes
    (adversary, expander, ..., frame-inverter) — STABLE.
    The substrate that best instantiates each = INFERRED from receipts,
    revisable, and on 18GB-Mac hardware currently ALL = Gemma
    (the one live-and-useful seat; a second MODEL added no marginal value).

So the "egregor superteam maturing raw data → CHIDDUSH" works — but its
insight range comes from **persona diversity on the available substrate**
(witnessed: two-cells 21→13→3 SHIP, harmony garden, goblin runs), NOT from
model diversity (NOT established: both probes GEMMA_ONLY). Range of insight
is a prompting-topology property, not a model-count property — on this box.

## Five frozen laws (before any Probe 3)

    L1  MythicRole ≠ ModelIdentity
    L2  RepresentationalDiversity ≠ DecisionDiversity ≠ DecisionImprovement
        (different tokens ⊬ different ideas ⊬ decision change ⊬ improvement;
         N_Q > N_G ⊬ MV_Q > MV_G — the deepest probe result)
    L3  SecondSampleValue ≠ HeterogeneityPremium
    L4  Specialization is INFERRED from receipts, never assigned by narrative
    L5  InsufficientEvidence ⇒ UNRESOLVED (default to the gap, not the story)

## Empirical seat resolution (replaces static Role→Model)

    ResolveSeat(o, x, R_t) =
      argmax_{m ∈ eligible} LCB_{1-α}[ MV̂(m | o, x, R_t) ]   if n_eff ≥ n_min
      UNRESOLVED                                              otherwise

    MV_{b|a}(x) = U(J(D_a ∪ D_b)) − U(J(D_a))    (U frozen pre-observation)
    χ_{b|a} = (N, D, I^decision, I^improve);  I^decision ⊬ benefit,
    only I^improve = U(J(D_a∪D_b)) − U(J(D_a)) answers "better?"

LCB (not raw mean) makes uncertainty default to UNRESOLVED, not to mythology.

## The 2×2 factorial (next experiment, competence-gated)

    cells: GG, GQ, QG, QQ  (first,second; independent generation, compose after)
    μ_GG,μ_GQ,μ_QG,μ_QQ = E[M_{b|a}]
    H_{Q|G} = μ_GQ − μ_GG      H_{G|Q} = μ_QG − μ_QQ
    S_same = (μ_GG+μ_QQ)/2     S_cross = (μ_GQ+μ_QG)/2
    Δ_hetero = S_cross − S_same        (the load-bearing statistic)
    S_all = mean of all four            (generic second-call value)

    COMPETENCE GATE: packet enters only if C_G(x)=C_Q(x)=1
    (runtime ok ∧ non-echo ∧ non-degenerate ∧ task-competence passed).
    ⇒ run on ROUTING (both competent), NOT frame-break (Q2_K degenerates).
    Report paired-bootstrap CI_95; CI(Δ_hetero) ∋ 0 = "not established",
    NOT "zero value".

Outcome taxonomy: A resampling-wins (Δ_hetero≈0) · B asymmetric (H_{Q|G}>0
only) · C reciprocal diversity · D coverage-not-selection (N_Q>N_G ∧
I_Q^improve ≤ I_G^improve — Qwen expands search space, doesn't improve
selection; upstream-generator use, not a seat) · E negative heterogeneity.

## Current receipt

    JESTER_OPERATION_CLASS     = PRESERVED
    JESTER_SUBSTRATE           = UNRESOLVED
    QWEN_ROUTING_ADVANTAGE     = NOT_ESTABLISHED
    QWEN_FRAME_BREAK_ADVANTAGE = WEAKENED (Q2_K confound: degraded quant)
    QWEN_GLOBAL_USEFULNESS     = NOT_TESTED
    HETEROGENEITY_PREMIUM      = UNRESOLVED (needs 2×2)
    MYTHIC_ROLE_INHERITANCE    = FORBIDDEN
    HARDWARE_VERDICT           = 18GB Mac = single live substrate (Gemma);
                                 personas multiplex on it
    DEEPEST_FINDING            = HELEN should learn comparative advantage as
                                 an empirical capability topology, not encode
                                 model mythology

None self-promotes. NEEDS_OPERATOR verb for: the 2×2 factorial (competence-
gated, routing task), or committing this doc.
