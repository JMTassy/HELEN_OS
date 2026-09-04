"""E002 guard — pre_state_hash totality contract. 🔵 OBSERVED.

Autoresearch BOUNDARY finding (gemma4-12b, local): "Semantic State Desynchronization."
Classification: caller-contract gap, NOT a capability.py logic bug. The equality check
is correct; it is only as complete as the hash the caller commits. These tests pin the
contract: total-hash CATCHES a hidden mutation; under-hash is a documented caller violation.
"""
from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock
from helen_os.kernel.hal import h_v


def _rig():
    clock = LogicalClock()
    return clock, CapabilityFactory(clock), Executor(clock)


def test_e002_total_hash_catches_hidden_mutation():
    """Contract honored: pre_state_hash commits the FULL state → any mutation caught."""
    clock, factory, ex = _rig()
    state = {"Balance": 100, "Internal_Flag": "open"}
    cap = factory.mint(binds_hash="c", pre_state_hash=h_v(state),
                       scope="w", admission_decision="ADMIT")
    state["Internal_Flag"] = "LOCKED"  # hidden mutation to a non-obvious field
    r = ex.invoke(cap, expected_hash="c", pre_state_hash=h_v(state), scope="w")
    assert r.status == "PRE_STATE_MISMATCH"  # total commitment defeats desync
    assert r.effect_ran is False


def test_e002_undocumented_underhash_is_caller_violation():
    """Contract violated: caller commits only a subset → mutation to an omitted field
    slips through. This is a CALLER error the layer cannot detect, pinned here so the
    totality requirement is regression-guarded, not silently forgotten."""
    clock, factory, ex = _rig()
    partial = lambda s: h_v({"Balance": s["Balance"]})  # omits Internal_Flag
    state = {"Balance": 100, "Internal_Flag": "open"}
    cap = factory.mint(binds_hash="c", pre_state_hash=partial(state),
                       scope="w", admission_decision="ADMIT")
    state["Internal_Flag"] = "LOCKED"
    r = ex.invoke(cap, expected_hash="c", pre_state_hash=partial(state), scope="w")
    assert r.status == "EXECUTED"  # DOCUMENTED failure mode of under-hashing
    # The remedy is the contract (commit full state), not a code change to invoke().
