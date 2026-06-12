---
name: reference_drift_witness
skill_id: REFERENCE_DRIFT_WITNESS_V1
description: Scans a declared set of non-sovereign artifacts and reports SHA drift, missing files, and stale receipts. Makes autoresearch epoch health observable and replayable.
authority: NONE
world_effect: NONE
sovereign_touch: false
domain_category: observability
provider_class: INTERNAL
admission_chain: E51→E52→E53→E54→E55→cb47c65
reducer_decision: ADMIT (JM_TASSY_MANUAL_REDUCER_DECISION, f73b7b2)
ledger_receipt: R-20260612-0007 / R-20260612-0008 / R-20260612-0009 (routing only)
institutional_admission: CONFIRMED (ADMISSION_LEDGER_V1.json / entry_hash=sha256:02ac60212c6f122b08b82250b766745dacc058b294a409158f8fd2786d98aee0 / replay_status=ACTIVE)
---

# REFERENCE_DRIFT_WITNESS_V1

Observability skill for non-sovereign autoresearch artifacts. Detects:
- **Drift** — SHA changed since last snapshot
- **Missing** — expected file absent
- **Stale** — receipt epoch lag exceeds threshold

## What it does NOT do

- No sovereign path reads or writes
- No ledger mutation
- No admission claims
- No calls to `helen_say.py`

## Inputs

```python
manifest: list[{"path": str, "expected_sha": str | None}]
```

## Outputs

```python
REFERENCE_DRIFT_REPORT_V1: {
    drift_count: int,
    missing_count: int,
    stale_count: int,
    total_artifacts: int,
    artifacts: [...],
    authority: "NONE",
    world_effect: "NONE",
    sovereign_touch: false,
}
```

## Usage

```python
from oracle_town.skills.reference_drift_witness import ReferenceDriftWitness

witness = ReferenceDriftWitness(
    sot_root="/path/to/helen_os_v1",
    current_epoch=55,
    staleness_epochs=10,
)

# Explicit manifest
report = witness.scan([
    {"path": "oracle_town/skills/ops/dan_goblin/scratch/EPOCH_RECEIPT_E51.json",
     "expected_sha": "sha256:abc..."},
])
print(report.clean)          # True if no drift/missing/stale
print(report.drift_count)
print(report.to_dict())

# Directory scan (auto-manifest)
report = witness.scan_directory(
    directory="oracle_town/skills/ops/dan_goblin/scratch",
    pattern="EPOCH_RECEIPT_E*.json",
)

# Snapshot current SHAs (for future expected_shas)
snapshot = witness.snapshot(manifest)
```

## CLI

```bash
PYTHONPATH=. .venv/bin/python -m oracle_town.skills.reference_drift_witness.cli \
  --dir oracle_town/skills/ops/dan_goblin/scratch \
  --pattern "EPOCH_RECEIPT_E*.json" \
  --epoch 55
```

## Tests

```bash
.venv/bin/pytest oracle_town/skills/reference_drift_witness/tests/ -v
```
