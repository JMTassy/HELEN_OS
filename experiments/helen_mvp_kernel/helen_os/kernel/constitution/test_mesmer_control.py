"""The negative control, falsified: the frozen gate refuses the 1826
causal conclusion on the PROOF ceiling; La Place's consensus collapses
to one mechanism class; the 1784 blinding attributes to expectation;
the self-verifying patient counts for nothing; recorded defeaters
block the conclusion; and the one chiddush stays a CANDIDATE, not law.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import corpus_protocol as cp
import mesmer_control as mc
from mesmer_control import (
    admit_conclusion_with_defeaters,
    commission_1784_cases,
    commission_1826_claim,
    corpus_value,
    design_grade_candidate,
    dissociation_test,
    findings_table,
    la_place_witnesses,
    mechanism_common_mode,
    negative_control,
    registration,
    self_verifying_patient,
)


# ── the lawful door: operator-supplied corpus, preregistered ───────────

def test_the_corpus_registers_through_the_operator_channel():
    r = registration()
    assert r["registered"] is True
    assert r["corpus"] == "MESMERISM_1844"
    assert r["against"] == cp.freeze()["frozen_hash"]
    assert len(r["expected_lessons"]) == 5


def test_the_registered_corpus_opens_and_unknowns_still_refuse():
    assert cp.open_corpus("MESMERISM_1844", registration())["opened"] \
        is True
    assert cp.preregister("AKASHIC_SCROLLS", ("x",))["reason"] == \
        "E_UNKNOWN_CORPUS"


def test_the_source_bias_and_sequencing_caveat_are_recorded():
    assert "partisan" in mc.GRADE
    assert "Sequencing caveat" in mc.__doc__


# ── finding 1: PROOF-ceiling breach on the causal conclusion ───────────

def test_the_1826_causal_conclusion_is_refused_by_the_frozen_gate():
    v = commission_1826_claim()
    assert v["verdict"] == "REJECT"
    assert v["breached"] == ["PROOF"]
    assert v["over"] == ["causation_by_magnetism_alone"]


# ── finding 2: consensus is one mechanism class ────────────────────────

def test_la_place_witnesses_share_one_mechanism_class():
    v = la_place_witnesses()
    assert v["witness_count"] == 5
    assert v["ancestry_classes"] == 5      # distinct seances, cities
    assert v["mechanism_classes"] == 1     # one suggestible instrument
    assert v["residual_missed_by_ancestry_alone"] is True
    assert v["u_effective"] == 1.0         # sqrt-N NOT earned


def test_distinct_mechanisms_do_earn_the_reduction():
    ws = ({"id": "w1", "ancestors": frozenset({"s1"}),
           "instrument_class": "human"},
          {"id": "w2", "ancestors": frozenset({"s2"}),
           "instrument_class": "thermometer"},
          {"id": "w3", "ancestors": frozenset({"s3"}),
           "instrument_class": "balance_scale"})
    v = mechanism_common_mode(ws, 1.0)
    assert v["mechanism_classes"] == 3
    assert v["u_effective"] < 1.0
    assert v["residual_missed_by_ancestry_alone"] is False


# ── finding 3: the 1784 blinding ────────────────────────────────────────

def test_response_tracks_belief_not_treatment():
    v = dissociation_test(commission_1784_cases())
    assert v["tracks_belief"] == 4
    assert v["tracks_actual"] == 0
    assert v["attribution"] == "EXPECTATION"


def test_a_real_agent_would_be_attributed_to_the_agent():
    cases = ({"actual": True, "believed": False, "responded": True},
             {"actual": False, "believed": True, "responded": False})
    assert dissociation_test(cases)["attribution"] == "AGENT"


def test_no_cases_is_refused():
    with pytest.raises(ValueError, match="E_NO_CASES"):
        dissociation_test(())


# ── finding 4: the self-verifying patient ──────────────────────────────

def test_the_self_verifying_patient_counts_for_nothing():
    v = self_verifying_patient()
    assert v["reputation_refused"] == "E_SELF_DECLARED_REPUTATION"
    assert v["generate_entails_admit"] is False


# ── finding 5: recorded defeaters block the conclusion ─────────────────

def test_undischarged_defeaters_reject_the_conclusion():
    v = admit_conclusion_with_defeaters("clairvoyance is real",
                                        frozenset())
    assert v["verdict"] == "REJECT"
    assert v["reason"] == "E_UNDISCHARGED_DEFEATER"
    assert len(v["open_defeaters"]) == 5


def test_the_rotating_eyes_are_on_the_commissions_own_record():
    v = admit_conclusion_with_defeaters("clairvoyance is real",
                                        frozenset())
    assert any("rotation" in d for d in v["open_defeaters"])
    assert any("paper or parchment" in d for d in v["open_defeaters"])


def test_discharging_all_defeaters_still_caps_at_design_grade():
    v = admit_conclusion_with_defeaters(
        "x", frozenset(mc.DEFEATERS_ON_RECORD))
    assert v["verdict"] == "ADMIT_AT_GRADE"
    assert "design grade" in v["grade_note"]


# ── finding 6: the candidate stays a candidate ─────────────────────────

def test_observational_witnesses_do_not_sum_to_interventional():
    v = design_grade_candidate(1000)
    assert v["summed_grade"] == "OBSERVATIONAL"
    assert v["reaches_interventional"] is False
    assert "thousand seances" in v["law_if_earned"]


def test_the_chiddush_is_held_at_candidate_not_wired_into_law():
    v = design_grade_candidate(10)
    assert v["status"] == "CANDIDATE_NOT_LAW"
    assert "Garden must first demonstrate" in v["promotion_condition"]


# ── the findings table under the frozen protocol ───────────────────────

def test_every_finding_classifies_and_only_one_is_chiddush():
    table = findings_table()
    assert all(f["classified"] for f in table)
    chiddush = [f for f in table if f["is_constitutional_chiddush"]]
    assert len(chiddush) == 1
    assert chiddush[0]["finding"] == "evidence_design_grade"


def test_the_corpus_value_is_positive_on_the_frozen_criterion():
    v = corpus_value()
    assert v["value_positive"] is True
    assert "exposes_missing_metrology_variable" in v["grounds"]
    assert "changes_measurable_risk_bound" in v["grounds"]


# ── the negative-control verdict ────────────────────────────────────────

def test_the_frozen_gate_refuses_the_negative_control():
    v = negative_control()
    assert v["frozen_gate_rejects_central_claim"] is True
    assert len(v["independent_grounds"]) == 2
    assert v["attribution_1784"] == "EXPECTATION"


def test_the_corpus_own_discipline_is_credited_not_erased():
    v = negative_control()
    assert len(v["corpus_own_discipline"]) == 3
    assert any("Braid" in d for d in v["corpus_own_discipline"])
    assert "mislabeled" in v["what_was_real"]


def test_deterministic():
    assert mc.canon(negative_control()) == mc.canon(negative_control())
    assert mc.canon(la_place_witnesses()) == \
        mc.canon(la_place_witnesses())
