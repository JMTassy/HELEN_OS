"""
Tests for duplicate seq detection in NDJSON ledger files.

Confirms that the scan utility correctly identifies NEEDS_REPAIR ledgers
(those with duplicate seq values) and passes clean ledgers.

These tests use the same _detect_duplicate_seq helper from
test_ndjson_writer_atomic — here it is defined inline to keep the module
self-contained and importable without side effects.
"""
from __future__ import annotations

import json
import tempfile
import os
from collections import Counter

import pytest

from tools.ndjson_writer import NDJSONWriter


def _detect_duplicate_seq(path: str) -> dict:
    """
    Return {seq: count} for any seq that appears more than once.
    Returns {} for a clean ledger (PASS).
    """
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    counts = Counter(e["seq"] for e in entries)
    return {seq: cnt for seq, cnt in counts.items() if cnt > 1}


def _write_clean_ledger(path: str, n: int):
    w = NDJSONWriter(path=path, seq=0, prev_cum_hash="0" * 64)
    for i in range(n):
        w.append_event("turn", {"i": i})


def _inject_duplicate_seq(path: str, dup_seq: int):
    """Append a fake entry with dup_seq to simulate a seq collision."""
    fake = {
        "type": "INJECTED_DUP",
        "seq": dup_seq,
        "payload": {"injected": True},
        "meta": {},
        "payload_hash": "d" * 64,
        "prev_cum_hash": "e" * 64,
        "cum_hash": "f" * 64,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(fake) + "\n")


# ---------------------------------------------------------------------------
# Clean ledger tests
# ---------------------------------------------------------------------------

def test_clean_ledger_returns_pass(tmp_path):
    ledger = str(tmp_path / "clean.ndjson")
    _write_clean_ledger(ledger, 10)
    assert _detect_duplicate_seq(ledger) == {}, "Clean ledger must return {} (PASS)"


def test_single_entry_clean(tmp_path):
    ledger = str(tmp_path / "single.ndjson")
    _write_clean_ledger(ledger, 1)
    assert _detect_duplicate_seq(ledger) == {}


def test_empty_ledger_clean(tmp_path):
    ledger = str(tmp_path / "empty.ndjson")
    ledger_obj = open(ledger, "w")
    ledger_obj.close()
    assert _detect_duplicate_seq(ledger) == {}


# ---------------------------------------------------------------------------
# Duplicate seq tests (NEEDS_REPAIR)
# ---------------------------------------------------------------------------

def test_duplicate_seq_at_zero_detected(tmp_path):
    ledger = str(tmp_path / "dup0.ndjson")
    _write_clean_ledger(ledger, 3)
    _inject_duplicate_seq(ledger, dup_seq=0)
    dups = _detect_duplicate_seq(ledger)
    assert dups == {0: 2}, f"Expected {{0: 2}}, got {dups}"


def test_duplicate_seq_mid_chain_detected(tmp_path):
    ledger = str(tmp_path / "dup_mid.ndjson")
    _write_clean_ledger(ledger, 10)
    _inject_duplicate_seq(ledger, dup_seq=5)
    dups = _detect_duplicate_seq(ledger)
    assert dups == {5: 2}, f"Expected {{5: 2}}, got {dups}"


def test_live_ledger_fork_pattern(tmp_path):
    """
    Reproduce the exact REFERENCE_DRIFT_WITNESS_V1 fork topology:
    seq 0..N written cleanly, then seq N injected again (SKILL_PROMOTION_DECISION_V1
    written by kernel before helen_say.py re-scanned the tail).
    """
    ledger = str(tmp_path / "fork.ndjson")
    _write_clean_ledger(ledger, 5)  # writes seq 0-4

    # Simulate the kernel writing at seq=4 while helen_say had pre-allocated seq=4
    _inject_duplicate_seq(ledger, dup_seq=4)

    # Continue writing seq=5 (live chain continues from injected entry)
    w = NDJSONWriter(path=ledger, seq=0, prev_cum_hash="0" * 64)
    w.append_event("turn", {"i": 5})

    dups = _detect_duplicate_seq(ledger)
    assert 4 in dups, "Duplicate at forked seq must be detected"
    assert dups[4] == 2


def test_multiple_duplicates_all_detected(tmp_path):
    ledger = str(tmp_path / "multi_dup.ndjson")
    _write_clean_ledger(ledger, 8)
    _inject_duplicate_seq(ledger, dup_seq=2)
    _inject_duplicate_seq(ledger, dup_seq=6)
    dups = _detect_duplicate_seq(ledger)
    assert set(dups.keys()) == {2, 6}


def test_status_pass_when_no_dups(tmp_path):
    """
    Classification test: detect_duplicate_seq == {} means PASS (no repair needed).
    A non-empty return means NEEDS_REPAIR.
    """
    ledger = str(tmp_path / "status.ndjson")
    _write_clean_ledger(ledger, 20)

    dups = _detect_duplicate_seq(ledger)
    status = "PASS" if not dups else "NEEDS_REPAIR"
    assert status == "PASS"


def test_status_needs_repair_when_dups(tmp_path):
    ledger = str(tmp_path / "status_bad.ndjson")
    _write_clean_ledger(ledger, 20)
    _inject_duplicate_seq(ledger, dup_seq=10)

    dups = _detect_duplicate_seq(ledger)
    status = "PASS" if not dups else "NEEDS_REPAIR"
    assert status == "NEEDS_REPAIR"
