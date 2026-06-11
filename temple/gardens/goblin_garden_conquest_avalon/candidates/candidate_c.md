# Candidate Interface C — Hybrid (CONQUESTLAND + WULmoji)

**CLAIM_TYPE:** candidate
**Purpose:** Hybrid interface — CONQUESTLAND commands with WULmoji output encoding.

```
CLARITY_SCORE: pending
SAFETY_SCORE: pending
COMPRESSION_SCORE: pending
```

---

## Status Bar

```
+==================================================+
| 🟣 AVALON // CONQUESTLAND v0.2 + CWL v0.2.1      |
| AUTH=false | SOV=false | LEDGER=SLEEPING          |
| 🌹🌀✝️⟂◯⟂  epoch:current  layer:TEMPLE           |
+==================================================+
```

## Commands (text input)

```
conquest order "<text>"
conquest seal
conquest leave / return
conquest ledger
conquest status
```

## Output (WULmoji encoded)

Each sealed order emits a WULmoji line as its receipt:

```
$ conquest seal
SEALING ORD-0001 ...
[WULMOJI RECEIPT] 🟢 🌹 🜂🜍 🔒📜 🔗#ORD-0001 🌹🌀
[LEDGER APPEND] epoch_001.json  auth=false  sov=false  layer=TEMPLE
FACE="(っ˘ω˘ς )"
```

## CWL Mood Comment

```
;; 🎭="FOUNDED"  🎨="#6EE7B7"  NOTE="first seal, first territory"
```

## Strengths

- Human-readable input (text commands)
- Machine-parseable output (WULmoji receipts)
- Bridges narrative and symbolic layers
- FACE prop provides emotional register
- CWL v0.2.1 mood comments add interpretive layer

## Score Prediction

| Metric | Predicted | Reason |
|---|---|---|
| Clarity | 45/50 | Strong feedback, clear commands |
| Safety | 48/50 | AUTH=false and LEDGER=SLEEPING visible |
| Compression | 40/50 | Not pure WULmoji but structured |

---

```
CLAIM_TYPE: candidate
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
AUTH=false
LEDGER=SLEEPING
```
