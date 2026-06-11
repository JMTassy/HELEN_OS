"""
Test: Skill promotion reducer Gate 7 — manifest registry enforcement.

These tests are RED until the governance patch (MANIFEST_GATE_V1) is
admitted through MAYOR. They document what Gate 7 must enforce.

Proposal: docs/proposals/MANIFEST_GATE_V1.md
Status: PENDING_MAYOR_REVIEW
"""
from __future__ import annotations

import pytest

from helen_os.governance.canonical import sha256_prefixed
from helen_os.governance.reason_codes import ReasonCode
from helen_os.governance.skill_promotion_reducer import reduce_promotion_packet

_MANIFEST_SHA = "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
_OTHER_SHA = "sha256:0000000000000000000000000000000000000000000000000000000000000000"


def _make_receipt():
    receipt_payload = {"receipt_id": "R1", "payload": {"data": "valid"}}
    return {
        "receipt_id": "R1",
        "payload": {"data": "valid"},
        "sha256": sha256_prefixed(receipt_payload),
    }


def _make_packet(skill_id: str = "S1", manifest_sha: str = _MANIFEST_SHA):
    return {
        "schema_name": "SKILL_PROMOTION_PACKET_V1",
        "schema_version": "1.0.0",
        "packet_id": "P1",
        "skill_id": skill_id,
        "candidate_version": "1.0.0",
        "lineage": {
            "parent_skill_id": "S0",
            "parent_version": "0.9.0",
            "proposal_sha256": _OTHER_SHA,
        },
        "capability_manifest_sha256": manifest_sha,
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
        "receipts": [_make_receipt()],
    }


def _make_state_no_manifests():
    """State without manifests registry — Gate 7 must pass (backward compat)."""
    return {
        "schema_name": "SKILL_LIBRARY_STATE_V1",
        "schema_version": "1.0.0",
        "law_surface_version": "v1",
        "active_skills": {
            "S0": {"active_version": "0.9.0", "status": "ACTIVE", "last_decision_id": "DEC0"}
        },
    }


def _make_state_with_manifests(allowed_skills: list[str] | None = None):
    """State with a manifest registry entry for _MANIFEST_SHA."""
    return {
        "schema_name": "SKILL_LIBRARY_STATE_V1",
        "schema_version": "1.0.0",
        "law_surface_version": "v1",
        "active_skills": {
            "S0": {"active_version": "0.9.0", "status": "ACTIVE", "last_decision_id": "DEC0"}
        },
        "manifests": {
            _MANIFEST_SHA: {
                "allowed_skills": allowed_skills if allowed_skills is not None else ["S1"],
            }
        },
    }


# ── Gate 7: backward compatibility (no registry) ─────────────────────────────

def test_no_manifest_registry_passes():
    """When active_state has no manifests key, Gate 7 must not block."""
    result = reduce_promotion_packet(_make_packet(), _make_state_no_manifests())
    assert result.decision == "ADMITTED"
    assert result.reason_code == ReasonCode.OK_ADMITTED.value


# ── Gate 7: manifest SHA not in registry ─────────────────────────────────────

def test_manifest_sha_not_in_registry_rejected():
    """Packet SHA that doesn't match any registry entry must be REJECTED."""
    unknown_sha = "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    packet = _make_packet(manifest_sha=unknown_sha)
    state = _make_state_with_manifests()
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_NOT_FOUND.value


# ── Gate 7: skill not in manifest's allowed_skills ────────────────────────────

def test_skill_not_in_manifest_allowed_skills_rejected():
    """skill_id not in manifest allowed_skills must be REJECTED."""
    packet = _make_packet(skill_id="S_UNAUTHORIZED")
    state = _make_state_with_manifests(allowed_skills=["S1", "S2"])
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_SKILL_UNAUTHORIZED.value


# ── Gate 7: valid manifest + allowed skill ────────────────────────────────────

def test_manifest_valid_and_skill_allowed_admitted():
    """Correct SHA in registry and skill_id in allowed_skills must be ADMITTED."""
    packet = _make_packet(skill_id="S1", manifest_sha=_MANIFEST_SHA)
    state = _make_state_with_manifests(allowed_skills=["S1"])
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "ADMITTED"
    assert result.reason_code == ReasonCode.OK_ADMITTED.value


# ── Gate 7: empty allowed_skills list ────────────────────────────────────────

def test_empty_allowed_skills_rejects_any_skill():
    """A manifest with empty allowed_skills must reject all skill promotions."""
    packet = _make_packet(skill_id="S1", manifest_sha=_MANIFEST_SHA)
    state = _make_state_with_manifests(allowed_skills=[])
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_SKILL_UNAUTHORIZED.value


# ── Gate ordering: manifest check must come after evaluation (Gate 6) ─────────

def test_gate_ordering_evaluation_fails_before_manifest_checked():
    """Evaluation failure must fire before manifest gate (gates run in order)."""
    packet = _make_packet(skill_id="S1", manifest_sha=_MANIFEST_SHA)
    packet["evaluation"]["passed"] = False
    state = _make_state_with_manifests(allowed_skills=["S1"])
    result = reduce_promotion_packet(packet, state)
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_THRESHOLD_NOT_MET.value
