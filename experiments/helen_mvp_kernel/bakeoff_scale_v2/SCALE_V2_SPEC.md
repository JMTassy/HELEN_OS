<!-- authority=false · canon=false · ledger_effect=none · measurement specification, not a ruling -->

# BAKEOFF SCALE_V2 — Independence Measurement Specification

**Status:** SPEC + instrument BUILT + validated on V1 replay · live campaign NOT executed (separate `EXECUTE SCALE_V2` verb).

## Deliverable set (spec-only)
- `SCALE_V2_SPEC.md` (this file — master) · `METRIC_DEFINITIONS.md` (N_RAW/N_P/N_E/N_F/N_L) · `PROPOSITION_SCHEMA.json` · `PROVENANCE_SCHEMA.json` (ancestry graph + independence status) · `CANONICALIZATION_RULES.md` (two-stage, structural→semantic) · `FALSIFIERS.md` · `scale_v2_metric.py` (+ `--self-test`, `--rescore-v1`).

## SCALE_V1 — frozen falsified instrument (mutation FORBIDDEN)
```
SCALE_V1  GOVERNANCE_RESULT = SURVIVED_THIS_TEST
          SCALING_METRIC    = INVALIDATED_BY_LINEAGE_FANOUT / LEXICAL_DEDUP
          SCALING_LAW       = NOT_ADMITTED
          SCALE_V1_MUTATION = FORBIDDEN
```
The strongest positive statement V1 earned: `k:1→5 with Γ_A=∅`, no observed authority expansion in that setup ⇒ `ΔCognition>0 ⇏ ΔAuthority>0` **survived this test** (not yet a universal theorem). The claim `ΔCognition>0 ⇒ ΔKnowledge>0` was **not** established — the knowledge counter was defective.

**Relationship to V1:** `SCALE_V1` is **preserved permanently as the falsified instrument** — not modified, not deleted. V2 is a **new measurement specification**; it changes *how independence is measured*, and changes **nothing** about the governance architecture (`Γ_A=∅`, admission gates, seal discipline all carry over unchanged).

## Hard laws (frozen)
```
LexicalDistinct   != SemanticDistinct
SemanticDistinct  != EpistemicIndependent
DifferentFiles    != IndependentRoots
DifferentAgents   != IndependentRoots
HAL_SURVIVED      != TRUE
N_P↑ ⇏ N_E↑   ·   N_E↑ ⇏ N_F↑   ·   N_F↑ ⇏ N_L↑
Semantic canonicalization may USE embeddings/entailment as aids; provenance independence is established SEPARATELY.
Unknown provenance ancestry stays UNKNOWN, never Independent.
```

## The defect V2 fixes

SCALE_V1 measured independence lexically: `Distinct(pᵢ,pⱼ) = [strings differ]`. So k goblins emitting the same claim in k wordings counted as k independent roots → `N_earned = 0.8·k`, a **fan-out artifact**. The governing law V2 encodes:

```
lexical difference  ≠  independent knowledge
SemanticDistinctness  ≠  EpistemicIndependence
```

Semantic difference tells you two propositions *mean* different things; it **cannot** tell you they rest on *independent provenance*. Both are required. Hence a **two-stage** pipeline.

## Pipeline

```
RAW SURVIVED CLAIMS
      ↓  STAGE 1 — SEMANTIC CANONICALIZATION   (entailment/NLI judge; paraphrases → one canonical proposition)
CANONICAL PROPOSITIONS
      ↓  STAGE 2 — PROVENANCE-ROOT RESOLUTION   (where does each canonical proposition ultimately rest?)
INDEPENDENT ROOT COUNT
      ↓  × FALSIFICATION STATUS (HAL)
N_E  /  N_F  /  N_L
```

- `5 agents → 1 proposition → 1 root` when all cite the one source document.
- `1 proposition ← 3 disjoint sources → 3 independent roots` when provenance is genuinely independent.

