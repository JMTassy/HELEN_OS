"""
helen_sourcebound_object.py — SOURCEBOUND OBJECT OS V0

O_adm = SOURCE_BOUND + CLAIMS + EVIDENCE + RISK + VALIDATION + RECEIPT
If any required stage is skipped → pipeline raises ValueError.

authority=false  canon=NO_SHIP  class=CANDIDATE
See: docs/theory/ADMISSIBLE_OBJECT_COMPUTING_V1.md
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import json
from typing import Any


class ObjectStatus(str, Enum):
    DIRTY             = "DIRTY"
    SOURCE_BOUND      = "SOURCE_BOUND"
    CLAIM_SPLIT       = "CLAIM_SPLIT"
    EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
    RISK_FLAGGED      = "RISK_FLAGGED"
    VALIDATED         = "VALIDATED"
    RECEIPTED         = "RECEIPTED"
    ADMISSIBLE        = "ADMISSIBLE"
    REJECTED          = "REJECTED"


def canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(obj: Any) -> str:
    return hashlib.sha256(canon_json(obj)).hexdigest()


@dataclass(frozen=True)
class SourceboundObject:
    object_id:         str
    content:           str
    status:            ObjectStatus        = ObjectStatus.DIRTY
    source_ref:        str | None          = None
    claims:            tuple[str, ...]     = ()
    evidence_refs:     tuple[str, ...]     = ()
    risk_flags:        tuple[str, ...]     = ()
    validator_results: tuple[str, ...]     = ()
    receipt_ref:       str | None          = None
    replay_path:       str | None          = None
    authority:         bool                = False

    def hash(self) -> str:
        return sha256_hex(asdict(self))

    def bind_source(self, source_ref: str) -> "SourceboundObject":
        if not source_ref:
            raise ValueError("source_ref required")
        return SourceboundObject(
            **{**asdict(self), "source_ref": source_ref, "status": ObjectStatus.SOURCE_BOUND}
        )

    def split_claims(self, claims: list[str]) -> "SourceboundObject":
        if not self.source_ref:
            raise ValueError("cannot split claims before source binding")
        if not claims:
            raise ValueError("at least one claim required")
        return SourceboundObject(
            **{**asdict(self), "claims": tuple(claims), "status": ObjectStatus.CLAIM_SPLIT}
        )

    def attach_evidence(self, evidence_refs: list[str]) -> "SourceboundObject":
        if not self.claims:
            raise ValueError("cannot attach evidence before claim split")
        if not evidence_refs:
            raise ValueError("at least one evidence_ref required")
        return SourceboundObject(
            **{**asdict(self), "evidence_refs": tuple(evidence_refs), "status": ObjectStatus.EVIDENCE_ATTACHED}
        )

    def flag_risks(self, risk_flags: list[str]) -> "SourceboundObject":
        return SourceboundObject(
            **{**asdict(self), "risk_flags": tuple(risk_flags), "status": ObjectStatus.RISK_FLAGGED}
        )

    def validate(self, validator_results: list[str]) -> "SourceboundObject":
        if not self.evidence_refs:
            raise ValueError("cannot validate before evidence attachment")
        if not validator_results:
            raise ValueError("validator result required")
        status = (
            ObjectStatus.VALIDATED
            if all(v == "PASS" for v in validator_results)
            else ObjectStatus.REJECTED
        )
        return SourceboundObject(
            **{**asdict(self), "validator_results": tuple(validator_results), "status": status}
        )

    def attach_receipt(self, receipt_ref: str, replay_path: str) -> "SourceboundObject":
        if self.status != ObjectStatus.VALIDATED:
            raise ValueError("cannot receipt unvalidated object")
        if not receipt_ref or not replay_path:
            raise ValueError("receipt_ref and replay_path required")
        return SourceboundObject(
            **{**asdict(self), "receipt_ref": receipt_ref, "replay_path": replay_path, "status": ObjectStatus.RECEIPTED}
        )

    def admit(self) -> "SourceboundObject":
        if self.status != ObjectStatus.RECEIPTED:
            raise ValueError("cannot admit object without receipt")
        return SourceboundObject(
            **{**asdict(self), "status": ObjectStatus.ADMISSIBLE, "authority": False}
        )
