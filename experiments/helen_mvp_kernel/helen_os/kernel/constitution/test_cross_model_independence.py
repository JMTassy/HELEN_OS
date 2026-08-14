"""CROSS_MODEL_INDEPENDENCE_V0 falsified: the three axes never
collapse; prose without a discriminator is not useful; mixed decoding
regimes are refused; preserve_thinking at baseline is carryover; an
unprobed model never enters the research graph; and no branch of the
promotion gate grants authority.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import cross_model_independence as cmi
from cross_model_independence import (
    baseline_config,
    collapse_to_neff,
    decoding_regime,
    delta_q_useful,
    first_witness,
    independence_axes,
    promotion_gate,
    useful,
    vendor_claim,
)


# ── the three axes ─────────────────────────────────────────────────────

def test_two_proposers_over_one_corpus_is_one_witness():
    v = independence_axes(2, 2, 1)
    assert v["independent_proposers"] is True
    assert v["independent_witnesses"] is False


def test_collapsing_the_axes_is_refused_by_name():
    v = collapse_to_neff(independence_axes(2, 2, 1))
    assert v["collapsed"] is False
    assert v["reason"] == "E_COLLAPSED_AXES"


def test_negative_counts_are_refused():
    with pytest.raises(ValueError, match="E_NEGATIVE_COUNT"):
        independence_axes(-1, 0, 0)


# ── usefulness ─────────────────────────────────────────────────────────

def test_novel_but_unfalsifiable_is_not_useful():
    v = useful(novel=True, falsifiable=False, discriminable=True,
               x_star="probe:1")
    assert v["useful"] is False
    assert v["missing"] == ("falsifiable",)


def test_surviving_without_a_discriminator_is_admiration():
    v = useful(True, True, True, x_star=None)
    assert v["useful"] is False
    assert v["reason"] == "E_NO_DISCRIMINATOR"


def test_the_full_conjunction_with_x_star_is_useful():
    assert useful(True, True, True, "grep:border_4")["useful"] is True


def test_magnificent_prose_inside_the_gemma_union_buys_nothing():
    v = delta_q_useful(frozenset({"a", "b"}),
                       frozenset({"a", "b", "c"}))
    assert v["delta_Q_useful_Q_given_G"] == 0
    assert v["verdict"] == "NO_COVERAGE_BOUGHT"


def test_a_marginal_class_is_coverage_bought_and_named():
    v = delta_q_useful(frozenset({"a", "d"}), frozenset({"a", "b"}))
    assert v["delta_Q_useful_Q_given_G"] == 1
    assert v["marginal_classes"] == ("d",)
    assert v["verdict"] == "COVERAGE_BOUGHT"
    assert v["jaccard"] == round(1 / 3, 6)


# ── decoding regimes ───────────────────────────────────────────────────

GEMMA = {"temperature": 0.7, "top_p": 0.9}
QWEN_NATIVE = {"temperature": 0.7, "top_p": 0.80,
               "presence_penalty": 1.5}


def test_e1_requires_identical_parameters():
    assert decoding_regime(GEMMA, dict(GEMMA), "E1_controlled")["ok"] \
        is True
    v = decoding_regime(GEMMA, QWEN_NATIVE, "E1_controlled")
    assert v["ok"] is False
    assert v["reason"] == "E_MIXED_DECODING_REGIMES"


def test_e2_requires_native_parameters_to_actually_differ():
    assert decoding_regime(GEMMA, QWEN_NATIVE, "E2_native")["ok"] \
        is True
    v = decoding_regime(GEMMA, dict(GEMMA), "E2_native")
    assert v["reason"] == "E_MIXED_DECODING_REGIMES"


def test_an_undeclared_regime_is_refused():
    assert decoding_regime(GEMMA, GEMMA, "vibes")["reason"] == \
        "E_UNKNOWN_REGIME"


# ── baseline hygiene ───────────────────────────────────────────────────

def test_the_lawful_baseline_is_one_intervention():
    assert baseline_config(think=False, preserve_thinking=False,
                           context_matched_to_gemma=True)["ok"] is True


def test_each_confound_is_refused_by_name():
    v = baseline_config(think=True, preserve_thinking=True,
                        context_matched_to_gemma=False)
    assert v["ok"] is False
    assert set(v["refusals"]) == {"E_THINKING_AT_BASELINE",
                                  "E_HIDDEN_STATE_CARRYOVER",
                                  "E_CONFOUNDED_CONTEXT"}


# ── the boring first witness ───────────────────────────────────────────

def test_an_unprobed_model_never_enters_the_research_graph():
    v = first_witness({"model_loaded": True, "parse_yield_1": False})
    assert v["enters_research_graph"] is False
    assert v["reason"] == "E_UNPROBED_MODEL"
    assert "execution_yield_1" in v["missing"]


def test_all_five_boring_witnesses_open_the_door():
    v = first_witness({k: True for k in cmi.FIRST_WITNESS})
    assert v["enters_research_graph"] is True


# ── vendor claims and promotion ────────────────────────────────────────

def test_model_card_figures_are_reported_external():
    v = vendor_claim("17-19 GB at 4-bit")
    assert v["grade"] == "REPORTED_EXTERNAL"
    assert v["observed_local"] is False


def test_the_seat_needs_all_three_and_grants_no_authority():
    assert promotion_gate(2, True, True)["seat_earned"] is True
    assert promotion_gate(0, True, True)["reason"] == \
        "E_NO_MARGINAL_COVERAGE"
    assert promotion_gate(2, False, True)["reason"] == \
        "E_UNSTABLE_ACROSS_SEEDS"
    assert promotion_gate(2, True, False)["reason"] == \
        "E_MARGINAL_COST_TOO_HIGH"


def test_no_branch_of_the_gate_grants_authority():
    for dq in (0, 5):
        for stable in (True, False):
            for cost in (True, False):
                assert promotion_gate(dq, stable, cost)[
                    "authority_delta"] == 0


def test_the_frozen_tree_names_the_later_ablations():
    assert "vision" in cmi.ABLATIONS_LATER
    assert "preserve_thinking" in cmi.ABLATIONS_LATER
    assert len(cmi.ARMS) == 4


def test_deterministic():
    assert cmi.canon(delta_q_useful(frozenset({"a"}),
                                    frozenset({"b"}))) == \
        cmi.canon(delta_q_useful(frozenset({"a"}), frozenset({"b"})))
