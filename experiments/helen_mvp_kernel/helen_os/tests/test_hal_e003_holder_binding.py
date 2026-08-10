"""E003 — κ holder binding refuses cross-actor handoff. 🔵 OBSERVED.

Autoresearch design epoch (gemma4-12b, local): κ bound candidate/pre-state/scope/
expiry/nonce but NOT a holder, so affine consumption stopped REUSE not HANDOFF.
Smallest fix (matching E001/E002 optional-binding pattern): opaque `holder`, enforced
only when set. Residual (documented): credential theft still lets the true secret-bearer
invoke — reduction, not elimination.
"""
from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock

C, PRE, SC = "c" * 64, "a" * 64, "ledger.append"


def _rig():
    clock = LogicalClock()
    return clock, CapabilityFactory(clock), Executor(clock)


def _mint(f, holder=""):
    return f.mint(binds_hash=C, pre_state_hash=PRE, scope=SC,
                  admission_decision="ADMIT", holder=holder)


def test_e003_wrong_holder_refused_and_not_consumed():
    clock, f, ex = _rig()
    cap = _mint(f, holder="actor_A")
    # actor_B presents its own id — handoff attempt
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                  presented_holder="actor_B")
    assert r.status == "HOLDER_MISMATCH" and r.effect_ran is False
    # κ not spent by the failed attempt — true holder can still use it
    r2 = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                   presented_holder="actor_A")
    assert r2.status == "EXECUTED"


def test_e003_correct_holder_executes():
    clock, f, ex = _rig()
    cap = _mint(f, holder="actor_A")
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                  presented_holder="actor_A")
    assert r.status == "EXECUTED"


def test_e003_unbound_holder_is_legacy():
    clock, f, ex = _rig()
    cap = _mint(f)  # holder="" — unbound
    # legacy callers pass no presented_holder and still work
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC)
    assert r.status == "EXECUTED"


def test_e003_holder_bound_still_one_shot():
    clock, f, ex = _rig()
    cap = _mint(f, holder="actor_A")
    ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC, presented_holder="actor_A")
    # affine guarantee preserved under holder binding
    r2 = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC, presented_holder="actor_A")
    assert r2.status == "ALREADY_CONSUMED"
