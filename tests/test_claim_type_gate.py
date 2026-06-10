"""
test_claim_type_gate.py — Pre-dispatch claim type gate tests.
NON_SOVEREIGN. Tests the K-tau extension rule only.
"""
import pytest
from helen_kernel.gates.claim_type_policy import (
    admissible_claim_types,
    operation_key,
    pre_dispatch_guard,
    validate_claim_type,
)


# --- operation_key ---

def test_operation_key_concatenates_family_and_op():
    dispatch = {"family": "autoresearch", "op": "epoch"}
    assert operation_key(dispatch) == "autoresearch.epoch"


def test_operation_key_handles_missing_fields():
    assert operation_key({}) == "."
    assert operation_key({"family": "gate"}) == "gate."


# --- admissible_claim_types ---

def test_autoresearch_epoch_admits_proposal_observation_audit():
    allowed = admissible_claim_types({"family": "autoresearch", "op": "epoch"})
    assert allowed == {"OBSERVATION", "PROPOSAL", "AUDIT"}


def test_gate_run_admits_verdict_and_audit():
    allowed = admissible_claim_types({"family": "gate", "op": "run"})
    assert allowed == {"VERDICT", "AUDIT"}


def test_executor_task_admits_receipt_and_audit():
    allowed = admissible_claim_types({"family": "executor", "op": "task"})
    assert allowed == {"RECEIPT", "AUDIT"}


def test_unknown_operation_returns_empty_set():
    allowed = admissible_claim_types({"family": "unknown", "op": "thing"})
    assert allowed == set()


# --- validate_claim_type (core gate) ---

def test_autoresearch_epoch_allows_proposal():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "PROPOSAL"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is True
    assert result["reason"] == "CLAIM_TYPE_ALLOWED"


def test_autoresearch_epoch_allows_observation():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "OBSERVATION"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is True


def test_autoresearch_epoch_allows_audit():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "AUDIT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is True


def test_autoresearch_epoch_blocks_verdict():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "VERDICT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is False
    assert result["reason"] == "INADMISSIBLE_CLAIM_TYPE"
    assert "PROPOSAL" in result["allowed"]
    assert "VERDICT" not in result["allowed"]


def test_autoresearch_epoch_blocks_receipt():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "RECEIPT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is False
    assert result["reason"] == "INADMISSIBLE_CLAIM_TYPE"


def test_gate_run_allows_verdict():
    dispatch = {"family": "gate", "op": "run", "claim_type": "VERDICT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is True


def test_gate_run_blocks_proposal():
    dispatch = {"family": "gate", "op": "run", "claim_type": "PROPOSAL"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is False
    assert result["reason"] == "INADMISSIBLE_CLAIM_TYPE"


def test_executor_task_allows_receipt():
    dispatch = {"family": "executor", "op": "task", "claim_type": "RECEIPT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is True


def test_executor_task_blocks_verdict():
    dispatch = {"family": "executor", "op": "task", "claim_type": "VERDICT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is False


def test_hal_epoch_allows_proposal():
    dispatch = {"family": "hal", "op": "epoch", "claim_type": "PROPOSAL"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is True


def test_hal_epoch_blocks_verdict():
    dispatch = {"family": "hal", "op": "epoch", "claim_type": "VERDICT"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is False


def test_unknown_operation_blocks_closed():
    dispatch = {"family": "unknown", "op": "thing", "claim_type": "PROPOSAL"}
    result = validate_claim_type(dispatch)
    assert result["ok"] is False
    assert result["reason"] == "UNKNOWN_OPERATION_CLASS"
    assert result["allowed"] == []


def test_result_carries_operation_key():
    dispatch = {"family": "gate", "op": "run", "claim_type": "AUDIT"}
    result = validate_claim_type(dispatch)
    assert result["operation"] == "gate.run"


def test_result_carries_requested_claim_type():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "VERDICT"}
    result = validate_claim_type(dispatch)
    assert result["requested"] == "VERDICT"


# --- pre_dispatch_guard ---

def test_pre_dispatch_guard_returns_none_when_allowed():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "PROPOSAL"}
    assert pre_dispatch_guard(dispatch) is None


def test_pre_dispatch_guard_returns_blocked_envelope():
    dispatch = {"family": "autoresearch", "op": "epoch", "claim_type": "VERDICT"}
    block = pre_dispatch_guard(dispatch)
    assert block is not None
    assert block["status"] == "BLOCKED"
    assert block["gate"] == "K_TAU"
    assert block["reason"] == "INADMISSIBLE_CLAIM_TYPE"
    assert block["authority"] == "NONE"


def test_pre_dispatch_guard_unknown_operation_blocks():
    dispatch = {"family": "rogue", "op": "free", "claim_type": "VERDICT"}
    block = pre_dispatch_guard(dispatch)
    assert block is not None
    assert block["reason"] == "UNKNOWN_OPERATION_CLASS"


def test_helen_say_fetch_allows_observation():
    dispatch = {"family": "helen_say", "op": "fetch", "claim_type": "OBSERVATION"}
    assert pre_dispatch_guard(dispatch) is None


def test_helen_say_fetch_blocks_proposal():
    dispatch = {"family": "helen_say", "op": "fetch", "claim_type": "PROPOSAL"}
    block = pre_dispatch_guard(dispatch)
    assert block is not None
    assert block["reason"] == "INADMISSIBLE_CLAIM_TYPE"
