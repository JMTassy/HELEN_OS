"""E005 — ghost-execution detection via write-ahead intent. 🔵 OBSERVED.

Autoresearch (gemma4-12b, local): write-ahead intent → recovery scan → ghost = PREPARED
without COMMITTED. Detection, not prevention. Witnesses the doctrine §13 distinction:
execution ≠ committed governed state. Also witnesses that write-ahead ORDER is load-bearing.
"""
from helen_os.kernel.intent_log import (
    COMMITTED, PREPARED, IntentLog, detect_ghosts, run_with_intent,
)
from helen_os.kernel.hal import h_v


def test_e005_clean_run_leaves_no_ghost():
    log = IntentLog()
    state = {"v": 0}
    status = run_with_intent(log, "txn_ok", h_v({"e": 1}),
                             lambda: state.__setitem__("v", 1))
    assert status == COMMITTED
    assert state["v"] == 1          # effect happened
    assert detect_ghosts(log) == []  # and it committed → no ghost


def test_e005_crash_between_effect_and_commit_is_detected():
    log = IntentLog()
    state = {"v": 0}
    # crash AFTER the side effect, BEFORE the receipt/commit
    status = run_with_intent(log, "txn_ghost", h_v({"e": 1}),
                             lambda: state.__setitem__("v", 1),
                             crash_before_commit=True)
    assert status == PREPARED        # left dangling
    assert state["v"] == 1           # ΔG ≠ 0 — the mutation really happened
    # recovery scan proves the ghost: state changed but no receipt committed
    assert detect_ghosts(log) == ["txn_ghost"]


def test_e005_write_ahead_order_is_load_bearing():
    # The intent is recorded BEFORE the effect, so even a crash makes the txn visible
    # to recovery. Prove: after a pre-commit crash, the txn is already in the log.
    log = IntentLog()
    run_with_intent(log, "txn_x", h_v({"e": 2}), lambda: None,
                    crash_before_commit=True)
    assert log.status("txn_x") == PREPARED  # visible despite the "crash"


def test_e005_multiple_txns_only_uncommitted_are_ghosts():
    log = IntentLog()
    run_with_intent(log, "a", "h", lambda: None)                       # commits
    run_with_intent(log, "b", "h", lambda: None, crash_before_commit=True)  # ghost
    run_with_intent(log, "c", "h", lambda: None)                       # commits
    assert detect_ghosts(log) == ["b"]


def test_e005_prepare_is_idempotent():
    log = IntentLog()
    log.prepare("t", "h1")
    log.commit("t")
    log.prepare("t", "h2")  # re-prepare must not resurrect/erase committed state
    assert log.status("t") == COMMITTED
