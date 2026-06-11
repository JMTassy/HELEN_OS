# Temple Autoresearch — Rollback Law

**CLAIM_TYPE:** simulation  
**Purpose:** What happens when an epoch fails. The rollback discipline.

---

## The Law

If an epoch produces a failed evaluation:

1. The epoch receipt is written with `gate_result: FAIL` and `failure_mode` populated
2. The carry-forward state is NOT updated (failed epoch does not propagate its conclusions)
3. The hypothesis is moved to `closed_hypotheses` with status `REJECTED`
4. The next epoch opens with the pre-failure carry-forward state
5. The failure is visible in the experiment log — never hidden

## What Rollback Is NOT

Rollback is not deletion. The failed artifact remains.  
The failed receipt remains. The failure_mode remains.  
Rollback is about carry-forward state — failed conclusions do not propagate.

```
ROLLBACK(epoch_N):
  carry_forward = carry_forward BEFORE epoch_N
  closed_hypotheses.append(epoch_N.hypothesis, status=REJECTED, reason=epoch_N.failure_mode)
  experiment_log[epoch_N].keep_reject = "REJECT"
  # artifact from epoch_N stays in the garden — honest record
```

## Why Rollback Is Sacred

Without rollback, one bad epoch can corrupt all subsequent carry-forward state.  
The corruption accumulates silently — each epoch builds on wrong conclusions.

Rollback breaks the corruption chain. Each epoch stands on verified prior state only.  
This is the Temple version of the sovereign invariant: **NO RECEIPT = NO CLAIM**.  
In autoresearch: **NO KEEP = NO CARRY-FORWARD**.

## Rollback Limit

If 3 consecutive epochs fail, the simulation enters HALT state:
- No new epochs open
- A HALT receipt is written
- The operator decides whether to continue or seal the garden

The garden does not loop forever on failure. The garden halts honestly.

---

```
CLAIM_TYPE: simulation
AUTHORITY: false
SOVEREIGN: false
```
