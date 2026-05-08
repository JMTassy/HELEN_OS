# HD-004 — DOCTRINE QUINTET AUTOEVALUATION

**Story:** HD-004  
**Epoch:** d0f97baa8aa3  
**Actor:** DAN_GOBLIN  
**Authority:** NON_SOVEREIGN  
**Canon:** NO_SHIP  
**Date:** 2026-05-08  
**Status:** EVALUATION_COMPLETE — `reducer_decision: null` — awaiting MAYOR  

---

## Scope

All 5 doctrine proposals inspected:
- `docs/proposals/EPISTEMIC_SYNTAX_V1.md`
- `docs/proposals/LATENT_WORLD_WITNESS_V1.md`
- `docs/proposals/BAYESIAN_WITNESS_V1.md`
- `docs/proposals/PURE_PREDICTOR_GATE_V1.md`
- `docs/proposals/TRUTH_PREDICTION_OBJECTIVE_V1.md`

---

## Acceptance criteria — results

| Criterion | Result |
|---|---|
| All 5 doctrine proposals read and inspected | PASS |
| Cross-references between docs verified | PASS with gaps (see below) |
| Gaps or contradictions identified and named | PASS — 4 findings |
| ORACLE_TO_POLICY_BOUNDARY present in PURE_PREDICTOR_GATE_V1 | PASS |
| ORACLE_TO_POLICY_BOUNDARY present in TRUTH_PREDICTION_OBJECTIVE_V1 | PASS |
| Findings report written to docs/reports/ | PASS (this file) |
| No code mutation, no ledger write, no sovereign path write | PASS |
| reducer_decision remains null — MAYOR validates | PASS |

---

## Finding 1 — STRUCTURAL BUG: Empty JOINT_DISTRIBUTION_WITNESS stub

**File:** `docs/proposals/LATENT_WORLD_WITNESS_V1.md`, lines 163–165  
**Severity:** HIGH — confuses readers, breaks document structure  

The file contains a bare section header with no content:

```markdown
## JOINT_DISTRIBUTION_WITNESS

---

## FORCED_LATENT_COMMITMENT
```

The actual JOINT_DISTRIBUTION_WITNESS content (definition, observed variables, forced-latent-variable rule, flat earth example, failure modes, law) appears correctly at the second occurrence of this section header (line 338+). The first occurrence is a vestigial stub — it was placeholder markup that was never removed when content was inserted further down.

**Recommended fix:** Remove the empty stub at lines 163–165 (the header + divider with no body). The second full section is the canonical one.

---

## Finding 2 — Vocabulary inconsistency: epistemic tag names

**Severity:** MEDIUM — tag vocabularies diverge across three docs

| Doc | Tag vocabulary used |
|---|---|
| EPISTEMIC_SYNTAX_V1 (canonical) | COMMUNICATION_ACT, MYTHIC_SIGNAL, LOCAL_OBSERVATION, VERIFIED_TEST, FORMAL_PROOF, SCIENTIFIC_MEASUREMENT, CANONICAL_CLAIM |
| BAYESIAN_WITNESS_V1 output schema | COMMUNICATION_ACT, VERIFIED_ANCHOR, LOCAL_OBSERVATION, VERIFIED_TEST, MYTHIC_SIGNAL |
| PURE_PREDICTOR_GATE_V1 output schema | COMMUNICATION_ACT, VERIFIED_CLAIM, LOCAL_OBSERVATION, VERIFIED_TEST, MYTHIC_SIGNAL |

**Discrepancies:**
- BAYESIAN_WITNESS uses `VERIFIED_ANCHOR` — not in EPISTEMIC_SYNTAX's canonical tag list
- PURE_PREDICTOR_GATE uses `VERIFIED_CLAIM` — not in either list
- Neither BAYESIAN_WITNESS nor PURE_PREDICTOR_GATE includes `FORMAL_PROOF`, `SCIENTIFIC_MEASUREMENT`, or `CANONICAL_CLAIM`

**Recommended fix:** Align BAYESIAN_WITNESS and PURE_PREDICTOR_GATE output schema `epistemic_tag` fields to use the EPISTEMIC_SYNTAX_V1 canonical set. `VERIFIED_ANCHOR` and `VERIFIED_CLAIM` are not canonical tags — they are conceptual shorthand that does not appear in the intake tagger.

---

## Finding 3 — Naming inconsistency: statement_kind vs epistemic_tag

