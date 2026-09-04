"""E007 — intra-transaction state migration (TOCTOU) detection. 🔵 OBSERVED.

Completeness-critic goblin (gemma4-12b, local): all six prior epochs silently assumed the
governed state is STABLE during a single execution — no re-entrant/concurrent mutation
between the gate check and the effect. No test stated it. Confirmed live: gate blessed G0,
effect ran against a moved G1.

E007 closes the RE-ENTRANCY case with an atomic post-effect recheck → STATE_MIGRATED.
DOCUMENTED RESIDUAL: true multi-thread concurrency (another thread mutating mid-effect)
still needs a lock/version-CAS — infrastructure the single-threaded MVP does not have.
This epoch makes the single-threaded assumption CHECKED for re-entrancy, not silent.
"""
from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock, h_v

G0 = {"head": "A"}
G1 = {"head": "B"}
C, SC = "c" * 64, "s"


def test_e007_reentrant_migration_flagged():
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    live = {"h": h_v(G0)}                       # mutable governed state
    ex = Executor(clock, state_provider=lambda: live["h"])
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    # the effect itself migrates the state out from under the capability (re-entrancy)
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC,
                  effect=lambda: live.__setitem__("h", h_v(G1)))
    assert r.status == "STATE_MIGRATED"          # gate passed G0, but state moved during effect


def test_e007_stable_state_still_executes():
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    live = {"h": h_v(G0)}
    ex = Executor(clock, state_provider=lambda: live["h"])
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    # a benign effect that does NOT move the checked state → clean EXECUTED
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC,
                  effect=lambda: None)
    assert r.status == "EXECUTED"


def test_e007_no_provider_no_recheck():
    # legacy (no state_provider) has no derived state to recheck — unchanged behavior.
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    ex = Executor(clock)
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC, effect=lambda: None)
    assert r.status == "EXECUTED"


def test_e007_migrated_capability_is_still_consumed():
    # affine at-most-once holds: a STATE_MIGRATED attempt still spends the capability
    # (consume-before-effect), so it cannot be retried.
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    live = {"h": h_v(G0)}
    ex = Executor(clock, state_provider=lambda: live["h"])
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC,
              effect=lambda: live.__setitem__("h", h_v(G1)))
    live["h"] = h_v(G0)  # even if state is restored, the cap is spent
    r2 = ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC, effect=lambda: None)
    assert r2.status == "ALREADY_CONSUMED"
