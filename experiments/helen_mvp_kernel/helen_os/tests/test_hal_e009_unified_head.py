"""E009 — single governed-state head closes cross-layer divergence. 🔵 OBSERVED.

Autoresearch dual-heads finding (relayed synthesis, falsified against real code): the
capability layer (Executor.state_provider) and the transaction layer
(TransactionRuntime.current_state_hash) held two separate heads that could diverge — a
committed tx moved one to G1 while a κ minted for the stale G0 still executed. E009 binds
both to one GovernedStore. Anti-vacuity / Non-Transport again: read the single root, don't
keep a private copy that can go stale.
"""
from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock, h_v
from helen_os.kernel.governed_store import GovernedStore
from helen_os.kernel.transaction import TransactionRuntime

G0 = h_v({"head": "A"})
G1 = h_v({"head": "B"})


def test_e009_dual_heads_reproduced_without_store():
    # BEFORE (regression witness): separate heads diverge — the gap E009 closes.
    rt = TransactionRuntime(current_state_hash=G0)          # tx head
    rt.prepare("t", h_v({"e": 1})); rt.execute("t", lambda: G1)
    rt.evidence("t"); rt.commit("t")
    assert rt.current_state_hash == G1                      # tx head moved
    clock = LogicalClock()
    ex = Executor(clock, state_provider=lambda: G0)         # SEPARATE stale head
    cap = CapabilityFactory(clock).mint(binds_hash="c", pre_state_hash=G0,
                                        scope="s", admission_decision="ADMIT")
    r = ex.invoke(cap, expected_hash="c", pre_state_hash=G0, scope="s")
    assert r.status == "EXECUTED"                           # stale κ fires — the bug


def test_e009_single_store_blocks_stale_capability():
    # AFTER: both layers read ONE GovernedStore → the stale κ is rejected.
    store = GovernedStore(G0)
    clock = LogicalClock()
    ex = Executor(clock, state_provider=store.head)         # cap layer reads the store
    rt = TransactionRuntime(current_state_hash=G0, store=store)  # tx layer writes the store
    # a committed tx advances the SINGLE head G0 -> G1
    rt.prepare("t", h_v({"e": 1})); rt.execute("t", lambda: G1)
    rt.evidence("t"); rt.commit("t")
    assert store.head() == G1                               # one head moved
    # a κ minted for the now-stale G0 must fail — cap layer sees the same G1
    cap = CapabilityFactory(clock).mint(binds_hash="c", pre_state_hash=G0,
                                        scope="s", admission_decision="ADMIT")
    r = ex.invoke(cap, expected_hash="c", pre_state_hash=G0, scope="s")
    assert r.status == "PRE_STATE_MISMATCH"                 # divergence closed


def test_e009_store_head_authoritative_on_construction():
    # runtime constructed over a store adopts the store head, not its own arg.
    store = GovernedStore(G1)
    rt = TransactionRuntime(current_state_hash="ignored", store=store)
    assert rt._head() == G1
    assert rt.current_state_hash == G1


def test_e009_head_advances_only_via_execute():
    store = GovernedStore(G0)
    rt = TransactionRuntime(current_state_hash=G0, store=store)
    rt.prepare("t", h_v({"e": 1}))
    assert store.head() == G0                               # prepare does not move the head
    rt.execute("t", lambda: G1)
    assert store.head() == G1                               # execute advances the single head


def test_e009_e008_semantics_preserved_over_store():
    # the E008 four-state discipline still holds when backed by a store.
    store = GovernedStore(G0)
    rt = TransactionRuntime(current_state_hash=G0, store=store)
    rt.prepare("t", h_v({"e": 1})); rt.execute("t", lambda: G1); rt.evidence("t")
    assert rt.recover("t") == "COMMITTED"
    assert rt.is_committed("t")
    assert rt.replay_committed() == ["t"]
