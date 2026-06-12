"""
context_packet.py — assembled context packet produced by InitAirlock.

NON_SOVEREIGN: carries authority="NON_SOVEREIGN" by construction.
A packet that passes the airlock is admissible for routing.
It is not yet truth. Truth requires receipt + admission + reducer verdict.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextPacket:
    """
    The output of a successful /init airlock pass.

    Fields are set by the airlock — callers must not mutate them.
    authority is always "NON_SOVEREIGN". fabricated is always False.
    mutation_path_open is always False.
    """
    packet_id: str
    assembled_at: str                     # ISO-8601
    authority: str                         # always "NON_SOVEREIGN"

    # Check 1 result
    memory_source: str                     # "storage" | "absent" | "partial"
    prior_context: dict[str, Any] | None   # None when memory absent

    # Check 3 result
    scope: dict[str, str]                  # {"domain": str, "permission_tier": str}

    # Check 4 result
    runtime_probe: dict[str, Any]          # {"probe_time": str, "coupling_state": str, "git_summary": str}

    # Invariants enforced by airlock
    fabricated: bool = field(default=False, init=False)
    mutation_path_open: bool = field(default=False, init=False)
    airlock_version: str = field(default="V1", init=False)
    schema: str = field(default="CONTEXT_PACKET_V1", init=False)

    def __post_init__(self) -> None:
        if self.authority != "NON_SOVEREIGN":
            raise ValueError("authority must be NON_SOVEREIGN")
        if self.fabricated:
            raise ValueError("fabricated must be False")
        if self.mutation_path_open:
            raise ValueError("mutation_path_open must be False")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "airlock_version": self.airlock_version,
            "packet_id": self.packet_id,
            "assembled_at": self.assembled_at,
            "authority": self.authority,
            "memory_source": self.memory_source,
            "prior_context": self.prior_context,
            "scope": self.scope,
            "runtime_probe": self.runtime_probe,
            "fabricated": self.fabricated,
            "mutation_path_open": self.mutation_path_open,
        }
