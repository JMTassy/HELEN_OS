"""
helen_agent_base.py — HELEN OS Agent Runtime Base · NON_SOVEREIGN
authority=false, canon=NO_SHIP
"""

from __future__ import annotations

import hashlib
import json
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


CANONICAL_ROLES = frozenset({"AURA", "HER", "HAL", "DAN", "GOBLIN", "RALPH"})


@dataclass
class WULPacket:
    sender: str
    recipient: str
    intent: str
    payload: dict
    packet_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    authority: bool = False
    canon: str = "NO_SHIP"
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "packet_id": self.packet_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "intent": self.intent,
            "payload": self.payload,
            "authority": self.authority,
            "canon": self.canon,
            "ts": self.ts,
        }


class HELENAgentBase:
    """
    Base class for all HELEN OS agents.

    Each agent:
    - Has a named role (must be in CANONICAL_ROLES)
    - Runs in its own daemon thread
    - Receives WUL packets via inbox queue
    - Emits a receipt JSON for every packet handled
    - Reports heartbeat; orchestrator can check liveness
    """

    ROLE: str = "BASE"

    def __init__(self, name: str, receipt_dir: Path | str = "receipts/agents") -> None:
        if name not in CANONICAL_ROLES:
            raise ValueError(f"Unknown agent role: {name!r}. Must be one of {sorted(CANONICAL_ROLES)}")
        self.name = name
        self.inbox: queue.Queue[dict] = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._heartbeat_ts: float = 0.0
        self._packet_count = 0
        self.receipt_dir = Path(receipt_dir)
        self.receipt_dir.mkdir(parents=True, exist_ok=True)

    # ── lifecycle ──────────────────────────────────────────────────────────────

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name=self.name
        )
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=timeout)

    # ── messaging ─────────────────────────────────────────────────────────────

    def send(self, packet: dict) -> None:
        self.inbox.put(packet)

    def _run_loop(self) -> None:
        while self._running:
            self._heartbeat_ts = time.monotonic()
            try:
                packet = self.inbox.get(timeout=0.5)
                receipt = self.handle(packet)
                if receipt:
                    self._emit_receipt(receipt)
            except queue.Empty:
                continue

    def handle(self, packet: dict) -> Optional[dict]:
        """Override in subclasses. Return a receipt dict or None."""
        return self._ack_receipt(packet)

    # ── receipts ──────────────────────────────────────────────────────────────

    def _ack_receipt(self, packet: dict) -> dict:
        return {
            "kind": "agent_ack",
            "agent": self.name,
            "role": self.ROLE,
            "packet_id": packet.get("packet_id", "unknown"),
            "authority": False,
            "canon": "NO_SHIP",
            "ts": time.time(),
        }

    def _emit_receipt(self, receipt: dict) -> Path:
        self._packet_count += 1
        canon = json.dumps(receipt, sort_keys=True)
        h = hashlib.sha256(canon.encode()).hexdigest()[:12]
        receipt["receipt_hash"] = h
        path = self.receipt_dir / f"{self.name}_{self._packet_count:04d}_{h}.json"
        path.write_text(json.dumps(receipt, indent=2))
        return path

    # ── liveness ──────────────────────────────────────────────────────────────

    @property
    def alive(self) -> bool:
        return self._running and (time.monotonic() - self._heartbeat_ts) < 2.0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} alive={self.alive}>"
