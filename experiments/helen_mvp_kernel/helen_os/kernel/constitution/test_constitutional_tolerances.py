"""Tolerances, falsified: margin separates barely from robustly
admitted; slack absorbs drift while the edge converts it into breach;
the Garden finds the admitted pair one epsilon apart with macroscopic
divergence; reliability claims are capped by the weakest dependency;
yield is not the target; chi_C is flat for noise and sharp for
evidence; the oscillator HOLDs unreceipted interpretive drift.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import ceiling_algebra as ca
import constitutional_tolerances as ct
from constitutional_tolerances import (
    chi_susceptibility,
    drift_absorption,
    drift_one,
    garden_yield,
    gate_reliability,
    lenient_gate,
    margins,
    oscillator_check,
    reference_corpus,
    sensitivity_search,
)

RECEIPT = ca.Receipt("r_tol",
                     frozenset({"root_R", "root_S", "root_T"}),
                     frozenset({"obj_A", "obj_B", "ui_note",
                                "ledger_root"}),
                     "ADJUDICATED")

ROBUST = ca.Transition("d_robust", frozenset({"root_R"}),
                       frozenset({"obj_A"}), "OBSERVED", True)

# uses the FULL proof grant and the EXACT authority grade: at the edge
BARELY = ca.Transition("d_barely",
                       frozenset({"root_R", "root_S", "root_T"}),
                       frozenset({"obj_A"}), "ADJUDICATED", True)


# ── the Margin Law ──────────────────────────────────────────────────────

def test_admitted_is_not_robustly_admitted():
    """Both ADMIT; only one has tolerance. C(delta)=1 is not enough."""
    mr, mb = margins(ROBUST, RECEIPT), margins(BARELY, RECEIPT)
    assert mr["verdict"] == mb["verdict"] == "ADMIT"
    assert mr["robustly_admitted"] is True and mr["M"] >= 1
    assert mb["barely_admitted"] is True and mb["M"] == 0


def test_the_thinnest_tolerance_is_named():
    mb = margins(BARELY, RECEIPT)
    assert mb["thinnest_tolerance"] in ("PROOF", "AUTHORITY")
    assert mb["margins"]["PROOF"] == 0
    assert mb["margins"]["AUTHORITY"] == 0


def test_replay_is_named_uninstrumented_not_given_a_fake_margin():
    m = margins(ROBUST, RECEIPT)
    assert "UNINSTRUMENTED" in m["replay_axis"]
    assert "REPLAY" not in m["margins"]


def test_a_rejected_delta_has_no_margin():
    bad = ca.Transition("d_bad", frozenset({"root_FOREIGN"}),
                        frozenset({"obj_A"}), "OBSERVED", True)
    m = margins(bad, RECEIPT)
    assert m["verdict"] == "REJECT"
    assert m["M"] is None
    assert m["robustly_admitted"] is False


# ── drift: slack absorbs, the edge breaks ──────────────────────────────

def test_margin_predicts_drift_absorption_on_both_deltas():
    for d in (ROBUST, BARELY):
        a = drift_absorption(d, RECEIPT)
        assert a["margin_predicts_absorption"] is True


def test_the_barely_admitted_delta_breaks_under_one_unit_of_drift():
    a = drift_absorption(BARELY, RECEIPT)
    assert a["dimensions"]["PROOF"]["absorbed"] is False
    assert a["dimensions"]["AUTHORITY"]["absorbed"] is False
    assert a["dimensions"]["SCOPE"]["absorbed"] is True   # scope has slack


def test_the_robust_delta_absorbs_the_same_drift_everywhere():
    a = drift_absorption(ROBUST, RECEIPT)
    assert all(v["absorbed"] for v in a["dimensions"].values())


def test_unknown_drift_dimension_refuses():
    with pytest.raises(ValueError, match="E_UNKNOWN_DRIFT_DIMENSION"):
        drift_one(ROBUST, RECEIPT, "TIME")


# ── constitutional sensitivity: little things, vitally big ─────────────

def test_the_garden_finds_the_admitted_pair_with_macroscopic_divergence():
    s = sensitivity_search(ROBUST, RECEIPT)
    assert s["sensitivity_found"] is True
    assert s["worst_case"]["added_object"] == "ledger_root"
    assert s["worst_case"]["epsilon"] == 1
    assert s["worst_case"]["divergence"] >= 100.0


def test_every_neighbor_in_the_search_is_itself_admitted():
    """The dangerous case is C(tau)=C(tau')=1 — both lawful."""
    s = sensitivity_search(ROBUST, RECEIPT)
    assert len(s["admitted_neighbors"]) == 3   # obj_B, ui_note, ledger_root
    for n in s["admitted_neighbors"]:
        d2 = ca.Transition("x", ROBUST.proof_roots,
                           ROBUST.effect_objects | {n["added_object"]},
                           ROBUST.authority_needed, True)
        assert ca.admit(d2, RECEIPT)["verdict"] == "ADMIT"


# ── the Microdependency Law ─────────────────────────────────────────────

def test_reliability_claims_are_capped_by_the_weakest_dependency():
    deps = {"hash_normalization": 0.999, "timestamp_parse": 0.99,
            "entity_resolution": 0.90, "grade_ladder": 0.9999}
    over = gate_reliability(deps, claimed=0.99)
    within = gate_reliability(deps, claimed=0.90)
    assert over["claim_admissible"] is False
    assert over["reason"] == "E_RELIABILITY_OVERCLAIM"
    assert over["weakest"] == "entity_resolution"
    assert within["claim_admissible"] is True


# ── the Yield Law ───────────────────────────────────────────────────────

def _garden():
    """Ten candidates: three robust, three barely, four inadmissible."""
    out = []
    for i in range(3):
        out.append(ca.Transition(f"g_rob{i}", frozenset({"root_R"}),
                                 frozenset({"obj_A"}), "OBSERVED", True))
    for i in range(3):
        out.append(ca.Transition(f"g_edge{i}",
                                 frozenset({"root_R", "root_S",
                                            "root_T"}),
                                 frozenset({"obj_A"}), "ADJUDICATED",
                                 True))
    for i in range(4):
        out.append(ca.Transition(f"g_bad{i}", frozenset({"root_X"}),
                                 frozenset({"obj_A"}), "OBSERVED", True))
    return tuple(out)


def test_low_yield_is_health_not_pathology():
    y = garden_yield(_garden(), RECEIPT, margin_floor=0)
    assert y["admitted"] == 6 and y["generated"] == 10
    assert y["low_yield_is_pathology"] is False
    assert y["hamilton_hairspring_yield"] == 0.025


def test_a_margin_floor_trades_yield_for_residue_stability():
    """The film's sentence, executed: the selective policy admits
    fewer and the residue is more stable."""
    loose = garden_yield(_garden(), RECEIPT, margin_floor=0)
    tight = garden_yield(_garden(), RECEIPT, margin_floor=1)
    assert tight["selectivity"] < loose["selectivity"]
    assert tight["residue_stability"] > loose["residue_stability"]
    assert "residue" in tight["law"]


# ── the Elinvar Law ─────────────────────────────────────────────────────

def test_chi_is_flat_for_noise_and_sharp_for_evidence():
    chi = chi_susceptibility(ROBUST, RECEIPT)
    assert chi["chi_irrelevant"] == 0.0     # renaming/order move nothing
    assert chi["chi_relevant"] == 1.0       # losing a real root flips
    assert chi["elinvar"] is True


# ── the Hairspring: the reference oscillator ────────────────────────────

def test_the_reference_corpus_holds_under_the_real_gate():
    o = oscillator_check(ca.admit)
    assert o["D_t"] == 0
    assert o["verdict"] == "REFERENCE_HELD"


def test_a_lenient_interpretation_is_caught_and_held():
    """The drifted gate admits 'one grade over'; the sealed corpus
    exposes it; without an amendment receipt the verdict is HOLD."""
    o = oscillator_check(lenient_gate)
    assert o["D_t"] == 1
    assert o["disagreements"][0]["case"] == "over_grade_rejects"
    assert o["verdict"] == "HOLD"
    assert o["reason"] == "E_INTERPRETIVE_DRIFT"


def test_a_receipted_amendment_is_lawful_change_not_drift():
    o = oscillator_check(lenient_gate,
                         amendment_receipt="r_amend_0042")
    assert o["verdict"] == "AMENDED_UNDER_RECEIPT"
    assert o["reason"] is None


def test_the_corpus_covers_all_four_ceilings_plus_the_admit_case():
    names = [c[0] for c in reference_corpus()]
    assert len(names) == 5
    assert names[0] == "exact_grade_admits"


def test_deterministic():
    assert ct.canon(margins(BARELY, RECEIPT)) == \
        ct.canon(margins(BARELY, RECEIPT))
    assert ct.canon(oscillator_check(ca.admit)) == \
        ct.canon(oscillator_check(ca.admit))
