"""
Tests for KernelDaemon._handle_promote_skill()

Covers all 8 required failure/success paths from MAYOR_HANDLER_PROMOTE_SKILL_SPEC_V1.
No real sovereign writes are made — NDJSONWriter and _tail_ledger are mocked for
tests that reach the write path.
"""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

from oracle_town.kernel.kernel_daemon import KernelDaemon

_VALID_HASH = "sha256:" + "a" * 64


def _base_packet(**overrides):
    p = {
        "schema_name":              "SKILL_PROMOTION_PACKET_V1",
        "schema_version":           "1.0.0",
        "skill_id":                 "TEST_SKILL_V1",
        "candidate_version":        "V1",
        "candidate_identity_hash":  _VALID_HASH,
        "skill_local_admission_commit": "abc1234",
        "checker_verdict":          "OPERATIONALLY_WITNESSED",
        "operator_countersign":     "JM_TASSY_2026",
        "requested_action":         "SOVEREIGN_PROMOTE",
    }
    p.update(overrides)
    return p


def _req(packet_obj):
    return {
        "packet":    json.dumps(packet_obj) if isinstance(packet_obj, dict) else packet_obj,
        "claim_id":  "test:promote:001",
        "proposer":  "helen",
        "intent":    "skill_sovereign_promotion",
    }


def _daemon():
    return KernelDaemon()


# ── Test 1: bad JSON ──────────────────────────────────────────────────────────

def test_bad_json_returns_parse_error():
    resp = _daemon()._handle_promote_skill({"packet": "not valid json {{{"})
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_PARSE_ERROR"
    assert resp["mutations"] == []
    assert resp["receipt_id"] is None


# ── Test 2: missing fields ────────────────────────────────────────────────────

def test_missing_fields_returns_missing_fields_gate():
    # Remove a required field
    p = _base_packet()
    del p["operator_countersign"]
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_MISSING_FIELDS"
    assert resp["mutations"] == []
    assert "operator_countersign" in resp["reason"]


# ── Test 3: wrong schema_name ─────────────────────────────────────────────────

def test_wrong_schema_name_returns_wrong_schema_gate():
    p = _base_packet(schema_name="WRONG_SCHEMA_V1")
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_WRONG_SCHEMA"
    assert resp["mutations"] == []


# ── Test 4: weak checker_verdict ──────────────────────────────────────────────

def test_weak_checker_verdict_returns_verdict_gate():
    p = _base_packet(checker_verdict="REPLAY_ACTIVE")
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_CHECKER_VERDICT_WEAK"
    assert resp["mutations"] == []
    assert "OPERATIONALLY_WITNESSED" in resp["reason"]


def test_ledger_appended_checker_verdict_also_rejected():
    p = _base_packet(checker_verdict="LEDGER_APPENDED")
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_CHECKER_VERDICT_WEAK"
    assert resp["mutations"] == []


# ── Test 5: bad candidate_identity_hash ───────────────────────────────────────

def test_bad_hash_format_returns_bad_hash_gate():
    p = _base_packet(candidate_identity_hash="not-a-hash")
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_BAD_HASH"
    assert resp["mutations"] == []


def test_hash_missing_sha256_prefix_rejected():
    # 64 hex chars but no sha256: prefix
    p = _base_packet(candidate_identity_hash="a" * 64)
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_BAD_HASH"


# ── Test 6: wrong requested_action ────────────────────────────────────────────

def test_wrong_requested_action_returns_wrong_action_gate():
    p = _base_packet(requested_action="LOCAL_ADMIT")
    resp = _daemon()._handle_promote_skill(_req(p))
    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_WRONG_ACTION"
    assert resp["mutations"] == []


# ── Test 7: writer failure → fail closed ─────────────────────────────────────

def test_writer_failure_returns_write_failed_gate():
    """NDJSONWriter.append_event raises → REJECT, mutations: [], receipt_id preserved."""
    p = _base_packet()
    req = _req(p)

    mock_writer = MagicMock()
    mock_writer.append_event.side_effect = OSError("disk full")

    with patch("oracle_town.kernel.kernel_daemon._tail_ledger", return_value=(0, "0" * 64)), \
         patch("oracle_town.kernel.kernel_daemon.NDJSONWriter", return_value=mock_writer):
        resp = _daemon()._handle_promote_skill(req)

    assert resp["decision"] == "REJECT"
    assert resp["gate"] == "GATE_PROMOTE_WRITE_FAILED"
    assert resp["mutations"] == []
    assert resp["receipt_id"] is not None, "receipt_id should be set (MAYOR ratified before write)"
    assert "disk full" in resp["reason"]


# ── Test 8: valid packet + MAYOR ACCEPT + writer success ─────────────────────

def test_valid_packet_accept_with_non_empty_mutations():
    """Full happy path: all gates pass, MAYOR accepts, writer succeeds → ACCEPT + mutations."""
    p = _base_packet()
    req = _req(p)

    mock_writer = MagicMock()
    mock_writer.append_event.return_value = {"seq": 0, "cum_hash": "x" * 64}

    with patch("oracle_town.kernel.kernel_daemon._tail_ledger", return_value=(0, "0" * 64)), \
         patch("oracle_town.kernel.kernel_daemon.NDJSONWriter", return_value=mock_writer):
        resp = _daemon()._handle_promote_skill(req)

    assert resp["decision"] == "ACCEPT"
    assert resp["gate"] == "GATE_PROMOTE_PASS"
    assert isinstance(resp["mutations"], list) and len(resp["mutations"]) > 0

    mutation = resp["mutations"][0]
    assert mutation["type"] == "SKILL_PROMOTION_DECISION_V1"
    assert mutation["skill_id"] == "TEST_SKILL_V1"
    assert "decision_id" in mutation
    assert mutation["ledger_path"] == "town/ledger_v1.ndjson"

    # Verify NDJSONWriter was called with the correct event_type and key payload fields
    mock_writer.append_event.assert_called_once()
    call_kwargs = mock_writer.append_event.call_args
    event_type = call_kwargs[1].get("event_type") or call_kwargs[0][0]
    payload    = call_kwargs[1].get("payload")    or call_kwargs[0][1]
    assert event_type == "SKILL_PROMOTION_DECISION_V1"
    assert payload["skill_id"] == "TEST_SKILL_V1"
    assert payload["sovereign_promotion"] is True
    assert payload["decision_type"] == "ADMITTED"


def test_accept_receipt_id_is_set():
    """receipt_id must be non-None on ACCEPT."""
    p = _base_packet()
    mock_writer = MagicMock()
    mock_writer.append_event.return_value = {}

    with patch("oracle_town.kernel.kernel_daemon._tail_ledger", return_value=(0, "0" * 64)), \
         patch("oracle_town.kernel.kernel_daemon.NDJSONWriter", return_value=mock_writer):
        resp = _daemon()._handle_promote_skill(_req(p))

    assert resp["decision"] == "ACCEPT"
    assert resp["receipt_id"] is not None
