"""The minimality witnesses, executed: for each ceiling C_i, one delta
that violates ONLY C_i, satisfies the other three, is Invalid — and is
ADMITTED the moment C_i is removed from the basis. Plus the
compositional-closure attack, survived. Verdict stated no stronger
than earned: evidence over the tested domain, never proof.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
import minimality as mn
from minimality import (
    CEILINGS,
    RECEIPT,
    admit_without,
    basis_verdict,
    check_witness,
    irreducibility,
    minimality_witnesses,
    run_compositional_attack,
)


# ── the witness condition, per ceiling ──────────────────────────────────

def test_every_ceiling_has_a_witness():
    covered = sorted(w["target_ceiling"] for w in minimality_witnesses())
    assert covered == sorted(CEILINGS)


def test_each_witness_violates_only_its_target_ceiling():
    for w in minimality_witnesses():
        c = check_witness(w)
        assert c["violates_only_target"] is True, c["target_ceiling"]
        assert c["others_hold"] is True, c["target_ceiling"]


def test_each_witness_is_invalid_with_a_named_harm():
    for w in minimality_witnesses():
        c = check_witness(w)
        assert c["invalid"] is True
        assert c["invalid_because"]                       # harm is named
        assert w["harm_class_witnessed_in_project_history"]


def test_the_full_gate_rejects_every_witness():
    for w in minimality_witnesses():
        v = ca.admit(w["delta"], RECEIPT)
        assert v["verdict"] == "REJECT"
        assert {b["ceiling"] for b in v["breaches"]} == \
            {w["target_ceiling"]}


# ── the irreducibility payload: ablation admits the invalid delta ───────

def test_dropping_the_target_ceiling_admits_its_invalid_witness():
    """The core of minimality: remove C_i and delta_i walks in."""
    for w in minimality_witnesses():
        abl = admit_without(w["delta"], RECEIPT, w["target_ceiling"])
        assert abl["verdict"] == "ADMIT", w["target_ceiling"]
        assert abl["full_gate_verdict"] == "REJECT"


def test_dropping_any_other_ceiling_still_rejects_the_witness():
    """No other ceiling was doing C_i's work: delta_i is caught only
    by C_i, so ablating C_j (j != i) changes nothing."""
    for w in minimality_witnesses():
        for other in CEILINGS:
            if other == w["target_ceiling"]:
                continue
            assert admit_without(w["delta"], RECEIPT, other)["verdict"] \
                == "REJECT"


def test_the_ablated_gate_refuses_an_unknown_ceiling():
    import pytest
    with pytest.raises(ValueError, match="E_UNKNOWN_CEILING"):
        admit_without(minimality_witnesses()[0]["delta"], RECEIPT,
                      "TIME")


def test_irreducibility_holds_over_the_tested_domain():
    irr = irreducibility()
    assert irr["every_ceiling_witnessed"] is True
    assert irr["each_ablation_admits_its_invalid_witness"] is True
    assert irr["irreducible_over_tested_domain"] is True
    assert irr["grade"] == "EVIDENCE_NOT_PROOF"


# ── the compositional-closure attack, survived ──────────────────────────

def test_the_compositional_attack_is_survived():
    comp = run_compositional_attack()
    assert comp["survived"] is True
    assert comp["fifth_ceiling_earned"] is False
    assert sorted(a["ceiling"] for a in comp["attacks"]) == \
        sorted(CEILINGS)
    for a in comp["attacks"]:
        assert a["compositional_gap"] is True         # the gap is real
        assert a["caught_transactionally"] is True    # and caught


# ── the combined verdict, stated no stronger than earned ────────────────

def test_the_basis_verdict_is_earned_and_bounded():
    v = basis_verdict()
    assert v["verdict"] == ("FOUR_CEILING_BASIS_IRREDUCIBLE_AND_"
                            "COMPOSITIONALLY_ADEQUATE_OVER_TESTED_DOMAIN")
    assert v["irreducible_over_tested_domain"] is True
    assert v["compositionally_adequate_over_tested_domain"] is True
    # the bound is stated, not hidden
    assert v["grade"] == "EVIDENCE_NOT_PROOF"
    assert v["completeness"] == "UNKNOWN"
    assert "does not entail Impossible" in v["domain_bound"]


def test_the_three_preserved_primitives_are_named():
    v = basis_verdict()
    assert len(v["preserved_primitives"]) == 3
    joined = " ".join(v["preserved_primitives"])
    assert "four-ceiling admission" in joined
    assert "generation/admission separation" in joined
    assert "witness supremacy" in joined
    # witness supremacy's possible derivability is recorded, not resolved
    assert "open question" in joined


def test_a_broken_witness_would_break_the_verdict():
    """Mutation check: a delta that breaches TWO ceilings is not a
    minimality witness — check_witness must say so."""
    bad = {"target_ceiling": "PROOF",
           "delta": ca.Transition("d_bad",
                                  frozenset({"root_R", "root_FORGED"}),
                                  frozenset({"obj_A", "obj_FOREIGN"}),
                                  "REPORTED", True),
           "invalid_because": "two breaches",
           "harm_class_witnessed_in_project_history": "n/a"}
    c = check_witness(bad)
    assert c["violates_only_target"] is False
    assert c["witness_holds"] is False
    # and ablating PROOF does NOT admit it — SCOPE still catches it
    assert c["ablation_verdicts"]["PROOF"] == "REJECT"


def test_deterministic():
    assert mn.canon(basis_verdict()) == mn.canon(basis_verdict())
    assert mn.canon(irreducibility()) == mn.canon(irreducibility())
