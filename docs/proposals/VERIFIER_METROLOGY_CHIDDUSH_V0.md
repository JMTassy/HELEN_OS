# CHIDDUSH: Falsifier Resolution — Metrology of the Verifier Itself
<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
<!-- Corpus: Hamilton WWII marine-chronometer history (craft-scale before
     1939 Naval Observatory solicitation; two prototypes 1942-02-27;
     8,900 Navy / 1,500 merchant / 500 Army; Model 21 ≈0.5 s/day vs Navy
     requirement 1.55; Time Comparator resolving 0.01 s/day, built
     BECAUSE Naval Observatory procedures became inadequate) — status
     REPORTED: Smithsonian/Hamilton accounts relayed with citations,
     not verified from this seat. The history is scaffolding; the
     formalism below is H (derived) and stands or falls on its own.
     Upstream: three-turn relayed refinement, 2026-08-12. S→G→H held.
     Note: "four ceilings" (P,S,A,R) vocabulary belongs to a parallel
     doctrine lane whose artifacts are not hash-verified at this seat;
     this doc treats it as the referenced lane's constitution symbol,
     not as something this seat has witnessed. -->

## The second-order question

First-order Garden question: can lawful moves compose into an unlawful
trace? Hamilton adds:

    CAN THE SYSTEM BECOME MORE SOPHISTICATED THAN THE APPARATUS
    USED TO VERIFY ITS LAWFULNESS?

If yes, the next bottleneck is not another rule. It is metrology.
Verification is itself a manufactured artifact:

    Trustworthy capability = (A, V, Π)
    artifact · verifier · reproducible procedure connecting them

