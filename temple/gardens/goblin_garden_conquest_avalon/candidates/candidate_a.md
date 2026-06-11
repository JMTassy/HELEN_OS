# Candidate Interface A — CONQUESTLAND CLI v0.2

**CLAIM_TYPE:** candidate
**Purpose:** Canonical CLI interface for DREAM_OF_CONQUEST. Deterministic, ledger-first.

```
CLARITY_SCORE: pending
SAFETY_SCORE: pending
COMPRESSION_SCORE: pending
```

---

## Status Bar

```
+==================================================+
| 🜏 AVALON // DREAM_OF_CONQUEST // CLI_GATE        |
| AUTH=false | SOV=false | CANON=no | LEDGER=SLEEPING |
+==================================================+
```

## Core Commands

```
conquest status        — read-only projection
conquest enter         — threshold
conquest order "..."   — draft until sealed
conquest seal          — irreversible inscription
conquest leave         — world continues
conquest return        — re-entry after 24h
conquest ledger [--tail N] [--json]
conquest inspect --delta
conquest agents
conquest help
```

## Example Session

```
$ conquest status
[CASTLE] name: AVALON  phase: FOUNDATION  tick: 0
[INVARIANTS]
  append_only_ledger: TRUE
  no_undo: TRUE
  no_silent_authority: TRUE
  single_order_before_first_return: TRUE
  return_delay_hours: 24

$ conquest enter
CONQUESTLAND THRESHOLD
You may issue exactly ONE order before first return.

$ conquest order "Engrave the Founding Oath into the Archive."
[ORDER DRAFT] id: ORD-0001  scope: AVALON::HOME_KEEP  status: DRAFT

$ conquest seal
SEALING ORD-0001 ... OK. No undo. No edit.
[LEDGER APPEND]
  (001) IDENTITY_DECLARED  actor=JM_SEMPER_FIDELIS  seal=SYSTEM
  (002) HOME_KEEP_ASSIGNED territory=AVALON  owner=JM_SEMPER_FIDELIS  status=INALIENABLE  seal=SYSTEM
  (003) ORDER_SEALED  id=ORD-0001  territory=AVALON  seal=JM

$ conquest leave
SEALED. World will continue without you.
Return available after: +24h
```

## CWL v0.2.1 Clause Example

```
⚔️: 🛑 @⚔️ ~◷8 ⚡ {
  🥖=8 🥖BAR="■■■■■■■■□□"
  💖=1.5 💖BAR="■◐□□□□□□□□"
  🛡️=4.5 🛡️BAR="■■■■◐□□□□□"
  ⚠️=2
  OVERLAY="🜂 ✝️ ⛧"
  ⛰️->⛓️  ⛓️->🔥  🔥->⚒️  ⚒️->⚡  ⚡->✖️
  FACE="(ง'̀-'́)ง" }

;; 🎭="CRISIS"  🎨="#EF4444"
```

---

```
CLAIM_TYPE: candidate
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
AUTH=false
LEDGER=SLEEPING
```
