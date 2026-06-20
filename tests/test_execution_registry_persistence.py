"""Regression: ExecutionRegistry must survive process restarts.

HAL objection #2: ExecutionRegistry._seen is in-process volatile — resets on
restart, so duplicate_execution protection is not a constitutional property.

Fix: ExecutionRegistry accepts persist_path; loads existing identities on
init; appends each new identity as a JSON-L line under fcntl exclusive lock.

Doctrine: in-memory dedup ⊬ constitutional dedup.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from helen_os.executor.bounded_executor_v1 import (
    BoundedExecutor,
    ExecutionRegistry,
    EMPTY_STATE_HASH,
    compute_execution_identity,
)
from helen_os.governance.canonical import sha256_prefixed


FAKE_IDENTITY = sha256_prefixed({"x": "test_identity"})


def test_registry_no_path_is_in_memory_only(tmp_path: Path) -> None:
    reg = ExecutionRegistry()
    assert reg._persist_path is None
    assert reg.register(FAKE_IDENTITY) is True
    assert reg.register(FAKE_IDENTITY) is False


def test_registry_file_created_on_first_registration(tmp_path: Path) -> None:
    path = tmp_path / "reg.ndjson"
    reg = ExecutionRegistry(persist_path=path)
    assert not path.exists()
    reg.register(FAKE_IDENTITY)
    assert path.exists()


def test_registry_written_as_ndjson(tmp_path: Path) -> None:
    path = tmp_path / "reg.ndjson"
    reg = ExecutionRegistry(persist_path=path)
    reg.register(FAKE_IDENTITY)
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["execution_identity"] == FAKE_IDENTITY
    assert "registered_at" in entry


def test_registry_survives_restart(tmp_path: Path) -> None:
    path = tmp_path / "reg.ndjson"
    reg1 = ExecutionRegistry(persist_path=path)
    reg1.register(FAKE_IDENTITY)

    reg2 = ExecutionRegistry(persist_path=path)
    assert reg2.register(FAKE_IDENTITY) is False, (
        "Duplicate must be blocked by fresh registry loaded from disk"
    )


def test_registry_new_identity_allowed_after_restart(tmp_path: Path) -> None:
    path = tmp_path / "reg.ndjson"
    identity_a = sha256_prefixed({"x": "a"})
    identity_b = sha256_prefixed({"x": "b"})

    reg1 = ExecutionRegistry(persist_path=path)
    reg1.register(identity_a)

    reg2 = ExecutionRegistry(persist_path=path)
    assert reg2.register(identity_b) is True, "Different identity must be allowed"


def test_registry_corrupt_line_skipped(tmp_path: Path) -> None:
    path = tmp_path / "reg.ndjson"
    path.write_text('{"execution_identity": "sha256:' + 'a' * 64 + '"}\n{CORRUPT}\n', encoding="utf-8")
    reg = ExecutionRegistry(persist_path=path)
    assert "sha256:" + "a" * 64 in reg._seen
    assert len(reg._seen) == 1


def test_executor_duplicate_blocked_after_restart(tmp_path: Path) -> None:
    registry_path = tmp_path / "reg.ndjson"
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    exe1 = BoundedExecutor(base_dir=sandbox, policy_version="v1", registry_path=registry_path)
    req = {"tool_type": "ANALYZE", "target": "x.txt", "payload": {"query": "hi"}}
    d1, r1, _ = exe1.execute(req)
    assert d1.decision == "ALLOW"

    exe2 = BoundedExecutor(base_dir=sandbox, policy_version="v1", registry_path=registry_path)
    d2, r2, _ = exe2.execute(req)
    assert d2.failure_code == "duplicate_execution", (
        "Same request must be rejected by fresh executor loading registry from disk"
    )


def test_executor_no_registry_path_backward_compatible(tmp_path: Path) -> None:
    exe = BoundedExecutor(base_dir=tmp_path, policy_version="v1")
    req = {"tool_type": "ANALYZE", "target": "x.txt", "payload": {"query": "hi"}}
    d, r, _ = exe.execute(req)
    assert d.decision == "ALLOW"
    assert r.status == "SUCCESS"


def test_registry_persist_latency_under_5ms(tmp_path: Path) -> None:
    path = tmp_path / "reg.ndjson"
    reg = ExecutionRegistry(persist_path=path)
    identity = sha256_prefixed({"x": "latency"})
    start = time.perf_counter()
    reg.register(identity)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 5, f"Registry persist must complete in <5 ms, took {elapsed_ms:.1f} ms"
