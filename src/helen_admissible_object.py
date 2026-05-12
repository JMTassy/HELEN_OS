"""
helen_admissible_object.py — ADMISSIBLE OBJECT COMPUTING scaffold

O_adm = β(O_raw, S, E, V, R, ρ)
If any required field is missing → ∅ (AdmissibleObject.EMPTY)

authority=false  canon=NO_SHIP  class=CANDIDATE
See: docs/theory/ADMISSIBLE_OBJECT_COMPUTING_V1.md
"""
from __future__ import annotations
import dataclasses, uuid, time
from typing import List, Optional

# ── Status stages (monotone forward only) ─────────────────────────────────
DIRTY             = "DIRTY"
SOURCE_BOUND      = "SOURCE_BOUND"
CLAIM_SPLIT       = "CLAIM_SPLIT"
EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
RISK_FLAGGED      = "RISK_FLAGGED"
VALIDATED         = "VALIDATED"
RECEIPTED         = "RECEIPTED"
ADMISSIBLE        = "ADMISSIBLE"
EMPTY             = "EMPTY"   # ∅ — failed admissibility

STAGE_ORDER = [
    DIRTY, SOURCE_BOUND, CLAIM_SPLIT, EVIDENCE_ATTACHED,
    RISK_FLAGGED, VALIDATED, RECEIPTED, ADMISSIBLE,
]


@dataclasses.dataclass
class AdmissibleObject:
    object_id:         str
    status:            str
    source_ref:        Optional[str]
    claims:            List[str]
    evidence_refs:     List[str]
    risk_flags:        List[str]
    validator_results: List[str]
    receipt_ref:       Optional[str]
    replay_path:       Optional[str]
    created_ts:        float
    authority:         bool = False   # always False — invariant

    def is_empty(self) -> bool:
        return self.status == EMPTY

    def is_admissible(self) -> bool:
        return self.status == ADMISSIBLE

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def new_dirty(cls, source_ref: Optional[str] = None) -> "AdmissibleObject":
        return cls(
            object_id=str(uuid.uuid4()),
            status=DIRTY,
            source_ref=source_ref,
            claims=[],
            evidence_refs=[],
            risk_flags=[],
            validator_results=[],
            receipt_ref=None,
            replay_path=None,
            created_ts=time.time(),
        )

    @classmethod
    def empty(cls) -> "AdmissibleObject":
        return cls(
            object_id="∅",
            status=EMPTY,
            source_ref=None,
            claims=[],
            evidence_refs=[],
            risk_flags=[],
            validator_results=[],
            receipt_ref=None,
            replay_path=None,
            created_ts=time.time(),
        )


def beta(
    obj: AdmissibleObject,
    source: Optional[str],
    evidence: List[str],
    validator_result: str,        # "PASS" or "FAIL"
    receipt: Optional[str],
    replay_path: Optional[str],
) -> AdmissibleObject:
    """
    Admissibility reducer: O_adm = β(O_raw, S, E, V, R, ρ)
    Returns ∅ if any required field is absent or validator fails.
    """
    if not source:
        return AdmissibleObject.empty()
    if not evidence:
        return AdmissibleObject.empty()
    if validator_result != "PASS":
        return AdmissibleObject.empty()
    if not receipt:
        return AdmissibleObject.empty()
    if not replay_path:
        return AdmissibleObject.empty()

    return AdmissibleObject(
        object_id=obj.object_id,
        status=ADMISSIBLE,
        source_ref=source,
        claims=list(obj.claims),
        evidence_refs=list(evidence),
        risk_flags=list(obj.risk_flags),
        validator_results=[validator_result],
        receipt_ref=receipt,
        replay_path=replay_path,
        created_ts=obj.created_ts,
        authority=False,  # invariant — never True
    )


def bind_source(obj: AdmissibleObject, source_ref: str) -> AdmissibleObject:
    return dataclasses.replace(obj, status=SOURCE_BOUND, source_ref=source_ref)


def split_claim(obj: AdmissibleObject, claim: str) -> AdmissibleObject:
    return dataclasses.replace(obj, status=CLAIM_SPLIT, claims=obj.claims + [claim])


def attach_evidence(obj: AdmissibleObject, ev_ref: str) -> AdmissibleObject:
    return dataclasses.replace(obj, status=EVIDENCE_ATTACHED, evidence_refs=obj.evidence_refs + [ev_ref])


def flag_risk(obj: AdmissibleObject, flag: str) -> AdmissibleObject:
    return dataclasses.replace(obj, status=RISK_FLAGGED, risk_flags=obj.risk_flags + [flag])
