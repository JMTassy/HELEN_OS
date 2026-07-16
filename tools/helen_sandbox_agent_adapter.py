#!/usr/bin/env python3
"""
helen_sandbox_agent_adapter.py — HELEN_SANDBOX_AGENT_ADAPTER_V0

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Wraps exactly one OpenAI Sandbox Agent (or equivalent sandbox coding agent) run
into a HELEN_SANDBOX_HARVEST_V0 packet.

Agent may: inspect files, run tests, propose patch.
Agent must emit the contract fields (or adapter normalizes).
HELEN always checks: AntiGhost, CapabilityRegistry, AuthorityLinter, forbidden path policy.

Final state for every wrapped run: HOLD_FOR_OPERATOR.

No ledger writes. No sovereign claims. Operator decides.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Policy constants (V0 inlined for tool portability; mirrors autoresearch_policy)
# ---------------------------------------------------------------------------

FORBIDDEN_PATH_PREFIXES = (
    "town/ledger_v1",
    "town/ledger_",
    "helen_kernel/",
    "oracle_town/kernel/",
    "oracle_town/skills/",
    "skills/",
    "admitted_canon",
    "helen_os/governance/",
    "helen_os/schemas/",
    "mayor_",
    "GOVERNANCE/CLOSURES/",
    "GOVERNANCE/TRANCHE_RECEIPTS/",
    "oracle_town/kernel",
)

KNOWN_SAFE_CAPABILITIES = frozenset({
    "inspect_files",
    "read_source",
    "list_dir",
    "run_tests",
    "execute_test_command",
    "propose_patch",
    "generate_diff",
    "local_receipt",
    "read_only_fs",
})

DANGEROUS_CAPABILITIES = frozenset({
    "write_ledger",
    "append_ledger",
    "direct_kernel_call",
    "kernel_mutation",
    "sovereign_write",
    "bypass_firewall",
    "sudo",
    "unrestricted_network",
    "outbound_call_unchecked",
    "privilege_escalation",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canon(obj: Any) -> str:
    """Deterministic canonical JSON for hashing (no spaces, sorted keys)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def check_forbidden_paths(changed_files: list[str]) -> list[str]:
    """Return violations for any path matching sovereign/forbidden prefixes."""
    violations: list[str] = []
    for path in changed_files or []:
        normalized = path.lstrip("/").replace("\\", "/")
        for prefix in FORBIDDEN_PATH_PREFIXES:
            if normalized.startswith(prefix) or ("/" + prefix) in normalized:
                violations.append(f"FORBIDDEN: {path!r} matches prefix {prefix!r}")
                break
    return violations


# ---------------------------------------------------------------------------
# HELEN checks
# ---------------------------------------------------------------------------

def anti_ghost_check(packet: dict[str, Any]) -> tuple[str, list[str]]:
    """AntiGhost: evidence of a real run must exist. No ghost claims."""
    findings: list[str] = []
    trace = packet.get("trace_id") or ""
    if not isinstance(trace, str) or not trace.strip():
        findings.append("missing or empty trace_id")

    diff = str(packet.get("diff_summary", "") or "").strip()
    files = packet.get("files_touched") or []
    tests = packet.get("tests_run") or {}
    total_tests = 0
    try:
        total_tests = int(tests.get("total", 0))
    except Exception:
        pass

    has_evidence = bool(diff) or (isinstance(files, list) and len(files) > 0) or (total_tests > 0)
    if not has_evidence:
        findings.append("no evidence of work (empty diff_summary + no files_touched + no tests)")

    lr = packet.get("local_receipt") or {}
    if not isinstance(lr, dict) or not lr.get("packet_hash"):
        findings.append("local_receipt missing or lacks packet_hash binding")

    verdict = "PASS" if not findings else "GHOST"
    return verdict, findings


def capability_registry_check(claims: list[str]) -> tuple[str, list[str]]:
    """CapabilityRegistry V0: record claims, flag dangerous or unknown."""
    findings: list[str] = []
    if not isinstance(claims, list):
        return "FLAGGED", ["capability_claims must be a list"]

    safe: list[str] = []
    flagged: list[str] = []
    for c in claims:
        if not isinstance(c, str):
            flagged.append(f"non-string claim: {c!r}")
            continue
        if c in DANGEROUS_CAPABILITIES:
            flagged.append(f"dangerous capability claimed: {c}")
        elif c not in KNOWN_SAFE_CAPABILITIES:
            # forward-compatible but noted
            flagged.append(f"unknown capability (recorded): {c}")
        else:
            safe.append(c)

    verdict = "PASS" if not flagged else "FLAGGED"
    return verdict, flagged or [f"accepted safe claims: {', '.join(safe) or 'none'}"]


