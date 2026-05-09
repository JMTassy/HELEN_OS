# Semantic Object Schema

Canonical schema for all objects in the HELEN OS semantic field.

```json
{
  "id":         "string — unique, stable identifier",
  "type":       "EVENT | EPOCH | ACTION | RECEIPT",
  "subject":    "string — semantic label, ≤70 chars",
  "relations":  ["string — relation labels"],
  "confidence": "float 0.0–1.0",
  "receipts":   "integer — 0 = unverified",
  "timestamp":  "ISO 8601 UTC",
  "provenance": "kernel | goblin | terminal",
  "sovereign":  "boolean",
  "hash":       "string — 12 hex chars, empty string if non-sovereign"
}
```

## Type Definitions

| Type | Source | Sovereign? |
|---|---|---|
| `EVENT` | Kernel ledger entries | Yes |
| `EPOCH` | GOBLIN brainstorm epochs (top-scored) | No |
| `ACTION` | Terminal ledger entries | No |
| `RECEIPT` | Future — tranche receipt objects | Depends |

## Validation

Run: `scripts/validate_objects.py`

All fields in REQUIRED set must be present. confidence must be 0.0–1.0. relations must be a list (may be empty).
