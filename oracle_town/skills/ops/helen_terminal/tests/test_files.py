"""Tests: file reader and editor with policy enforcement."""
import json
import tempfile
from pathlib import Path
import pytest


def _patch_data(monkeypatch, tmp_path):
    import oracle_town.skills.ops.helen_terminal.receipts.action_receipts as ar
    monkeypatch.setattr(ar, "RECEIPTS_DIR", tmp_path / "receipts")
    monkeypatch.setattr(ar, "LEDGER_PATH", tmp_path / "ledger.ndjson")


def test_read_file_success(tmp_path, monkeypatch):
    _patch_data(monkeypatch, tmp_path)
    from oracle_town.skills.ops.helen_terminal.files.file_reader import read_file
    f = tmp_path / "test.md"
    f.write_text("line1\nline2\nline3")
    result = read_file(f)
    assert "line1" in result["artifact"]["content"]
    assert result["artifact"]["type"] == "FILE_READ"
    assert result["receipt_id"].startswith("RT-")


def test_read_file_blocked_extension(tmp_path, monkeypatch):
    _patch_data(monkeypatch, tmp_path)
    from oracle_town.skills.ops.helen_terminal.files.file_reader import read_file
    f = tmp_path / "binary.exe"
    f.write_bytes(b"\x00\x01\x02")
    with pytest.raises(PermissionError):
        read_file(f)


def test_inspect_folder(tmp_path, monkeypatch):
    _patch_data(monkeypatch, tmp_path)
    from oracle_town.skills.ops.helen_terminal.files.file_reader import inspect_folder
    (tmp_path / "sub").mkdir()
    (tmp_path / "file.txt").write_text("hello")
    result = inspect_folder(tmp_path)
    assert result["artifact"]["type"] == "FOLDER_INSPECTION"
    assert result["receipt_id"].startswith("RT-")


def test_propose_edit_creates_pending(tmp_path, monkeypatch):
    _patch_data(monkeypatch, tmp_path)
    import oracle_town.skills.ops.helen_terminal.files.file_editor as fe
    monkeypatch.setattr(fe, "_PENDING_DIR", tmp_path / "pending")
    from oracle_town.skills.ops.helen_terminal.files.file_editor import propose_edit, confirm_edit

    f = tmp_path / "doc.md"
    f.write_text("Hello world")
    result = propose_edit(f, "Hello", "Hi", reason="friendlier greeting")
    assert result["status"] == "PENDING_CONFIRM"
    assert "proposal_id" in result

    confirm = confirm_edit(result["proposal_id"])
    assert confirm["status"] == "APPLIED"
    assert f.read_text() == "Hi world"


def test_propose_edit_reject(tmp_path, monkeypatch):
    _patch_data(monkeypatch, tmp_path)
    import oracle_town.skills.ops.helen_terminal.files.file_editor as fe
    monkeypatch.setattr(fe, "_PENDING_DIR", tmp_path / "pending")
    from oracle_town.skills.ops.helen_terminal.files.file_editor import propose_edit, reject_edit

    f = tmp_path / "doc.txt"
    f.write_text("original content")
    result = propose_edit(f, "original", "changed")
    reject_edit(result["proposal_id"])
    assert f.read_text() == "original content"


def test_propose_edit_old_string_not_found(tmp_path, monkeypatch):
    _patch_data(monkeypatch, tmp_path)
    import oracle_town.skills.ops.helen_terminal.files.file_editor as fe
    monkeypatch.setattr(fe, "_PENDING_DIR", tmp_path / "pending")
    from oracle_town.skills.ops.helen_terminal.files.file_editor import propose_edit

    f = tmp_path / "doc.py"
    f.write_text("def foo(): pass")
    with pytest.raises(ValueError):
        propose_edit(f, "def bar():", "def baz():")
