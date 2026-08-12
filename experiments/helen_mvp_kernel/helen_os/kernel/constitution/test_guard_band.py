"""Guard band, falsified: per-ceiling signed margins name the
bottleneck mechanically; the three-region decision makes HOLD the
correct output near the boundary; an uncalibrated PASS is an
indication; calibrated admission needs band AND Gamma AND Pi; and
authority contracts when resolution falls below the decision margin —
a guard band, never a fifth ceiling.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import ceiling_algebra as ca
import guard_band as gb
from guard_band import (
    admission_measurement,
    authority_contraction,
    calibrated_admit,
    ceiling_margins_signed,
    epistemic_chain,
    guarded_decision,
    is_calibrated_result,
)

RECEIPT = ca.Receipt("r_gb", frozenset({"root_r", "root_s"}),
                     frozenset({"obj_a", "obj_b"}), "ADJUDICATED")

ROBUST = ca.Transition("d_rob", frozenset({"root_r"}),
                       frozenset({"obj_a"}), "OBSERVED", True)
VIOLATOR = ca.Transition("d_bad",
                         frozenset({"root_r", "root_x", "root_y"}),
                         frozenset({"obj_a"}), "OBSERVED", True)


# ── per-ceiling signed margins and the active constraint ───────────────

def test_signed_margins_positive_inside_negative_outside():
    m = ceiling_margins_signed(ROBUST, RECEIPT)
    assert m["mu"]["PROOF"] == 1 and m["mu"]["SCOPE"] == 1
    assert m["mu"]["AUTHORITY"] == 2 and m["mu"]["REPLAY"] == 1
    bad = ceiling_margins_signed(VIOLATOR, RECEIPT)
    assert bad["mu"]["PROOF"] == -2
    assert bad["mu_C"] == -2


def test_the_argmin_names_the_bottleneck_mechanically():
    bad = ceiling_margins_signed(VIOLATOR, RECEIPT)
    assert bad["active_constraint"] == "PROOF"
    assert "no narrative diagnosis" in bad["law"]


def test_replay_margin_is_coarse_and_says_so():
    m = ceiling_margins_signed(ROBUST, RECEIPT)
    assert m["mu"]["REPLAY"] in (-1, 1)
    assert "named not faked" in m["replay_note"]


# ── the three-region guarded decision ───────────────────────────────────

def test_the_three_regions():
    assert guarded_decision(2.0, 0.5, k=2.0)["region"] == "ADMIT"
    assert guarded_decision(-2.0, 0.5, k=2.0)["region"] == "REJECT"
    assert guarded_decision(0.5, 0.5, k=2.0)["region"] == "HOLD_UNKNOWN"


def test_hold_is_the_correct_output_near_the_boundary():
    v = guarded_decision(0.5, 0.5, k=2.0)
    assert v["reason"] == "E_BELOW_RESOLUTION"


def test_uncertainty_widens_hold_never_weakens_the_constitution():
    narrow = guarded_decision(1.5, 0.1, k=2.0)
    wide = guarded_decision(1.5, 1.0, k=2.0)
    assert narrow["region"] == "ADMIT"
    assert wide["region"] == "HOLD_UNKNOWN"     # same mu, more u
    assert wide["hold_width"] > narrow["hold_width"]
    assert "never weakens the constitution" in wide["law"]


def test_negative_uncertainty_is_refused():
    with pytest.raises(ValueError, match="E_NEGATIVE_UNCERTAINTY"):
        guarded_decision(1.0, -0.1)


# ── the admission measurement ───────────────────────────────────────────

def test_a_full_measurement_is_a_calibrated_result():
    m = admission_measurement(ROBUST, RECEIPT, u=0.2,
                              e="ceiling_algebra vX",
                              v="constitution@64probes")
    assert is_calibrated_result(m)["status"] == "CALIBRATED_RESULT"


def test_pass_without_coordinates_is_an_indication():
    m = admission_measurement(ROBUST, RECEIPT, u=0.2, e="env", v="v1")
    for field in ("u", "Gamma", "e", "v"):
        stripped = {k: v for k, v in m.items() if k != field}
        r = is_calibrated_result(stripped)
        assert r["status"] == "INDICATION"
        assert r["reason"] == "E_UNCALIBRATED_PASS"
        assert field in r["missing"]


# ── calibrated admission: band AND Gamma AND Pi ─────────────────────────

def test_a_robust_delta_with_small_uncertainty_admits():
    v = calibrated_admit(ROBUST, RECEIPT, u=0.2, k=2.0)
    assert v["verdict"] == "ADMIT"
    assert v["gamma_valid"] is True and v["pi_reproduces"] is True


def test_the_same_delta_with_large_uncertainty_holds():
    """mu_C = 1; k*u = 2 > 1: the identical constitutional facts, a
    coarser instrument — HOLD, not ADMIT."""
    v = calibrated_admit(ROBUST, RECEIPT, u=1.0, k=2.0)
    assert v["verdict"] == "HOLD_UNKNOWN"
    assert v["band_region"] == "HOLD_UNKNOWN"


def test_a_clear_violator_rejects_even_with_coarse_instrument():
    v = calibrated_admit(VIOLATOR, RECEIPT, u=0.4, k=2.0)
    assert v["verdict"] == "REJECT"
    assert v["active_constraint"] == "PROOF"


# ── Replayable =/=> Resolvable =/=> Safe ────────────────────────────────

def test_the_chain_never_collapses():
    # replayable but not resolvable: |mu| <= k*u
    a = epistemic_chain(0.5, 0.5, replay_ok=True, k=2.0)
    assert a["replayable"] is True and a["resolvable"] is False
    assert a["safe_to_admit"] is False
    # resolvable on the FAIL side: still not safe
    b = epistemic_chain(-3.0, 0.5, replay_ok=True, k=2.0)
    assert b["resolvable"] is True and b["safe_to_admit"] is False
    # all three links present: safe
    c = epistemic_chain(3.0, 0.5, replay_ok=True, k=2.0)
    assert c["safe_to_admit"] is True
    # resolvable and positive but NOT replayable: not safe
    d = epistemic_chain(3.0, 0.5, replay_ok=False, k=2.0)
    assert d["safe_to_admit"] is False


# ── the locked rule ─────────────────────────────────────────────────────

def test_authority_contracts_when_resolution_falls_below_margin():
    v = authority_contraction(0.5, 0.5, k=2.0)   # resolution 1.0 > 0.5
    assert v["authority_contracts"] is True
    assert v["verdict_when_contracted"] == "HOLD_UNKNOWN"
    assert v["law"] == ("WHEN RESOLUTION FALLS BELOW THE DECISION "
                        "MARGIN, AUTHORITY MUST CONTRACT")


def test_the_contraction_is_a_guard_band_not_a_fifth_ceiling():
    v = authority_contraction(0.5, 0.5, k=2.0)
    assert v["is_fifth_ceiling"] is False
    assert v["is_guard_band"] is True
    assert v["route_on_persistent_contraction"] == "metrology_upgrade"


def test_no_contraction_when_the_margin_is_resolved():
    v = authority_contraction(3.0, 0.5, k=2.0)   # resolution 1.0 < 3.0
    assert v["authority_contracts"] is False


def test_deterministic():
    assert gb.canon(calibrated_admit(ROBUST, RECEIPT, 0.2)) == \
        gb.canon(calibrated_admit(ROBUST, RECEIPT, 0.2))
    assert gb.canon(ceiling_margins_signed(VIOLATOR, RECEIPT)) == \
        gb.canon(ceiling_margins_signed(VIOLATOR, RECEIPT))
