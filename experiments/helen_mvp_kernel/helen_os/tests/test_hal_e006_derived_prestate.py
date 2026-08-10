"""E006 — pre-state DERIVED at the choke point, not caller-asserted. 🔵 OBSERVED.

Autoresearch (gemma4-12b, local): the executor holds an authoritative state source and
derives the current state hash itself, ignoring the caller-supplied pre_state_hash. Closes
the deepest E004 residual: candidate/pre-state were caller-asserted. Same anti-vacuity law
as HAL (don't trust the evaluated party to assert the fact you check) and E004 (effect).

REMAINING SLIVER (documented, not solved): binds_hash (candidate) is still caller-asserted
in this MVP — deriving it needs a canonical candidate object passed to invoke(). E007.
"""
from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock, h_v

G0 = {"ledger_head": "A"}
G1 = {"ledger_head": "B"}  # state after it moves
C, SC = "c" * 64, "s"


def test_e006_stale_state_attack_fails_when_derived():
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    # authoritative state source: currently reports G1 (state has moved past G0)
    current = {"h": h_v(G1)}
    ex = Executor(clock, state_provider=lambda: current["h"])
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    # caller LIES: echoes cap's own pre_state_hash (claims state is still G0)
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC)
    assert r.status == "PRE_STATE_MISMATCH" and r.effect_ran is False


def test_e006_matching_derived_state_executes():
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    current = {"h": h_v(G0)}  # state still at G0 — matches the capability
    ex = Executor(clock, state_provider=lambda: current["h"])
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    # even if the caller supplies garbage, the DERIVED value is what's checked
    r = ex.invoke(cap, expected_hash=C, pre_state_hash="caller-garbage", scope=SC)
    assert r.status == "EXECUTED"


def test_e006_caller_pre_state_ignored_when_provider_present():
    # the caller cannot make a stale κ pass by supplying a matching-looking value:
    # the provider is authoritative, the caller arg is dead.
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    current = {"h": h_v(G1)}
    ex = Executor(clock, state_provider=lambda: current["h"])
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC)  # caller says G0
    assert r.status == "PRE_STATE_MISMATCH"  # provider says G1 — caller ignored


def test_e006_legacy_no_provider_trusts_caller():
    # back-compat: no state_provider → caller-supplied pre_state_hash path unchanged.
    clock = LogicalClock()
    f = CapabilityFactory(clock)
    ex = Executor(clock)  # no provider
    cap = f.mint(binds_hash=C, pre_state_hash=h_v(G0), scope=SC, admission_decision="ADMIT")
    assert ex.invoke(cap, expected_hash=C, pre_state_hash=h_v(G0), scope=SC).status == "EXECUTED"