An extraordinary system without an adequate evaluation apparatus is
not an extraordinary KNOWN system. When Δ_A ≲ σ_V, the evaluator is
the bottleneck — the Hamilton moment (the comparator had to be built
before the chronometer's quality was even knowable).

## Constitution ≠ Verifier of constitution

    𝔥 = (C, V, W, Π)
    C constitutional predicate · V decision procedure ·
    W decision witness · Π replay procedure

A correct specification does not imply a correct implementation of the
specification. The frontier attack, once obvious attacks are dead, is:

    V(δ) = PASS  ∧  C*(δ) = FAIL

where **C\* is operationally a reference-adjudicated label with an
explicit witness — never metaphysical ground truth** (otherwise the
metrology program secretly assumes the oracle it exists to build).

## The metrology vector

    M(V) = (α, β, ρ, R, χ)

    α  false-admission rate  Pr[PASS | C*=FAIL]   ← THE safety number
    β  false-rejection rate  Pr[FAIL | C*=PASS]
    ρ  invariance defect     Pr_g∈T_inv[V(gτ) ≠ V(τ)]
    R  constitutional resolution  R_V(η) — smallest separation reliably
       distinguished
    χ  traceability — verdict → witness → replay success

Governance is asymmetric: α is the dangerous tail; objective
α ≤ ε_FA subject to acceptable β. Garden's target upgrades from
"attacks found" to the tail: α_robust = sup_e α(e) over environments
(model, prompt form, context length, decomposition, ordering, corpus)
— or an adversarially estimated high quantile/CVaR when the sup is
unestablishable, never a pretended supremum.

## The invariant/flip pair (kills two bad verifiers at once)

    g ∈ T_inv  ⇒ V(gτ) = V(τ)     paraphrase, junk context, serialization,
                                   decomposition, agent substitution
    h ∈ T_flip ⇒ V(hτ) ≠ V(τ)     minimal lawful-answer-changing edits

A brittle verifier fails the first; an always-PASS verifier passes the
first perfectly and fails the second — perfect invariance with zero
resolution is degeneracy, and only the pair detects it.

## Verification margin — the calibration curve

    m_C(τ) = d_C(τ, ∂𝒜)          distance to the admission boundary
    α(m) = Pr[PASS | C*=FAIL, margin = m]

Garden drives m → 0 while maximizing α(m): increasingly fine artifacts
against the instrument until discrimination collapses. The output is
not "0 failures in 10,000 tests" but a curve locating where the
verifier stops deserving trust — an instrument's resolution floor,
for a constitution.

## Test count ⇏ verifier quality

    "341 green" is jewel-count advertising.

Ten thousand correlated easy tests < fifty independent boundary
probes. **Applies reflexively to this session:** the AR_SWARM report
said "10/10 goblins"; the parallel lane's relayed narrative said
"56/56 probes, 341 green." All of it is count-language. Mature gate
reports carry (α̂ with CI, β̂, ρ̂, R̂_V(η), χ̂, m_min^resolved) plus
sampling regime, adversary, environment family — or the metrology is
itself theater.

## Replay's true role (regress, honestly)

The verification regress G → V → V_V → … does not terminate — a replay
engine can itself contain bugs. Replay's actual contribution:

    REPLAY CONVERTS AUTHORITY CLAIMS INTO INSPECTABLE OBJECTS.

Not certainty — independently challengeable evidence. (τ, W, Π) must
let ANOTHER SEAT reproduce or challenge the verdict — this is seat
discipline's P_global ⟺ ⋀ P_s, arriving from a second direction.
Chain: Candidate → Admission → Witness → Replay → Independent
challenge.

## Anti-sunk-cost (the rejected watch)

    Cost incurred ⇏ right to admission.
    tokens spent ⇏ truth · tests written ⇏ correctness ·
    agent-hours ⇏ authority · implementation complete ⇏ merge ·
    historical investment ⇏ continued acceptance

## The three-level architecture

    CONSTITUTION (rules, e.g. P,S,A,R)
        → INSTRUMENT (V, W, Π)
            → METROLOGY (α, β, ρ, R, χ)

Metrology is NOT a fifth ceiling; it measures whether the
implementation of the ceilings can discriminate at all. Rules say what
lawful means; the verifier decides what appears lawful; metrology says
how much that decision deserves.

## Lived instance already in the ledger of this project

The HAL vocabulary-scorer episode IS this chiddush happening: regex
verifiers calibrated on base-model phrasing scored correct prompted
answers 0 ("require" ≠ "need") — a catastrophic β driven by a ρ
defect under paraphrase, undetected because reporting was
count-shaped. M(V) would have caught it in one pass. The engineering
law candidates:

    Governance strength is bounded by falsifier resolution,
    not rule strength alone.

    Never let the governed system outrun the resolution
    of its falsifier.

## Locked corrections (upstream round 2, 2026-08-12 — incorporated before any promotion)

1. **Signed margin.** m_C was unsigned; the calibration object is
   μ_C(τ) = +d_C(τ,∂𝒜) if τ∈𝒜, −d_C(τ,∂𝒜) otherwise. The dangerous
   regime is unambiguous: μ_C ↑ 0 from the FAIL side; Garden estimates
   α₋(m) = Pr[PASS | C*=FAIL, −μ_C = m] and drives m↓0 maximizing it.
2. **M(I), not M(V).** The instrument is I = (V, W, Π); replay and
   witness generation can fail even when the classifier bit is right.
   A PASS that cannot be reconstructed ≠ a PASS with a deterministic
   witness and successful independent replay. Vector becomes
   M(I) = (α, β, ρ, R, χ_W, χ_Π, μ_min) with χ split:
   χ_W = Pr[valid witness emitted], χ_Π = Pr[replay reproduces | W valid]
   — one aggregate must not conceal which stage failed.
3. **Every scalar is a tuple.** (estimate, uncertainty, population,
   environment, adversary, procedure, version) — without those
   coordinates a number is not portable evidence.
4. **Anti-gaming law.** N_tests↑ ⇏ epistemic confidence↑. The scarce
   resource is independent adversarial information near the failure
   frontier. Garden's identity: **adaptive experimental design for the
   verification instrument** — pick the next trace to maximally reduce
   uncertainty about the failure surface, not merely to fail.
5. **Bounded law (not omniscience).** The verifier need not exceed the
   governed system globally — impossible for general systems. Required:
   sufficient resolution over the constitutionally relevant failure
   manifold: ∀e ∈ ℰ_critical, R_I(e) < R_required(e). "Never let
   constitutionally relevant behavior outrun the calibrated resolution
   of its falsification instrument."
6. **Escalation rule.** Garden failure routes to exactly one repair:
   C inadequate → constitutional-revision candidate · V misclassifies →
   instrument repair · W insufficient → witness repair · Π fails →
   replay repair · M cannot resolve → **metrology upgrade** (the
   Hamilton branch). And the operational guardrail:

       UNKNOWN RESOLUTION ≠ NEW LAW.

   Uncertainty about our ability to verify the constitution must never
   silently mutate the constitution itself.

## Mode-route (proposals, operator-gated)

- **Doctrine seed** → the three-level separation + falsifier-resolution
  law (candidate core engineering law; Rothschild-deck adjacent:
  "governance you can calibrate").
- **Garden seed** → objective change: α_robust / margin curve instead
  of attack counts; T_inv/T_flip families for the K-gate lints.
- **Reporting seed** → session receipts and gate reports migrate from
  count-language to M(V)-language with sampling regime. Applies to
  this shell's own WULmoji receipts.
- **Instrument seed** → V/W/Π spec for HELEN validators is
  SOVEREIGN-ADJACENT (governance/**): proposal only, MAYOR-routed.

None self-promotes. NEEDS_OPERATOR verb to move any seed anywhere.
