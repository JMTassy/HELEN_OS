"""C13 — frame-bound witness receipt falsifiers. 🔵 OBSERVED.

Every executable witness carries its exact software frame; a PASS cannot transport
across frames unless the frame matches. PASS@F1 ⊬ PASS@F2.

C13-01 different commit          → REJECT_TRANSPORT
C13-02 dirty worktree differs    → REJECT_TRANSPORT
C13-03 different test artifact   → REJECT_TRANSPORT
C13-04 different environment     → HOLD
C13-05 missing frame field       → UNKNOWN
C13-06 exact same frame          → PASS
"""
from dataclasses import replace

from helen_os.frame.witness import (
    Transport, frame_hash, mint_receipt, transport, valid_receipt,
)

BASE = dict(
    claim_id="E013",
    repo_id="helen-conquest",
    branch="claude/doctrine-proposals",
    commit="05c9f10",
    worktree_hash="wt_clean",
    test_id="test_e013_hal_completeness",
    test_artifact_hash="art_v1",
    environment_hash="env_py311",
    toolchain_version="pytest-8.0",
    result="PASS",
    timestamp="T0",
)


def _r(**over):
    d = dict(BASE)
    d.update(over)
    return mint_receipt(**d)


# ---- C13-06: exact same frame + valid receipt → PASS
def test_c13_06_exact_frame_transports_pass():
    a, b = _r(), _r()
    assert transport(a, b) == (Transport.PASS, "FRAME_MATCH")
    assert valid_receipt(a) and frame_hash(a) is not None


# ---- C13-01: same result, different commit → REJECT_TRANSPORT
def test_c13_01_different_commit_rejects_transport():
    a, b = _r(commit="05c9f10"), _r(commit="84d057f")
    assert transport(a, b) == (Transport.REJECT_TRANSPORT, "E_CODE_FRAME_DIFFERS")


# ---- C13-02: same commit, dirty worktree differs → REJECT_TRANSPORT
def test_c13_02_dirty_worktree_rejects_transport():
    a, b = _r(worktree_hash="wt_clean"), _r(worktree_hash="wt_dirty_abc")
    assert transport(a, b) == (Transport.REJECT_TRANSPORT, "E_CODE_FRAME_DIFFERS")


# ---- C13-03: same source, different test artifact → REJECT_TRANSPORT
def test_c13_03_different_test_artifact_rejects_transport():
    a, b = _r(test_artifact_hash="art_v1"), _r(test_artifact_hash="art_v2")
    assert transport(a, b) == (Transport.REJECT_TRANSPORT, "E_CODE_FRAME_DIFFERS")


# ---- C13-04: same code artifact, different environment → HOLD
def test_c13_04_different_environment_holds():
    a, b = _r(environment_hash="env_py311"), _r(environment_hash="env_py312")
    assert transport(a, b) == (Transport.HOLD, "E_ENVIRONMENT_DIFFERS")


# ---- C13-05: missing frame field → UNKNOWN (h_F uncomputable)
def test_c13_05_missing_frame_field_unknown():
    a, b = _r(commit=""), _r()
    assert frame_hash(a) is None
    assert transport(a, b) == (Transport.UNKNOWN, "E_MISSING_FRAME_HASH")


# ---- tamper: field mutated after mint → self-hash fails → UNKNOWN
def test_c13_tampered_receipt_is_invalid():
    a = _r()
    tampered = replace(a, result="FAIL")   # flip result, keep stale receipt_hash
    assert not valid_receipt(tampered)
    assert transport(tampered, _r()) == (Transport.UNKNOWN, "E_INVALID_RECEIPT")


# ---- toolchain (env subset) differs → HOLD
def test_c13_toolchain_diff_holds():
    a, b = _r(toolchain_version="pytest-8.0"), _r(toolchain_version="pytest-8.2")
    assert transport(a, b) == (Transport.HOLD, "E_ENVIRONMENT_DIFFERS")


# ---- frame equality is symmetric and self-consistent
def test_c13_frame_hash_deterministic_and_symmetric():
    a, b = _r(timestamp="T9"), _r(timestamp="T0")
    # timestamp is NOT a frame field → same frame hash despite different timestamps
    assert frame_hash(a) == frame_hash(b)
    assert transport(a, b)[0] == Transport.PASS
