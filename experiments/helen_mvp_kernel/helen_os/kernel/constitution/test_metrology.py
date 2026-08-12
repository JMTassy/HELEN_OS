"""Metrology, falsified: the margin is signed; alpha_-(m) finds the
defective verifier only at the boundary; chi_W and chi_Pi separate a
right bit from a reconstructible pass; a bare scalar is not portable
evidence; 100 duplicates far from the frontier carry zero information;
the resolution law binds only the critical manifold; and UNKNOWN
RESOLUTION never mints NEW LAW.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
import metrology as mt
from metrology import (
    alpha_minus,
    broken_witness_maker,
    chi_split,
    escalate,
    frontier_information,
    make_witness,
    mint_law_from_unresolved,
    replay_witness,
    report_scalar,
    resolution_check,
    signed_margin,
    sloppy_verifier,
)

RECEIPT = ca.Receipt("r_met", frozenset({"root_r", "root_s"}),
                     frozenset({"obj_a", "obj_b"}), "ADJUDICATED")

PASS_ROBUST = ca.Transition("d_pass", frozenset({"root_r"}),
                            frozenset({"obj_a"}), "OBSERVED", True)


def _fail_at(m: int, tag: str = "") -> ca.Transition:
    """Ground-truth FAIL exactly m unit-edits from the boundary:
    m foreign proof roots."""
    foreign = frozenset(f"root_x{tag}{i}" for i in range(m))
    return ca.Transition(f"d_fail_{m}{tag}",
                         frozenset({"root_r"}) | foreign,
                         frozenset({"obj_a"}), "OBSERVED", True)


# case foreign ONLY by capitalization: mu = -1, the boundary case the
# sloppy verifier falsely admits
BOUNDARY_CASE = ca.Transition("d_case", frozenset({"ROOT_R"}),
                              frozenset({"obj_a"}), "OBSERVED", True)


# ── the signed margin ───────────────────────────────────────────────────

def test_the_margin_is_signed_positive_inside_negative_outside():
    inside = signed_margin(PASS_ROBUST, RECEIPT)
    outside = signed_margin(_fail_at(3), RECEIPT)
    assert inside["side"] == "PASS" and inside["mu"] >= 1
    assert outside["side"] == "FAIL" and outside["mu"] == -3


def test_mu_counts_all_violation_dimensions():
    d = ca.Transition("d_multi", frozenset({"root_r", "root_x"}),
                      frozenset({"obj_a", "obj_z"}), "ADMITTED", False)
    # 1 foreign root + 1 foreign object + 1 grade over + 1 stale = -4
    assert signed_margin(d, RECEIPT)["mu"] == -4


def test_the_boundary_case_sits_at_minus_one():
    assert signed_margin(BOUNDARY_CASE, RECEIPT)["mu"] == -1


# ── alpha_-(m): the failure surface lives at the boundary ──────────────

def test_the_sloppy_verifier_falsely_admits_only_at_the_boundary():
    """alpha_-(1) = 1 on the case-mangled family; alpha_-(m>=2) = 0 on
    the far family. Sampling far from the frontier would report a
    perfect verifier."""
    cases = (BOUNDARY_CASE, _fail_at(2), _fail_at(3), _fail_at(5))
    a = alpha_minus(sloppy_verifier, cases, RECEIPT)
    assert a[1]["alpha_minus"] == 1.0          # the calibration find
    assert a[2]["alpha_minus"] == 0.0
    assert a[3]["alpha_minus"] == 0.0
    assert a[5]["alpha_minus"] == 0.0


def test_the_real_gate_has_zero_alpha_minus_on_the_same_cases():
    cases = (BOUNDARY_CASE, _fail_at(2), _fail_at(3))
    a = alpha_minus(ca.admit, cases, RECEIPT)
    assert all(v["alpha_minus"] == 0.0 for v in a.values())


def test_pass_cases_are_excluded_from_alpha_minus():
    a = alpha_minus(sloppy_verifier, (PASS_ROBUST,), RECEIPT)
    assert a == {}


# ── the instrument: chi_W and chi_Pi, separated ─────────────────────────

def test_a_complete_witness_replays_and_reproduces():
    w = make_witness(ca.admit, PASS_ROBUST, RECEIPT)
    rep = replay_witness(w)
    assert rep["replayed"] is True and rep["reproduces"] is True


def test_an_insufficient_witness_is_refused_with_the_missing_fields():
    w = broken_witness_maker(ca.admit, PASS_ROBUST, RECEIPT)
    rep = replay_witness(w)
    assert rep["replayed"] is False
    assert rep["reason"] == "E_WITNESS_INSUFFICIENT"
    assert "receipt_id" in rep["missing"]


def test_chi_w_and_chi_pi_separate_the_bit_from_the_reconstruction():
    """M(I) != M(V): the broken-W instrument has a perfect verdict bit
    and chi_W = 0 — the aggregate may not conceal which stage failed."""
    cases = (PASS_ROBUST, _fail_at(2))
    good = chi_split(make_witness, ca.admit, cases, RECEIPT)
    broken = chi_split(broken_witness_maker, ca.admit, cases, RECEIPT)
    assert good["chi_W"] == 1.0 and good["chi_Pi"] == 1.0
    assert broken["chi_W"] == 0.0 and broken["chi_Pi"] == 0.0


def test_a_false_pass_fails_replay_not_just_review():
    """The sloppy verifier's boundary false-admit produces a witness
    whose INDEPENDENT replay contradicts it — Pi catches V."""
    w = make_witness(sloppy_verifier, BOUNDARY_CASE, RECEIPT)
    assert w["verdict"] == "ADMIT"             # V's false bit
    rep = replay_witness(w)
    assert rep["reproduces"] is False
    assert rep["independent_verdict"] == "REJECT"


# ── portable evidence ───────────────────────────────────────────────────

def test_a_bare_scalar_is_not_portable_evidence():
    v = report_scalar(estimate=0.01)
    assert v["portable"] is False
    assert v["reason"] == "E_UNPORTABLE_EVIDENCE"
    assert "adversary" in v["missing"]


def test_the_full_seven_coordinate_tuple_is_portable():
    v = report_scalar(estimate=0.01, uncertainty="95CI:[0.005,0.02]",
                      population="boundary fail cases m<=2",
                      environment="ceiling_algebra vX",
                      adversary="sloppy_verifier family",
                      procedure="alpha_minus sweep",
                      version="constitution@63probes")
    assert v["portable"] is True
    assert len(v["tuple"]) == 7


# ── the anti-gaming law ─────────────────────────────────────────────────

def test_a_hundred_far_duplicates_carry_zero_frontier_information():
    far_dupes = tuple(_fail_at(5) for _ in range(100))
    v = frontier_information(far_dupes, RECEIPT, window=1)
    assert v["n_cases"] == 100
    assert v["frontier_information"] == 0


def test_ten_distinct_boundary_cases_beat_the_hundred_duplicates():
    near = tuple(_fail_at(1, tag=f"_{i}") for i in range(10))
    v = frontier_information(near, RECEIPT, window=1)
    assert v["frontier_information"] == 10
    assert "scarce resource" in v["law"]


def test_duplicate_boundary_cases_are_counted_once():
    dupes = tuple(_fail_at(1, tag="_same") for _ in range(50))
    assert frontier_information(dupes, RECEIPT)["frontier_information"] \
        == 1


# ── the resolution law, bounded ─────────────────────────────────────────

def test_resolution_binds_the_critical_manifold_only():
    envs = {"admission_boundary": {"critical": True, "R_I": 0.01,
                                   "R_required": 1.55},
            "cosmetic_rendering": {"critical": False, "R_I": 99.0,
                                   "R_required": 1.0}}
    v = resolution_check(envs)
    assert v["holds"] is True                  # non-critical tolerated
    assert v["omniscience_required"] is False


def test_a_critical_env_outrunning_its_falsifier_fails_the_law():
    envs = {"admission_boundary": {"critical": True, "R_I": 2.0,
                                   "R_required": 1.55}}
    v = resolution_check(envs)
    assert v["holds"] is False
    assert v["failing_envs"] == ["admission_boundary"]
    assert "outrun" in v["doctrine"]


def test_the_hamilton_numbers_satisfy_the_law_as_relayed():
    """Time Comparator resolution 0.01 s/day against the 1.55 s/day
    Navy spec — the historical instance of R_I < R_required."""
    assert mt.TIME_COMPARATOR_RESOLUTION < mt.NAVY_SPEC_SEC_PER_DAY
    assert mt.MODEL_21_SEC_PER_DAY < mt.NAVY_SPEC_SEC_PER_DAY


# ── escalation, and the guardrail ───────────────────────────────────────

def test_all_five_escalation_routes_exist_and_none_mints_law():
    for kind, route in mt.ESCALATION_ROUTES.items():
        v = escalate(kind)
        assert v["route"] == route
        assert v["authorizes_new_law"] is False


def test_metrology_failure_is_the_hamilton_branch():
    v = escalate("M_CANNOT_RESOLVE")
    assert v["route"] == "metrology_upgrade"
    assert v["hamilton_branch"] is True
    assert v["guardrail"] == "UNKNOWN RESOLUTION is not NEW LAW"


def test_an_unknown_finding_kind_is_flagged():
    assert escalate("VIBES")["reason"] == "E_UNKNOWN_FINDING_KIND"


def test_unknown_resolution_never_mints_new_law():
    v = mint_law_from_unresolved("cannot resolve mu below 1 unit")
    assert v["minted"] is False
    assert v["reason"] == "E_UNKNOWN_RESOLUTION_IS_NOT_NEW_LAW"
    assert v["route_instead"] == "metrology_upgrade"
    assert "must not silently mutate the constitution" in v["law"]


def test_the_frozen_architecture_and_garden_identity():
    assert mt.ARCHITECTURE_FROZEN == ("CONSTITUTION (P,S,A,R)",
                                      "INSTRUMENT (V,W,Pi)",
                                      "METROLOGY M(I)")
    assert "experimental design" in mt.GARDEN_IDENTITY


def test_deterministic():
    cases = (BOUNDARY_CASE, _fail_at(2))
    assert mt.canon(alpha_minus(sloppy_verifier, cases, RECEIPT)) == \
        mt.canon(alpha_minus(sloppy_verifier, cases, RECEIPT))
    assert mt.canon(chi_split(make_witness, ca.admit, cases, RECEIPT)) \
        == mt.canon(chi_split(make_witness, ca.admit, cases, RECEIPT))
