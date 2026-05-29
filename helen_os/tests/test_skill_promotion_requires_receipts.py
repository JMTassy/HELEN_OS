"""Test: Skill promotion reducer enforces gate hierarchy."""
from __future__ import annotations

from helen_os.governance.canonical import sha256_prefixed
from helen_os.governance.reason_codes import ReasonCode
from helen_os.governance.skill_promotion_reducer import reduce_promotion_packet


def _make_valid_receipt():
    """Create a valid receipt with correct hash."""
    receipt_payload = {"receipt_id": "R1", "payload": {"data": "valid"}}
    receipt_with_hash = {
        "receipt_id": "R1",
        "payload": {"data": "valid"},
        "sha256": sha256_prefixed(receipt_payload),
    }
    return receipt_with_hash


def _make_valid_packet():
    """Create a minimal valid packet."""
    return {
        "schema_name": "SKILL_PROMOTION_PACKET_V1",
        "schema_version": "1.0.0",
        "packet_id": "P1",
        "skill_id": "S1",
        "candidate_version": "1.0.0",
        "lineage": {
            "parent_skill_id": "S0",
            "parent_version": "0.9.0",
            "proposal_sha256": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
        },
        "capability_manifest_sha256": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
        "doctrine_surface": {
            "law_surface_version": "v1",
            "transfer_required": False,
        },
        "evaluation": {
            "threshold_name": "accuracy",
            "threshold_value": 0.9,
            "observed_value": 0.95,
            "passed": True,
        },
        "receipts": [_make_valid_receipt()],
        "human_seal": "JM",
        "override": False,
    }


def _make_valid_state():
    """Create a minimal valid state."""
    return {
        "schema_name": "SKILL_LIBRARY_STATE_V1",
        "schema_version": "1.0.0",
        "law_surface_version": "v1",
        "active_skills": {
            "S0": {
                "active_version": "0.9.0",
                "status": "ACTIVE",
                "last_decision_id": "DEC0",
            }
        },
    }


def test_valid_packet_admitted():
    """A valid packet passes all gates and is ADMITTED."""
    packet = _make_valid_packet()
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "ADMITTED"
    assert result.reason_code == ReasonCode.OK_ADMITTED.value


def test_schema_invalid_rejected():
    """Packet with wrong schema_name is REJECTED."""
    packet = _make_valid_packet()
    packet["schema_name"] = "WRONG_SCHEMA"
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_SCHEMA_INVALID.value


def test_missing_receipts_rejected():
    """Packet with empty receipts list is REJECTED.

    After failure_class enum + receipts minItems:1 enrichment (GOVERNANCE_DECISION_V1),
    empty receipts triggers schema validation failure (ERR_SCHEMA_INVALID) before
    reaching the receipt-checking logic. This IS correct behavior: minItems:1
    is the schema-level enforcement of NO_RECEIPT = NO_SHIP.
    """
    packet = _make_valid_packet()
    packet["receipts"] = []
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_SCHEMA_INVALID.value


def test_invalid_receipt_hash_rejected():
    """Packet with receipt where sha256 doesn't match content is REJECTED."""
    packet = _make_valid_packet()
    # Create a receipt where the sha256 field doesn't match the actual content hash
    bad_receipt = {
        "receipt_id": "R1",
        "payload": {"data": "valid"},
        "sha256": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    }
    packet["receipts"] = [bad_receipt]
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_RECEIPT_HASH_MISMATCH.value


def test_parent_skill_missing_rejected():
    """Packet referencing non-existent parent is REJECTED."""
    packet = _make_valid_packet()
    packet["lineage"]["parent_skill_id"] = "S_NONEXISTENT"
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_CAPABILITY_DRIFT.value


def test_doctrine_mismatch_rejected():
    """Packet with mismatched law_surface_version is REJECTED."""
    packet = _make_valid_packet()
    packet["doctrine_surface"]["law_surface_version"] = "v2"
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_DOCTRINE_CONFLICT.value


def test_evaluation_failed_rejected():
    """Packet with evaluation.passed=False is REJECTED."""
    packet = _make_valid_packet()
    packet["evaluation"]["passed"] = False
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_THRESHOLD_NOT_MET.value


def test_transfer_required_but_missing_quarantined():
    """Packet with transfer_required but no evidence is QUARANTINED."""
    packet = _make_valid_packet()
    packet["doctrine_surface"]["transfer_required"] = True
    # Remove transfer_evidence entirely (not present at all)
    if "transfer_evidence" in packet:
        del packet["transfer_evidence"]
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "QUARANTINED"
    assert result.reason_code == ReasonCode.OK_QUARANTINED.value


def test_override_forbidden_rejected():
    """Packet with override=True is REJECTED — clean admission forbids override path."""
    packet = _make_valid_packet()
    packet["override"] = True
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_OVERRIDE_FORBIDDEN.value


def test_human_seal_missing_rejected():
    """Packet with human_seal=None is REJECTED — operator initials are required."""
    packet = _make_valid_packet()
    packet["human_seal"] = None
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_HUMAN_SEAL_MISSING.value


def test_transfer_required_with_evidence_admitted():
    """Packet with transfer_required and evidence is ADMITTED."""
    packet = _make_valid_packet()
    packet["doctrine_surface"]["transfer_required"] = True
    packet["transfer_evidence"] = {"proof": "valid"}
    state = _make_valid_state()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "ADMITTED"
    assert result.reason_code == ReasonCode.OK_ADMITTED.value
