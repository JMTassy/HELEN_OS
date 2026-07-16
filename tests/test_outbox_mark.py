"""Tests for the consumption organ: outbox_consume (the pen) + outbox_guard (the gate).

Law under test:
  - only recorded decisions consume; the log is append-only and hash-chained
  - decisions bind to packet bytes (sha256)
  - failure is classified, never synthesized (BAD_JSON is named, can't be 'acted')
  - the guard fails closed: BAD_JSON, broken chain, stale decision, graveyard ceiling
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from temple.autoresearch.operator_pen import (
    load_packets, read_log, verify_chain, effective_decisions, unconsumed, mark,
)
from scripts.outbox_guard import run_guard


def make_packet(outbox: Path, pid: str, finding="test_gap", summary="a finding") -> Path:
    outbox.mkdir(parents=True, exist_ok=True)
    p = outbox / f"{pid}.json"
    p.write_text(json.dumps({
        "schema": "AUTORESEARCH_PACKET_V1", "packet_id": pid,
        "finding_type": finding, "summary": summary,
        "authority": False, "sovereign": False, "canon": False,
        "ledger_effect": "none", "reducer_required": True,
    }))
    return p


@pytest.fixture
def garden(tmp_path):
    outbox = tmp_path / "outbox"
    log = tmp_path / "consumption_log.ndjson"
    for i in range(3):
        make_packet(outbox, f"AR-aaa{i}")
    return outbox, log


# ---------------------------------------------------------- the pen

def test_list_shows_unconsumed(garden):
    outbox, log = garden
    un = unconsumed(load_packets(outbox), effective_decisions(read_log(log)))
    assert len(un) == 3


def test_mark_writes_chained_entry_with_packet_sha(garden):
    outbox, log = garden
    e = mark(outbox, log, "AR-aaa0", "acted", "built the thing", "JM")
    assert e["schema"] == "CONSUMPTION_ENTRY_V0"
    assert e["prev"] == "GENESIS"
    assert len(e["packet_sha256"]) == 64
    assert e["authority"] is False and e["ledger_effect"] == "none"
    entries = read_log(log)
    assert len(entries) == 1
    assert verify_chain(entries) is None


def test_marked_packet_no_longer_unconsumed(garden):
    outbox, log = garden
    mark(outbox, log, "AR-aaa1", "rejected", "not worth it", "JM")
    un = unconsumed(load_packets(outbox), effective_decisions(read_log(log)))
    assert {p["packet_id"] for p in un} == {"AR-aaa0", "AR-aaa2"}


def test_log_is_append_only_latest_wins(garden):
    outbox, log = garden
    mark(outbox, log, "AR-aaa0", "deferred", "later", "JM")
    mark(outbox, log, "AR-aaa0", "acted", "done now", "JM")
    entries = read_log(log)
    assert len(entries) == 2                       # nothing overwritten
    assert verify_chain(entries) is None           # chain still intact
    assert effective_decisions(entries)["AR-aaa0"]["decision"] == "acted"


def test_mark_phantom_packet_blocked(garden):
    outbox, log = garden
    with pytest.raises(SystemExit, match="phantom"):
        mark(outbox, log, "AR-nope", "acted", "x", "JM")


def test_mark_requires_note(garden):
    outbox, log = garden
    with pytest.raises(SystemExit, match="note"):
        mark(outbox, log, "AR-aaa0", "acted", "   ", "JM")


def test_bad_decision_vocabulary_blocked(garden):
    outbox, log = garden
    with pytest.raises(SystemExit, match="decision"):
        mark(outbox, log, "AR-aaa0", "admitted", "n", "JM")   # 'admitted' is NOT pen vocabulary


def test_bad_json_is_named_and_cannot_be_acted(garden):
    outbox, log = garden
    (outbox / "AR-corrupt.json").write_text("{ not json")
    pkts = load_packets(outbox)
    corrupt = [p for p in pkts if p["packet_id"] == "AR-corrupt"]
    assert corrupt and corrupt[0]["finding_type"] == "BAD_JSON"   # named, not synthesized
    with pytest.raises(SystemExit, match="BAD_JSON"):
        mark(outbox, log, "AR-corrupt", "acted", "pretend", "JM")
    mark(outbox, log, "AR-corrupt", "rejected", "corrupt on arrival", "JM")  # rejection allowed


def test_mark_refuses_to_write_on_broken_chain(garden):
    outbox, log = garden
    mark(outbox, log, "AR-aaa0", "acted", "ok", "JM")
    entries = read_log(log)
    entries[0]["note"] = "tampered"                              # forge the sidecar
    log.write_text(json.dumps(entries[0]) + "\n")
    with pytest.raises(SystemExit, match="chain broken"):
        mark(outbox, log, "AR-aaa1", "acted", "x", "JM")


# ---------------------------------------------------------- the gate

def test_guard_passes_under_ceiling(garden):
    outbox, log = garden
    ok, findings = run_guard(outbox, log, max_unconsumed=10)
    assert ok and not findings


def test_guard_fails_over_ceiling(garden):
    outbox, log = garden
    ok, findings = run_guard(outbox, log, max_unconsumed=2)
    assert not ok
    assert any("graveyard" in f for f in findings)


def test_guard_fails_on_bad_json(garden):
    outbox, log = garden
    (outbox / "AR-corrupt.json").write_text("{ nope")
    ok, findings = run_guard(outbox, log, max_unconsumed=10)
    assert not ok
    assert any("BAD_JSON" in f for f in findings)


def test_guard_fails_on_tampered_log(garden):
    outbox, log = garden
    mark(outbox, log, "AR-aaa0", "acted", "ok", "JM")
    raw = read_log(log)
    raw[0]["decision"] = "rejected"
    log.write_text(json.dumps(raw[0]) + "\n")
    ok, findings = run_guard(outbox, log, max_unconsumed=10)
    assert not ok
    assert any("chain broken" in f for f in findings)


def test_guard_fails_when_packet_changes_after_decision(garden):
    outbox, log = garden
    mark(outbox, log, "AR-aaa0", "acted", "judged these bytes", "JM")
    make_packet(outbox, "AR-aaa0", summary="silently rewritten")   # bytes changed post-decision
    ok, findings = run_guard(outbox, log, max_unconsumed=10)
    assert not ok
    assert any("sha mismatch" in f for f in findings)


def test_consumption_never_touches_sovereign_paths(garden):
    outbox, log = garden
    mark(outbox, log, "AR-aaa2", "acted", "bounded work", "JM")
    entry = read_log(log)[-1]
    assert entry["ledger_effect"] == "none"
    assert entry["sovereign"] is False
    assert "town" not in str(log) and "GOVERNANCE" not in str(log)
