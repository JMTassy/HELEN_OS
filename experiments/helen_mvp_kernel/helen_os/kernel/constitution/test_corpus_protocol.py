"""Corpus protocol, falsified: freeze precedes extraction;
unregistered corpora do not open; a stale freeze forces
re-registration; only a candidate new invariant is chiddush; unknown
value flags refuse rather than count; the QC crosswalk carries the
five rows and the decision/estimation split.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import corpus_protocol as cp
from corpus_protocol import (
    classify_finding,
    freeze,
    open_corpus,
    preregister,
    qc_thread,
    value_of,
)


# ── freeze and preregistration ─────────────────────────────────────────

def test_the_freeze_hashes_calculus_and_metrology_vector():
    f = freeze()
    assert f["C_0"] == ("PROOF", "SCOPE", "AUTHORITY", "REPLAY")
    assert f["M_0"] == ("alpha", "beta", "rho", "R", "chi")
    assert len(f["frozen_hash"]) == 16
    assert freeze()["frozen_hash"] == f["frozen_hash"]  # stable


def test_preregistration_binds_corpus_to_the_frozen_version():
    r = preregister("QUALITY_CONTROL",
                    ("OC curve maps to discrimination curve",
                     "consumer/producer risk maps to alpha/beta"))
    assert r["registered"] is True
    assert r["against"] == freeze()["frozen_hash"]


def test_an_unknown_corpus_cannot_be_registered():
    r = preregister("VIBES_ARCHIVE", ("anything",))
    assert r["registered"] is False
    assert r["reason"] == "E_UNKNOWN_CORPUS"


def test_an_empty_preregistration_is_not_a_preregistration():
    r = preregister("BOILER", ())
    assert r["registered"] is False
    assert r["reason"] == "E_EMPTY_PREREGISTRATION"


def test_an_unregistered_corpus_does_not_open():
    v = open_corpus("RAIL", {"registered": False})
    assert v["opened"] is False
    assert v["reason"] == "E_UNREGISTERED_CORPUS"


def test_a_registration_for_another_corpus_does_not_open_this_one():
    r = preregister("BOILER", ("safety valve = liveness dual",))
    v = open_corpus("RAIL", r)
    assert v["opened"] is False


def test_a_stale_freeze_forces_reregistration():
    r = dict(preregister("BOILER", ("x",)))
    r["against"] = "0000000000000000"
    v = open_corpus("BOILER", r)
    assert v["opened"] is False
    assert v["reason"] == "E_STALE_FREEZE"


def test_a_registered_corpus_opens_in_adversarial_mode():
    r = preregister("QUALITY_CONTROL", ("alpha/beta mapping",))
    v = open_corpus("QUALITY_CONTROL", r)
    assert v["opened"] is True
    assert v["mode"] == ("historical adversarial testing of a frozen "
                         "governance calculus")


# ── classification: only category 3 is chiddush ────────────────────────

def test_only_a_candidate_new_invariant_is_chiddush():
    for cls in ("ALREADY_REPRESENTABLE", "NEW_PARAMETERIZATION",
                "NOT_RELEVANT"):
        assert classify_finding("f", cls)[
            "is_constitutional_chiddush"] is False
    assert classify_finding("f", "CANDIDATE_NEW_INVARIANT")[
        "is_constitutional_chiddush"] is True


def test_an_unknown_class_is_refused():
    v = classify_finding("f", "INTERESTING")
    assert v["classified"] is False
    assert v["reason"] == "E_UNKNOWN_FINDING_CLASS"


# ── the value criterion ─────────────────────────────────────────────────

def test_value_positive_on_any_of_the_four_grounds():
    v = value_of("stack-up", reveals_non_closure_under_composition=True)
    assert v["value_positive"] is True
    assert v["destination"] == "architecture"


def test_no_grounds_means_the_history_notebook():
    v = value_of("nice anecdote")
    assert v["value_positive"] is False
    assert v["destination"] == "history_notebook"


def test_an_unknown_value_flag_is_refused_not_counted():
    v = value_of("f", is_really_cool=True)
    assert v["value_positive"] is None
    assert v["reason"] == "E_UNKNOWN_VALUE_FLAG"


# ── the QC thread ───────────────────────────────────────────────────────

def test_quality_control_follows_hamilton():
    t = qc_thread()
    assert t["order"][0] == "HAMILTON"
    assert t["next_after_hamilton"] == "QUALITY_CONTROL"
    assert len(t["order"]) == 9


def test_the_crosswalk_and_the_decision_estimation_split():
    t = qc_thread()
    assert t["crosswalk"]["consumer_risk"] == "alpha (false admission)"
    assert t["crosswalk"]["producer_risk"] == "beta (false rejection)"
    assert len(t["crosswalk"]) == 5
    assert "admission decision != world-model estimation" in t["law"]


def test_deterministic():
    assert cp.canon(freeze()) == cp.canon(freeze())
    assert cp.canon(qc_thread()) == cp.canon(qc_thread())
