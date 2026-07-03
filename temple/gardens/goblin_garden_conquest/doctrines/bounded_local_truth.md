---
schema: GARDEN_DOCTRINE_V0
title: Bounded Local Truth — Application in CONQUEST Simulation
authority: false
sovereign: false
canon: false
ledger_effect: none
origin: BOUNDED_RECEIPT_DOCTRINE_V0 → CONQUEST application
captured: 2026-06-21
---

# Bounded Local Truth — CONQUEST Application

**CLAIM_TYPE: draft_doctrine**

🔵 OBSERVED · NON_SOVEREIGN · GARDEN_ONLY · NO_CLAIM

Child doctrine of `../BOUNDED_RECEIPT_DOCTRINE_V0.md`.

---

## The Core Insight Applied to CONQUEST

CONQUEST is a governed world model living entirely in TEMPLE. It has its own:
- Territories (held or contested)
- Factions (Archive Rose / Spiral Guild / Bound Order / Perpendicular Circle)
- Quests (active / sealed / failed)
- Power (accumulated, lost, traded)

All of it is `SIMULATION · NON_SOVEREIGN · AUTHORITY=false`.

But within that simulation — **it is real**.

When the Spiral Guild holds the Meridian Crossing, that is a fact. Not a claim pending
global admission. A locally permanent fact, receipted within the CONQUEST scope, visible
to all players inside the simulation, invisible to the sovereign ledger (which was never
meant to record it).

The BOUNDED RECEIPT doctrine gives this a name:

```
CONQUEST_FACT(x) = BOUNDED_RECEIPT(x, scope="CONQUEST_SIMULATION")

authority:       false  (sovereign sense)
local_authority: true   (within simulation)
ledger_route:    FORBIDDEN
```

---

## What This Changes for CONQUEST

**Before:** CONQUEST events were implicitly "just fiction" — no governance category,
no receipt form, no way to distinguish a locally-true simulation fact from a failed
claim or a temporary dream.

**After:** CONQUEST facts can be BOUNDED — locally receipted, locally permanent,
zero sovereign effect.

```
CONQUEST event types:

QUEST_OPENED    → BOUNDED(quest_id, scope=CONQUEST)
TERRITORY_HELD  → BOUNDED(territory+faction, scope=CONQUEST)
FACTION_PACT    → BOUNDED(pact_terms, scope=CONQUEST)
EPOCH_CLOSED    → BOUNDED(epoch_receipt, scope=CONQUEST)
```

None of these enter the sovereign ledger. All of them are real within the world.

---

## The Goblin's Read

```
GOBLIN says:

"A conquered territory is locally true.
 It does not need the ledger to remember it.
 The map remembers it.
 The faction remembers it.
 The simulation receipts it.

 If the territory falls, COMPOST captures the fall.
 If the territory holds, BOUNDED seals the holding.

 Neither requires REDUCER.
 Neither seeks MAYOR.

 The game is the scope.
 The scope is enough."
```

---

## Membrane Law (CONQUEST-specific)

```
CONQUEST_FACT ⊬ HELEN_CANON
CONQUEST_RECEIPT ⊬ LEDGER_ENTRY
SIMULATION_AUTHORITY ⊬ SOVEREIGN_AUTHORITY
WORLD_MEMORY ⊬ SPINE_MEMORY
```

CONQUEST has its own memory. The spine has its own memory. They do not need to be the
same memory to both be real in their respective scopes.

---

## Status

```
authority:     false
sovereign:     false
canon:         false
ledger_effect: none
claim_status:  NO_CLAIM
final:         HOLD_FOR_OPERATOR
git_stage:     no
```

🔵 OBSERVED in the garden. 🌀 Real within the simulation. 👁️ Invisible to the ledger.
