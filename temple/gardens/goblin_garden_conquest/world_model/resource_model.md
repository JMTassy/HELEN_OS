# Resource Model

**CLAIM_TYPE:** world_model  
**Purpose:** Define the resources of DREAM_OF_CONQUEST. What accumulates. What depletes.

---

## Resource Schemas (two layers, reconciled E026)

This model has two resource layers. Both are non-sovereign simulation resources only.

### Layer A — Island Economy (runner vocabulary)

```
ISLAND_RESOURCES = {
  "QUINT_CORE":    "Produced by HOME_KEEP_AVALON + ISLE_QUINT; primary action currency",
  "IGNIS_SHARD":   "Produced by ISLE_IGNIS; native claim cost for fire territory",
  "AQUA_SHARD":    "Produced by ISLE_AQUA; native claim cost for water territory",
  "AETHER_SHARD":  "Produced by ISLE_AETHER; native claim cost for air territory",
  "TERRA_SHARD":   "Produced by ISLE_TERRA; native claim cost for earth territory",
  "knowledge_fragment": "Output of EXPLORE action; 5 → K2P ritual → power_token"
}
```

Conversion: 3 any_shard at ISLE_QUINT → 1 QUINT_CORE

### Layer B — Epistemic Economy (proto-schema, phase 1)

```
EPISTEMIC_RESOURCES = {
  "KNOWLEDGE_UNITS":   "Accumulated from verified domain understanding",
  "CLAIM_TOKENS":      "Earned by producing receipted claims; spent to assert territory",
  "HEAP_SHARDS":       "Raw unverified material; abundant, low value, honest",
  "RECEIPT_CHAINS":    "Sequences of verified claims; compound interest on knowledge",
  "GATE_PASSES":       "Earned by passing local claim validation; required for territory",
  "GOBLIN_HOURS":      "Time spent in meditation / honest labeling; scarce, valuable"
}
```

Status: Layer B is the proto-genesis vocabulary. Layer A is the active runner vocabulary.
Both are valid simulation resources. They represent different abstraction levels of the same world.
Layer A = economic substrate. Layer B = epistemic layer above it.

## Accumulation Mechanics

| Action | Layer | Resource Gained |
|---|---|---|
| collect_phase fires (automatic, per turn) | A | +≤5 island resources → faction_wallet |
| EXPLORE ISLE_X (cost 1 QUINT_CORE) | A | +1 knowledge_fragment:X |
| 3 any_shard at ISLE_QUINT | A | +1 QUINT_CORE |
| 5 knowledge_fragment → K2P ritual | A | +1 power_token |
| Produce receipted claim | B | +1 CLAIM_TOKEN |
| Pass claim validation | B | +1 GATE_PASS |
| Build receipt chain (3+) | B | +1 RECEIPT_CHAIN |
| Label heap material honestly | B | +2 HEAP_SHARDS |
| Complete a quest | B | +K KNOWLEDGE_UNITS (K = quest difficulty) |
| Meditate (honest labeling session) | B | +1 GOBLIN_HOUR |

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
