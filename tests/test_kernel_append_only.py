"""
tests/test_kernel_append_only.py

RED TEST — Property P1: append grows ledger length by exactly 1.

Kernel contract:
  append L a t raw = Some L'  →  |L'| = |L| + 1
  response: {"ok": true, "cum_hash": "...", "seq": N}  (seq = |L| before append)

This test starts RED because kernel_cli is a stub that returns:
  {"ok": false, "error": "kernel_cli stub: not yet linked"}

It turns GREEN when kernel_cli is compiled and properly wired to the
extracted structural_valid_b from formal/LedgerKernel.v.

Hash scheme: HELEN_CUM_V1 (pinned)
  payload_hash = SHA256(raw_payload_bytes)
  cum_hash     = SHA256("HELEN_CUM_V1" || bytes(prev) || bytes(payload_hash))
"""

import json
import os
import tempfile

import pytest
pytestmark = pytest.mark.requires_ocaml

# Import helpers (not a pytest conftest — use direct import)
import sys
sys.path.insert(0, os.path.dirname(__file__))
from conftest_kernel import (
    GENESIS_HASH,
    invoke_kernel_cli,
    compute_expected,
    chain_hash_v1,
    compute_payload_hash,
    canon_json_bytes,
    sha256_hex,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path):
    """Provide a fresh empty ledger file path."""
    return str(tmp_path / "test_append_only.ndjson")


# ---------------------------------------------------------------------------
# Test P1.1: First append to empty ledger returns ok=true, seq=0
# ---------------------------------------------------------------------------

def test_append_first_event_ok(ledger):
    """
    P1: First append to empty ledger → ok=true, seq=0.
    RED: stub returns ok=false with stub error.
    """
    payload = {"channel": "HER_HAL_V1", "turn": 0, "verdict": "PASS"}
    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)

    assert resp.get("ok") is True, (
        f"Expected ok=true for first append.\n"
        f"Got: {resp}\n"
        f"[RED] binary is stub or not found."
    )
    assert resp.get("seq") == 0, (
        f"Expected seq=0 for first event. Got seq={resp.get('seq')}"
    )


# ---------------------------------------------------------------------------
# Test P1.2: Second append returns ok=true, seq=1
# ---------------------------------------------------------------------------

def test_append_second_event_seq_increments(ledger):
    """
    P1: Second append → ok=true, seq=1.
    RED: stub always rejects.
    """
    p0 = {"channel": "HER_HAL_V1", "turn": 0, "verdict": "PASS"}
    p1 = {"channel": "HER_HAL_V1", "turn": 1, "verdict": "PASS"}

    rc0, r0 = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", p0)
    assert r0.get("ok") is True, f"First append failed: {r0}"

    rc1, r1 = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", p1)
    assert r1.get("ok") is True, f"Second append failed: {r1}"
    assert r1.get("seq") == 1, f"Expected seq=1, got {r1.get('seq')}"


# ---------------------------------------------------------------------------
# Test P1.3: N sequential appends all succeed, seq = 0..N-1
# ---------------------------------------------------------------------------

def test_append_n_events_seq_range(ledger):
    """
    P1: N sequential appends all succeed with seq = 0..N-1.
    RED: stub always rejects.
    """
    N = 5
    for i in range(N):
        payload = {"turn": i, "verdict": "PASS", "channel": "HER_HAL_V1"}
        rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)

        assert resp.get("ok") is True, (
            f"Append {i} failed: {resp}"
        )
        assert resp.get("seq") == i, (
            f"Append {i}: expected seq={i}, got seq={resp.get('seq')}"
        )


# ---------------------------------------------------------------------------
# Test P1.4: Rejected append does NOT grow the ledger
# ---------------------------------------------------------------------------

def test_rejected_append_does_not_grow_ledger(ledger):
    """
    P1 converse: rejected append (authority violation) does not grow ledger.
    A subsequent valid append must still get seq=0 (not seq=1).
    RED: stub always rejects, so the second append also fails.
    """
    # HELEN cannot issue TERMINATION — should be rejected
    rc_bad, r_bad = invoke_kernel_cli(
        ledger, "HELEN", "TERMINATION", {"reason": "unauthorized"}
    )
    assert r_bad.get("ok") is False, (
        f"Expected rejection for HELEN TERMINATION, got: {r_bad}"
    )

    # Valid first append should still get seq=0
    rc_ok, r_ok = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION", {"reason": "done", "run_id": "R001"}
    )
    assert r_ok.get("ok") is True, f"Valid append failed: {r_ok}"
    assert r_ok.get("seq") == 0, (
        f"After rejected append, valid event should have seq=0, got {r_ok.get('seq')}"
    )
