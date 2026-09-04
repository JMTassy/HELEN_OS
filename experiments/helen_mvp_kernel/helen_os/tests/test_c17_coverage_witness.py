"""C17 — coverage-witness (Π_D) falsifiers, A⁰ reference harness. 🔵 OBSERVED.

The resolver earns VALID_BY_TRANSPORT only on a DEFENSIBLE completeness claim; it may honestly
return UNKNOWN; it FAILS_UNSOUND only when it claimed a completeness it did not have. UNKNOWN is
a success state of the discipline, not a weakness.
"""
from helen_os.audit.c17 import (
    Dep, DepClass, Decision, PiD, Resolution, classify, decide,
)

EXEC = Dep(DepClass.FILE_READ, "executor.py")
POLICY = Dep(DepClass.ENV_READ, "POLICY_ROOT")
NATIVE = Dep(DepClass.OPAQUE_NATIVE, "libc.strlen")
EMPTY = frozenset()


def _pid(observed, complete, unresolved=EMPTY, d_minus=EMPTY):
    return PiD(nu="v0", omega=(DepClass.FILE_READ, DepClass.ENV_READ),
               d_plus=frozenset(observed), d_minus=frozenset(d_minus),
               unresolved=frozenset(unresolved), claims_complete=complete).bind()


# ---- C17-01a: HiddenSemanticDependency under a completeness claim → FAIL_UNSOUND (the danger)
def test_c17_01a_hidden_dep_under_completeness_is_fail_unsound():
    pid = _pid({EXEC}, complete=True)                       # sees only executor.py, claims complete
    true_support = frozenset({EXEC, POLICY})                # but φ really depends on POLICY_ROOT too
    dec, reason = decide(pid, frozenset({"POLICY_ROOT"}), true_support)
    assert dec == Decision.FAIL_UNSOUND and reason == "HIDDEN_DEP_UNDER_COMPLETENESS_CLAIM"
    assert dec != Decision.VALID_BY_TRANSPORT               # the forbidden result


# ---- C17-01b: same hidden dep, but ν does NOT claim completeness → honest UNKNOWN (PASS_C17)
def test_c17_01b_no_completeness_claim_is_unknown():
    pid = _pid({EXEC}, complete=False)                      # ν admits it may not be complete
    true_support = frozenset({EXEC, POLICY})
    dec, reason = decide(pid, frozenset({"POLICY_ROOT"}), true_support)
    assert dec == Decision.UNKNOWN and reason == "NO_COMPLETENESS_CLAIM"


# ---- C17-02: NewBypassArtifact — a change inside the D⁻ discovery scope → INVALIDATED
def test_c17_02_discovery_scope_change_invalidates():
    pid = _pid({EXEC}, complete=True, d_minus={"ns:governed"})   # closed-world over ns:governed
    true_support = frozenset({EXEC})
    dec, reason = decide(pid, frozenset({"ns:governed"}), true_support)   # a new artifact appears
    assert dec == Decision.INVALIDATED and reason == "DISCOVERY_SCOPE_CHANGED"
    assert dec != Decision.VALID_BY_TRANSPORT               # old absence PASS cannot transport


# ---- known observed dep changed → INVALIDATED
def test_c17_known_dep_changed_invalidates():
    pid = _pid({EXEC}, complete=True)
    dec, reason = decide(pid, frozenset({"executor.py"}), frozenset({EXEC}))
    assert dec == Decision.INVALIDATED and reason == "KNOWN_DEP_CHANGED"


# ---- FAIL_UNSOUND when completeness is claimed over an admittedly OPAQUE relevant class
def test_c17_complete_over_opaque_is_fail_unsound():
    pid = _pid({EXEC}, complete=True, unresolved={DepClass.OPAQUE_NATIVE})
    true_support = frozenset({EXEC, NATIVE})               # φ touches native code, flagged opaque
    dec, reason = decide(pid, EMPTY, true_support)
    assert dec == Decision.FAIL_UNSOUND and reason == "COMPLETE_CLAIMED_OVER_OPAQUE_CLASS"


# ---- UNKNOWN is a SUCCESS state: opaque relevant class + honest (no completeness claim)
def test_c17_opaque_without_claim_is_unknown_not_fail():
    pid = _pid({EXEC}, complete=False, unresolved={DepClass.OPAQUE_NATIVE})
    dec, _ = decide(pid, EMPTY, frozenset({EXEC, NATIVE}))
    assert dec == Decision.UNKNOWN                          # honestly bounded, not FAIL


# ---- positive control (non-vacuity): fully covered, defensible, stable → VALID_BY_TRANSPORT
def test_c17_covered_and_stable_transports():
    pid = _pid({EXEC, POLICY}, complete=True)              # observes everything φ depends on
    dec, reason = decide(pid, EMPTY, frozenset({EXEC, POLICY}))
    assert dec == Decision.VALID_BY_TRANSPORT and reason == "COVERED_AND_STABLE"


# ---- no completeness claim ⇒ UNKNOWN even when fully covered (transport needs a defensible claim)
def test_c17_covered_but_no_claim_is_unknown():
    pid = _pid({EXEC, POLICY}, complete=False)
    dec, reason = decide(pid, EMPTY, frozenset({EXEC, POLICY}))
    assert dec == Decision.UNKNOWN and reason == "NO_COMPLETENESS_CLAIM"


# ---- native / dynamic classes are OPAQUE by construction (never certifiable here, not a sandbox)
def test_c17_native_and_dynamic_are_opaque():
    assert classify(DepClass.OPAQUE_NATIVE) == Resolution.OPAQUE
    assert classify(DepClass.UNKNOWN_DYNAMIC) == Resolution.OPAQUE
    assert classify(DepClass.FILE_READ) == Resolution.RESOLVED


# ---- Π_D self-hash is deterministic
def test_c17_pid_bind_deterministic():
    a = _pid({EXEC}, complete=True)
    b = _pid({EXEC}, complete=True)
    assert a.sigma == b.sigma and a.sigma != ""
