"""Test: ManifestRegistry — all five required behaviors."""
from __future__ import annotations

import pytest

from helen_os.manifest_registry import ManifestRegistry, ManifestRegistrationError


def _valid_manifest(
    manifest_id: str = "M1",
    allowed_skills: list[str] | None = None,
) -> dict:
    return {
        "manifest_id": manifest_id,
        "authority": "NONE",
        "allowed_skills": allowed_skills if allowed_skills is not None else ["S1", "S2"],
        "domain_category": "reasoning",
        "provider_class": "INTERNAL",
        "provenance": {"source": "test"},
    }


# ── valid manifest registers ──────────────────────────────────────────────────

def test_valid_manifest_registers():
    reg = ManifestRegistry()
    record = reg.register(_valid_manifest())
    assert record.manifest_id == "M1"
    assert record.authority == "NONE"
    assert "S1" in record.allowed_skills
    assert reg.get("M1") is record


# ── non-NONE authority rejected ───────────────────────────────────────────────

def test_non_none_authority_rejected():
    reg = ManifestRegistry()
    m = _valid_manifest()
    m["authority"] = "MAYOR"
    with pytest.raises(ManifestRegistrationError, match="authority"):
        reg.register(m)


def test_sovereign_authority_rejected():
    reg = ManifestRegistry()
    m = _valid_manifest()
    m["authority"] = "SOVEREIGN"
    with pytest.raises(ManifestRegistrationError, match="authority"):
        reg.register(m)


# ── duplicate manifest_id with different hash rejected ────────────────────────

def test_duplicate_manifest_id_same_content_is_idempotent():
    reg = ManifestRegistry()
    r1 = reg.register(_valid_manifest())
    r2 = reg.register(_valid_manifest())  # same content
    assert r1 is r2


def test_duplicate_manifest_id_different_hash_rejected():
    reg = ManifestRegistry()
    reg.register(_valid_manifest(allowed_skills=["S1"]))
    m2 = _valid_manifest(allowed_skills=["S1", "S2"])  # different content → different hash
    with pytest.raises(ManifestRegistrationError, match="different hash"):
        reg.register(m2)


# ── skill link succeeds when allowed ─────────────────────────────────────────

def test_skill_link_succeeds_when_allowed():
    reg = ManifestRegistry()
    reg.register(_valid_manifest(allowed_skills=["S1", "S2"]))
    reg.link_skill("S1", "M1")
    found = reg.get_manifest_for_skill("S1")
    assert found is not None
    assert found.manifest_id == "M1"


# ── skill link fails when not in allowed_skills ───────────────────────────────

def test_skill_link_fails_when_not_allowed():
    reg = ManifestRegistry()
    reg.register(_valid_manifest(allowed_skills=["S1"]))
    with pytest.raises(ManifestRegistrationError, match="not in allowed_skills"):
        reg.link_skill("S_OTHER", "M1")


def test_skill_link_fails_when_manifest_not_registered():
    reg = ManifestRegistry()
    with pytest.raises(ManifestRegistrationError, match="not registered"):
        reg.link_skill("S1", "M_NONEXISTENT")


# ── validate_skill_allowed ────────────────────────────────────────────────────

def test_validate_skill_allowed_returns_true_for_valid():
    reg = ManifestRegistry()
    record = reg.register(_valid_manifest(allowed_skills=["S1"]))
    assert reg.validate_skill_allowed("S1", "M1", record.manifest_hash) is True


def test_validate_skill_allowed_wrong_hash_returns_false():
    reg = ManifestRegistry()
    reg.register(_valid_manifest(allowed_skills=["S1"]))
    assert reg.validate_skill_allowed("S1", "M1", "sha256:" + "0" * 64) is False


def test_validate_skill_allowed_unknown_manifest_returns_false():
    reg = ManifestRegistry()
    assert reg.validate_skill_allowed("S1", "M_UNKNOWN", "sha256:" + "0" * 64) is False


def test_validate_skill_allowed_skill_not_in_list_returns_false():
    reg = ManifestRegistry()
    record = reg.register(_valid_manifest(allowed_skills=["S1"]))
    assert reg.validate_skill_allowed("S_OTHER", "M1", record.manifest_hash) is False


# ── required fields validation ────────────────────────────────────────────────

def test_missing_manifest_id_raises():
    reg = ManifestRegistry()
    m = _valid_manifest()
    del m["manifest_id"]
    with pytest.raises(ManifestRegistrationError, match="manifest_id"):
        reg.register(m)


def test_missing_domain_category_raises():
    reg = ManifestRegistry()
    m = _valid_manifest()
    del m["domain_category"]
    with pytest.raises(ManifestRegistrationError, match="domain_category"):
        reg.register(m)


def test_missing_provider_class_raises():
    reg = ManifestRegistry()
    m = _valid_manifest()
    del m["provider_class"]
    with pytest.raises(ManifestRegistrationError, match="provider_class"):
        reg.register(m)


def test_missing_allowed_skills_raises():
    reg = ManifestRegistry()
    m = _valid_manifest()
    del m["allowed_skills"]
    with pytest.raises(ManifestRegistrationError, match="allowed_skills"):
        reg.register(m)


# ── get_by_hash ───────────────────────────────────────────────────────────────

def test_get_by_hash_returns_record():
    reg = ManifestRegistry()
    record = reg.register(_valid_manifest())
    found = reg.get_by_hash(record.manifest_hash)
    assert found is record


def test_get_by_hash_unknown_returns_none():
    reg = ManifestRegistry()
    assert reg.get_by_hash("sha256:" + "f" * 64) is None
