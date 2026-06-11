# Temple Autoresearch — Experiment Memory

**CLAIM_TYPE:** simulation  
**Purpose:** How the simulation tracks experiments. The local non-sovereign experiment log.

---

## Experiment Log Schema

```
EXPERIMENT_LOG_V0 = {
  "log_type": "TEMPLE_AUTORESEARCH_LOG",
  "authority": false,
  "sovereign": false,
  "entries": [
    {
      "epoch": N,
      "hypothesis": "...",
      "experiment": "...",
      "metric": "...",
      "failure_mode": "...",
      "keep_reject": "KEEP|REJECT",
      "upgrade_path": "...",
      "receipt_id": "epoch_XXX"
    }
  ]
}
```

## Carry-Forward State

The autoresearch simulation maintains carry-forward state across epochs.  
An epoch may reference the conclusion of prior epochs.  
The carry-forward state is:

```
CARRY_FORWARD = {
  "best_quest_ordering": "UNKNOWN",  # starts unknown
  "best_map_layout": "UNKNOWN",
  "best_bulletin_format": "UNKNOWN",
  "world_model_errors": 0,
  "epochs_completed": 0,
  "open_hypotheses": [],
  "closed_hypotheses": []
}
```

## Memory Rules

1. Experiment memory is local to this garden. It does not write to HELEN memory.
2. Every entry must have a receipt.
3. Rejected hypotheses are not deleted — they are labeled REJECTED with a reason.
4. A REJECTED hypothesis in memory is more valuable than a missing hypothesis.
   (The heap of rejected ideas is honest. Empty history is a lie.)
5. Carry-forward state is updated only after KEEP verdict.

## Halt Discipline

Each epoch seals before the next opens.  
No epoch may reference a future epoch's conclusions.  
The simulation respects causality even in the dream world.

---

```
CLAIM_TYPE: simulation
AUTHORITY: false
SOVEREIGN: false
```
