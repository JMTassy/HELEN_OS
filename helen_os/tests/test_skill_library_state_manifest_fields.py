"""Test: State updater stores manifest provenance fields on ADMITTED decisions."""
from __future__ import annotations

from helen_os.state.skill_library_state_updater import apply_skill_promotion_decision


def _base_state():
    return {
        "schema_name": "SKILL_LIBRARY_STATE_V1",
        "schema_version": "1.0.0",
        "law_surface_version": "v1",
        "active_skills": {},
    }


def _admitted_decision():
    return {
        "schema_name": "SKILL_PROMOTION_DECISION_V1",
        "schema_version": "1.0.0",
        "decision_id": "dec_001",
        "skill_id": "skill.search",
        "candidate_version": "1.2.0",
        "decision_type": "ADMITTED",
        "reason_code": "EVAL_PASS",
        "candidate_identity_hash": "sha256:" + "c" * 64,
    }


def _full_packet():
    return {
        "schema_name": "SKILL_PROMOTION_PACKET_V1",
        "schema_version": "1.0.0",
        "packet_id": "P1",
        "skill_id": "skill.search",
        "candidate_version": "1.2.0",
        "manifest_id": "M1",
        "manifest_hash": "sha256:" + "a" * 64,
        "domain_category": "reasoning",
        "provider_class": "INTERNAL",
    }


# ── backward compatibility: no packet → base fields only ─────────────────────

def test_admitted_without_packet_stores_base_fields():
    result = apply_skill_promotion_decision(_base_state(), _admitted_decision())
    entry = result["active_skills"]["skill.search"]
    assert entry["active_version"] == "1.2.0"
    assert entry["status"] == "ACTIVE"
    assert entry["last_decision_id"] == "dec_001"
    assert "manifest_id" not in entry
    assert "manifest_hash" not in entry


# ── with packet → manifest provenance stored ─────────────────────────────────

def test_admitted_with_packet_stores_manifest_id():
    result = apply_skill_promotion_decision(
        _base_state(), _admitted_decision(), _full_packet()
    )
    entry = result["active_skills"]["skill.search"]
    assert entry["manifest_id"] == "M1"


def test_admitted_with_packet_stores_manifest_hash():
    result = apply_skill_promotion_decision(
        _base_state(), _admitted_decision(), _full_packet()
    )
    entry = result["active_skills"]["skill.search"]
    assert entry["manifest_hash"] == "sha256:" + "a" * 64


def test_admitted_with_packet_stores_domain_category():
    result = apply_skill_promotion_decision(
        _base_state(), _admitted_decision(), _full_packet()
    )
    entry = result["active_skills"]["skill.search"]
    assert entry["domain_category"] == "reasoning"


def test_admitted_with_packet_stores_provider_class():
    result = apply_skill_promotion_decision(
        _base_state(), _admitted_decision(), _full_packet()
    )
    entry = result["active_skills"]["skill.search"]
    assert entry["provider_class"] == "INTERNAL"


def test_admitted_with_packet_stores_all_six_fields():
    result = apply_skill_promotion_decision(
        _base_state(), _admitted_decision(), _full_packet()
    )
    entry = result["active_skills"]["skill.search"]
    for key in ("active_version", "status", "last_decision_id",
                "manifest_id", "manifest_hash", "domain_category", "provider_class"):
        assert key in entry, f"missing field: {key}"


# ── non-ADMITTED decisions ignore packet ─────────────────────────────────────

def test_rejected_with_packet_does_not_mutate_state():
    dec = _admitted_decision()
    dec["decision_type"] = "REJECTED"
    dec["reason_code"] = "EVAL_FAIL"
    del dec["candidate_identity_hash"]
    result = apply_skill_promotion_decision(_base_state(), dec, _full_packet())
    assert result["active_skills"] == {}


# ── partial packet: only present fields stored ────────────────────────────────

def test_partial_packet_stores_only_present_manifest_fields():
    packet = {"manifest_id": "M2"}  # only manifest_id present
    result = apply_skill_promotion_decision(_base_state(), _admitted_decision(), packet)
    entry = result["active_skills"]["skill.search"]
    assert entry["manifest_id"] == "M2"
    assert "manifest_hash" not in entry
    assert "domain_category" not in entry
    assert "provider_class" not in entry
