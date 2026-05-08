"""
HELEN Terminal — action receipt builder.
Every terminal action emits a receipt. NO RECEIPT = NO CLAIM.
authority=NON_SOVEREIGN  canon=NO_SHIP
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RECEIPTS_DIR = Path(__file__).resolve().parent.parent / "data" / "receipts"
LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "ledger.ndjson"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(obj: Any) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:24]


def build_receipt(
    action_type: str,
    action_params: dict,
    artifact: dict,
    verified: bool = True,
) -> dict:
    base = {
        "action_type": action_type,
        "action_params": action_params,
        "artifact_hash": _hash(artifact),
        "artifact_preview": str(artifact.get("content_preview", ""))[:200],
        "verified": verified,
        "verifier": "HELEN_TERMINAL_HAL_V0",
        "timestamp_utc": _now(),
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
    }
    receipt_id = "RT-" + _hash(base)
    receipt = {"receipt_id": receipt_id, **base}
    _persist(receipt)
    return receipt


def _persist(receipt: dict) -> None:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS_DIR / f"{receipt['receipt_id']}.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    _append_ledger(receipt)


def _append_ledger(receipt: dict) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    events = []
    if LEDGER_PATH.exists():
        for line in LEDGER_PATH.read_text().splitlines():
            if line.strip():
                events.append(json.loads(line))
    prev_hash = events[-1]["event_hash"] if events else "GENESIS"
    event_base = {
        "event_id": "TE-" + uuid.uuid4().hex[:12],
        "event_type": "TERMINAL_ACTION",
        "timestamp_utc": _now(),
        "prev_hash": prev_hash,
        "payload_hash": _hash(receipt),
        "payload": {"receipt_id": receipt["receipt_id"], "action_type": receipt["action_type"]},
    }
    event_base["event_hash"] = _hash(event_base)
    with LEDGER_PATH.open("a") as f:
        f.write(json.dumps(event_base, sort_keys=True, separators=(",", ":")) + "\n")
