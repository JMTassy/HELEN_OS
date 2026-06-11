"""
Test: Reducer manifest gate v2 — new gate order and manifest_id/manifest_hash fields.

RED until docs/proposals/code/skill_promotion_reducer_v2.py is promoted to
helen_os/governance/skill_promotion_reducer.py AND reason_codes additions
are promoted to helen_os/governance/reason_codes.py.

Gate order after patch:
  1. schema
  2. manifest legitimacy  ← NEW (was absent)
  3. receipts present
  4. receipt hash integrity
  5. parent capability
  6. doctrine match
  7. threshold
"""
from __future__ import annotations

import pytest

from helen_os.governance.canonical import sha256_prefixed
from helen_os.governance.reason_codes import ReasonCode
from helen_os.governance.skill_promotion_reducer import reduce_promotion_packet

_MANIFEST_ID = "M1"
_MANIFEST_HASH = "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
_ZERO_HASH = "sha256:" + "0" * 64


def _receipt():
    payload = {"receipt_id": "R1", "payload": {"data": "ok"}}
    return {"receipt_id": "R1", "payload": {"data": "ok"}, "sha256": sha256_prefixed(payload)}


def _packet(**overrides):
    base = {
        "schema_name": "SKILL_PROMOTION_PACKET_V1",
        "schema_version": "1.0.0",
        "packet_id": "P1",
        "skill_id": "S1",
        "candidate_version": "1.0.0",
        "lineage": {
            "parent_skill_id": "S0",
            "parent_version": "0.9.0",
            "proposal_sha256": _ZERO_HASH,
        },
        "manifest_id": _MANIFEST_ID,
        "manifest_hash": _MANIFEST_HASH,
        "domain_category": "reasoning",
        "provider_class": "INTERNAL",
        "capability_manifest_sha256": _MANIFEST_HASH,
        "doctrine_surface": {"law_surface_version": "v1", "transfer_required": False},
        "evaluation": {
            "threshold_name": "accuracy",
            "threshold_value": 0.9,
            "observed_value": 0.95,
            "passed": True,
        },
        "receipts": [_receipt()],
    }
    base.update(overrides)
    return base


def _state(manifests=None):
    s = {
        "schema_name": "SKILL_LIBRARY_STATE_V1",
        "schema_version": "1.0.0",
        "law_surface_version": "v1",
        "active_skills": {
            "S0": {"active_version": "0.9.0", "status": "ACTIVE", "last_decision_id": "D0"}
        },
    }
    if manifests is not None:
        s["manifests"] = manifests
    return s


def _valid_manifests():
    return {_MANIFEST_HASH: {"manifest_id": _MANIFEST_ID, "allowed_skills": ["S1"]}}


# ── Gate 2: manifest legitimacy — new gate ────────────────────────────────────

def test_missing_manifest_id_rejected():
    """manifest_id absent in packet → REJECTED at manifest gate."""
    p = _packet()
    del p["manifest_id"]
    result = reduce_promotion_packet(p, _state(_valid_manifests()))
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_NOT_FOUND.value


def test_unknown_manifest_id_rejected():
    """manifest_id not in active_state manifests registry → REJECTED."""
    p = _packet(manifest_id="M_UNKNOWN")
    result = reduce_promotion_packet(p, _state(_valid_manifests()))
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_NOT_FOUND.value


def test_wrong_manifest_hash_rejected():
    """manifest_hash in packet doesn't match registry entry → REJECTED."""
    p = _packet(manifest_hash="sha256:" + "f" * 64)
    result = reduce_promotion_packet(p, _state(_valid_manifests()))
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_NOT_FOUND.value


def test_skill_not_allowed_by_manifest_rejected():
    """skill_id not in manifest allowed_skills → REJECTED."""
    manifests = {_MANIFEST_HASH: {"manifest_id": _MANIFEST_ID, "allowed_skills": ["S_OTHER"]}}
    p = _packet()
    result = reduce_promotion_packet(p, _state(manifests))
    assert result.decision == "REJECTED"
    assert result.reason_code == ReasonCode.ERR_MANIFEST_SKILL_UNAUTHORIZED.value


# ── full valid path ───────────────────────────────────────────────────────────

def test_admit_only_when_manifest_and_receipts_both_validate():
    """Only when manifest gate + receipt gate both pass → ADMITTED."""
    result = reduce_promotion_packet(_packet(), _state(_valid_manifests()))
    assert result.decision == "ADMITTED"
    assert result.reason_code == ReasonCode.OK_ADMITTED.value


# ── gate ordering: manifest check is Gate 2 (before receipts Gate 3) ─────────

def test_manifest_gate_fires_before_receipt_gate():
    """Missing manifest_id fires before receipt hash check (Gate 2 < Gate 4)."""
    p = _packet()
    del p["manifest_id"]
    # corrupt receipt hash — would fail at Gate 4; manifest gate (Gate 2) fires first
    p["receipts"][0]["sha256"] = "sha256:" + "f" * 64
    result = reduce_promotion_packet(p, _state(_valid_manifests()))
    assert result.decision == "REJECTED"
    # Must be manifest error, not receipt-hash error
    assert result.reason_code == ReasonCode.ERR_MANIFEST_NOT_FOUND.value


# ── backward compat: no manifests registry → gate passes ─────────────────────

def test_no_manifests_registry_passes_gate():
    """When active_state has no manifests key, manifest gate must not block."""
    result = reduce_promotion_packet(_packet(), _state(manifests=None))
    assert result.decision == "ADMITTED"
