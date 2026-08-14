"""HELEN_LAYERED_FRONTIER_V0 falsified: an unlicensed delta is
refused; missing NON_DELTAS are refused; pressure without witnesses
moves the epistemic frontier by zero; no layer mints the next layer's
resource; and flat yield at tripled cost is measured as useless.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import layered_frontier as lf
from layered_frontier import (
    cross_advance,
    elasticity,
    epistemic_pressure,
    mint,
    pressure_conservation,
    transition,
)


# ── the transition object ──────────────────────────────────────────────

def _qwen_download():
    """The incident as a lawful receipt: F_S moves, four NON_DELTAS."""
    return transition(
        layer="substrate", before="STALLED", after="COMPLETE",
        deltas={"F_S": 1},
        licenses={"F_S": "byte_growth_resumed_after_do(Xet=OFF)"},
        non_deltas={"F_I": "unknown", "F_C": "none",
                    "F_E": "unchanged", "F_X": "unchanged"},
        rederivation="stat artifact at t1/t2; compare byte counts")


def test_the_qwen_receipt_answers_the_four_questions():
    v = _qwen_download()
    assert v["ok"] is True
    assert v["four_questions_answered"] is True
    assert set(v["non_deltas"]) == {"F_I", "F_C", "F_E", "F_X"}


def test_an_unlicensed_delta_is_refused():
    v = transition("substrate", "a", "b", {"F_S": 1}, {},
                   {f: "0" for f in lf.FRONTIERS if f != "F_S"},
                   "recipe")
    assert v["ok"] is False
    assert v["reason"] == "E_UNLICENSED_TRANSITION"
    assert v["unlicensed"] == ("F_S",)


def test_missing_non_deltas_are_refused():
    """The mandatory block: unrecorded implications are the leak."""
    v = transition("substrate", "a", "b", {"F_S": 1},
                   {"F_S": "l"}, {}, "recipe")
    assert v["ok"] is False
    assert v["reason"] == "E_MISSING_NON_DELTAS"
    assert set(v["missing"]) == {"F_I", "F_C", "F_E", "F_X"}


def test_a_transition_without_a_rederivation_path_is_not_a_receipt():
    v = transition("substrate", "a", "b", {"F_S": 1}, {"F_S": "l"},
                   {f: "0" for f in lf.FRONTIERS if f != "F_S"},
                   rederivation=None)
    assert v["reason"] == "E_NO_REDERIVATION_PATH"


def test_an_unknown_frontier_is_refused():
    assert transition("x", "a", "b", {"F_Z": 1}, {}, {}, "r")[
        "reason"] == "E_UNKNOWN_FRONTIER"


def test_downloaded_does_not_entail_loadable():
    v = cross_advance("F_S", "F_I", licensed=False)
    assert v["advanced"] is False
    assert v["reason"] == "E_UNLICENSED_COUPLING"
    assert cross_advance("F_S", "F_I", True)["advanced"] is True


# ── epistemic pressure ─────────────────────────────────────────────────

def test_one_root_fanned_a_hundred_ways_is_pressure_not_evidence():
    v = epistemic_pressure(n_representations=100,
                           n_independent_roots=1)
    assert v["Pi_C"] == 100.0
    assert v["is_confidence"] is False


def test_pressure_without_witnesses_moves_nothing():
    v = pressure_conservation(delta_pi=99.0, delta_w=0,
                              delta_d_valid=0)
    assert v["delta_F_E"] == 0
    assert v["reason"] == "E_PRESSURE_IS_NOT_EVIDENCE"


def test_a_new_witness_reopens_the_ordinary_door():
    v = pressure_conservation(99.0, delta_w=1, delta_d_valid=0)
    assert v["delta_F_E"] == "licensable"


def test_negative_counts_are_refused():
    with pytest.raises(ValueError, match="E_NEGATIVE_COUNT"):
        epistemic_pressure(-1, 0)


# ── conservation of minting rights ─────────────────────────────────────

def test_representation_may_not_mint_a_warrant():
    v = mint("representation", "empirical_warrant")
    assert v["minted"] is False
    assert v["reason"] == "E_MINTING_RIGHTS_VIOLATION"
    assert v["owns"] == "representation"


def test_each_layer_mints_exactly_what_it_owns():
    for layer, resource in lf.MINTING_RIGHTS.items():
        assert mint(layer, resource)["minted"] is True
    assert mint("cognition", "institutional_admission")["minted"] \
        is False
    assert mint("receipt", "world_mutation")["minted"] is False
    assert mint("vibes", "anything")["reason"] == "E_UNKNOWN_LAYER"


# ── cognitive elasticity ───────────────────────────────────────────────

def test_flat_yield_at_tripled_cost_is_economically_useless():
    v = elasticity(q1=10, q2=10, c1=1.0, c2=3.0)
    assert v["MCY"] == 0.0
    assert v["economically_useless"] is True


def test_positive_marginal_yield_is_measured_not_presumed():
    v = elasticity(q1=10, q2=15, c1=1.0, c2=2.0)
    assert v["eps_C"] == 0.5
    assert v["MCY"] == 5.0
    assert v["economically_useless"] is False


def test_a_zero_baseline_is_refused():
    with pytest.raises(ValueError, match="E_BAD_BASELINE"):
        elasticity(0, 1, 1, 2)


def test_deterministic():
    assert lf.canon(_qwen_download()) == lf.canon(_qwen_download())
