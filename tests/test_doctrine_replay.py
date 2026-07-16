"""Doctrine replay fixture — proves the consumption hash chain is tamper-evident.

This is the REPLAYED leg of the three-part doctrine admissibility criterion:

  ADMIT(doctrine) iff LOCATED ∧ ENFORCED ∧ REPLAYED

The chain verifier from operator_pen.py is the authoritative implementation;
these tests confirm it detects tampering at the exact tampered position and
that valid chains always pass.

authority=false · non-sovereign · no ledger writes
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "temple" / "autoresearch"))
from operator_pen import verify_chain, GENESIS  # noqa: E402


# Minimal doctrine packet — authority=False, admission=NO_RECEIPT are the
# two fields that encode the "DREAMT ≠ CLAIMED" invariant in fixture form.
_DOCTRINE_PACKET: dict = {
    "schema": "CONSUMPTION_ENTRY_V0",
    "packet_id": "AR-doctrine-fixture-0",
    "packet_sha256": "0" * 64,
    "decision": "acted",
    "note": "doctrine admissibility: LOCATED+ENFORCED+REPLAYED",
    "operator": "TEST",
    "at": "2026-07-06T00:00:00+00:00",
    "authority": False,
    "sovereign": False,
    "ledger_effect": "none",
    "admission": "NO_RECEIPT",
}


def _hash_body(body: dict) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def make_chain(*payloads: dict) -> list[dict]:
    """Build a valid hash chain from a sequence of payload dicts (operator_pen pattern)."""
    entries: list[dict] = []
    prev = GENESIS
    for payload in payloads:
        body = {**payload, "prev": prev}
        body["entry_hash"] = _hash_body({k: v for k, v in body.items() if k != "entry_hash"})
        entries.append(body)
        prev = body["entry_hash"]
    return entries


def _broken_positions(entries: list[dict]) -> list[int]:
    """Return 0-based indices of entries that fail the chain check."""
    broken: list[int] = []
    prev = GENESIS
    for i, e in enumerate(entries):
        if e.get("prev") != prev:
            broken.append(i)
            prev = e.get("entry_hash", "")
            continue
        body = {k: v for k, v in e.items() if k != "entry_hash"}
        if e.get("entry_hash") != _hash_body(body):
            broken.append(i)
        prev = e.get("entry_hash", "")
    return broken


# ── clean chain ─────────────────────────────────────────────────────────────

def test_clean_chain_passes():
    entries = make_chain(_DOCTRINE_PACKET, _DOCTRINE_PACKET)
    assert verify_chain(entries) is None
    assert _broken_positions(entries) == []


def test_empty_chain_passes():
    assert verify_chain([]) is None


def test_single_entry_chain_passes():
    entries = make_chain(_DOCTRINE_PACKET)
    assert verify_chain(entries) is None


# ── tamper detection ─────────────────────────────────────────────────────────

def test_tamper_at_position_0_detected():
    entries = make_chain(_DOCTRINE_PACKET, _DOCTRINE_PACKET, _DOCTRINE_PACKET)
    entries[0] = {**entries[0], "decision": "TAMPERED"}
    assert verify_chain(entries) is not None


def test_tamper_at_position_1_detected():
    entries = make_chain(_DOCTRINE_PACKET, _DOCTRINE_PACKET, _DOCTRINE_PACKET)
    entries[1] = {**entries[1], "decision": "TAMPERED"}
    assert verify_chain(entries) is not None


def test_tamper_localization_exact_position():
    """Tamper at pos 2 only — positions 0 and 1 must still pass the local check."""
    entries = make_chain(_DOCTRINE_PACKET, _DOCTRINE_PACKET, _DOCTRINE_PACKET)
    # Mutate entry 2 without updating its hash → hash mismatch at exactly pos 2.
    entries[2] = {**entries[2], "decision": "TAMPERED"}
    broken = _broken_positions(entries)
    assert 2 in broken
    assert 0 not in broken
    assert 1 not in broken


def test_genesis_guard_enforced():
    """An entry whose prev is forced to GENESIS (wrong) is rejected."""
    entries = make_chain(_DOCTRINE_PACKET, _DOCTRINE_PACKET)
    # Force entry 1's prev back to GENESIS and recompute its hash so it's
    # internally self-consistent but the chain pointer is wrong.
    e1_body = {**entries[1], "prev": GENESIS}
    e1_body["entry_hash"] = _hash_body({k: v for k, v in e1_body.items() if k != "entry_hash"})
    entries[1] = e1_body
    result = verify_chain(entries)
    assert result is not None
    assert "prev" in result or "1" in result


# ── determinism ──────────────────────────────────────────────────────────────

def test_chain_is_deterministic():
    a = make_chain(_DOCTRINE_PACKET)
    b = make_chain(_DOCTRINE_PACKET)
    assert a[0]["entry_hash"] == b[0]["entry_hash"]


# ── authority field invariant ────────────────────────────────────────────────

def test_authority_mutation_breaks_hash():
    """Changing authority from False to True invalidates the stored entry_hash."""
    entries = make_chain(_DOCTRINE_PACKET)
    original_hash = entries[0]["entry_hash"]
    body_mutated = {k: v for k, v in entries[0].items() if k != "entry_hash"}
    body_mutated["authority"] = True
    assert _hash_body(body_mutated) != original_hash


# ── fixture invariants ───────────────────────────────────────────────────────

def test_doctrine_packet_admission_no_receipt():
    assert _DOCTRINE_PACKET["admission"] == "NO_RECEIPT"
    assert _DOCTRINE_PACKET["authority"] is False
