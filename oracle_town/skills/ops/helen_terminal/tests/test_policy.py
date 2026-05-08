"""Tests: policy enforcement — no destructive ops, no unauthorized extensions."""
import json
from pathlib import Path
import pytest


def test_policy_file_exists():
    policy_path = Path(__file__).resolve().parent.parent / "policy.json"
    assert policy_path.exists()
    p = json.loads(policy_path.read_text())
    assert p["authority"] == "NON_SOVEREIGN"
    assert p["canon"] == "NO_SHIP"
    assert p["mayor_default"] == "NO_SHIP"
    assert p["email"]["send"] == "operator_confirm_only"
    assert p["files"]["write"] == "proposal_then_confirm"


def test_no_send_in_gmail_code():
    gmail_path = Path(__file__).resolve().parent.parent / "inbox" / "gmail_reader.py"
    src = gmail_path.read_text()
    assert "messages().send" not in src, "gmail_reader must never call messages().send"


def test_no_destructive_ops_in_editor():
    editor_path = Path(__file__).resolve().parent.parent / "files" / "file_editor.py"
    src = editor_path.read_text()
    for forbidden in ["os.remove", "shutil.rmtree", "Path.unlink", "os.unlink"]:
        assert forbidden not in src, f"file_editor must not call {forbidden}"


def test_no_chmod_in_codebase():
    root = Path(__file__).resolve().parent.parent
    for py_file in root.rglob("*.py"):
        if py_file.parent.name == "tests":
            continue
        src = py_file.read_text()
        assert "os.chmod" not in src, f"{py_file.name} must not call os.chmod"
        assert "subprocess" not in src or py_file.name == "cli.py", \
            f"{py_file.name} must not use subprocess directly (route through policy gate)"
