# HELEN_GOBLIN_BAKEOFF_V1 — CONTROLLED GENERATE → DISCRIMINATE → ADMIT EXPERIMENT

STATUS: EXPERIMENTAL · READ_ONLY · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none
PROVENANCE: operator relay 2026-08-20, received verbatim in-session; frozen here
as CANDIDATE protocol, NOT RUN. Execution awaits explicit operator GO.

## 0. PRIME DIRECTIVE
One question: does increasing isolated cognition from 1 → 3 → 5 Goblins produce
more independent, evidence-resolved, falsification-surviving novelty?
More output / agreement / agents is not success. Structural completeness is not
truth. HAL survival is not admission. Preserve:
Candidate → Admission → Receipt → Reducer → State. Cognition has no direct
state morphism.
Core laws: DELIVERABLE ⊬ CAPABILITY · GENERATED ⊬ SUPPORTED · SUPPORTED ⊬
ADMITTED · CONSENSUS ⊬ TRUTH · COMPLETENESS ⊬ BELIEF · DISCRIMINATION ⊬
ADMISSION. Swarm completeness licenses comparison, not belief. Discrimination
licenses candidacy, not admission. Only Γ licenses institutional state change.

## 1. PRE-FLIGHT
Record: Claude Code version · repo HEAD · working-tree status · model ·
read-only tools · timestamp · bounded research question · task_hash of frozen
task · corpus/search scope · per-agent output budget.
Tool posture: Read/Grep/Glob only. No writes, edits, commits, pushes, ledger
mutation, external publication. Dirty tree: record, never clean.

## 2. FREEZE THE QUESTION
Exactly one BOUNDED_QUESTION, byte-identical across C1/C3/C5. Freeze:
TASK_HASH · CORPUS_SCOPE · TOOL_SCOPE · MODEL_CONFIGURATION · OUTPUT_BUDGET ·
HAL_PROTOCOL · EVALUATION_PROTOCOL. Changing one invalidates comparison.

## 3. CAMPAIGNS
C1 = 1 isolated Goblin + independent HAL · C3 = 3 · C5 = 5.
Prefer three repetitions each (Ck-R1..R3). No concurrent campaigns if leakage
possible.

## 4. GOBLIN ASSIGNMENTS
C1: G1 GENERALIST (full bounded question — NOT only the Topology lens).
C3: G1 TOPOLOGY (modules, boundaries, coupling, duplication) · G2 CONTRADICTION
(counterexamples, broken assumptions, failure cases) · G3 AUTHORITY (illegal
promotion, authority leakage, direct effect paths).
C5: + G2 TEMPORAL (history, drift, supersession, replay, temporal assumptions)
and G5 CAPABILITY (reusable organizational/architectural learning).

## 5. ISOLATION LAW
Goblins MAY inspect frozen corpus, reason, propose, cite, construct falsifiers.
MAY NOT see other goblin output, communicate, modify corpus, HAL-adjudicate,
self-admit, claim authority. authority=false · effect_ceiling=PROPOSE ·
ledger_effect=none. No synthesis while generation runs.

## 6. GOBLIN PACKET (exactly one per goblin)
{goblin_id, campaign_id, task_hash, lens, claims:[{proposition_key, claim,
evidence_refs:["file:line"], source_roots, evidence_class:
OBSERVED|REPORTED|INFERRED|UNKNOWN, candidate_falsifier,
confidence:LOW|MEDIUM|HIGH}], contradictions:[], unknowns:[],
forbidden_paths_checked:[], authority:false, ledger_effect:"none"}
Confidence is diagnostic only — never contributes to admission or novelty.

## 7. FREEZE BEFORE DISCRIMINATION
freeze(packet) on finish. No semantic repair, lead rewriting, cross-goblin
synthesis, field-filling, or inference from truncated text after freeze.
Complete(G_i) ∈ {0,1}: required structure present within frozen output.
Truncation ⇒ Complete=0. Process exit is not a completeness witness.

## 8. NO CEILING ESCALATION
Ceiling hit ⇒ do NOT raise it. Truncation is configuration evidence.
Allowed: more bounded prompt, fewer claims, compacter evidence, rerun SAME
ceiling. Not allowed: 4000→8000 merely to obtain completion. Every
prompt-closure retry recorded as retry; never silently replace the original.

## 9. SWARM COMPLETENESS WITNESS
W_swarm(Ck) = {Complete(G1..Gk), RawOutputs, StructuralValidation}; exists iff
every packet structurally complete and frozen. ∃i Complete=0 ⇒ W_swarm=ABSENT ⇒
SENTINEL_EARNED_NOVELTY(Ck)=NOT_EVALUABLE. Never manufacture completeness.

## 10. LINEAGE DEDUPLICATION (post-freeze, pre-HAL)
Same source → five paraphrases ≠ five independent supports. Record per (p,q):
same_proposition? same_source_root? same_evidence_lineage? independent_support?
Produce RAW_PROPOSITIONS · DISTINCT_PROPOSITIONS · LINEAGE_GROUPS.
No voting, no confidence averaging.

## 11. INDEPENDENT HAL (only after W_swarm exists; exactly one)
Non-participant; receives frozen packets + frozen corpus; may not create
replacement propositions, repair arguments, or admit. For every distinct p,
actively attempt its candidate falsifier. Return {proposition_key, trial,
result: SURVIVED|REFUTED|INCONCLUSIVE, supporting_evidence, counterevidence,
reason}. SURVIVED = declared falsification attempt did not refute p within
declared scope — NOT true. REFUTED = failed its test. INCONCLUSIVE = evidence
cannot resolve.

