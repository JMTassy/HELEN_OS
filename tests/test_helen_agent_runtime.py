"""
tests/test_helen_agent_runtime.py — HELEN OS Agent Runtime tests
NON_SOVEREIGN · authority=false · canon=NO_SHIP
"""

import time
import threading
import pytest

from src.helen_agent_base import HELENAgentBase, WULPacket, CANONICAL_ROLES
from src.helen_agent_registry import HELENAgentRegistry
from src.helen_orchestrator import HELENOrchestrator, RoutingError


# ── fixtures ──────────────────────────────────────────────────────────────────

class HALAgent(HELENAgentBase):
    """Minimal HAL agent that records handled packets for test inspection."""
    ROLE = "HAL"

    def __init__(self, tmp_path):
        super().__init__("HAL", receipt_dir=tmp_path / "receipts")
        self.handled: list[dict] = []

    def handle(self, packet: dict):
        self.handled.append(packet)
        return self._ack_receipt(packet)


class HERAgent(HELENAgentBase):
    ROLE = "HER"

    def __init__(self, tmp_path):
        super().__init__("HER", receipt_dir=tmp_path / "receipts")


# ── agent base tests ──────────────────────────────────────────────────────────

def test_agent_rejects_unknown_role(tmp_path):
    with pytest.raises(ValueError, match="Unknown agent role"):
        HELENAgentBase("UNKNOWN_ROLE", receipt_dir=tmp_path)


def test_agent_accepts_canonical_roles(tmp_path):
    for role in CANONICAL_ROLES:
        agent = HELENAgentBase(role, receipt_dir=tmp_path / role)
        assert agent.name == role


def test_agent_starts_and_is_alive(tmp_path):
    agent = HELENAgentBase("HER", receipt_dir=tmp_path)
    agent.start()
    time.sleep(0.1)
    assert agent.alive
    agent.stop()


def test_agent_stops_cleanly(tmp_path):
    agent = HELENAgentBase("DAN", receipt_dir=tmp_path)
    agent.start()
    time.sleep(0.1)
    agent.stop()
    assert not agent._running


def test_agent_emits_receipt_on_packet(tmp_path):
    agent = HALAgent(tmp_path)
    agent.start()

    agent.send({"packet_id": "test-001", "intent": "GATE_CHECK", "payload": {}})
    time.sleep(0.3)

    agent.stop()
    receipts = list((tmp_path / "receipts").glob("HAL_*.json"))
    assert len(receipts) == 1


def test_receipt_is_non_sovereign(tmp_path):
    import json
    agent = HALAgent(tmp_path)
    agent.start()

    agent.send({"packet_id": "test-002", "intent": "GATE_CHECK", "payload": {}})
    time.sleep(0.3)
    agent.stop()

    receipts = list((tmp_path / "receipts").glob("HAL_*.json"))
    data = json.loads(receipts[0].read_text())
    assert data["authority"] is False
    assert data["canon"] == "NO_SHIP"


# ── registry tests ────────────────────────────────────────────────────────────

def test_registry_register_and_get(tmp_path):
    registry = HELENAgentRegistry()
    agent = HELENAgentBase("HAL", receipt_dir=tmp_path)
    registry.register(agent)
    assert registry.get("HAL") is agent


def test_registry_rejects_unknown_role(tmp_path):
    registry = HELENAgentRegistry()

    class BadAgent(HELENAgentBase):
        pass

    with pytest.raises(ValueError):
        bad = object.__new__(HELENAgentBase)
        bad.name = "INVALID"
        bad.inbox = __import__("queue").Queue()
        bad._running = False
        bad._heartbeat_ts = 0.0
        bad._packet_count = 0
        registry.register(bad)


def test_registry_status_reports_liveness(tmp_path):
    registry = HELENAgentRegistry()
    agent = HELENAgentBase("AURA", receipt_dir=tmp_path)
    registry.register(agent)
    agent.start()
    time.sleep(0.1)

    status = registry.status()
    assert "AURA" in status
    assert status["AURA"]["alive"] is True
    agent.stop()


# ── orchestrator tests ────────────────────────────────────────────────────────

def test_orchestrator_routes_packet(tmp_path):
    orch = HELENOrchestrator(receipt_dir=tmp_path / "receipts")
    hal = HALAgent(tmp_path)
    orch.register(hal)

    packet_id = orch.route("HER", "HAL", "GATE_CHECK", {"claim": "test"})
    time.sleep(0.3)

    orch.stop_all()
    assert len(hal.handled) == 1
    assert hal.handled[0]["packet_id"] == packet_id


def test_orchestrator_raises_on_missing_recipient(tmp_path):
    orch = HELENOrchestrator(receipt_dir=tmp_path / "receipts")
    with pytest.raises(RoutingError, match="No agent registered"):
        orch.route("HER", "HAL", "GATE_CHECK", {})


def test_orchestrator_routes_her_to_hal_roundtrip(tmp_path):
    orch = HELENOrchestrator(receipt_dir=tmp_path / "receipts")
    hal = HALAgent(tmp_path)
    her = HERAgent(tmp_path)
    orch.register(hal)
    orch.register(her)

    packet_id = orch.route("HER", "HAL", "GATE_CHECK", {"intent": "check authority"})
    time.sleep(0.3)

    orch.stop_all()
    assert hal.handled[0]["sender"] == "HER"
    assert hal.handled[0]["recipient"] == "HAL"
    receipts = list((tmp_path / "receipts").glob("HAL_*.json"))
    assert len(receipts) >= 1


def test_orchestrator_status_is_non_sovereign(tmp_path):
    orch = HELENOrchestrator(receipt_dir=tmp_path / "receipts")
    status = orch.status()
    assert status["authority"] is False
    assert status["canon"] == "NO_SHIP"


def test_orchestrator_stop_all(tmp_path):
    orch = HELENOrchestrator(receipt_dir=tmp_path / "receipts")
    hal = HALAgent(tmp_path)
    her = HERAgent(tmp_path)
    orch.register(hal)
    orch.register(her)

    time.sleep(0.1)
    orch.stop_all()
    assert not hal._running
    assert not her._running


def test_wul_packet_dataclass(tmp_path):
    pkt = WULPacket(sender="HER", recipient="HAL", intent="GATE_CHECK", payload={"x": 1})
    d = pkt.to_dict()
    assert d["authority"] is False
    assert d["canon"] == "NO_SHIP"
    assert d["sender"] == "HER"
    assert d["recipient"] == "HAL"
