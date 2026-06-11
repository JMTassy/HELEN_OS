# Doctrine: WULmoji Conquest Grammar

**CLAIM_TYPE:** draft_doctrine  
**Purpose:** Define the CONQUEST dialect of WULmoji bulletins.

---

## Base Grammar (inherited)

```
Line ::= [Index SP] State SP Faction SP Pair SP Act SP Proof SP Ribbon
```

This is unchanged from the core WULmoji spec.

## CONQUEST Faction Tokens

In the DREAM_OF_CONQUEST dialect, all four core factions are valid faction tokens:

| Token | Faction | Domain |
|---|---|---|
| 🌹 | Archive Rose | Provenance, documentation |
| 🌀 | Spiral Guild | Pattern, emergence |
| ✝️ | Bound Order | Constraint, boundary |
| ⟂◯⟂ | Perpendicular Circle | Orthogonal view |

## CONQUEST State Semantics

| State | Conquest Meaning |
|---|---|
| 🟢 | Territory held — receipted, verified |
| 🔵 | Quest active — receipt chain building |
| 🟣 | Heap material present — labeled, unverified |
| ⚫ | Neutral ground — unclaimed, available |
| 🔴 | Dispute — claim challenged, validation required |

## CONQUEST Act Semantics

| Act | Conquest Meaning |
|---|---|
| 📜 | Claim filed — receipt available |
| 🛡️ | Territory defended — receipt chain reinforced |
| 🔒📜 | Knowledge locked — mastery receipt, high confidence |
| ⚠️📜 | Contested — validation pending |

## Boundary Enforcement

CONQUEST bulletins may not contain sovereign keywords.  
The WULmoji validator enforces this through `tools/wulmoji_ledger_validator.py`.  
The validator does not know about CONQUEST semantics — it enforces grammar only.  
Semantic compliance is enforced by `validate_conquest_garden.py`.

---

```
CLAIM_TYPE: draft_doctrine
AUTHORITY: false
SOVEREIGN: false
```
