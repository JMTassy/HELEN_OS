"""Falsifiers for HF-01..HF-15: the history fiber, obligation
conservation, the five laundering classes, the reducer conservation
law, and the equal-state/different-history bead.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import history_fiber as hf
from history_fiber import (
    DischargeReceipt,
    History,
    Movement,
    Obligation,
    RawFinding,
    authority_laundering,
    causal_aliasing,
    compensate,
    conserve_obligations,
    discharges,
    equal_state_different_history_bead,
    equiv_governed,
    equiv_visible,
    learning_laundering,
    memory_laundering,
    projection_laundering,
    reducer_conservation,
    safe_reduce,
    state_laundering,
)

DISCLOSE = Obligation("o1", "repair", owed_by="org",
                      created_by="m1",
                      discharge_contract="notify affected parties")


def _h_a():
    """S0 -> S1 -> S0, the disclosure-then-deletion shape."""
    return History("A", "S0",
                   (Movement("m1", "S0", "S1",
                             {"exposure": "disclosed",
                              "consent": "absent"}),
                    Movement("m2", "S1", "S0",
                             {"repair": "deleted"})),
                   frozenset({DISCLOSE}))


def _h_b():
    """S0, untouched."""
    return History("B", "S0", (), frozenset())


# ── HF-01/02: pi is many-to-one ────────────────────────────────────────

def test_two_histories_share_a_visible_state():
    a, b = _h_a(), _h_b()
    assert a.visible_state() == b.visible_state() == "S0"
    assert equiv_visible(a, b) is True
    assert a.fingerprint() != b.fingerprint()      # pi loses this


# ── HF-03: ~_G strictly finer; aliasing detected ───────────────────────

def test_governed_equivalence_is_strictly_finer_than_visible():
    e = equiv_governed(_h_a(), _h_b())
    assert e["visible_equivalent"] is True
    assert e["governed_equivalent"] is False
    assert set(e["differing_dimensions"]) >= {"exposure", "consent",
                                              "repair"}


def test_representing_them_as_equal_is_causal_aliasing():
    r = causal_aliasing(_h_a(), _h_b(), represented_equal=True)
    assert r["verdict"] == "E_CAUSAL_ALIASING"
    assert r["visible_equivalent"] is True
    assert causal_aliasing(_h_a(), _h_b(),
                           represented_equal=False)["verdict"] == \
        "NO_ALIASING"


def test_a_history_is_governed_equivalent_to_itself():
    assert equiv_governed(_h_a(), _h_a())["governed_equivalent"] is True


# ── HF-04: governed state carries three coordinates ────────────────────

def test_governed_state_is_a_triple():
    g = _h_a().governed_state()
    assert set(g) == {"S", "F", "Omega"}
    assert g["S"] == "S0" and g["Omega"] == frozenset({"o1"})


# ── HF-05/06: compensation is not erasure ──────────────────────────────

def test_state_returns_but_history_and_obligations_do_not():
    h = History("A", "S0", (Movement("m1", "S0", "S1",
                                     {"exposure": "disclosed"}),),
                frozenset({DISCLOSE}))
    r = compensate(h, Movement("m2", "S1", "S0", {"repair": "deleted"}))
    assert r["state_restored"] is True
    assert r["history_restored"] is False
    assert r["obligations_surviving"] == ["o1"]    # deletion is not notice
    assert "does not imply ERASURE" in r["law"]


# ── HF-07/08/09: obligation conservation and typed discharge ───────────

def test_an_obligation_without_a_contract_is_unconstructible():
    with pytest.raises(ValueError, match="E_OBLIGATION_WITHOUT_CONTRACT"):
        Obligation("x", "repair", "org", "m1", discharge_contract="")


def test_a_receipt_without_a_witness_is_unconstructible():
    with pytest.raises(ValueError, match="E_DISCHARGE_WITHOUT_WITNESS"):
        DischargeReceipt("r", ("o1",), "notify affected parties", "")


def test_the_wrong_contract_discharges_nothing():
    wrong = DischargeReceipt("r1", ("o1",), "deleted the record",
                             "log#9")
    d = discharges(wrong, DISCLOSE)
    assert d["discharges"] is False and d["reason"] == "E_CONTRACT_MISMATCH"
    right = DischargeReceipt("r2", ("o1",), "notify affected parties",
                             "email#77")
    assert discharges(right, DISCLOSE)["discharges"] is True


def test_undischarged_obligations_survive_the_transition():
    r = conserve_obligations(frozenset({DISCLOSE}),
                             (DischargeReceipt("r1", ("o1",),
                                               "deleted the record",
                                               "log#9"),))
    assert r["carried_forward"] == ["o1"]
    assert r["discharged"] == []
    assert r["refused_discharges"][0]["reason"] == "E_CONTRACT_MISMATCH"
    assert "does not imply obligation discharged" in r["law"]


def test_the_conservation_equation_adds_generated_and_residual():
    gen = Obligation("o2", "notify", "org", "m2", "regulator filing")
    res = Obligation("o1r", "repair", "org", "m1", "partial remedy")
    good = DischargeReceipt("r", ("o1",), "notify affected parties",
                            "email#77")
    r = conserve_obligations(frozenset({DISCLOSE}), (good,),
                             frozenset({gen}), frozenset({res}))
    ids = {o.oblig_id for o in r["omega_out"]}
    assert ids == {"o2", "o1r"}                    # o1 discharged, others in
    assert r["discharged"] == ["o1"]


def test_discharging_an_unknown_obligation_is_refused():
    r = conserve_obligations(frozenset(), (DischargeReceipt(
        "r", ("ghost",), "c", "w"),))
    assert r["refused_discharges"][0]["reason"] == "E_DISCHARGE_OF_UNKNOWN"


# ── HF-10..14: the five laundering classes ─────────────────────────────

def test_projection_laundering():
    r = projection_laundering(root_count=1, representation_count=5)
    assert r["laundering"] is True
    assert r["reason"] == "E_PROJECTION_LAUNDERING"
    assert projection_laundering(3, 3)["laundering"] is False


def test_authority_laundering():
    assert authority_laundering(authorized_at=20,
                                effect_at=10)["reason"] == \
        "E_AUTHORITY_LAUNDERING"
    assert authority_laundering(10, 20)["laundering"] is False


def test_state_laundering():
    r = state_laundering(_h_b(), _h_a(), treated_as_never_happened=True)
    assert r["reason"] == "E_STATE_LAUNDERING"
    assert state_laundering(_h_b(), _h_a(), False)["laundering"] is False


def test_learning_laundering():
    assert learning_laundering(succeeded=True)["reason"] == \
        "E_LEARNING_LAUNDERING"
    assert learning_laundering(True, "lease#L1")["laundering"] is False


def test_memory_laundering():
    r = memory_laundering(restatement_count=12)
    assert r["reason"] == "E_MEMORY_LAUNDERING" and r["restatements"] == 12
    assert memory_laundering(12, "operator_admission#1")["laundering"] \
        is False


def test_all_five_classes_share_one_structural_error():
    assert len(hf.LAUNDERING_CLASSES) == 5
    assert "mistakes that change for" in hf.LAUNDERING_COMMON_ERROR


# ── HF-15: the reducer conservation law ────────────────────────────────

THREE_ON_ONE_SOURCE = (
    RawFinding("f1", "X is true", "quote A", "doi:10.1/Q", 0.91),
    RawFinding("f2", "x is true", "quote B", "doi:10.1/Q", 0.72),
    RawFinding("f3", "X IS TRUE", "quote C", "doi:10.1/Q", 0.55),
)


def test_the_reducer_counts_source_roots_not_worker_copies():
    """Three workers on ONE source are ONE witness. The label must say
    so — this is the bug that motivated the law."""
    r = safe_reduce(THREE_ON_ONE_SOURCE)
    note = r["notes"][0]
    assert note["workers"] == 3
    assert note["independent_roots"] == 1
    assert note["corroborated"] is False
    assert "1 independent source" in note["label"]


def test_genuine_corroboration_is_recognized():
    findings = THREE_ON_ONE_SOURCE[:1] + (
        RawFinding("f4", "X is true", "quote D", "doi:10.2/OTHER", 0.6),)
    note = safe_reduce(findings)["notes"][0]
    assert note["independent_roots"] == 2 and note["corroborated"] is True


def test_the_reducer_never_manufactures_provenance():
    r = safe_reduce(THREE_ON_ONE_SOURCE)
    assert r["roots_out"] <= r["roots_in"]
    assert reducer_conservation(r)["verdict"] == "CONSERVING"


def test_manufactured_provenance_is_caught():
    forged = {"roots_in": frozenset({"a"}), "roots_out": frozenset({"a", "b"}),
              "contradictions_in": frozenset(),
              "contradictions_out": frozenset(), "reduced": ()}
    v = reducer_conservation(forged)
    assert v["verdict"] == "E_PROVENANCE_MANUFACTURED"
    assert v["invented_roots"] == ["b"]


def test_contradictions_must_survive_reduction():
    swallowed = {"roots_in": frozenset({"a"}), "roots_out": frozenset({"a"}),
                 "contradictions_in": frozenset({"c1"}),
                 "contradictions_out": frozenset(), "reduced": ()}
    v = reducer_conservation(swallowed)
    assert v["verdict"] == "E_CONTRADICTION_LOST"
    assert v["swallowed"] == ["c1"]


def test_real_contradictions_survive_the_real_reducer():
    findings = (RawFinding("f1", "X is true", "q", "r1", 0.9,
                           contradicts=("f9",)),
                RawFinding("f2", "x is true", "q2", "r2", 0.5))
    r = safe_reduce(findings)
    assert "f9" in r["contradictions_out"]
    assert reducer_conservation(r)["verdict"] == "CONSERVING"


def test_the_reducer_merges_evidence_rather_than_discarding_it():
    r = safe_reduce(THREE_ON_ONE_SOURCE)
    ev = r["reduced"][0].evidence
    assert "quote A" in ev and "quote B" in ev and "quote C" in ev


def test_the_reducer_does_not_mutate_its_input():
    before = tuple(f.evidence for f in THREE_ON_ONE_SOURCE)
    safe_reduce(THREE_ON_ONE_SOURCE)
    safe_reduce(THREE_ON_ONE_SOURCE)               # idempotent
    assert tuple(f.evidence for f in THREE_ON_ONE_SOURCE) == before


# ── the generic bead ───────────────────────────────────────────────────

def test_the_bead_fails_a_system_that_calls_them_equal():
    r = equal_state_different_history_bead(_h_a(), _h_b(),
                                           system_says_equal=True)
    assert r["pi_equal"] is True
    assert r["passed"] is False
    assert r["verdict"] == "E_CAUSAL_ALIASING"


def test_the_bead_passes_a_system_that_distinguishes_them():
    r = equal_state_different_history_bead(_h_a(), _h_b(),
                                           system_says_equal=False)
    assert r["passed"] is True


# ── the registry: every invariant cites a real enforcer ────────────────

def test_fifteen_invariants_each_resolving_to_an_executable():
    assert len(hf.HF_INVARIANTS) == 15
    assert len({i[0] for i in hf.HF_INVARIANTS}) == 15
    mod = importlib.import_module("history_fiber")
    for hid, _claim, enforcer in hf.HF_INVARIANTS:
        obj = mod
        for part in enforcer.split("."):
            assert hasattr(obj, part), (hid, enforcer)
            obj = getattr(obj, part)


def test_deterministic():
    assert hf.canon(safe_reduce(THREE_ON_ONE_SOURCE)["notes"]) == \
        hf.canon(safe_reduce(THREE_ON_ONE_SOURCE)["notes"])
