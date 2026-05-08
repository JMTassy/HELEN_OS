"""Tests: action receipt builder."""
import json
import tempfile
from pathlib import Path
import pytest


def test_build_receipt_creates_file(tmp_path, monkeypatch):
    import oracle_town.skills.ops.helen_terminal.receipts.action_receipts as ar
    monkeypatch.setattr(ar, "RECEIPTS_DIR", tmp_path / "receipts")
    monkeypatch.setattr(ar, "LEDGER_PATH", tmp_path / "ledger.ndjson")

    receipt = ar.build_receipt(
        "TEST_ACTION",
        {"key": "value"},
        {"type": "TEST_ARTIFACT", "content_preview": "test"},
    )
    assert receipt["receipt_id"].startswith("RT-")
    assert receipt["authority"] == "NON_SOVEREIGN"
    assert receipt["canon"] == "NO_SHIP"
    assert receipt["verified"] is True
    assert (tmp_path / "receipts" / f"{receipt['receipt_id']}.json").exists()


def test_receipt_appends_ledger(tmp_path, monkeypatch):
    import oracle_town.skills.ops.helen_terminal.receipts.action_receipts as ar
    monkeypatch.setattr(ar, "RECEIPTS_DIR", tmp_path / "receipts")
    ledger = tmp_path / "ledger.ndjson"
    monkeypatch.setattr(ar, "LEDGER_PATH", ledger)

    ar.build_receipt("ACTION_A", {}, {"type": "A", "content_preview": "a"})
    ar.build_receipt("ACTION_B", {}, {"type": "B", "content_preview": "b"})

    lines = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    assert len(lines) == 2
    assert lines[0]["prev_hash"] == "GENESIS"
    assert lines[1]["prev_hash"] == lines[0]["event_hash"]


def test_receipt_hash_determinism(tmp_path, monkeypatch):
    import oracle_town.skills.ops.helen_terminal.receipts.action_receipts as ar
    monkeypatch.setattr(ar, "RECEIPTS_DIR", tmp_path / "r1")
    monkeypatch.setattr(ar, "LEDGER_PATH", tmp_path / "l1.ndjson")
    h1 = ar._hash({"b": 2, "a": 1})
    h2 = ar._hash({"a": 1, "b": 2})
    assert h1 == h2
