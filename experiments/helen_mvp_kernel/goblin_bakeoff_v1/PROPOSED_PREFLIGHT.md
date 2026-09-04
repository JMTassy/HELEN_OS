# BAKEOFF_V1 — PROPOSED PRE-FLIGHT (awaiting operator ratification)

STATUS: PROPOSAL · nothing frozen yet · no goblin launched · authority=false.
Ratifying this file (operator verb "GO BAKEOFF" or edits + GO) freezes the
four open items and licenses computation of the first TASK_HASH.

## 1. BOUNDED_QUESTION (candidate — byte-identical across C1/C3/C5 once frozen)
"Within the frozen corpus experiments/helen_mvp_kernel/** at commit 0bdbf06,
identify: (a) defects or contradictions between receipts and the code they
describe; (b) authority-leak or illegal-promotion risks; (c) temporal drift
between documents and witnessed state; (d) reusable architectural
capabilities. Every claim must cite file:line evidence, declare its evidence
class (OBSERVED|REPORTED|INFERRED|UNKNOWN), and include a candidate
falsifier."

## 2. CORPUS_SCOPE (candidate)
experiments/helen_mvp_kernel/** read-only, pinned at HEAD 0bdbf06c270ef4cb.
Excluded: all sovereign-firewall paths (read allowed by policy but out of
corpus to keep scope small), .venv-gates/**, raw model logs > 1 MB.

## 3. OUTPUT_BUDGET (candidate — closed-role style per O₁/H₁)
Structural budget, not just a token ceiling: per packet max 8 claims; each
claim ≤ 2 sentences + ≥1 file:line ref; contradictions/unknowns ≤ 5 items
each; whole packet ≤ 450 words. Ceiling fixed across ALL campaigns and
retries (no escalation, per protocol §8). ρ_i recorded for every packet.

## 4. AGENT SUBSTRATE + HAL_PROTOCOL (candidate — needs explicit arbitrage)
- Goblins: isolated Claude sub-agents (read-only tools: Read/Grep/Glob),
  one per lens, no cross-visibility, spawned per campaign. Parallel WITHIN a
  campaign is admissible (isolation holds); campaigns sequential.
- HAL: ONE fresh Claude sub-agent per campaign, non-participant context,
  receives frozen packets + corpus paths, actively attempts each declared
  falsifier via Read/Grep. proposer ≠ validator at CONTEXT level.
- DECLARED CAVEAT: goblins and HAL share model weights (same Claude) —
  lineage note in every campaign receipt; weights-level separation (local
  Qwen/Gemma HAL) is a later ablation arm, not V1.

## 5. CAMPAIGN PLAN (candidate)
C1 (G1 GENERALIST) · C3 (TOPOLOGY, CONTRADICTION, AUTHORITY) ·
C5 (+TEMPORAL, +CAPABILITY) · 3 repetitions each = 27 goblin packets +
9 HAL runs. Lineage dedup + canonicalization (AMENDMENT_1 lock 4) between
freeze and HAL. Metrics per §14 + ρ_i + N_P/N_E + C_internal/C_corpus +
MV_{1→3}, MV_{3→5} + Stability_k.

## WHAT RATIFICATION DOES NOT LICENSE
No commit, no push, no ledger effect, no admission of any surviving
proposition, no scaling law claimed before comparable campaigns complete.
