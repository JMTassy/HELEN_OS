"""
tests/test_kernel_authority.py

RED TEST — Authority fence enforcement.

Kernel invariant: authority_ok_event_b(e) = false → append returns None.

Authority fences (from LedgerKernel.v authority_ok_event_b):
  HELEN   + VERDICT      → BLOCKED
  HELEN   + TERMINATION  → BLOCKED
  MAYOR   + USER_MESSAGE → BLOCKED
  CHRONOS + VERDICT      → BLOCKED
  CHRONOS + TERMINATION  → BLOCKED
  CHRONOS + RECEIPT      → BLOCKED
  All other (actor, etype) combinations → ALLOWED (structurally)

This test starts RED because kernel_cli is a stub.
It turns GREEN when kernel_cli enforces structural_valid_b's authority check.

Note: "allowed" here means structurally valid — policy_validb may add
further restrictions on top. Tests use the pass-through policy stub.
"""

import os
import sys

import pytest
pytestmark = pytest.mark.requires_ocaml

sys.path.insert(0, os.path.dirname(__file__))
from conftest_kernel import invoke_kernel_cli


# ---------------------------------------------------------------------------
# Helper payloads
# ---------------------------------------------------------------------------

VERDICT_PAYLOAD  = {"turn": 0, "verdict": "PASS", "channel": "HER_HAL_V1"}
TERM_PAYLOAD     = {"reason": "done", "run_id": "R001"}
UM_PAYLOAD       = {"text": "hello", "user": "alice"}
RECEIPT_PAYLOAD  = {"ref_verdict": "VID001", "verdict_hash_hex": "a" * 64}
PROPOSAL_PAYLOAD = {"title": "New feature", "body": "Details..."}
SLAB_PAYLOAD     = {"content": "AUTHORITY: HUMAN-ONLY", "schema": "WUL_V1"}
RHOCERT_PAYLOAD  = {"inf_rho": "0.03", "t_star": "2"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path):
    return str(tmp_path / "test_authority.ndjson")


# ===========================================================================
# BLOCKED combinations — must return ok=false
# ===========================================================================

def test_helen_cannot_issue_verdict(ledger):
    """HELEN + VERDICT → structural_valid_b = false → ok=false."""
    rc, resp = invoke_kernel_cli(ledger, "HELEN", "VERDICT", VERDICT_PAYLOAD)
    assert resp.get("ok") is False, (
        f"HELEN must NOT be able to issue VERDICT.\nGot: {resp}"
    )


def test_helen_cannot_issue_termination(ledger):
    """HELEN + TERMINATION → structural_valid_b = false → ok=false."""
    rc, resp = invoke_kernel_cli(ledger, "HELEN", "TERMINATION", TERM_PAYLOAD)
    assert resp.get("ok") is False, (
        f"HELEN must NOT be able to issue TERMINATION.\nGot: {resp}"
    )


def test_mayor_cannot_issue_user_message(ledger):
    """MAYOR + USER_MESSAGE → structural_valid_b = false → ok=false."""
    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "USER_MESSAGE", UM_PAYLOAD)
    assert resp.get("ok") is False, (
        f"MAYOR must NOT be able to issue USER_MESSAGE.\nGot: {resp}"
    )


def test_chronos_cannot_issue_verdict(ledger):
    """CHRONOS + VERDICT → structural_valid_b = false → ok=false.
    CHRONOS is the 'no ship' agent; VERDICT is a finality event."""
    rc, resp = invoke_kernel_cli(ledger, "CHRONOS", "VERDICT", VERDICT_PAYLOAD)
    assert resp.get("ok") is False, (
        f"CHRONOS must NOT be able to issue VERDICT.\nGot: {resp}"
    )


def test_chronos_cannot_issue_termination(ledger):
    """CHRONOS + TERMINATION → structural_valid_b = false → ok=false."""
    rc, resp = invoke_kernel_cli(ledger, "CHRONOS", "TERMINATION", TERM_PAYLOAD)
    assert resp.get("ok") is False, (
        f"CHRONOS must NOT be able to issue TERMINATION.\nGot: {resp}"
    )


def test_chronos_cannot_issue_receipt(ledger):
    """CHRONOS + RECEIPT → structural_valid_b = false → ok=false.
    CHRONOS is 'no finality'; RECEIPT is a finality/ship event."""
    rc, resp = invoke_kernel_cli(ledger, "CHRONOS", "RECEIPT", RECEIPT_PAYLOAD)
    assert resp.get("ok") is False, (
        f"CHRONOS must NOT be able to issue RECEIPT.\nGot: {resp}"
    )


