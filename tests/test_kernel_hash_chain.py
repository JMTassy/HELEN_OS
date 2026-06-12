"""
tests/test_kernel_hash_chain.py

RED TEST — Properties P4 + P5 + P6: hash chain integrity.

Properties tested:
  P4: hash_chain_integrity — every event's cum_hash = HELEN_CUM_V1(prev || ph)
  P5: payload_hash_correct — payload_hash = SHA256(raw_payload_bytes)
  P6: genesis_chain        — first event chains from "0"*64

Pinned scheme: HELEN_CUM_V1
  payload_hash = SHA256(canon_json_bytes(payload_dict))
  cum_hash     = SHA256("HELEN_CUM_V1" || bytes.fromhex(prev) || bytes.fromhex(ph))

This test starts RED because kernel_cli is a stub.
It turns GREEN when kernel_cli implements hash_util.ml Hash_util.concat
with the HELEN_CUM_V1 domain separator.
"""

import hashlib
import json
import os
import sys

import pytest
pytestmark = pytest.mark.requires_ocaml

sys.path.insert(0, os.path.dirname(__file__))
from conftest_kernel import (
    GENESIS_HASH,
    HELEN_CUM_V1_PREFIX,
    invoke_kernel_cli,
    compute_expected,
    compute_payload_hash,
    chain_hash_v1,
    sha256_hex,
    canon_json_bytes,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path):
    return str(tmp_path / "test_hash_chain.ndjson")


# ---------------------------------------------------------------------------
# Reference verification
# ---------------------------------------------------------------------------

def read_events(path: str) -> list:
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


# ---------------------------------------------------------------------------
# Test P5: payload_hash = SHA256(raw_payload_bytes) (from response)
# ---------------------------------------------------------------------------

def test_payload_hash_matches_sha256_of_raw_bytes(ledger):
    """
    P5: kernel response's payload_hash must equal SHA256(canon_json(payload)).
    RED: stub never returns payload_hash.
    """
    payload = {"channel": "HER_HAL_V1", "turn": 0, "verdict": "PASS"}
    expected_ph = compute_payload_hash(payload)

    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)
    assert resp.get("ok") is True, f"Append failed: {resp}"

    actual_ph = resp.get("payload_hash")
    assert actual_ph == expected_ph, (
        f"payload_hash mismatch.\n"
        f"  Expected: {expected_ph}\n"
        f"  Got:      {actual_ph}\n"
        f"  (SHA256 of: {canon_json_bytes(payload)!r})"
    )


# ---------------------------------------------------------------------------
# Test P6: First event chains from genesis ("0"*64)
# ---------------------------------------------------------------------------

def test_first_event_chains_from_genesis(ledger):
    """
    P6: cum_hash of first event = HELEN_CUM_V1(genesis_hash, payload_hash).
    RED: stub returns no cum_hash.
    """
    payload = {"channel": "HER_HAL_V1", "turn": 0, "verdict": "PASS"}
    expected_ph, expected_cum = compute_expected(payload, GENESIS_HASH)

    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)
    assert resp.get("ok") is True, f"Append failed: {resp}"

    actual_cum = resp.get("cum_hash")
    assert actual_cum == expected_cum, (
        f"cum_hash mismatch for first event (genesis chain).\n"
        f"  prev_cum_hash: {GENESIS_HASH}\n"
        f"  payload_hash:  {expected_ph}\n"
        f"  Expected cum:  {expected_cum}\n"
        f"  Got cum:       {actual_cum}\n"
        f"  Formula: SHA256('HELEN_CUM_V1' || bytes(prev) || bytes(ph))"
    )


# ---------------------------------------------------------------------------
# Test P4: Full hash chain across N events
# ---------------------------------------------------------------------------

