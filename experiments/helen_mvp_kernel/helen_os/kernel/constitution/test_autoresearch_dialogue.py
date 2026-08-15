"""Ten epochs of adversarial dialogue produce zero witnesses; a turn
that claims a warrant, authority or effect is refused; agreement is
not evidence; an unidentifiable hypothesis HOLDs however well
predicted; when the next hypothesis sits in the same observational
class the licensed move is ACQUIRE not THINK; and predictive support
never becomes a causal mechanism.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import autoresearch_dialogue as ad
from autoresearch_dialogue import (
    agreement_claim,
    causal_promotion,
    dialogue_turn,
    dialogue_warrant,
    discriminator,
    observational_class,
    run_protocol,
    stopping_criterion,
)

ZERO = {a: 0 for a in ad.DELTA_AXES}


# ── the typed exchange ─────────────────────────────────────────────────

def test_dialogue_moves_representation_and_candidates_only():
    ok = dialogue_turn("CHAOS", "PROPOSE", {**ZERO, "R": 1, "C": 1})
    assert ok["ok"] is True
    for axis, reason in (("W", "E_DIALOGUE_MINTS_WARRANT"),
                         ("A", "E_DIALOGUE_MINTS_AUTHORITY"),
                         ("X", "E_DIALOGUE_MINTS_EFFECT")):
        v = dialogue_turn("CHAOS", "PROPOSE", {**ZERO, axis: 1})
        assert v["reason"] == reason


def test_roles_have_disjoint_act_alphabets():
    assert dialogue_turn("CHAOS", "BLOCK", ZERO)["reason"] == \
        "E_ACT_OUTSIDE_ROLE"
    assert dialogue_turn("MASON", "PROPOSE", ZERO)["reason"] == \
        "E_ACT_OUTSIDE_ROLE"
    assert dialogue_turn("MASON", "HOLD", ZERO)["ok"] is True


def test_an_untyped_delta_is_refused():
    v = dialogue_turn("CHAOS", "PROPOSE", {"R": 1})
    assert v["reason"] == "E_UNTYPED_DELTA"


def test_ten_turns_are_not_ten_witnesses():
    v = dialogue_warrant(n_turns=10, n_acquisitions=0)
    assert v["N_dialogue"] == 10 and v["N_epi"] == 0
    assert v["delta_W_external"] == 0
    assert v["dialogue_only"] is True
    real = dialogue_warrant(30, 3)
    assert real["N_epi"] == 3 and real["delta_W_external"] == 3


def test_agreement_is_not_a_witness():
    assert agreement_claim(True, claims_truth=True)["reason"] == \
        "E_AGREEMENT_AS_WITNESS"
    assert agreement_claim(True, claims_truth=False)["ok"] is True


# ── identifiability and stopping ───────────────────────────────────────

def test_an_indistinguishable_rival_holds_identifiability():
    v = observational_class({"K3": (0.01, 0.02)}, epsilon=0.05)
    assert v["class_size"] == 2
    assert v["identifiable_in_H"] is False
    assert v["reason"] == "E_UNIDENTIFIABLE_IN_H"
    alone = observational_class({"K3": (0.9,)}, epsilon=0.05)
    assert alone["identifiable_in_H"] is True


def test_same_class_means_acquire_not_think():
    v = stopping_criterion(next_equivalent_to_current=True,
                           discriminator_available=True)
    assert v["continue_dialogue"] is False
    assert v["next_operation"] == "ACQUIRE_X_STAR"
    seek = stopping_criterion(True, discriminator_available=False)
    assert seek["next_operation"] == "SEEK_DISCRIMINATOR"
    assert stopping_criterion(False, True)["continue_dialogue"] is True


def test_a_non_discriminating_experiment_is_invalid():
    assert discriminator("A", "A", 1.0, 0.0)["reason"] == \
        "E_NON_DISCRIMINATING"
    assert discriminator("A", "B", 1.0, 0.0)["valid"] is True


# ── the closing refusal ────────────────────────────────────────────────

def test_predictive_is_not_causal():
    v = causal_promotion(True, discharged=())
    assert v["status"] == "HOLD"
    assert v["reason"] == "E_PREDICTIVE_IS_NOT_CAUSAL"
    assert set(v["undischarged"]) == set(ad.CAUSAL_OBLIGATIONS)
    partial = causal_promotion(True, ("intervention",))
    assert partial["status"] == "HOLD"
    full = causal_promotion(True, ad.CAUSAL_OBLIGATIONS)
    assert full["promoted"] is True


# ── the executed protocol ──────────────────────────────────────────────

def test_the_ten_epoch_run_moves_C_W_F_but_never_A_or_X():
    r = run_protocol()
    assert r["all_turns_typed"] is True
    d = r["final_delta"]
    assert d["C"] > 0 and d["W"] > 0 and d["F"] > 0
    assert d["A"] == 0 and d["X"] == 0
    assert r["AUTHORITY"] == 0 and r["EFFECT"] == 0


def test_twenty_transforms_of_one_warrant_stay_one_root():
    r = run_protocol()
    assert r["N_repr_of_c1"] == 21
    assert r["N_epi_of_c1"] == 1


def test_warrants_came_from_acquisition_not_from_turns():
    r = run_protocol()
    assert len(r["warrants"]) == 3
    assert len(r["independent_roots"]) == 3
    # far more turns than warrants: dialogue did not inflate evidence
    assert r["turns"] > len(r["warrants"]) * 5


def test_the_final_frontier_closes_on_causal_hold():
    r = run_protocol()
    f = r["final_frontier"]
    assert f["EXECUTABLE"] == "PASS"
    assert f["PREDICTIVE"] == "PASS"
    assert f["MATCHED_CONTROL"] == "PASS"
    assert f["REPLICATED"] == "PASS"
    assert f["IDENTIFIABLE_IN_H"] == "PASS"
    assert f["CAUSAL"] == "HOLD"
    assert r["causal"] == "HOLD"


def test_deterministic():
    assert ad.canon(run_protocol()) == ad.canon(run_protocol())
