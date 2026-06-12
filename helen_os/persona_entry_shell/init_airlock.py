"""
init_airlock.py — /init constitutional airlock.

Implements the 6-check contract from docs/specs/PERSONA_ENTRY_SHELL_V1.md §3.

Usage:
    airlock = InitAirlock(storage_dir="storage", scope={"domain": "HELEN_OS", "permission_tier": "READ_ONLY"})
    packet = airlock.open()   # raises AirlockRejected if any check fails

Shell ≠ Truth. This airlock produces a context packet, never a truth claim.
"""
from __future__ import annotations

import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from helen_os.boot.boot_loader import load_boot_context
from .context_packet import ContextPacket

# Sovereign surfaces — the airlock must never open a write path to these
_SOVEREIGN_SURFACES = (
    "helen_os/governance/",
    "helen_os/schemas/",
    "oracle_town/kernel/",
    "town/ledger_v1",
    "GOVERNANCE/CLOSURES/",
    "GOVERNANCE/TRANCHE_RECEIPTS/",
    "mayor_",
)

_VALID_PERMISSION_TIERS = {"READ_ONLY", "EXECUTION", "SANDBOX"}
_SOVEREIGN_TIERS = {"SOVEREIGN", "KERNEL", "LEDGER"}


class AirlockRejected(Exception):
    """Raised when the /init airlock rejects a context packet."""
    def __init__(self, check: str, reason: str) -> None:
        self.check = check
        self.reason = reason
        super().__init__(f"AirlockRejected at [{check}]: {reason}")


