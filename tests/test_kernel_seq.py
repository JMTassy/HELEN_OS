"""
tests/test_kernel_seq.py

RED TEST — Property P2 (seq strict monotonicity):
  Every event in the ledger has seq = its position (0-indexed).
  After N appends: ledger[i].seq == i for all i in 0..N-1.

This test starts RED because kernel_cli is a stub.
It turns GREEN when kernel_cli is compiled and writes correct seq numbers.

Also tests: ledger file is parseable NDJSON after appends.
"""

import json
import os
import sys

import pytest
pytestmark = pytest.mark.requires_ocaml

sys.path.insert(0, os.path.dirname(__file__))
from conftest_kernel import (
    invoke_kernel_cli,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path):
    return str(tmp_path / "test_seq.ndjson")


# ---------------------------------------------------------------------------
# Helper: read all events from a ledger file
# ---------------------------------------------------------------------------

def read_ledger_events(ledger_path: str) -> list:
    """Read all NDJSON lines from a ledger file. Returns list of dicts."""
    events = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


# ---------------------------------------------------------------------------
# Test P2.1: seq in responses is 0, 1, 2, ... (from stdout)
# ---------------------------------------------------------------------------

def test_seq_strictly_increasing_in_response(ledger):
    """
    P2: seq values in kernel_cli responses are 0, 1, 2, ...
    RED: stub always returns ok=false (seq not present).
    """
    N = 5
    for i in range(N):
        payload = {"turn": i, "verdict": "PASS", "channel": "HER_HAL_V1"}
        rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)

        assert resp.get("ok") is True, f"Append {i} failed: {resp}"
        assert resp.get("seq") == i, (
            f"Seq mismatch at append {i}: expected {i}, got {resp.get('seq')}"
        )


# ---------------------------------------------------------------------------
# Test P2.2: seq values in the ledger file are 0, 1, 2, ...
# ---------------------------------------------------------------------------

def test_seq_strictly_increasing_in_ledger_file(ledger):
    """
    P2: After N appends, the ledger file's seq fields are 0..N-1.
    RED: stub never writes to the file, so read_ledger_events returns [].
    """
    N = 4
    for i in range(N):
        payload = {"turn": i, "verdict": "PASS", "channel": "HER_HAL_V1"}
        rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)
        assert resp.get("ok") is True, f"Append {i} failed: {resp}"

    # Read back from file
    events = read_ledger_events(ledger)
    assert len(events) == N, (
        f"Expected {N} events in ledger file, got {len(events)}"
    )
    for i, event in enumerate(events):
        assert event.get("seq") == i, (
            f"Ledger event {i}: expected seq={i}, got seq={event.get('seq')}"
        )


# ---------------------------------------------------------------------------
# Test P2.3: Rejected append does NOT write to ledger file
# ---------------------------------------------------------------------------

def test_rejected_append_not_written_to_file(ledger):
    """
    P2: Rejected appends produce no ledger file entries.
    RED: stub also fails valid appends, so ledger file stays empty.
    """
    # First a valid append
    rc0, r0 = invoke_kernel_cli(
        ledger, "MAYOR", "VERDICT",
        {"turn": 0, "verdict": "PASS", "channel": "HER_HAL_V1"}
    )
    assert r0.get("ok") is True, f"First append failed: {r0}"

    # Rejected append (HELEN cannot issue TERMINATION)
    rc_bad, r_bad = invoke_kernel_cli(
        ledger, "HELEN", "TERMINATION", {"reason": "bad"}
    )
    assert r_bad.get("ok") is False, "Expected rejection for authority violation"

    # File should have exactly 1 event
    events = read_ledger_events(ledger)
    assert len(events) == 1, (
        f"After 1 valid + 1 rejected, expected 1 event in file, got {len(events)}"
    )
    assert events[0].get("seq") == 0


# ---------------------------------------------------------------------------
# Test P2.4: seq in file matches seq in response, event by event
# ---------------------------------------------------------------------------

def test_seq_in_file_matches_response(ledger):
    """
    P2: seq values returned in responses match seq values written to file.
    RED: stub doesn't write to file and returns no seq.
    """
    N = 3
    seqs_from_responses = []

    for i in range(N):
        payload = {"turn": i, "verdict": "PASS", "channel": "HER_HAL_V1"}
        rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", payload)
        assert resp.get("ok") is True, f"Append {i} failed: {resp}"
        seqs_from_responses.append(resp["seq"])

    events = read_ledger_events(ledger)
    seqs_from_file = [e.get("seq") for e in events]

    assert seqs_from_responses == seqs_from_file, (
        f"seq mismatch: responses={seqs_from_responses}, file={seqs_from_file}"
    )
