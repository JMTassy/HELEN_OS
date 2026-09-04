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

## AMENDMENT (2026-08-13, post-negative-controls — NEGATIVE_CONTROLS.json)

The mandated controls (K_mem, K_random, permutation null) were run
after the initial verdicts. They CHANGE the results:

- **PRICE_MONOTONE_SIZE: DEMOTED SUPPORTED → NOT BETTER THAN CHANCE.**
  Held-out support 1.0 (n=8 groups) looked perfect, but the groups are
  tiny (mostly 2 elements): under a within-group price-permutation
  null, shuffled data is fully monotone in 49.1% of 5000 trials
  (p ≈ 0.49). The swarm's flagship rule is indistinguishable from
  chance at this sample size. Eight workers converging on it was one
  lineage amplifying an under-powered pattern.
- **PRICE_PER_UNIT band [2.5, 15]¢/in: UPGRADED to SUPPORTED-vs-
  control.** Observed support 0.974 (n=39); only 2.1% of 5000 random
  equal-log-width bands match or beat it (p ≈ 0.021). The one rule
  that survives a real null.
- **K_mem control: 0/40** held-out hits (deduped corpus) — confirms
  any nonzero generalization beats memorization, but also that the bar
  was trivially low; the permutation null is the binding control.

Run-1 verdict, restated: **the swarm's only control-surviving
discovery is the price-per-inch band.** Monotonicity needs bigger
ladders (≥3-element groups) before it can be evidence. This amendment
is the TWO_SYSTEM doctrine biting its own output — selection ≠
promotion, and a held-out 1.0 is not a result until it beats a null.

## DISCRIMINATE output (per the new verb)

- Monotone-threshold variants (20/24/30/36 in) are distinguished by
  specimens with lengths bracketing 20–36 in within one family×point
  ladder — lengths present in corpus: 12–72 in, so the data EXISTS;
  extraction needs to capture more of it (current parser recovers 162
  of a much larger specimen population).
- PHASE_PAIR: 4/4 equal-price on full set; discriminating data =
  pair-stratified resplit putting ≥2 matched pairs in held-out.
- Structural grammar B=(g,τ,ρ,κ,σ,λ): NOT discriminable from metadata
  at all — requires visual ORB on page images.

## RETYPE (audit round 2, adopted)

All "REFUTED" verdicts in this run are **REFUTED_IN_H** — the
hypothesis class searched was the 6-template DSL over OCR metadata;
nothing here bounds grammars outside that class (visual grammars are
untouched). "DESCRIPTIVE_TAXONOMY" is a disposition, not an ontology
claim. Conclusion type of this whole run: BOUNDED_PROPERTY_TEST — an
instance, not a theorem. Corpus identity tuple correction: the local
PDF has 1267 SCAN IMAGES; bibliographic pagination is xvi+1188
(1900 ed.) / xvi+1168 (1902 ed.) per public catalogues — scans ≠
printed pages; edition of the local digitization not yet pinned.
Root ID going forward: (work, edition, holding, digitization,
sha256), not a filename. Held-out isolation note: workers never saw
held-out rows, but final verdict selection read them once — future
runs freeze K̂ (seal) before unsealing O_test.

## Next stage (held for verb)

1. Pair-stratified re-split + harness repair (reject degenerate
   ranges) — cheap, sharpens PHASE_PAIR to a real held-out test.
2. Visual Orb(p) recovery from page images — the true capability-
   complex test.
3. FETCH 1851 as out-of-distribution validation of whatever survives.
