"""Regression: audit gate must use structural policy, not keyword scanning.

HAL objection #1: _audit() used keyword scanner ("REJECT" in text, "DEFER" in text).
Any user input containing those words triggered policy routing — structurally wrong.

Fix: _audit() uses two structural triggers:
  1. policy_directive field in request (explicit "DEFER" or "REJECT")
  2. epoch >= HARD_REJECT_EPOCH (session ceiling)
  Free text is never scanned for routing decisions.

Doctrine: keyword(text) ⊬ policy_finding / surface_content ⊬ routing_decision
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from helen_os.api.do_next_v1 import DoNextService, compute_state_hash, HARD_REJECT_EPOCH


def make_service(tmp_path: Path) -> DoNextService:
    return DoNextService(storage_dir=tmp_path)


def _seed_session(tmp_path: Path, session_id: str, epoch: int) -> None:
    now = "2026-01-01T00:00:00Z"
    session = {
        "schema": "helen_session_state_v1",
        "session_id": session_id,
        "created_at": now,
        "updated_at": now,
        "epoch": epoch,
        "run_count": epoch,
        "continuity_score": 1.0,
        "memory": [],
        "receipts": [],
        "recent_receipts": [],
        "state_hash": "",
    }
    session["state_hash"] = compute_state_hash(session)
    (tmp_path / f"{session_id}.json").write_text(
        json.dumps(session, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )


def _base_req(session_id: str, user_input: str = "hello", **extra) -> dict:
    return {"session_id": session_id, "user_input": user_input, "mode": "deterministic", "model": "test-model", **extra}


# ── Free-text keywords no longer route ──────────────────────────────────────

def test_free_text_reject_keyword_passes_through(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s1", user_input="please reject this idea"))
    assert result.status_code == 200, (
        "'reject' keyword in free text must not trigger REJECT routing"
    )
    assert result.response.get("reply") == "please reject this idea"


def test_free_text_defer_keyword_passes_through(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s2", user_input="I want to defer this decision"))
    assert result.status_code == 200, (
        "'defer' keyword in free text must not trigger DEFER routing"
    )
    assert result.response.get("reply") == "I want to defer this decision"


def test_upper_reject_in_text_passes_through(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s3", user_input="REJECT THIS BAD THING"))
    assert result.status_code == 200, (
        "Uppercase REJECT in free text must not trigger REJECT routing"
    )


def test_partial_keyword_in_text_passes_through(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s4", user_input="She rejected the offer and deferred judgment"))
    assert result.status_code == 200, (
        "Partial keyword forms ('rejected', 'deferred') must not trigger routing"
    )


# ── Structural policy_directive triggers ─────────────────────────────────────

def test_policy_directive_defer_routes_to_defer(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s5", policy_directive="DEFER"))
    assert result.status_code == 200
    events = [r["event_type"] for r in result.receipts]
    assert "DEFERRED_EXECUTION" in events, "policy_directive=DEFER must route to DEFER"


def test_policy_directive_reject_routes_to_reject(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s6", policy_directive="REJECT"))
    assert result.status_code == 400, "policy_directive=REJECT must route to REJECT"
    assert result.response.get("reply") is None


def test_no_policy_directive_routes_to_kernel(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s7"))
    assert result.status_code == 200
    assert result.response.get("reply") == "hello"


def test_invalid_policy_directive_returns_400(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    status, resp = svc.handle_http(_base_req("s8", policy_directive="OVERRIDE"))
    assert status == 400, "Unknown policy_directive must be rejected at validation"


# ── Epoch ceiling triggers REJECT ─────────────────────────────────────────────

def test_epoch_at_ceiling_triggers_reject(tmp_path: Path) -> None:
    _seed_session(tmp_path, "s9", HARD_REJECT_EPOCH)
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s9", user_input="normal request"))
    assert result.status_code == 400, (
        f"Session at epoch={HARD_REJECT_EPOCH} must be rejected by structural ceiling"
    )
    findings = result.session_state.get("memory", [{}])[-1].get("audit_findings", [])
    assert any(f.get("code") == "AUDIT_BLOCK" for f in findings)


def test_epoch_below_ceiling_passes(tmp_path: Path) -> None:
    _seed_session(tmp_path, "s10", HARD_REJECT_EPOCH - 1)
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s10", user_input="normal request"))
    assert result.status_code == 200, (
        f"Session at epoch={HARD_REJECT_EPOCH - 1} must still be accepted"
    )


def test_epoch_ceiling_reject_does_not_increment_epoch(tmp_path: Path) -> None:
    _seed_session(tmp_path, "s11", HARD_REJECT_EPOCH)
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s11"))
    assert result.response.get("epoch") == HARD_REJECT_EPOCH, (
        "Epoch must not increment on REJECT"
    )


# ── policy_directive does not scan text ───────────────────────────────────────

def test_audit_finding_identifies_structural_trigger(tmp_path: Path) -> None:
    svc = make_service(tmp_path)
    result = svc.execute(_base_req("s12", policy_directive="DEFER"))
    memory = result.session_state.get("memory", [{}])[-1]
    findings = memory.get("audit_findings", [])
    assert any(f.get("code") == "AUDIT_DEFER" for f in findings), (
        "DEFER routing must produce an AUDIT_DEFER finding in session memory"
    )
