# Non-Sovereign World State

**CLAIM_TYPE:** world_model  
**Purpose:** Define the structure of world state in DREAM_OF_CONQUEST. Entirely non-sovereign.

---

## World State Schema (simulation only)

```
DREAM_STATE_V0 = {
  "world": "DREAM_OF_CONQUEST",
  "sovereign": false,
  "authority": false,
  "simulation_only": true,

  "factions": [],          # list of active factions
  "territories": {},       # territory_id -> faction_id | "neutral"
  "resources": {},         # resource_type -> quantity (simulation units)
  "quests": [],            # active quests
  "player_agents": [],     # non-sovereign agents navigating the world

  "claim_log": [],         # local Temple receipt chain (NOT sovereign ledger)
  "last_epoch": 0,

  "forbidden": [
    "ledger-writes",
    "kernel-mutations",
    "schema-changes",
    "canon-promotion",
    "write-gate-approval"
  ]
}
```

## World State Rules

1. World state lives only in Temple. It does not persist to sovereign layers.
2. Every state change requires a local receipt (`DREAM_RECEIPT_V0`).
3. No sovereign keys (the hash-chain fields, seq, and hash-payload fields) may appear in world state.
4. Status of any world-state element: `simulation` — never `CANON`, `ADMITTED`, `SOVEREIGN`.
5. The `claim_log` is a local Temple receipt chain — structurally similar to sovereign receipt chains but carrying no constitutional weight.

## What Can Change

Factions may rise and fall. Territories may shift.  
Resources may accumulate or deplete. Quests may open and close.  
Agents may gain knowledge and convert it to territory.

None of this touches HELEN's kernel. None of this writes to the ledger.  
The dream is bounded. The boundary holds.

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
