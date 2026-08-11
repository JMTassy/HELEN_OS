"""Falsifiers for the epistemic-layer harness: sigma is computed not
declared, roles are not roots, failures yield hypothesis-grade
constraint candidates, externalization keeps its counter-hypotheses
alive, and the 40-item packet receiver refuses malformed deliveries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import epistemic_layers as el
from epistemic_layers import (
    Accident,
    ExternalizationDepth,
    compute_sigma,
    constraint_externalization,
    externalization_trend,
    infer_missing_constraint,
    roles_and_roots,
    validate_packet,
    validate_packet_item,
)


# ── sigma: computed, contiguous above D, entry rung at P ───────────────

def test_claim_alone_is_claimed_and_demo_alone_is_demonstrated():
    assert compute_sigma(frozenset({"P"}))["sigma"] == "claimed"
    # harakeke law: demonstration does not require a prior patent claim
    r = compute_sigma(frozenset({"D"}))
    assert r["sigma"] == "demonstrated" and r["gap"] is False


def test_full_chain_reaches_the_top():
    r = compute_sigma(frozenset({"P", "D", "J", "F", "C"}))
    assert r["sigma"] == "institutionally_required" and not r["gap"]


def test_jury_witness_without_demonstration_is_a_stranded_gap():
    r = compute_sigma(frozenset({"P", "J"}))
    assert r["sigma"] == "claimed"
    assert r["gap"] and r["reason"] == "E_LAYER_GAP"
    assert r["stranded_witness"] == "J"
    # and a bare J with nothing beneath crosses nothing at all
    bare = compute_sigma(frozenset({"J"}))
    assert bare["sigma"] is None and bare["gap"]


def test_skipping_judgment_strands_the_survival_witness():
    r = compute_sigma(frozenset({"D", "F"}))
    assert r["sigma"] == "demonstrated"
    assert r["stranded_witness"] == "F"


# ── roles are not roots ─────────────────────────────────────────────────

def test_catalogue_and_jury_are_two_roles_one_root():
    ws = ({"role": "catalogue_description",
           "root": "great_exhibition_ecosystem"},
          {"role": "jury_evaluation",
           "root": "great_exhibition_ecosystem"})
    r = roles_and_roots(ws)
    assert r["independent_roles"] == 2
    assert r["independent_roots"] == 1
    assert r["evaluation_independence"] is True
    assert r["evidential_independence"] is False   # the whole point


def test_a_second_root_grants_evidential_independence():
    ws = ({"role": "catalogue_description", "root": "exhibition"},
          {"role": "accident_investigation", "root": "board_of_trade"})
    assert roles_and_roots(ws)["evidential_independence"] is True


# ── failure -> constraint candidates, hypothesis grade ─────────────────

ACC = Accident("BT-1864-007", state_before="train approaching junction",
               action="proceed on seen signal with delayed braking",
               bad_state="collision")


def test_failure_yields_both_repair_candidates_untyped():
    r = infer_missing_constraint(ACC)
    kinds = {c["kind"] for c in r["candidates"]}
    assert kinds == {"missing_guard", "missing_invariant"}
    assert r["grade"] == "HYPOTHESIS"
    assert "GATE != INVARIANT" in r["law"]


def test_externalization_mechanism_needs_a_next_generation_witness():
    p = constraint_externalization(ACC, "interlock: signal state binds "
                                        "points mechanically")
    assert p["verdict"] == "PROPOSED_CONSTRAINT"
    assert p["reason"] == "E_NEXT_GENERATION_UNWITNESSED"
    w = constraint_externalization(ACC, "interlock",
                                   next_gen_witness="1876 exhibit: "
                                   "interlocking frame")
    assert w["verdict"] == "EXTERNALIZATION_WITNESSED"


# ── externalization depth: measured, counter-hypotheses live ───────────

def test_depth_vectors_match_the_relay_examples():
    hand_tool = ExternalizationDepth(0, 0, 0, 0, 0)
    recorder = ExternalizationDepth(1, 1, 0, 0, 0)
    course = ExternalizationDepth(0, 0, 1, 0, 0)
    assert hand_tool.total() == 0
    assert recorder.vector() == (1, 1, 0, 0, 0)
    assert course.e_j == 1 and course.e_a == 0    # recommends, never acts


def test_trend_reports_the_sample_and_keeps_h0_h1_alive():
    series = ((1772, ExternalizationDepth(0, 0, 0, 0, 0)),
              (1851, ExternalizationDepth(1, 1, 0, 1, 1)))
    r = externalization_trend(series)
    assert r["verdict"] == "MONOTONE_IN_SAMPLE"
    assert any("H0" in h for h in r["live_counter_hypotheses"])
    assert "candidate" in r["note"]


def test_non_monotone_sample_is_reported_not_suppressed():
    series = ((1772, ExternalizationDepth(0, 1, 1, 0, 0)),
              (1851, ExternalizationDepth(1, 0, 0, 0, 0)))
    assert externalization_trend(series)["verdict"] == \
        "NON_MONOTONE_IN_SAMPLE"
    assert externalization_trend(series[:1])["reason"] == \
        "E_TREND_NEEDS_TWO_POINTS"


# ── the packet receiver ─────────────────────────────────────────────────

def _item(i, vol, sigma, layers):
    return {"item_id": f"{vol}-{i:02d}", "corpus_volume": vol,
            "claim": f"claim {vol}{i}", "sigma": sigma,
            "witnesses": tuple({"layer": l, "ref": f"{l}:{i}"}
                               for l in layers)}


def _good_packet():
    items = []
    for vol, layers, sigma in (("A", ("P",), "claimed"),
                               ("B", ("D",), "demonstrated"),
                               ("C", ("D", "J"), "judged"),
                               ("D", ("D", "J", "F"),
                                "operationally_survived")):
        items.extend(_item(i, vol, sigma, layers) for i in range(10))
    return tuple(items)


def test_sigma_overclaim_is_refused():
    bad = _item(1, "A", "demonstrated", ("P",))    # claims D on P evidence
    r = validate_packet_item(bad)
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_SIGMA_OVERCLAIM"
    assert r["computed"] == "claimed"


def test_missing_fields_and_unknown_volumes_are_refused():
    assert validate_packet_item({"item_id": "x"})["reason"] == \
        "E_PACKET_FIELD_MISSING"
    bad = _item(1, "E", "claimed", ("P",))
    assert validate_packet_item(bad)["reason"] == "E_UNKNOWN_VOLUME"


def test_the_promised_shape_is_ten_by_four():
    short = _good_packet()[:-1]
    r = validate_packet(short)
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_PACKET_SHAPE"


def test_a_well_formed_packet_is_accepted_and_frozen():
    r = validate_packet(_good_packet())
    assert r["verdict"] == "PACKET_ACCEPTED"
    assert r["count"] == 40 and r["packet_hash"]


def test_one_overclaiming_item_sinks_the_packet():
    items = list(_good_packet())
    items[0] = _item(0, "A", "judged", ("P",))
    r = validate_packet(tuple(items))
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_PACKET_ITEMS_INVALID"
    assert "A-00" in r["invalid"]


def test_deterministic():
    import crystal_palace as cp
    assert cp.canon(validate_packet(_good_packet())) == \
        cp.canon(validate_packet(_good_packet()))
