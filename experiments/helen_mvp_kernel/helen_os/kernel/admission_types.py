"""Typed admission objects + ValidReceiptPath — 🔵 OBSERVED · NON_SOVEREIGN sandbox.

Fences:
  - a receipt cannot self-declare SEALED/ADMITTED (construction-time TypeError)
  - witness independence is a decidable predicate (seat + provenance roots),
    never an LLM judgment
  - orphan receipts (no admitted parent) fail the path: receipt-shaped data
    is not receipt authority
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from helen_os.ledger.hash_chain import canonical_json, sha256_hex

FORBIDDEN_SELF_STATUS = {"SEALED", "ADMITTED"}


@dataclass(frozen=True)
class Witness:
    witness_id: str
    seat: str
    provenance_roots: frozenset  # roots via DERIVED_FROM closure, declared


@dataclass(frozen=True)
class HumanSeal:
    binds_receipt_hash: str


@dataclass(frozen=True)
class TypedAdmissionReceipt:
    receipt_id: str
    candidate_hash: str
    pre_state_hash: str
    post_state_hash: str
    prev_receipt_hash: str
    witnesses: tuple  # tuple[Witness, ...]
    status: str = "CANDIDATE"

    def __post_init__(self) -> None:
        if self.status in FORBIDDEN_SELF_STATUS:
            raise TypeError(
                f"SELF_ATTESTATION: receipt may not declare status={self.status!r}; "
                "SEALED/ADMITTED are granted by the kernel, never self-assigned"
            )


def receipt_hash(r: TypedAdmissionReceipt) -> str:
    body = {
        "receipt_id": r.receipt_id,
        "candidate_hash": r.candidate_hash,
        "pre_state_hash": r.pre_state_hash,
        "post_state_hash": r.post_state_hash,
        "prev_receipt_hash": r.prev_receipt_hash,
        "witnesses": sorted(w.witness_id for w in r.witnesses),
        "status": r.status,
    }
    return sha256_hex(canonical_json(body))


def candidate_hash_of(payload: dict) -> str:
    return sha256_hex(canonical_json(payload))


def independent(witnesses: tuple, proposer_seat: str, proposer_roots: frozenset) -> bool:
    """Decidable independence: no proposer seat, disjoint provenance roots, ≥2 seats."""
    if not witnesses:
        return False
    seats = {w.seat for w in witnesses}
    if proposer_seat in seats:
        return False
    for w in witnesses:
        if w.provenance_roots & proposer_roots:
            return False
    return len(seats) >= 2


@dataclass(frozen=True)
class PathResult:
    overall: str                 # PASS | FAIL | UNKNOWN
    checks: dict = field(default_factory=dict)
    reason: str = ""


def valid_receipt_path(
    receipt: Optional[TypedAdmissionReceipt],
    candidate_payload: Optional[dict],
    tip_hash: str,
    seal: Optional[HumanSeal],
    *,
    proposer_seat: str,
    proposer_roots: frozenset,
    admitted_index: Optional[set] = None,
) -> PathResult:
    if receipt is None or candidate_payload is None:
        return PathResult("FAIL", {}, "NO_RECEIPT")

    checks: dict = {}
    checks["typed"] = receipt.status not in FORBIDDEN_SELF_STATUS
    checks["binds_candidate"] = receipt.candidate_hash == candidate_hash_of(candidate_payload)
    checks["pre_neq_post"] = receipt.pre_state_hash != receipt.post_state_hash
    checks["chain_ok"] = receipt.prev_receipt_hash == tip_hash
    checks["seal_binds"] = seal is not None and seal.binds_receipt_hash == receipt_hash(receipt)

    if not receipt.witnesses:
        checks["witnesses_present"] = False
        return PathResult("UNKNOWN", checks, "MISSING_WITNESS")
    checks["witnesses_present"] = True
    checks["witnesses_independent"] = independent(
        receipt.witnesses, proposer_seat, proposer_roots
    )

    if admitted_index is not None and receipt.candidate_hash not in admitted_index:
        checks["admitted_parent"] = False
        return PathResult("FAIL", checks, "ORPHAN_RECEIPT: NO_ADMITTED_PARENT")

    if all(checks.values()):
        return PathResult("PASS", checks, "")
    failed = [k for k, v in checks.items() if not v]
    return PathResult("FAIL", checks, "FAILED:" + ",".join(failed))


def evaluate_admission(path: Optional[PathResult]) -> str:
    """Route a path result. PASS is ADMIT-ELIGIBLE — the kernel admits, not this fn."""
    if path is None:
        return "REJECT"
    return {"FAIL": "REJECT", "UNKNOWN": "HOLD", "PASS": "ADMIT_ELIGIBLE"}[path.overall]
