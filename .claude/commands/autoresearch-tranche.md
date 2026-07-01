# HELEN Autoresearch Tranche

Execute a bounded PULL-mode autoresearch tranche: one hypothesis per epoch, observable signals only.

## Inputs

$ARGUMENTS — frontier and tranche size. Example: "drift 5", "closure 3", "legoracle 1". Default: operator picks frontier, size=5.

## Recipe

### Pre-flight

1. Check current autoresearch state:
   - Read `GOVERNANCE/TRANCHE_RECEIPTS/` for the latest sealed tranche
   - Verify the previous tranche is sealed before opening a new one
   - If unsealed tranche exists: HALT and report

2. Identify the frontier from $ARGUMENTS or the MAYOR re-rank queue

### Per Epoch (sequential, one at a time)

1. **Hypothesis**: State a single falsifiable claim about observable behavior
   - Must target non-sovereign layers only (kernel, memory, identity, ledger, replay are NOT mutation targets)
   - Must be testable with existing tooling or a small new test

2. **Experiment**: Design and execute the test
   - Bounded: max 30 file reads, max 1 new test file
   - Deterministic: no wall-clock, no random, sorted outputs

3. **Observation**: Record what happened (not what you expected)
   - Metric: quantitative where possible
   - Failure mode: what would falsify this?

4. **Verdict**: KEEP / REJECT / INCONCLUSIVE
   - KEEP: hypothesis survived the test, artifact produced
   - REJECT: hypothesis falsified, counterexample recorded
   - INCONCLUSIVE: test was insufficient, state what's missing

5. **Receipt**: 7-field tranche sub-receipt:
   ```yaml
   carry_forward_state: ...
   hypothesis: ...
   experiment: ...
   metric: ...
   failure_mode: ...
   keep_reject_rule: ...
   upgrade_path: ...
   ```

### Tranche Seal

After all epochs: write `TRANCHE_SUB_RECEIPT_V1` to `GOVERNANCE/TRANCHE_RECEIPTS/`. Seal before any new tranche opens.

## Constraints

- PULL-mode: one hypothesis per epoch, halt between tranches
- Non-sovereign layers only
- Observable signals only — no speculative ideas
- Bounded: max epochs per tranche = $size argument (default 5)
- No open-ended pauses: SHIP or ABORT only

## Loop Engineering (Fable)

```
while frontier.has_open_hypotheses():
    tranche = autoresearch_tranche(frontier, size=5)
    seal(tranche)
    mayor_rerank(frontier)  # reprioritize based on findings
    if tranche.all_inconclusive:
        break  # halt discipline
```
Each sealed tranche feeds the next MAYOR re-rank. Fable never opens two tranches simultaneously.
