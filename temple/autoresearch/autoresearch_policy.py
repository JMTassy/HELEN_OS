"""autoresearch_policy.py — Pure policy functions for HELEN Autoresearch.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

All functions are pure: no I/O, no network, no subprocess, no state mutation.
Caller is responsible for all I/O.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PACKET_SCHEMA = "AUTORESEARCH_PACKET_V1"

VALID_FINDING_TYPES = frozenset({
    "proposal",
    "risk",
    "doc_gap",
    "test_gap",
    "compost_candidate",
    "quest_candidate",
})

REQUIRED_PACKET_FIELDS = frozenset({
    "schema",
    "packet_id",
    "source_refs",
    "finding_type",
    "summary",
    "evidence",
    "risk_flags",
    "recommended_action",
    "authority",
    "sovereign",
    "canon",
    "ledger_effect",
    "reducer_required",
})

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

SELF_ADMISSION_PHRASES = frozenset({
    "self_admit",
    "self-admit",
    "auto_admit",
    "autoadmit",
    "bypass reducer",
    "skip reducer",
    "directly admit",
    "self admit",
    "admit without reducer",
    "override reducer",
    "self-promote",
    "self_promote",
    "auto promote",
    "auto_promote",
})

TRAINING_PHRASES = frozenset({
    "run training",
    "training job",
    "fine_tune",
    "finetune",
    "fine-tune",
    "train model",
    "training run",
    "gradient descent",
    "backprop",
})

NETWORK_PHRASES = frozenset({
    "fetch url",
    "make request",
    "call api",
    "http request",
    "wget ",
    "curl ",
    "requests.get",
    "requests.post",
    "urllib.request",
    "httpx",
    "aiohttp",
    "outbound call",
    "remote endpoint",
})

LEDGER_STAGED_SIGNALS = frozenset({
    "town/ledger_v1.ndjson",
    "town/ledger_",
})


# ---------------------------------------------------------------------------
# classify_finding
# ---------------------------------------------------------------------------

def classify_finding(
    summary: str,
    evidence: list[str],
    *,
    source_refs: list[str] | None = None,
    risk_flags: list[str] | None = None,
) -> str:
    """Classify a raw finding into a VALID_FINDING_TYPES label.

    Heuristic only — never authoritative. Returns a finding_type string.
    Caller should always let a human reviewer override.
    """
    text = (summary + " " + " ".join(evidence)).lower()

    if any(kw in text for kw in ("danger", "violation", "forbidden", "breach", "unsafe", "risk")):
        return "risk"
    if any(kw in text for kw in ("test missing", "test gap", "no test", "untested", "coverage gap")):
        return "test_gap"
    if any(kw in text for kw in ("doc missing", "doc gap", "undocumented", "missing doc", "no spec")):
        return "doc_gap"
    if any(kw in text for kw in ("compost", "stale", "obsolete", "dead code", "unused", "deprecated")):
        return "compost_candidate"
    if any(kw in text for kw in ("quest", "explore", "investigate", "open question", "unknown")):
        return "quest_candidate"
    return "proposal"


# ---------------------------------------------------------------------------
# validate_packet
# ---------------------------------------------------------------------------

def validate_packet(packet: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate an AUTORESEARCH_PACKET_V1 dict.

    Returns (ok, errors). ok=True only when errors is empty.
    Fails closed: any unknown or disallowed field value is an error.
    """
    errors: list[str] = []

    # Schema check
    if packet.get("schema") != PACKET_SCHEMA:
        errors.append(f"schema must be '{PACKET_SCHEMA}', got {packet.get('schema')!r}")

    # Required fields presence
    missing = REQUIRED_PACKET_FIELDS - set(packet.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    # Sovereignty invariants — fail closed
    if packet.get("authority") is not False:
        errors.append("authority must be false (boolean)")
    if packet.get("sovereign") is not False:
        errors.append("sovereign must be false (boolean)")
    if packet.get("canon") is not False:
        errors.append("canon must be false (boolean)")
    if packet.get("ledger_effect") != "none":
        errors.append(f"ledger_effect must be 'none', got {packet.get('ledger_effect')!r}")
    if packet.get("reducer_required") is not True:
        errors.append("reducer_required must be true (boolean)")

    # finding_type
    ft = packet.get("finding_type", "")
    if ft not in VALID_FINDING_TYPES:
        errors.append(f"finding_type must be one of {sorted(VALID_FINDING_TYPES)}, got {ft!r}")

    # evidence must be non-empty
    evidence = packet.get("evidence", [])
    if not isinstance(evidence, list) or len(evidence) == 0:
        errors.append("evidence must be a non-empty list")

    # source_refs must be a list
    if not isinstance(packet.get("source_refs", []), list):
        errors.append("source_refs must be a list")

    # Check recommended_action and summary for forbidden language
    text_to_scan = " ".join([
        str(packet.get("summary", "")),
        str(packet.get("recommended_action", "")),
    ]).lower()

    for phrase in SELF_ADMISSION_PHRASES:
        if phrase in text_to_scan:
            errors.append(f"self-admission language detected: {phrase!r}")

    for phrase in TRAINING_PHRASES:
        if phrase in text_to_scan:
            errors.append(f"training action detected: {phrase!r}")

    for phrase in NETWORK_PHRASES:
        if phrase in text_to_scan:
            errors.append(f"network action detected: {phrase!r}")

    return (len(errors) == 0), errors


# ---------------------------------------------------------------------------
# check_forbidden_paths
# ---------------------------------------------------------------------------

def check_forbidden_paths(changed_files: list[str]) -> list[str]:
    """Return list of violations: changed_files that touch sovereign/forbidden paths.

    Input is a list of relative file paths (as from git status --short).
    Returns empty list if clean.
    """
    violations: list[str] = []
    for path in changed_files:
        normalized = path.lstrip("/").replace("\\", "/")
        for prefix in FORBIDDEN_PATH_PREFIXES:
            if normalized.startswith(prefix) or ("/" + prefix) in normalized:
                violations.append(f"FORBIDDEN: {path!r} matches prefix {prefix!r}")
                break
    return violations


# ---------------------------------------------------------------------------
# check_stop_conditions
# ---------------------------------------------------------------------------

def check_stop_conditions(
    *,
    staged_files: list[str] | None = None,
    changed_files: list[str] | None = None,
    text_output: str = "",
    loop_count: int = 0,
    operator_queue_depth: int = 0,
    tests_passed: bool = True,
    test_scope: str = "",
    attempted_action: str = "",
) -> tuple[bool, str]:
    """Evaluate all stop conditions.

    Returns (should_stop, reason). If should_stop=True, caller must halt immediately.
    Fails closed: any ambiguous condition stops the run.
    """
    # Input validation — fail closed on malformed input
    if text_output is None or not isinstance(text_output, str):
        return (True, "STOP_MALFORMED: text_output is not a string")
    if tests_passed is not True:
        return (True, "STOP_TESTS_NOT_PASSED")

    staged = staged_files or []
    changed = changed_files or []

    # Ledger staged
    for f in staged:
        for signal in LEDGER_STAGED_SIGNALS:
            if signal in f:
                return True, f"STOP: ledger file appears staged: {f!r}"

    # Kernel path in changed files
    violations = check_forbidden_paths(changed)
    if violations:
        return True, f"STOP: forbidden path in changed files: {violations[0]}"

    # Kernel path in staged files
    staged_violations = check_forbidden_paths(staged)
    if staged_violations:
        return True, f"STOP: forbidden path in staged files: {staged_violations[0]}"

    # Secrets in text output (simple heuristic)
    secret_signals = ("api_key", "secret_key", "private_key", "password=", "token=", "bearer ")
    lower_output = text_output.lower()
    for sig in secret_signals:
        if sig in lower_output:
            return True, f"STOP: possible secret detected in output: {sig!r}"

    # Evidence gap — output exists but no evidence markers
    if text_output and len(text_output) > 100:
        if "evidence" not in lower_output and "source_ref" not in lower_output:
            return True, "STOP: output lacks evidence references"

    # Loop repeat
    if loop_count >= 2:
        return True, f"STOP: same loop repeated {loop_count} times without new findings"

    # Operator queue ceiling
    if operator_queue_depth > 10:
        return True, f"STOP: operator queue depth {operator_queue_depth} exceeds threshold"

    # Test failure outside allowed scope
    if not tests_passed:
        allowed = ("test_autoresearch", "autoresearch_policy")
        if not any(kw in test_scope for kw in allowed):
            return True, f"STOP: test failure outside allowed scope: {test_scope!r}"

    # Self-commit / self-admit attempt
    action_lower = attempted_action.lower()
    self_action_signals = ("git commit", "git push", "self_admit", "bypass reducer", "directly admit")
    for sig in self_action_signals:
        if sig in action_lower:
            return True, f"STOP: self-commit or self-admit attempted: {sig!r}"

    return False, ""
