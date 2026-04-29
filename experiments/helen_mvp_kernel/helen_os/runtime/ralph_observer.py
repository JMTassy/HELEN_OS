"""Ralph Observer — tails the ralph sidecar and yields iteration snapshots.

Ralph explores. HELEN observes. Nothing here touches the ledger.

The ralph sidecar (artifacts/ralph_runs.ndjson) is written by
scripts/ralph_ollama_once.py --sidecar. This module makes those
iterations visible as a continuous event stream, subscribable via SSE.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Generator


def tail_ralph(
    sidecar_path: Path,
    poll_interval: float = 0.25,
) -> Generator[dict, None, None]:
    """Continuously yield new Ralph iteration records as they are appended.

    Each record carries: ts, model, prompt_hash, output_hash,
    promise_found, promise_token — exactly what ralph_ollama_once.py writes.
    Adds iteration_index (monotonically increasing from 0).
    """
    sidecar_path = Path(sidecar_path)
    seen = 0

    while True:
        if sidecar_path.exists():
            with sidecar_path.open("r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]

            while seen < len(lines):
                try:
                    record = json.loads(lines[seen])
                    record["iteration_index"] = seen
                    yield record
                except json.JSONDecodeError:
                    pass
                seen += 1

        time.sleep(poll_interval)


def current_ralph_state(sidecar_path: Path) -> dict:
    """Return a point-in-time summary of all Ralph iterations so far."""
    sidecar_path = Path(sidecar_path)
    if not sidecar_path.exists():
        return {"iteration_count": 0, "last_iteration": None, "complete": False}

    with sidecar_path.open("r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    if not records:
        return {"iteration_count": 0, "last_iteration": None, "complete": False}

    last = records[-1]
    return {
        "iteration_count": len(records),
        "last_iteration": last,
        "complete": any(r.get("promise_found") for r in records),
        "last_promise_found": last.get("promise_found", False),
        "last_model": last.get("model"),
        "last_ts": last.get("ts"),
    }
