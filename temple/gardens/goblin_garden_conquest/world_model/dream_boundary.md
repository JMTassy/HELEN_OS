# DREAM_OF_CONQUEST — World Boundary

**CLAIM_TYPE:** world_model  
**Purpose:** Define what the dream world is, what it contains, and where it stops.

---

```
    ┌──────────────────────────────────────────────┐
    │              HELEN OS (SOVEREIGN)             │
    │   kernel / ledger / schemas / governance      │
    │                                               │
    │   ┌──────────────────────────────────────┐   │
    │   │        TEMPLE LAYER (NON-SOVEREIGN)   │   │
    │   │                                       │   │
    │   │  ┌────────────────────────────────┐   │   │
    │   │  │   DREAM_OF_CONQUEST (TEMPLE)   │   │   │
    │   │  │                                │   │   │
    │   │  │  knowledge → power             │   │   │
    │   │  │  factions / territories        │   │   │
    │   │  │  quests / resources            │   │   │
    │   │  │  strategy / simulation         │   │   │
    │   │  │                                │   │   │
    │   │  │  [ SIMULATION ONLY ]           │   │   │
    │   │  │  [ NOT CANON ]                 │   │   │
    │   │  │  [ NO LEDGER WRITES ]          │   │   │
    │   │  └────────────────────────────────┘   │   │
    │   └──────────────────────────────────────┘   │
    └──────────────────────────────────────────────┘
```

---

## Boundary Rules

**Inside the boundary:** all simulation, modeling, generation of world-state, quest logic, faction dynamics, resource allocation, territory maps.

**Outside the boundary (forbidden):**
- Ledger writes
- Kernel mutations
- Schema changes
- Canon promotion
- Reducer calls
- Write-gate approval
- Skill mutations
- Test file edits
- Model training

## What the Dream World IS

A Temple-side simulation of a conquest-and-knowledge world.  
The game mechanic: *knowledge converts to power* — the better you understand a domain, the more territory you can claim in the simulation.

This is edutainment architecture. The world rewards learning.  
The goblin is your guide. The ledger is not in the dream.

## What the Dream World IS NOT

A real HELEN module. A sovereign layer. A source of canon.  
A ledger gate. A deployment target. A kernel component.

The boundary is the architecture. You cannot think your way out of it.

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
