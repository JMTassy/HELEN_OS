"""
tests/test_receipt_linkage.py

Receipt triad binding invariant:
  A receipt is valid only when it binds ALL THREE:
    leg 1: refs.ref_verdict_payload_hash_hex == VERDICT_event.payload_hash
    leg 2: refs.ref_verdict_cum_hash_hex      == VERDICT_event.cum_hash
    leg 3: recomputed.verdict_payload_hash_hex == refs.ref_verdict_payload_hash_hex

NO RECEIPT = NO SHIP:
  Every VERDICT with verdict_kind == "SHIP" must have at least one RECEIPT bound to it.
"""
import hashlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kernel.canonical_json import canon_json_bytes
from tools.validate_receipt_linkage import validate_receipt_linkage

HELEN_CUM_V1_PREFIX = b"HELEN_CUM_V1"
GENESIS_HASH = "0" * 64


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon_payload_hash(payload: dict) -> str:
    return sha256_hex(canon_json_bytes(payload))


def chain_hash_v1(prev_hex: str, ph_hex: str) -> str:
    return sha256_hex(
        HELEN_CUM_V1_PREFIX + bytes.fromhex(prev_hex) + bytes.fromhex(ph_hex)
    )


def make_verdict_event(seq: int, verdict_id: str, kind: str, prev_cum: str) -> dict:
    payload = {
        "schema": "VERDICT_PAYLOAD_V1",
        "verdict_id": verdict_id,
        "verdict_kind": kind,
    }
    ph = canon_payload_hash(payload)
    ch = chain_hash_v1(prev_cum, ph)
    return {
        "seq": seq,
        "type": "VERDICT",
        "payload": payload,
        "payload_hash": ph,
        "prev_cum_hash": prev_cum,
        "cum_hash": ch,
    }


def make_receipt_event(seq: int, verdict_event: dict, prev_cum: str) -> dict:
    payload = {
        "schema": "RECEIPT_PAYLOAD_V1",
        "refs": {
            "verdict_id": verdict_event["payload"]["verdict_id"],
            "ref_verdict_payload_hash_hex": verdict_event["payload_hash"],
            "ref_verdict_cum_hash_hex": verdict_event["cum_hash"],
        },
    }
    ph = canon_payload_hash(payload)
    ch = chain_hash_v1(prev_cum, ph)
    return {
        "seq": seq,
        "type": "RECEIPT",
        "payload": payload,
        "payload_hash": ph,
        "prev_cum_hash": prev_cum,
        "cum_hash": ch,
    }


def as_indexed(events: list[dict]) -> list[tuple]:
    """Wrap events as (line_num, obj) tuples as expected by validate_receipt_linkage."""
    return [(i + 1, ev) for i, ev in enumerate(events)]


# ── Valid binding ─────────────────────────────────────────────────────────────

def test_valid_receipt_verdict_pair_passes():
    """A correctly formed RECEIPT bound to a SHIP VERDICT must pass."""
    v = make_verdict_event(0, "VID_001", "SHIP", GENESIS_HASH)
    r = make_receipt_event(1, v, v["cum_hash"])
    result = validate_receipt_linkage(as_indexed([v, r]))
    assert result == (1, 1)


def test_no_ship_verdict_without_receipt_passes():
    """A NO_SHIP verdict without a receipt must pass (only SHIP requires receipt)."""
    v = make_verdict_event(0, "VID_002", "NO_SHIP", GENESIS_HASH)
    result = validate_receipt_linkage(as_indexed([v]))
    assert result[0] == 1


# ── Leg 1: ref_verdict_payload_hash_hex mismatch ─────────────────────────────

def test_wrong_ref_verdict_payload_hash_rejected():
    """Receipt with wrong ref_verdict_payload_hash_hex must be rejected (leg 1)."""
    v = make_verdict_event(0, "VID_003", "SHIP", GENESIS_HASH)
    r = make_receipt_event(1, v, v["cum_hash"])

    # Break leg 1
    r["payload"]["refs"]["ref_verdict_payload_hash_hex"] = "a" * 64
    r["payload_hash"] = canon_payload_hash(r["payload"])

    with pytest.raises(ValueError, match="leg 1"):
        validate_receipt_linkage(as_indexed([v, r]))


# ── Leg 2: ref_verdict_cum_hash_hex mismatch ─────────────────────────────────

def test_wrong_ref_verdict_cum_hash_rejected():
    """Receipt with wrong ref_verdict_cum_hash_hex must be rejected (leg 2)."""
    v = make_verdict_event(0, "VID_004", "SHIP", GENESIS_HASH)
    r = make_receipt_event(1, v, v["cum_hash"])

    # Break leg 2
    r["payload"]["refs"]["ref_verdict_cum_hash_hex"] = "b" * 64
    r["payload_hash"] = canon_payload_hash(r["payload"])

    with pytest.raises(ValueError, match="leg 2"):
        validate_receipt_linkage(as_indexed([v, r]))


# ── NO RECEIPT = NO SHIP ──────────────────────────────────────────────────────

def test_ship_without_receipt_raises():
    """SHIP verdict with no bound RECEIPT must be rejected."""
    v = make_verdict_event(0, "VID_005", "SHIP", GENESIS_HASH)
    with pytest.raises(ValueError, match="NO RECEIPT|SHIP"):
        validate_receipt_linkage(as_indexed([v]))


def test_ship_with_receipt_passes():
    """SHIP verdict with valid RECEIPT must pass."""
    v = make_verdict_event(0, "VID_006", "SHIP", GENESIS_HASH)
    r = make_receipt_event(1, v, v["cum_hash"])
    result = validate_receipt_linkage(as_indexed([v, r]))
    assert result == (1, 1)


# ── Multiple verdicts ─────────────────────────────────────────────────────────

def test_two_ship_verdicts_first_has_receipt_second_does_not():
    """Two SHIP verdicts: first receipted, second not → must fail."""
    v1 = make_verdict_event(0, "VID_007", "SHIP", GENESIS_HASH)
    r1 = make_receipt_event(1, v1, v1["cum_hash"])
    v2 = make_verdict_event(2, "VID_008", "SHIP", r1["cum_hash"])
    with pytest.raises(ValueError, match="NO RECEIPT|SHIP"):
        validate_receipt_linkage(as_indexed([v1, r1, v2]))


def test_empty_event_list_passes():
    """No events → nothing to validate."""
    result = validate_receipt_linkage([])
    assert result == (0, 0)


def test_receipt_for_unknown_verdict_id_raises():
    """RECEIPT referencing a verdict_id that doesn't exist must raise."""
    # A receipt with no corresponding verdict event
    payload = {
        "schema": "RECEIPT_PAYLOAD_V1",
        "refs": {
            "verdict_id": "VID_GHOST",
            "ref_verdict_payload_hash_hex": "c" * 64,
            "ref_verdict_cum_hash_hex": "d" * 64,
        },
    }
    ph = canon_payload_hash(payload)
    ch = chain_hash_v1(GENESIS_HASH, ph)
    orphan_receipt = {
        "seq": 0, "type": "RECEIPT",
        "payload": payload, "payload_hash": ph,
        "prev_cum_hash": GENESIS_HASH, "cum_hash": ch,
    }
    with pytest.raises(ValueError, match="VID_GHOST|not found"):
        validate_receipt_linkage(as_indexed([orphan_receipt]))
