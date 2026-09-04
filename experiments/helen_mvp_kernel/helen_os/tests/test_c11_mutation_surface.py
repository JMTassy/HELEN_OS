"""C11 — mutation-surface completeness falsifiers. 🔵 OBSERVED.

The algebra classifies each governed-state mutation sink and fails closed: any BYPASS → FAIL,
any UNCLASSIFIED → INCOMPLETE, PASS_SCOPED only when every enumerated reachable governed sink is
MEDIATED — and PASS_SCOPED never implies M_enumerated == M_reachable.

C11-01 known legal commit        → MEDIATED
C11-02 synthetic direct mutation → BYPASS  (→ status FAIL)
C11-03 unresolved sink           → UNCLASSIFIED
C11-04 test-only helper          → NON_GOVERNED
C11-05 any UNCLASSIFIED          → status INCOMPLETE (never PASS_SCOPED)
plus: the REAL kernel inventory @ c94fe32 is honestly INCOMPLETE.
"""
from helen_os.audit.c11 import (
    C11Status, C11Surface, Cls, Reach, KERNEL_INVENTORY, c11_status, classify, run_c11,
)


def _surface(reach, domain="committed_head", passes=True):
    return C11Surface(
        id="s", evidence_refs="f:1", symbol="sym", state_domain=domain,
        reachability_basis=reach, boundary="TransactionRuntime.commit",
        passes_declared_boundary=passes, mutation_kind="k",
    )


# ---- C11-01: legal commit sink → MEDIATED
def test_c11_01_legal_commit_is_mediated():
    assert classify(_surface(Reach.DIRECT_CALL_GRAPH, passes=True)) == Cls.MEDIATED


# ---- C11-02: synthetic direct mutation that skips the boundary → BYPASS → FAIL
def test_c11_02_direct_mutation_is_bypass():
    s = _surface(Reach.DIRECT_CALL_GRAPH, passes=False)   # reachable, governed, skips boundary
    assert classify(s) == Cls.BYPASS
    assert c11_status([s]) == (C11Status.FAIL, "BYPASS_FOUND")


# ---- C11-03: unresolved reachability of a governed sink → UNCLASSIFIED (fail-closed)
def test_c11_03_unresolved_is_unclassified():
    assert classify(_surface(Reach.UNRESOLVED)) == Cls.UNCLASSIFIED


# ---- C11-04: test-only helper → NON_GOVERNED (not a production bypass)
def test_c11_04_test_only_is_non_governed():
    assert classify(_surface(Reach.TEST_ONLY, passes=False)) == Cls.NON_GOVERNED


# ---- C11-05: any UNCLASSIFIED present ⇒ status INCOMPLETE, never PASS_SCOPED
def test_c11_05_unclassified_blocks_pass_scoped():
    surfaces = [_surface(Reach.DIRECT_CALL_GRAPH, passes=True),   # a MEDIATED one
                _surface(Reach.UNRESOLVED)]                        # and an UNCLASSIFIED one
    status, reason = c11_status(surfaces)
    assert status == C11Status.INCOMPLETE and reason == "UNCLASSIFIED_PRESENT"


# ---- non-governed sink never counts as a bypass even if it skips the boundary
def test_c11_non_governed_sink_never_bypass():
    s = _surface(Reach.DIRECT_CALL_GRAPH, domain="ui_cache", passes=False)
    assert classify(s) == Cls.NON_GOVERNED
    assert c11_status([s]) == (C11Status.PASS_SCOPED, "NO_BYPASS_OVER_ENUMERATED_SURFACES")


# ---- FAIL dominates INCOMPLETE (a bypass outranks an unknown)
def test_c11_fail_dominates_incomplete():
    surfaces = [_surface(Reach.DIRECT_CALL_GRAPH, passes=False),  # BYPASS
                _surface(Reach.UNRESOLVED)]                        # UNCLASSIFIED
    assert c11_status(surfaces)[0] == C11Status.FAIL


# ---- the REAL kernel inventory is honestly INCOMPLETE @ c94fe32
def test_c11_real_kernel_inventory_is_incomplete():
    report = run_c11()
    assert report["status"] == "INCOMPLETE"
    # the two direct governed-state setters are the unresolved sinks that block PASS_SCOPED
    unresolved = {s["id"] for s in report["surfaces"] if s["classification"] == "UNCLASSIFIED"}
    assert "store.advance" in unresolved
    assert "tx.current_state_hash" in unresolved
    # and no confirmed BYPASS (we cannot prove production-reachability either → not FAIL)
    assert report["bypass_count"] == 0
    # the mediated ones are the boundary-crossing sinks
    mediated = {s["id"] for s in report["surfaces"] if s["classification"] == "MEDIATED"}
    assert {"tx.commit", "tx._advance", "capability.consume"} <= mediated
