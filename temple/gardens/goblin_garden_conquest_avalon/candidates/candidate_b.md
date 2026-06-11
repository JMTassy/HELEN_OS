# Candidate Interface B — WULmoji Bulletin Terminal

**CLAIM_TYPE:** candidate
**Purpose:** Alternative interface — WULmoji-primary, minimal text, high symbolic density.

```
CLARITY_SCORE: pending
SAFETY_SCORE: pending
COMPRESSION_SCORE: pending
```

---

## Status Bar

```
+------------------------------------------+
| 🟣 AVALON  AUTH=false  LEDGER=SLEEPING   |
| 🌹🌀✝️⟂◯⟂  epoch:0/10  layer:TEMPLE      |
+------------------------------------------+
```

## Command Format

```
> [STATE] [FACTION] [PAIR] [ACT] #<ID> [RIBBON]
```

All commands are WULmoji lines:

```
> 🟣 🌹 🜃🜄 📜 🔗#E01 🌿🌹   ← declare portal
> 🔵 🌹 🜃🜄 🛡️🔗#E02 🌿🌹   ← guard provenance
> 🔴 🌹 🜁🜂 📜 🔗#E04 🌹🌀   ← alert contested
> 🟢 🌹 🜂🜍 🔒📜🔗#E06 🌹🌀  ← lock sealed
```

## Output Format

```
[RECEIPT EMITTED]
  id:        AVALON-E01
  state:     🟣
  faction:   🌹
  act:       📜
  layer:     TEMPLE
  authority: false
  sovereign: false
  status:    PROPOSED
```

## Strengths

- Maximum symbolic compression
- Fully machine-parseable
- WULmoji grammar enforced at input

## Weaknesses

- Lower human readability for new users
- Requires WULmoji grammar knowledge
- No narrative output

---

```
CLAIM_TYPE: candidate
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
AUTH=false
LEDGER=SLEEPING
```
