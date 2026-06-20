"""Constitutional tests for HELEN Autoresearch safe policy functions.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Tests cover the 10 required policy invariants:
  1. valid packet passes
  2. packet with authority=true fails
  3. packet with ledger_effect != none fails
  4. packet without evidence fails
  5. forbidden path fails
  6. staged ledger warning fails closed
  7. self-admission language fails
  8. training action fails
  9. network action fails
 10. outbox-only write policy passes

Doctrine: self_referential_receipt ⊬ sovereign_witness /
          autoresearch_pass ⊬ admission / packet ⊬ claim
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure temple/autoresearch is importable from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "temple" / "autoresearch"))

from autoresearch_policy import (
    validate_packet,
    check_forbidden_paths,
    check_stop_conditions,
    classify_finding,
    PACKET_SCHEMA,
)
from autoresearch_scanner import reject_write_outside_outbox


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_packet(**overrides) -> dict:
    base = {
        "schema": PACKET_SCHEMA,
        "packet_id": "AR-abc123def456",
        "source_refs": ["docs/proposals/FOO.md:10"],
        "finding_type": "proposal",
        "summary": "Found a candidate proposal in FOO.md",
        "evidence": ["This is a candidate proposal: source_ref docs/proposals/FOO.md:10"],
        "risk_flags": [],
        "recommended_action": "ROUTE_TO_OPERATOR_FOR_REVIEW",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Valid packet passes
# ---------------------------------------------------------------------------

def test_valid_packet_passes() -> None:
    ok, errors = validate_packet(_valid_packet())
    assert ok is True, f"Expected valid packet to pass, got errors: {errors}"
    assert errors == []


# ---------------------------------------------------------------------------
# 2. Packet with authority=true fails
# ---------------------------------------------------------------------------

def test_authority_true_fails() -> None:
    ok, errors = validate_packet(_valid_packet(authority=True))
    assert ok is False
    assert any("authority" in e for e in errors), f"Expected authority error, got: {errors}"


def test_authority_string_false_fails() -> None:
    ok, errors = validate_packet(_valid_packet(authority="false"))
    assert ok is False
    assert any("authority" in e for e in errors)


# ---------------------------------------------------------------------------
# 3. Packet with ledger_effect != none fails
# ---------------------------------------------------------------------------

def test_ledger_effect_write_fails() -> None:
    ok, errors = validate_packet(_valid_packet(ledger_effect="write"))
    assert ok is False
    assert any("ledger_effect" in e for e in errors)


def test_ledger_effect_append_fails() -> None:
    ok, errors = validate_packet(_valid_packet(ledger_effect="append"))
    assert ok is False
    assert any("ledger_effect" in e for e in errors)


def test_ledger_effect_none_string_passes() -> None:
    ok, errors = validate_packet(_valid_packet(ledger_effect="none"))
    assert ok is True, f"ledger_effect='none' should pass, got: {errors}"


# ---------------------------------------------------------------------------
# 4. Packet without evidence fails
# ---------------------------------------------------------------------------

def test_empty_evidence_fails() -> None:
    ok, errors = validate_packet(_valid_packet(evidence=[]))
    assert ok is False
    assert any("evidence" in e for e in errors)


def test_missing_evidence_field_fails() -> None:
    packet = _valid_packet()
    del packet["evidence"]
    ok, errors = validate_packet(packet)
    assert ok is False


def test_non_list_evidence_fails() -> None:
    ok, errors = validate_packet(_valid_packet(evidence="some string"))
    assert ok is False
    assert any("evidence" in e for e in errors)


# ---------------------------------------------------------------------------
# 5. Forbidden path fails
# ---------------------------------------------------------------------------

def test_ledger_path_forbidden() -> None:
    violations = check_forbidden_paths(["town/ledger_v1.ndjson"])
    assert len(violations) > 0


def test_kernel_path_forbidden() -> None:
    violations = check_forbidden_paths(["oracle_town/kernel/kernel_daemon.py"])
    assert len(violations) > 0


def test_governance_path_forbidden() -> None:
    violations = check_forbidden_paths(["helen_os/governance/schema_registry.py"])
    assert len(violations) > 0


def test_allowed_path_not_forbidden() -> None:
    violations = check_forbidden_paths(["docs/proposals/SOME_DOC.md"])
    assert violations == []


def test_multiple_files_only_forbidden_flagged() -> None:
    violations = check_forbidden_paths([
        "docs/proposals/OK.md",
        "town/ledger_v1.ndjson",
        "temple/autoresearch/outbox/AR-abc.json",
    ])
    paths_flagged = [v for v in violations if "town/ledger_v1.ndjson" in v]
    assert len(paths_flagged) == 1
    ok_paths = [v for v in violations if "docs/proposals/OK.md" in v]
    assert len(ok_paths) == 0


# ---------------------------------------------------------------------------
# 6. Staged ledger warning fails closed
# ---------------------------------------------------------------------------

def test_staged_ledger_triggers_stop() -> None:
    should_stop, reason = check_stop_conditions(
        staged_files=["town/ledger_v1.ndjson"],
    )
    assert should_stop is True
    assert "ledger" in reason.lower() or "STOP" in reason


def test_staged_kernel_triggers_stop() -> None:
    should_stop, reason = check_stop_conditions(
        staged_files=["oracle_town/kernel/kernel_daemon.py"],
    )
    assert should_stop is True


def test_clean_state_does_not_stop() -> None:
    should_stop, reason = check_stop_conditions(
        staged_files=[],
        changed_files=["docs/proposals/NEW.md"],
        tests_passed=True,
    )
    assert should_stop is False
    assert reason == ""


# ---------------------------------------------------------------------------
# 7. Self-admission language fails
# ---------------------------------------------------------------------------

def test_self_admit_in_summary_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        summary="We should self_admit this finding directly"
    ))
    assert ok is False
    assert any("self-admission" in e for e in errors)


def test_bypass_reducer_in_recommended_action_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        recommended_action="bypass reducer and directly admit to ledger"
    ))
    assert ok is False
    assert any("self-admission" in e for e in errors)


def test_auto_admit_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        recommended_action="auto_admit this packet"
    ))
    assert ok is False


# ---------------------------------------------------------------------------
# 8. Training action fails
# ---------------------------------------------------------------------------

def test_training_job_in_recommended_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        recommended_action="run training job on this corpus"
    ))
    assert ok is False
    assert any("training" in e for e in errors)


def test_finetune_in_summary_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        summary="We should finetune the model on these findings"
    ))
    assert ok is False
    assert any("training" in e for e in errors)


def test_fine_tune_dash_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        summary="Plan: fine-tune base model on autoresearch output"
    ))
    assert ok is False
    assert any("training" in e for e in errors)


# ---------------------------------------------------------------------------
# 9. Network action fails
# ---------------------------------------------------------------------------

def test_fetch_url_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        recommended_action="fetch url https://example.com for more context"
    ))
    assert ok is False
    assert any("network" in e for e in errors)


def test_requests_get_in_summary_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        summary="Use requests.get to retrieve external data"
    ))
    assert ok is False
    assert any("network" in e for e in errors)


def test_call_api_fails() -> None:
    ok, errors = validate_packet(_valid_packet(
        recommended_action="call api endpoint to validate"
    ))
    assert ok is False
    assert any("network" in e for e in errors)


# ---------------------------------------------------------------------------
# 10. Outbox-only write policy passes
# ---------------------------------------------------------------------------

def test_outbox_write_allowed(tmp_path: Path) -> None:
    outbox = tmp_path / "temple" / "autoresearch" / "outbox"
    outbox.mkdir(parents=True)
    target = outbox / "AR-abc123.json"
    assert reject_write_outside_outbox(target, outbox) is True


def test_write_outside_outbox_blocked(tmp_path: Path) -> None:
    outbox = tmp_path / "temple" / "autoresearch" / "outbox"
    outbox.mkdir(parents=True)
    sovereign_path = tmp_path / "town" / "ledger_v1.ndjson"
    assert reject_write_outside_outbox(sovereign_path, outbox) is False


def test_write_to_docs_blocked(tmp_path: Path) -> None:
    outbox = tmp_path / "temple" / "autoresearch" / "outbox"
    outbox.mkdir(parents=True)
    docs_path = tmp_path / "docs" / "proposals" / "NEW.md"
    assert reject_write_outside_outbox(docs_path, outbox) is False


def test_write_to_kernel_blocked(tmp_path: Path) -> None:
    outbox = tmp_path / "temple" / "autoresearch" / "outbox"
    outbox.mkdir(parents=True)
    kernel_path = tmp_path / "oracle_town" / "kernel" / "kernel_daemon.py"
    assert reject_write_outside_outbox(kernel_path, outbox) is False


# ---------------------------------------------------------------------------
# Bonus: classify_finding heuristics
# ---------------------------------------------------------------------------

def test_classify_risk_signal() -> None:
    result = classify_finding("danger: ledger breach detected", ["forbidden path accessed"])
    assert result == "risk"


def test_classify_test_gap() -> None:
    result = classify_finding("test gap in executor module", ["no test coverage"])
    assert result == "test_gap"


def test_classify_doc_gap() -> None:
    result = classify_finding("missing doc for gate", ["undocumented behavior in gate"])
    assert result == "doc_gap"


def test_classify_defaults_to_proposal() -> None:
    result = classify_finding("interesting observation", ["found something new"])
    assert result == "proposal"
