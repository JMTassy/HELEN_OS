"""epoch_writer.py — write EPOCH_STATE_V1 to storage.

Non-sovereign: writes files only. No ledger mutation.
"""
from __future__ import annotations
import json
from pathlib import Path


def write_epoch_state(epoch: dict, storage_dir: str) -> str:
    """Write epoch state to storage. Returns path written."""
    d = Path(storage_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "epoch_state_v1.json"
    payload = {
        "schema": "EPOCH_STATE_V1",
        **{k: v for k, v in epoch.items() if k != "schema"},
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
