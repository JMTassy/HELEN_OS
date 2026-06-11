# WULmoji Ledger Spec v0.2

**Status:** NON_SOVEREIGN | NOT the HELEN sovereign ledger | authority=false  
**Scope:** CONQUEST WhatsApp bulletin / skin / parser format for human-readable CONQUEST updates.  
**Do not merge** with `town/ledger_v1.ndjson` or any HELEN trust ledger.

---

## Grammar

```
Line ::= [Index SP] State SP Faction SP Pair SP Act SP Proof SP Ribbon
```

### Arity

| Tokens | Form |
|---|---|
| 6 | State Faction Pair Act Proof Ribbon |
| 7 | Index State Faction Pair Act Proof Ribbon |

Separator: single ASCII space (U+0020) between every token. No leading/trailing spaces.

### Index (optional)

`(N)` where N is a non-negative integer. Example: `(0)`, `(7)`.

### State

One of:

| Glyph | Meaning |
|---|---|
| 🔵 | Pending |
| 🟢 | Pass |
| 🟣 | Oracle |
| ⚫ | Alert |
| 🔴 | Block |

### Faction

One of: `⟂◯⟂` `🌹` `🌀` `✝️`

### Pair

Exactly **2 Unicode grapheme clusters**.  
`⚠️` (U+26A0) is **forbidden** in Pair.

### Act

One of:

| Token | Meaning |
|---|---|
| `📜` | Decree |
| `🛡️` | Guard |
| `🔒📜` | Sealed decree |
| `⚠️📜` | Warning decree |

### Proof

Format: `🔗#ID`  
- Must start with `🔗#` (link emoji + hash). `🔒#` is a proof confusion error.  
- `⚠️` forbidden in ProofID.

**Default mode:** `ID` matches `[A-Z0-9_\-]+`  
**StrictProof mode (`--strict-proof`):** `ID` matches `[0-9A-F]{4}` (exactly 4 uppercase hex digits)

### Ribbon

Exactly **2 Unicode grapheme clusters**.  
`⚠️` forbidden in Ribbon **unless** Act == `⚠️📜`.

---

## Constraint: ⚠️ scope

```
⚠️ in Act     → only valid as part of "⚠️📜" token
⚠️ in Pair    → ALWAYS forbidden
⚠️ in ProofID → ALWAYS forbidden
⚠️ in Ribbon  → forbidden UNLESS Act == ⚠️📜
```

---

## AlchemyStrict mode (`--alchemy-strict`)

When **both** grapheme clusters of Pair are alchemy glyphs, the transition must be valid:

| Glyph | Symbol |
|---|---|
| 🜃 | Earth |
| 🜄 | Water |
| 🜁 | Air |
| 🜂 | Fire |
| 🜍 | Salt |

**Allowed adjacent transitions (forward only):**

```
🜃 → 🜄 → 🜁 → 🜂 → 🜍
```

Reverse transitions, skipped transitions, and non-adjacent pairs are rejected.  
If either cluster is not an alchemy glyph, the transition check is skipped.

---

## Examples

### Valid (default mode)

```
(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜
(1) 🔵 ⟂◯⟂ 🜃⚗️ 📜 🔗#GATE ✨🜍
(2) 🟢 ⟂◯⟂ 🜃🏰 🛡️ 🔗#WALL 🏰📜
(7) ⚫ 🌀 🜁🜄 ⚠️📜 🔗#INJ1 ⚠️🌀
(9) 🔴 ✝️ 🜂🜍 🔒📜 🔗#VETO 🔒⚰️
```

### Valid (strict proof + alchemy-strict)

```
(1) 🔵 ⟂◯⟂ 🜄🜁 📜 🔗#A1B2 ✨🜍
(2) 🟢 ⟂◯⟂ 🜁🜂 🛡️ 🔗#C3D4 🏰📜
(3) ⚫ 🌀 🜂🜍 🔒📜 🔗#E5F6 🔒⚰️
```

### Invalid

```
🔵 ⟂◯⟂ 🜄⚠️ 📜 🔗#A1B2 ✨🜍          ← ⚠️ in Pair
🔵 ⟂◯⟂ 🜃🏰 📜 #A1B2 🏰📜             ← Proof missing 🔗
🔵 ⟂◯⟂ 🜃🏰 ⚔️ 🔗#A1B2 🏰📜           ← Invalid Act
🔵 ⟂◯⟂ 🜃🏰 📜 🔗#A1B2 🏰📜✨          ← Ribbon has 3 grapheme clusters
🔵 ⟂◯⟂ 🜃🜂 📜 🔗#A1B2 ✨🜍            ← invalid ONLY with --alchemy-strict
```

---

## CLI

```bash
python tools/wulmoji_ledger_validator.py bulletin.txt
python tools/wulmoji_ledger_validator.py bulletin.txt --strict-proof
python tools/wulmoji_ledger_validator.py bulletin.txt --alchemy-strict
python tools/wulmoji_ledger_validator.py bulletin.txt --json
```

Exit code: `0` = all lines pass, `1` = any line fails.

---

```
NOT HELEN SOVEREIGN LEDGER
NOT CANON ADMISSION
authority=false
```
