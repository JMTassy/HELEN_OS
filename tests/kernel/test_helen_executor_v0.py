"""Tests for the HELEN Executor v0 — routing, receipts, and the I()-gated keep/reject."""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "executor", Path(__file__).resolve().parents[2] / "scripts/kernel/helen_executor_v0.py")
ex = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ex)

GOOD_CANDIDATE = {
    "id": "c1", "authority": False, "owner": "reducer",
    "proposer": "builder", "validator": "hal",
    "ledger_ops": [{"op": "append"}],
    "memory_mutations": [{"key": "k", "receipt": "sha256:r"}],
    "projections": [{"name": "v", "read_only": True}],
    "cold_restore": {"repo": "r", "branch": "b", "commit": "c", "ledger_checksum": "s"},
    "tool_calls": [{"name": "fs_inspect", "gate": "approved", "perm": "READ"}],
}


def test_read_hand_keep():
    r = ex.execute({"hand": "fs_inspect", "args": {"path": "."}})
    assert r["decision"] == "KEEP"
    assert r["receipt"]["schema"] == "EXECUTOR_RECEIPT_V0"
    assert r["receipt"]["authority"] is False


def test_unknown_hand_rejects():
    r = ex.execute({"hand": "nuke", "args": {}})
    assert r["decision"] == "REJECT"


def test_integration_candidate_passing_I_keeps():
    r = ex.execute({"hand": "fs_inspect", "args": {"path": "."},
                    "integration_candidate": GOOD_CANDIDATE})
    assert r["invariant_check"]["I"] == 1
    assert r["decision"] == "KEEP"
    assert r["receipt"]["I"] == 1


def test_integration_candidate_failing_I_rejects_even_if_hand_succeeds():
    bad = dict(GOOD_CANDIDATE, authority=True)  # violates authority_explicit
    r = ex.execute({"hand": "fs_inspect", "args": {"path": "."},
                    "integration_candidate": bad})
    assert r["invariant_check"]["I"] == 0
    assert r["decision"] == "REJECT"          # hand succeeded, but I()=0 blocks KEEP
    assert "I()=0" in r["metric"].get("reason", "")


def test_declared_slot_hand_runs_but_marks_declared():
    r = ex.execute({"hand": "map_builder", "args": {}})
    assert r["output"].get("declared") is True


def test_receipt_schema_stable():
    rec = ex.execute({"hand": "git_status", "args": {}})["receipt"]
    for k in ("schema", "authority", "claim", "hand", "output_sha256", "metric", "decision"):
        assert k in rec
    assert rec["claim"] == "NO_CLAIM"
