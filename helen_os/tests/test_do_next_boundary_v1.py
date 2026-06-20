import json
from pathlib import Path

from helen_os.api.do_next_v1 import DoNextService, compute_state_hash, HARD_REJECT_EPOCH


def make_service(tmp_path: Path) -> DoNextService:
    return DoNextService(storage_dir=tmp_path)


def test_phase_trace_kernel_path(tmp_path: Path):
    svc = make_service(tmp_path)
    req = {
        "session_id": "session_one",
        "user_input": "hello",
        "mode": "deterministic",
        "model": "test-model",
    }
    result = svc.execute(req)
    assert result.trace == [
        "REQUEST_VALIDATION",
        "SESSION_LOAD",
        "KNOWLEDGE_AUDIT",
        "DISPATCH_DECISION",
        "CONSEQUENCE_OR_BLOCK",
        "CONSOLIDATION",
        "PERSISTENCE_RESPONSE",
    ]
    assert result.status_code == 200


def test_receipt_lineage_kernel_path(tmp_path: Path):
    svc = make_service(tmp_path)
    req = {
        "session_id": "session_two",
        "user_input": "hello",
        "mode": "deterministic",
        "model": "test-model",
    }
    result = svc.execute(req)
    receipts = result.receipts
    events = {r["event_type"]: r for r in receipts}
    assert "KNOWLEDGE_AUDIT" in events
    assert "DISPATCH_DECISION" in events
    assert "INFERENCE_EXECUTION" in events
    assert "CONCLUSION" in events
    assert "SESSION_COMMIT" in events
    assert events["KNOWLEDGE_AUDIT"]["parent_receipt_id"] is None
    assert events["DISPATCH_DECISION"]["parent_receipt_id"] == events["KNOWLEDGE_AUDIT"]["receipt_id"]
    assert events["INFERENCE_EXECUTION"]["parent_receipt_id"] == events["DISPATCH_DECISION"]["receipt_id"]
    assert events["CONCLUSION"]["parent_receipt_id"] == events["INFERENCE_EXECUTION"]["receipt_id"]
    assert events["SESSION_COMMIT"]["parent_receipt_id"] == events["CONCLUSION"]["receipt_id"]


def test_session_resumption_receipt_parent(tmp_path: Path):
    svc = make_service(tmp_path)
    req = {
        "session_id": "session_resume",
        "user_input": "hello",
        "mode": "deterministic",
        "model": "test-model",
    }
    svc.execute(req)
    second = svc.execute(req)
    events = {r["event_type"]: r for r in second.receipts}
    assert "SESSION_RESUMPTION" in events
    assert events["KNOWLEDGE_AUDIT"]["parent_receipt_id"] == events["SESSION_RESUMPTION"]["receipt_id"]


def _seed_session(tmp_path: Path, session_id: str, epoch: int) -> None:
    """Write a pre-populated session file so tests can trigger epoch-based policy."""
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
    path = tmp_path / f"{session_id}.json"
    path.write_text(json.dumps(session, sort_keys=True, separators=(",", ":")), encoding="utf-8")


def test_reject_path_no_increment(tmp_path: Path):
    # Structural trigger: session at epoch hard ceiling → REJECT
    _seed_session(tmp_path, "session_reject", HARD_REJECT_EPOCH)
    svc = make_service(tmp_path)
    req = {
        "session_id": "session_reject",
        "user_input": "a normal request that should be rejected on epoch ceiling",
        "mode": "deterministic",
        "model": "test-model",
    }
    result = svc.execute(req)
    assert result.status_code == 400
    assert result.response.get("reply") is None
    assert result.response.get("receipt_id") is None
    assert result.response.get("run_id") == HARD_REJECT_EPOCH
    assert result.response.get("epoch") == HARD_REJECT_EPOCH


def test_defer_path(tmp_path: Path):
    # Structural trigger: explicit policy_directive → DEFER
    svc = make_service(tmp_path)
    req = {
        "session_id": "session_defer",
        "user_input": "a normal request explicitly deferred by caller",
        "mode": "deterministic",
        "model": "test-model",
        "policy_directive": "DEFER",
    }
    result = svc.execute(req)
    assert result.status_code == 200
    assert result.response.get("reply") is None
    assert result.response.get("receipt_id") is not None
    events = [r["event_type"] for r in result.receipts]
    assert "DEFERRED_EXECUTION" in events


def test_epoch_increments_on_accept(tmp_path: Path):
    svc = make_service(tmp_path)
    req = {
        "session_id": "session_epoch",
        "user_input": "hello",
        "mode": "deterministic",
        "model": "test-model",
    }
    r1 = svc.execute(req)
    assert r1.response.get("epoch") == 1
    r2 = svc.execute(req)
    assert r2.response.get("epoch") == 2


def test_replay_conformance(tmp_path: Path):
    svc1 = make_service(tmp_path)
    req = {
        "session_id": "session_replay",
        "user_input": "hello replay",
        "mode": "deterministic",
        "model": "test-model",
    }
    r1 = svc1.execute(req)
    reply1 = r1.response.get("reply")
    session_file = tmp_path / "session_replay.json"
    data = json.loads(session_file.read_text(encoding="utf-8"))

    tmp2 = tmp_path / "replay_copy"
    tmp2.mkdir(parents=True, exist_ok=True)
    (tmp2 / "session_replay.json").write_text(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    svc2 = make_service(tmp2)
    r2 = svc2.execute(req)
    reply2 = r2.response.get("reply")

    assert reply1 == reply2
    assert r1.response.get("mode") == r2.response.get("mode")
    assert r1.response.get("model") == r2.response.get("model")
