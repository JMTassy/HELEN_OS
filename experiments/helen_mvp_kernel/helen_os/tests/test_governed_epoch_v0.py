"""GOVERNED_EPOCH_V0 — one-complete-epoch kill-suite. 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "one governed-causal-discovery epoch produces a WITNESSED contraction whose replay
reproduces (H_before, H_after, B_forbidden) with zero unjustified elimination, and Γ_E KILL does not imply
Γ_I ADMIT." NOT a proof of the underlying scientific claim.
"""
from dataclasses import replace
from helen_os.kernel.governed_epoch_v0 import (
    GovernedEpoch, build_ar_epoch, gamma_E, gamma_I, replay, contraction_count, run_one_epoch,
)


def test_witnessed_contraction():
    g = build_ar_epoch()
    r = gamma_E(g)
    assert r["verdict"] == "CONTRACT"
    assert r["contraction_count"] == 1 and r["eliminated"] == ["H_L1"]   # 'L1 load-bearing' eliminated
    assert "H_L2" in r["H_after"] and "H_L3" in r["H_after"]             # L2/L3 stay live (they survived)


def test_gamma_E_kill_does_not_imply_gamma_I_admit():
    g = build_ar_epoch()
    assert gamma_E(g)["verdict"] == "CONTRACT"
    gi = gamma_I(g)
    assert gi["verdict"] == "NO_ADMISSION" and gi["authority_gain"] == 0 and gi["ledger_effect"] == "none"


def test_replay_reproduces_contraction_zero_unjustified():
    g = build_ar_epoch()
    rp = replay(g)
    assert rp["replay_valid"] is True
    assert rp["unjustified_eliminations"] == []
    assert rp["H_before"] == sorted(g.hypotheses_before)
    assert rp["H_after"] == sorted(g.hypotheses_after)
    assert rp["B_forbidden"]                                             # boundary present


def test_unjustified_elimination_rejected():
    g = build_ar_epoch()
    # drop H_L2 (which SURVIVES, not KILLED) from H_after → unjustified contraction
    bad = replace(g, hypotheses_after=g.hypotheses_after - {"H_L2"})
    assert gamma_E(bad)["verdict"] == "REJECT_RECEIPT"
    assert replay(bad)["replay_valid"] is False


def test_no_contraction_is_HOLD_not_failure():
    g = build_ar_epoch()
    # H_after == H_before ⇒ nothing eliminated ⇒ HOLD (discriminator_insufficient)
    none = replace(g, hypotheses_after=g.hypotheses_before)
    r = gamma_E(none)
    assert r["verdict"] == "HOLD" and r["reason"] == "discriminator_insufficient"


def test_H_before_must_match_prereg():
    g = build_ar_epoch()
    bad = replace(g, hypotheses_before=g.hypotheses_before - {"H_L7"})
    assert gamma_E(bad)["verdict"] == "REJECT_RECEIPT"


def test_run_one_epoch_gate_separation_holds():
    out = run_one_epoch()
    assert out["gate_separation_holds"] is True
    assert out["authority"] is False
