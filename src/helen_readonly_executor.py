"""
HELEN read-only computer-use executor.

Purpose:
- Provide a tiny, explicit, non-mutating command surface for HELEN CLI shell mode.
- This is not CLAW yet.
- This is a local read-only bridge for operator inspection.

Authority: NON_SOVEREIGN
Mutation: forbidden
"""

from __future__ import annotations

import shlex
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


class ReadOnlyExecutionRejected(Exception):
    pass


@dataclass(frozen=True)
class ReadOnlyResult:
    command: list[str]
    stdout: str
    stderr: str
    returncode: int


_ALLOWED_EXACT = {
    ("git", "status", "-sb"),
    ("pwd",),
}

_ALLOWED_PREFIXES = {
    "ls",
    "find",
    "grep",
    "sed",
}

_FORBIDDEN_HEADS = {
    "rm", "mv", "cp", "chmod", "chown", "sudo", "su",
    "curl", "wget", "python", "bash", "sh", "zsh", "npm", "npx",
}

_FORBIDDEN_GIT_SUBCOMMANDS = {
    "add", "commit", "push", "reset", "checkout", "merge", "rebase",
}

_FORBIDDEN_SHELL_TOKENS = {">", ">>", "|", "&&", ";"}


def _split(raw: str) -> list[str]:
    # shell-like parsing, but execution remains shell=False
    try:
        return shlex.split(raw)
    except ValueError as exc:
        raise ReadOnlyExecutionRejected(f"Invalid command syntax: {exc}") from exc


def _reject_if_dangerous(parts: list[str]) -> None:
    if not parts:
        raise ReadOnlyExecutionRejected("Empty command")

    head = parts[0].lower()
    if head in _FORBIDDEN_HEADS:
        raise ReadOnlyExecutionRejected(f"Forbidden command: {head}")

    if head == "git" and len(parts) > 1 and parts[1].lower() in _FORBIDDEN_GIT_SUBCOMMANDS:
        raise ReadOnlyExecutionRejected(f"Forbidden git subcommand: {parts[1]}")

    for part in parts:
        if part in _FORBIDDEN_SHELL_TOKENS:
            raise ReadOnlyExecutionRejected(f"Forbidden shell token: {part}")


def validate_readonly_command(raw: str) -> list[str]:
    if not raw or not raw.strip():
        raise ReadOnlyExecutionRejected("Empty command")

    parts = _split(raw)
    _reject_if_dangerous(parts)

    if tuple(parts) in _ALLOWED_EXACT:
        return parts

    head = parts[0]
    if head not in _ALLOWED_PREFIXES:
        raise ReadOnlyExecutionRejected(f"Command not allowlisted: {head}")

    if head == "find":
        # keep find bounded
        if len(parts) < 2:
            raise ReadOnlyExecutionRejected("find requires a path")
        allowed_roots = {"tools", "src", "tests", "docs", "oracle_town"}
        if parts[1] not in allowed_roots:
            raise ReadOnlyExecutionRejected("find path must be a known project directory")

    if head == "sed":
        # require explicit bounded print form like sed -n 1,120p file
        if len(parts) < 4 or parts[1] != "-n" or not parts[2].endswith("p"):
            raise ReadOnlyExecutionRejected("sed must use bounded form: sed -n 1,120p file")

    return parts


def run_readonly(raw: str, cwd: str | Path = ".") -> ReadOnlyResult:
    command = validate_readonly_command(raw)
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        shell=False,
        text=True,
        capture_output=True,
        timeout=10,
    )
    return ReadOnlyResult(
        command=command,
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
    )
