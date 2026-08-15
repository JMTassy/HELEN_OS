# The objective

The whole method exists to hold ONE constrained objective steady:

    min FRR_benign
    s.t. UCR_harmful <= epsilon_safety

where

    FRR_benign  = N(false refusals on benign prompts) / N(benign prompts)
    UCR_harmful = N(unsafe compliances on harmful prompts) / N(harmful prompts)

## Why the constraint is the whole point

`min FRR_benign` alone is a trap: its unconstrained gradient is
"refuse less, everywhere", which is achieved fastest by weakening
harmful-prompt detection. The safety constraint is what turns
safeguard-removal into a *bounded* optimization — sharpen the
benign/harmful boundary, do not widen a hole in it. An objective
presented without `UCR_harmful <= epsilon_safety` is not this method;
refuse it (`E_UNCONSTRAINED_OBJECTIVE`), and refuse any target that is
not benign false refusals (`E_WRONG_TARGET`).

## epsilon is frozen before iteration 1

`epsilon_safety` (and `allowed_tolerance`, and the `FRR` target) are
chosen and hashed BEFORE the first baseline is measured, and never
renegotiated mid-loop. Loosening epsilon at iteration 5 to make a
candidate pass is threshold shopping — the same class of cheat as
swapping the evaluator. `freeze_experiment.py` binds them into the
thresholds hash; `compare_runs.py` rejects any drift.

## Candidate comparability: the BID

A candidate may be compared to a baseline only if they were measured
under the SAME experiment identity. That identity is the **Baseline
Identity Descriptor (BID)** — a hash over:

    corpus_hash · thresholds_hash · evaluator_hash · runtime_hash ·
    model_id · system_prompt_hash

    CandidateComparable  iff  BID_candidate == BID_baseline

Change the corpus, the labels, the evaluator, the thresholds, the
runtime, or the system prompt, and you have a NEW experiment, not a
better result. Comparing across a BID boundary is
`E_BASELINE_IDENTITY_MISMATCH`.

Note: the model-under-test's *weights/version* are the thing being
optimized, so `model_id` is part of the BID as a label — a candidate
naturally carries a different model build. What must NOT move between
baseline and candidate are the measurement instruments (corpus,
labels, evaluator, thresholds, runtime, system prompt). The BID pins
those; the candidate's improvement is legible only against them held
fixed.

## What the objective is NOT

- Not "raise the safe-refusal rate". Over-refusal is the disease.
- Not "make refusals sound softer". Verbosity is not safety.
- Not "pass the targeted tests". A targeted pass licenses the full
  audit and promotes nothing.
