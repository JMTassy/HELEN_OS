#!/usr/bin/env python3
"""
EGREGOR SUPERTEAM ORCHESTRATOR v0

FAN-OUT (Grok+Claude+Codex via CLI subscriptions)
  → JSON extraction + HAL gate (local)
  → Egregore aggregation
  → EGREGOR_WITNESS_V0 sidecar receipt (authority=false, never ledger)

Designed to sit on top of a local Gemma4 finetune (the proposer / HER).
Gemma imagines cheaply. The egregor witnesses.

NON_SOVEREIGN / TEMPLE LAYER ONLY.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

try:
    from .cli_adapters import (  # when imported as package
        CliResult,
        call_grok,
        call_claude,
        call_codex,
        Role,
    )
except ImportError:
    # when run as script
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from cli_adapters import (  # type: ignore
        CliResult,
        call_grok,
        call_claude,
        call_codex,
        Role,
    )

REPO = Path(__file__).resolve().parents[3]
EGREGOR_DIR = Path(__file__).resolve().parent
RUNS_DIR = EGREGOR_DIR / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

# ensure we can import cli_adapters when run directly
if str(EGREGOR_DIR) not in sys.path:
    sys.path.insert(0, str(EGREGOR_DIR))

# Local HAL firewall for the egregor layer (extends the codex_pilot one)
HAL_FORBIDDEN = [
    "town/ledger_v1.ndjson",
    "oracle_town/kernel",
    "helen_os/governance",
    "helen_os/schemas",
    "GOVERNANCE/",
    "mayor_",
    "rm -rf",
    "shutdown",
    ":(){",  # fork bomb
]

@dataclass
class Witness:
    role: Role
    content: str
    parsed: Optional[dict | list] = None
    latency_ms: int = 0
    error: Optional[str] = None
    hal_verdict: str = "PENDING"

@dataclass
class EgregorReceipt:
    schema: str = "EGREGOR_WITNESS_V0"
    authority_status: str = "NON_SOVEREIGN_EGREGOR"
    generated_at: str = ""
    intent: str = ""
    intent_sha: str = ""
    witnesses: list[dict] = field(default_factory=list)
    aggregation: dict = field(default_factory=dict)
    hal_summary: dict = field(default_factory=dict)
    notes: str = ""

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def extract_json(text: str) -> Optional[Any]:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # greedy find first balanced object or array
    m = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None

def hal_gate(text: str) -> dict:
    forbidden = next((p for p in HAL_FORBIDDEN if p in text), None)
    if forbidden:
        return {"verdict": "BLOCK", "reason": f"forbidden:{forbidden}"}
    if len(text) < 2:
        return {"verdict": "BLOCK", "reason": "empty_or_too_short"}
    return {"verdict": "PASS", "reason": "ok"}

def call_with_timeout(fn, prompt: str, timeout: int = 60) -> CliResult:
    """Wrapper that also fills latency."""
    t0 = time.monotonic()
    res = fn(prompt, timeout=timeout)
    res.latency_ms = int((time.monotonic() - t0) * 1000)
    return res

def run_egregor(intent: str, *, timeout: int = 90) -> EgregorReceipt:
    """Main entry: fan out to the three CLIs, gate, aggregate."""
    intent_sha = sha(intent)[:16]

    # 1. Fan-out (graceful: missing CLIs just get error entries)
    raw_results: dict[Role, CliResult] = {}
    for fn, role in [(call_grok, "grok"), (call_claude, "claude"), (call_codex, "codex")]:
        try:
            raw_results[role] = call_with_timeout(fn, intent, timeout=timeout)
        except Exception as e:
            raw_results[role] = CliResult(role=role, success=False, content="", raw="", latency_ms=0, error=str(e))

    # 2. Witness construction + HAL
    witnesses: list[Witness] = []
    for role, res in raw_results.items():
        w = Witness(
            role=role,
            content=res.content or res.raw,
            latency_ms=res.latency_ms,
            error=res.error,
        )
        if res.success and res.content:
            parsed = extract_json(res.content)
            w.parsed = parsed if isinstance(parsed, (dict, list)) else None
            gate = hal_gate(res.content)
            w.hal_verdict = gate["verdict"]
        else:
            w.hal_verdict = "ERROR"
        witnesses.append(w)

    # 3. Simple aggregation (majority presence + role notes)
    successful = [w for w in witnesses if w.hal_verdict == "PASS" and w.parsed is not None]
    blocked = [w for w in witnesses if w.hal_verdict == "BLOCK"]
    errors = [w for w in witnesses if w.hal_verdict == "ERROR"]

    aggregation = {
        "num_witnesses": len(witnesses),
        "num_success": len(successful),
        "num_blocked": len(blocked),
        "num_errored": len(errors),
        "roles_responded": [w.role for w in successful],
        "consensus_hint": "MULTI_WITNESS" if len(successful) >= 2 else ("SINGLE_WITNESS" if successful else "NO_WITNESS"),
    }

    hal_summary = {
        "overall": "PASS" if not blocked and successful else ("BLOCK" if blocked else "DEGRADED"),
        "blocked_roles": [w.role for w in blocked],
        "errored_roles": [w.role for w in errors],
    }

    receipt = EgregorReceipt(
        generated_at=now_iso(),
        intent=intent[:2000],
        intent_sha=intent_sha,
        witnesses=[{
            "role": w.role,
            "success": w.hal_verdict == "PASS",
            "latency_ms": w.latency_ms,
            "has_json": w.parsed is not None,
            "error": w.error,
            "hal": w.hal_verdict,
            "preview": (w.content or "")[:300],
        } for w in witnesses],
        aggregation=aggregation,
        hal_summary=hal_summary,
        notes="NON_SOVEREIGN_EGREGOR. Output is witness only. Never ledgered.",
    )

    # 4. Write sidecar
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RUNS_DIR / f"EGREGOR__{ts}__{intent_sha}.json"
    out.write_text(json.dumps(asdict(receipt), indent=2))

    return receipt

def main():
    import argparse, sys
    ap = argparse.ArgumentParser(description="EGREGOR superteam witness (CLI subscriptions)")
    ap.add_argument("intent", nargs="?", help="intent / query for the egregor")
    ap.add_argument("--intent-file", type=Path)
    ap.add_argument("--timeout", type=int, default=75)
    args = ap.parse_args()

    intent = args.intent or (args.intent_file.read_text() if args.intent_file else "").strip()
    if not intent:
        print("ERROR: provide intent or --intent-file", file=sys.stderr)
        return 2

    print(f"[EGREGOR] fanning out to grok+claude+codex for: {intent[:80]}...")
    r = run_egregor(intent, timeout=args.timeout)
    print(json.dumps({
        "schema": r.schema,
        "overall": r.hal_summary.get("overall"),
        "consensus": r.aggregation.get("consensus_hint"),
        "responded": r.aggregation.get("roles_responded"),
        "receipt": str(RUNS_DIR / f"EGREGOR__*.json"),
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