# ===========================================================================
# ALLOWED combinations — must return ok=true (given policy stub passes)
# ===========================================================================

def test_mayor_can_issue_verdict(ledger):
    """MAYOR + VERDICT → ok=true (standard governance event).
    RED: stub always rejects (correct red behavior)."""
    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", VERDICT_PAYLOAD)
    assert resp.get("ok") is True, (
        f"MAYOR should be able to issue VERDICT.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_mayor_can_issue_termination(ledger):
    """MAYOR + TERMINATION → ok=true (MAYOR seals the session)."""
    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "TERMINATION", TERM_PAYLOAD)
    assert resp.get("ok") is True, (
        f"MAYOR should be able to issue TERMINATION.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_helen_can_issue_assistant_message(ledger):
    """HELEN + ASSISTANT_MESSAGE → ok=true (dialogue layer)."""
    rc, resp = invoke_kernel_cli(
        ledger, "HELEN", "ASSISTANT_MESSAGE",
        {"text": "Hello, I am HELEN.", "turn": 0}
    )
    assert resp.get("ok") is True, (
        f"HELEN should be able to issue ASSISTANT_MESSAGE.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_helen_can_issue_proposal(ledger):
    """HELEN + PROPOSAL → ok=true (idea proposal, not finality)."""
    rc, resp = invoke_kernel_cli(ledger, "HELEN", "PROPOSAL", PROPOSAL_PAYLOAD)
    assert resp.get("ok") is True, (
        f"HELEN should be able to issue PROPOSAL.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_chronos_can_issue_proposal(ledger):
    """CHRONOS + PROPOSAL → ok=true (CHRONOS is an ideation agent)."""
    rc, resp = invoke_kernel_cli(ledger, "CHRONOS", "PROPOSAL", PROPOSAL_PAYLOAD)
    assert resp.get("ok") is True, (
        f"CHRONOS should be able to issue PROPOSAL.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_chronos_can_issue_wul_slab(ledger):
    """CHRONOS + WUL_SLAB → ok=true (CHRONOS produces slab content)."""
    rc, resp = invoke_kernel_cli(ledger, "CHRONOS", "WUL_SLAB", SLAB_PAYLOAD)
    assert resp.get("ok") is True, (
        f"CHRONOS should be able to issue WUL_SLAB.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_chronos_can_issue_rho_cert(ledger):
    """CHRONOS + RHO_CERT → ok=true (viability certificate, not ship)."""
    rc, resp = invoke_kernel_cli(ledger, "CHRONOS", "RHO_CERT", RHOCERT_PAYLOAD)
    assert resp.get("ok") is True, (
        f"CHRONOS should be able to issue RHO_CERT.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


def test_mayor_can_issue_receipt(ledger):
    """MAYOR + RECEIPT → ok=true (MAYOR seals; only CHRONOS is fenced from RECEIPT)."""
    rc, resp = invoke_kernel_cli(ledger, "MAYOR", "RECEIPT", RECEIPT_PAYLOAD)
    assert resp.get("ok") is True, (
        f"MAYOR should be able to issue RECEIPT.\nGot: {resp}\n"
        f"[RED if stub not wired]"
    )


# ===========================================================================
# Cross-cutting: blocked events do not contaminate subsequent valid events
# ===========================================================================

def test_blocked_then_valid_seq_is_zero(ledger):
    """
    After a blocked event (authority violation), valid event still gets seq=0.
    The ledger must be unmodified by the blocked event.
    RED: stub always blocks, so seq check fails.
    """
    # Blocked: HELEN cannot issue VERDICT
    rc_bad, r_bad = invoke_kernel_cli(ledger, "HELEN", "VERDICT", VERDICT_PAYLOAD)
    assert r_bad.get("ok") is False

    # Valid: MAYOR can issue VERDICT
    rc_ok, r_ok = invoke_kernel_cli(ledger, "MAYOR", "VERDICT", VERDICT_PAYLOAD)
    assert r_ok.get("ok") is True, (
        f"Valid MAYOR VERDICT after blocked HELEN VERDICT failed.\nGot: {r_ok}"
    )
    assert r_ok.get("seq") == 0, (
        f"After blocked event, valid event must get seq=0.\nGot seq={r_ok.get('seq')}"
    )
