"""GOVERNED_EPOCH_V0_KILL_SUITE — the 7 mutants that must die + precision/recall. 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "no hypothesis dies without its own valid witness; a witness for one hypothesis
cannot kill another; observation tampering, unwitnessed elimination, and Γ_E→Γ_I leakage are rejected; and a
lazy always-HOLD is penalised by recall." NOT a proof of any scientific claim.
"""
from dataclasses import replace
from helen_os.kernel.governed_epoch_kill_suite import (
    WitnessedEpoch, KillWitness, gamma_E_strict, gamma_I, scores, replay, base_epoch,
    obs_hash, AR_OBS, H_ALL,
)


def test_valid_witnessed_kill_contracts():
    g = gamma_E_strict(base_epoch())
    assert g["verdict"] == "CONTRACT" and g["licensed_kills"] == ["H_L1"]
    assert "H_L1" not in g["H_after"]


def test_elimination_without_witness_rejected():
    # claim H_L2 dead but provide no witness for it
    bad = replace(base_epoch(), claimed_H_after=H_ALL - {"H_L1", "H_L2"})
    g = gamma_E_strict(bad)
    assert g["verdict"] == "REJECT" and any("ELIMINATION_WITHOUT_WITNESS" in r for r in g["reasons"])


def test_witness_for_H1_cannot_kill_H2():
    # a witness aimed at H_L2 but reading H_L1's observation key
    ep = replace(base_epoch(), kill_witnesses=(KillWitness("H_L2", "minus_L1"),),
                 claimed_H_after=H_ALL - {"H_L2"})
    g = gamma_E_strict(ep)
    assert g["verdict"] == "REJECT" and any("WITNESS_TARGET_MISMATCH" in r for r in g["reasons"])


def test_kill_of_non_refuted_hypothesis_rejected():
    # H_L2's own key, but the observation does NOT refute it (removing L2 dropped Q)
    ep = replace(base_epoch(), kill_witnesses=(KillWitness("H_L2", "minus_L2"),),
                 claimed_H_after=H_ALL - {"H_L2"})
    g = gamma_E_strict(ep)
    assert g["verdict"] == "REJECT" and any("TARGET_NOT_REFUTED" in r for r in g["reasons"])


def test_observation_modified_after_prereg_rejected():
    tampered = {**AR_OBS, "minus_L2": 0.99}                 # change obs but keep old prereg hash
    ep = replace(base_epoch(), observation=tampered)        # prereg_observation_hash still = hash(AR_OBS)
    g = gamma_E_strict(ep)
    assert g["verdict"] == "REJECT" and any("OBSERVATION_MODIFIED_AFTER_PREREG" in r for r in g["reasons"])


def test_gamma_E_kill_does_not_imply_gamma_I_admit():
    ep = base_epoch()
    assert gamma_E_strict(ep)["verdict"] == "CONTRACT"
    gi = gamma_I(ep)
    assert gi["verdict"] == "NO_ADMISSION" and gi["authority_gain"] == 0


def test_observation_compatible_with_both_holds():
    # an observation where nothing is refuted (all removals dropped Q) ⇒ no kill ⇒ HOLD
    obs = {"K7": 0.60, "minus_L1": 0.50, "minus_L2": 0.50}
    ep = WitnessedEpoch(frozenset({"H_L1", "H_L2"}), obs, obs_hash(obs), (), frozenset({"H_L1", "H_L2"}), ())
    assert gamma_E_strict(ep)["verdict"] == "HOLD"


def test_replay_determinism_same_after_and_forbidden():
    ep = base_epoch()
    assert replay(ep) == replay(ep)


def test_precision_recall_perfect_on_base():
    s = scores(base_epoch())
    assert s["precision_kill"] == 1.0 and s["recall_kill"] == 1.0 and s["false_kill_rate"] == 0.0


def test_lazy_always_hold_has_low_recall():
    # never kill anything, though H_L1 is genuinely refuted ⇒ recall penalised (HOLD is not free)
    lazy = replace(base_epoch(), kill_witnesses=(), claimed_H_after=H_ALL)
    assert gamma_E_strict(lazy)["verdict"] == "HOLD"
    s = scores(lazy)
    assert s["recall_kill"] == 0.0 and s["licensed_available"] == ["H_L1"]


def test_false_kill_penalised():
    # kill H_L2 with its own key but it's not refuted → invalid witness, and false_kill_rate = 1
    ep = replace(base_epoch(), kill_witnesses=(KillWitness("H_L2", "minus_L2"),),
                 claimed_H_after=H_ALL - {"H_L2"})
    s = scores(ep)
    assert s["false_kill_rate"] == 1.0 and s["valid_contraction"] == 0
