#!/usr/bin/env python3
"""Append-Only Hash-Chained Ledger (Deterministic).

Properties:
- Append-only (entries never modified intentionally)
- Hash-linked (each entry references previous via prev_hash)
- Deterministic hashing (canonical JSON, sorted keys)

Determinism contract (D0):
- Wall-clock timestamps are METADATA.
- They MUST NOT participate in identity hashes.

Implementation notes:
- `canonicalize_for_hash()` is the single source of truth for hashing.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class Ledger:
    """Append-only, hash-chained ledger."""

    # Volatile keys are excluded from identity hashing.
    VOLATILE_KEYS = {"timestamp", "hash"}

    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    @staticmethod
    def canonicalize_for_hash(entry: Dict[str, Any]) -> Dict[str, Any]:
        """Return a deterministic view of the entry for hashing.

        Single source of truth (H1): both append() and verify_chain() must use this.
        """
        return {k: entry[k] for k in sorted(entry.keys()) if k not in Ledger.VOLATILE_KEYS}

    @staticmethod
    def _hash_canonical(payload: Dict[str, Any]) -> str:
        """Deterministic SHA256 over canonical JSON (sorted keys, no whitespace)."""
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def compute_hash(entry: Dict[str, Any]) -> str:
        """Compute deterministic entry hash (excludes volatile keys)."""
        return Ledger._hash_canonical(Ledger.canonicalize_for_hash(entry))

    def append(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Append entry to ledger.

        Adds:
        - timestamp (UTC ISO) [METADATA]
        - prev_hash (chain link) [IDENTITY]
        - hash (entry hash) [IDENTITY]

        Returns augmented entry.
        """
        # Metadata (excluded from hash): keep for observability.
        entry["timestamp"] = datetime.utcnow().isoformat(timespec="microseconds") + "Z"
        entry["prev_hash"] = self.entries[-1]["hash"] if self.entries else None

        entry["hash"] = Ledger.compute_hash(entry)

        self.entries.append(entry)
        return entry

    def export(self, path: str | Path = "ledger.jsonl") -> None:
        """Backwards-compatible alias for export_jsonl()."""
        self.export_jsonl(path)

    def export_jsonl(self, path: str | Path) -> None:
        """Export ledger to JSONL (one entry per line)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "Ledger":
        """Load ledger from JSONL and return a Ledger instance (verifiable)."""
        path = Path(path)
        ledger = cls()
        if not path.exists():
            return ledger
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ledger.entries.append(json.loads(line))
        return ledger

    def deterministic_digest(self) -> str:
        """Digest that is stable across runs under D0 (ignores timestamps)."""
        # The per-entry `hash` is deterministic (timestamp excluded), so chaining them is stable.
        joined = "|".join([e.get("hash", "") for e in self.entries])
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()

    def get_all(self) -> List[Dict[str, Any]]:
        return self.entries

    def get_by_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        return [e for e in self.entries if e.get("namespace") == namespace]

    def get_by_role(self, role: str) -> List[Dict[str, Any]]:
        return [e for e in self.entries if e.get("role") == role]

    def verify_chain(self) -> bool:
        """Verify hash chain integrity (links + recomputation)."""
        for i, entry in enumerate(self.entries):
            # Link check
            if i == 0:
                if entry.get("prev_hash") is not None:
                    return False
            else:
                if entry.get("prev_hash") != self.entries[i - 1].get("hash"):
                    return False

            # Recompute hash
            stored = entry.get("hash")
            if not stored:
                return False
            recomputed = Ledger.compute_hash(entry)
            if stored != recomputed:
                return False

        return True

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return f"Ledger({len(self.entries)} entries, chain_valid={self.verify_chain()})"
