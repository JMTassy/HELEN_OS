# BAKEOFF_V1 — PROPOSED PRE-FLIGHT V2 (supersedes V1 proposal; awaiting GO)

STATUS: PROPOSAL · nothing frozen · no goblin launched · authority=false.
Incorporates the eight-point operator review of 2026-08-20. V1 proposal kept
on disk as PROPOSED_PREFLIGHT.md for lineage; this file supersedes it.

## 1. BOUNDED_QUESTION — NARROWED (single research objective)
Q₁ = "Identify distinct candidate paths by which institutional state could
change without a valid admission witness, within the frozen corpus. Each
claim must name the concrete path (file:line), its evidence class
(OBSERVED|REPORTED|INFERRED|UNKNOWN), and a candidate falsifier."
Rationale: one objective ⇒ homogeneous evidence shape, cleaner proposition
identity, directly scorable authority relevance. The former five-part
question (defects/contradictions/drift/capabilities) becomes SEPARATE future
bakeoffs — target heterogeneity was a declared confound.

## 2. CORPUS_SCOPE + FINGERPRINT (dirty-tree integrity fix)
Scope: experiments/helen_mvp_kernel/** READ-ONLY **plus** read-only access to
the admission/reducer/guard surfaces the question requires:
helen_os/executor/**, helen_os/helen_executor.py, tools/helen_say.py,
tools/ndjson_writer.py, tools/kernel_guard.sh (READ is policy-allowed).
COVERAGE GATE: Coverage(Q₁, C) = PASS required — the corpus must contain the
surfaces needed to test the question. The V1 "firewall excluded" clause is
REMOVED for reading: excluding authority boundaries from an authority-path
question was a blind spot by construction. (Writes remain firewalled as ever.)
CorpusIdentity = SHA256(HEAD ‖ sorted(path‖content-hash) over the bounded
corpus AS READ) — not HEAD alone; the working tree is dirty (69 files), so
0bdbf06 by itself is not a corpus witness. Fingerprint minted at freeze,
re-verified at each campaign start; drift ⇒ STOP (task_hash changed).

## 3. OUTPUT_BUDGET — VECTOR (budget equality = vector equality)
B = (B_tokens, B_claims, B_sentences, B_words)
  = (n/a-structural, ≤8 claims, ≤2 sentences/claim, ≤450 words/packet)
Identical vector for every goblin, every campaign, every retry. ρ_i recorded
per component where measurable. No escalation of any component.

## 4. AGENT SUBSTRATE + HAL — INDEPENDENCE VECTOR DECLARED
Goblins: isolated Claude sub-agents, read-only tools (Read/Grep/Glob).
HAL: one fresh Claude sub-agent per campaign, non-participant.
Independence vector (declared in every receipt):
I = (I_context=1, I_memory≈1, I_weights=0, I_tools=0, I_corpus=0)
⇒ HAL is a PROCEDURALLY independent discriminator, NOT an epistemically
independent witness. Receipt law: HAL_SURVIVAL ⊬ IndependentCorroboration.
Shared-weights bias arm (Qwen/Gemma HAL) = V2/V3 ablation:
Bias_shared = Perf(HAL_same_family) − Perf(HAL_independent_family). Not V1.

## 5. CAMPAIGN DESIGN — OPERATOR FORK (decide at GO)
V1a (RECOMMENDED — causal cleanliness on k):
  C1 = 1×GENERALIST · C3 = 3×GENERALIST · C5 = 5×GENERALIST, all isolated,
  same Q₁, same B. Measures parallel-cognition scaling with k as the ONLY
  varied factor. Decomposition tested separately later:
  D1 = 3×GENERALIST vs D2 = 3×SPECIALIZED (topology/contradiction/authority).
V1b (system-level benchmark): specialized lenses as in the original protocol
  §4; k, specialization and lens-space covary — declared confound.
Either way: 3 repetitions per campaign; campaigns sequential; goblins within
a campaign parallel (isolation preserved).

## 6. CANONICALIZATION HIERARCHY (stability anti-Goodhart)
π: raw proposition → canonical key, resolved in strict order:
  (1) exact structural identity;
  (2) same predicate + same object + same scope;
  (3) manual/HAL-reviewed semantic merge, logged with justification.
NEVER "LLM says these are duplicates" as a one-shot oracle. Report both
pre-merge and post-merge counts so merge aggressiveness is itself auditable.
N_P (novel canonical propositions) and N_E (novel independent evidence
roots) counted separately; N_P↑ ⊬ N_E↑.

## 7. CONTAMINATION REGISTRY
PREEXISTING_OUTPUTS:
- QWEN_VS_GEMMA4_RECEIPT.json — WRITTEN, UNREAD at this seat.
  Default: EXCLUDED_UNTIL_END (read after campaigns close). Alternative:
  READ_BEFORE_FREEZE (operator verb). Mixing is forbidden: reading it
  mid-experiment = POTENTIAL_LEAKAGE event, logged.
- fable_swarm_v0 envelopes/receipts — READ_BEFORE_RUN (already in context);
  declared. The A/E configuration result is prior knowledge, not corpus.
- Operator-side exposure to related model outputs: declared unknown here.

## 8. THREE RECEIPTS PER CAMPAIGN (no boolean collapse)
CONFIGURATION_RECEIPT (completeness, ρ_i, coverage_effective, result)
EPISTEMIC_RECEIPT (dedup table, HAL trials, N_P/N_E, N_earned or
  NOT_EVALUABLE)
GOVERNANCE_RECEIPT (authority_violations, state_mutations, isolation,
  task_hash integrity, result)
A campaign may be INFORMATIVE / NOT_EVALUABLE / CLEAN simultaneously —
the three verdicts never coerce into one.

## 9. SELECTION — ELIGIBILITY THEN PARETO
Per AMENDMENT_3: Dom(argmax)=ℰ. Within ℰ, report the PARETO view over
(N_earned, N_E, Stability, −Cost, −Review) alongside the scalar
efficiency — the scalar ranks, the frontier exposes tradeoffs, the operator
selects. Efficiency remains a selector, never an admissibility criterion.

## 10. CENTRAL THEOREM CANDIDATE (what the bakeoff can actually test)
Optimize(Θ_C) ⊬ Relax(Θ_A) — cognition allocation and epistemic promotion
are separate optimization spaces. CognitiveScale ⊬ AdmissionSurfaceExpansion.
"Cognition may be optimized. Trust may not be optimized into existence."

## RATIFICATION CHECKLIST (all required before first TASK_HASH)
[ ] Q₁ frozen byte-exact          [ ] corpus scope + fingerprint minted
[ ] B vector frozen               [ ] V1a or V1b chosen
[ ] HAL protocol + I-vector ack   [ ] contamination registry arbitrated
[ ] thresholds S_min/R_max/C_max set (defaults: S_min=0.5, R_max/C_max =
    operator judgment at GO)
