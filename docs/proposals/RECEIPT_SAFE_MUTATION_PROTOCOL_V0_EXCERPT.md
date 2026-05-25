# RECEIPT_SAFE_MUTATION_PROTOCOL_V0 — operator excerpt

**authority:** NON_SOVEREIGN
**lifecycle:** DOCTRINE_DRAFT
**status:** reference excerpt of `RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md`
**origin_signal:** `HIGH ev=3 "mutating ledger without receipt"` — RALPH epochs 8, 9, 10

Use this excerpt to ground a proposal in HELEN OS concepts. Do not restate it.
Propose a concrete next mechanism that advances the doctrine.

## §0 Axiom

**NO VALID RECEIPT = NO TRUSTED STATE MUTATION.**

Receipt law extended: not just "no observable action," but "no trusted writable state."

## §1 Origin

Three RALPH autoresearch epochs (8, 9, 10) surfaced the same sovereignty violation:
the system can mutate durable state without producing a corresponding receipt.
The recurring pressure is the absence of a doctrine. The kernel enforces receipt-for-action;
nothing yet enforces receipt-for-mutation as a separate, named discipline.

## §3 Mutation classes (M1–M7)

- M1 Ledger mutation (hash-chained, via `LedgerWriter` only)
- M2 Quarantine receipt write (RAW lifecycle, `GOVERNANCE/*_PROPOSALS/`)
- M3 Lane annotation (`operator_decision` xor `hal_verdict`, strict isolation)
- M4 Lifecycle promotion (MAYOR-only, not yet implemented)
- M5 Derived artifact (`reports/`, `docs/` — not state)
- M6 Filesystem scaffolding (not state)
- M7 External effect via CLAW (gated, two-receipt, authority=False)

## §5 Gates (authority partition)

- Governor (G layer, kernel) — gates M1 and M7, 5 fail-closed gates
- Operator — gates M3 op lane only, via `review_cockpit.py`
- HAL — gates M3 hal lane only, via cockpit H-path or `hal_reviewer.py`
- MAYOR — sole gate for M4, NOT YET IMPLEMENTED

No actor holds more than one gate.

## §6 Forbidden mutations

1. Writing `helensh/.state/live_ledger.jsonl` outside `LedgerWriter`
2. Writing a receipt without first reading it
3. Mutating `lifecycle_entry` or `auto_promotion_ceiling` from non-MAYOR
4. Cross-lane writes (operator writes hal_verdict, or vice versa)
5. Writing a receipt with `authority = True`
6. Mutating a source NDJSON (sources are append-only by producer)
7. Embedding timestamps inside the hashed body
8. Reusing a receipt filename for a different logical receipt
9. Coalescing two mutations into one write
10. Reporting success when the receipt write failed
11. Bypassing canonical JSON serialization

## §8 Per-tool implementation contract

A tool is receipt-safe-mutation-compliant only if it satisfies all of:
- Declared mutation class (M1–M7) in docstring
- Hard-constraint block enumerating §6 violations it does not perform
- Lane isolation (M3 tools): separate write functions for op and hal
- Canonical serialization (M1 tools): `sort_keys=True, separators=(",",":")`
- UTF-8 explicit on every `write_text`
- Read-tolerant decode (utf-8, cp1252 fallback)
- Non-zero exit on write failure (no silent retry)
- No timestamps in hashed bodies
- Determinism test (same input → same output bytes)
- Cited §5 gate it claims authority under
