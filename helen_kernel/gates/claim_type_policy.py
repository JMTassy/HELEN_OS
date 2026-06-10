"""
claim_type_policy.py — Pre-dispatch claim type gate.

Enforces: claim_type ∈ admissible_claim_types(operation, surface, epoch, authority)
before any cognition begins.

NON_SOVEREIGN. Produces BLOCKED/ALLOWED verdicts. No ledger writes.
Authority: NONE
"""

ADMISSIBLE_CLAIM_TYPES: dict[str, set[str]] = {
    "helen_say.fetch": {
        "OBSERVATION",
    },
    "helen_say.summarize": {
        "OBSERVATION",
        "PROPOSAL",
    },
    "autoresearch.epoch": {
        "OBSERVATION",
        "PROPOSAL",
        "AUDIT",
    },
    "gate.run": {
        "VERDICT",
        "AUDIT",
    },
    "executor.task": {
        "RECEIPT",
        "AUDIT",
    },
    "hal.epoch": {
        "PROPOSAL",
        "AUDIT",
        "OBSERVATION",
    },
}


def operation_key(dispatch: dict) -> str:
    """Deterministic operation key from dispatch metadata only. Never inspect content."""
    family = dispatch.get("family", "")
    op = dispatch.get("op", "")
    return f"{family}.{op}"


def admissible_claim_types(dispatch: dict) -> set[str]:
    key = operation_key(dispatch)
    return ADMISSIBLE_CLAIM_TYPES.get(key, set())


def validate_claim_type(dispatch: dict) -> dict:
    """
    Gate check: is the declared claim_type admissible for this operation?

    Returns dict with:
      ok: bool
      reason: "CLAIM_TYPE_ALLOWED" | "INADMISSIBLE_CLAIM_TYPE" | "UNKNOWN_OPERATION_CLASS"
      operation: str
      allowed: sorted list
      requested: str
    """
    requested = dispatch.get("claim_type")
    allowed = admissible_claim_types(dispatch)

    if not allowed:
        return {
            "ok": False,
            "reason": "UNKNOWN_OPERATION_CLASS",
            "operation": operation_key(dispatch),
            "allowed": [],
            "requested": requested,
        }

    if requested not in allowed:
        return {
            "ok": False,
            "reason": "INADMISSIBLE_CLAIM_TYPE",
            "operation": operation_key(dispatch),
            "allowed": sorted(allowed),
            "requested": requested,
        }

    return {
        "ok": True,
        "reason": "CLAIM_TYPE_ALLOWED",
        "operation": operation_key(dispatch),
        "allowed": sorted(allowed),
        "requested": requested,
    }


def pre_dispatch_guard(dispatch: dict) -> dict | None:
    """
    Drop-in guard for execution paths.
    Returns None if allowed; returns BLOCKED envelope if not.

    Usage:
        block = pre_dispatch_guard(dispatch)
        if block:
            return block
        return run_cognition(dispatch)
    """
    gate = validate_claim_type(dispatch)
    if gate["ok"]:
        return None
    return {
        "status": "BLOCKED",
        "gate": "K_TAU",
        "reason": gate["reason"],
        "operation": gate["operation"],
        "requested_claim_type": gate["requested"],
        "allowed_claim_types": gate["allowed"],
        "authority": "NONE",
    }
