"""Append-only NDJSON event log."""
from __future__ import annotations

import json
import os
from pathlib import Path

from helen_os.ledger.hash_chain import canonical_json

# Optional capability guard for the append sink (χ_med). When installed, every
# append must present a capability the guard accepts; without a guard the sink
# behaves as before (legacy tests unaffected). Install/reset via set_capability_guard.
_capability_guard = None


def set_capability_guard(guard) -> None:
    """guard: callable(event: dict, capability) -> None, raising PermissionError
    to deny. Pass None to uninstall."""
    global _capability_guard
    _capability_guard = guard


def append_event(path: str | os.PathLike, event: dict, capability=None) -> None:
    if _capability_guard is not None:
        _capability_guard(event, capability)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(canonical_json(event).decode("utf-8") + "\n")


def read_events(path: str | os.PathLike) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    out: list[dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out
