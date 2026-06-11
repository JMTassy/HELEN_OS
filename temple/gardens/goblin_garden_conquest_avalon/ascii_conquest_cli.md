# ASCII CONQUEST CLI — AVALON INTERFACE SPEC

```
CLAIM_TYPE: cli
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```

---

## Status Bar (always visible)

```
+==================================================+
| 🜏 AVALON // DREAM_OF_CONQUEST // CLI_GATE        |
| AUTH=false | SOV=false | CANON=no | LEDGER=SLEEPING |
+==================================================+
```

**Hard constants:**

| Field | Value | Meaning |
|---|---|---|
| AUTH | false | No authority over HELEN |
| SOV | false | Non-sovereign layer |
| CANON | no | Cannot self-promote to canon |
| LEDGER | SLEEPING | No direct writes permitted |

---

## Command Set

```
+--------------------------------------------------+
| COMMAND     | SYNTAX               | ACT          |
+--------------------------------------------------+
| ask         | > ask <question>     | 🧌 GUIDE_ONLY |
| claim       | > claim <text>       | 🧾 LOCAL_ONLY |
| receipt     | > receipt <id>       | 🧾 EMIT_LOCAL |
| quest       | > quest <id>         | 🏰 SIMULATE  |
| map         | > map                | 🟣 SHOW_WORLD |
| faction     | > faction <name>     | 🌹🌀✝️⟂       |
| validate    | > validate           | 🔵 LINT_ONLY  |
| exit-temple | > exit-temple        | 🚪 LEAVE_SIM  |
+--------------------------------------------------+
| ⚠️ All commands are simulation-only              |
| ⚠️ No command writes to HELEN kernel or ledger   |
+--------------------------------------------------+
```

---

## Command: `ask`

```
+--------------------------------------------------+
| 🧌 GOBLIN GUIDE — READ ONLY                      |
+--------------------------------------------------+
| > ask "can I write to the ledger?"               |
|                                                  |
| 🧌 Goblin says: No. The ledger sleeps.           |
|   The dream provides no sovereign path.          |
|   Claims exist locally. HELEN decides admission. |
+--------------------------------------------------+
| STATUS: GUIDE_ONLY | AUTH=false | NO_VERDICT     |
+--------------------------------------------------+
```

---

## Command: `claim`

```
+--------------------------------------------------+
| 🟡 CLAIM — LOCAL RECEIPT ONLY                    |
+--------------------------------------------------+
| > claim "the spiral pattern holds"               |
|                                                  |
| 🟡 CLAIM REGISTERED (local only)                 |
|   proof_id: AVALON-CXXXXX                        |
|   layer: TEMPLE                                  |
|   authority: false                               |
|   sovereign: false                               |
|   status: PROPOSED                               |
|                                                  |
| ⚠️ NOT admitted. NOT canon. NOT sovereign.       |
| ⚖️ HELEN will judge when/if admitted.            |
+--------------------------------------------------+
```

---

## Command: `receipt`

```
+--------------------------------------------------+
| 🧾 RECEIPT — EMIT LOCAL                          |
+--------------------------------------------------+
| > receipt AVALON-E07                             |
|                                                  |
| 🧾 Receipt emitted: epoch_007.json               |
|   authority: false                               |
|   sovereign: false                               |
|   layer: TEMPLE                                  |
|   status: PROPOSED                               |
|                                                  |
| 📜 Ledger does not move.                         |
+--------------------------------------------------+
```

---

## Command: `map`

```
+==================================================+
| 🟣 AVALON WORLD MAP (SIMULATION ONLY)            |
+==================================================+
|                                                  |
|  [PROVENANCE REACHES] 🌹   [PATTERN WASTES] 🌀   |
|  receipted sources         emergent connections  |
|                                                  |
|  ─────────── [DREAM CORE] ─────────────          |
|              [ unclaimed ]                       |
|          [ highest knowledge ]                   |
|                                                  |
|  [BOUNDARY KEEPS] ✝️     [PERP FIELDS] ⟂◯⟂      |
|  constraint holding       orthogonal views       |
|                                                  |
|  ════════════ [HEAP WILDS] ═══════════           |
|              [ALWAYS NEUTRAL]                    |
|                                                  |
+==================================================+
| SIMULATION_ONLY | AUTH=false | LEDGER=SLEEPING   |
+==================================================+
```

---

## WULmoji Heraldic Format

```
[INDEX]  [STATE]  [FACTION]  [PAIR]  [ACT]  [PROOF]  [RIBBON]

Example:
(7) 🟣 🌀 🜃🜁 📜 🔗#AVALON-E07 🌿🌀

VALID_STATES:   🔵 🟢 🟣 ⚫ 🔴
VALID_FACTIONS: 🌹 🌀 ✝️ ⟂◯⟂
VALID_ACTS:     📜  🛡️  🔒📜  ⚠️📜
PROOF:          🔗#[A-Z0-9_-]+
PAIR:           exactly 2 grapheme clusters
RIBBON:         exactly 2 grapheme clusters
```

---

## Boundary Law

```
+--------------------------------------------------+
| 🔒 HARD BOUNDARY                                 |
+--------------------------------------------------+
| FORBIDDEN:                                       |
|   ✗ ledger writes                                |
|   ✗ kernel mutations                             |
|   ✗ schema changes                               |
|   ✗ canon promotion (self-declared)              |
|   ✗ write-gate approval                          |
|                                                  |
| ALLOWED:                                         |
|   ✓ local simulation                             |
|   ✓ WULmoji bulletins (non-sovereign)           |
|   ✓ local receipt chain                          |
|   ✓ CLI navigation and asking                    |
|   ✓ goblin guidance (non-authoritative)          |
+--------------------------------------------------+
| AUTH=false | SOV=false | LEDGER=SLEEPING         |
+--------------------------------------------------+
```

---

## WUL Law for AVALON

```
🜁 SYMBOL → 🜍 PATTERN → 🧪 TEST → 🧾 RECEIPT → ⚖️ ADMISSION → 📜 LEDGER

🜁 → 📜  ❌  (symbol to ledger direct: FORBIDDEN)

🧌🌿🚪🏰  Avalon may simulate.
🧪 Validator may read.
🧾 Receipts bind locally.
⚖️ HELEN waits.
📜 Ledger sleeps.
```

---

```
CLAIM_TYPE: cli
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
AUTH=false
SOV=false
LEDGER=SLEEPING
```
