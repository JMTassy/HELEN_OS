"""TEST 1, executed: PASS/PASS locally and FAIL globally on the
double-spend, with MUTATIONS_COMMITTED = 0. Plus the positive control
that keeps it non-vacuous — one mint, one invoke, and the same checker
says PASS.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import global_admissibility as ga
from global_admissibility import (
    I1_linear_capability,
    I2_foundationally_acyclic,
    I3_no_self_supporting_root,
    I4_temporal_persistence,
    attack_coverage,
    fixture_double_spend,
    fixture_grounded_chain,
    fixture_honest_spend,
    fixture_self_support,
    fixture_status,
    fixture_temporal_gap,
    fixture_warranted_transport,
    gedge,
    global_validate,
    local_validate,
    registration,
    undeclared_influence,
    use_count,
)


# ── T_G1: the whole point, in one assertion ────────────────────────────

def test_every_edge_of_the_double_spend_is_locally_valid():
    """Non-vacuity. If a local validator could catch this, the fixture
    would prove nothing."""
    for e in fixture_double_spend():
        v = local_validate(e)
        assert v["verdict"] == ga.PASS
        assert v["reasons"] == []


def test_local_valid_everywhere_does_not_entail_global_valid():
    g = global_validate(fixture_double_spend())
    assert g["LOCAL_EDGE_RESULTS"] == ("PASS", "PASS", "PASS")
    assert g["all_edges_locally_valid"] is True
    assert g["GLOBAL_RESULT"] == ga.FAIL
    assert g["REASON"] == "CAPABILITY_DOUBLE_SPEND"
    assert g["MUTATIONS_COMMITTED"] == 0
    assert g["gap_witnessed"] is True


def test_the_arithmetic_is_use_count_two_over_max_one():
    edges = fixture_double_spend()
    assert use_count(edges, "kappa") == 2
    v = I1_linear_capability(edges, max_use=1)
    assert v["verdict"] == ga.FAIL
    assert v["use_counts"]["kappa"] == 2
    assert v["overspent"] == {"kappa": 2}


def test_one_mint_one_invoke_passes_globally():
    """The positive control: I_1 refuses the DOUBLE, not the spend.
    Without this, 'never invoke anything' would score perfectly."""
    g = global_validate(fixture_honest_spend())
    assert g["GLOBAL_RESULT"] == ga.PASS
    assert g["REASON"] is None
    assert g["gap_witnessed"] is False


def test_a_locally_invalid_edge_is_a_different_failure():
    """When the local checker DOES catch it, gap_witnessed is false —
    that case proves nothing about global composition."""
    edges = (gedge("A", "k", ga.MINT, token="k"),
             gedge("k", "E", ga.INVOKE, token="k", scope_ok=False))
    g = global_validate(edges)
    assert g["all_edges_locally_valid"] is False
    assert g["gap_witnessed"] is False


def test_raising_max_use_makes_the_double_spend_lawful():
    v = I1_linear_capability(fixture_double_spend(), max_use=2)
    assert v["verdict"] == ga.PASS


def test_an_empty_graph_is_refused():
    with pytest.raises(ValueError, match="E_EMPTY_GRAPH"):
        global_validate(())


# ── T_G2: epistemic self-support, not merely a cycle ───────────────────

def test_a_provenance_cycle_with_no_root_is_self_supporting():
    v = I3_no_self_supporting_root(fixture_self_support(),
                                   roots=frozenset())
    assert v["verdict"] == ga.FAIL
    assert v["reason"] == "FAIL_PROVENANCE_SELF_SUPPORT"
    assert v["self_supporting_claims"] == ("c1", "c2", "c3")


def test_a_grounded_chain_of_the_same_length_passes():
    v = I3_no_self_supporting_root(fixture_grounded_chain(),
                                   roots=frozenset({"r"}))
    assert v["verdict"] == ga.PASS


def test_the_criterion_is_no_root_not_the_presence_of_a_cycle():
    """The sharpened predicate: a cycle that DOES reach an independent
    root is not self-support. 'A cycle exists' would wrongly fail this,
    and cycles across research epochs are lawful."""
    edges = fixture_self_support() + (gedge("r", "c1", ga.DERIVE),)
    v = I3_no_self_supporting_root(edges, roots=frozenset({"r"}))
    assert v["verdict"] == ga.PASS


def test_a_claim_with_no_support_at_all_is_not_self_support():
    v = I3_no_self_supporting_root((gedge("r", "c", ga.DERIVE),),
                                   roots=frozenset({"r"}))
    assert "r" not in v["self_supporting_claims"]


def test_the_cycle_is_still_reported_by_the_acyclicity_invariant():
    v = I2_foundationally_acyclic(fixture_self_support())
    assert v["verdict"] == ga.FAIL
    assert v["reason"] == "E_DERIVATION_CYCLE"


def test_acyclicity_is_exact_at_any_depth():
    """Kahn in integer arithmetic. The relayed engine's
    max|eigenvalue| > 1e-5 test misreports long DAGs as cyclic,
    because a nilpotent adjacency matrix is the worst possible
    conditioning for eigenvalues."""
    for n in (5, 40, 200):
        chain = tuple(gedge(f"n{i}", f"n{i+1}", ga.DERIVE)
                      for i in range(n))
        v = I2_foundationally_acyclic(chain)
        assert v["verdict"] == ga.PASS, f"depth {n}"
        assert len(v["topological_order"]) == n + 1


# ── T_G3: transport without a connection is UNDEFINED ──────────────────

def test_a_temporal_crossing_without_a_warrant_is_undefined():
    v = I4_temporal_persistence(fixture_temporal_gap())
    assert v["verdict"] == ga.UNDEFINED
    assert v["reason"] == "FAIL_TEMPORAL_PERSISTENCE"


def test_undefined_transport_holds_the_graph_it_does_not_deny_it():
    g = global_validate(fixture_temporal_gap())
    assert g["GLOBAL_RESULT"] == ga.UNDEFINED
    assert g["GLOBAL_RESULT"] != ga.FAIL


def test_a_warranted_transport_passes():
    assert I4_temporal_persistence(fixture_warranted_transport())[
        "verdict"] == ga.PASS


def test_a_failure_outranks_an_undefined():
    g = global_validate(fixture_double_spend() +
                        fixture_temporal_gap())
    assert g["GLOBAL_RESULT"] == ga.FAIL
    assert g["REASON"] == "CAPABILITY_DOUBLE_SPEND"


# ── status discipline ──────────────────────────────────────────────────

def test_a_passing_fixture_licenses_a_claim_about_that_fixture():
    v = fixture_status(1, 3)
    assert v["TEST_FIXTURE"] == "VERIFIED_ON_EXECUTED_FIXTURE"
    assert v["ENGINE"] == "PARTIALLY_WITNESSED"
    assert v["delta_gamma"] == 0


def test_an_agenda_is_registered_not_admitted():
    v = registration(n_epochs=20, promotions=0)
    assert v["status"] == "REGISTERED_PRECLAIM_AGENDA"
    assert v["delta_gamma"] == 0 and v["canon"] is False


def test_a_promotion_count_needs_a_gamma_receipt():
    assert registration(20, 1)["status"] == \
        "E_UNWITNESSED_PROMOTION_CLAIM"


# ── the two corrected formulations ─────────────────────────────────────

def test_a_redundant_attacker_adds_no_coverage():
    same = (("s1", "s2"), ("s1", "s2"), ("s1", "s2"))
    v = attack_coverage(same)
    assert v["n_HAL"] == 3
    assert v["coverage_attack"] == 2
    assert v["N_HAL_entails_more_witness"] is False


def test_a_genuinely_new_surface_does_raise_coverage():
    v = attack_coverage((("s1",), ("s2",), ("s3",)))
    assert v["coverage_attack"] == 3


def test_the_proposer_may_write_the_declared_interface():
    v = undeclared_influence(("candidate_hash", "contracted_data"))
    assert v["ok"] is True
    assert v["influence_undeclared"] == 0


def test_the_proposer_may_not_touch_the_policy_set_or_the_evaluator():
    v = undeclared_influence(("candidate_hash", "policy_set",
                              "evaluator"))
    assert v["ok"] is False
    assert v["reason"] == "E_UNDECLARED_INFLUENCE"
    assert v["protected_surface_breached"] == ("evaluator", "policy_set")


def test_deterministic():
    assert ga.canon(global_validate(fixture_double_spend())) == \
        ga.canon(global_validate(fixture_double_spend()))


# ── I_5: warrant-value rebind (CHID-SMITH-1793, gap witnessed then closed)

def test_the_rebind_passed_the_four_prior_invariants():
    """The witness of the gap, preserved as a test: every edge is
    locally valid and I_1..I_4 all PASS on the rebind fixture. Only
    I_5 sees it. (Witnessed live against commit 92f01d5, where
    global_validate wrongly returned PASS.)"""
    from global_admissibility import (I5_warrant_binding,
                                      fixture_warrant_rebind)
    edges = fixture_warrant_rebind()
    for e in edges:
        assert local_validate(e)["verdict"] == ga.PASS
    assert I1_linear_capability(edges)["verdict"] == ga.PASS
    assert I2_foundationally_acyclic(edges)["verdict"] == ga.PASS
    assert I4_temporal_persistence(edges)["verdict"] == ga.PASS
    v = I5_warrant_binding(edges)
    assert v["verdict"] == ga.FAIL
    assert v["reason"] == "E_WARRANT_VALUE_REBIND"
    assert v["rebound_edges"] == ("kappa2->E_2",)


def test_global_validate_now_refuses_the_rebind():
    from global_admissibility import fixture_warrant_rebind
    g = global_validate(fixture_warrant_rebind())
    assert g["all_edges_locally_valid"] is True
    assert g["GLOBAL_RESULT"] == ga.FAIL
    assert g["REASON"] == "E_WARRANT_VALUE_REBIND"
    assert g["gap_witnessed"] is True


def test_the_honest_warrant_pair_still_passes():
    """Positive control: I_5 refuses the REBIND, not the warrant."""
    from global_admissibility import fixture_honest_warrant
    g = global_validate(fixture_honest_warrant())
    assert g["GLOBAL_RESULT"] == ga.PASS


def test_an_unwarranted_edge_is_not_i5_business():
    from global_admissibility import I5_warrant_binding
    assert I5_warrant_binding(fixture_double_spend())["verdict"] == \
        ga.PASS