class InitAirlock:
    """
    The /init constitutional airlock.

    Runs 6 checks in sequence. All must pass before a ContextPacket is returned.
    Any failure raises AirlockRejected — the packet is not assembled.

    Checks (from spec §3):
      1. memory_source     — storage-backed or explicitly absent; never fabricated
      2. no_fabrication    — absent memory → prior_context must be None
      3. scope_resolved    — domain and permission_tier declared, not sovereign-tier
      4. runtime_probe     — Probe(now) called and attached
      5. packet_nonsov     — authority="NON_SOVEREIGN" enforced
      6. no_mutation_path  — no write path to ledger/kernel/sovereign schemas opened
    """

    def __init__(self, storage_dir: str, scope: dict[str, str],
                 boot_time_iso: str = "") -> None:
        self._storage_dir = storage_dir
        self._scope = scope
        self._boot_time_iso = boot_time_iso or datetime.now(tz=timezone.utc).isoformat()
        self._checks_passed: list[str] = []

    # ── Public entry point ──────────────────────────────────────────

    def open(self) -> ContextPacket:
        """
        Run all 6 checks. Returns a ContextPacket on success.
        Raises AirlockRejected if any check fails.
        """
        memory_source, prior_context = self._check_memory_source()
        self._check_no_fabrication(memory_source, prior_context)
        scope = self._check_scope_resolved()
        runtime_probe = self._check_runtime_probe()
        packet = self._assemble_packet(memory_source, prior_context, scope, runtime_probe)
        self._check_packet_nonsovereign(packet)
        self._check_no_mutation_path(packet)
        return packet

    @property
    def checks_passed(self) -> list[str]:
        return list(self._checks_passed)

    # ── Check 1: memory source ──────────────────────────────────────

    def _check_memory_source(self) -> tuple[str, dict[str, Any] | None]:
        storage = Path(self._storage_dir)
        if not storage.exists():
            self._checks_passed.append("memory_source")
            return "absent", None

        boot_ctx = load_boot_context(self._storage_dir, self._boot_time_iso)
        if boot_ctx.loaded_from == "empty":
            self._checks_passed.append("memory_source")
            return "absent", None

        prior: dict[str, Any] = {
            "loaded_from": boot_ctx.loaded_from,
            "last_session": boot_ctx.last_session,
            "epoch_state": boot_ctx.epoch_state,
            "person_profile": boot_ctx.person_profile,
        }
        memory_source = "storage" if boot_ctx.loaded_from == "storage" else "partial"
        self._checks_passed.append("memory_source")
        return memory_source, prior

    # ── Check 2: no fabrication ─────────────────────────────────────

    def _check_no_fabrication(self, memory_source: str,
                               prior_context: dict[str, Any] | None) -> None:
        # If memory is absent, prior_context MUST be None — no invented history
        if memory_source == "absent" and prior_context is not None:
            raise AirlockRejected(
                "no_fabrication",
                "memory_source=absent but prior_context is not None — fabrication detected"
            )
        # prior_context must not contain invented fields
        if prior_context is not None:
            if prior_context.get("_fabricated"):
                raise AirlockRejected(
                    "no_fabrication",
                    "prior_context carries _fabricated=True marker"
                )
        self._checks_passed.append("no_fabrication")

    # ── Check 3: scope resolved ─────────────────────────────────────

    def _check_scope_resolved(self) -> dict[str, str]:
        scope = self._scope
        if not scope:
            raise AirlockRejected("scope_resolved", "scope is empty — must be declared before opening airlock")

        domain = scope.get("domain", "").strip()
        if not domain:
            raise AirlockRejected("scope_resolved", "scope.domain is missing or empty")

        tier = scope.get("permission_tier", "").strip()
        if not tier:
            raise AirlockRejected("scope_resolved", "scope.permission_tier is missing or empty")

        if tier in _SOVEREIGN_TIERS:
            raise AirlockRejected(
                "scope_resolved",
                f"permission_tier={tier!r} is sovereign — airlock cannot open a sovereign-tier context"
            )

        if tier not in _VALID_PERMISSION_TIERS:
            raise AirlockRejected(
                "scope_resolved",
                f"permission_tier={tier!r} is unknown — valid tiers: {sorted(_VALID_PERMISSION_TIERS)}"
            )

        self._checks_passed.append("scope_resolved")
        return scope

    # ── Check 4: runtime probe ──────────────────────────────────────

    def _check_runtime_probe(self) -> dict[str, Any]:
        probe_time = datetime.now(tz=timezone.utc).isoformat()

        # git status — coupling state
        try:
            r = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=10
            )
            dirty_lines = [l for l in r.stdout.splitlines() if not l.startswith("??")]
            sovereign_dirty = [
                l[3:].strip() for l in dirty_lines
                if any(s in l for s in _SOVEREIGN_SURFACES)
                and "town/ledger_v1" not in l  # expected noise
            ]
            coupling_state = "HARD_DRIFT" if sovereign_dirty else "COUPLED"
            git_summary = f"{len(dirty_lines)} modified, {len(sovereign_dirty)} sovereign-dirty"
        except Exception as exc:
            coupling_state = "PROBE_ERROR"
            git_summary = f"git probe failed: {exc}"
            sovereign_dirty = []

        probe = {
            "probe_time": probe_time,
            "coupling_state": coupling_state,
            "git_summary": git_summary,
            "sovereign_dirty": sovereign_dirty,
        }
        self._checks_passed.append("runtime_probe")
        return probe

    # ── Assemble packet ─────────────────────────────────────────────

    def _assemble_packet(self, memory_source: str, prior_context: dict | None,
                          scope: dict, runtime_probe: dict) -> ContextPacket:
        return ContextPacket(
            packet_id=f"PKT-{uuid.uuid4().hex[:12].upper()}",
            assembled_at=datetime.now(tz=timezone.utc).isoformat(),
            authority="NON_SOVEREIGN",
            memory_source=memory_source,
            prior_context=prior_context,
            scope=scope,
            runtime_probe=runtime_probe,
        )

    # ── Check 5: packet marked non-sovereign ───────────────────────

    def _check_packet_nonsovereign(self, packet: ContextPacket) -> None:
        if packet.authority != "NON_SOVEREIGN":
            raise AirlockRejected(
                "packet_nonsovereign",
                f"packet.authority={packet.authority!r} — must be NON_SOVEREIGN"
            )
        if packet.fabricated:
            raise AirlockRejected("packet_nonsovereign", "packet.fabricated=True")
        self._checks_passed.append("packet_nonsovereign")

    # ── Check 6: no mutation path ───────────────────────────────────

    def _check_no_mutation_path(self, packet: ContextPacket) -> None:
        if packet.mutation_path_open:
            raise AirlockRejected(
                "no_mutation_path",
                "packet.mutation_path_open=True — airlock must not open a write path"
            )
        # Structural: verify scope does not request sovereign write tier
        tier = packet.scope.get("permission_tier", "")
        if tier in _SOVEREIGN_TIERS:
            raise AirlockRejected(
                "no_mutation_path",
                f"permission_tier={tier!r} would open a sovereign mutation path"
            )
        self._checks_passed.append("no_mutation_path")
