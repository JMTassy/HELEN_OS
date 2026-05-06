"""
helen_orchestrator.py — HELEN OS Agent Orchestrator · NON_SOVEREIGN
authority=false, canon=NO_SHIP

Starts agents, routes WUL packets between them, reports system status.
Does NOT write to the sovereign ledger. Does NOT emit MAYOR verdicts.
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Optional

from src.helen_agent_base import CANONICAL_ROLES, HELENAgentBase, WULPacket
from src.helen_agent_registry import HELENAgentRegistry


class RoutingError(Exception):
    pass


class HELENOrchestrator:
    """
    Non-sovereign agent orchestrator.

    Topology (canonical): AURA → HER → DAN ↔ GOBLIN → HAL → DIRECTOR → MAYOR → LEDGER
    The orchestrator routes packets; it does not decide verdicts.
    """

    def __init__(self, receipt_dir: Path | str = "receipts/agents") -> None:
        self.registry = HELENAgentRegistry()
        self._receipt_dir = Path(receipt_dir)
        self._route_count = 0

    # ── agent lifecycle ───────────────────────────────────────────────────────

    def register(self, agent: HELENAgentBase) -> None:
        """Register and start an agent."""
        self.registry.register(agent)
        if not agent.alive:
            agent.start()

    def stop_all(self) -> None:
        """Stop all registered agents."""
        for name in list(self.registry.all_roles()):
            agent = self.registry.get(name)
            if agent:
                agent.stop()

    # ── message routing ───────────────────────────────────────────────────────

    def route(
        self,
        sender: str,
        recipient: str,
        intent: str,
        payload: dict,
    ) -> str:
        """
        Route a WUL packet from sender → recipient.
        Returns the packet_id for tracking.
        Raises RoutingError if recipient is not registered.
        """
        agent = self.registry.get(recipient)
        if agent is None:
            raise RoutingError(
                f"No agent registered for role {recipient!r}. "
                f"Registered: {sorted(self.registry.all_roles())}"
            )
        if not agent.alive:
            raise RoutingError(f"Agent {recipient!r} is registered but not alive.")

        packet = WULPacket(
            sender=sender,
            recipient=recipient,
            intent=intent,
            payload=payload,
        )
        self._route_count += 1
        agent.send(packet.to_dict())
        return packet.packet_id

    # ── status ────────────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "routes_dispatched": self._route_count,
            "agents": self.registry.status(),
            "authority": False,
            "canon": "NO_SHIP",
        }

    def __repr__(self) -> str:
        return (
            f"<HELENOrchestrator "
            f"agents={sorted(self.registry.all_roles())} "
            f"routes={self._route_count}>"
        )