The hierarchy becomes experimentally measurable, each level non-implying the next:
```
N_P (propositions)  ↛  N_E (independent provenance roots)  ↛  N_F (falsification-surviving)  ↛  N_L (lineage-ready)
```

## Proof the fix works — re-score of frozen SCALE_V1 data (no new model calls)

`scale_v2_metric.py --rescore-v1` reads the **frozen** V1 bundle (`82fa01e9…`, unmodified) and re-scores its raw survived propositions with the V2 instrument:

| config | k | V1 `N_earned` (lexical) | V2 `N_canonical` (stage 1) | V2 `N_E` (stage 2, roots) |
|---|---|---|---|---|
| C1 | 1 | 0.8 | 0.8 | 0.2 |
| C3 | 3 | 2.4 | 1.2 | 0.6 |
| C5 | 5 | **4.0** | **1.4** | **1.0** |
| **Δ(C5−C1)** | | **+3.2 (≈0.8·k, fan-out)** | **+0.6 (~5.3× flatter)** | **+0.8, capped ≤ 1** |

**Reading (honest, no overclaim):**
- **Stage 1 (semantic) crushes the fan-out** — slope `+3.2 → +0.6`, a ~5.3× reduction. The k paraphrases-of-one-claim no longer inflate the count. The V1 `0.8·k` signal was lexical, not epistemic.
- **Stage 2 (provenance) caps independence at the corpus's true root count.** This corpus is **one document** → 1 provenance root, so V2 `N_E ≤ 1` — it can *never* report the 5 that V1 implied. It respects that ceiling (max 1.0).
- **The residual is real, not fan-out.** `N_canonical` drifts 0.8→1.4 because occasionally a *second* canonical proposition (an Egyptian-origin or OTHER claim) survives at higher k. A correct metric should surface that small genuine diversity — not force it to zero. This is signal, not artifact.
- **The instrument is not "always collapse to 1."** `--self-test` proves it counts `N_E=3` when a claim genuinely rests on 3 disjoint sources — so it measures real independence when real independence exists.

## Requirements for a LIVE SCALE_V2 campaign (separate `EXECUTE SCALE_V2`)

The re-score used a **deterministic origin-signature PROXY** for Stage 1, sufficient to replay this single-answer corpus. A live campaign must upgrade:

1. **Stage 1 = a real entailment/NLI judge** (embeddings alone are insufficient — embed distance ≠ mutual entailment). Two propositions collapse iff they mutually entail.
2. **Provenance is MANDATORY.** Goblins must cite `evidence_refs`; a survived proposition with no provenance is `NOT_KNOWLEDGE`, not an independent root. (The V1 re-score's low `N_E` at small k partly reflects goblins leaving `evidence_refs` empty — a live V2 forbids that.)
3. **Multi-source corpus with a KNOWN independent-root structure** — so `N_E` has legitimate headroom to exceed 1, and the experiment can actually test whether higher k finds *more independent roots* (the real scaling question, which a 1-root corpus cannot pose).
4. **`N_F` = falsification-surviving canonical propositions**, `N_L` = lineage-ready (provenance + falsification + scope resolved). Report all four levels separately; never collapse.
5. **All V1 governance carries over unchanged:** `Γ_A=∅` across k, admission gates, prereg seal, fixed R + no top-up, independent peer-review of receipts.

## The chiddush this run produced

Not a scaling law — a **measurement law**: *agent-count scaling and epistemic scaling require different metrics.* SCALE_V1 didn't merely fail; it demonstrated **why** `N_agents↑ ↛ N_independent_roots↑`, and V2 operationalizes the distinction. Governance held clean throughout (`ΔCognition>0 ⇏ ΔAuthority>0`, experimentally supported k=1→5 with `Γ_A=∅`); only the yield instrument needed repair.

## Firewall
Non-sovereign `experiments/helen_mvp_kernel/bakeoff_scale_v2/`. Reads V1 read-only; **modifies nothing under bakeoff_scale_v1/**. No sovereign-path writes. Sidecars only. `authority=false · canon=false · ledger_effect=none`. Not committed.
