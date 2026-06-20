"""Regression: successful executor actions must route a receipt envelope to the ledger.

HAL objection #3: BoundedExecutor receipt chain is self-referential — hashes its own
output, no external witness, never enters the sovereign ledger.

Fix (MAYOR-authorized, option A): _route_executor_receipt() called after every
SUCCESS, spawning helen_say.py --op dialog via subprocess.Popen (fire-and-forget).
Best-effort: spawn failures are logged and never propagated to the HTTP response.

Doctrine: self_referential_receipt ⊬ sovereign_witness
"""
from __future__ import annotations

import sys
import json
from unittest import mock

import helen_api_server_v1 as server
from helen_os.executor.bounded_executor_v1 import (
    ExecutionDecisionReceipt,
    ExecutionResultReceipt,
    ArtifactWriteReceipt,
)

if server.helen is None:
    server.initialize()

client = server.app.test_client()

_NOW = "2026-01-01T00:00:00Z"


def _mock_decision(**overrides) -> ExecutionDecisionReceipt:
    base = dict(
        schema_name="EXECUTION_DECISION_RECEIPT_V1",
        schema_version="1.0",
        decision_id="did-001",
        created_at=_NOW,
        tool_type="ANALYZE",
        normalized_target="bridge_test.txt",
        normalized_payload_sha256="abc123",
        pre_state_hash="pre-hash",
        policy_version="STAGE_B1_V1",
        execution_identity="ei-deadbeef",
        decision="EXECUTE",
        failure_code=None,
        notes=None,
    )
    base.update(overrides)
    return ExecutionDecisionReceipt(**base)


def _mock_result(status: str = "SUCCESS", **overrides) -> ExecutionResultReceipt:
    base = dict(
        schema_name="EXECUTION_RESULT_RECEIPT_V1",
        schema_version="1.0",
        execution_id="eid-001",
        created_at=_NOW,
        decision_id_ref="did-001",
        tool_type="ANALYZE",
        status=status,
        failure_code=None if status == "SUCCESS" else "bounds_violation",
        pre_state_hash="pre-hash",
        post_state_hash="post-hash" if status == "SUCCESS" else None,
        output_sha256="out-sha",
        execution_identity="ei-deadbeef",
        artifact_refs=[],
        notes=None,
    )
    base.update(overrides)
    return ExecutionResultReceipt(**base)


def _mock_artifact() -> ArtifactWriteReceipt:
    return ArtifactWriteReceipt(
        schema_name="ARTIFACT_WRITE_RECEIPT_V1",
        schema_version="1.0",
        artifact_id="art-001",
        created_at=_NOW,
        target_path="bridge_test.txt",
        sha256="sha-artifact",
        bytes=42,
        execution_id_ref="eid-001",
    )


def test_successful_action_triggers_bridge_attempt() -> None:
    decision = _mock_decision()
    result = _mock_result()
    with mock.patch.object(server.action_executor, "execute", return_value=(decision, result, None)), \
         mock.patch("helen_api_server_v1.subprocess") as mock_sub:
        mock_sub.DEVNULL = -1
        resp = client.post("/actions/execute", json={"tool_type": "ANALYZE", "target": "t.txt", "payload": {}})
        assert resp.status_code == 200
        mock_sub.Popen.assert_called_once()
        cmd = mock_sub.Popen.call_args[0][0]
        assert "helen_say.py" in cmd[1]
        assert "--op" in cmd
        assert "dialog" in cmd


def test_bridge_call_includes_envelope_fields() -> None:
    decision = _mock_decision(tool_type="ANALYZE", execution_identity="ei-fields")
    result = _mock_result(execution_id="eid-fields", execution_identity="ei-fields")
    artifact = _mock_artifact()
    with mock.patch.object(server.action_executor, "execute", return_value=(decision, result, artifact)), \
         mock.patch("helen_api_server_v1.subprocess") as mock_sub:
        mock_sub.DEVNULL = -1
        client.post("/actions/execute", json={"tool_type": "ANALYZE", "target": "t.txt", "payload": {}})
        cmd = mock_sub.Popen.call_args[0][0]
        envelope = json.loads(cmd[2])
        assert envelope["schema"] == "EXECUTOR_RECEIPT_ENVELOPE_V1"
        assert envelope["tool_type"] == "ANALYZE"
        assert envelope["execution_identity"] == "ei-fields"
        assert envelope["execution_id"] == "eid-fields"
        assert envelope["artifact_id"] == "art-001"
        assert "policy_version" in envelope


def test_failed_action_does_not_trigger_bridge() -> None:
    decision = _mock_decision(decision="BLOCK")
    result = _mock_result(status="FAILURE")
    with mock.patch.object(server.action_executor, "execute", return_value=(decision, result, None)), \
         mock.patch("helen_api_server_v1.subprocess") as mock_sub:
        mock_sub.DEVNULL = -1
        resp = client.post("/actions/execute", json={"tool_type": "WRITE", "target": "t.txt", "payload": {}})
        assert resp.status_code == 400
        mock_sub.Popen.assert_not_called()


def test_bridge_spawn_failure_does_not_propagate_to_http() -> None:
    decision = _mock_decision()
    result = _mock_result()
    with mock.patch.object(server.action_executor, "execute", return_value=(decision, result, None)), \
         mock.patch("helen_api_server_v1.subprocess") as mock_sub:
        mock_sub.DEVNULL = -1
        mock_sub.Popen.side_effect = OSError("no such file or directory")
        resp = client.post("/actions/execute", json={"tool_type": "ANALYZE", "target": "t.txt", "payload": {}})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True


def test_bridge_returns_true_on_successful_spawn() -> None:
    decision = _mock_decision()
    result = _mock_result()
    with mock.patch.object(server.action_executor, "execute", return_value=(decision, result, None)), \
         mock.patch("helen_api_server_v1.subprocess") as mock_sub:
        mock_sub.DEVNULL = -1
        mock_sub.Popen.return_value = mock.Mock()
        resp = client.post("/actions/execute", json={"tool_type": "ANALYZE", "target": "t.txt", "payload": {}})
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True


def test_bridge_uses_sys_executable() -> None:
    decision = _mock_decision()
    result = _mock_result()
    with mock.patch.object(server.action_executor, "execute", return_value=(decision, result, None)), \
         mock.patch("helen_api_server_v1.subprocess") as mock_sub:
        mock_sub.DEVNULL = -1
        client.post("/actions/execute", json={"tool_type": "ANALYZE", "target": "t.txt", "payload": {}})
        cmd = mock_sub.Popen.call_args[0][0]
        assert cmd[0] == sys.executable
