# GOBLIN GARDEN — AUTO EVALUATION

```
CLAIM_TYPE     = simulation
LAYER          = TEMPLE
AUTHORITY      = false
SOVEREIGN      = false
CANON          = false
STATE_MUTATION = none
STATUS         = PROPOSED
TOPIC          = auto_evaluation_of_wul_claims
EPOCH_COUNT    = 5 (bounded, sealed)
```

---

## Threshold Law

The goblin stands at the membrane.
Every claim that arrives gets a structural check.
The check is fast.
The check is not enough.

Auto-evaluation can enforce form.
Only the reducer can enforce meaning.

```
AUTO_EVAL ⊂ STRUCTURAL_GATE
REDUCER   ⊂ SEMANTIC_GATE
AUTO_EVAL ⊬ REDUCTION
```

Ledger does not move.

---

## Research Question

**What is automatable in WUL claim evaluation, and where does the human reducer become mandatory?**

Scope: `wul_claim_schema_v0.json` + `CHRONOS_WUL_BRIDGE_SPEC_V1.md` + membrane law.

---

## Simulation Rules

```
AUTORESEARCH_SIMULATION_RULES = {
  "hypothesis_per_epoch": 1,
  "observable_signals_only": true,
  "kernel_mutation": false,
  "ledger_mutation": false,
  "memory_mutation": false,
  "halt_discipline": true,
  "receipt_required": true,
  "proposer_ne_validator": true,
  "authority": false,
  "sovereign": false
}
```

Candidates in scope (allowed):
- Schema structural validation automatable or not
- Evidence presence as admissibility proxy
- `kernel_admissible` computability from schema fields
- GOBLIN membrane as computable filter function
- Auto-eval ceiling vs. reducer ceiling

Out of scope (forbidden):
- Mutating kernel, ledger, memory, schemas
- Claiming reducer authority
- Promoting any epoch output to canon
