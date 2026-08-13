# PROGRAMME: Heterogeneous Corpus Campaign for Verifier Metrology
<!-- authority=false · claim=NO_CLAIM · a research programme, not a ruling -->
<!-- Companion to VERIFIER_METROLOGY_CHIDDUSH_V0.md. Upstream relay
     2026-08-12. Design is H; no corpus fetched yet. All corpus slots
     NOT_IN_SESSION until fetched under the chiddush-archive skill. -->

## Hard acceptance criterion (gate for every corpus)

    A corpus earns value only if it either FALSIFIES the existing
    calculus or identifies a measurable failure mode not already
    parameterized by M(I). Otherwise it is historical decoration.

## Pre-registration protocol (anti-retrofit)

Before reading corpus D, register its predicted laundering signature
L̂_D = (p̂_P, p̂_S, p̂_A, p̂_R, p̂_M, p̂_comp). Extract falsifiers BLIND
to the prediction; compare observed vs predicted. Without this, every
historical anecdote retrospectively fits HELEN — the retrofit failure
the multi-lens engine exists to prevent. Predictions are recorded in
this file per-corpus at FETCH time, before extraction begins.

## Corpus families and predicted stress surfaces

| # | Corpus | Predicted primary stress |
|---|--------|--------------------------|
| 1 | 19th-c. railway accident investigations | REPLAY + composition (competing testimony, causal reconstruction from partial traces) |
| 2 | Early aviation / NACA reports | METROLOGY + SCOPE (evolving standards, instrument limits, prototype→production) |
| 3 | Naval navigation / longitude records | WITNESS + TRACEABILITY (calibration chains, reference standards, accumulated error) |
| 4 | Early telegraph / electrical standards | composition (incompatible units; local correctness vs end-to-end) |
| 5 | Industrial boiler-explosion inquiries | ∀i C(aᵢ)=1 ⇏ C*(a₁∘…∘aₙ)=1 — compliant parts, catastrophic assembly |
| 6 | Patent interference / priority disputes | AUTHORITY + PROOF + REPLAY (conception vs reduction-to-practice, chronology, provenance) |
| 7 | Historical pharmacopeias / drug standards | specification ≠ measurement procedure (identity, purity, assay tolerance, batch variation) |
| 8 | WWII statistical quality-control manuals | direct Hamilton continuation: acceptance sampling, producer/consumer risk, distributions over exemplars |

Sequence: HAMILTON → RAIL → BOILER → AVIATION → PHARMACOPEIA → PATENT
→ QUALITY CONTROL. Acquisition targets: Smithsonian / NIST / NASA-NACA
/ National Archives / LoC / HathiTrust / Internet Archive government
technical reports.

## Three chiddush classes to hunt (registered in advance)

1. **Calibration inheritance failure.**
   Valid(x | V_t, E_t) ⇏ Valid(x | V_t, E_{t+k}) — an observation
   reused after its calibration assumptions expired. Consequence:
   provenance must carry CALIBRATION CONTEXT, not only source.
   (Already half-witnessed this session: the 1918 welding lane's
   "Cost Based on Conditions of 1916" REPLAY finding is an instance.)
2. **Compositional uncertainty accumulation** (tolerance stack-up).
   d(xᵢ, xᵢ₊₁) < εᵢ for every step, yet d(x₀, xₙ) crosses the
   admissibility boundary: locally bounded distortion ⇏ globally
   bounded distortion. Candidate Garden benchmark for HELEN's own
   summarization → memory → retrieval → synthesis chains.
3. **Common-mode verifier failure.** W₁ ← S and W₂ ← S: two witnesses,
   one source, zero independence. N_effective ≠ |W|;
   N_effective ≈ number of sufficiently independent provenance
   branches in the witness graph G_W. **Directly attacks a live AI
   pathology: agent multiplicity masquerading as epistemic
   independence — five agents repeating one retrieval are one
   lineage, not five votes.**
   [Session witness: AR_SWARM_20260812's contamination flag found
   exactly this — four chiddush docs sharing one author chain scored
   as one lineage, and ten goblin lenses collapsed to one register.
   The class is already observed in-house; the corpora would give it
   historical depth.]

## HELEN consequences if the hunts succeed

- Provenance schema grows a calibration-context field (SOVEREIGN-
  ADJACENT — MAYOR-routed).
- Receipt chains gain an accumulated-distortion budget, not only
  per-step tolerances.
- The Bayesian Witness weighs independent ancestry, not witness count
  — seat discipline generalized from machines to evidential lineages.

None self-promotes. Each corpus enters via chiddush-archive intake
(FETCH verb per corpus), gets its L̂_D registered here first, and
produces at most one chiddush doc. NEEDS_OPERATOR verb to start the
campaign.

## UPGRADE (2026-08-12 relay): from library to falsification database

    Internet Archive = CORPUS RESERVOIR ≠ EVIDENCE AUTHORITY
    (authority stays with the document's issuer, never the host)

Three layers, each arrow an admission gate:

    ARCHIVE → EVIDENCE → CHIDDUSH
    ARCHIVE row ⇏ EVIDENCE row ⇏ CHIDDUSH

- **ARCHIVE**: immutable source objects d = (id, date, issuer, genre,
  domain, provenance, pages, hash).
- **EVIDENCE**: the research unit is the smallest evidence-bearing
  EPISODE e = (S, X, K, H) — passage, situation, claim/counterexample,
  lineage — plus page coordinates and OCR confidence. Workers receive
  e, never an interpretation of the whole book. OCR corruption is a
  first-class ⊥-confounder.
- **CHIDDUSH**: model outputs, execution manifests, reduction
  derivations, duplicate clusters, adversarial challenges, status.

**Sampling before reading:** stratify 𝒟 by domain, then
dᵢ ~ StratifiedSample(𝒟). Kills researcher degrees of freedom:
pre-sampled evidence → blind falsification → only then chiddush.
Caveat registered: the digitized archive is a SELECTED projection of
history (survivorship, secrecy, institutional incentives) —
missingness is informative; corpus-metrology variable, not a ceiling.

**Two-arm design per episode:** blind workers get only the frozen
calculus + evidence ("find the smallest governance counterexample");
targeted workers get the accumulated attack catalogue. Independent
rediscovery I(H) = 1[H_blind ≃ H_targeted], equivalence decided by
anonymized referee REDUCTION, never keyword overlap.

**Referee as compiler:** Reduce(H) → {existing / composition / ⊥};
only ⊥ enters the queue, and ⊥₁ ⇏ CHIDDUSH (could be bad
formalization, missing context, OCR, vocabulary duplication).

**Chiddush qualification (all six required):**
BlindDiscover = 1 · Reduce = ⊥ · Duplicate = 0 · SourceVerified = 1 ·
CrossDomain ≥ k (independent institutions) · AdversarialSurvival = 1.
Until then: Candidate. Interesting idea ⇏ new invariant.

**Negative evidence, stated correctly:** N_⊥ = 0 after N episodes is
recorded as NoCounterexample(calculus | 𝒟, sampling, protocol, N) —
the experiment is part of the claim; "complete" is never concluded.

**Primary target of the first real run:** try to BREAK EAC
(EPISTEMIC_AUTHORITY_CONSERVATION_CHIDDUSH_V0) — find one historical
episode where a legitimate epistemic promotion occurred with no new
admitted evidence. Falsify T1 / T2 / GA / EDI; everything else must
reduce or produce a genuine ⊥.
