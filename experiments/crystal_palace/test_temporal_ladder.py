"""Falsifiers for the Temporal Chiddush Ladder — the backtest state
machine, the seat law (this seat is disqualified, and the instrument
says so), the generality control, and the absence law on deltas.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import temporal_ladder as tl
from crystal_palace import UNREACHABLE
from temporal_ladder import (
    Backtest,
    freeze_predictions,
    generality_check,
    motif_delta,
    open_holdout,
    score,
    this_seat_attestation,
)

BT = Backtest("repertory-vs-1851", "repertory_patents_le1850",
              "crystal_palace_1851")
PREDICTIONS = ("conditional_automation", "parallel_execution",
               "steam_hammer_motif")
WITNESSED = ("conditional_automation", "parallel_execution",
             "sensor_to_record", "source_channel_code")

FRESH_SEAT = {"seat": "fresh-seat-A", "holdout_accessed": False}


# ── the ladder itself ───────────────────────────────────────────────────

def test_six_rungs_ordered_by_year_all_dark_from_this_seat():
    years = [c["year"] for c in tl.LADDER]
    assert years == sorted(years) and len(tl.LADDER) == 6
    assert all(c["availability"] == UNREACHABLE for c in tl.LADDER)


def test_run_order_starts_with_the_repertory_backtest():
    assert tl.RUN_ORDER[0] == "repertory_patents_le1850"
    assert tl.RUN_ORDER[1] == "crystal_palace_1851"      # the holdout
    assert tl.RUN_ORDER[2] == "encyclopedie_1772"        # the control


# ── the seat law: this instrument disqualifies its own builder ─────────

def test_this_seat_attests_holdout_access_truthfully():
    a = this_seat_attestation()
    assert a["holdout_accessed"] is True
    assert "batches 1-2" in a["basis"]


def test_a_freeze_from_this_seat_is_marked_and_scoring_refuses_it():
    fr = freeze_predictions(BT, PREDICTIONS, this_seat_attestation())
    assert fr["seat_contaminated"] is True        # recorded, not hidden
    opened = open_holdout(fr)
    r = score(fr, opened, PREDICTIONS, WITNESSED)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_SEAT_CONTAMINATED"
    assert "disqualified" in r["law"]


def test_undeclared_attestation_defaults_to_contaminated():
    """Silence about holdout access is not innocence."""
    fr = freeze_predictions(BT, PREDICTIONS, {"seat": "mystery"})
    assert fr["seat_contaminated"] is True


# ── the state machine: one legal order ─────────────────────────────────

def test_holdout_refuses_to_open_before_a_freeze():
    assert open_holdout(None)["reason"] == "E_TARGET_BEFORE_FREEZE"
    assert open_holdout({"state": "nope"})["reason"] == \
        "E_TARGET_BEFORE_FREEZE"


def test_empty_prediction_set_cannot_freeze():
    assert freeze_predictions(BT, (), FRESH_SEAT)["reason"] == \
        "E_EMPTY_PREDICTION_SET"


def test_swapped_predictions_are_caught_by_the_hash():
    fr = freeze_predictions(BT, PREDICTIONS, FRESH_SEAT)
    opened = open_holdout(fr)
    doctored = PREDICTIONS + ("sensor_to_record",)   # added post-hoc
    r = score(fr, opened, doctored, WITNESSED)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_PREDICTIONS_SWAPPED"


def test_clean_path_scores_with_denominators_shown():
    fr = freeze_predictions(BT, PREDICTIONS, FRESH_SEAT)
    opened = open_holdout(fr)
    r = score(fr, opened, PREDICTIONS, WITNESSED)
    assert r["verdict"] == "SCORED"
    assert r["precision"] == 2 / 3                   # 2 hits of 3 predicted
    assert r["recall"] == 2 / 4                      # 2 of 4 witnessed
    assert r["predicted"] == 3 and r["witnessed"] == 4


# ── the negative control ────────────────────────────────────────────────

def test_deep_time_matching_near_time_indicts_the_grammar():
    r = generality_check(r_deep=0.8, r_near=0.85)
    assert r["verdict"] == "E_GRAMMAR_TOO_GENERIC"


def test_near_time_dominating_deep_time_is_the_local_signal():
    r = generality_check(r_deep=0.3, r_near=0.75)
    assert r["verdict"] == "HISTORICALLY_LOCAL_SIGNAL"
    assert abs(r["gap"] - 0.45) < 1e-9


def test_weak_both_ways_is_inconclusive_not_a_win():
    assert generality_check(0.2, 0.3)["verdict"] == "METHOD_INCONCLUSIVE"


# ── the absence law on deltas ──────────────────────────────────────────

def test_motif_delta_never_declares_extinction():
    d = motif_delta(frozenset({"a", "b"}), frozenset({"b", "c"}))
    assert d["new_in_later"] == ["c"]
    assert d["retained"] == ["b"]
    assert d["not_witnessed_later"] == ["a"]
    assert "removed" not in d and "extinct" not in str(d.keys())
    assert "sample, not a census" in d["law"]


# ── determinism ─────────────────────────────────────────────────────────

def test_freeze_and_score_are_deterministic():
    import crystal_palace as cp
    a = cp.canon(freeze_predictions(BT, PREDICTIONS, FRESH_SEAT))
    b = cp.canon(freeze_predictions(BT, PREDICTIONS, FRESH_SEAT))
    assert a == b