**Severity:** LOW — different field names for the same concept

`TRUTH_PREDICTION_OBJECTIVE_V1.md` training example schema uses field name `"statement_kind"`.  
All other docs use `"epistemic_tag"`.

Both refer to the same concept: the EPISTEMIC_SYNTAX intake classification label.

**Recommended fix:** Rename `statement_kind` to `epistemic_tag` in TRUTH_PREDICTION_OBJECTIVE_V1.md training example schema to align with all other docs.

---

## Finding 4 — Missing forward references in EPISTEMIC_SYNTAX

**Severity:** LOW — navigational gap, not a correctness error

`EPISTEMIC_SYNTAX_V1.md` is positioned as the intake layer ("the first act of honesty is labeling"). It defines the tags used by downstream layers. But it contains no forward references to:
- LATENT_WORLD_WITNESS (which consumes tagged inputs)
- BAYESIAN_WITNESS (which scores tagged claims)
- PURE_PREDICTOR_GATE (which scores tagged actions)

A reader entering the doctrine at EPISTEMIC_SYNTAX cannot follow the pipeline forward without reading all five docs in order.

**Recommended fix:** Add one short integration note at the end of EPISTEMIC_SYNTAX_V1.md pointing to the downstream layers:

> Tagged inputs flow to LATENT_WORLD_WITNESS (inference), BAYESIAN_WITNESS (claim scoring), and PURE_PREDICTOR_GATE (action scoring). See those proposals for downstream doctrine.

---

## Cross-reference consistency map

| Claim | Verified |
|---|---|
| LATENT_WORLD_WITNESS integration table references EPISTEMIC_SYNTAX and BAYESIAN_WITNESS | ✓ |
| LATENT_WORLD_WITNESS pipeline diagram includes BAYESIAN_WITNESS and PURE_PREDICTOR_GATE | ✓ |
| PURE_PREDICTOR_GATE vs BAYESIAN_WITNESS distinction table | ✓ |
| PURE_PREDICTOR_GATE complete epistemic stack lists all 5 layers in order | ✓ |
| TRUTH_PREDICTION_OBJECTIVE doctrine quintet summary lists all 5 | ✓ |
| ORACLE_TO_POLICY_BOUNDARY in PURE_PREDICTOR_GATE_V1 (before canon lines) | ✓ |
| ORACLE_TO_POLICY_BOUNDARY in TRUTH_PREDICTION_OBJECTIVE_V1 (before canon lines) | ✓ |
| FORCED_LATENT_COMMITMENT covered across EPISTEMIC_SYNTAX, LATENT_WORLD_WITNESS, TRUTH_PREDICTION_OBJECTIVE | ✓ appropriate distribution |
| SCAFFOLDED_AGENCY_RISK covered in PURE_PREDICTOR_GATE (runtime) and TRUTH_PREDICTION_OBJECTIVE (training) | ✓ appropriate distribution |
| RALPH revert (b9762b5→2d2c760) cited as canonical HELEN SCAFFOLDED_AGENCY_RISK example | ✓ |
| NON_AGENTIC_PREDICTOR_BOUNDARY (weather model) in PURE_PREDICTOR_GATE | ✓ |
| HAL boundary asserted in all 5 docs | ✓ |
| authority=false in all 5 docs | ✓ |
| canon=NO_SHIP in all 5 docs | ✓ |

---

## Summary

The doctrine quintet is **internally coherent**. The five proposals chain correctly: EPISTEMIC_SYNTAX (intake) → LATENT_WORLD_WITNESS (inference) → BAYESIAN_WITNESS (claim scoring) → PURE_PREDICTOR_GATE (action scoring) → TRUTH_PREDICTION_OBJECTIVE (training target). All HAL boundaries are consistently asserted. ORACLE_TO_POLICY_BOUNDARY is present in both required docs.

**4 findings:**
1. STRUCTURAL BUG — empty JOINT_DISTRIBUTION_WITNESS stub in LATENT_WORLD_WITNESS (HIGH — fix recommended before COMMIT+PUSH)
2. Vocabulary inconsistency — epistemic tag names across 3 docs (MEDIUM)
3. Naming inconsistency — `statement_kind` vs `epistemic_tag` (LOW)
4. Missing forward references in EPISTEMIC_SYNTAX (LOW)

**`reducer_decision: null` — MAYOR validates.**

---

*Epistemic tag: LOCAL_OBSERVATION. Authority: false. Canon: NO_SHIP.*
