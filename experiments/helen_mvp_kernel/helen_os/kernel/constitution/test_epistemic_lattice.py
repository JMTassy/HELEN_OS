"""The four-state lattice, falsified: inclusions checked on estimates
with the caveat stated; all five illegal absence inferences refuse by
name; absence is a research signal naming its candidate causes; shared
generator is provenance, never similarity; the analogy boundary holds.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import epistemic_lattice as el
from epistemic_lattice import (
    absence_signal,
    analogy_boundary,
    infer,
    instantiate,
    lattice_holds,
    shared_generator,
    similarity_claim,
)


def test_the_chain_holds_on_consistent_estimates():
    v = lattice_holds({"GENERABLE": {"a", "b", "c", "d"},
                       "PRODUCED": {"a", "b", "c"},
                       "SURVIVED": {"a", "b"},
                       "OBSERVED": {"a"}})
    assert v["holds_on_estimates"] is True
    assert "incomplete estimates" in v["caveat"]


def test_an_estimate_violation_is_named_not_absorbed():
    v = lattice_holds({"GENERABLE": {"a"}, "PRODUCED": {"a", "z"},
                       "SURVIVED": {"a"}, "OBSERVED": {"a"}})
    assert v["holds_on_estimates"] is False
    assert v["violations"] == ["PRODUCED not within GENERABLE"]


def test_all_five_illegal_inferences_refuse_by_name():
    for premise, conclusion in el.ILLEGAL_INFERENCES:
        v = infer(premise, conclusion)
        assert v["licensed"] is False
        assert v["reason"] == "E_ILLEGAL_ABSENCE_INFERENCE"
    assert len(el.ILLEGAL_INFERENCES) == 5


def test_an_unnamed_inference_is_left_to_its_own_evidence():
    v = infer("observed", "survived")     # downstream->upstream, fine
    assert v["licensed"] is None


def test_absence_is_a_research_signal_with_named_causes():
    v = absence_signal("open_tint_motif", "OBSERVED")
    assert v["verdict"] == "RESEARCH_SIGNAL"
    assert v["is_evidence_of_rejection"] is False
    assert "survival_bias" in v["candidate_causes"]
    assert "cultural_rejection" in v["candidate_causes"]  # one of many


def test_an_unknown_level_is_refused():
    with pytest.raises(ValueError, match="E_UNKNOWN_LATTICE_LEVEL"):
        absence_signal("x", "IMAGINED")


def test_shared_generator_is_provenance_not_similarity():
    g1 = instantiate("G_border_12", {"scale": 2})
    g2 = instantiate("G_border_12", {"scale": 3})
    g3 = instantiate("G_border_99", {"scale": 2})
    same = shared_generator(g1, g2)
    diff = shared_generator(g1, g3)
    assert same["shared_generator"] is True
    assert same["identical_tokens"] is False     # lineage, not token
    assert diff["shared_generator"] is False
    assert same["basis"] == "PROVENANCE"


def test_visual_similarity_establishes_nothing():
    v = similarity_claim(True)
    assert v["shared_generator_established"] is False
    assert v["reason"] == "E_GLYPH_TRAP"


def test_the_analogy_boundary_stays_hard():
    v = analogy_boundary()
    assert v["is_evidence_of_anticipation"] is False
    assert "convergence is not proof" in v["law"]


def test_the_selection_operators_are_all_named():
    assert set(el.SELECTION_OPERATORS) == {"C_t", "S_t", "D_t", "A_t"}


def test_deterministic():
    assert el.canon(absence_signal("x", "SURVIVED")) == \
        el.canon(absence_signal("x", "SURVIVED"))
