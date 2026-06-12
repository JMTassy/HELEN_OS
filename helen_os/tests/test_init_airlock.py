"""
Tests for the /init constitutional airlock.
Covers all 6 checks from PERSONA_ENTRY_SHELL_V1.md §3.

NON_SOVEREIGN — these tests produce no ledger writes.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from helen_os.persona_entry_shell import InitAirlock, AirlockRejected, ContextPacket


# ── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture()
def storage(tmp_path):
    """Temporary storage directory with valid session + epoch state."""
    s = tmp_path / "storage"
    s.mkdir()
    (s / "last_session_v1.json").write_text(json.dumps({
        "schema": "SESSION_LOG_V1",
        "session_id": "TEST-001",
        "ended_at": "2026-06-12T00:00:00Z",
        "open_threads": ["test thread"],
    }))
    (s / "epoch_state_v1.json").write_text(json.dumps({
        "schema": "EPOCH_STATE_V1",
        "epoch_id": "E50",
        "last_result": "GREEN",
        "pass_count": 584,
    }))
    return str(s)


@pytest.fixture()
def empty_storage(tmp_path):
    """Existing directory but no session/epoch files."""
    s = tmp_path / "empty_storage"
    s.mkdir()
    return str(s)


@pytest.fixture()
def absent_storage(tmp_path):
    """Non-existent directory."""
    return str(tmp_path / "does_not_exist")


_VALID_SCOPE = {"domain": "HELEN_OS", "permission_tier": "READ_ONLY"}
_EXEC_SCOPE = {"domain": "HELEN_OS", "permission_tier": "EXECUTION"}
_SANDBOX_SCOPE = {"domain": "TEMPLE", "permission_tier": "SANDBOX"}


# ── Check 1: memory source ───────────────────────────────────────────

def test_memory_source_storage(storage):
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    assert packet.memory_source == "storage"
    assert packet.prior_context is not None
    assert packet.prior_context["loaded_from"] == "storage"


def test_memory_source_absent_dir(absent_storage):
    packet = InitAirlock(absent_storage, _VALID_SCOPE).open()
    assert packet.memory_source == "absent"
    assert packet.prior_context is None


def test_memory_source_empty_dir(empty_storage):
    packet = InitAirlock(empty_storage, _VALID_SCOPE).open()
    assert packet.memory_source == "absent"
    assert packet.prior_context is None


# ── Check 2: no fabrication ──────────────────────────────────────────

def test_no_fabrication_absent_memory_has_null_prior(absent_storage):
    packet = InitAirlock(absent_storage, _VALID_SCOPE).open()
    assert packet.prior_context is None, "absent memory must yield null prior_context"
    assert packet.fabricated is False


def test_fabricated_field_always_false(storage):
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    assert packet.fabricated is False


# ── Check 3: scope resolved ──────────────────────────────────────────

def test_scope_required(absent_storage):
    with pytest.raises(AirlockRejected) as exc_info:
        InitAirlock(absent_storage, {}).open()
    assert exc_info.value.check == "scope_resolved"


def test_scope_missing_domain(absent_storage):
    with pytest.raises(AirlockRejected) as exc_info:
        InitAirlock(absent_storage, {"permission_tier": "READ_ONLY"}).open()
    assert exc_info.value.check == "scope_resolved"
    assert "domain" in exc_info.value.reason


def test_scope_missing_tier(absent_storage):
    with pytest.raises(AirlockRejected) as exc_info:
        InitAirlock(absent_storage, {"domain": "HELEN_OS"}).open()
    assert exc_info.value.check == "scope_resolved"
    assert "permission_tier" in exc_info.value.reason


def test_scope_sovereign_tier_rejected(absent_storage):
    for tier in ("SOVEREIGN", "KERNEL", "LEDGER"):
        with pytest.raises(AirlockRejected) as exc_info:
            InitAirlock(absent_storage, {"domain": "HELEN_OS", "permission_tier": tier}).open()
        assert exc_info.value.check == "scope_resolved"
        assert "sovereign" in exc_info.value.reason.lower()


def test_scope_unknown_tier_rejected(absent_storage):
    with pytest.raises(AirlockRejected) as exc_info:
        InitAirlock(absent_storage, {"domain": "HELEN_OS", "permission_tier": "GOD_MODE"}).open()
    assert exc_info.value.check == "scope_resolved"


def test_valid_tiers_accepted(absent_storage):
    for tier in ("READ_ONLY", "EXECUTION", "SANDBOX"):
        packet = InitAirlock(absent_storage, {"domain": "HELEN_OS", "permission_tier": tier}).open()
        assert packet.scope["permission_tier"] == tier


# ── Check 4: runtime probe ───────────────────────────────────────────

def test_runtime_probe_present(absent_storage):
    packet = InitAirlock(absent_storage, _VALID_SCOPE).open()
    probe = packet.runtime_probe
    assert "probe_time" in probe
    assert "coupling_state" in probe
    assert "git_summary" in probe
    assert probe["coupling_state"] in ("COUPLED", "HARD_DRIFT", "PROBE_ERROR")


def test_runtime_probe_has_timestamp(absent_storage):
    packet = InitAirlock(absent_storage, _VALID_SCOPE).open()
    assert packet.runtime_probe["probe_time"].startswith("2026") or "T" in packet.runtime_probe["probe_time"]


# ── Check 5: packet marked non-sovereign ────────────────────────────

def test_packet_authority_nonsovereign(storage):
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    assert packet.authority == "NON_SOVEREIGN"


def test_packet_schema(storage):
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    assert packet.schema == "CONTEXT_PACKET_V1"
    assert packet.airlock_version == "V1"


def test_context_packet_rejects_wrong_authority():
    with pytest.raises(ValueError, match="authority must be NON_SOVEREIGN"):
        ContextPacket(
            packet_id="P1",
            assembled_at="2026-06-12T00:00:00Z",
            authority="SOVEREIGN",
            memory_source="absent",
            prior_context=None,
            scope=_VALID_SCOPE,
            runtime_probe={"probe_time": "now", "coupling_state": "COUPLED", "git_summary": ""},
        )


# ── Check 6: no mutation path ────────────────────────────────────────

def test_no_mutation_path_open(storage):
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    assert packet.mutation_path_open is False


def test_all_6_checks_recorded(storage):
    airlock = InitAirlock(storage, _VALID_SCOPE)
    airlock.open()
    expected = {
        "memory_source", "no_fabrication", "scope_resolved",
        "runtime_probe", "packet_nonsovereign", "no_mutation_path",
    }
    assert set(airlock.checks_passed) == expected


# ── Packet serialization ─────────────────────────────────────────────

def test_to_dict_roundtrip(storage):
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    d = packet.to_dict()
    assert d["authority"] == "NON_SOVEREIGN"
    assert d["fabricated"] is False
    assert d["mutation_path_open"] is False
    assert d["schema"] == "CONTEXT_PACKET_V1"
    assert "runtime_probe" in d
    assert "scope" in d


# ── Two-clock model: shell ≠ trust ───────────────────────────────────

def test_shell_ready_does_not_imply_trust_ready(storage):
    """
    PresenceActive_shell=1 does not imply PresenceActive_kernel=1.
    A valid packet is shell-ready but carries no truth claim.
    """
    packet = InitAirlock(storage, _VALID_SCOPE).open()
    # Shell: packet assembled
    assert packet.packet_id.startswith("PKT-")
    # No truth: no receipt, no admission, no ledger entry
    assert packet.authority == "NON_SOVEREIGN"
    # The packet does NOT carry a receipt_id, decision, or ledger_hash
    d = packet.to_dict()
    assert "receipt_id" not in d
    assert "ledger_hash" not in d
    assert "admission_decision" not in d
