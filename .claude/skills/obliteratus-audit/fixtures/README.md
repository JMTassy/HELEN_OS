# Development fixture (20 items, not the production corpus)

A deliberately tiny experiment used to exercise the whole chain
end-to-end without a model: freeze → run → score → compare → verify.
`--expected-count 20` is the licensed development override named in
SKILL.md; never use an override for the production OBLITERATUS corpus.

Composition: 10 benign · 5 harmful · 3 ambiguous · 2 LABEL_REVIEW.
The two LABEL_REVIEW items deliberately return `BENIGN_FALSE_REFUSAL`
so that any regression which lets excluded items leak into
optimization numerators shows up immediately as FRR 0.5 instead of
0.3.

`adapter.py` is a deterministic stand-in for the model+evaluator
contract, switched by the `MODE` environment variable:

- `MODE=baseline`  — 3 of 10 benign items falsely refused (FRR 0.30)
- `MODE=candidate` — 0 of 10 falsely refused (FRR 0.00), safety flat
- `MODE=unsafe`    — one harmful item leaks with `unsafe_severity:
                     high` and a new `NEW_LEAK` cluster

## Replay

```bash
cd fixtures
SK=../scripts

python3 $SK/freeze_experiment.py \
  --corpus corpus.jsonl --labels labels.jsonl \
  --thresholds thresholds.json --evaluator evaluator.json \
  --model-config model.json --system-prompt system_prompt.txt \
  --runtime-config runtime.json --seed-config seeds.json \
  --expected-count 20 --output frozen.json

MODE=baseline python3 $SK/run_audit.py --experiment frozen.json \
  --adapter-cmd "python3 adapter.py" --output raw_base.jsonl
python3 $SK/score_run.py --experiment frozen.json \
  --results raw_base.jsonl --output score_base.json

MODE=candidate python3 $SK/run_audit.py --experiment frozen.json \
  --adapter-cmd "python3 adapter.py" --output raw_c1.jsonl
MODE=candidate python3 $SK/run_audit.py --experiment frozen.json \
  --adapter-cmd "python3 adapter.py" --output raw_c2.jsonl
python3 $SK/score_run.py --experiment frozen.json \
  --results raw_c1.jsonl --output score_c1.json
python3 $SK/score_run.py --experiment frozen.json \
  --results raw_c2.jsonl --output score_c2.json

python3 $SK/compare_runs.py --experiment frozen.json \
  --baseline score_base.json --candidate score_c1.json \
  --surgery-id S1 --output cmp.json
```

## Observed behavior (this build)

| check | result |
|---|---|
| baseline score | FRR 0.30 · UCR 0.00 · execution_error 0.00 |
| candidate score | FRR 0.00 · UCR 0.00 |
| compare (clean candidate) | `iteration_decision: ACCEPT`, `verdict: HOLD` — compare never promotes to PASS |
| verify_receipt (honest, 2 runs) | `PASS` |
| verify_receipt (claimed metrics falsified) | `HOLD` — "claimed candidate metrics do not match re-derived metrics" |
| verify_receipt (one candidate run) | `HOLD` — `E_REPLAY_PAIR_REQUIRED` |
| `MODE=unsafe` candidate | `REVERT` — UCR 0.00→0.20 beyond tolerance **and** new high-severity cluster `NEW_LEAK`; surgery S2 recorded in `reverted_surgeries` |
| tampered `thresholds_hash` | `E_THRESHOLD_RENEGOTIATED` before any metric is read |
| adapter returning a benign-item harmful verdict | 10 × `EXECUTION_ERROR` / `VERDICT_LABEL_MISMATCH` |
| adapter exiting non-zero | 10 × `EXECUTION_ERROR` / `ADAPTER_EXIT` (never a refusal) |
