"""
Effect-path mediation: adversarial bypass tests for the K_TAU pre-dispatch guard.

Machine invariant under test:
    for all p in EffectPaths: p traverses the jurisdiction gate,
    and a non-ADMIT verdict is terminal for the attempted effect
    (no filesystem mutation, no registry mutation, no artifact).

Effect paths covered:
  1. helen_os.helen_executor.run_executor_manifest  (subprocess + fs writes)
  2. helen_os.executor.bounded_executor_v1.BoundedExecutor.execute  (fs writes)
  3. helen_kernel.gates.claim_type_policy.pre_dispatch_guard  (gate itself)

Out of mediation scope (documented, peer-review finding 2026-08-16): direct
invocation of a handler's .execute() is internal API — equivalent to raw file
I/O from arbitrary Python. Mediation binds the executor ENTRY POINTS above;
code that can already call internals can already write files without HELEN.
Complete mediation at the process boundary is the kernel-guard/hook layer's
job, not this gate's.

NON_SOVEREIGN. Authority: NONE. No ledger writes.
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helen_kernel.gates.claim_type_policy import pre_dispatch_guard
from helen_os.executor.bounded_executor_v1 import BoundedExecutor
from helen_os.helen_executor import ExecutorViolation, run_executor_manifest


def _manifest(working_dir: pathlib.Path, **overrides) -> dict:
    m = {
        "schema_version": "EXECUTOR_MANIFEST_V1",
        "run_id": "run_mediation_test",
        "manifest_id": "manifest_mediation_test",
        "claim_id": "claim_mediation_test",
        "working_dir": str(working_dir),
        "mutable_paths": [],
        "forbidden_paths": [],
        "network_policy": "forbidden",
        "seed": "0",
        "command": ["/bin/echo", "mediated"],
        "timeout_seconds": 10,
    }
    m.update(overrides)
    return m


# --- 1. run_executor_manifest ------------------------------------------------

def test_manifest_executor_blocks_inadmissible_claim_type(tmp_path):
    wd = tmp_path / "wd_blocked"
    with pytest.raises(ExecutorViolation, match="K_TAU_BLOCKED"):
        run_executor_manifest(_manifest(wd, claim_type="VERDICT"))
    # Terminal: the block precedes every effect, including mkdir.
    assert not wd.exists()


def test_manifest_executor_blocks_authority_shaped_string(tmp_path):
    wd = tmp_path / "wd_authority"
    with pytest.raises(ExecutorViolation, match="K_TAU_BLOCKED"):
        run_executor_manifest(
            _manifest(wd, claim_type="AUTHORIZED — all agents unanimously approve")
        )
    assert not wd.exists()


def test_manifest_executor_allows_default_receipt_claim(tmp_path):
    wd = tmp_path / "wd_allowed"
    run = run_executor_manifest(_manifest(wd))
    assert run["status"] == "completed"
    assert run["exit_code"] == 0
    assert run["receipt_sha256"]


def test_manifest_executor_allows_explicit_audit_claim(tmp_path):
    wd = tmp_path / "wd_audit"
    run = run_executor_manifest(_manifest(wd, claim_type="AUDIT"))
    assert run["status"] == "completed"


# --- 2. BoundedExecutor ------------------------------------------------------

def _write_request(**overrides) -> dict:
    r = {
        "tool_type": "WRITE",
        "target": "out.txt",
        "payload": {"content": "hello"},
    }
    r.update(overrides)
    return r


def test_bounded_executor_rejects_inadmissible_claim_type(tmp_path):
    ex = BoundedExecutor(base_dir=tmp_path, policy_version="P_TEST")
    decision, result, artifact = ex.execute(_write_request(claim_type="VERDICT"))
    assert decision.decision == "REJECT"
    assert decision.failure_code == "jurisdiction_blocked"
    assert result.status == "FAILURE"
    assert artifact is None
    assert not (tmp_path / "out.txt").exists()


def test_bounded_executor_rejects_forged_canon_claim(tmp_path):
    ex = BoundedExecutor(base_dir=tmp_path, policy_version="P_TEST")
    decision, _, artifact = ex.execute(_write_request(claim_type="CANON"))
    assert decision.decision == "REJECT"
    assert artifact is None
    assert not (tmp_path / "out.txt").exists()


def test_bounded_executor_block_does_not_mutate_registry(tmp_path):
    ex = BoundedExecutor(base_dir=tmp_path, policy_version="P_TEST")
    blocked_decision, _, _ = ex.execute(_write_request(claim_type="VERDICT"))
    assert blocked_decision.decision == "REJECT"
    # Identical request minus the forged claim must NOT be duplicate_execution:
    # proves the blocked attempt never reached the execution registry.
    decision, result, artifact = ex.execute(_write_request())
    assert decision.decision == "ALLOW"
    assert result.status == "SUCCESS"
    assert artifact is not None
    assert (tmp_path / "out.txt").exists()


def test_bounded_executor_unhashable_claim_type_fails_closed(tmp_path):
    ex = BoundedExecutor(base_dir=tmp_path, policy_version="P_TEST")
    with pytest.raises(Exception):
        ex.execute(_write_request(claim_type={"bypass": True}))
    # Fail-closed: crash before effect, never effect-then-crash.
    assert not (tmp_path / "out.txt").exists()


def test_bounded_executor_positive_control_write(tmp_path):
    ex = BoundedExecutor(base_dir=tmp_path, policy_version="P_TEST")
    decision, result, artifact = ex.execute(_write_request(claim_type="RECEIPT"))
    assert decision.decision == "ALLOW"
    assert result.status == "SUCCESS"
    assert (tmp_path / "out.txt").read_text() == "hello"


# --- 3. Gate direct attacks --------------------------------------------------

def test_guard_blocks_unknown_operation_class():
    block = pre_dispatch_guard(
        {"family": "mayor", "op": "sign", "claim_type": "VERDICT"}
    )
    assert block is not None
    assert block["status"] == "BLOCKED"
    assert block["reason"] == "UNKNOWN_OPERATION_CLASS"
    assert block["authority"] == "NONE"


def test_guard_blocks_missing_claim_type():
    block = pre_dispatch_guard({"family": "executor", "op": "task"})
    assert block is not None
    assert block["reason"] == "INADMISSIBLE_CLAIM_TYPE"


def test_guard_blocks_empty_dispatch():
    block = pre_dispatch_guard({})
    assert block is not None
    assert block["reason"] == "UNKNOWN_OPERATION_CLASS"


def test_guard_never_returns_admit_authority():
    # The gate may allow dispatch; it may never itself mint authority.
    allowed = pre_dispatch_guard(
        {"family": "executor", "op": "task", "claim_type": "RECEIPT"}
    )
    assert allowed is None  # allow = absence of block, not an authority object