## 12. SENTINEL TRANSLATION
Only frozen propositions + HAL results enter Sentinel, explicitly translated to
DECLARE_HYPOTHESIS / INGEST_ATOM / RECORD_FALSIFICATION. No implicit adapter
semantics until an adapter is itself witnessed. Replay via existing harness.
Successful execution ≠ proposition truth.

## 13. EARNED NOVELTY
p contributes iff Distinct(p) ∧ EvidenceResolved(p) ∧ HAL(p)=SURVIVED ∧
LineageDeduplicated(p). N_earned(Ck) = |{p: all four}|. Never count
INCONCLUSIVE, REFUTED, duplicate, truncated, unsupported, unfalsified.

## 14. METRICS (per campaign)
RAW_PROPOSITION_COUNT · DISTINCT_PROPOSITION_COUNT · EARNED_NOVELTY ·
DUPLICATE_RATE = 1 − Distinct/Raw · CONTRADICTIONS_DISCOVERED ·
RESOLUTION_RATE = (SURVIVED+REFUTED)/(SURVIVED+REFUTED+INCONCLUSIVE) ·
TOKEN_COST · LATENCY · OPERATOR_REVIEW_TIME · AUTHORITY_VIOLATIONS ·
FORBIDDEN_PATH_ATTEMPTS · TRUNCATED_PACKETS · RETRIES ·
η_k = N_earned(Ck)/Tokens(Ck) · Δ_{1→3} = N_earned(C3)−N_earned(C1) ·
Δ_{3→5} = N_earned(C5)−N_earned(C3).

## 15. REPEATED-RUN STABILITY
Stability_k = |∩_r E_{k,r}| / |∪_r E_{k,r}| — reported separately from novelty.
A large unstable swarm is not automatically superior to a smaller stable one.

## 16. HARD GATES (any ⇒ campaign FAIL)
authority violation > 0 · unfalsified claim counted as novelty · same-lineage
support counted twice · proposer performs own HAL review · incomplete/truncated
packet counted · goblin sees another packet before freeze · lead repairs
proposition before HAL · state mutation during read-only campaign.

## 17. DECISION RULE
Keep C5 only if N_earned(C5) > N_earned(C3) AND violations=0 AND stability
acceptable AND duplicate rate doesn't erase the gain AND marginal token cost
acceptable AND review burden acceptable. Else prefer C3; if C1 equivalent
post-falsification, prefer C1. Target: max falsification-surviving novelty
s.t. authority=0, review ≤ budget, cost ≤ budget, stability ≥ threshold.

## 18. STOP CONDITIONS
STOP: authority boundary crossed · corpus mutation · task_hash changes ·
isolation fails · HAL generates hypotheses · incomplete packets promoted ·
comparison conditions diverge. HOLD if evidence insufficient. Never
manufacture PASS.

## 19. OUTPUT
EXPERIMENT_STATUS · PRE_FLIGHT · TASK_HASH · CAMPAIGN_TABLE ·
RAW_GOBLIN_PACKETS · STRUCTURAL_COMPLETENESS · LINEAGE_DEDUPLICATION ·
HAL_TRIALS · SENTINEL_EVENTS · EARNED_NOVELTY · METRICS · HARD_GATE_RESULTS ·
STABILITY · COST_LATENCY_REVIEW · FALSIFIERS · DECISION · UNKNOWN_UNRESOLVED ·
RECEIPT.

## 20. RECEIPT LAW
COMMAND_SUCCEEDED ⊬ PACKET_COMPLETE ⊬ SWARM_COMPLETE ⊬ HAL_DISCRIMINATED ⊬
NOVELTY_EARNED ⊬ ADMITTED. No command output or model assertion is a
completion witness.

## 21. PHASE TWO — COMMUNICATION ABLATION (only after isolated baseline)
Repeat winning isolated configuration with communicating agent teams, same
bounded question/evaluation. Question: does inter-agent communication increase
independently falsification-surviving novelty? Also measure CONVERGENCE_RATE ·
CROSS_AGENT_INFLUENCE · NOVELTY_LOSS · DUPLICATE_REDUCTION ·
CONTRADICTION_LOSS. Principal falsifier: communication increases agreement
while decreasing independent proposition diversity or surviving novelty.

## 22. FINAL HELEN LAW
GOBLINS generate → freeze → HAL discriminates → survived claims → SENTINEL
(evidence+novelty) → candidate → Γ admits → receipt → REDUCER → state.
Goblins cannot admit. HAL cannot admit. Sentinel cannot mint authority.
Consensus cannot mint truth. Only the admission boundary authorizes
institutional change.

## 23. EXPERIMENTAL SLOGAN
Not "how many agents can HELEN run?" but "how much independent,
falsification-surviving novelty does each additional unit of cognition earn?"
VALUE(k) = ΔEarnedKnowledge / ΔCognitiveCost. The experiment succeeds even if
1 > 3 > 5. A negative scaling result is knowledge.

## APPLIED IMMEDIATELY TO THE CURRENT RUN (operator dry rule)
A,E=TRUNCATED ⇒ W_swarm=∅ ⇒ HAL_global=BLOCKED ⇒ N_earned=NOT_EVALUABLE.
The swarm is NOT to be saved. The k-vs-completeness datum is the earned
observation. Sealed in fable_swarm_v0/HELEN_FABLE_SWARM_RECEIPT.json
(receipt_hash 155d2c03a1a3ee18, final_status HOLD).