def authority_linter_check(texts: list[str]) -> tuple[str, dict[str, Any]]:
    """AuthorityLinter: delegate to the canonical linter. Fail closed on HARD."""
    # Lazy import to keep CLI usable even if linter path changes slightly
    try:
        sys.path.insert(0, str(ROOT))
        from tools.validators.authority_language_linter import lint_text
    except Exception as e:  # pragma: no cover
        return "BLOCK", {"error": f"failed to load authority linter: {e}"}

    blob = "\n".join(t for t in texts if isinstance(t, str))
    result = lint_text(blob)
    verdict = result.verdict  # "PASS" or "BLOCK"
    return verdict, result.to_dict()


def forbidden_path_check(files_touched: list[str]) -> tuple[str, list[str]]:
    violations = check_forbidden_paths(files_touched or [])
    verdict = "PASS" if not violations else "VIOLATIONS"
    return verdict, violations


def run_helen_checks(packet: dict[str, Any]) -> dict[str, Any]:
    """Run all four required checks. Never suppresses findings."""
    anti, anti_findings = anti_ghost_check(packet)
    caps, cap_findings = capability_registry_check(packet.get("capability_claims") or [])
    auth_v, auth_detail = authority_linter_check(
        [packet.get("diff_summary", ""), packet.get("operator_task", "")]
    )
    forb_v, forb_findings = forbidden_path_check(packet.get("files_touched") or [])

    overall = "HOLD_FOR_OPERATOR"
    # If any check is terminal BLOCK / serious GHOST we still emit but mark clearly
    if auth_v == "BLOCK" or anti == "GHOST":
        overall = "HOLD_FOR_OPERATOR_WITH_FINDINGS"

    return {
        "anti_ghost": anti,
        "anti_ghost_findings": anti_findings,
        "capability_registry": caps,
        "capability_findings": cap_findings,
        "authority_linter": auth_v,
        "authority_detail": auth_detail,
        "forbidden_path": forb_v,
        "forbidden_findings": forb_findings,
        "overall": overall,
    }


# ---------------------------------------------------------------------------
# Packet construction + local receipt
# ---------------------------------------------------------------------------

def build_local_receipt(trace_id: str, packet_for_hash: dict[str, Any]) -> dict[str, Any]:
    # Exclude the receipt itself from the hash content
    content = {k: v for k, v in packet_for_hash.items() if k != "local_receipt"}
    return {
        "trace_id": trace_id,
        "packet_hash": _sha256_hex(_canon(content)),
        "generated_at": _utc_now(),
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "ledger_effect": "none",
    }


def wrap_sandbox_run(
    operator_task: str,
    agent_output: dict[str, Any],
    *,
    simulate: bool = False,
) -> dict[str, Any]:
    """Core wrapper. Normalizes agent output + required fields into harvest packet."""
    trace_id = agent_output.get("trace_id") or f"sbx-{uuid.uuid4().hex[:12]}"

    # Normalize required fields with safe defaults
    diff_summary = str(agent_output.get("diff_summary", agent_output.get("summary", "")) or "")
    tests_run = agent_output.get("tests_run") or {"passed": 0, "failed": 0, "total": 0}
    if isinstance(tests_run, dict):
        tests_run = {
            "passed": int(tests_run.get("passed", 0)),
            "failed": int(tests_run.get("failed", 0)),
            "total": int(tests_run.get("total", 0)),
            "command": tests_run.get("command"),
            "summary": tests_run.get("summary") or tests_run.get("stdout_tail"),
        }
    else:
        tests_run = {"passed": 0, "failed": 0, "total": 0}

    files_touched = list(agent_output.get("files_touched", []) or [])
    forbidden_self = list(agent_output.get("forbidden_paths_touched", []) or [])
    capability_claims = list(agent_output.get("capability_claims", []) or [])

    # Start building the packet (without receipt first for hash)
    packet: dict[str, Any] = {
        "schema": "HELEN_SANDBOX_HARVEST_V0",
        "trace_id": trace_id,
        "operator_task": operator_task,
        "diff_summary": diff_summary,
        "tests_run": tests_run,
        "files_touched": files_touched,
        "forbidden_paths_touched": forbidden_self,
        "capability_claims": capability_claims,
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "status": "HOLD_FOR_OPERATOR",
        "final": "HOLD_FOR_OPERATOR",
    }

    # Local receipt (agent may have supplied one; we (re)bind for HELEN)
    supplied_lr = agent_output.get("local_receipt")
    local_receipt = supplied_lr if isinstance(supplied_lr, dict) else {}
    packet["local_receipt"] = build_local_receipt(trace_id, {**packet, "local_receipt": local_receipt})

    # Re-verify forbidden from our policy (union with self-report)
    policy_violations = check_forbidden_paths(files_touched)
    if policy_violations:
        # Append detected (dedup)
        for v in policy_violations:
            if v not in packet["forbidden_paths_touched"]:
                packet["forbidden_paths_touched"].append(v)

    # HELEN checks
    helen_checks = run_helen_checks(packet)
    packet["helen_checks"] = helen_checks

    # Contract surface (per HELEN_SANDBOX_ADAPTER_RECEIPT_V0 / required output contract)
    # These are flattened top-level fields in addition to the rich helen_checks object.
    packet["tests_passed"] = int(tests_run.get("passed", 0))
    packet["authority_lint"] = helen_checks.get("authority_linter", "UNKNOWN")
    packet["anti_ghost"] = helen_checks.get("anti_ghost", "UNKNOWN")
    packet["local_receipt_present"] = bool(packet.get("local_receipt"))
    packet["admission"] = False
    # forbidden_paths_touched is kept as rich list; also expose boolean flag
    packet["forbidden_paths_touched_flag"] = len(packet.get("forbidden_paths_touched", [])) > 0

    # If simulate, mark provenance
    if simulate:
        packet["_simulate"] = True
        packet["diff_summary"] = (packet["diff_summary"] or "SIMULATED: demo patch for task.") + " [SIMULATE]"

    return packet


