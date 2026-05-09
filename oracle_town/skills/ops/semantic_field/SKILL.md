---
name: helen-semantic-field
description: load when the user asks to inspect, debug, modify, or extend the HELEN OS semantic object field, /api/semantic endpoint, object types (EVENT/EPOCH/ACTION/RECEIPT), edge structure, provenance rules (kernel/goblin/terminal), force simulation, or constellation graph behavior.
authority: NON_SOVEREIGN
canon: NO_SHIP
---

# HELEN Semantic Field Skill

## Purpose

The semantic field is the core operating surface of HELEN OS. It is an object-first model, not a chat sequence. Every piece of knowledge, action, and receipt is a typed object with provenance, confidence, and receipt count.

```
semantic object field → pull → compose → validate → persist
```

Not: message → response.

## Object Schema

Every object in the field:

```json
{
  "id":         "string",
  "type":       "EVENT | EPOCH | ACTION | RECEIPT",
  "subject":    "string (≤70 chars — the semantic label)",
  "relations":  ["string"],
  "confidence": 0.0–1.0,
  "receipts":   "integer — 0 means unverified",
  "timestamp":  "ISO UTC",
  "provenance": "kernel | goblin | terminal",
  "sovereign":  "boolean",
  "hash":       "string (12 chars, empty if non-sovereign)"
}
```

## Provenance Rules

| Provenance | Source | Sovereign? | Signal color? |
|---|---|---|---|
| `kernel` | `experiments/helen_os_v02/data/ledger.ndjson` | Yes | Amber |
| `goblin` | `oracle_town/skills/ops/dan_goblin/brainstorm/batches/*.jsonl` | No | Silver |
| `terminal` | `oracle_town/skills/ops/helen_terminal/data/ledger.ndjson` | No | Dim |

## Edge Rules

Edges represent semantic relations between objects:

- `weight 0.4` — temporal (same provenance, sequential)
- `weight 0.7` — cross-provenance, high-confidence objects linked

Edge color opacity scales with weight. Cross-provenance edges use signal amber tint.

## Force Simulation Parameters

| Parameter | Value | Effect |
|---|---|---|
| GRAVITY | 0.005 | Pull toward center (HELEN) |
| AVATAR_R | 80px | Exclusion zone around sovereign anchor |
| REPEL_K | 1100 | Node repulsion strength |
| REPEL_R | 90px | Repulsion radius |
| SPRING_K | 0.03 | Edge spring strength |
| DAMP | 0.85 | Velocity damping |
| VMAX | 2.2 | Max velocity (px/frame) |

## Scripts

```bash
scripts/inspect_semantic_api.py    # print object count, types, provenance, top-5 by confidence
scripts/validate_objects.py        # validate all objects against canonical schema
```

## Gotchas

- `receipts: 0` means unverified — do not treat 0-receipt objects as canonical.
- GOBLIN epochs have `sovereign: false` — they cannot be promoted without MAYOR gate.
- The `/api/semantic` endpoint synthesizes from three live sources; if any source dir is missing, that provenance returns empty (graceful, not error).
- High-confidence GOBLIN epochs (0.765) are displayed with labels in the constellation — this is intentional (they earned it by HER scoring).
- Never add a node type without updating both server.py synthesis and the canonical schema here.
- Kernel objects use real hash IDs (e.g., `E-00c498c39b01`) from the ledger. Do not generate fake hashes.
