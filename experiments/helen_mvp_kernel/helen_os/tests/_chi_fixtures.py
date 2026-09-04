"""Shared fixtures for the χ⁺ witness suite. 🔵 OBSERVED · NON_SOVEREIGN."""
from __future__ import annotations

from helen_os.kernel.admission_types import (
    HumanSeal,
    TypedAdmissionReceipt,
    Witness,
    candidate_hash_of,
    receipt_hash,
)
from helen_os.ledger.hash_chain import GENESIS_HASH

PROPOSER_SEAT = "goblin-01"
PROPOSER_ROOTS = frozenset({"root:proposer"})

CANDIDATE = {"kind": "test_candidate", "value": 42}
C_HASH = candidate_hash_of(CANDIDATE)


def good_witnesses() -> tuple:
    return (
        Witness("w1", seat="hal-seat", provenance_roots=frozenset({"root:hal"})),
        Witness("w2", seat="operator-seat", provenance_roots=frozenset({"root:op"})),
    )


def make_receipt(*, witnesses=None, prev=GENESIS_HASH, pre="a" * 64, post="b" * 64,
                 candidate_hash=None) -> TypedAdmissionReceipt:
    return TypedAdmissionReceipt(
        receipt_id="r_test_001",
        candidate_hash=candidate_hash or C_HASH,
        pre_state_hash=pre,
        post_state_hash=post,
        prev_receipt_hash=prev,
        witnesses=good_witnesses() if witnesses is None else witnesses,
    )


def seal_for(r: TypedAdmissionReceipt) -> HumanSeal:
    return HumanSeal(binds_receipt_hash=receipt_hash(r))
