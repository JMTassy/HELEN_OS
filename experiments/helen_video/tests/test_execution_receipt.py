"""Execution Receipt — invariant and functional tests."""
import ast
import hashlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# tools/ is not a package — add it to path
_TOOLS = Path(__file__).resolve().parents[3] / "tools"
sys.path.insert(0, str(_TOOLS))

from execution_receipt import (
    AUTHORITY,
    STATUS_FAIL,
    STATUS_SUCCESS,
    command_hash,
    make_receipt,
    output_hash,
    run_with_receipt,
    verify_receipt,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ── command_hash ──────────────────────────────────────────────────────────────

def test_command_hash_string():
    assert command_hash("echo hello") == _sha256("echo hello")


def test_command_hash_list():
    assert command_hash(["echo", "hello"]) == _sha256("echo hello")


def test_command_hash_stable():
    assert command_hash("ls -la") == command_hash("ls -la")


def test_command_hash_differs_for_different_commands():
    assert command_hash("ls") != command_hash("pwd")


# ── output_hash ───────────────────────────────────────────────────────────────

def test_output_hash_empty():
    assert output_hash() == _sha256("")


def test_output_hash_combines_stdout_stderr():
    assert output_hash("out", "err") == _sha256("outerr")


def test_output_hash_stable():
    assert output_hash("hello", "world") == output_hash("hello", "world")


# ── make_receipt ──────────────────────────────────────────────────────────────

def test_make_receipt_success():
    r = make_receipt("echo hello", stdout="hello\n", exit_code=0)
    assert r["status"] == STATUS_SUCCESS
    assert r["exit_code"] == 0
    assert r["authority"] == AUTHORITY


def test_make_receipt_fail():
    r = make_receipt("bad_cmd", stderr="not found", exit_code=1)
    assert r["status"] == STATUS_FAIL
    assert r["exit_code"] == 1


def test_make_receipt_has_all_required_fields():
    r = make_receipt("ls", stdout="file.txt", exit_code=0)
    required = {"command_hash", "output_hash", "status", "exit_code", "authority", "timestamp"}
    assert required <= set(r.keys())


def test_make_receipt_authority_is_non_sovereign():
    r = make_receipt("ls")
    assert r["authority"] == "NON_SOVEREIGN_EXECUTION"


def test_make_receipt_command_hash_correct():
    cmd = "pytest -q"
    r = make_receipt(cmd)
    assert r["command_hash"] == _sha256(cmd)


def test_make_receipt_output_hash_correct():
    r = make_receipt("echo", stdout="ok", stderr="")
    assert r["output_hash"] == _sha256("ok")


def test_make_receipt_does_not_mutate_nothing():
    # No mutable inputs — just check it returns a new dict each call
    r1 = make_receipt("ls")
    r2 = make_receipt("ls")
    assert r1 is not r2


# ── verify_receipt ────────────────────────────────────────────────────────────

def test_verify_receipt_valid():
    cmd = "echo hello"
    out = "hello\n"
    r = make_receipt(cmd, stdout=out, exit_code=0)
    assert verify_receipt(r, cmd, stdout=out) is True


def test_verify_receipt_wrong_command():
    r = make_receipt("ls", stdout="file.txt", exit_code=0)
    assert verify_receipt(r, "pwd", stdout="file.txt") is False


def test_verify_receipt_wrong_output():
    r = make_receipt("ls", stdout="file.txt", exit_code=0)
    assert verify_receipt(r, "ls", stdout="other.txt") is False


def test_verify_receipt_forged_authority():
    r = make_receipt("ls")
    r = {**r, "authority": "SOVEREIGN"}
    assert verify_receipt(r, "ls") is False


def test_verify_receipt_forged_command_hash():
    r = make_receipt("ls", stdout="ok")
    r = {**r, "command_hash": "fake"}
    assert verify_receipt(r, "ls", stdout="ok") is False


# ── run_with_receipt ──────────────────────────────────────────────────────────

def test_run_with_receipt_success():
    result, receipt = run_with_receipt(["echo", "hello"])
    assert result.returncode == 0
    assert receipt["status"] == STATUS_SUCCESS
    assert receipt["authority"] == AUTHORITY
    assert verify_receipt(receipt, ["echo", "hello"],
                          stdout=result.stdout, stderr=result.stderr)


def test_run_with_receipt_fail():
    result, receipt = run_with_receipt(["false"])
    assert result.returncode != 0
    assert receipt["status"] == STATUS_FAIL


def test_run_with_receipt_receipt_binds_output():
    result, receipt = run_with_receipt(["echo", "test"])
    assert verify_receipt(
        receipt, ["echo", "test"],
        stdout=result.stdout, stderr=result.stderr
    )


# ── invariant: no sovereign paths ────────────────────────────────────────────

def test_module_has_no_ledger_writes():
    mod_path = _TOOLS / "execution_receipt.py"
    tree = ast.parse(mod_path.read_text())
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    forbidden = {"append", "write_text", "write_bytes"}
    assert not (set(calls) & forbidden), f"Forbidden calls: {set(calls) & forbidden}"


def test_authority_constant_is_non_sovereign():
    assert AUTHORITY == "NON_SOVEREIGN_EXECUTION"
