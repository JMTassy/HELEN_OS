# BATCH 001 — TEMPLE_GOBLIN_SANDBOX00_300

**Scope:** epochs 001–050 only (Batch 001 of 006)  
**Mode:** TRACE_ONLY  
**Sandbox path:** `temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/batch_001/`

## Authorization

```
AUTHORITY=false
SOVEREIGN=false
CANON=false
LEDGER=SLEEPING
COMMIT=BLOCKED
PUSH=BLOCKED
JM_ADMITS=PENDING
```

## What this batch does

Generates 50 world-model artifacts for GARDEN_CONQUEST_AVALON in TRACE_ONLY mode.
Each artifact is a JSON file with 13 required fields. No executable code is generated.
No governance paths are touched. Ledger does not move.

## Files in this batch

```
epochs/epoch_001.json  … epoch_050.json    — 50 world-model artifacts
receipts/receipt_001.json … receipt_050.json — 50 local receipts
BATCH_001_SUMMARY.md                         — produced after generation
run_batch_001.py                             — generates epochs + receipts
validate_batch_001.py                        — validates before and after generation
```

## Forbidden paths (must remain untouched)

```
GOVERNANCE/
docs/proposals/
helensh/.state/live_ledger.jsonl
admitted_canon.jsonl
town/ledger_v1.ndjson
oracle_town/kernel/
helen_os/governance/
helen_os/schemas/
oracle_town/skills/
tests/   (except sandbox-local validators in this directory)
```

## Stop conditions (hard)

Stop immediately if any artifact contains:
`CANON=true`, `SOVEREIGN=true`, `AUTHORITY=true`, `ADMITTED`, `MAYOR`, `SEAL` (without `_LOCAL`),
`LEDGER_WRITE`, `HELEN_APPROVED`, `JM_ADMITTED`

Stop if any file outside the sandbox path was modified.
Stop if same failure occurred twice.
Stop after epoch 050.

## Run sequence

```
1. python validate_batch_001.py   (pre-run check — must pass)
2. python run_batch_001.py        (generates 50 epochs + 50 receipts)
3. python validate_batch_001.py   (post-run check — must pass)
4. inspect BATCH_001_SUMMARY.md
5. git status --short             (final containment check)
```

---

```
CLAIM_TYPE: cli
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
This batch is not admitted, not canon, not sovereign, and not HELEN governance.
```
