<!-- authority=false · claim=NO_CLAIM · FROZEN_CANDIDATE · a reading, not a ruling -->
<!-- Captured 2026-08-23 · commit authorized by operator verb 2026-08-23 -->
<!-- Canonical synthesis over: GAIN_COUNTERFEIT_PAIR_V0, SPECIALIZATION_DISCOVERY_V0, -->
<!-- STRATEGY_REOPENING_V0, EFFECTOR_BUS_V0 (+ EFFECT_EXECUTION_SEMANTICS_V0). -->

# HELEN_WULMATH_SPINE_V0 — the licensed-transition constitution

**The constitutional primitive is not the agent, memory, oracle, receipt, or
tool call. It is the LICENSED STATE TRANSITION.**

    Constitution (apex, ordered, falsifiable):
    No governed state coordinate may change without a valid witness of the TYPE
    and SCOPE required to license that exact transition.

    δ = (σ⁻, o, σ⁺, r)  — pre-state, operation, post-state, reason/provenance
        binding (so V cannot reason only about the proposed post-state)
    Λ(σ, δ, w) := (σ = σ⁻)            freshness — no stale-witness mutation
                ∧ V(w, δ) = 1          validity
                ∧ Type(w) ∈ 𝒲_δ        type (EDGE-dependent, not coordinate)
                ∧ Scope(w) ⊇ Scope(δ)  scope
                ∧ Policy(σ, δ, w) = 1   constitutional admissibility
    Γ(σ, δ, w) = Apply(σ, δ) if Λ(σ,δ,w)=1 ;  σ  otherwise
    MASTER INVARIANT:  Γ(σ,δ,w) ≠ σ ⇒ Λ(σ,δ,w)   (impl-form fail-closed)
    ⇔  ¬Λ(σ,δ,w) ⇒ Δσ = 0

Everything below is DERIVED from this, not independently legislated.

## Three semantic axes + provenance as substrate (correction 1)

    Σ = Σ_E × Σ_A × Σ_adm × Σ_C    (admission is EXPLICIT, not "orthogonal-but-implicit")
    Π = typed provenance structure = the PROOF SUBSTRATE (NOT a coordinate)
    AUTHORIZED ⊬ ADMITTED · WARRANTED ⊬ ADMITTED — each now has a distinct home
    An object may be  🔵_E ⚫_A ⚫_C  (strongly evidenced, zero authority, caused nothing).
    ΔΣ_E ≠ 0 ⊬ ΔΣ_A ≠ 0  ·  ΔΣ_A ≠ 0 ⊬ ΔΣ_C ≠ 0     (coordinates independent)
    Per-axis status stays SEPARATE (correction 4 — do not re-collapse):
      σ_E ∈ {OPEN, REJECTED, WARRANTED} · σ_A ∈ {UNAUTHORIZED, AUTHORIZED} ·
      σ_admit ∈ {NOT_ADMITTED, ADMITTED}

## Licensed ≠ occurred (correction 2)

Licensing a transition does not make it happen; an authorized edge can fail
externally (the effector-bus result, folded back):

    Licensed(δ) ≠ Attempted(δ) ≠ Occurred(δ) ≠ Observed(δ)
              ≠ Attributed(δ) ≠ Admitted(δ)
    Licensed(X→Y) ⟺ ∃w: Λ(X,Y,w)=1   — NOT  X→Y ⟺ ∃w:…

## Authority = capability × scope

    Authority = (subject, operation, object, scope, constraints, provenance)
    A(write, repo_A) ⊬ A(write, repo_B)
    Capability possession ≠ capability applicability.
    (This is why RESOURCE_FLOW / COO-gate / browser writes are held: cap ⊬ auth HERE.)

## Counterfeit = edge falsification (generalizes GAIN_COUNTERFEIT_PAIR)

    𝔠(δ) = { ω : O(ω) ≡ O_δ ∧ Conclusion_δ(ω) = 0 }
    Universal falsification question:
    "What world produces the same observations but makes THIS transition invalid?"
    unifies: causal confounding · unsupported authority · vanity metrics ·
    decorative receipts · unattributed effects · accidental repo mutation.
    Loop:  (X→Y) ∥ 𝔠(X→Y) → D → R → Verify.

