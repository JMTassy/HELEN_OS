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

_FORBIDDEN_TOKENS = {
    "rm", "mv", "cp", "chmod", "chown", "sudo", "su",
    "git add", "git commit", "git push", "git reset", "git checkout",
    "curl", "wget", "python", "bash", "sh", "zsh", "npm", "npx",
    ">", ">>", "|", "&&", ";",
}


def _reject_if_dangerous(raw: str) -> None:
    lowered = raw.lower()
    for token in _FORBIDDEN_TOKENS:
        if token in lowered:
            raise ReadOnlyExecutionRejected(f"Forbidden token: {token}")


def _split(raw: str) -> list[str]:
    # intentionally simple: no shell=True, no pipes, no redirects
    return raw.strip().split()


def validate_readonly_command(raw: str) -> list[str]:
    if not raw or not raw.strip():
        raise ReadOnlyExecutionRejected("Empty command")

    _reject_if_dangerous(raw)
    parts = _split(raw)

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
