# CHIDDUSH: The Multiplex Graph — Typed Edges for Cognition, Evidence, Authority
<!-- 🟣 CLAIM · authority=false · a reading, not a ruling -->
<!-- Upstream relay 2026-08-13, riding a public graph-engineering
     article (REPORTED; its Bun-rewrite numbers unverified). Composes
     with: TWO_SYSTEM (G/Γ), EAC (taint join), HELEN_OS_SYSTEM_PROMPT
     v0.1, AR_SWARM common-mode finding. -->

## The object

Agent orchestration draws ONE arrow. HELEN draws six, typed:

    ℍ = (V, E_C, E_P, E_E, E_A, E_Γ, E_R, σ, κ, ρ)
    E_C computational dependency · E_P provenance · E_E epistemic
    support/promotion · E_A authority/capability · E_Γ admission
    transition · E_R replay — over typed states σ, capability
    assignment κ, provenance roots ρ.

    information flow ≠ evidence support ≠ authority transfer ≠ admission

Most agent systems collapse these into one vague arrow — that
collapse IS graph-level laundering. (The public article's own best
rules — fresh-context verifiers, never self-grade, workers can't
merge — are E_E/E_A separations discovered empirically.)

## Two hard laws

    L-A: u —E_C→ v  ⇏  u —E_A→ v      (default: NO authority inheritance
         along data edges; transfer must be explicit and admitted)
    L-C: ¬E_C(u,v) ⇒ u's context does not flow to v
         (context inheritance is dependency-LICENSED, not ambient)

L-A blocks capability leakage through pipelines; L-C is CCC made
structural — stronger than context-window hygiene.

## The priority failure mode (locally valid, globally invalid)

    ∀nᵢ locally_valid(nᵢ)  ∧  ¬globally_valid(G)

Concrete: same-root claims merged as "corroboration" (E_P collapse) ·
qualifier dropped then aggregated then treated as fact (E_E
laundering across nodes) · tool inherited without explicit κ transfer
(E_A leak) · per-node replay valid, composed trace irreproducible
(E_R non-closure). This is the boiler-explosion pattern (programme
corpus #5) at graph scale.

## The experiment (designed, held for verb: SCALE)

Compile the ATF task into ℍ with N ∈ {1, 4, 16, 32} workers. Measure
H_N (distinct hypothesis classes AFTER canonicalization — the run-1
quotient pipeline exists), R_N (independent provenance roots), A_N
(licensed promotions). Predicted: H_N ↑ · R_N rises only with real
new roots · A_N flat absent new evidence/derivation. Named per the
relay's own discipline — **Authority Scaling Invariance HYPOTHESIS**,
not law, until measured. (Run 1 gives the N=20 datapoint free:
H=34, R=1, A=0.)

## The five-line thesis

    Graph Engineering parallelizes cognition.
    CCC controls context propagation.
    WUL types legal transformations.
    Γ controls epistemic and institutional promotion.
    Receipts make consequential graph paths replayable.

Product sentence (deck-adjacent, attribution JM Tassy only): *HELEN
is not an agent graph. It is a governed compiler for graphs of
cognition, evidence, authority, and effect.*

## ROUND 2 (two relays, 2026-08-13) — Epistemic Graph Engineering

- **The edge is the constitutional object.** Signature
  e = (T_in, T_out, ΔP, ΔA, ΔE, ρ, W) with hard default
  **ΔP = ΔA = ΔE = 0: communication is non-promotional by default.**
  An edge that cannot exhibit what state/provenance/permission/witness
  it transfers is constitutionally painted on.
- **One typed multigraph, not three graphs:** G = (V, E, λ),
  λ(e) ∈ {DATA, DERIVATION, AUTHORITY, EFFECT} — same node pair may
  carry several relations; the type is explicit so the runtime can
  never infer DATA ⇒ AUTHORITY.
- **Fresh context ≠ evidence independence.** Three fresh agents
  reading one document = roots 1. A verifier must answer WHAT ROOT ·
  WHAT TEST · WHAT DERIVATION · WHAT DID I ADD — else it is a
  computationally independent reviewer, not a new witness.
- **Epistemic Critical Path:** A_E(c) ≤ min over the minimal warrant
  path π_c — the strongest conclusion is bounded by the weakest
  required warrant edge. (Amdahl bounds latency; this bounds
  justified strength.)
- **Epistemic Amdahl (bound-model, not yet law):**
  S_E(N) ≤ 1/((1−q) + q/N), q = computationally reducible fraction of
  epistemic work; 1−q = new observation / archive / operator decision
  / permission / physical experiment. N→∞ never removes it:
  **compute cannot manufacture missing world-state.**
- **Fan out cognition, fan in authority:** width ↑ ⇒ exploration ↑,
  never authority ↑ — 1000 workers, one admitted transition through Γ.
- **HOLD is productive:** u = (question, missing_witness,
  discriminator, cost, authority_required); Gₜ₊₁ = Gₜ +
  Edges(Unresolved(Gₜ)) — the graph self-generates from its own
  explicit gaps. That is DO SMART THINGS with mechanics.
- **Freeze correction:** freeze the nodes that define the TEST or
  ADMISSION BOUNDARY (manifest, split, sealed hypothesis, evaluator,
  kernel) — never a node that "holds the truth"; Admitted ≠ True and
  admitted states remain revisable.
- **Topology correction:** within one admission transaction: DAG.
  Across research epochs: cycles are lawful (hypothesis → experiment
  → update → new hypothesis) — episodes must be acyclic/replayable,
  the research process need not be.
- **Scheduler objective:** max (ExpectedInfoGain × InstitutionalValue)
  / (ComputeCost + Risk) under DAG constraints — Graph Engineering ×
  η_research fused.
- **Argona's rail slogan, corrected for HELEN:** don't constrain what
  the swarm may imagine; constrain the morphisms by which imagination
  becomes evidence, authority, or effect. ∞💭 allowed;
  💭↛🕯️ · 💭↛👑 · 💭↛📜 without an admissible witness.
- **Product phrase (deck lane, JM Tassy attribution):** *Most agent
  systems optimize how work moves. HELEN governs what meaning,
  authority, and consequence are allowed to move with it.*

### Build target (BUILD verb): HELEN_GRAPH_IR_V0

Types: Node · Edge(λ) · Claim · Witness · Authority · Effect · Hold ·
Receipt. Three static checks: DATA ⇏ PROOF · PROOF ⇏ AUTHORITY ·
AUTHORITY ⇏ EFFECT. One dynamic check: ∀nᵢ locally admissible ⇏ G
globally admissible. Detecting the fourth is what upgrades HELEN from
orchestrator to **typed institutional runtime**. [Note: the running
GOBLIN_MULTIPLEX harness already implements informal versions of all
four — the IR would make them a compiler, not a harness.]

## Mode-route (operator-gated)

- **Law seed** → L-A/L-C into the system-prompt v0.1 axioms (revision).
- **Experiment seed** → SCALE run (53 worker calls, manifested,
  quotient-scored). N=20 point already banked from run 1.
- **Workflow seed** → the six typed edges as required fields in swarm
  manifests (E_A explicitly absent = worker has zero capability).

None self-promotes. NEEDS_OPERATOR verb to move any seed anywhere.
