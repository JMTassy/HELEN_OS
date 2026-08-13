---
name: chiddush-archive
description: Run a governed chiddush extraction over a historical or symbolic corpus (books, type-specimen catalogues, material archives, exhibition catalogues, occult/mythic texts, patents, obsolete theories). Use when the operator says "chiddush <source>", relays upstream chiddush analysis with a verb, or asks to mine an archive for structural insight. Turns sources into falsifiable hypothesis generators — never into ingested facts. Output is always a proposal doc, never canon. authority=false · NON_SOVEREIGN.
---

# CHIDDUSH ARCHIVE — governed hypothesis extraction from historical corpora

The archive is not primarily memory. It is a **counterfactual laboratory**:
historical books, catalogues, diagrams, and obsolete theories become
generators of hypotheses whose implications HELEN derives, compares, and
attempts to falsify — without ever confusing the original author's
assertions with established knowledge.

Constitutional frame (non-negotiable):

    representation ≠ admission · glyph ≠ receipt · rendering ≠ authority
    replay ≠ authority · Δ_CHIDDUSH ⇏ Δ_KERNEL · chiddush ≠ canon
    H never collapses into S

## Provenance chain

    S (source) → G (extracted structure) → H (chiddush / hypothesis)

Every output states which layer each claim lives in. The source stays
evidence; the interpretation stays interpretation.

## Pipeline

### 1 · INTAKE (verb-gated)
- An explicit operator verb is required ("chiddush X", CHIDDUSH-prefixed
  relay, BUILD/FETCH verbs). Unverbed relayed upstream-AI output gets an
  assessment, never a write (relay discipline).
- Fetch the corpus to `~/helen_kernel/chiddush_intake/<slug>/`; extract
  a text layer when possible; record sha256 of the source file.
- Record corpus status honestly, one of:
  `DOWNLOADED` (full source on disk) · `WITNESSED` / `WITNESSED-PARTIAL`
  (pages seen — screenshots count, cite them) · `REPORTED` (claims
  carried from a relay or secondary source, unverified) ·
  `NOT_IN_SESSION` (referenced but absent). Never launder REPORTED into
  WITNESSED.

### 2 · EVIDENCE DISCIPLINE
- Ingest propositions only as tagged claims:
  `CLAIM(author, date, proposition)` — never as knowledge.
- Tag the corpus and each extraction with an EPISTEMIC_SYNTAX class
  (COMMUNICATION_ACT / MYTHIC_SIGNAL / LOCAL_OBSERVATION /
  VERIFIED_TEST / FORMAL_PROOF / CANONICAL_CLAIM).
- **Verify every load-bearing relayed claim against the source when the
  source is on disk** — grep it, quote it, cite line numbers. A claim
  that verifies upgrades to WITNESSED; one that can't stays REPORTED.
- Keep the epistemic types separate at all times:
  `OBSERVED OBJECT ≠ DECLARED CAPABILITY ≠ INFERRED CAPABILITY`.
- Every extracted relation is an evidence-qualified edge
  `e = (u, r, v, π, ε)` with π = source location and
  ε ∈ {explicit, derived, inferred, hypothesized}.

### 3 · STRUCTURAL EXTRACTION
Choose the decompositions the corpus supports:
- **Grammar** (specimen books, ornament catalogues):
  B = (g, τ, ρ, κ, σ, λ) — primitive, repetition, rotation/reflection,
  corner operator, scale, layer. Phase duality g = (g⁺, g⁻) (OPEN/TINT).
  Semantic unit Ψ = (identity, topology, orientation, phase, fill,
  scale); role classes [g]_ROLE = semantic equivalence without visual
  identity.
- **Generative memory** (any executable/replayable source):
  M_gen = (P, O, E, S, C, τ, Out, W) with witnessed relation
  Replay(P, O, E, S, C, τ) —W→ Out. Archive the generator, not the
  render: code ≠ image, output ≠ recipe, instance ≠ generator.
