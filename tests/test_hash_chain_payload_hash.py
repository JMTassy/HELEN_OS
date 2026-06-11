"""
tests/test_hash_chain_payload_hash.py

Pinned invariant: payload_hash = SHA256(CANON_JSON_V1(payload))

Validators must recompute the hash from the payload bytes.
Trusting a stored hash without recomputation is a constitutional violation.

These tests exercise validate_hash_chain.validate() (production path) and
directly verify the recomputation law.
"""
import hashlib
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kernel.canonical_json import canon_json_bytes

HELEN_CUM_V1_PREFIX = b"HELEN_CUM_V1"
GENESIS_HASH = "0" * 64


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon_payload_hash(payload: dict) -> str:
    return sha256_hex(canon_json_bytes(payload))


def chain_hash_v1(prev_hex: str, payload_hash_hex: str) -> str:
    return sha256_hex(
        HELEN_CUM_V1_PREFIX
        + bytes.fromhex(prev_hex)
        + bytes.fromhex(payload_hash_hex)
    )


def make_event(seq: int, payload: dict, prev_cum_hash: str) -> dict:
    ph = canon_payload_hash(payload)
    ch = chain_hash_v1(prev_cum_hash, ph)
    return {
        "seq": seq,
        "payload": payload,
        "payload_hash": ph,
        "prev_cum_hash": prev_cum_hash,
        "cum_hash": ch,
    }


def write_ledger(events: list[dict]) -> str:
    fd, path = tempfile.mkstemp(suffix=".ndjson")
    with os.fdopen(fd, "w") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return path


# ── Recomputation law: SHA256(CANON_JSON_V1(payload)) ────────────────────────

def test_canonical_hash_is_deterministic():
    """Same payload always produces same hash — canonical JSON is stable."""
    p = {"key": "value", "num": 42, "nested": {"a": 1}}
    h1 = canon_payload_hash(p)
    h2 = canon_payload_hash(p)
    assert h1 == h2


def test_canonical_hash_is_order_independent():
    """Key insertion order in payload must not change hash (sort_keys semantics)."""
    p1 = {"b": 2, "a": 1}
    p2 = {"a": 1, "b": 2}
    assert canon_payload_hash(p1) == canon_payload_hash(p2)


def test_payload_mutation_changes_hash():
    """Mutating any payload field must produce a different hash."""
    p_original = {"action": "test", "value": 1}
    p_mutated = {"action": "test", "value": 2}
    assert canon_payload_hash(p_original) != canon_payload_hash(p_mutated)


def test_tampered_payload_hash_mismatch():
    """Stored payload_hash that doesn't match recomputed hash must be detected."""
    payload = {"event": "created", "id": "X1"}
    correct_ph = canon_payload_hash(payload)
    tampered_ph = "0" * 64

    # The stored hash doesn't match what recomputing from payload gives
    assert correct_ph != tampered_ph
    assert sha256_hex(canon_json_bytes(payload)) == correct_ph


def test_validator_detects_tampered_payload(tmp_path):
    """validate_hash_chain must reject an event whose payload was changed after hashing."""
    from tools.validate_hash_chain import main as validate_main
    import io, contextlib

    payload = {"event": "test", "v": 1}
    event = make_event(0, payload, GENESIS_HASH)

    # Tamper: change payload content without updating payload_hash
    tampered = dict(event)
    tampered["payload"] = {"event": "TAMPERED", "v": 999}

    ledger_path = str(tmp_path / "tampered.ndjson")
    with open(ledger_path, "w") as f:
        f.write(json.dumps(tampered) + "\n")

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf), pytest.raises(SystemExit) as exc:
        validate_main(ledger_path, scheme_override="HELEN_CUM_V1")

    assert exc.value.code != 0
    assert "payload_hash" in buf.getvalue() or "mismatch" in buf.getvalue()


def test_validator_accepts_correct_chain(tmp_path):
    """validate_hash_chain must accept a correctly formed 3-event chain."""
    from tools.validate_hash_chain import main as validate_main
    import io, contextlib

    events = []
    prev = GENESIS_HASH
    for i in range(3):
        ev = make_event(i, {"step": i, "data": f"event_{i}"}, prev)
        events.append(ev)
        prev = ev["cum_hash"]

    ledger_path = str(tmp_path / "valid.ndjson")
    with open(ledger_path, "w") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        validate_main(ledger_path, scheme_override="HELEN_CUM_V1")

    assert "PASS" in buf.getvalue()


def test_validator_detects_broken_cum_hash_chain(tmp_path):
    """validate_hash_chain must reject event whose cum_hash is wrong."""
    from tools.validate_hash_chain import main as validate_main
    import io, contextlib

    payload = {"event": "test"}
    event = make_event(0, payload, GENESIS_HASH)

    # Break the cum_hash
    broken = dict(event)
    broken["cum_hash"] = "f" * 64

    ledger_path = str(tmp_path / "broken_cum.ndjson")
    with open(ledger_path, "w") as f:
        f.write(json.dumps(broken) + "\n")

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf), pytest.raises(SystemExit) as exc:
        validate_main(ledger_path, scheme_override="HELEN_CUM_V1")

    assert exc.value.code != 0
    assert "cum_hash" in buf.getvalue() or "mismatch" in buf.getvalue()
