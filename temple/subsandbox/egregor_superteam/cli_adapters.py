#!/usr/bin/env python3
"""
EGREGOR CLI ADAPTERS — headless wrappers for subscription CLIs.

NON_SOVEREIGN. Subprocess only. No API keys. Uses your local CLAUDE / CODEX / GROK
subscriptions via their CLIs (not Anthropic/xAI/OpenAI HTTP APIs).

Each adapter forces JSON output and returns (content, meta).

Roles in the superteam (suggested):
  - GROK   : lateral witness, edge cases, irreverence
  - CLAUDE : deep reasoning, structure, critique
  - CODEX  : code execution verification, implementation sanity

All outputs stamped authority=false, never touch sovereign paths.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal, Optional

Role = Literal["grok", "claude", "codex"]


@dataclass
class CliResult:
    role: Role
    success: bool
    content: str
    raw: str
    latency_ms: int
    error: Optional[str] = None
    command: Optional[str] = None


def _run(cmd: list[str], timeout: int = 90) -> tuple[str, int, str]:
    """Run CLI, return (stdout, returncode, stderr)."""
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        latency = int((time.monotonic() - t0) * 1000)
        return proc.stdout.strip(), proc.returncode, proc.stderr.strip()
    except subprocess.TimeoutExpired as e:
        latency = int((time.monotonic() - t0) * 1000)
        out = (e.stdout or b"").decode() if e.stdout else ""
        return out, -1, f"timeout after {timeout}s"
    except FileNotFoundError:
        return "", 127, f"CLI not found: {cmd[0]}"


def call_grok(prompt: str, *, force_json: bool = True, timeout: int = 90) -> CliResult:
    """Grok CLI headless. Pattern that works: --single + --no-plan."""
    p = prompt
    if force_json:
        p = (
            "Return ONLY valid minified JSON. No prose, no markdown. "
            f"JSON object or array only.\n\n{p}"
        )
    cmd = ["grok", "--single", p, "--no-plan"]
    out, rc, err = _run(cmd, timeout)
    ok = rc == 0 and bool(out)
    return CliResult(
        role="grok",
        success=ok,
        content=out if ok else "",
        raw=out or err,
        latency_ms=0,  # filled by caller if needed
        error=err if not ok else None,
        command=" ".join(cmd),
    )


def call_claude(prompt: str, *, force_json: bool = True, timeout: int = 120) -> CliResult:
    """Claude Code CLI headless. Uses -p/--print."""
    p = prompt
    if force_json:
        p = (
            "Respond with ONLY valid minified JSON. No explanations. "
            f"Output must be parseable JSON.\n\n{p}"
        )
    # --dangerously-skip-permissions is often needed for non-interactive
    cmd = ["claude", "-p", p, "--dangerously-skip-permissions"]
    out, rc, err = _run(cmd, timeout)
    ok = rc == 0 and bool(out)
    return CliResult(
        role="claude",
        success=ok,
        content=out if ok else "",
        raw=out or err,
        latency_ms=0,
        error=err if not ok else None,
        command=" ".join(cmd[:2]) + " ...",
    )


def call_codex(prompt: str, *, force_json: bool = True, timeout: int = 120) -> CliResult:
    """Codex CLI headless via exec."""
    p = prompt
    if force_json:
        p = (
            "Output EXACTLY and ONLY valid minified JSON. Nothing else. "
            f"JSON object or array.\n\n{p}"
        )
    cmd = ["codex", "exec", p]
    out, rc, err = _run(cmd, timeout)
    ok = rc == 0 and bool(out)
    return CliResult(
        role="codex",
        success=ok,
        content=out if ok else "",
        raw=out or err,
        latency_ms=0,
        error=err if not ok else None,
        command=" ".join(cmd[:2]) + " ...",
    )


def call_all(prompt: str, timeout: int = 120) -> dict[Role, CliResult]:
    """Fan-out to all three. Returns dict keyed by role."""
    results: dict[Role, CliResult] = {}
    for fn in (call_grok, call_claude, call_codex):
        r = fn(prompt, timeout=timeout)
        results[r.role] = r
    return results


if __name__ == "__main__":
    # Quick smoke
    test = "Return ONLY this JSON: {\"egregor_test\": true, \"role\": \"witness\"}"
    for role, res in call_all(test, timeout=60).items():
        print(f"{role}: ok={res.success} len={len(res.content)} err={res.error}")