- **Capability records** (exhibition/industrial catalogues):
  R_cap = (a, M, T, P, O, C, t, g, π, w) — actor, material, tooling,
  process, witnessed output, constraints, time, geography, provenance,
  witness. A capability receipt has a DOMAIN:
  R_cap ⇏ unbounded capability. Exhibited(m,o) supports CapableOf(m,p)
  only when the source says so explicitly.
- **Transformation memory** (material archives): morphism chains
  M₀ —p₁→ M₁ —…→ A; archive verbs and relations, not only nouns;
  documented provenance vs material evidence = two independent
  witnesses that may conflict (report the conflict, never resolve it
  silently).

### 4 · MULTI-LENS FAN-OUT (proposer ≠ validator)
- Spawn heterogeneous lenses as fresh sub-agent contexts: history,
  geography, language, material, symbol, counterexample, anachronism —
  pick lenses the corpus deserves.
- Each lens returns h = (p, E, A, X): proposition, evidence,
  assumptions, counterevidence.
- Maintain bounded disagreement D_min < D(hᵢ,hⱼ) < D_max. **Measure D
  on structure (predictions, assumptions, entailments) — never on
  vocabulary.** Surface-lexical metrics Goodhart the band (HAL-scorer
  lesson).
- CONTRADICTION → INFORMATION: disagreement between lenses is signal,
  not noise; report it as such.

### 5 · INVARIANT → CHIDDUSH
- I* = ⋂ structure(hᵢ): the chiddush is what survives changes of
  interpretation, not the cleverest single association.
- 𝒞(S) = Novel[Intersect(Π₁(S), …, Πₙ(S))].

### 6 · FALSIFICATION
- CLAIM → PREDICTION → TEST: derive the prediction vector P(h) across
  applicable axes (genetic, linguistic, archaeological, chronological,
  maritime, symbolic, material, economic…), then score
  Test(h) = Σ w_k · Evidence(P_k(h)). Scores feed the Bayesian
  Witness: probability ≠ permission, authority=false always.
- Possibility nesting for capability claims:
  conceivable ⊇ technically-known ⊇ locally-accessible ⊇
  economically-feasible ⊇ produced ⊇ surviving. Known(p,t) ⇏
  Accessible(p,g,t) ⇏ EconomicallyViable(p,g,t).
- **Negative-evidence guard:** absence is informative only with
  availability + accessibility + sampling adequacy established.
  Absence alone is never evidence.
- Reconstruction failure criteria: a reconstructed graph that predicts
  historically impossible processes, unavailable materials, impossible
  chronology, or unsupported transmission paths FAILS.

### 7 · OUTPUT
- One proposal doc at `docs/proposals/<NAME>_CHIDDUSH_V0.md` in house
  format: header comment `authority=false · claim=NO_CLAIM · a reading,
  not a ruling`, corpus-status block, witnessed quotes with line refs,
  the extraction, laws carried over, and an operator-gated mode-route
  ("None self-promotes. NEEDS_OPERATOR verb to move any seed
  anywhere.").
- Untracked by default (NO_COMMIT / NO_PUSH protocol); explicit verb
  required per artifact to commit.
- End the session report with a full-color WULmoji receipt block
  (max 1 WULmoji/line, receipts never on sovereign paths, never as
  claim).

## Firewall (hard)

Never write to: `oracle_town/kernel/**`, `helen_os/governance/**`,
`helen_os/schemas/**`, `town/ledger_v1*.ndjson`, `mayor_*.json`,
`GOVERNANCE/**`. Schema-shaped seeds (new receipt fields, record
schemas) are SOVEREIGN-ADJACENT: propose only; they route to MAYOR
through HELEN machinery, never through this skill.

## Reads / Writes / Artifact / Receipt / HAL flag

- **Reads:** any path; web fetch for public-domain corpora.
- **Writes:** `~/helen_kernel/chiddush_intake/**` (corpus),
  `docs/proposals/**` (chiddush docs), this skill's own directory.
- **Artifact:** `<NAME>_CHIDDUSH_V0.md` proposal doc(s).
- **Receipt:** WULmoji receipt block in the session report; corpus
  sha256 in the doc header when DOWNLOADED.
- **HAL flag:** authority=false. Every output is a REVIEWED_CANDIDATE
  at best. Admission belongs to the gates.
