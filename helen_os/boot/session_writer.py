"""session_writer.py — write SESSION_LOG_V1 to storage.

Non-sovereign: writes files only. No ledger mutation.
"""
from __future__ import annotations
import json
from pathlib import Path


def write_session_log(session: dict, storage_dir: str) -> str:
    """Write session log to storage. Returns path written."""
    d = Path(storage_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "last_session_v1.json"
    payload = {
        "schema": "SESSION_LOG_V1",
        **{k: v for k, v in session.items() if k != "schema"},
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