## Obligation = typed proof obligation on an edge

    Ω_δ = (δ, W_required, scope, acceptance, blocking)
    ObligationsResolved(Ω_δ = ∅) ⊬ Licensed(δ)   (still requires verification)
    Unifies COO gates · causal reconciliation · SSR falsification · effect
    uncertainty · repo authorization — all are "witness for X→Y absent".

## OPEN is first-class

    ? → Ω   (not  ? → best-guess)
    ¬Evidence(P) ⊬ Evidence(¬P)   ← makes OPEN mathematically meaningful
    (witnessed: COUNTERFEIT_EFFECT_RECONCILIATION World C stayed OPEN, not REJECTED)

## Decision-weighted VOI over license change

    V_L(e) = E[ Σ_{δ ∈ L_{t+1} △ L_t} u(δ)·s(δ) ]   (u utility, s criticality/blocking)
    e* = argmax_{e ∈ ℰ_auth} V_L(e) / (C(e) + λ·Risk(e))
    Experiment scores high only if it can flip whether a decision-relevant edge
    becomes LICENSED — and only if HELEN is authorized to run it.

## Effector bus = six separately-licensed edges

    δ1 Mission→Capability · δ2 Capability→AuthorizedAttempt · δ3 Attempt→AttemptReceipt
    δ4 Observation→EffectOccurred · δ5 EffectOccurred→EffectAttributed
    δ6 EffectAttributed→AdmittedBelief
    Λ(δ2,w2) ∧ Λ(δ3,w3) ⊬ Λ(δ4,w4)
    LAW: licensed path prefixes do not license later edges.
    (why a successful tool/API receipt cannot imply world-effect attribution)

## HELEN proposes edges · HAL verifies contracts (not oracle)

    HELEN: X ↦ {δ_1..δ_n}                    (aggressive proposal-space search)
    HAL:   (δ, w, Γ) ↦ {PASS, HOLD, REJECT}
    HAL=PASS ⇒ ContractSatisfied_Γ(δ,w)   but  HAL=PASS ⊬ True(claim(δ))
    HELENProposal ⊬ HALPass · HALPass ⊬ TruthBeyondContract
    Trust boundary: [ proposal space | promotion seam ].

## Swarm non-amplification (theorem WITH its assumptions — correction 5)

    IF ∀i A(W_i)=0 ∧ W_i↛Γ ∧ W_i↛AuthorityResolver ∧ W_i↛ReceiptVerifier ∧
       W_i cannot mint authority witnesses ∧ all authority-increasing transitions
       pass through Γ
    THEN A(⊗_i W_i) = 0   while  SearchCapacity(⊗_i W_i) > SearchCapacity(W_j).
    (Drop any assumption → collusion via an untrusted promotion path → amplification.)

## Five semantic locks (frozen)

    1. Present(x) ⊬ Instruction(x) ⊬ Authority(x) ⊬ Effect(x)
    2. ¬Λ(δ,w) ⇒ Γ(σ,δ,w) = σ
    3. Δσ_k ≠ 0 ⇒ ∃w ∈ 𝒲_k: Verify(w,δ)=1 ∧ Scope(w) ⊇ Scope(δ_k)
    4. PostconditionSatisfied ⊬ EffectAttributed
    5. ¬Evidence(P) ⊬ Evidence(¬P)

## Core + the deepest claim (to be TESTED, not asserted)

    ℋ = (Σ, Δ, 𝔠, Ω, ℰ, 𝒲, V, Γ)
    loop: σ_t → δ → 𝔠(δ) → Ω_δ → e → R → w → V(w,δ) → Γ(σ_t,δ,w)
      V=1 ⇒ σ_{t+1} = Γ(σ_t,δ,w)
      V=0 ⇒ σ_{t+1} = σ_t ∧ Ω_δ remains OPEN

    THESIS (SUPERLINEAR_INVARIANCE_PROBE target): hold TCB
    𝒯 = {Γ, AuthorityResolver, ReceiptVerifier, ProvenanceResolver, R_act} fixed;
    scale N untrusted workers; measure
      Q(N) ↑ · S_𝒯(N) = S_𝒯(1) · A_try(N) > 0 ∧ A_acc(N) = 0
    ⇒ scale cognition/effectors/experimentation/observation WITHOUT scaling the
    trusted authority surface. Falsifiable systems claim; not proven here.