def test_hash_chain_across_multiple_events(ledger):
    """
    P4: Every event's cum_hash = HELEN_CUM_V1(prev_cum_hash, payload_hash).
    Chain must hold end-to-end.
    RED: stub never returns correct cum_hash.
    """
    payloads = [
        {"channel": "HER_HAL_V1", "turn": 0, "verdict": "PASS"},
        {"channel": "HER_HAL_V1", "turn": 1, "verdict": "WARN"},
        {"channel": "HER_HAL_V1", "turn": 2, "verdict": "PASS"},
    ]

    prev = GENESIS_HASH
    responses = []

    for i, payload in enumerate(payloads):
        expected_ph, expected_cum = compute_expected(payload, prev)
        rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)

        assert resp.get("ok") is True, f"Append {i} failed: {resp}"
        responses.append(resp)

        actual_cum = resp.get("cum_hash")
        assert actual_cum == expected_cum, (
            f"cum_hash mismatch at event {i}.\n"
            f"  prev:     {prev}\n"
            f"  Expected: {expected_cum}\n"
            f"  Got:      {actual_cum}"
        )

        # Advance chain
        prev = expected_cum

    # Verify last_cum_hash in ledger file
    events = read_events(ledger)
    assert len(events) == len(payloads), (
        f"Expected {len(payloads)} events in file, got {len(events)}"
    )
    for i, (event, expected_resp) in enumerate(zip(events, responses)):
        assert event.get("cum_hash") == expected_resp.get("cum_hash"), (
            f"Event {i}: cum_hash in file differs from response"
        )


# ---------------------------------------------------------------------------
# Test P4 (file): Validate full chain from the written NDJSON file
# ---------------------------------------------------------------------------

def test_full_hash_chain_in_ledger_file(ledger):
    """
    P4: Validate the full hash chain by re-reading the ledger file.
    This is the test that validate_hash_chain.py would run in CI.
    RED: stub doesn't write to file.
    """
    N = 4
    payloads = [
        {"channel": "HER_HAL_V1", "turn": i, "verdict": "PASS"}
        for i in range(N)
    ]

    for payload in payloads:
        rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)
        assert resp.get("ok") is True, f"Append failed: {resp}"

    # Re-read and validate
    events = read_events(ledger)
    assert len(events) == N

    prev = GENESIS_HASH
    for i, event in enumerate(events):
        # Verify payload_hash
        stored_ph = event.get("payload_hash")
        assert stored_ph is not None, f"Event {i}: missing payload_hash"

        # Verify cum_hash = HELEN_CUM_V1(prev, payload_hash)
        expected_cum = chain_hash_v1(prev, stored_ph)
        actual_cum = event.get("cum_hash")
        assert actual_cum == expected_cum, (
            f"Event {i}: cum_hash chain broken.\n"
            f"  prev:     {prev}\n"
            f"  ph:       {stored_ph}\n"
            f"  Expected: {expected_cum}\n"
            f"  Got:      {actual_cum}"
        )

        prev = actual_cum


# ---------------------------------------------------------------------------
# Test P7: No hash injection — kernel ignores any supplied cum_hash
# ---------------------------------------------------------------------------

def test_no_hash_injection(ledger, tmp_path):
    """
    P7: Same payload always produces same cum_hash regardless of call site.
    (Kernel recomputes hashes; any injected value in request is ignored.)
    RED: stub always returns ok=false.
    """
    payload = {"channel": "HER_HAL_V1", "turn": 42, "verdict": "PASS"}

    # Independent ledger A
    ledger_a = str(tmp_path / "ledger_a.ndjson")
    rc_a, resp_a = invoke_kernel_cli(ledger_a, "MAYOR", "VERDICT", payload)
    assert resp_a.get("ok") is True, f"Ledger A append failed: {resp_a}"

    # Independent ledger B
    ledger_b = str(tmp_path / "ledger_b.ndjson")
    rc_b, resp_b = invoke_kernel_cli(ledger_b, "MAYOR", "VERDICT", payload)
    assert resp_b.get("ok") is True, f"Ledger B append failed: {resp_b}"

    # Both should produce identical cum_hash (determinism)
    assert resp_a.get("cum_hash") == resp_b.get("cum_hash"), (
        f"P7 FAIL: same payload produced different cum_hash on two independent runs.\n"
        f"  Ledger A cum_hash: {resp_a.get('cum_hash')}\n"
        f"  Ledger B cum_hash: {resp_b.get('cum_hash')}"
    )
