"""
test_hal_epoch_gate.py — Integration test: claim type gate blocks inadmissible
operations before any HAL cognition fires.
NON_SOVEREIGN. No Ollama required — BLOCKED path returns without network call.
"""
from helen_kernel.gates.claim_type_policy import pre_dispatch_guard
from tools.run_hal_epoch import run_epoch


def test_hal_epoch_allows_proposal_at_gate_only():
    """PROPOSAL is admissible for hal.epoch — gate must not block it."""
    dispatch = {"family": "hal", "op": "epoch", "claim_type": "PROPOSAL"}
    assert pre_dispatch_guard(dispatch) is None


def test_hal_epoch_blocks_verdict_before_cognition():
    """VERDICT is inadmissible — gate fires before HalDriver() is ever called."""
    result = run_epoch(
        epoch_id="TEST_E_BLOCK",
        task="should not reach HAL cognition",
        claim_type="VERDICT",
    )
    assert result["status"] == "BLOCKED"
    assert result["gate"] == "K_TAU"
    assert result["reason"] == "INADMISSIBLE_CLAIM_TYPE"
    assert result["operation"] == "hal.epoch"
    assert result["requested_claim_type"] == "VERDICT"
    assert result["sovereign"] is False
    assert result["authority"] is False


def test_hal_epoch_blocks_receipt():
    """RECEIPT is inadmissible for hal.epoch."""
    result = run_epoch("TEST_E_RECEIPT", "task", claim_type="RECEIPT")
    assert result["status"] == "BLOCKED"
    assert result["gate"] == "K_TAU"


def test_hal_epoch_blocks_unknown_claim_type():
    """Unrecognised claim type → UNKNOWN_OPERATION_CLASS or INADMISSIBLE — either is BLOCKED."""
    result = run_epoch("TEST_E_ROGUE", "task", claim_type="ROGUE")
    assert result["status"] == "BLOCKED"


def test_blocked_result_carries_no_authority():
    result = run_epoch("TEST_E_AUTH", "task", claim_type="VERDICT")
    assert result["authority"] is False
    assert result["sovereign"] is False


def test_blocked_result_has_no_llm_keys():
    """BLOCKED envelope must return before any network call — no output/elapsed keys."""
    result = run_epoch("TEST_E_NOLLM", "task", claim_type="VERDICT")
    assert "output" not in result
    assert "elapsed_s" not in result
    assert "model" not in result
