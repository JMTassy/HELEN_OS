"""Adversarial negative tests for NON_INTERFERENCE_MATRIX_V0: the
diagonal is not a free pass, forbidden crossings admit no warrant,
licensed ones demand a verified typed witness, N_eff never implies
roots in either direction, a memory read cannot upgrade status, a
non-bisimilar topology is fine while F* holds, roles are types not
entities, and D_NI = 0 with a moved frontier falsifies the MATRIX.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import non_interference_matrix as nim
from non_interference_matrix import (
    cell,
    chid01_trace,
    chid02_neff,
    chid03_memory,
    chid04_topology,
    chid05_roles,
    evaluate,
    gamma_I,
    in_M_I,
    local_invariant,
    matrix,
    monoid_conditions,
    nim_implies_monoid,
    status,
    warrant_is_not_assertion,
)


# ── three states, not two ──────────────────────────────────────────────

def test_the_matrix_has_three_states_and_is_twelve_squared():
    m = matrix()
    assert m["n_coordinates"] == 12 and m["cells"] == 144
    assert m["counts"]["I"] == 12                 # the diagonal
    assert m["counts"]["L"] == len(nim.LICENSED_CROSSINGS) == 5
    assert m["counts"]["F"] == 144 - 12 - 5
    assert set(nim.CELL_STATES) == {"I", "F", "L"}


def test_forbidden_crossings_admit_no_warrant_at_all():
    c = cell("Q", "A")
    assert c["state"] == "F"
    # even a perfect witness cannot license a structurally barred pair
    v = evaluate([{"source": "Q", "target": "A",
                   "warrant": "W_ANYTHING", "witness": "tok"}])
    assert v["D_NI"] == 1
    assert v["violations"][0]["code"] == "E_FORBIDDEN_INTERFERENCE"


def test_licensed_crossings_demand_the_exact_typed_witness():
    assert cell("A", "X")["required_warrant"] == "W_CAPABILITY_TOKEN"
    wrong = evaluate([{"source": "A", "target": "X",
                       "warrant": "W_MEMORY_COMPRESSION",
                       "witness": "tok"}])
    assert wrong["violations"][0]["code"] == "E_UNLICENSED_CROSSING"
    tokenless = evaluate([{"source": "A", "target": "X",
                           "warrant": "W_CAPABILITY_TOKEN"}])
    assert tokenless["D_NI"] == 1
    ok = evaluate([{"source": "A", "target": "X",
                    "warrant": "W_CAPABILITY_TOKEN",
                    "witness": "kappa:1"}])
    assert ok["admissible"] is True


def test_a_warrant_asserted_is_not_a_warrant_verified():
    v = warrant_is_not_assertion("W_INDEPENDENT_ROOT", verified=False)
    assert v["reason"] == "E_ASSERTED_NOT_VERIFIED"
    assert warrant_is_not_assertion("W_INDEPENDENT_ROOT", True)[
        "licensed"] is True


# ── correction 2: the diagonal is NOT a free pass ──────────────────────

def test_authority_escalating_inside_its_own_coordinate_is_caught():
    v = local_invariant("A", {"level": 1}, {"level": 3})
    assert v["reason"] == "E_LOCAL_AUTHORITY_ESCALATION"
    # and the engine counts it as D_local, not D_cross
    e = evaluate([{"source": "A", "target": "A",
                   "before": {"level": 1}, "after": {"level": 3}}])
    assert e["D_local"] == 1 and e["D_cross"] == 0
    assert e["admissible"] is False
    delegated = evaluate([{"source": "A", "target": "A",
                           "before": {"level": 1}, "after": {"level": 3},
                           "warrant": "W_AUTHORITY_DELEGATION"}])
    assert delegated["admissible"] is True


def test_evidence_corrupted_while_still_called_evidence_is_caught():
    v = local_invariant("E", {"root": "rho1"}, {"root": "rho9"})
    assert v["reason"] == "E_LOCAL_EVIDENCE_CORRUPTION"


def test_the_other_local_invariants_bite():
    assert local_invariant("RHO_E", {"count": 1}, {"count": 4})[
        "reason"] == "E_LOCAL_ROOT_INFLATION"
    assert local_invariant("X", {"effects": 0}, {"effects": 1})[
        "reason"] == "E_LOCAL_NON_IDEMPOTENT_EFFECT"
    assert local_invariant("R", {"replayable": True},
                           {"replayable": False})["reason"] == \
        "E_LOCAL_REPLAY_LOST"
    assert local_invariant("X", {"effects": 0},
                           {"effects": 1,
                            "idempotency_key": "k"})["ok"] is True


def test_d_ni_is_the_sum_of_both_defect_classes():
    e = evaluate([
        {"source": "Q", "target": "A"},                  # cross
        {"source": "A", "target": "A",
         "before": {"level": 1}, "after": {"level": 5}},  # local
    ])
    assert e["D_cross"] == 1 and e["D_local"] == 1
    assert e["D_NI"] == 2 and e["admissible"] is False


# ── correction 3: covariance does not speak about roots ────────────────

def test_n_eff_does_not_imply_roots_in_either_direction():
    # N_eff = 1 with a genuinely new independent root: LEGAL
    a = chid02_neff(cov_rank=1, n_workers=50, delta_rho_e=1,
                    independent_root_witness="W_INDEPENDENT_ROOT")
    assert a["N_eff"] == 1 and a["ok"] is True
    # N_eff = 7 does NOT supply a root
    b = chid02_neff(cov_rank=7, n_workers=50, delta_rho_e=1)
    assert b["N_eff"] == 7
    assert b["reason"] == "E_ROOT_WITHOUT_WITNESS"
    assert b["n_eff_implies_roots"] is False
    # the honest zero case
    c = chid02_neff(cov_rank=1, n_workers=100, delta_rho_e=0)
    assert c["ok"] is True and c["N_eff"] == 1


# ── correction 4: memory is not a proof DAG ────────────────────────────

ITEM = {"value": "v", "root": "rho1", "tau_persist": 10,
        "scope": "T1", "status": "HYPOTHESIS"}


def test_a_memory_read_cannot_upgrade_what_it_reads():
    v = chid03_memory(ITEM, "read", status_rank_before=1,
                      status_rank_after=3)
    assert v["reason"] == "E_READ_UPGRADED_STATUS"
    ok = chid03_memory(ITEM, "read", 1, 1)
    assert ok["ok"] is True


def test_an_ungoverned_memory_item_is_refused():
    v = chid03_memory({"value": "v"}, "read", 1, 1)
    assert v["reason"] == "E_UNGOVERNED_MEMORY_ITEM"
    assert "status" in v["missing"] and "root" in v["missing"]


# ── correction 5: bisimilarity is not the requirement ──────────────────

def test_a_non_bisimilar_topology_is_fine_while_the_frontier_holds():
    v = chid04_topology(bisimilar=False, frontier_preserved=True)
    assert v["permitted"] is True and v["bisimilar"] is False
    bad = chid04_topology(bisimilar=True, frontier_preserved=False)
    assert bad["reason"] == "E_TOPOLOGY_CHANGED_FRONTIER"


# ── correction 6: roles are types, not entities ────────────────────────

def test_one_principal_may_hold_several_roles_but_types_stay_distinct():
    same = chid05_roles("p1", "p1", "p1", roles_typed=True,
                        kappa_valid=True)
    assert same["ok"] is True and same["same_principal"] is True
    untyped = chid05_roles("p1", "p2", "p3", roles_typed=False)
    assert untyped["reason"] == "E_ROLES_UNTYPED"
    nokappa = chid05_roles("p1", "p2", "p3", roles_typed=True,
                           kappa_valid=False)
    assert nokappa["reason"] == "E_TOOLCALL_WITHOUT_KAPPA"
    assert nokappa["same_principal_permitted"] is True


# ── CHID-01 ────────────────────────────────────────────────────────────

def test_a_fully_compliant_trace_can_still_be_inadmissible():
    v = chid01_trace(local_steps_ok=True, global_valid=False)
    assert v["admissible"] is False
    assert v["reason"] == "E_TRACE_COMPLIANT_STATE_INADMISSIBLE"
    assert chid01_trace(True, True)["admissible"] is True


# ── correction 7: the monoid hierarchy with its conditions ─────────────

def test_M_I_is_a_monoid_only_with_identity_and_closure():
    assert monoid_conditions(True, True)["is_monoid"] is True
    assert monoid_conditions(False, True)["reason"] == "E_NO_IDENTITY"
    assert monoid_conditions(True, False)["reason"] == "E_NOT_CLOSED"


def test_gamma_I_is_the_reversible_sector_not_all_of_M_I():
    F = {"acoustic": "MEASURED"}
    assert in_M_I(F, dict(F))["in_M_I"] is True
    assert in_M_I(F, {"acoustic": "WARRANTED"})["reason"] == \
        "E_FRONTIER_MOVED"
    non_unit = gamma_I(t_in_M_I=True, inverse_exists=False,
                       inverse_in_M_I=False)
    assert non_unit["in_Gamma_I"] is False
    assert non_unit["reason"] == "E_NOT_INVERTIBLE"
    unit = gamma_I(True, True, True)
    assert unit["in_Gamma_I"] is True
    assert "M_I" in unit["hierarchy"]


def test_zero_defect_with_a_moved_frontier_falsifies_the_matrix():
    """The self-falsifier: if D_NI = 0 but F* moved, a leakage channel
    is MISSING from the matrix — the specification is wrong, not the
    run."""
    v = nim_implies_monoid(0, {"a": 1}, {"a": 2})
    assert v["consistent"] is False
    assert v["reason"] == "E_MATRIX_INCOMPLETE"
    good = nim_implies_monoid(0, {"a": 1}, {"a": 1})
    assert good["consistent"] is True
    conservative = nim_implies_monoid(3, {"a": 1}, {"a": 1})
    assert conservative["consistent"] is True


# ── status discipline ──────────────────────────────────────────────────

def test_this_is_a_conjecture_not_a_sealed_theorem():
    s = status()
    assert s["status"] == "ARCHITECTURAL_CONJECTURE"
    assert s["sealed_theorem"] is False
    assert s["authority"] is False and s["canon"] is False
    assert "PROBLEM SPACE" in s["note"]


def test_deterministic():
    assert nim.canon(matrix()) == nim.canon(matrix())
