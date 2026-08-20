# PROPOSED PRE-FLIGHT V2 — ADDENDUM 1 (operator adjudication 2026-08-20)

STATUS: adjudicated refinements to PROPOSED_PREFLIGHT_V2.md.
Architecture = ACCEPTED · theorem/benchmark law = CANDIDATE ·
scaling law = NOT_ADMITTED. Still a PROPOSAL until GO.

## DELTAS LOCKED BY ADJUDICATION

1. **Budget vector extended**: B = (B_tokens, B_claims, B_sentences,
   B_words, **B_tools**) — tool-call count / search depth bounded per goblin
   where the substrate exposes it; equality is component-wise.

2. **CorpusIdentity is a triple**:
   CorpusIdentity = (HEAD, WorkingTreeDiffHash, CorpusManifestHash)
   with H_C = H({path_i ‖ hash(content_i)} in canonical path order) over the
   files actually accessible to the benchmark. Two campaigns comparable iff
   H_C equal — never merely same commit.

3. **Coverage(Q,C) is a hard gate inside Evaluable**:
   RequiredSurfaces(Q) ⊆ ObservedSurfaces(C), else Coverage=FAIL ⇒
   Evaluable(θ)=false ⇒ θ ∉ Dom(argmax). A clean result on an uncovered
   question is not informative.

4. **Two experiments, formally split** (supersedes the V1a/V1b fork —
   both run, separately, in this order):
   - SCALE_V1: C1=1×GENERALIST · C3=3×GENERALIST · C5=5×GENERALIST —
     measures k ↦ N_earned with k the only varied factor.
   - DECOMPOSITION_V1: D_G=3×GENERALIST vs D_S=Topology+Contradiction+
     Authority — separates decomposition effect from scaling effect.

5. **Dedup preserves both identities**: every proposition carries
   raw_proposition_key AND canonical_proposition_key; semantic merge never
   destroys the raw proposition; merge steps logged with justification.

6. **Novelty inequalities extended**: N_P↑ ⊬ N_E↑ and N_E↑ ⊬ N_earned↑
   (new roots may refute hypotheses — that outcome is desirable).

7. **Selection pipeline final form**:
   VALIDATE → FILTER(ℰ) → PARETO over (N_earned, N_E, Stability, −Cost,
   −Review) → TIE-BREAK by η = N_earned/CognitiveCost among non-dominated
   configurations → OPERATOR SELECT. Never SCORE → MAX.

8. **Contamination registry fields**: PREEXISTING_OUTPUTS ·
   READ_BEFORE_FREEZE · EXCLUDED_UNTIL_END · OPERATOR_EXPOSURE ·
   MODEL_EXPOSURE · POTENTIAL_LEAKAGE. Gemma receipt: READ_BEFORE_FREEZE
   or EXCLUDED_UNTIL_END — never "maybe read later, then treated as
   independent".

9. **Three receipts, typed fields**:
   CONFIGURATION_RECEIPT: task_hash · corpus_hash · budgets ·
     swarm_complete · truncation · closure_pressure · isolation · result
   EPISTEMIC_RECEIPT: canonical propositions · evidence roots · HAL trials ·
     N_P · N_E · N_earned · result
   GOVERNANCE_RECEIPT: authority violations · forbidden mutations · tool
     violations · admission events · ledger effects · result
   No future reducer may flatten them into success=true.

10. **Tri-axial typing with no implicit coercion**:
    ExperimentValidity ⊬ EpistemicMerit ⊬ AdmissionStatus.
    Γ_C(θ)=ALLOW ⊬ Γ_A(p)=ALLOW. CognitiveScale↑ ⊬ AdmissionSurface↑.

11. **HAL**: governed by HAL_V1_CONTRACT.md (frozen spec, this directory) —
    narrow procedural discriminator; falsifier executed FIRST; dedup happens
    before HAL; HAL_SURVIVAL ⊬ INDEPENDENT_CORROBORATION in every receipt.

## PARADIGM LINE (status: theorem CANDIDATE)
HELEN separates cognition allocation from epistemic promotion.
Optimize(Θ_C) ⊬ Relax(Γ_A).
ΔCognition ⊬ ΔEvidence ⊬ ΔTrust ⊬ ΔAuthority.
"Cognition may be optimized. Trust may not be optimized into existence."

## REMAINING BEFORE FIRST TASK_HASH (unchanged)
Freeze byte-exact: Q₁ · corpus scope + fingerprint triple · budget vector
(incl. B_tools) · SCALE_V1 first · HAL per contract · thresholds
S_min/R_max/C_max · contamination arbitrage (Gemma). Then mint TASK_HASH,
then C1-R1.
