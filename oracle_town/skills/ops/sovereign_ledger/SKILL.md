---
id: sovereign_ledger
label: Ledger
icon: 🏛️
domain: governance
status: active
ledger_enabled: true
---

Load this skill when the user asks to inspect receipts, review decisions, audit actions, query MAYOR verdicts, or verify the chain of events. This is the memory surface of HELEN OS.

## Actions
- inspect_receipt — show a specific receipt by hash or event ID
- list_events — list recent ledger events by type or date
- verify_chain — check hash-chain integrity
- query_verdict — retrieve MAYOR verdict for a given claim
- export_summary — produce a human-readable ledger summary

## Reads
- town/ledger_v1.ndjson (read-only)
- GOVERNANCE/CLOSURES/
- GOVERNANCE/TRANCHE_RECEIPTS/

## Writes
- artifacts/ledger_exports/ (read-only summaries, never ledger writes)

## Gotchas
- NEVER write to town/ledger_v1.ndjson directly — sovereign firewall path
- The only admitted writer is tools/helen_say.py
- NO RECEIPT = NO CLAIM — if there's no receipt, the event did not happen
- Reading is always safe; writing requires MAYOR authorization
