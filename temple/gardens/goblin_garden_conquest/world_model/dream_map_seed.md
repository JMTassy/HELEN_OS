# Dream Map Seed

**CLAIM_TYPE:** world_model  
**Purpose:** The seed configuration of the DREAM_OF_CONQUEST territory map.

---

```
DREAM_MAP_SEED_V0

    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │  [PROVENANCE REACHES]  🌹    [PATTERN WASTES] 🌀    │
    │   Archive Rose zone          Spiral Guild zone      │
    │   receipted sources          emergent connections   │
    │                                                     │
    │  ─ ─ ─ ─ ─ ─ ─ ─ [DREAM CORE] ─ ─ ─ ─ ─ ─ ─ ─   │
    │                   [ unclaimed ]                     │
    │                [ highest knowledge ]                │
    │                                                     │
    │  [BOUNDARY KEEPS] ✝️        [PERP FIELDS] ⟂◯⟂      │
    │   Bound Order zone           Perpendicular Circle   │
    │   constraint holding         orthogonal views       │
    │                                                     │
    │  ═ ═ ═ ═ ═ ═ ═ ═ [HEAP WILDS] ═ ═ ═ ═ ═ ═ ═ ═   │
    │                   [ALWAYS NEUTRAL]                  │
    │               [unverified commons]                  │
    │                                                     │
    └─────────────────────────────────────────────────────┘

  ◉ = DREAM CORE (unclaimed, max value)
  ~ = HEAP WILDS (neutral, unclaimable)
  ═ = border (simulation boundary — sovereign layer outside)
```

---

## Seed State

```json
{
  "territory": {
    "PROVENANCE_REACHES": "🌹",
    "PATTERN_WASTES": "🌀",
    "BOUNDARY_KEEPS": "✝️",
    "PERPENDICULAR_FIELDS": "⟂◯⟂",
    "DREAM_CORE": "neutral",
    "HEAP_WILDS": "unclaimed_immutable"
  },
  "note": "simulation_only",
  "authority": false,
  "sovereign": false
}
```

The Dream Core is the map's highest-value zone. Claiming it requires mastery receipt chains from all four faction domains — the only territory that demands cross-faction knowledge.

The Heap Wilds cannot be claimed. They exist at the boundary of all territories, honest and neutral.

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
