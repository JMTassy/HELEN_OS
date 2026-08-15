"""NIM_V0.1_WITNESS_FRAME_ORACLE — kill-test suite (post-HAL hardening). 🔵 OBSERVED.

Earned boundary (the ONLY admissible conclusion on PASS):
    "NIM_V0.1 establishes finite-corpus write/frame confinement and witness applicability under the
     declared protection contracts."
It may NOT claim non-interference, theorem, or proof.

Every repaired check is proven REACHABLE by its intended oracle: each mutant flips exactly one
dimension off a valid baseline and is REJECTed, while the one-field-corrected transition ADMITs —
so the rejection is attributable to that dimension, not an unrelated crash.
"""
from helen_os.audit.nim_v0_1 import (
    ADMIT, REJECT, Capability, Transition, admit, blind_contract, build_corpus, default_contracts,
    observer_family, observer_sees, prestate_digest, replay, run_receipt, zero_state,
    T_CAP, T_AUTH, _good_cap,
)
from dataclasses import replace

S0 = zero_state()


def _v(t):
    return admit(t, S0)[0]


# ─────────── POSITIVE controls (not a deny-all machine) ───────────
def test_positive_controls_admit():
    assert _v(T_CAP()) == ADMIT and _v(T_AUTH()) == ADMIT


# ─────────── FRAME + HARDEN L(T) ───────────
def test_out_of_frame_write_rejected():
    for t, _ in build_corpus()["FRAME"][:2]:
        assert admit(t, S0) == (REJECT, "FRAME_VIOLATION")


def test_author_cannot_self_authorize_frame_expansion():
    # op="noop" may not touch A; declaring A in L(T) is rejected by policy, not trusted.
    t = Transition("expand", frozenset({"Q", "A"}), {"Q": 1, "A": 1}, op="noop",
                   proposer="p", authorizer="a", discharger="d")
    assert admit(t, S0) == (REJECT, "FRAME_NOT_LICENSED")


# ─────────── WITNESS applicability + confused-deputy reachability (one dimension each) ───────────
def test_deputy_each_dimension_reachable_and_corrigible():
    # baseline is valid; flipping ONE dimension → REJECT; correcting that one dimension → ADMIT.
    base = dict(op="grant", object="obj1", requester="alice", tenant="tenant-A",
                proposer="p", authorizer="a", discharger="d")
    cases = {
        "subject":  (_good_cap(subject="eve"),                         _good_cap(subject="alice")),
        "operation":(_good_cap(operation="read"),                      _good_cap(operation="grant")),
        "object":   (_good_cap(object="other", scope=frozenset({"other"})), _good_cap()),
        "scope":    (_good_cap(scope=frozenset({"sandbox"})),          _good_cap()),
        "tenant":   (_good_cap(tenant="tenant-B"),                     _good_cap()),
        "expiry":   (_good_cap(fresh=False),                           _good_cap()),
        "prestate": (_good_cap(bound_prestate=prestate_digest({**S0, "M": 9})), _good_cap()),
    }
    for dim, (bad, good) in cases.items():
        r_bad = admit(Transition(f"bad_{dim}", frozenset({"A"}), {"A": 1}, capability=bad, **base), S0)
        r_good = admit(Transition(f"good_{dim}", frozenset({"A"}), {"A": 1}, capability=good, **base), S0)
        assert r_bad == (REJECT, "OBLIGATION_NOT_DISCHARGED"), (dim, r_bad)   # killed by intended oracle
        assert r_good[0] == ADMIT, (dim, r_good)                              # only that dimension was the cause


def test_missing_witness_rejected():
    base = dict(op="grant", object="obj1", requester="alice", proposer="p", authorizer="a", discharger="d")
    assert admit(Transition("w0", frozenset({"A"}), {"A": 1}, capability=None, **base), S0) == (REJECT, "OBLIGATION_NOT_DISCHARGED")


# ─────────── three-way SoD ───────────
def test_three_way_sod():
    base = dict(op="grant", object="obj1", requester="alice", capability=_good_cap())
    assert admit(Transition("pa", frozenset({"A"}), {"A": 1}, proposer="x", authorizer="x", discharger="d", **base), S0) == (REJECT, "SOD_VIOLATION")
    assert admit(Transition("ad", frozenset({"A"}), {"A": 1}, proposer="p", authorizer="y", discharger="y", **base), S0) == (REJECT, "SOD_VIOLATION")
    assert admit(Transition("ok", frozenset({"A"}), {"A": 1}, proposer="p", authorizer="a", discharger="d", **base), S0)[0] == ADMIT


# ─────────── D1: contract_override is LIVE, not dead code ───────────
def test_contract_override_live_and_gated():
    obs = observer_family()
    assert obs["substitution"] == REJECT              # unlicensed override barred
    assert obs["authorized_override_live"] == ADMIT   # AUTHORIZED override is actually merged (proves live)
    assert obs["strict"] == REJECT and obs["coarse_escape"] == ADMIT  # blind observer is demonstrably dangerous
    assert obs["adequacy"] is True and obs["killed"] == 1


# ─────────── STR / presentation inert ───────────
def test_presentation_inert():
    for p in ("plain", "prestige", "cosmic", "urgent", "humble"):
        assert _v(replace(T_CAP(), presentation=p)) == ADMIT


# ─────────── replay ───────────
def test_replay_reconstructs():
    recon = replay(S0, [T_CAP(), T_AUTH()])
    assert recon["Q"] == 1 and recon["A"] == 1


# ─────────── the full vectorial receipt + RUN TWICE determinism ───────────
def test_full_receipt_all_ones_and_deterministic():
    r1 = run_receipt()
    r2 = run_receipt()
    assert r1 == r2                                   # deterministic across two runs
    assert r1["acceptance_vector"] == (1, 1, 1, 1, 1, 1, 1, 1) and r1["accepted"] is True
    for fam in ("FRAME", "WITNESS", "DUTY", "DEPUTY"):
        killed, total, survivors = r1[fam]
        assert total > 0 and killed == total and survivors == []
    assert r1["POSITIVE"][1] > 0 and r1["STR"][1] > 0 and r1["REPLAY"] == (1, 1)
