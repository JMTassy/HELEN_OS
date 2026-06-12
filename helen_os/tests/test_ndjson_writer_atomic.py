"""
Tests for NDJSONWriter atomic append behaviour (file locking + seq integrity).

Covers:
  1. Sequential appends produce unique, incrementing seq values
  2. Re-read under lock: even if writer is constructed with wrong seq,
     append_event() uses the correct on-disk seq
  3. Concurrent appends (threading) produce unique seq values
  4. append_event returns dict with seq, payload_hash, cum_hash, prev_cum_hash
  5. A helper scan function detects duplicate seq in a fixture file
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from typing import List

import pytest

from tools.ndjson_writer import NDJSONWriter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_writer(path: str, seq: int = 0, prev_cum: str = "0" * 64) -> NDJSONWriter:
    return NDJSONWriter(path=path, seq=seq, prev_cum_hash=prev_cum)


def _load_entries(path: str) -> List[dict]:
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def _detect_duplicate_seq(path: str) -> dict:
    """
    Scan a ledger file and return a dict mapping seq -> count for any seq
    that appears more than once.  Returns {} for a clean ledger.
    """
    from collections import Counter
    entries = _load_entries(path)
    counts = Counter(e["seq"] for e in entries)
    return {seq: cnt for seq, cnt in counts.items() if cnt > 1}


# ---------------------------------------------------------------------------
# Test 1: Sequential appends produce unique, incrementing seq values
# ---------------------------------------------------------------------------

def test_sequential_appends_produce_unique_incrementing_seqs(tmp_path):
    ledger = str(tmp_path / "ledger.ndjson")
    writer = _new_writer(ledger)

    results = []
    for i in range(5):
        r = writer.append_event("turn", {"i": i})
        results.append(r)

    seqs = [r["seq"] for r in results]
    assert seqs == list(range(5)), f"Expected [0,1,2,3,4], got {seqs}"

    # Verify on disk
    entries = _load_entries(ledger)
    assert len(entries) == 5
    on_disk_seqs = [e["seq"] for e in entries]
    assert on_disk_seqs == list(range(5))

    # No duplicates
    assert _detect_duplicate_seq(ledger) == {}


# ---------------------------------------------------------------------------
# Test 2: Wrong constructor seq is ignored — on-disk tail wins
# ---------------------------------------------------------------------------

def test_wrong_constructor_seq_is_overridden_by_on_disk_tail(tmp_path):
    """
    Pre-populate a ledger with 3 entries (seq 0-2), then construct a NEW
    NDJSONWriter with seq=0 (wrong). append_event() must use seq=3 (on-disk).
    """
    ledger = str(tmp_path / "ledger.ndjson")

    # Write 3 entries with a well-behaved writer
    w1 = _new_writer(ledger)
    for i in range(3):
        w1.append_event("turn", {"i": i})

    # Construct a badly-initialised writer that claims seq=0
    w2 = _new_writer(ledger, seq=0, prev_cum="0" * 64)
    written = w2.append_event("turn", {"i": 99})

    # The written record must have seq=3 (the correct next seq), not 0
    assert written["seq"] == 3, f"Expected seq=3, got seq={written['seq']}"

    entries = _load_entries(ledger)
    assert len(entries) == 4
    assert entries[-1]["seq"] == 3
    # No duplicates
    assert _detect_duplicate_seq(ledger) == {}


# ---------------------------------------------------------------------------
# Test 3: Concurrent appends produce unique seq values (no duplicates)
# ---------------------------------------------------------------------------

def test_concurrent_appends_produce_unique_seqs(tmp_path):
    """
    5 threads each append 4 records to the same ledger.
    Total: 20 records — all seq values must be unique (0-19).
    """
    ledger = str(tmp_path / "ledger.ndjson")
    errors: List[Exception] = []

    def worker(thread_id: int):
        try:
            w = _new_writer(ledger)
            for i in range(4):
                w.append_event("turn", {"thread": thread_id, "i": i})
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"

    entries = _load_entries(ledger)
    assert len(entries) == 20, f"Expected 20 entries, got {len(entries)}"

    seqs = sorted(e["seq"] for e in entries)
    assert seqs == list(range(20)), f"Expected seqs 0-19, got {seqs}"

    assert _detect_duplicate_seq(ledger) == {}


# ---------------------------------------------------------------------------
# Test 4: append_event returns dict with required fields
# ---------------------------------------------------------------------------

def test_append_event_returns_full_record(tmp_path):
    ledger = str(tmp_path / "ledger.ndjson")
    writer = _new_writer(ledger)
    result = writer.append_event("turn", {"x": 1}, meta={"note": "test"})

    assert isinstance(result, dict)
    assert "seq" in result
    assert "payload_hash" in result
    assert "cum_hash" in result
    assert "prev_cum_hash" in result
    assert result["type"] == "turn"
    assert result["payload"] == {"x": 1}
    assert result["meta"] == {"note": "test"}

    # payload_hash and cum_hash must be 64-char hex strings
    assert len(result["payload_hash"]) == 64
    assert all(c in "0123456789abcdef" for c in result["payload_hash"])
    assert len(result["cum_hash"]) == 64
    assert all(c in "0123456789abcdef" for c in result["cum_hash"])

    # prev_cum_hash for first entry must be the genesis zero
    assert result["prev_cum_hash"] == "0" * 64


# ---------------------------------------------------------------------------
# Test 5: Duplicate seq detector catches forked ledger
# ---------------------------------------------------------------------------

def test_duplicate_seq_detector_flags_forked_ledger(tmp_path):
    """
    Write a ledger with a manually injected seq=1 duplicate (simulating the
    REFERENCE_DRIFT_WITNESS_V1 fork) and verify the detector flags it.
    """
    ledger = str(tmp_path / "ledger.ndjson")

    # Write seq=0 and seq=1 normally
    writer = _new_writer(ledger)
    writer.append_event("turn", {"i": 0})
    writer.append_event("turn", {"i": 1})

    # Manually inject a second seq=1 entry (simulating a concurrent write race)
    fake_entry = {
        "type": "SKILL_PROMOTION_DECISION_V1",
        "seq": 1,
        "payload": {"skill_id": "FAKE"},
        "meta": {},
        "payload_hash": "a" * 64,
        "prev_cum_hash": "b" * 64,
        "cum_hash": "c" * 64,
    }
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(fake_entry) + "\n")

    # Write seq=2 normally (to simulate the live chain continuing past the fork)
    writer2 = _new_writer(ledger)  # will re-read tail; gets seq=2 from last on-disk entry
    writer2.append_event("turn", {"i": 2})

    duplicates = _detect_duplicate_seq(ledger)
    assert duplicates == {1: 2}, f"Expected {{1: 2}}, got {duplicates}"


def test_duplicate_seq_detector_passes_clean_ledger(tmp_path):
    ledger = str(tmp_path / "ledger.ndjson")
    writer = _new_writer(ledger)
    for i in range(10):
        writer.append_event("turn", {"i": i})

    assert _detect_duplicate_seq(ledger) == {}
