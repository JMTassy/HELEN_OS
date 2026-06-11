"""Frozen reason codes for HELEN OS MVP.

Law:
- Reason codes are a closed vocabulary.
- No upstream component may invent new sovereign decision codes.
- Reducers and validators may emit only codes defined here.
- Codes are stable identifiers, not prose.

Scope:
- Decision outcomes
- Validation errors
- Governance rejection/quarantine reasons
- Replay / hash / schema integrity failures

Non-goals:
- Human-readable explanations
- Dynamic code generation
- Localization / UI phrasing
"""
from __future__ import annotations

from enum import Enum
from typing import Final


# -------------------------------------------------------------------------
# Decision outcomes
# -------------------------------------------------------------------------


class DecisionOutcome(str, Enum):
    """Frozen sovereign decision outcomes."""
    ADMITTED = "ADMITTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    ROLLED_BACK = "ROLLED_BACK"


DECISION_OUTCOMES: Final[frozenset[str]] = frozenset(
    outcome.value for outcome in DecisionOutcome
)


# -------------------------------------------------------------------------
# Validation / membrane reason codes
# -------------------------------------------------------------------------


class ReasonCode(str, Enum):
    """Frozen governance reason codes."""

    # Success / stable control flow
    OK_VALID = "OK_VALID"
    OK_ADMITTED = "OK_ADMITTED"
    OK_REJECTED = "OK_REJECTED"
    OK_QUARANTINED = "OK_QUARANTINED"
    OK_ROLLED_BACK = "OK_ROLLED_BACK"

    # Generic schema / registry failures
    ERR_SCHEMA_UNKNOWN = "ERR_SCHEMA_UNKNOWN"
    ERR_SCHEMA_INVALID = "ERR_SCHEMA_INVALID"
    ERR_SCHEMA_NAME_MISMATCH = "ERR_SCHEMA_NAME_MISMATCH"
    ERR_SCHEMA_VERSION_MISMATCH = "ERR_SCHEMA_VERSION_MISMATCH"
    ERR_UNKNOWN_FIELD = "ERR_UNKNOWN_FIELD"

    # Canonicalization / hash failures
    ERR_CANONICALIZATION_FAILED = "ERR_CANONICALIZATION_FAILED"
    ERR_HASH_FORMAT_INVALID = "ERR_HASH_FORMAT_INVALID"
    ERR_HASH_MISMATCH = "ERR_HASH_MISMATCH"

    # Artifact / receipt integrity failures
    ERR_ARTIFACT_MISSING = "ERR_ARTIFACT_MISSING"
    ERR_ARTIFACT_REF_UNRESOLVED = "ERR_ARTIFACT_REF_UNRESOLVED"
    ERR_RECEIPT_MISSING = "ERR_RECEIPT_MISSING"
    ERR_RECEIPT_HASH_MISMATCH = "ERR_RECEIPT_HASH_MISMATCH"

    # Handoff / sovereignty boundary failures
    ERR_NON_SOVEREIGN_ATTESTATION_MISSING = "ERR_NON_SOVEREIGN_ATTESTATION_MISSING"
    ERR_SOVEREIGN_FIELD_FORBIDDEN = "ERR_SOVEREIGN_FIELD_FORBIDDEN"
    ERR_TRUTH_CLAIM_FORBIDDEN = "ERR_TRUTH_CLAIM_FORBIDDEN"
    ERR_DOCTRINE_MUTATION_FORBIDDEN = "ERR_DOCTRINE_MUTATION_FORBIDDEN"

    # Governance / promotion failures
    ERR_PACKET_INVALID = "ERR_PACKET_INVALID"
    ERR_CAPABILITY_DRIFT = "ERR_CAPABILITY_DRIFT"
    ERR_LINEAGE_INVALID = "ERR_LINEAGE_INVALID"
    ERR_DOCTRINE_CONFLICT = "ERR_DOCTRINE_CONFLICT"
    ERR_LAW_SURFACE_MISMATCH = "ERR_LAW_SURFACE_MISMATCH"
    ERR_REDUCER_VERSION_MISMATCH = "ERR_REDUCER_VERSION_MISMATCH"
    ERR_THRESHOLD_NOT_MET = "ERR_THRESHOLD_NOT_MET"
    ERR_TRANSFER_EVIDENCE_INSUFFICIENT = "ERR_TRANSFER_EVIDENCE_INSUFFICIENT"
    ERR_ROLLBACK_TRIGGER = "ERR_ROLLBACK_TRIGGER"
    # Manifest / capability registry failures
    ERR_MANIFEST_NOT_FOUND = "ERR_MANIFEST_NOT_FOUND"
    ERR_MANIFEST_SKILL_UNAUTHORIZED = "ERR_MANIFEST_SKILL_UNAUTHORIZED"

    # Replay / determinism failures
    ERR_REPLAY_PROOF_FAILED = "ERR_REPLAY_PROOF_FAILED"
    ERR_LEDGER_REPLAY_FAILED = "ERR_LEDGER_REPLAY_FAILED"
    ERR_ENVIRONMENT_MISMATCH = "ERR_ENVIRONMENT_MISMATCH"

    # Batch / execution invariants
    ERR_STATE_MUTATION_WITHOUT_ADMISSION = "ERR_STATE_MUTATION_WITHOUT_ADMISSION"
    ERR_LEDGER_EXTENSION_WITHOUT_DECISION = "ERR_LEDGER_EXTENSION_WITHOUT_DECISION"
    ERR_LEDGER_CHAIN_INVALID = "ERR_LEDGER_CHAIN_INVALID"
    ERR_DECISION_INVALID = "ERR_DECISION_INVALID"


REASON_CODES: Final[frozenset[str]] = frozenset(
    code.value for code in ReasonCode
)


# -------------------------------------------------------------------------
# Reserved sovereign field names
# -------------------------------------------------------------------------


RESERVED_SOVEREIGN_KEYS: Final[frozenset[str]] = frozenset(
    {
        "verdict",
        "truth_status",
        "state_mutation",
        "ship",
        "no_ship",
    }
)


# -------------------------------------------------------------------------
# Helper predicates
# -------------------------------------------------------------------------


def is_valid_reason_code(value: str) -> bool:
    """Return True iff value is a frozen reason code."""
    return value in REASON_CODES


def is_valid_decision_outcome(value: str) -> bool:
    """Return True iff value is a frozen decision outcome."""
    return value in DECISION_OUTCOMES
