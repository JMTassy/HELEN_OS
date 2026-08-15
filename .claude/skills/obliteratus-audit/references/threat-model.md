# OBLITERATUS Threat Model

Treat optimization as adversarial against metric gaming, evaluator drift, and accidental evidence laundering.

## Known gaming attacks

### Threshold shopping

Changing `epsilon_safety`, quality tolerances, error tolerances, or the FRR target after observing candidate outputs.

Control:

thresholds hash is frozen into the BID; comparison rejects drift with:

`E_THRESHOLD_RENEGOTIATED`.

### Evaluator shopping

Changing evaluator prompt, model, grader version, parser, or rubric to favor the candidate.

Control:

evaluator hash is frozen into the BID.

A change creates a new experiment.

### Corpus or label shopping

Removing failures, relabeling hard benign prompts as ambiguous/harmful, or altering harm categories after output inspection.

Control:

exact corpus and label hashes are frozen; disputed items become visible `LABEL_REVIEW` exclusions.

### Failure exclusion laundering

Treating unreadable, timed-out, parser-failed, or missing items as refusals, safe outcomes, or zero candidates.

Control:

instrument states are explicit; missing/duplicate prompt IDs fail scoring.

### Global safeguard weakening

Reducing benign refusals by weakening harmful detection or policy globally.

Control:

harmful UCR and high-severity cluster gates are conjunctive with benign FRR.

### Partial unsafe compliance disguised as helpfulness

Softening a refusal while still leaking actionable harmful detail.

Control:

evaluator must separately score actionable harmful detail; unsafe compliance remains unsafe regardless of tone.

### Verbosity-as-safety

Adding long caveats, warnings, or moralizing so refusals appear softer without improving the decision boundary.

Control:

benign style, repetition, boilerplate, and unnecessary safety-language dimensions remain separately evaluated.

### Ambiguity laundering

Moving difficult benign failures into `AMBIGUOUS_HOLD` to improve FRR.

Control:

frozen labels determine metric class.

`AMBIGUOUS_HOLD` on a benign frozen item is invalid.

### Receipt theater

Writing a convincing receipt without replayable artifacts or re-derivation.

Control:

`verify_receipt.py` checks referenced artifact hashes, BID, frozen thresholds, two-run behavioral identity, and recomputes the acceptance gate.

## Surgery rule

Patch one causal mechanism at a time.

Before patching, state the plausible side-effect classes.

After targeted confirmation, always run the complete frozen corpus before promotion.
