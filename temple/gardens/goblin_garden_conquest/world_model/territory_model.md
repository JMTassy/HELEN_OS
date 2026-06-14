# Territory Model

**CLAIM_TYPE:** world_model  
**Purpose:** Define the territory map of DREAM_OF_CONQUEST.

---

```
                    DREAM MAP (SEED STATE)

         [ THE HEAP ]          [ NEUTRAL GROUND ]
              ↓                        ↓
    ┌──────────────────────────────────────────┐
    │  PROVENANCE REACHES  🌹    PATTERN WASTES 🌀  │
    │  (Archive Rose territory)  (Spiral Guild)   │
    ├──────────────────────────────────────────┤
    │      THE BOUNDARY KEEPS ✝️               │
    │      (Bound Order holds the edges)        │
    ├──────────────────────────────────────────┤
    │   THE PERPENDICULAR FIELDS ⟂◯⟂           │
    │   (orthogonal — seen from outside)        │
    └──────────────────────────────────────────┘
         ↓
    [ THE DREAM CORE ] — unclaimed, maximum knowledge density
    [ THE HEAP WILDS ] — unverified, always neutral, always honest
```

---

## Territory Rules

1. **Neutral ground** is unclaimed. Any faction may enter; claiming requires a GATE_PASS.
2. **Faction territory** is held by receipt chain. Challenge requires better receipts.
3. **THE HEAP WILDS** are never claimable. They are the honest unverified commons.
4. **THE DREAM CORE** is the highest-value territory — holds only after mastery receipt chain.
5. Territory maps are simulation state only. They do not correspond to HELEN's real architecture.

## Action Registry (E026)

| Action | Cost | Output | Territory Mutation | Receipt |
|---|---|---|---|---|
| COLLECT_PHASE | automatic (per turn) | QUINT_CORE → faction_wallet (cap 5/turn) | none | none |
| EXPLORE | 1 QUINT_CORE | knowledge_fragment:{island} | none | EXPLORE_RECEIPT_V0 |
| CLAIM_LIGHT | 1 QUINT_CORE | island assigned to faction | yes | CLAIM_RECEIPT_V0 |
| CLAIM | native element shard | island assigned to faction | yes | CLAIM_RECEIPT_V0 |
| CONQUEST | 3 QUINT_CORE | forced island takeover | yes | CONQUEST_RECEIPT_V0 |

### collect_phase — automatic tick (NOT a player action)

```
collect_phase fires once per turn tick, automatically.
It is NOT triggered by a player action.
It is NOT optional.

flow: island_production → island_stockpile → collect_phase → faction_wallet
cap:  5 units per turn
```

All factions hold HOME_KEEP_AVALON (inalienable). HOME_KEEP_AVALON produces QUINT_CORE.
At T=1, each faction has ≥1 QUINT_CORE in wallet from the automatic collect_phase.
EXPLORE is therefore available at T=1 without any prior CLAIM.

### Bootstrap path (confirmed, E026)

```
T=0  HOME_KEEP_AVALON held (inalienable, all factions)
T=1  collect_phase fires → QUINT_CORE in faction_wallet
     EXPLORE ISLE_X (cost 1 QUINT_CORE) → knowledge_fragment:X
     × 5 fragments → K2P ritual → power_token
     CLAIM_LIGHT (cost 1 QUINT_CORE) → island claimed
```

No SCOUT / EXPLORE_LIGHT needed. The bootstrap is already in the design.

## Claiming Territory

```
CLAIM_TERRITORY(faction, zone, receipt_chain):
  IF receipt_chain.length >= 3 AND all_verified:
    IF zone == "neutral": ASSIGN zone → faction
    IF zone == faction_territory: REINFORCE
    IF zone == other_faction_territory: DISPUTE
      → resolved by CLAIM_VALIDATION_RITUAL (epoch 009)
  ELSE:
    CLAIM FAILS — insufficient receipt chain
```

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
UPDATED: E026 — action registry + collect_phase documentation added
```
