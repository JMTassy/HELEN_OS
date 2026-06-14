# AUTORESEARCH_RECEIPT_V1 Schema

Every admissible autoresearch epoch emits one receipt.

```json
{
  "type": "AUTORESEARCH_RECEIPT_V1",
  "epoch": 42,
  "concept": "REPLAY",
  "probe_dimension": "frequency_in_docs",
  "hypothesis": "REPLAY appears frequently in docs/ indicating a doctrine-level attractor",
  "method": "FREQUENCY",
  "evidence_count": 47,
  "verdict": "CONFIRMED",
  "claim": "REPLAY is a high-frequency concept in HELEN doctrine (47 occurrences in 23 files)",
  "source_paths": [
    "docs/autoresearch/doctrine.md",
    "KERNEL_V2.md"
  ],
  "source_hashes": {
    "docs/autoresearch/doctrine.md": "sha256:abc123...",
    "KERNEL_V2.md": "sha256:def456..."
  },
  "gate_scores": {
    "K0": 1, "K1": 1, "K2": 1, "K3": 1, "K4": 1,
    "K5": 1, "K6": 1, "K7": 1, "K8": 1, "Ktau": 1, "W": 1
  },
  "gate_total": 1.0,
  "lineage_pressure": 0.85,
  "receipt_hash": "sha256:...",
  "authority": "NONE",
  "non_sovereign": true
}
```

## Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| type | string | yes | Always "AUTORESEARCH_RECEIPT_V1" |
| epoch | int | yes | Epoch number (1-N) |
| concept | string | yes | Attractor concept probed |
| probe_dimension | string | yes | Which angle was probed |
| hypothesis | string | yes | Falsifiable hypothesis tested |
| method | string | yes | FREQUENCY/COUPLING/EVOLUTION/CONTRADICTION/COVERAGE/STALENESS |
| evidence_count | int | yes | Number of evidence instances found |
| verdict | string | yes | CONFIRMED/WEAK/ABSENT/ERROR |
| claim | string | yes | Explicit claim in definite language |
| source_paths | list[str] | yes | Files or artifacts probed |
| source_hashes | dict | yes | sha256 of each source at probe time |
| gate_scores | dict | yes | K0-K8, Ktau, W — all binary |
| gate_total | float | yes | sum(gate_scores) / 11 |
| lineage_pressure | float | yes | 0.0-1.0; proportion of probe angles that CONFIRM |
| receipt_hash | string | yes | sha256(canon(receipt without receipt_hash field)) |
| authority | string | yes | Always "NONE" — autoresearch is non-sovereign |
| non_sovereign | bool | yes | Always true |

## Verdict Definitions

| Verdict | Condition |
|---|---|
| CONFIRMED | evidence_count ≥ threshold AND all gates PASS |
| WEAK | evidence_count > 0 but below threshold OR coupling is partial |
| ABSENT | evidence_count = 0 |
| ERROR | gate failure; receipt is diagnostic only, not admissible |

## Lineage Pressure

lineage_pressure = confirmed_probe_angles / total_probe_angles_for_concept

This is the Obsidian Mirror's key output per attractor.
High lineage_pressure = strong attractor candidate.
Low lineage_pressure = weak or context-specific appearance.

lineage_pressure is NOT truth.
It is evidence of recurrence — input for doctrine delta, not doctrine itself.

## Authority Invariant

AUTORESEARCH_RECEIPT_V1 is always authority: NONE.
These receipts are candidate claims for MAYOR routing.
They do not enter town/ledger_v1.ndjson without MAYOR verdict.
