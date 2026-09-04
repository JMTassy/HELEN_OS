"""C13 forged-frame falsifier — the swarm's designated first attack. 🔵 OBSERVED.

C13's disclosed residual: frame digests are CALLER-SUPPLIED; witness.py never harvests
git / filesystem / environment. So transport proves  PASS@declared-F ⊬ PASS@declared-F,
NOT  PASS@measured-F.

These tests characterize the vulnerability as a runnable witness (green = the residual is
real and bounded), and stand as a TRIPWIRE: the day a verifier-owned FrameHarvester lands,
test_c13_no_verifier_owned_harvester_exists must flip and be revisited. This is the one
boundary where the H* law (ANCHOR → COMPARE → EMIT) is violated — the anchor is caller-owned,
not machine-derived. Everywhere else (HAL recompute_live, quorum recompute, Executor
choke-point, TransactionRuntime._head via GovernedStore) the anchor is machine-owned.
"""
from helen_os.frame.witness import Transport, mint_receipt, transport

BASE = dict(
    claim_id="E013", repo_id="helen-conquest", branch="claude/doctrine-proposals",
    commit="05c9f10", worktree_hash="wt_clean", test_id="t",
    test_artifact_hash="art_v1", environment_hash="env", toolchain_version="tc",
    result="PASS", timestamp="T0",
)


def _r(**over):
    d = dict(BASE)
    d.update(over)
    return mint_receipt(**d)


def test_c13_transport_is_blind_to_physical_head():
    # Both receipts DECLARE a commit that is NOT the real HEAD (05c9f10 in this frame).
    # transport still PASSes: it compares declared frames and never consults the repo.
    a = _r(commit="DEADBEEFcafe")   # a lie about the frame
    b = _r(commit="DEADBEEFcafe")   # the same lie, agreed between two dishonest receipts
    assert transport(a, b) == (Transport.PASS, "FRAME_MATCH")


def test_c13_dishonest_clean_worktree_is_undetectable():
    # A caller can declare a CLEAN worktree while the physical tree is dirty; C13 cannot tell,
    # because nothing measures the tree. Declared-equal ⇒ PASS regardless of physical truth.
    honest = _r(worktree_hash="wt_measured")
    forged = _r(worktree_hash="wt_measured")
    assert transport(forged, honest) == (Transport.PASS, "FRAME_MATCH")


def test_c13_no_verifier_owned_harvester_exists():
    # The missing morphism: no function in witness.py measures the physical frame, and the
    # module imports no filesystem/process access. The anchor is caller-owned, not derived.
    # TRIPWIRE: adding a harvester (git rev-parse / worktree digest / env fingerprint) flips this.
    import helen_os.frame.witness as w
    assert not [n for n in dir(w) if "harvest" in n.lower() or "measure" in n.lower()]
    assert not hasattr(w, "os") and not hasattr(w, "subprocess")
