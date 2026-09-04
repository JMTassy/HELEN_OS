"""
helen_agent_registry.py — HELEN OS Agent Registry · NON_SOVEREIGN
authority=false, canon=NO_SHIP
"""

from __future__ import annotations

from typing import Dict, Optional

from src.helen_agent_base import CANONICAL_ROLES, HELENAgentBase


class HELENAgentRegistry:
    """
    Named registry for HELEN OS agents.

    Only CANONICAL_ROLES are admissible.
    One agent per role — re-registering replaces the previous instance.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, HELENAgentBase] = {}

    def register(self, agent: HELENAgentBase) -> None:
        if agent.name not in CANONICAL_ROLES:
            raise ValueError(
                f"Role {agent.name!r} not in canonical set {sorted(CANONICAL_ROLES)}"
            )
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[HELENAgentBase]:
        return self._agents.get(name)

    def all_roles(self) -> frozenset[str]:
        return frozenset(self._agents.keys())

    def status(self) -> dict:
        return {
            name: {
                "alive": agent.alive,
                "queue_depth": agent.inbox.qsize(),
                "packets_handled": agent._packet_count,
            }
            for name, agent in self._agents.items()
        }

    def __len__(self) -> int:
        return len(self._agents)

    def __repr__(self) -> str:
        return f"<HELENAgentRegistry roles={sorted(self._agents)}>"
