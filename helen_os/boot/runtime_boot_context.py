"""RUNTIME_BOOT_CONTEXT_V1 — boot continuity object.

Law: greeting_render reads only this object.
     NOT provider memory. NOT ad hoc queries. NOT improvisation.

Graceful degradation: if component = None, render null-honest.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeBootContext:
    """Composed boot context. All fields are optional — graceful degradation law."""
    person_profile: dict[str, Any] | None = None
    last_session: dict[str, Any] | None = None
    epoch_state: dict[str, Any] | None = None
    companion_state: dict[str, Any] | None = None
    live_context: dict[str, Any] | None = None
    boot_time_iso: str = ""
    loaded_from: str = "empty"  # "storage" | "fallback" | "empty"

    def is_empty(self) -> bool:
        return all(
            v is None
            for v in (self.person_profile, self.last_session,
                      self.epoch_state, self.companion_state, self.live_context)
        )

    def person_name(self) -> str | None:
        if self.person_profile:
            return self.person_profile.get("name")
        return None

    def last_epoch_id(self) -> str | None:
        if self.epoch_state:
            return self.epoch_state.get("epoch_id")
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "RUNTIME_BOOT_CONTEXT_V1",
            "person_profile": self.person_profile,
            "last_session": self.last_session,
            "epoch_state": self.epoch_state,
            "companion_state": self.companion_state,
            "live_context": self.live_context,
            "boot_time_iso": self.boot_time_iso,
            "loaded_from": self.loaded_from,
        }
