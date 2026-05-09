#!/usr/bin/env python3
"""
HELEN OS → AIRI avatar bridge.

Implements the real AIRI plugin-protocol (plugin-protocol/src/types/events.ts):
  - Auth:      {"type": "module:authenticate", "token": "<token>"}  → module:authenticated
  - Heartbeat: raw "🩵"  →  raw "💛"
  - Witness:   {"type": "spark:notify", ...}  →  character reacts

Runs as a daemon thread with its own asyncio event loop.
Push witness events from any thread via push_witness().
Fail-closed: AIRI offline → events silently drop, Flask never blocks.

authority=NON_SOVEREIGN  canon=NO_SHIP
"""
from __future__ import annotations

import asyncio
import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("helen.airi_bridge")

AIRI_URI       = "ws://localhost:6121/ws"
HELEN_TOKEN    = "helen-os"
RECONNECT_SEC  = 6
QUEUE_MAX      = 64

PING = "🩵"
PONG = "💛"


class AIRIBridge:
    """
    Thread-safe bridge: Flask thread calls push_witness(); asyncio loop delivers.
    """

    def __init__(self, uri: str = AIRI_URI):
        self.uri = uri
        self.connected: bool = False
        self.last_ping: Optional[str] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._aqueue: Optional[asyncio.Queue] = None
        self._thread: Optional[threading.Thread] = None

    # ── public API (thread-safe) ──────────────────────────────────────────────

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="airi-bridge"
        )
        self._thread.start()

    def push_witness(
        self,
        obj_type: str,
        subject: str,
        confidence: float = 0.0,
        provenance: str = "kernel",
    ) -> bool:
        if self._loop is None or self._aqueue is None:
            return False
        msg = {
            "type": "spark:notify",
            "id": f"helen-witness-{uuid.uuid4().hex[:8]}",
            "eventId": uuid.uuid4().hex[:12],
            "kind": "ping",
            "urgency": "soon",
            "headline": f"I witness this {obj_type}.",
            "note": subject[:80],
            "payload": {
                "confidence": round(confidence, 3),
                "provenance": provenance,
                "authority": "NONE",
            },
            "destinations": ["character"],
        }
        try:
            self._loop.call_soon_threadsafe(self._aqueue.put_nowait, msg)
            return True
        except Exception:
            return False

    def status(self) -> dict:
        return {
            "connected": self.connected,
            "last_ping": self.last_ping,
            "uri": self.uri,
            "authority": "NON_SOVEREIGN",
        }

    # ── internal ──────────────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._main())

    async def _main(self) -> None:
        self._aqueue = asyncio.Queue(maxsize=QUEUE_MAX)
        while True:
            try:
                await self._connect()
            except Exception as exc:
                logger.debug(f"AIRI connect error: {exc}")
            finally:
                self.connected = False
            await asyncio.sleep(RECONNECT_SEC)

    async def _connect(self) -> None:
        try:
            import websockets  # type: ignore
        except ImportError:
            logger.warning("websockets not installed — AIRI bridge inactive")
            await asyncio.sleep(3600)
            return

        logger.info(f"AIRI bridge connecting → {self.uri}")
        try:
            async with websockets.connect(self.uri, ping_interval=None) as ws:
                # authenticate
                await ws.send(json.dumps({
                    "type": "module:authenticate",
                    "token": HELEN_TOKEN,
                }))
                self.connected = True
                logger.info("AIRI bridge connected (NON_SOVEREIGN)")

                await asyncio.gather(
                    self._recv(ws),
                    self._send(ws),
                )
        except (ConnectionRefusedError, OSError):
            logger.debug(f"AIRI not reachable at {self.uri}")
        except Exception as exc:
            logger.debug(f"AIRI bridge error: {exc}")

    async def _recv(self, ws) -> None:
        async for raw in ws:
            try:
                if raw == PING:
                    await ws.send(PONG)
                    self.last_ping = datetime.now(timezone.utc).isoformat()
                    continue
                data = json.loads(raw)
                t = data.get("type", "")
                if t == "module:authenticated":
                    logger.info(f"AIRI authenticated: {data}")
                elif t == "transport:connection:heartbeat":
                    if data.get("message") == PING:
                        await ws.send(PONG)
                        self.last_ping = datetime.now(timezone.utc).isoformat()
                else:
                    logger.debug(f"AIRI → HELEN: {t}")
            except json.JSONDecodeError:
                pass
            except Exception as exc:
                logger.debug(f"recv error: {exc}")
                return

    async def _send(self, ws) -> None:
        assert self._aqueue is not None
        while True:
            msg = await self._aqueue.get()
            try:
                await ws.send(json.dumps(msg))
                logger.debug(f"HELEN → AIRI: {msg['type']}")
            except Exception as exc:
                logger.debug(f"send error: {exc}")
                return


# ── module-level singleton (imported by server.py) ────────────────────────────

_bridge: Optional[AIRIBridge] = None


def get_bridge() -> AIRIBridge:
    global _bridge
    if _bridge is None:
        _bridge = AIRIBridge()
        _bridge.start()
    return _bridge
