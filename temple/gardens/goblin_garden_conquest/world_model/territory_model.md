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
```
