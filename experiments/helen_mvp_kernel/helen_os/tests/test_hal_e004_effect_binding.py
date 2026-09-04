"""E004 — κ exact-effect binding + forged-type guard + ΔG-witnessed control. 🔵 OBSERVED.

Autoresearch (gemma4-12b, local) + relayed critique. Two findings this epoch:
  §8 scope authorizes an effect CLASS, not one transition — κ minted for e1 could be
     redirected to e2 (same scope). Fix: effect_hash, DERIVED at the choke point.
  #10 a duck-typed dict crashed invoke() with AttributeError instead of refusing.

CRITICAL discipline (relayed critique, accepted): the executor DERIVES the effect hash
from the request — it does NOT trust a caller-supplied effect_hash string. Anti-vacuity,
same theorem as the HAL Witness Law: don't trust the evaluated party to assert the fact
you check. Positive control witnesses ACTUAL ΔG (state hash changes), not a reported flag.

DOCUMENTED RESIDUAL: binds_hash (candidate) + pre_state_hash remain caller-asserted in
this MVP — deriving them needs a governed-state object; that is the next epoch.
"""
from helen_os.kernel.capability import (
    CapabilityFactory, Executor, LogicalClock, h_v,
)

C, PRE, SC = "c" * 64, "a" * 64, "ledger.append"
EFFECT_A = {"op": "append", "receipt": "R1"}
EFFECT_B = {"op": "append", "receipt": "R2"}  # different exact effect, same scope


def _rig():
    clock = LogicalClock()
    return clock, CapabilityFactory(clock), Executor(clock)


def _mint(f, effect_hash=""):
    return f.mint(binds_hash=C, pre_state_hash=PRE, scope=SC,
                  admission_decision="ADMIT", effect_hash=effect_hash)


def test_e004_wrong_effect_refused_derived_not_asserted():
    clock, f, ex = _rig()
    cap = _mint(f, effect_hash=h_v(EFFECT_A))  # κ bound to exactly EFFECT_A
    # attacker presents a κ valid on every other axis but requests EFFECT_B
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                  effect_request=EFFECT_B)
    assert r.status == "EFFECT_MISMATCH" and r.effect_ran is False


def test_e004_caller_cannot_forge_effect_hash():
    # the executor derives h_v(effect_request) ITSELF; there is no caller effect_hash
    # argument to echo. Presenting EFFECT_B cannot be laundered into EFFECT_A's hash.
    clock, f, ex = _rig()
    cap = _mint(f, effect_hash=h_v(EFFECT_A))
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                  effect_request=EFFECT_B)
    assert r.status == "EFFECT_MISMATCH"


def test_e004_correct_effect_executes():
    clock, f, ex = _rig()
    cap = _mint(f, effect_hash=h_v(EFFECT_A))
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                  effect_request=EFFECT_A)
    assert r.status == "EXECUTED"


def test_e004_unbound_effect_is_legacy():
    clock, f, ex = _rig()
    cap = _mint(f)  # effect_hash="" — unbound
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC)
    assert r.status == "EXECUTED"


def test_e004_forged_dict_refused_cleanly():
    clock, f, ex = _rig()
    fake = {"cap_id": "x", "nonce": "y", "holder": "", "effect_hash": ""}
    r = ex.invoke(fake, expected_hash=C, pre_state_hash=PRE, scope=SC)
    assert r.status == "CAP_TYPE_MISMATCH" and r.effect_ran is False  # no AttributeError


def test_e004_positive_control_witnesses_actual_delta_g():
    # anti-vacuity: prove the state ACTUALLY changed, not that a flag says so.
    clock, f, ex = _rig()
    cap = _mint(f, effect_hash=h_v(EFFECT_A))
    state = {"v": 0}
    before = h_v(state)
    r = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC,
                  effect_request=EFFECT_A,
                  effect=lambda: state.__setitem__("v", 1))
    after = h_v(state)
    assert r.status == "EXECUTED"
    assert after != before  # witnessed ΔG ≠ 0, not merely reported


def test_e004_effect_bound_still_one_shot():
    clock, f, ex = _rig()
    cap = _mint(f, effect_hash=h_v(EFFECT_A))
    ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC, effect_request=EFFECT_A)
    r2 = ex.invoke(cap, expected_hash=C, pre_state_hash=PRE, scope=SC, effect_request=EFFECT_A)
    assert r2.status == "ALREADY_CONSUMED"  # affine preserved under effect binding
