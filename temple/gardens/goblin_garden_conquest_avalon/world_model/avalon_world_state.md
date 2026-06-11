# Avalon World State

**CLAIM_TYPE:** world_model
**Purpose:** Define the non-sovereign world state schema for GARDEN_CONQUEST_AVALON.

---

## World State Schema (simulation only)

```
AVALON_STATE_V0 = {
  "world": "DREAM_OF_CONQUEST/AVALON",
  "sovereign": false,
  "authority": false,
  "simulation_only": true,
  "layer": "TEMPLE",

  "cli_version": "CONQUESTLAND_V0.2",
  "cwl_version": "v0.2.1",

  "factions": ["🌹", "🌀", "✝️", "⟂◯⟂"],
  "territories": {},
  "resources": {},
  "quests": [],
  "player_agents": [],

  "claim_log": [],
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

## CONQUESTLAND State Loop

```
conquest enter
  → conquest order "<text>"
    → conquest seal
      → conquest leave (world continues)
        → [24h]
          → conquest return
```

Each sealed order is irreversible. No edit. No undo.

## WULmoji State Codes

| State | Meaning |
|---|---|
| 🟣 | INITIATING — portal opening |
| 🔵 | STABLE — in progress |
| 🟢 | COMPLETE — sealed |
| 🔴 | ALERT — contested |
| ⚫ | LOCKED — blackout |

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
