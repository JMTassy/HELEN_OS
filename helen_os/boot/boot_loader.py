"""boot_loader.py — load RuntimeBootContext from storage.

Law: reads from storage only. Never queries provider APIs.
     Never improvises. Missing file = None field, not error.
"""
from __future__ import annotations
import json
from pathlib import Path
from .runtime_boot_context import RuntimeBootContext


PERSON_PROFILE_FILE = "person_profile_v1.json"
SESSION_LOG_FILE = "last_session_v1.json"
EPOCH_STATE_FILE = "epoch_state_v1.json"
COMPANION_STATE_FILE = "companion_state_v1.json"
LIVE_CONTEXT_FILE = "live_context_v1.json"


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_boot_context(storage_dir: str, boot_time_iso: str = "") -> RuntimeBootContext:
    """Load boot context from storage_dir. Missing files produce None fields."""
    d = Path(storage_dir)
    person_profile = _load_json(d / PERSON_PROFILE_FILE)
    last_session   = _load_json(d / SESSION_LOG_FILE)
    epoch_state    = _load_json(d / EPOCH_STATE_FILE)
    companion_state = _load_json(d / COMPANION_STATE_FILE)
    live_context   = _load_json(d / LIVE_CONTEXT_FILE)

    any_loaded = any(v is not None for v in
                     (person_profile, last_session, epoch_state,
                      companion_state, live_context))

    return RuntimeBootContext(
        person_profile=person_profile,
        last_session=last_session,
        epoch_state=epoch_state,
        companion_state=companion_state,
        live_context=live_context,
        boot_time_iso=boot_time_iso,
        loaded_from="storage" if any_loaded else "empty",
    )
