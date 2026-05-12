"""
tests/test_helen_sourcebound_object.py — falsification suite for SourceboundObject

Invariants under test:
  1. authority is always False — even after full admission
  2. Pipeline enforces strict stage ordering
  3. REJECTED status blocks receipt attachment
  4. Full pipeline reaches ADMISSIBLE
  5. Hash is deterministic
  6. Empty source/claims/evidence raise ValueError
"""
import pytest
from src.helen_sourcebound_object import SourceboundObject, ObjectStatus


def test_dirty_object_starts_without_authority():
    obj = SourceboundObject(object_id="obj_001", content="Muse Spark signals ambient AI.")
    assert obj.status == ObjectStatus.DIRTY
    assert obj.authority is False
    assert obj.source_ref is None


def test_full_pipeline_reaches_admissible_without_authority():
    obj = SourceboundObject(object_id="obj_001", content="Muse Spark signals ambient AI.")
    obj = obj.bind_source("src_meta_muse_spark_2026")
    obj = obj.split_claims(["AI is moving toward multimodal ambient surfaces."])
    obj = obj.attach_evidence(["ev_meta_announcement_hash"])
    obj = obj.flag_risks(["external_market_signal_not_internal_proof"])
    obj = obj.validate(["PASS"])
    obj = obj.attach_receipt("rcpt_001", "replay/sourcebound/obj_001")
    obj = obj.admit()
    assert obj.status == ObjectStatus.ADMISSIBLE
    assert obj.authority is False
    assert obj.receipt_ref == "rcpt_001"
    assert obj.replay_path == "replay/sourcebound/obj_001"


def test_no_claim_split_before_source():
    obj = SourceboundObject(object_id="obj_001", content="raw")
    with pytest.raises(ValueError, match="source binding"):
        obj.split_claims(["claim"])


def test_no_evidence_before_claim():
    obj = SourceboundObject(object_id="obj_001", content="raw").bind_source("src_001")
    with pytest.raises(ValueError, match="claim split"):
        obj.attach_evidence(["ev_001"])


def test_no_receipt_before_validation():
    obj = (
        SourceboundObject(object_id="obj_001", content="raw")
        .bind_source("src_001")
        .split_claims(["claim"])
        .attach_evidence(["ev_001"])
    )
    with pytest.raises(ValueError, match="unvalidated"):
        obj.attach_receipt("rcpt_001", "replay_001")


def test_rejected_validation_blocks_receipt():
    obj = (
        SourceboundObject(object_id="obj_001", content="raw")
        .bind_source("src_001")
        .split_claims(["claim"])
        .attach_evidence(["ev_001"])
        .validate(["FAIL"])
    )
    assert obj.status == ObjectStatus.REJECTED
    with pytest.raises(ValueError):
        obj.attach_receipt("rcpt_001", "replay_001")


def test_mixed_validator_results_rejects():
    obj = (
        SourceboundObject(object_id="obj_002", content="mixed signal")
        .bind_source("src_001")
        .split_claims(["claim"])
        .attach_evidence(["ev_001"])
        .validate(["PASS", "FAIL"])
    )
    assert obj.status == ObjectStatus.REJECTED


def test_admit_requires_receipt():
    obj = (
        SourceboundObject(object_id="obj_001", content="raw")
        .bind_source("src_001")
        .split_claims(["claim"])
        .attach_evidence(["ev_001"])
        .validate(["PASS"])
    )
    with pytest.raises(ValueError, match="without receipt"):
        obj.admit()


def test_authority_false_even_after_admission():
    obj = (
        SourceboundObject(object_id="obj_001", content="raw", authority=True)
        .bind_source("src_001")
        .split_claims(["claim"])
        .attach_evidence(["ev_001"])
        .validate(["PASS"])
        .attach_receipt("rcpt_001", "replay_001")
        .admit()
    )
    assert obj.authority is False


def test_hash_is_deterministic():
    obj1 = SourceboundObject(object_id="obj_001", content="raw")
    obj2 = SourceboundObject(object_id="obj_001", content="raw")
    assert obj1.hash() == obj2.hash()


def test_hash_changes_on_mutation():
    obj1 = SourceboundObject(object_id="obj_001", content="raw")
    obj2 = obj1.bind_source("src_001")
    assert obj1.hash() != obj2.hash()


def test_empty_source_ref_raises():
    obj = SourceboundObject(object_id="obj_001", content="raw")
    with pytest.raises(ValueError):
        obj.bind_source("")


def test_empty_claims_raises():
    obj = SourceboundObject(object_id="obj_001", content="raw").bind_source("src_001")
    with pytest.raises(ValueError):
        obj.split_claims([])


def test_empty_evidence_raises():
    obj = (
        SourceboundObject(object_id="obj_001", content="raw")
        .bind_source("src_001")
        .split_claims(["claim"])
    )
    with pytest.raises(ValueError):
        obj.attach_evidence([])


def test_risk_flags_optional_stage():
    obj = (
        SourceboundObject(object_id="obj_001", content="raw")
        .bind_source("src_001")
        .split_claims(["claim"])
        .attach_evidence(["ev_001"])
        .flag_risks(["low_confidence"])
    )
    assert obj.status == ObjectStatus.RISK_FLAGGED
    assert "low_confidence" in obj.risk_flags


def test_object_is_immutable():
    obj = SourceboundObject(object_id="obj_001", content="raw")
    with pytest.raises(Exception):
        obj.status = ObjectStatus.ADMISSIBLE
