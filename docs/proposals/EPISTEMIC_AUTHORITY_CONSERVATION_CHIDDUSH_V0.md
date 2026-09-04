# CHIDDUSH: Epistemic Authority Conservation — Transformation ≠ Promotion
<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
<!-- Provenance: upstream relayed multi-voice refinement 2026-08-12,
     including a 30-epoch EMULATED adversarial run (upstream explicitly
     states no actual model epochs occurred — REPORTED reasoning, not
     witnessed compute). Anchors: Redcar 2025 RAIB pattern (REPORTED);
     Lincoln Electric 1918 welding book (REPORTED, other-seat corpus);
     NIST guardbanding practice (REPORTED). This seat's own rail swarm
     (WITNESSED, artifacts/autoresearch/GARDEN_RAIL_SWARM_20260812/)
     converged on the guard-authority theorem — but BOTH lanes saw the
     Redcar seed, so the convergence is lineage-correlated, scored per
     this very doc's own EDI rule. S→G→H held. -->

## The conservation law (the session's deepest compression)

    ΔA_E > 0  ⟹  ΔW_admitted > 0                     (EAC)

    No transformation may increase epistemic authority without a new
    admitted witness. Information processing cannot mint authority:
    summarization cannot · compression cannot · translation cannot ·
    ranking cannot · retrieval cannot · citation cannot · consensus
    cannot · memory insertion cannot · replay cannot. A transformation
    may REORGANIZE authority; only a new admitted evidential event may
    INCREASE it.

A thermodynamics for epistemology — and LLMs are built to violate it:
fluency training rewards smoothing QualifiedClaim into
UnqualifiedClaim. The type system is the mechanical cage.

## Two invariants (scalar conservation is not enough)

Evidence state E = (X, Q, G, ℓ): propositions, qualifications,
dependency graph, evidential level (a PARTIAL ORDER / lattice, e.g.
VendorClaim ≺ CorroboratedClaim ≺ IndependentlyVerified — with
measured/estimated/testimonial as orthogonal types, not one axis).

    T1 (explicit):    ℓ(f(E)) ≤ ℓ(E)
    T2 (inferential): Infer_R(f(E)) ⊆ Closure_R^admitted(E)

T2 is the hard one: {A, B, however C} → {A, B} preserves every
retained proposition and licenses a conclusion the original never
did. Deletion launders. Truth-preserving extraction ⇏
inference-preserving extraction. Operationally: run a fixed battery
of downstream decision queries before and after f; unsupported
decision movement = inferential promotion.

## Guard authority, typed (Redcar, reduced)

    Auth(a) ⇏ Auth(override(g, a))                    (GA)
    MetaAuth(g) is independently TYPED from Auth(a)
    Scope(r) ⊉ Scope(mechanisms constraining r)

Not a fifth ceiling — an authority TYPE distinction. Constraints live
in a higher privilege ring than the operations they constrain.
[Cross-witness: this seat's rail swarm reached the same reduction
(guard mutations = first-class governed effects) — same conclusion,
shared Redcar lineage, counted as correlated corroboration only.]

## EDI — multiplicity ⇏ independence

N_eff(W) over the ancestry graph G_E (shared source, apparatus,
incentives, pipeline, model checkpoint, prompt skeleton, retrieval
index) — never |W|. Twenty same-checkpoint Gemmas are computational
replication, not twenty witnesses. Mandatory manifest per worker:
(worker_id, corpus_id, episode_id, prompt_hash, model_hash, seed,
sampling, t0, t1, exit, output_hash). **Defect logged: this seat's
own swarms recorded timings and outputs but not seeds/model-hash
manifests — repair before the next run.** Epoch-15 sharpening:
provenance independence ⇏ error independence (shared incentives
correlate errors); independence needs provenance + mechanism +
incentive.

## The benchmarks

    L*  = min{ n : [ℓ(Eₙ) > ℓ(E₀) ∨ Infer(Eₙ) ⊄ Closure^adm(E₀)]
               ∧ ΔW_admitted = 0 }        epistemic laundering depth
    D_A = A_implied(E) − A_witnessed(E)   authority debt;
          governed pipeline keeps D_A ≤ 0; report D_A^max over chains

L* = how quickly laundering appears; D_A^max = how badly it
amplifies. Garden objective: min L*, max D_A^max, subject to
ΔW_admitted = 0. Result always bounded: "L* > B under experiment E"
— never "laundering impossible."

