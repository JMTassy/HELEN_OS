"""
tests/test_kernel_termination_unique.py

RED TEST — Property P3: second TERMINATION always rejected.

Kernel invariant I3 (at_most_one_termination):
  count_terminations(L) <= 1 maintained by structural_valid_b.
  append L MAYOR TERMINATION raw → Some L'  iff  count_terminations L = 0.
  Any subsequent TERMINATION → None.

This test starts RED because kernel_cli is a stub.
It turns GREEN when kernel_cli enforces structural_valid_b's termination check.

Important: MAYOR is the only actor that can issue TERMINATION.
(HELEN and CHRONOS are fenced out by authority_ok_event_b.)
"""

import os
import sys

import pytest
pytestmark = pytest.mark.requires_ocaml

sys.path.insert(0, os.path.dirname(__file__))
from conftest_kernel import invoke_kernel_cli


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path):
    return str(tmp_path / "test_termination.ndjson")


# ---------------------------------------------------------------------------
# Test P3.1: First TERMINATION succeeds
# ---------------------------------------------------------------------------

def test_first_termination_ok(ledger):
    """
    P3: First TERMINATION on an empty ledger → ok=true.
    RED: stub always rejects.
    """
    rc, resp = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION",
        {"reason": "session complete", "run_id": "R001"},
    )
    assert resp.get("ok") is True, (
        f"First TERMINATION should succeed.\nGot: {resp}"
    )
    assert resp.get("seq") == 0


# ---------------------------------------------------------------------------
# Test P3.2: Second TERMINATION rejected
# ---------------------------------------------------------------------------

def test_second_termination_rejected(ledger):
    """
    P3: Second TERMINATION on same ledger → ok=false.
    RED: stub always rejects (wrong reason).
    """
    # First TERMINATION — must succeed
    rc0, r0 = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION",
        {"reason": "first seal", "run_id": "R001"},
    )
    assert r0.get("ok") is True, f"First TERMINATION failed: {r0}"

    # Second TERMINATION — must be rejected
    rc1, r1 = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION",
        {"reason": "second seal (must fail)", "run_id": "R001"},
    )
    assert r1.get("ok") is False, (
        f"Second TERMINATION must be rejected.\nGot: {r1}"
    )


# ---------------------------------------------------------------------------
# Test P3.3: TERMINATION after intermediate events
# ---------------------------------------------------------------------------

def test_termination_after_verdicts(ledger):
    """
    P3: TERMINATION after N VERDICTs → ok=true.
    A second TERMINATION after that → ok=false.
    RED: stub always rejects.
    """
    N = 3
    for i in range(N):
        rc, resp = invoke_kernel_cli(
            ledger, "MAYOR", "VERDICT",
            {"turn": i, "verdict": "PASS", "channel": "HER_HAL_V1"},
        )
        assert resp.get("ok") is True, f"VERDICT {i} failed: {resp}"

    # TERMINATION
    rc_t, r_t = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION",
        {"reason": "all verdicts complete", "run_id": "R001"},
    )
    assert r_t.get("ok") is True, f"TERMINATION after {N} VERDICTs failed: {r_t}"
    assert r_t.get("seq") == N, f"Expected seq={N}, got {r_t.get('seq')}"

    # Second TERMINATION — rejected
    rc_t2, r_t2 = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION",
        {"reason": "second seal (must fail)", "run_id": "R001"},
    )
    assert r_t2.get("ok") is False, (
        f"Second TERMINATION must be rejected.\nGot: {r_t2}"
    )


# ---------------------------------------------------------------------------
# Test P3.4: After TERMINATION, even valid non-termination events are rejected
# ---------------------------------------------------------------------------

def test_no_events_after_termination(ledger):
    """
    P3 (extension): After TERMINATION, further appends should fail.
    Rationale: Ledger is sealed — no further events are admissible.
    NOTE: This is a POLICY-level constraint, not purely structural.
    If policy_validb is a pass-through stub, this test may pass
    VERDICT after TERMINATION (which would be a policy gap, not structural).
    Mark this test as xfail until policy layer is implemented.

    RED: stub always rejects (but for the wrong reason).
    """
    pytest.xfail(
        "Policy-layer constraint: events after TERMINATION require "
        "policy_validb to be implemented, not just structural_valid_b. "
        "This test will remain XFAIL until policy layer is wired."
    )

    rc0, r0 = invoke_kernel_cli(
        ledger, "MAYOR", "TERMINATION",
        {"reason": "seal", "run_id": "R001"},
    )
    assert r0.get("ok") is True

    rc1, r1 = invoke_kernel_cli(
        ledger, "MAYOR", "VERDICT",
        {"turn": 0, "verdict": "PASS", "channel": "HER_HAL_V1"},
    )
    assert r1.get("ok") is False, (
        f"VERDICT after TERMINATION should be rejected.\nGot: {r1}"
    )
