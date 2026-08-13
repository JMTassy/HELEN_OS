# T-INDUB-01 REFEREE SUMMARY — inverse grammar induction, ATF Desk Book
<!-- 🟠 REVIEW / PROPOSAL — authority=false, no admission implied -->

## Run facts (manifested)

20/20 epochs completed, alternating gemma4-12b (avg ~42s) and
gemma-4-26B-A4B (avg ~150s). 43 rules accumulated; every call carries
(worker, model, epoch, SEED, prompt_sha, output_sha) in
indub_results.json — first fully-manifested swarm at this seat.
Dataset: 162 specimens from the verified OCR (sha fbd38ee9…), 122
train / 40 held-out; held-out sealed from workers throughout.
Format-failure rate: 5/20 worker outputs unparseable (JSON drift) —
counted as dead epochs, not evidence.

## Verdicts (EDI-deduplicated — lineages, not rule-count)

- **SUPPORTED — PRICE_MONOTONE_SIZE** (held-out support 1.0, n=8
  family×length groups). Price nondecreasing in point size. Emitted
  by 8 workers ⇒ ONE lineage (shared corpus+prompt ancestry), counted
  once.
- **SUPPORTED (weak) — PRICE_PER_UNIT band** ≈2.5–15 ¢/inch
  (0.97, n=39). Wide but non-trivial.
- **DEGENERATE (referee self-catch) — PRICE_PER_UNIT_RANGE {}** with
  empty params scored 1.0 via defaults (0..∞) — an always-PASS rule,
  exactly the T_inv/T_flip degeneracy the metrology chiddush warns
  about. Excluded. Harness repair queued: reject param-less range
  rules.
- **HOLD — PHASE_PAIR_EQUAL_PRICE**: 4/4 matched OPEN/TINT pairs
  equal-price on the FULL set, but held-out contained zero matched
  pairs (n=0 ⇒ UNCHECKABLE there). Needs pair-stratified split.
- **HOLD — FAMILY_POINTS** (ART [12,18,24]+OCR-noise "1"; NEWSPAPER
  [6,18] n=3).
- **REFUTED pile**: mostly type/format errors (workers emitting
  "24IN" strings where ints required) — format noise, not semantic
  refutation; plus genuinely wrong size-ladders.

## T-INDUB-01 result: **HOLD, with one SUPPORTED substructure**

A compact PRICING structure is recoverable and predicts held-out
specimens (monotonicity + band). A full generative grammar 𝕂̂ was NOT
demonstrated: what the swarm recovered is metadata-level regularity
(catalogue economics), not the visual production grammar
B=(g,τ,ρ,κ,σ,λ). The harder inverse problem — printed specimen p ↦
{grammars capable of generating p} — requires the page IMAGES (on
disk, 1267pp PDF), not the OCR metadata. Per the operator's guard,
carried forward unbroken:

    Reconstructible(p) ⇏ HistoricallyUsed(p)

No rule here claims historical use; all claims are about catalogue
structure under the stated extraction.

## Next stage (held for verb)

1. Pair-stratified re-split + harness repair (reject degenerate
   ranges) — cheap, sharpens PHASE_PAIR to a real held-out test.
2. Visual Orb(p) recovery from page images — the true capability-
   complex test.
3. FETCH 1851 as out-of-distribution validation of whatever survives.
