"""Tests for I(), the kernel-invariant checker. Deterministic, no network.

A fully-compliant candidate passes (I=1); each invariant has a violating candidate
that flips exactly that invariant to fail (I=0).
"""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "invck", Path(__file__).resolve().parents[2] / "scripts/kernel/invariant_checker_v0.py")
I = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(I)


GOOD = {
    "id": "cand-001",
    "authority": False,
    "owner": "reducer",
    "proposer": "builder", "validator": "hal",
    "ledger_ops": [{"op": "append", "payload": "x"}],
    "memory_mutations": [{"key": "skill.v2", "receipt": "sha256:abc"}],
    "projections": [{"name": "wulmoji_view", "read_only": True}],
    "cold_restore": {"repo": "conquest-oracle-town", "branch": "claude/gallant-khayyam",
                     "commit": "deadbeef", "ledger_checksum": "sha256:def"},
    "tool_calls": [{"name": "fs_inspect", "gate": "approved", "perm": "READ"}],
}


def test_good_candidate_passes():
    r = I.check(GOOD)
    assert r["I"] == 1 and r["ok"] is True
    assert r["failed_invariants"] == []
    assert r["authority"] is False and r["claim"] == "NO_CLAIM"


def test_append_only_violation():
    bad = dict(GOOD, ledger_ops=[{"op": "overwrite", "payload": "x"}])
    r = I.check(bad)
    assert r["I"] == 0 and "append_only_ledger" in r["failed_invariants"]


def test_authority_must_be_explicit_and_false():
    miss = {k: v for k, v in GOOD.items() if k != "authority"}
    assert "authority_explicit" in I.check(miss)["failed_invariants"]
    tru = dict(GOOD, authority=True)
    assert "authority_explicit" in I.check(tru)["failed_invariants"]


def test_proposer_equals_validator_violation():
    bad = dict(GOOD, proposer="hal", validator="hal")
    assert "single_owner_governance" in I.check(bad)["failed_invariants"]


def test_silent_memory_mutation_violation():
    bad = dict(GOOD, memory_mutations=[{"key": "skill.v2", "receipt": ""}])
    assert "no_silent_memory_mutation" in I.check(bad)["failed_invariants"]


def test_projection_must_be_read_only():
    bad = dict(GOOD, projections=[{"name": "leaky", "read_only": False}])
    assert "projection_downstream" in I.check(bad)["failed_invariants"]


def test_cold_restore_incomplete_violation():
    bad = dict(GOOD, cold_restore={"repo": "x", "branch": "y"})  # missing commit + checksum
    assert "cold_restore_valid" in I.check(bad)["failed_invariants"]


def test_sovereign_write_tool_violation():
    bad = dict(GOOD, tool_calls=[{"name": "ledger_write", "gate": "approved", "perm": "WRITE_SOVEREIGN"}])
    assert "bounded_tool_execution" in I.check(bad)["failed_invariants"]


def test_ungated_tool_violation():
    bad = dict(GOOD, tool_calls=[{"name": "shell", "gate": "none", "perm": "WRITE"}])
    assert "bounded_tool_execution" in I.check(bad)["failed_invariants"]


def test_schema_stable():
    r = I.check(GOOD)
    for k in ("schema", "checker", "authority", "claim", "candidate_sha256", "I", "ok",
              "failed_invariants", "invariants"):
        assert k in r
    assert len(r["invariants"]) == 7
