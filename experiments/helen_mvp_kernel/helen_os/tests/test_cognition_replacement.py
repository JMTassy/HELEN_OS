"""COGNITION_REPLACEMENT_INVARIANT_V0 — falsifiers. 🔵 OBSERVED.

THE INVARIANT under test (stated first):
    A well-formed governed application preserves its STRUCTURE (Π_struct) when its cognition is
    replaced — including by a deterministically stupid stub, a timeout, malformed output, or an
    adversary. Business quality may collapse; workflow legality, receipt discipline, gate order,
    tenant isolation, replay, and runtime identity may not.  C → C₀ ⇒ ΔΠ_struct = 0.

The suite is honest because it includes a POSITIVE CONTROL: a `leaky` application that violates
the thesis (recommendation writes state directly). The invariant MUST fail on it — a falsifier
that cannot fail proves nothing.
"""
from helen_os.audit.cognition_replacement import (
    AdversarialCognition, MalformedCognition, RealCognition, StubCognition, TimeoutCognition,
    APPROVED, EXECUTED, HOLD, CLOSED,
    cognition_replacement_invariant, pi_struct, run_application,
    DEFAULT_RUNTIME, _default_ctx,
)

REAL, STUB = RealCognition(), StubCognition()


# ─────────── the core thesis: structure survives cognition replacement ───────────
def test_wellformed_app_survives_replacement_by_stub():
    holds, sigs = cognition_replacement_invariant([REAL, STUB], leaky=False)
    assert holds                                    # ΔΠ_struct = 0
    assert sigs[0] == sigs[1]


def test_quality_is_allowed_to_differ_while_structure_does_not():
    # the OUTCOME diverges (real executes, stub holds) — proving the invariant is not trivially
    # true by making the two runs identical. Only STRUCTURE is required to match.
    real = run_application(REAL, _default_ctx(), DEFAULT_RUNTIME, leaky=False)
    stub = run_application(STUB, _default_ctx(), DEFAULT_RUNTIME, leaky=False)
    assert real.final_state == CLOSED and stub.final_state == CLOSED
    assert any(t.to_state == EXECUTED for t in real.transitions)      # real reached execution
    assert all(t.to_state != EXECUTED for t in stub.transitions)      # stub never did
    assert pi_struct(real) == pi_struct(stub)                         # …yet structure is identical


# ─────────── the positive control: the falsifier must catch a real leak ───────────
def test_leaky_app_is_caught_by_replacement():
    # LLMOutput ⇒ StateTransition. Invisible under Real (it recommends ACT, leak branch untaken);
    # detonates under the stub (recommends NO_ACTION → silent, receiptless state write).
    holds, _ = cognition_replacement_invariant([REAL, STUB], leaky=True)
    assert holds is False


def test_leak_is_invisible_without_replacement():
    # with only the cooperative cognition, the leaky app looks perfectly structural — which is
    # precisely why single-cognition testing misses it and replacement is required.
    holds, _ = cognition_replacement_invariant([REAL], leaky=True)
    assert holds is True


def test_leak_breaks_specific_structural_guarantees_under_stub():
    leaked = run_application(STUB, _default_ctx(), DEFAULT_RUNTIME, leaky=True)
    sig = dict(pi_struct(leaked))
    assert sig["every_transition_has_receipt"] is False      # the silent close had no receipt
    assert sig["all_transitions_legal"] is False             # VERIFIED→CLOSED is not in δ
    assert sig["cognition_never_wrote_state"] is False       # cognition wrote state directly
    assert sig["replay_reconstructs_final"] is False         # the eventless write can't be replayed


# ─────────── mutation sensitivity: failure degrades utility, not structure ───────────
def test_structure_invariant_across_the_full_cognition_ladder():
    ladder = [RealCognition(), StubCognition(), TimeoutCognition(),
              MalformedCognition(), AdversarialCognition()]
    holds, sigs = cognition_replacement_invariant(ladder, leaky=False)
    assert holds                                    # identical Π_struct across all five
    # and every structural predicate is TRUE for every run
    for s in sigs:
        d = dict(s)
        assert d["all_transitions_legal"] and d["every_transition_has_receipt"]
        assert d["cognition_never_wrote_state"] and d["connector_only_under_permit_e"]
        assert d["replay_reconstructs_final"] and d["tenant_isolation_holds"]


def test_adversarial_cognition_is_denied_at_the_effect_gate():
    # it verifies OK and demands ACT, but its out-of-policy effect is denied — no connector call.
    adv = run_application(AdversarialCognition(), _default_ctx(), DEFAULT_RUNTIME, leaky=False)
    assert adv.final_state == CLOSED
    assert adv.connector.invocations == []                   # effect gate held; nothing executed
    assert all(t.to_state != APPROVED for t in adv.transitions)


def test_missing_execute_capability_denies_effect():
    # CanReason ⊬ CanExecute — strip the capability and even Real cannot cross the effect gate.
    ctx = _default_ctx(); ctx["capabilities"] = ("read",)
    r = run_application(RealCognition(), ctx, DEFAULT_RUNTIME, leaky=False)
    assert r.connector.invocations == []
    assert r.final_state in (HOLD, CLOSED)
    assert pi_struct(r) == pi_struct(run_application(RealCognition(), _default_ctx(), DEFAULT_RUNTIME, leaky=False))


def test_cross_tenant_read_is_denied():
    r = run_application(RealCognition(), _default_ctx(), DEFAULT_RUNTIME, leaky=False)
    assert r.tenant_isolation_holds is True
