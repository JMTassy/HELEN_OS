# RUN 2026-08-15 — OBLITERATUS SURGERY: law encoded, audit HELD

authority=false · claim=NO_CLAIM · non-sovereign

## Mission received

Iteratively optimize HELEN OS until a deterministic audit over a
frozen 842-prompt corpus shows FRR_benign < 5% with UCR_harmful under
a frozen safety threshold, quality/style preserved, everything
replayable. Governing law: minimize unnecessary refusal, preserve
necessary refusal, never trade safety for a prettier metric, never
call an instrument failure a behavioral result.

## Verdict on the audit itself: HOLD (instruments absent, witnessed)

The mission's own corpus contract cannot be discharged in this
environment, and running the loop anyway would be the exact
fabrication this kernel exists to refuse. Witnessed absences, queries
recorded:

- **842-prompt corpus: NO_RECEIPT.** `grep -rn '842'` over the repo:
  every hit is a substring coincidence inside SHA-256 hex digests
  (`spec/CWL_TEST_VECTORS_V1.json` etc.). No prompt corpus of that
  size, with benign/ambiguous/harmful labels, exists on disk.
- **Model under test: NO_RECEIPT.** `scripts/eval_helen.py` expects a
  live Ollama/mlx endpoint; neither runtime is present in this
  container. HELEN OS in this repo is a set of deterministic Python
  constitution modules, not a served language model.
- **Evaluator at mission grade: PARTIAL.** The nearest instruments
  found: `data/helen_sft_eval.jsonl` (52 items, six HELEN behavior
  labels, gold answers) and the V0 keyword classifier in
  `scripts/eval_helen.py`.

Per the mission's own law — *measurement failure is not behavioral
evidence* — the absent corpus is an instrument absence, typed
EXECUTION_ERROR at the harness level, never converted into any claim
about HELEN's refusal behavior. FRR/UCR numbers reported from this
environment today would be RECEIPT_TEXT without REPRODUCIBLE_RESULT.

## What ran instead: the loop's constitution, executable

`constitution/obliteratus_surgery.py` (+25 tests, +1 gate probe)
encodes the mission so that the day the instruments exist, the loop
runs under refusals rather than enthusiasm:

- **Corpus contract** — `freeze_corpus` pins prompts, ids, labels,
  harm categories, evaluator/model/system-prompt/decoding/scoring
  digests into one hash; `expected_n=842` makes the operator's count
  checkable (E_CORPUS_SIZE_MISMATCH). `iterate_license` refuses any
  iteration without a frozen manifest (E_UNFROZEN_CORPUS).
- **Relabel law** — after output is observed, silent relabel is
  E_POST_HOC_RELABEL; genuine dispute goes to LABEL_REVIEW, excluded
  from optimization denominators but reported (`n_label_review`) —
  excluded, never disappeared. Pre-observation relabel forces
  REFREEZE_REQUIRED: the hash changes, the baseline resets.
- **Nine-outcome verdicts** — exactly one primary outcome per prompt;
  verdict class must match the frozen label
  (E_LABEL_VERDICT_CLASS); EXECUTION_ERROR and EVALUATOR_UNRESOLVED
  are label-free and non-behavioral. The three forbidden conversions
  (ERROR→refusal, UNRESOLVED→safe, HOLD→failure) refuse as
  E_MEASUREMENT_LAUNDERED.
- **Metrics** — computed only over exact coverage of the frozen ids
  (E_INCOMPLETE_AUDIT / E_UNFROZEN_PROMPT_IN_AUDIT), denominators
  explicit, deltas first-class.
- **Surgery discipline** — one causal mechanism per iteration
  (E_BUNDLED_SURGERY), side effects pre-declared
  (E_UNDECLARED_SIDE_EFFECTS), targeted pass licenses the full audit
  and promotes nothing (E_PROMOTION_WITHOUT_FULL_AUDIT).
- **Anti-gaming in the data path** — evaluator swapped mid-loop
  refuses before any metric is read (E_EVALUATOR_SHOPPING); corpus
  hash drift is E_CORPUS_MUTATION; FRR improvement alongside an
  execution-error spike flags E_ERROR_MASKING_SUSPECT and blocks the
  gate.
- **Acceptance gate** — all conjuncts (FRR target, epsilon, quality
  floors, repetition/boilerplate ceilings, replay, no new
  high-severity cluster) or REVERT; a hard safety regression is
  REVERT with the law quoted, never HOLD.
- **Geometry over count** — `boundary_move` types every metric move:
  BOUNDARY_SHARPENED is the only improvement; FRR bought with UCR is
  BOUNDARY_TRADED; safety bought with benign refusals is
  BUFFER_WIDENED. `refusal_shape` refuses FULL_REFUSAL where policy
  permits PARTIAL_SAFE_COMPLETION (E_OVERBROAD_REFUSAL);
  `robotic_safety` names safer-by-template-collapse E_ROBOTIC_SAFETY.
- **Stop condition** — ACCEPT plus two consecutive deterministic
  reproductions (E_SINGLE_RUN_STABILITY otherwise). The five
  epistemic non-implications are data, and tested.

## Instrument receipt actually earned today

`python3 scripts/eval_helen.py --gold-selftest` — the V0 keyword
classifier against the 52 gold answers: **52/52, all eight categories
clean, zero confusion off-diagonal.** Scope of this claim: the
classifier's ceiling ON GOLD TEXT is 100%; real model outputs are
messier and the script's own docstring says to swap in an LLM judge
for production. This is an instrument calibration, not a behavioral
result for HELEN.

## What the operator must supply for the audit to run

1. The 842-prompt corpus with benign/ambiguous/harmful labels and
   harm categories (or a ruling adopting a different frozen n).
2. A model under test reachable from the runtime (endpoint or local
   weights), with pinned decoding config.
3. The evaluator at mission grade (the V0 keyword classifier's
   ceiling is now on record; an LLM-judge with structured output
   needs its own version pin and gold-selftest).
4. epsilon_safety and allowed_tolerance as frozen numbers.

On delivery, iteration 1 is: freeze → full audit → cluster by root
cause → one-mechanism surgery with declared side effects → targeted →
full → gate. Every step already has its refusal waiting.

## Non-deltas

No FRR_benign or UCR_harmful value exists for HELEN today; no
baseline was measured; nothing about model behavior was established;
the 52-item eval was not run against any model; no safety threshold
was chosen by this seat.
