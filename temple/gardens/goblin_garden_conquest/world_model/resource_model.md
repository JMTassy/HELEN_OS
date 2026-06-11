# Resource Model

**CLAIM_TYPE:** world_model  
**Purpose:** Define the resources of DREAM_OF_CONQUEST. What accumulates. What depletes.

---

## Resource Types

```
RESOURCE_TABLE = {
  "KNOWLEDGE_UNITS":   "Accumulated from verified domain understanding",
  "CLAIM_TOKENS":      "Earned by producing receipted claims; spent to assert territory",
  "HEAP_SHARDS":       "Raw unverified material; abundant, low value, honest",
  "RECEIPT_CHAINS":    "Sequences of verified claims; compound interest on knowledge",
  "GATE_PASSES":       "Earned by passing local claim validation; required for territory",
  "GOBLIN_HOURS":      "Time spent in meditation / honest labeling; scarce, valuable"
}
```

## Accumulation Mechanics

| Action | Resource Gained |
|---|---|
| Produce receipted claim | +1 CLAIM_TOKEN |
| Pass claim validation | +1 GATE_PASS |
| Build receipt chain (3+) | +1 RECEIPT_CHAIN |
| Label heap material honestly | +2 HEAP_SHARDS |
| Complete a quest | +K KNOWLEDGE_UNITS (K = quest difficulty) |
| Meditate (honest labeling session) | +1 GOBLIN_HOUR |

## Depletion Mechanics

| Action | Resource Lost |
|---|---|
| Assert unreceipted claim as fact | -3 CLAIM_TOKENS |
| Fail claim validation | -1 GATE_PASS |
| Make sovereignty claim | BOUNDARY VIOLATION (all resources frozen) |

## Resource Constraints

Resources live in the dream world only. They have no sovereign value.  
KNOWLEDGE_UNITS cannot be converted to ledger entries.  
CLAIM_TOKENS cannot be redeemed for real write permissions.  
GOBLIN_HOURS cannot unlock kernel access.

The simulation is honest about this. The dream does not pretend to be the real world.

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
