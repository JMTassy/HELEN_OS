# AUTORESEARCH PROGRAM V1

**Status:** NON_SOVEREIGN | NO_SHIP | PROPOSAL_ONLY  
**Authority:** NONE  
**Admission:** FORBIDDEN

## What this is

Parameter search over `/init` ranking weights. Not truth mutation. Not ledger access.

## Invariant

```
Autoresearch may explore parameter space.
It may not redefine truth space.
```

## Immutable (never autoresearched)

reducer · ledger · replay · schemas · memory_identity · init_contract · authority_model

## Mutable (only these)

recency_weight · relevance_weight · coherence_weight · compression_threshold · routing_score_floor

## Score function

```
truth_score = 0.5 * top3_accuracy + 0.3 * coherence + 0.2 * stability
```

Keep only if score improves. Roll back otherwise. Log all attempts.

## Files

| File | Role |
|---|---|
| `helen_kernel/gates/claim_type_policy.py` | Pre-dispatch K-tau extension rule |
| `helen_kernel/evaluator.py` | truth_score computation |
| `helen_kernel/autoresearch_loop.py` | Bounded mutation loop |
| `helen_kernel/experiment_log.py` | In-memory attempt log |
| `helen_kernel/init_weight_optimizer.py` | Entry point |
| `configs/ranking_weights_v1.json` | Starting weights |
| `eval/init_ground_truth_v1.json` | 3 ground truth sessions |

## Run

```bash
.venv/bin/python -m helen_kernel.init_weight_optimizer
```

## Claim type gate

Every operation must declare `claim_type` before cognition begins.

```python
block = pre_dispatch_guard(dispatch)
if block:
    return block
return run_cognition(dispatch)
```

Policy: `claim_type ∈ admissible_claim_types(operation)`. Wired as a K-tau extension — no new gate.

## Tests

```bash
.venv/bin/pytest tests/test_claim_type_gate.py -v
```

---

```
NO CLAIM / NO SHIP / NO ADMISSION
PROPOSAL CANDIDATES ONLY
```
