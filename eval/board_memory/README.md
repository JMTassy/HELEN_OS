# Board Memory Falsifier (V0)

<!-- NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
     2026-08-10. The falsifier is built BEFORE the believer, per the
     discipline: a harness that cannot detect collapse would pass any
     pipeline. No file under helen_os/governance/, helen_os/schemas/,
     town/, or any kernel path is touched by this directory. -->

**The falsifiable question** (from the Board Memory deep dive):

> Can HELEN reconstruct organizational decisions more reliably, traceably,
> and usefully than ordinary RAG — specifically, without confusing a
> conversation with an agreement?

This directory is the measuring instrument for that question, not an answer to it.

## Contents

| file | role |
|---|---|
| `gold_set_schema.json` | `GOLD_SET_V1` — gold annotations incl. **collapse-bait** items (`proposal_as_decision`, `paraphrase_agreement`, `claim_as_fact`, `hearsay_provenance`) |
| `output_schema.json` | `BOARD_MEMORY_OUTPUT_V1` — pipelines must report **per-layer** verdicts (extractor / verifier / gate) so collapse is attributable |
| `scorer.py` | Deterministic scorer: P, R, `p_prov`, `c_abstain`, `bait_catch_rate`, and **`e_collapse` decomposed by failing layer** |
| `baseline_rag.py` | The indictable baseline: flat keyword-RAG, one opinion + three rubber stamps. Supposed to fail the baits |
| `fixtures/` | `board_corpus_v0` (8 docs: real decision, commitment, open question, contradiction pair, 3 baits) + `board_gold_v0` (8 items) |
| `run_falsifier.py` | Runner. `--pipeline baseline` works today; `--pipeline helen` is a typed interface that raises until the governed pipeline exists |
| `test_falsifier.py` | 8 tests proving the harness itself: perfect pipeline scores clean; collapse attributed to the correct layer; **baseline demonstrably collapses** (the teeth); scorer determinism |

## Baseline verdict (fixtures v0, reproducible)

```text
python3 eval/board_memory/run_falsifier.py --pipeline baseline

precision 0.2857 · recall 1.0 · p_prov 1.0 · c_abstain 0.0
bait_catch_rate 0.0 · e_collapse 0.7143  (extractor: 5, verifier: 0, gate: 0)

COLLAPSE G-04 proposal_as_decision   proposed    → "decision"
COLLAPSE G-05 paraphrase_agreement   discussed   → "decision"
COLLAPSE G-06/G-07 (contradiction)   contradicted→ "decision" (both sides at once)
COLLAPSE G-08 hearsay_provenance     unknowable  → "decision"
```

This is the product thesis as a number: ordinary extraction **finds everything and types nothing** — perfect recall, 71% category collapse, zero abstention. A governed pipeline wins not by finding more but by refusing better.

## Design commitments

1. **E_collapse is decomposed, never flat.** A single number hides which membrane failed. The Season-02/ARC-03 lesson is encoded: a verifier can PASS what a gate must still refuse; each layer is scored on its own honesty.
2. **Baits are permanent fixtures.** Every gold set carries deliberate traps; `bait_catch_rate` and `c_abstain` are the board-facing scores. If the baseline ever stops failing them, the fixtures have rotted.
3. **Determinism law.** Pure stdlib, no wall-time, no randomness, canonical serialization; same inputs → same report bytes (`test_scorer_deterministic`).
4. **The believer implements `HelenPipeline.run()`** emitting `BOARD_MEMORY_OUTPUT_V1` with honest per-layer verdicts, and is scored by the *same* gold set as the baseline. Nothing in this harness grants it anything.

```text
STATUS        : FALSIFIER READY (believer absent, by design)
AUTHORITY     : DENY
CANON         : FALSE
LEDGER_EFFECT : NONE
```