# ---------------------------------------------------------------------------
# Simulate a realistic agent output for a clean demo
# ---------------------------------------------------------------------------

def _simulate_agent_output(task: str) -> dict[str, Any]:
    # A "successful" sandbox agent run that touched only safe paths
    return {
        "trace_id": f"sbx-sim-{uuid.uuid4().hex[:10]}",
        "diff_summary": "Added regression guard in widget and tightened assertion in test_widget.py. No behavior change for happy path.",
        "tests_run": {
            "passed": 12,
            "failed": 0,
            "total": 12,
            "command": "python -m pytest tests/test_widget.py -q --tb=no",
            "summary": "12 passed in 0.8s",
        },
        "files_touched": [
            "src/widget.py",
            "tests/test_widget.py",
        ],
        "capability_claims": [
            "inspect_files",
            "read_source",
            "run_tests",
            "propose_patch",
            "generate_diff",
        ],
        "local_receipt": {
            "note": "produced by simulated sandbox agent",
        },
    }


# ---------------------------------------------------------------------------
# Sidecar emission (non-sovereign)
# ---------------------------------------------------------------------------

def emit_sidecars(packet: dict[str, Any], out_dir: Path | None = None) -> tuple[Path, Path]:
    trace = packet.get("trace_id", "unknown")
    base = out_dir or (ROOT / "artifacts" / "sandbox_harvest")
    base.mkdir(parents=True, exist_ok=True)

    harvest_path = base / f"harvest_{trace}.json"
    receipt_path = base / f"harvest_{trace}.local_receipt.json"

    # Write the full harvest packet (includes embedded local_receipt + checks)
    harvest_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Separate sidecar receipt for easy ingestion
    receipt = packet.get("local_receipt", {})
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return harvest_path, receipt_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="HELEN_SANDBOX_AGENT_ADAPTER_V0 — wrap one sandbox agent run as HELEN harvest packet (HOLD_FOR_OPERATOR)"
    )
    parser.add_argument("--task", required=True, help="Operator task string given to the agent")
    parser.add_argument("--simulate", action="store_true", help="Generate a clean demo packet (no external agent)")
    parser.add_argument("--ingest-json", type=Path, help="Path to JSON emitted by a real sandbox agent run")
    parser.add_argument("--emit-sidecar", action="store_true", help="Write non-sovereign sidecar files under artifacts/sandbox_harvest/")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the harvest packet to stdout")
    args = parser.parse_args()

    agent_output: dict[str, Any] = {}

    if args.simulate:
        agent_output = _simulate_agent_output(args.task)
    elif args.ingest_json:
        try:
            raw = Path(args.ingest_json).read_text(encoding="utf-8")
            agent_output = json.loads(raw)
        except Exception as e:
            print(f"ERROR: failed to load --ingest-json: {e}", file=sys.stderr)
            return 2
    else:
        # Minimal stdin fallback: read a JSON blob from stdin if no simulate/ingest
        try:
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                agent_output = json.loads(stdin_data)
        except Exception:
            pass

    if not agent_output and not args.simulate:
        # Last resort: create an empty-but-valid structure so checks can still run and show failures
        agent_output = {
            "trace_id": "",
            "diff_summary": "",
            "tests_run": {"passed": 0, "failed": 0, "total": 0},
            "files_touched": [],
            "capability_claims": [],
        }

    packet = wrap_sandbox_run(args.task, agent_output, simulate=args.simulate)

    if args.pretty or not args.emit_sidecar:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(packet, indent=2, ensure_ascii=False))

    if args.emit_sidecar:
        h_path, r_path = emit_sidecars(packet)
        print(f"\n[sidecar] harvest -> {h_path}", file=sys.stderr)
        print(f"[sidecar] receipt  -> {r_path}", file=sys.stderr)

    # Exit 0 on clean HOLD, 1 if any HELEN check produced a hard finding (still emitted)
    checks = packet.get("helen_checks", {})
    if checks.get("authority_linter") == "BLOCK" or checks.get("anti_ghost") == "GHOST":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())