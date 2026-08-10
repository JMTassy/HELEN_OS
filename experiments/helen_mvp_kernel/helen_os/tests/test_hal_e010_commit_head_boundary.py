"""E010 — the authoritative head advances only at commit. 🔵 OBSERVED.

Deepest finding (relayed meditation, falsified against committed E008/E009 code): execute()
advanced the head to a computed-but-uncommitted post-state, so a crash after execute left
G_head=G1 with no receipt and no commit — the ambiguous half-state E008 forbids. E010 makes
the head the LATEST COMMITTED head at all times:

    EXECUTED ⊬ COMMITTED        G_head = G_post ⇒ Committed(τ)
    before commit: head = pre   after commit: head = post   (advance exactly once)

Commit is the single serialization point, with a compare-and-swap on the pre-state so an
interleaved committed tx cannot be silently overwritten. (In-memory MVP; durable atomic
state+receipt+marker boundary remains the production substrate — E008 residual.)
"""
from helen_os.kernel.governed_store import GovernedStore
from helen_os.kernel.transaction import ABORTED, COMMITTED, TransactionRuntime, h_v

G0 = h_v({"head": "A"})
G1 = h_v({"head": "B"})
G2 = h_v({"head": "C"})


def _rig(store=None):
    store = store or GovernedStore(G0)
    return store, TransactionRuntime(current_state_hash=G0, store=store)


def test_e010_execute_does_not_advance_head():
    store, rt = _rig()
    rt.prepare("t", h_v({"e": 1}))
    rt.execute("t", lambda: G1)
    assert rt._txs["t"].status == "EXECUTED"
    assert rt._txs["t"].post_state_hash == G1   # pending post-state computed
    assert store.head() == G0                   # but head unmoved — EXECUTED ⊬ head advance


def test_e010_crash_after_execute_keeps_committed_head():
    # the exact half-state E008 forbids: effect computed, crash before commit.
    store, rt = _rig()
    rt.prepare("t", h_v({"e": 1}))
    rt.execute("t", lambda: G1)                  # 💥 crash simulated: stop here
    assert store.head() == G0                    # authoritative head still G0
    assert not rt.is_committed("t")
    assert rt.replay_committed() == []           # nothing committed → nothing to replay


def test_e010_head_advances_exactly_once_at_commit():
    store, rt = _rig()
    rt.prepare("t", h_v({"e": 1})); rt.execute("t", lambda: G1); rt.evidence("t")
    assert store.head() == G0
    assert rt.commit("t") == COMMITTED
    assert store.head() == G1                    # advanced at commit
    assert rt.commit("t") == "ALREADY_COMMITTED"
    assert store.head() == G1                    # not advanced twice
    assert rt._committed_log.count("t") == 1


def test_e010_head_equals_post_implies_committed():
    # the property-based invariant: G_head == G_post ⇒ Committed(τ)
    store, rt = _rig()
    rt.prepare("t", h_v({"e": 1})); rt.execute("t", lambda: G1); rt.evidence("t")
    assert not (store.head() == G1)              # pre-commit: head != post, and not committed
    rt.commit("t")
    assert store.head() == G1 and rt.is_committed("t")   # head==post ⟺ committed


def test_e010_interleaved_commit_cas_blocks_stale():
    # two txs prepared at G0; whichever commits first moves the head; the other is stale.
    store, rt = _rig()
    rt.prepare("A", h_v({"e": "a"})); rt.execute("A", lambda: G1); rt.evidence("A")
    rt.prepare("B", h_v({"e": "b"})); rt.execute("B", lambda: G2); rt.evidence("B")
    assert rt.commit("A") == COMMITTED           # A wins, head G0 -> G1
    assert store.head() == G1
    assert rt.commit("B") == "STALE_PRE_STATE"   # B's pre (G0) != head (G1) → refused
    assert store.head() == G1                    # B did NOT apply
    assert not rt.is_committed("B")
    assert rt.replay_committed() == ["A"]         # exactly one committed transition


def test_e010_no_store_legacy_also_advances_only_at_commit():
    # the fix holds on the legacy (no-store) path too: current_state_hash moves at commit.
    rt = TransactionRuntime(current_state_hash=G0)
    rt.prepare("t", h_v({"e": 1})); rt.execute("t", lambda: G1)
    assert rt.current_state_hash == G0           # execute does not move the legacy head
    rt.evidence("t"); rt.commit("t")
    assert rt.current_state_hash == G1           # commit does