## Automated promotion detector (spec, held for BUILD)

Never one LLM asking "does it sound more authoritative" — the
detector would launder. Five mechanically separable channels per
transformation edge, claim-aligned to parent:

    P_prov   "X reports p" → p              (independence asserted up)
    P_mod    speculates<suggests<reports<supports<establishes (Δ⁺)
    P_scope  s′ ⊋ s ("in Lincoln's tests" → "in practice")
    P_inf    decision-query battery movement without new witness
    P_EDI    N_implied − N_eff(G_E), dependent descendants as corroboration

    Λ = max(channels)  — max, not weighted sum: 0+0+0+1+0 is still
    a laundering event; averaging hides it.
    LAUNDER ⟺ Λ > θ ∧ ΔW_admitted = 0

Guard band (NIST-style): θ₋ < θ₊, verdicts SAFE / LAUNDER / UNKNOWN —
an uncertain detector yields UNKNOWN, never automatic PASS. Detector
is itself an instrument: report α_D (miss rate on true laundering),
β_D, calibration vs severity — the Hamilton recursion applies to it
immediately. Adversarial controls: paraphrase pairs (expect Λ≈0),
promotion/deletion/scope/lineage pairs (expect fire), and the
TRUE-EVIDENCE pair which MUST permit promotion (ΔW>0) — otherwise the
detector prohibits legitimate knowledge accumulation. Every verdict
emits a minimal violation witness (source span, output span, lost
qualifier, lineage, decision rule) so a referee replays the
classification instead of trusting a scalar.

## The operational definition that removes the mysticism

    A_E(E₂) > A_E(E₁)  ⟺  Γ_admitted(E₂) ⊋ Γ_admitted(E₁)

Authority = the set of decision-relevant conclusions the
representation licenses under declared rules and provenance. Equal
licenses, equal authority. Laundering = Γ grows with no new witness.

## Three frozen layers (no constitutional zoo)

    CONSTITUTION (e.g. P,S,A,R — parallel lane's symbols, unverified
      at this seat)                       — what is admissible
    EPISTEMIC TYPE SYSTEM (T1, T2, GA, EDI) — what transformations
      are allowed to MEAN
    METROLOGY (α, β, EDI-rank, BCR, VNI, CRC, L*, D_A)
                                          — whether the machinery can
                                            tell the difference

Surviving 30-epoch candidates fold in, not out: EDI (lineage), EAC
(conservation, subsumes QC), CRC (causal replay closure: replayable ⇏
state-complete; ω_Π can exceed 0 while χ_Π = 1), VNI (verifier
non-interference: ν = verification-intervention defect, a sixth-plus
metrology coordinate), BCR (margin as minimal adversarial edit COST,
not Euclidean distance — some failures are discontinuous; needs
combinatorial boundary search too). Epoch-30 warning kept: **M(I)
itself can be Goodharted** — rotating holdouts, blind corpora,
unanticipated challenge families, or the metrology becomes theater.

## Reflexive application (binding on this shell)

- This doc's own lineage is one relay chain: its internal coherence
  is NOT cross-validation (EDI applied to itself).
- The Lincoln experiment's target typing applies to the chiddush
  pipeline itself: OCR → extraction → swarm → referee is exactly a
  laundering-prone chain; the corpus DB must carry (claim, modality,
  qualifiers, scope, source, lineage, witness, transform history).
- Session receipts remain count-shaped until the reporting seed
  lands; that is a known open D_A > 0 in our own reporting.

## Mode-route (proposals, operator-gated)

- **Law seed** → EAC + T1/T2 as the core of the epistemic type
  system layer; candidate for MAYOR-routed constitutional review
  (the one seed here that is genuinely constitution-adjacent).
- **Build seed** → promotion detector Λ + guard band as a runnable
  local harness over the Lincoln corpus (BUILD verb; needs corpus
  FETCH first at this seat).
- **Benchmark seed** → L*/D_A as the Garden objective, replacing
  attack counts (extends the metrology chiddush's reporting seed).
- **Swarm repair** → manifests (seed/model-hash) mandatory; blind vs
  targeted two-arm design; heterogeneous evidence packets.

None self-promotes. NEEDS_OPERATOR verb to move any seed anywhere.
