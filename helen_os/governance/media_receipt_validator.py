"""
Validator for MEDIA_RECEIPT_V1.

Binds the schema defined in docs/proposals/MEDIA_RECEIPT_V1.md into
executable rules. Wraps the IDENTITY_GATE_RECEIPT_V1_SEQUENCE verdict;
does NOT re-implement identity logic.

HAL boundary:
    MEDIA_RECEIPT proves the media chain exists.
    It does NOT prove the media is admitted.
    Admissibility is still reducer-only.

Authority: NON_SOVEREIGN. Never writes, never mutates.
"""
from __future__ import annotations

from typing import Any


# Sub-ledger path (V1 §7) — distinct from frame and sequence ledgers
MEDIA_RECEIPT_LEDGER_PATH = "ledgers/media_receipt_v1.ndjson"

# Identity-sequence verdicts that map to each admissibility status (V1 §5)
VERDICT_ELIGIBLE       = {"PASS"}
VERDICT_CANDIDATE_ONLY = {"REWORK"}
VERDICT_BLOCKING       = {"REJECT"}


def validate_media_receipt(
    receipt: dict[str, Any],
    *,
    identity_sequence_store: dict[str, dict[str, Any]] | None = None,
    style_gate_store: dict[str, bool] | None = None,
    artifact_gate_store: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """
    Validate a MEDIA_RECEIPT_V1 against the doctrine.

    Args:
        receipt: the receipt dict to validate (NOT mutated)
        identity_sequence_store: {hash: sequence_receipt_dict} for verdict lookup
        style_gate_store:    {hash: True} for optional style gate existence check
        artifact_gate_store: {hash: True} for optional artifact gate existence check

    Returns:
        {
          "valid": bool,
          "violations": list[str],          # violation codes
          "admissibility_status": str,      # "ELIGIBLE" | "CANDIDATE_ONLY" | "BLOCKED"
          "details": list[str],
        }
    """
    violations: list[str] = []
    details: list[str] = []

    def fail(code: str, msg: str) -> None:
        violations.append(code)
        details.append(f"{code}: {msg}")

    # Default state — gets refined as we walk the checks
    admissibility_status = "BLOCKED"

    # ── Top-level required fields ─────────────────────────────────────────────
    if receipt.get("type") != "MEDIA_RECEIPT_V1":
        fail("WRONG_TYPE", f"type must be MEDIA_RECEIPT_V1, got {receipt.get('type')!r}")

    for field in ("media_receipt_id", "project_id"):
        if not receipt.get(field):
            fail(f"MISSING_{field.upper()}", f"required field {field!r} missing or empty")

    # ── Required laws §2 — laws 1 and 2 (authority + admissible) ──────────────
    if receipt.get("authority") is not False:
        fail("AUTHORITY_VIOLATION", "authority must be false (NON_SOVEREIGN)")

    if receipt.get("admissible") is not False:
        fail("ADMISSIBILITY_VIOLATION",
             "admissible must be false (media receipt does not admit canon)")

    if receipt.get("claim") != "NO_CLAIM":
        fail("CLAIM_VIOLATION", f"claim must be 'NO_CLAIM', got {receipt.get('claim')!r}")

    # ── Required asset_chain fields ──────────────────────────────────────────
    asset_chain = receipt.get("asset_chain", {})
    if not asset_chain.get("source_refs_hash"):
        fail("MISSING_SOURCE_REFS_HASH",
             "asset_chain.source_refs_hash required to bind the source")
    if not asset_chain.get("render_hash"):
        fail("MISSING_RENDER_HASH",
             "asset_chain.render_hash required to bind the rendered output")

    # ── Required gate_chain.identity_gate_sequence_receipt_hash ───────────────
    gate_chain = receipt.get("gate_chain", {})
    id_seq_hash = gate_chain.get("identity_gate_sequence_receipt_hash")
    if not id_seq_hash:
        fail("MISSING_IDENTITY_SEQUENCE",
             "gate_chain.identity_gate_sequence_receipt_hash required — "
             "Media Receipt wraps an identity sequence receipt")

    # ── Resolve identity sequence verdict from the store ──────────────────────
    sequence_verdict: str | None = None
    if id_seq_hash and identity_sequence_store is not None:
        if id_seq_hash not in identity_sequence_store:
            fail("MISSING_IDENTITY_SEQUENCE",
                 f"identity_gate_sequence_receipt_hash {id_seq_hash!r} "
                 f"not present in identity sequence store")
        else:
            seq_receipt = identity_sequence_store[id_seq_hash]
            sequence_verdict = (seq_receipt.get("decision") or {}).get("verdict")
            if sequence_verdict is None:
                fail("BAD_IDENTITY_SEQUENCE",
                     f"identity sequence receipt {id_seq_hash!r} has no decision.verdict")

    # ── Optional gates: if referenced, must exist in their stores ─────────────
    style_hash = gate_chain.get("style_gate_receipt_hash")
    if style_hash and style_gate_store is not None and style_hash not in style_gate_store:
        fail("REFERENCED_GATE_MISSING",
             f"style_gate_receipt_hash {style_hash!r} referenced but not in style gate store")

    artifact_hash = gate_chain.get("artifact_gate_receipt_hash")
    if artifact_hash and artifact_gate_store is not None and artifact_hash not in artifact_gate_store:
        fail("REFERENCED_GATE_MISSING",
             f"artifact_gate_receipt_hash {artifact_hash!r} referenced but not in artifact gate store")

    # ── Compute admissibility_status from the identity sequence verdict ───────
    # (laws 4, 5, 6 from §2)
    if sequence_verdict in VERDICT_ELIGIBLE:
        admissibility_status = "ELIGIBLE"
    elif sequence_verdict in VERDICT_CANDIDATE_ONLY:
        admissibility_status = "CANDIDATE_ONLY"
        # Receipt is still valid; admissibility is blocked but candidacy stands
    elif sequence_verdict in VERDICT_BLOCKING:
        admissibility_status = "BLOCKED"
        fail("BLOCKED_BY_REJECT",
             "identity sequence verdict is REJECT — media receipt validity is blocked")
    elif sequence_verdict is not None:
        admissibility_status = "BLOCKED"
        fail("UNKNOWN_IDENTITY_SEQUENCE_VERDICT",
             f"identity sequence verdict {sequence_verdict!r} is not recognized")

    # If we found a candidacy block in the receipt, sanity-check it matches
    # what we computed (the receipt is allowed to assert; we audit it).
    declared = (receipt.get("candidacy") or {}).get("admissibility_status")
    if declared is not None and declared != admissibility_status:
        # This is a soft inconsistency — the validator's computed status wins,
        # but flag the mismatch.
        fail("CANDIDACY_MISMATCH",
             f"declared candidacy.admissibility_status={declared!r} "
             f"differs from computed {admissibility_status!r}")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "admissibility_status": admissibility_status,
        "details": details,
    }