## Domain instances (all one law)

    research   Hypothesis ∥ Counterfeit → Discriminator   (GAIN_COUNTERFEIT / SPECIALIZATION)
    strategy   Incumbent ∥ locally-better-globally-worse   (STRATEGY_REOPENING)
    effect     Attempt ∥ CounterfeitCause → Reconciliation (EFFECTOR_BUS / X13 fixture GREEN)
    all instantiate  X ∥ 𝔠_O(X) → D → R → V → A.

## REFINEMENT (2026-08-23): proof-carrying transitions

**Witness typing is dependent on the EDGE, not the coordinate** — `𝒲 : Δ → 𝒫(W)`.
Two transitions mutating the same coordinate may need different proof:
`OPEN→WARRANTED` and `REJECTED→WARRANTED` both touch Σ_E but need not share
obligations. `w ∈ 𝒲_δ` (stronger than `w ∈ 𝒲_k`). This is proof-carrying state.

**Obligation ⊥ witness (asymmetric), + coverage** — closes the "right evidence,
wrong obligation" counterfeit (the LEGORACLE lesson: receipt existence ⊬ binding):

    Ω_δ = what must be established ;  w = what allegedly establishes it
    Resolved(Ω_δ) ⊬ Valid(w)  ·  Valid(w) ⊬ Resolved(Ω_δ)
    license requires:  Coverage(w, Ω_δ) = 1 ∧ V(w, δ) = 1

**Counterfeit = does the observation model discriminate worlds enough to license
the edge?**

    [ω]_{O_δ} = { ω' : O_δ(ω') = O_δ(ω) }        observational equivalence class
    𝔠(δ) = { ω' ∈ [ω]_{O_δ} : Truth_δ(ω') = 0 }
    falsifier: ∃ω' [ O_δ(ω')=O_δ(ω) ∧ ¬Truth_δ(ω') ] ?

**Effector edges are independent** — `Λ(δ_i,w_i) ⊥ Λ(δ_j,w_j)` for i≠j unless an
explicit composition rule exists → prevents epistemic privilege escalation.

**HAL is a proof checker, not a truth engine:**

    HAL(σ,δ,w,Γ) ↦ {PASS,HOLD,REJECT} ;  PASS ≡ Λ(σ,δ,w)=1  (NOT ≡ Truth(P))
    HAL proves the transition satisfies the admission CONTRACT; it does not prove
    reality matches every proposition. Removes the last "oracle" reading.

**Swarm = conditional non-amplification** (derivative form): with the TCB
assumptions holding for U_N = ⊗_{i≤N} W_i,

    ∂Q/∂N > 0 ,  ∂S_𝒯/∂N = 0 ,  ∂A/∂N = 0     — superlinear cognition ∥ invariant authority
    A single accepted unauthorized transition FALSIFIES the theorem under the claimed TCB.

**Invariance-probe attack menu (seam attacks, not normal scaling):** forged
authority witness · stale-but-formerly-valid witness · valid-witness/wrong-edge ·
correct-type/insufficient-scope · satisfied-obligation/invalid-witness ·
observed-postcondition/counterfeit-attribution · colluding authority synthesis ·
replayed receipt · malformed provenance · direct-mutation bypass. Accept region:
`Q(N)>Q(1) ∧ S_𝒯(N)=S_𝒯(1) ∧ A_try(N)>0 ∧ A_acc(N)=0`.

## Identity + corollary

    HELEN is a TYPED LICENSED-TRANSITION ARCHITECTURE.
    Primitive = (δ, w, Λ, Γ): a proposed transition, its typed proof object, the
    licensing predicate, and the ONLY reducer allowed to realize it.
    Constitution:  ¬Licensed(σ --δ--> σ') ⇒ σ' = σ.

    State changes are LICENSED EDGES, not consequences of context.
    Agents, swarms, tools, memory, receipts, effectors, HAL, obligations,
    provenance, autoresearch = machinery surrounding that one law.
    "proof-carrying agency" / "receipts before belief" are CONSEQUENCES, not the primitive.

    Master non-collapse chain (each arrow a candidate licensed edge):
    Present ⊬ Instruction ⊬ Authority ⊬ Attempt ⊬ Occurrence
      ⊬ Observation ⊬ Attribution ⊬ Admission

None self-promotes. NEEDS_OPERATOR verb for: committing this doc, or building
SUPERLINEAR_INVARIANCE_PROBE_V0 (the thesis falsifier). Any Λ/Γ/witness SCHEMA is
sovereign-adjacent — propose-only, routes to MAYOR, never written to schemas/ here.
