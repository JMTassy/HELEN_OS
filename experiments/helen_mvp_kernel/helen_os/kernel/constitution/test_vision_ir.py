"""HELEN VISION V2, falsified: the packet has no world field to write;
(PHOTOGRAPH, PROMOTES) is ordinary and buys no observation; the honest
ladder answer is (1, ?, 0, 0, 0) and not one collapsed yes; promotion
depth does not fall when the picture gets prettier; and PER_R->W = 0 is
worthless without coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import vision_ir as vi
from vision_ir import (
    climb,
    confidence_independence,
    packet,
    per_matrix,
    promotion_depth,
    warrant,
    write_world_claim,
)


def _r(**over):
    f = {"I": "img:AA_1950_07_p31", "kappa_M": "PHOTOGRAPH",
         "kappa_F": "PROMOTES", "rho": "unverified", "t": None,
         "s": "scan", "u": "operator"}
    f.update(over)
    return packet(**f)


# ── G_R only: there is no world field ──────────────────────────────────

def test_a_packet_is_a_representation_and_nothing_else():
    r = _r()
    assert r["ok"] is True
    assert r["layer"] == "G_R"
    assert r["emits_world_claim"] is False
    assert "G_W" not in r


def test_the_vision_layer_may_never_write_a_world_claim():
    v = write_world_claim(_r(), "phi3_referent_existed_by_date")
    assert v["written"] is False
    assert v["reason"] == "E_VISION_MAY_NOT_WRITE_G_W"


def test_an_incomplete_packet_is_refused():
    v = packet(I="img:x", kappa_M="PHOTOGRAPH")
    assert v["ok"] is False and v["reason"] == "E_INCOMPLETE_PACKET"
    assert "rho" in v["missing"] and "kappa_F" in v["missing"]


def test_medium_and_function_are_separate_and_both_checked():
    assert _r(kappa_M="VIBES")["reason"] == "E_UNKNOWN_MEDIUM"
    assert _r(kappa_F="DOCUMENTS")["reason"] == "E_UNKNOWN_FUNCTION"


def test_documents_is_gone_because_it_fused_two_axes():
    assert "DOCUMENTS" not in vi.KAPPA_M
    assert "DOCUMENTS" not in vi.KAPPA_F
    assert set(vi.KAPPA_M).isdisjoint(set(vi.KAPPA_F) - {"BOTTOM"})


# ── the four-part warrant ──────────────────────────────────────────────

def test_a_photograph_that_promotes_is_ordinary_and_buys_nothing():
    """(PHOTOGRAPH, PROMOTES) is a perfectly lawful pair — and on its
    own it warrants no historical proposition at all."""
    r = _r()
    assert r["ok"] is True
    v = warrant(r, "phi3_referent_existed_by_date",
                provenance=False, temporal=False, bridge_to_phi=False)
    assert v["warranted"] is False
    assert v["reason"] == "E_INCOMPLETE_WARRANT"
    assert v["missing"] == ["B", "T", "rho"]
    assert v["parts"]["M"] is True         # medium classified, that is all


def test_all_four_parts_or_no_warrant():
    r = _r()
    full = {"provenance": True, "temporal": True, "bridge_to_phi": True}
    assert warrant(r, "phi1_visually_represented", **full)[
        "warranted"] is True
    for drop in ("provenance", "temporal", "bridge_to_phi"):
        v = warrant(r, "phi1_visually_represented",
                    **{**full, drop: False})
        assert v["warranted"] is False
        assert v["reason"] == "E_INCOMPLETE_WARRANT"


def test_an_unclassified_medium_kills_the_M_part():
    v = warrant(_r(kappa_M="BOTTOM"), "phi1_visually_represented",
                provenance=True, temporal=True, bridge_to_phi=True)
    assert v["parts"]["M"] is False and v["warranted"] is False


def test_a_warrant_for_phi1_is_not_a_warrant_for_phi3():
    """B is indexed to the proposition. Holding the bridge for the weak
    rung does not carry to the strong one."""
    r = _r()
    weak = warrant(r, "phi1_visually_represented", provenance=True,
                   temporal=True, bridge_to_phi=True)
    strong = warrant(r, "phi3_referent_existed_by_date",
                     provenance=True, temporal=True,
                     bridge_to_phi=False)
    assert weak["warranted"] is True
    assert strong["warranted"] is False
    assert strong["missing"] == ["B"]


def test_an_unknown_proposition_and_a_bad_packet_are_refused():
    assert warrant(_r(), "phi9_world_peace", True, True, True)[
        "reason"] == "E_UNKNOWN_PROPOSITION"
    assert warrant(packet(I="x"), "phi1_visually_represented",
                   True, True, True)["reason"] == "E_BAD_PACKET"


# ── the promotion ladder ───────────────────────────────────────────────

def test_the_ladder_is_five_rungs_of_increasing_depth():
    depths = [promotion_depth(p)["d_P"] for p in vi.LADDER]
    assert depths == [0, 1, 2, 3, 4]
    assert depths == sorted(depths)


def test_an_unknown_rung_raises():
    with pytest.raises(ValueError, match="E_UNKNOWN_PROPOSITION"):
        promotion_depth("phi9_world_peace")


def test_the_honest_answer_is_one_yes_and_four_noes():
    """A bare photograph with no bridges: (1, 0, 0, 0, 0). Something is
    visually represented; nothing else follows."""
    v = climb(_r(), frozenset(), visual_confidence=0.99)
    assert v["rungs"]["phi1_visually_represented"] == "SUPPORTED"
    assert all(v["rungs"][p] == "UNSUPPORTED" for p in vi.LADDER[1:])
    assert v["collapsed_to_one_yes"] is False


def test_provenance_alone_buys_the_second_rung_and_no_more():
    """(1, ?, 0, 0, 0) — the '?' resolves only when provenance is
    established, and resolving it moves nothing above it."""
    v = climb(_r(), frozenset({"provenance"}), visual_confidence=0.2)
    assert v["rungs"]["phi2_depicts_referent"] == "SUPPORTED"
    assert v["rungs"]["phi3_referent_existed_by_date"] == "UNSUPPORTED"
    assert v["rungs"]["phi5_component_installed"] == "UNSUPPORTED"


def test_the_vlm_failure_mode_is_the_collapse_into_one_yes():
    """An ordinary VLM answers the whole ladder with a single yes. That
    is exactly the state this flag names — and it requires every bridge
    to be genuinely held before it is lawful."""
    every = frozenset({"provenance", "temporal", "design_comparison",
                       "component_evidence"})
    v = climb(_r(), every, visual_confidence=0.5)
    assert v["collapsed_to_one_yes"] is True
    assert all(s == "SUPPORTED" for s in v["rungs"].values())


def test_a_bad_packet_cannot_climb():
    assert climb(packet(I="x"), frozenset(), 0.9)["reason"] == \
        "E_BAD_PACKET"


# ── VisualConfidence PERPENDICULAR TO promotion depth ──────────────────

def test_confidence_is_recorded_and_never_read():
    low = climb(_r(), frozenset({"provenance"}), visual_confidence=0.01)
    high = climb(_r(), frozenset({"provenance"}), visual_confidence=1.0)
    assert low["rungs"] == high["rungs"]
    assert low["confidence_used_in_verdict"] is False
    assert low["visual_confidence"] != high["visual_confidence"]


def test_depth_is_identical_at_low_and_high_confidence():
    for phi in vi.LADDER:
        v = confidence_independence(phi, low=0.05, high=0.99)
        assert v["orthogonal"] is True
        assert v["reason"] is None
        assert v["d_P_at_low_confidence"] == \
            v["d_P_at_high_confidence"] == promotion_depth(phi)["d_P"]


def test_a_prettier_picture_does_not_shorten_the_proof_path():
    """The falsifier, stated as an experiment: raise confidence by 20x
    on the deepest rung and the required bridge set must not shrink."""
    deep = "phi5_component_installed"
    before = set(promotion_depth(deep)["required_bridges"])
    confidence_independence(deep, low=0.05, high=1.0)
    after = set(promotion_depth(deep)["required_bridges"])
    assert before == after == {"provenance", "temporal",
                               "design_comparison", "component_evidence"}


# ── PER is a matrix, and coverage is the positive control ──────────────

def _case(a, b, bridged, answered):
    return {"from": a, "to": b, "bridged": bridged,
            "answered": answered}


def test_a_governed_reader_passes_both_halves():
    cases = (_case("R", "E", True, True),
             _case("E", "W", True, True),
             _case("R", "W", True, True),
             _case("R", "W", True, True))
    v = per_matrix(cases, coverage_min=0.5)
    assert v["critical_PER_R_to_W"] == 0.0
    assert v["coverage"] == 1.0
    assert v["verdict"] == "PASS"


def test_one_unbridged_jump_from_representation_to_world_is_laundering():
    cases = (_case("R", "W", True, True),
             _case("R", "W", False, True))
    v = per_matrix(cases)
    assert v["critical_PER_R_to_W"] == 0.5
    assert v["verdict"] == "FAIL_LAUNDERING"


def test_hold_everything_scores_a_perfect_per_and_still_fails():
    """The trivial system: answer nothing, launder nothing, useless.
    Same positive control proof_ceiling already enforces."""
    cases = tuple(_case("R", "W", False, False) for _ in range(8))
    v = per_matrix(cases, coverage_min=0.5)
    assert v["critical_PER_R_to_W"] == 0.0      # perfect on the canary
    assert v["coverage"] == 0.0
    assert v["verdict"] == "FAIL_COVERAGE"


def test_the_matrix_reports_each_crossing_separately():
    cases = (_case("R", "E", False, True), _case("E", "W", True, True))
    v = per_matrix(cases)
    assert v["per"]["PER_R->E"] == 1.0
    assert v["per"]["PER_E->W"] == 0.0
    assert "PER_R->W" not in v["per"]
    assert v["critical_PER_R_to_W"] is None


def test_no_cases_is_refused():
    with pytest.raises(ValueError, match="E_NO_CASES"):
        per_matrix(())


def test_deterministic():
    a = climb(_r(), frozenset({"provenance"}), 0.3)
    b = climb(_r(), frozenset({"provenance"}), 0.3)
    assert vi.canon(a) == vi.canon(b)
