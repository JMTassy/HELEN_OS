#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDJSON Writer — ENVIRONMENT-SOVEREIGN Hash Scheme

Implements payload/meta split with environment-driven cumulative hashing.
Enforces: no floats in payload, sorted keys, canonical JSON.

Hash scheme: HELEN_CUM_V1 (via registries/environment.v1.json)
  cum_hash = SHA256(b"HELEN_CUM_V1" || bytes(prev_hex) || bytes(payload_hex))
  Input: 12 + 32 + 32 = 76 bytes

Environment is sovereign. Writer reads scheme from registries/environment.v1.json.
No component may hardcode a scheme or guess.

Must agree with: kernel/hash_util.ml — Hash_util.concat
Reference: PAYLOAD_META_WRITER_SPEC.md, HASH_SCHEME_ACTIVATION_PROTOCOL.md
"""

import json
import hashlib
import sys
import os as _os
_repo_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
from kernel.canonical_json import canon_json_bytes
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable

# Platform-safe file locking
try:
    import fcntl as _fcntl
    _HAS_FCNTL = True
except ImportError:
    _HAS_FCNTL = False
    import warnings as _warnings
    _warnings.warn(
        "fcntl not available on this platform — NDJSONWriter will operate without exclusive "
        "file locking. Concurrent writers may produce duplicate seq values.",
        RuntimeWarning,
        stacklevel=1,
    )

# ──────────────────────────────────────────────────────────────────────────────
# Hash scheme support — both V0 and V1 implemented
# ──────────────────────────────────────────────────────────────────────────────

# HELEN_CUM_V1 domain separator — HARDCODED BYTE LITERAL (never dynamic)
# OCaml: Bytes.of_string "HELEN_CUM_V1"  (kernel/hash_util.ml, line 65)
# 12 ASCII bytes. No trailing whitespace. No encoding variation.
HELEN_CUM_V1_PREFIX: bytes = b"HELEN_CUM_V1"

_ENV_PATH = _os.path.join(_repo_root, "registries", "environment.v1.json")
HEX64_ZERO = "0" * 64


def _is_int(x: Any) -> bool:
    """Check if x is an int (not bool)."""
    return isinstance(x, int) and not isinstance(x, bool)


def assert_no_floats(x: Any, path: str = "$") -> None:
    """Recursively check that governance payload contains no floats."""
    if isinstance(x, float):
        raise ValueError(f"Float forbidden in payload at {path}. Use canonical string.")
    if isinstance(x, dict):
        for k, v in x.items():
            assert_no_floats(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            assert_no_floats(v, f"{path}[{i}]")


def sha256_hex(b: bytes) -> str:
    """SHA256 hash of bytes, return as hex string."""
    return hashlib.sha256(b).hexdigest()


def load_hash_scheme() -> str:
    """
    Load hash_scheme from registries/environment.v1.json.

    Environment is sovereign. No component may hardcode or guess.
    Raises ValueError if environment file is missing or scheme is invalid.
    """
    try:
        with open(_ENV_PATH, "r", encoding="utf-8") as f:
            env = json.load(f)
    except FileNotFoundError:
        raise ValueError(
            f"Environment file not found: {_ENV_PATH}\n"
            "Cannot create ledger without explicit hash scheme declaration.\n"
            "Environment is sovereign."
        )

    scheme = env.get("hash_scheme")
    if not scheme:
        raise ValueError(
            f"hash_scheme field missing from {_ENV_PATH}\n"
            "Environment is sovereign — hash_scheme must be declared."
        )

    if scheme not in ("HELEN_CUM_V1", "CUM_SCHEME_V0"):
        raise ValueError(
            f"Unknown hash_scheme: {scheme!r}\n"
            "Expected 'HELEN_CUM_V1' or 'CUM_SCHEME_V0'."
        )

    return scheme


# ──────────────────────────────────────────────────────────────────────────────
# Hash scheme implementations (environment-selectable)
# ──────────────────────────────────────────────────────────────────────────────

def _cum_hash_v0(prev_hex: str, payload_hex: str) -> str:
    """
    CUM_SCHEME_V0 — no domain separation (historical).

    cum_hash = SHA256(bytes(prev_hex) || bytes(payload_hex))
    Input: 32 + 32 = 64 bytes.

    Use only if environment explicitly declares CUM_SCHEME_V0.
    """
    prev_b = bytes.fromhex(prev_hex)
    payl_b = bytes.fromhex(payload_hex)
    return sha256_hex(prev_b + payl_b)


def _cum_hash_v1(prev_hex: str, payload_hex: str) -> str:
    """
    HELEN_CUM_V1 — domain-separated (all new ledgers).

    cum_hash = SHA256(b"HELEN_CUM_V1" || bytes(prev_hex) || bytes(payload_hex))
    Input: 12 + 32 + 32 = 76 bytes.

    INVARIANT: Must produce byte-identical output to OCaml Hash_util.concat.
    PREFIX is HELEN_CUM_V1_PREFIX — hardcoded byte literal, never dynamic.

    Use if environment declares HELEN_CUM_V1.
    """
    prev_b = bytes.fromhex(prev_hex)
    payl_b = bytes.fromhex(payload_hex)
    return sha256_hex(HELEN_CUM_V1_PREFIX + prev_b + payl_b)


def get_hash_fn(scheme: str) -> Callable[[str, str], str]:
    """Return the cum_hash function for the given scheme."""
    if scheme == "HELEN_CUM_V1":
        return _cum_hash_v1
    elif scheme == "CUM_SCHEME_V0":
        return _cum_hash_v0
    else:
        raise ValueError(f"Unknown scheme: {scheme!r}")


def sha256_hex_from_hexbytes_concat(prev_hex: str, payload_hex: str) -> str:
    """
    DEPRECATED: Use NDJSONWriter which is environment-sovereign.

    This function is kept for backward compatibility only.
    It hardcodes HELEN_CUM_V1, which violates the principle that
    environment is sovereign.

    New code must use NDJSONWriter instead.
    """
    # Fallback: read environment and use it
    scheme = load_hash_scheme()
    hash_fn = get_hash_fn(scheme)
    return hash_fn(prev_hex, payload_hex)


@dataclass
class NDJSONWriter:
    """
    NDJSON writer with payload/meta split and environment-sovereign cumulative hashing.

    Hash scheme is read from registries/environment.v1.json at initialization.
    Environment is sovereign. No hardcoding. No guessing.

    Every append_event() call:
      1. Validates no floats in payload
      2. Computes payload_hash = SHA256(Canon(payload))
      3. Computes cum_hash using environment-declared scheme
      4. Writes one NDJSON line
      5. Updates seq and prev_cum_hash for next call

    Genesis: seq=0, prev_cum_hash="0"*64
    """

    path: str
    seq: int = 0
    prev_cum_hash: str = HEX64_ZERO
    _hash_fn: Callable[[str, str], str] = None  # Cached hash function
    _scheme: str = None  # Cached scheme name

    def __post_init__(self):
        """Initialize hash function from environment."""
        if self._hash_fn is None:  # Only initialize once
            self._scheme = load_hash_scheme()
            self._hash_fn = get_hash_fn(self._scheme)
            print(
                f"[INFO] NDJSONWriter initialized with scheme={self._scheme}",
                file=sys.stderr
            )

    def _read_tail_under_fd(self, fd) -> tuple:
        """
        Re-read the on-disk tail of the file through an already-open fd.

        Must be called while holding an exclusive lock on fd so that the read
        and the subsequent write are atomic with respect to other writers.

        Returns (last_seq, last_cum_hash) using the same semantics as
        tail_prev_state(): for an empty file returns (None, HEX64_ZERO)
        so the caller can distinguish "genesis" from "seq=0 exists".
        """
        try:
            _os.lseek(fd, 0, _os.SEEK_END)
            size = _os.lseek(fd, 0, _os.SEEK_CUR)
            if size == 0:
                return None, HEX64_ZERO
            read_start = max(0, size - 65536)
            _os.lseek(fd, read_start, _os.SEEK_SET)
            raw = _os.read(fd, min(65536, size))
        except OSError:
            return None, HEX64_ZERO

        chunk = raw.decode("utf-8", "replace").strip().splitlines()
        for line in reversed(chunk):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if isinstance(ev, dict) and "seq" in ev and "cum_hash" in ev:
                    return int(ev["seq"]), str(ev["cum_hash"])
            except Exception:
                continue
        return None, HEX64_ZERO

    def append_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Append event to NDJSON file with exclusive file locking.

        Acquires an exclusive lock (fcntl.LOCK_EX on POSIX), re-reads the
        on-disk tail under the lock to get the authoritative (seq, prev_cum_hash),
        then writes.  This prevents two concurrent processes from allocating the
        same seq even if both read the tail before either writes.

        Hash scheme is determined by environment at writer initialization.
        Payload is hash-bound (floats forbidden). Meta is observational.

        Args:
            event_type: "turn", "milestone", "seal", etc.
            payload: Hash-bound deterministic fields (no floats)
            meta: Observational fields (timestamp, notes, etc.)

        Returns:
            Full record dict (for testing/inspection), including seq,
            payload_hash, cum_hash, and prev_cum_hash as written.
        """
        if meta is None:
            meta = {}

        # HARD CONSTRAINT: No floats in payload
        assert_no_floats(payload)

        # Compute payload_hash via canonical JSON (independent of seq/chain state)
        payload_bytes = canon_json_bytes(payload)
        payload_hash = sha256_hex(payload_bytes)

        # Open file for appending (creates if absent)
        raw_fd = _os.open(self.path, _os.O_RDWR | _os.O_CREAT | _os.O_APPEND, 0o644)
        try:
            # Acquire exclusive lock — blocks until all other writers release
            if _HAS_FCNTL:
                _fcntl.flock(raw_fd, _fcntl.LOCK_EX)

            # Re-read tail under lock — authoritative seq allocation
            last_seq, last_cum = self._read_tail_under_fd(raw_fd)
            if last_seq is None:
                # File is empty (genesis)
                authoritative_seq = 0
                authoritative_prev_cum = HEX64_ZERO
            else:
                authoritative_seq = last_seq + 1
                authoritative_prev_cum = last_cum

            # Compute cum_hash using authoritative prev_cum (not constructor-supplied)
            cum_hash = self._hash_fn(authoritative_prev_cum, payload_hash)

            # Build record
            record = {
                "type": event_type,
                "seq": authoritative_seq,
                "payload": payload,
                "meta": meta,
                "payload_hash": payload_hash,
                "prev_cum_hash": authoritative_prev_cum,
                "cum_hash": cum_hash,
            }

            # Write one NDJSON line (canonical JSON + LF)
            line = (canon_json_bytes(record).decode("utf-8") + "\n").encode("utf-8")
            # Seek to end before writing (O_APPEND guarantees this, but be explicit)
            _os.lseek(raw_fd, 0, _os.SEEK_END)
            _os.write(raw_fd, line)

        finally:
            if _HAS_FCNTL:
                _fcntl.flock(raw_fd, _fcntl.LOCK_UN)
            _os.close(raw_fd)

        # Update instance state to reflect written record (for callers that
        # chain multiple append_event() calls on the same writer instance)
        self.seq = authoritative_seq + 1
        self.prev_cum_hash = cum_hash

        return record
