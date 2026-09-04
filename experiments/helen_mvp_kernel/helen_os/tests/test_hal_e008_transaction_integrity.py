"""E008 — internal transaction integrity under crash injection. 🔵 OBSERVED.

Extends E005 write-ahead intent into the full four-state machine. Target:
    Recover(τ) ∈ {NO_COMMIT, ONE_COMMITTED}   never ambiguous authoritative history.
Central law: status="COMMITTED" ≠ Committed(τ) — Committed is DERIVED from durable facts.
Replay consumes committed transitions only, so a ghost receipt/execution cannot enter
governed history. Includes the three sharpened falsifiers (relayed spec): capability
non-resurrection, commit-marker forgery without post-state, recovery monotonicity.
"""
from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock
from helen_os.kernel.transaction import (
    ABORTED, COMMITTED, EVIDENCED, EXECUTED, PREPARED,
    TransactionRuntime, h_v,
)

G0 = h_v({"head": "A"})
G1 = h_v({"head": "B"})
EFFECT = h_v({"op": "append", "r": "R1"})


def _fresh():
    return TransactionRuntime(current_state_hash=G0)


# ---- E005-01: crash before effect → NO_COMMIT, ΔG=0
def test_e008_crash_before_effect_no_commit():
    rt = _fresh()
    rt.prepare("tx", EFFECT)
    assert rt.recover("tx") in {"NO_COMMIT", "STALE_PRE_STATE"}
    assert not rt.is_committed("tx")
    assert rt.current_state_hash == G0  # governed state untouched


# ---- E005-02: crash after effect, before receipt → NEVER auto-commit
def test_e008_effect_without_receipt_never_auto_commits():
    rt = _fresh()
    rt.prepare("tx", EFFECT)
    rt.execute("tx", mutation=lambda: G1)   # side effect happened (state moved)
    assert rt.recover("tx") == "RECOVERY_REQUIRED"
    assert not rt.is_committed("tx")         # E=1, R=0 ⊬ C=1
    assert rt.replay_committed() == []       # moved state is NOT governed history


# ---- E005-03: crash after receipt, before commit → revalidate then commit
def test_e008_receipt_without_commit_revalidates():
    rt = _fresh()
    rt.prepare("tx", EFFECT)
    rt.execute("tx", mutation=lambda: G1)
    rt.evidence("tx")
    assert rt.recover("tx") == COMMITTED     # re-derived, not fabricated
    assert rt.is_committed("tx")


# ---- committed is DERIVED, not the status field
def test_e008_status_field_is_not_trusted():
    rt = _fresh()
    tx = rt.prepare("tx", EFFECT)
    tx.status = COMMITTED                    # forge the symbolic field
    assert not rt.is_committed("tx")         # no receipt/marker → derived False


# ---- E005-07 sharpened: commit marker forgery WITHOUT durable post-state
def test_e008_commit_marker_forgery_without_post_state():
    rt = _fresh()
    tx = rt.prepare("tx", EFFECT)
    tx.commit_marker = "forged"              # M=1 ...
    tx.execution_receipt_hash = "forged"     # ... and a matching-looking receipt
    # but post_state_hash is still None → derivation fails
    assert not rt.is_committed("tx")         # M(τ) ⊬ C(τ)


# ---- E005-05: replay reads committed transitions only
def test_e008_replay_ignores_partial_transactions():
    rt = _fresh()
    rt.prepare("tx1", EFFECT); rt.execute("tx1", lambda: G1); rt.evidence("tx1"); rt.commit("tx1")
    rt.prepare("tx2", EFFECT)                       # PREPARED only
    rt.prepare("tx3", EFFECT); rt.execute("tx3", lambda: h_v({"head": "C"}))  # EXECUTED only
    assert rt.replay_committed() == ["tx1"]


# ---- E005-04: idempotent recovery + at-most-one commit
def test_e008_recovery_is_idempotent():
    rt = _fresh()
    rt.prepare("tx", EFFECT); rt.execute("tx", lambda: G1); rt.evidence("tx")
    rt.recover("tx"); rt.recover("tx"); rt.recover("tx")
    assert rt.is_committed("tx")
    assert rt._committed_log.count("tx") == 1        # committed exactly once


# ---- recovery monotonicity: committed stays committed under repeated recovery
def test_e008_recovery_monotonicity():
    rt = _fresh()
    rt.prepare("tx", EFFECT); rt.execute("tx", lambda: G1); rt.evidence("tx"); rt.commit("tx")
    for _ in range(5):
        assert rt.recover("tx") == "COMMITTED_ONCE"  # C(τ) ⇒ C(Recover^n(τ))
        assert rt.is_committed("tx")


# ---- E005-06: stale prepared intent is not resumed against a moved world
def test_e008_stale_prepared_not_resumed():
    rt = _fresh()
    rt.prepare("stale", EFFECT)              # prepared against G0
    rt.current_state_hash = G1               # a different transition moved the world
    assert rt.recover("stale") == "STALE_PRE_STATE"
    assert not rt.is_committed("stale")


# ---- capability non-resurrection: Consumed(κ) ∧ ¬C(τ) ⊬ Reusable(κ)
def test_e008_capability_non_resurrection():
    clock = LogicalClock()
    ex = Executor(clock)
    cap = CapabilityFactory(clock).mint(
        binds_hash="c", pre_state_hash=G0, scope="s", admission_decision="ADMIT")
    # tx attempt consumes the cap, then "crashes" before commit (effect is a no-op here)
    ex.invoke(cap, expected_hash="c", pre_state_hash=G0, scope="s", effect=lambda: None)
    # recovery must NOT resurrect the spent capability for a retry
    r2 = ex.invoke(cap, expected_hash="c", pre_state_hash=G0, scope="s", effect=lambda: None)
    assert r2.status == "ALREADY_CONSUMED"   # failed tx does not mint reusable authority
