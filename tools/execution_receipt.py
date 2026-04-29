"""Execution Receipt — non-sovereign receipt for code execution events.

Every command run through HELEN tooling must produce a receipt.
This closes the gap between render receipts (video pipeline) and
execution receipts (tool/script pipeline).

Hard invariants:
  - Authority is always NON_SOVEREIGN_EXECUTION. Never elevated.
  - Hashes are deterministic: sha256(command) + sha256(output).
  - This module never executes commands. Callers run; this receipts.
  - Never writes to town/ledger_v1.ndjson or any sovereign path.

Receipt schema:
  {
    "command_hash":  str   sha256(command string),
    "output_hash":   str   sha256(stdout + stderr, empty string if absent),
    "status":        str   "SUCCESS" | "FAIL",
    "exit_code":     int   actual process exit code,
    "authority":     str   "NON_SOVEREIGN_EXECUTION",
    "timestamp":     str   ISO-8601 UTC,
  }
"""
from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from typing import Sequence


AUTHORITY = "NON_SOVEREIGN_EXECUTION"
STATUS_SUCCESS = "SUCCESS"
STATUS_FAIL = "FAIL"


# ── hash helpers ──────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def command_hash(command: str | list) -> str:
    """Canonical hash of a command string or argv list."""
    canonical = command if isinstance(command, str) else " ".join(str(a) for a in command)
    return _sha256(canonical)


def output_hash(stdout: str = "", stderr: str = "") -> str:
    """Hash of combined stdout+stderr output."""
    return _sha256((stdout or "") + (stderr or ""))


# ── receipt construction ──────────────────────────────────────────────────────

def make_receipt(
    command: str | list,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
) -> dict:
    """Build an execution receipt from command + output.

    Does NOT execute the command. Caller is responsible for running it.

    Args:
        command:   The command string or argv list that was run.
        stdout:    Captured standard output (empty string if not captured).
        stderr:    Captured standard error (empty string if not captured).
        exit_code: Process exit code (0 = success by convention).

    Returns:
        Receipt dict. authority is always NON_SOVEREIGN_EXECUTION.
    """
    status = STATUS_SUCCESS if exit_code == 0 else STATUS_FAIL
    return {
        "command_hash": command_hash(command),
        "output_hash": output_hash(stdout, stderr),
        "status": status,
        "exit_code": exit_code,
        "authority": AUTHORITY,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def verify_receipt(
    receipt: dict,
    command: str | list,
    stdout: str = "",
    stderr: str = "",
) -> bool:
    """Verify that a receipt was produced from the given command and output.

    Checks command_hash and output_hash. Does not re-execute the command.

    Returns:
        True if both hashes match and authority is NON_SOVEREIGN_EXECUTION.
        False otherwise.
    """
    if receipt.get("authority") != AUTHORITY:
        return False
    if receipt.get("command_hash") != command_hash(command):
        return False
    if receipt.get("output_hash") != output_hash(stdout, stderr):
        return False
    return True


# ── convenience: run + receipt ────────────────────────────────────────────────

def run_with_receipt(
    cmd: Sequence[str],
    *,
    timeout: int | None = 30,
    cwd: str | None = None,
) -> tuple[subprocess.CompletedProcess, dict]:
    """Run a subprocess and return (result, receipt).

    The receipt is issued after the process completes. The caller decides
    what to do with both — this function does not write to any ledger.

    Args:
        cmd:     Command argv sequence.
        timeout: Seconds before subprocess.TimeoutExpired is raised.
        cwd:     Working directory for the subprocess.

    Returns:
        (CompletedProcess, receipt_dict)

    Raises:
        subprocess.TimeoutExpired: if the command exceeds timeout.
        FileNotFoundError: if the executable is not found.
    """
    result = subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )
    receipt = make_receipt(
        command=list(cmd),
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )
    return result, receipt
