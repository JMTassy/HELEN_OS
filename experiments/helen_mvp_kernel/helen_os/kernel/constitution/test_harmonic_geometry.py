"""Sacred does not imply physical, but symbolism may generate
hypotheses; power is typed per domain or refused; the picture must
compile into invariants before physics; symmetry is not a quality
prior; the scrambled control can kill the sacred reading; Phi chooses
experiments and predicts nothing; the two frontiers stay orthogonal
until a bridge is measured; and the frontier moves on warrant only —
in both directions.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harmonic_geometry as hg
from harmonic_geometry import (
    adversary_step,
    domain_cross,
    experiment,
    frontier_pair,
    geometry_descriptors,
    invariant_survival,
    next_geometry,
    phi_score,
    psi_climb,
    resonance_claim,
    sigma_support,
    smart_sigil_status,
    symmetry_prior,
    typed_power,
)


# ── the poset and the orthogonal axis ──────────────────────────────────

def test_the_psi_ladder_climbs_one_discharged_rung_at_a_time():
    assert len(hg.PSI) == 5
    ok = psi_climb("FORM", "SYMMETRY_PATTERN", True)
    assert ok["ok"] is True
    skip = psi_climb("FORM", "MEASURED_EFFECT", True)
    assert skip["reason"] == "E_RUNG_SKIPPED"
    assert "PREDICTED_MODAL_EFFECT" in skip["skipped"]
    lazy = psi_climb("MEASURED_EFFECT",
                     "REPLICATED_GEOMETRY_SPECIFIC", False)
    assert lazy["reason"] == "E_UNDISCHARGED_OBLIGATION"


def test_sigma_never_supports_a_physical_rung():
    v = sigma_support("PREDICTED_MODAL_EFFECT",
                      support_is_symbolic=True)
    assert v["reason"] == "E_SYMBOLIC_AXIS_CONFUSION"
    assert sigma_support("FORM", support_is_symbolic=False)["ok"]


def test_the_two_frontiers_are_consistent_and_unbridgeable_by_inference():
    v = frontier_pair("strongly_historically_warranted",
                      "no_exceptional_effect_demonstrated")
    assert v["ok"] is True and v["consistent"] is True
    inf = frontier_pair("high", "high", inferred_from_other=True,
                        bridge_measured=False)
    assert inf["reason"] == "E_UNBRIDGED_FRONTIERS"
    bridged = frontier_pair("high", "high", inferred_from_other=True,
                            bridge_measured=True)
    assert bridged["ok"] is True


# ── typed resonance & power ────────────────────────────────────────────

def test_three_resonances_three_regimes():
    s = resonance_claim("symbolic")
    assert s["licensed_as"] == "semiotic_property"
    assert s["physical_claim"] is False
    p = resonance_claim("perceptual")
    assert p["requires"] == "human_experiments"
    naked = resonance_claim("physical")
    assert naked["reason"] == "E_MECHANISM_UNDEFINED"
    none_mech = resonance_claim("physical", "NONE", "Q", "1kHz", "b")
    assert none_mech["reason"] == "E_MECHANISM_UNDEFINED"
    full = resonance_claim("physical", "acoustic", "Q_factor",
                           "200-800Hz", "clamped_plate")
    assert full["ok"] is True
    assert full["physical_claim"] is False   # hypothesis != effect


def test_a_scalar_power_is_refused():
    assert typed_power(value=0.92)["reason"] == "E_UNTYPED_POWER"
    assert typed_power(0.5, "acoustic", warrant=None)["reason"] == \
        "E_PHYSICAL_POWER_UNWARRANTED"
    assert typed_power(0.5, "acoustic", "receipt:lab1")["ok"] is True
    assert typed_power(0.5, "symbolic")["ok"] is True


def test_every_new_domain_needs_its_own_cross():
    v = domain_cross("acoustic", "biological", new_cross_warrant=None)
    assert v["reason"] == "E_DOMAIN_CROSS_WITHOUT_WARRANT"
    ok = domain_cross("acoustic", "biological", "receipt:bio_exp")
    assert ok["ok"] is True


# ── mathematics over mystique ──────────────────────────────────────────

def test_a_hypothesis_from_the_picture_alone_is_visual_mystique():
    v = geometry_descriptors({"Aut": "C6"})
    assert v["reason"] == "E_VISUAL_MYSTIQUE"
    assert "Lambda" in v["missing_invariants"]
    full = geometry_descriptors({k: f"v_{k}" for k in
                                 hg.DESCRIPTOR_KEYS})
    assert full["compiled"] is True


def test_symmetry_is_not_a_quality_prior():
    v = symmetry_prior(symmetry_increase=True,
                       assumed_quality_increase=True)
    assert v["reason"] == "E_SYMMETRY_PRIOR"
    ok = symmetry_prior(True, False)
    assert "geometry_response_map" in ok["study_object"]


# ── counterfactual controls ────────────────────────────────────────────

H_OK = {"mechanism": "acoustic", "observable": "Q",
        "frequency_band": "200-800Hz", "boundary": "clamped",
        "predicted_effect": "Q(g)>Q(matched)"}


def test_an_experiment_without_controls_is_refused():
    v = experiment("flower_of_life", H_OK, controls=("rotate",),
                   replications=1)
    assert v["reason"] == "E_UNCONTROLLED_GEOMETRY"
    ok = experiment("flower_of_life", H_OK,
                    ("scramble", "random", "symmetry_matched"), 2)
    assert ok["ok"] is True
    assert "which invariant must survive" in ok["question"]
    bad = experiment("g", H_OK, ("scramble", "vibes", "random"), 1)
    assert bad["reason"] == "E_UNKNOWN_CONTROL"


def test_the_scrambled_control_kills_the_sacred_reading():
    v = invariant_survival(effect_on_g=True,
                           effect_by_control={"scramble": True,
                                              "random": True})
    assert v["verdict"] == "ARRANGEMENT_NOT_CAUSE"


def test_a_structural_candidate_names_its_surviving_invariant():
    v = invariant_survival(True, {"scramble": False,
                                  "symmetry_matched": True,
                                  "random": False})
    assert v["verdict"] == "STRUCTURAL_CANDIDATE"
    assert "symmetry_matched" in v["effect_survives_in"]
    assert "scramble" in v["effect_killed_by"]
    # a clean null is valuable too
    assert invariant_survival(False, {})["verdict"] == "NO_EFFECT"


# ── Phi and the experiment chooser ─────────────────────────────────────

def test_phi_prioritizes_and_never_predicts():
    v = phi_score(0.9, 0.8, 0.7, 0.9)
    assert v["ok"] is True and v["predicts_power"] is False
    bad = phi_score(0.9, 0.8, 0.7, 0.9, used_as_power=True)
    assert bad["reason"] == "E_PHI_IS_NOT_POWER"


def test_the_next_geometry_maximizes_information_per_cost():
    # (id, info_gain, cost, risk)
    v = next_geometry((("pretty_but_settled", 0.1, 1.0, 0.0),
                       ("boring_but_discriminating", 0.9, 1.0, 0.0)))
    assert v["g_star"] == "boring_but_discriminating"


# ── the SMART SIGIL ladder ─────────────────────────────────────────────

def test_the_sigil_status_ladder_is_earned():
    sym = smart_sigil_status({"physical_hypothesis":
                              {"mechanism": "NONE"}})
    assert sym["status"] == "SYMBOLIC"
    incomplete = smart_sigil_status({"physical_hypothesis":
                                     {"mechanism": "acoustic"}})
    assert incomplete["status"] == "SYMBOLIC"
    assert incomplete["reason"] == "E_MECHANISM_UNDEFINED"
    cand = smart_sigil_status({"physical_hypothesis":
                               dict(H_OK)})
    assert cand["status"] == "CANDIDATE"
    measured = smart_sigil_status({"physical_hypothesis": dict(H_OK),
                                   "experiment_run": True,
                                   "controls_run": ("scramble",
                                                    "random",
                                                    "rotate"),
                                   "replications": 1,
                                   "geometry_specific": None})
    assert measured["status"] == "MEASURED"
    warranted = smart_sigil_status({"physical_hypothesis": dict(H_OK),
                                    "experiment_run": True,
                                    "controls_run": ("scramble",
                                                     "random",
                                                     "rotate"),
                                    "replications": 2,
                                    "geometry_specific": True})
    assert warranted["status"] == "WARRANTED"


# ── the adversary, both directions ─────────────────────────────────────

def test_salience_never_moves_the_physical_frontier():
    stack = adversary_step(salience_delta=100,   # 4K + captions + VLMs
                           warrant_delta=0, frontier_moved=True)
    assert stack["reason"] == "E_SALIENCE_MOVED_FRONTIER"
    held = adversary_step(100, 0, frontier_moved=False)
    assert held["ok"] is True and held["non_amplification"] is True


def test_a_genuine_measurement_must_move_the_frontier():
    inert = adversary_step(0, warrant_delta=1, frontier_moved=False)
    assert inert["reason"] == "E_UNRESPONSIVE_FRONTIER"
    moved = adversary_step(0, 1, frontier_moved=True)
    assert moved["ok"] is True and moved["responsive"] is True


def test_deterministic():
    assert hg.canon(phi_score(0.9, 0.8, 0.7, 0.9)) == \
        hg.canon(phi_score(0.9, 0.8, 0.7, 0.9))
