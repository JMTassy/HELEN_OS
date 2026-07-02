# HELEN Verifier Sub-Agent

Independent verification of any artifact. The maker never grades itself — this is the K2 anti-violation (proposer ≠ validator) and the Fable-5 verifier-sub-agent pattern in one.

## Inputs

$ARGUMENTS — the artifact to verify. A file path, a claim, a diff, a screenshot, a test result, or a receipt.

## Why this exists

A model evaluating its own output sees its own reasoning trail and prefers conclusions consistent with what it already wrote. A separate context sees only the artifact and the rubric — no skin in the maker's game. Anthropic measured this (Parameter Golf): Fable-5 with an independent verifier explored larger hypothesis spaces and recovered from negative intermediate results. HELEN has always known it: **proposer ≠ validator** (K2, Rule 3).

## Recipe

### Step 1: Receive ONLY the artifact and the rubric
- Do NOT read the maker's reasoning, chat history, or intent narrative.
- Read only: the artifact itself, the stated success criteria, and the relevant doctrine (CLAUDE.md rules, schema, gate spec).

### Step 2: Build the rubric (if not supplied)
Derive gradable criteria from the artifact's type:
- **Code**: does it run? do tests pass? does it match the API contract? any crash/security/determinism defect?
- **Receipt**: is it honest? does the proof hash match? are all required fields present? does `authority`/`claim_status` match the artifact's actual lifecycle?
- **Claim**: is it falsifiable? is there a counterexample? does it overstate scope?
- **Diff**: does it touch anything off-limits (sovereign firewall)? does it do what it says and nothing more?
- **Screenshot/UI**: does it match the goal + design tokens + the previous state?

### Step 3: Adversarial pass
Default to REFUTED. Try to break the artifact:
- For code: find the input that crashes it.
- For a claim: find the counterexample that falsifies it.
- For a receipt: find the field that's dishonest or the hash that doesn't reproduce.
- For a crossing: find the `authority=true` leak or the ungated promotion.

### Step 4: Verdict
```yaml
verdict: CONFIRMED | CONFIRMED_WITH_CORRECTION | REFUTED
artifact: <path or description>
rubric_checked: [<criterion>, ...]
survived: [<criterion that held>, ...]
failed: [<criterion that broke>, ...]
counterexample: <concrete input/state → wrong output, or null>
correction_required: [<repair>, ...]
```

### Step 5: Write the lesson (stage 4 distillation)
If the verification found a real defect, write the lesson into `.claude/STATE.md` (Open failures or Lessons learned) AND into the skill that produced the artifact. The skill gets sharper every time.

## Constraints

- The verifier must be a fresh context — never the maker.
- Re-verify against fresh metal (re-read the actual files), do not trust prior reports.
- Prefer local model (gemma4:e2b, the HAL reviewer default) — escalate to Sonnet 5 only if the verdict is INCONCLUSIVE.
- Vision artifacts (UI, charts, screenshots) require Fable-tier vision — text-only verifiers miss the failure mode that matters.
- A REFUTED verdict HALTS the pipeline. Do not proceed past a failed gate.

## Loop Engineering (Fable)

Adversarial verification per task — the canonical pattern:
```
for artifact in maker_outputs:
    verdict = verify(artifact)          # independent context
    if verdict == REFUTED:
        halt(); report(counterexample)
    elif verdict == CONFIRMED_WITH_CORRECTION:
        distill_lesson(verdict.correction_required)  # → STATE.md + skill
```
Pair with perspective-diverse verifiers for artifacts that can fail multiple ways: spawn N verifiers each with a distinct lens (correctness / security / determinism / does-it-reproduce). Kill if majority refute.
