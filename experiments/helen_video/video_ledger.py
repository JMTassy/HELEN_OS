"""Video Ledger — append-only hash-chained record of admitted media decisions.

Every entry is immutable once written. Supersession is recorded by appending
a new SUPERSEDED entry, not by editing the old one.

Status values:
  ACCEPTED   — gate approved; delivery engine may use this video
  REJECTED   — gate blocked; never delivered
  PENDING    — gate deferred (insufficient evidence); not yet deliverable
  SUPERSEDED — replaced by a newer ACCEPTED entry with higher receipt score

Only ACCEPTED entries are visible to the delivery engine.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

Status = Literal["ACCEPTED", "REJECTED", "PENDING", "SUPERSEDED"]

GENESIS_HASH = "0" * 64


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _entry_hash(entry_without_id: dict) -> str:
    return _sha256(_canonical(entry_without_id))


def make_entry(
    video_id: str,
    status: Status,
    receipt: dict | None,
    decision_reason: str,
    prev_entry_hash: str,
    ralph_iteration_id: str | None = None,
) -> dict:
    body = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "ralph_iteration_id": ralph_iteration_id,
        "status": status,
        "receipt": receipt,
        "decision_reason": decision_reason,
        "prev_entry_hash": prev_entry_hash,
    }
    body["entry_hash"] = _entry_hash(body)
    return body


class VideoLedger:
    """Append-only video ledger backed by an NDJSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        entries = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def _last_hash(self) -> str:
        entries = self._read_all()
        return entries[-1]["entry_hash"] if entries else GENESIS_HASH

    def append(
        self,
        video_id: str,
        status: Status,
        receipt: dict | None,
        decision_reason: str,
        ralph_iteration_id: str | None = None,
    ) -> dict:
        entry = make_entry(
            video_id=video_id,
            status=status,
            receipt=receipt,
            decision_reason=decision_reason,
            prev_entry_hash=self._last_hash(),
            ralph_iteration_id=ralph_iteration_id,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
        return entry

    def accepted(self) -> list[dict]:
        """Return ACCEPTED entries not superseded by a later entry."""
        entries = self._read_all()
        superseded_ids = {e["video_id"] for e in entries if e["status"] == "SUPERSEDED"}
        return [e for e in entries
                if e["status"] == "ACCEPTED" and e["video_id"] not in superseded_ids]

    def verify_chain(self) -> bool:
        """Verify hash chain integrity. Returns False on any break."""
        entries = self._read_all()
        prev = GENESIS_HASH
        for e in entries:
            stored = e.get("entry_hash")
            body = {k: v for k, v in e.items() if k != "entry_hash"}
            if _entry_hash(body) != stored:
                return False
            if e.get("prev_entry_hash") != prev:
                return False
            prev = stored
        return True

    def supersede(self, video_id: str, reason: str) -> dict | None:
        """Mark an existing ACCEPTED entry as SUPERSEDED (append-only)."""
        entries = self._read_all()
        target = next(
            (e for e in reversed(entries)
             if e["video_id"] == video_id and e["status"] == "ACCEPTED"),
            None,
        )
        if target is None:
            return None
        return self.append(
            video_id=video_id,
            status="SUPERSEDED",
            receipt=target.get("receipt"),
            decision_reason=reason,
        )
