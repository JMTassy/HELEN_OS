"""Layout cannot become dependency, a classifier cannot mint a route,
a producer cannot approve itself, identical JSON from incompatible
configs is not one artifact, NOT_FOUND is not NO_ACCESS, a join
without a policy is an implicit barrier, persistence is not truth, and
a hundred agents over one source are one witness.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import execution_graph as eg
from execution_graph import (
    collapse_failures,
    dependency_audit,
    deploy_graph,
    edge,
    evidence_roots,
    failure_state,
    hidden_state_falsifier,
    idempotent_write,
    join_policy,
    node_contract,
    output_object,
    pass_payload,
    pipeline_order,
    primitive,
    promotion_step,
    route,
    route_decision,
    run_state,
    same_artifact,
    sizing,
    verification_edge,
)


# ── dependency truth ───────────────────────────────────────────────────

def test_an_edge_that_consumes_nothing_is_typography():
    v = edge("search", "draft", consumes=False)
    assert v["licensed"] is False
    assert v["reason"] == "E_FALSE_EDGE"
    assert v["law"] == "sequence != dependency"
    assert edge("search", "draft", consumes=True)["licensed"] is True
    assert edge("a", "a", True)["reason"] == "E_SELF_EDGE"


def test_the_research_example_is_a_fan_not_a_chain():
    """Four sources, none consuming another, all feeding synthesis:
    written as a chain that is four round trips; the audit shows the
    real width."""
    nodes = ("filings", "papers", "pricing", "commentary", "synthesis")
    written_as_chain = (
        ("filings", "papers", False), ("papers", "pricing", False),
        ("pricing", "commentary", False),
        ("filings", "synthesis", True), ("papers", "synthesis", True),
        ("pricing", "synthesis", True),
        ("commentary", "synthesis", True))
    v = dependency_audit(nodes, written_as_chain)
    assert v["ok"] is True
    assert v["declared_edges"] == 7
    assert v["real_dependencies"] == 4
    assert len(v["false_edges"]) == 3
    assert v["parallel_width_at_start"] == 4      # all four at once


def test_a_node_that_changes_without_consuming_exposes_hidden_state():
    v = hidden_state_falsifier(edge_consumes=False,
                               downstream_changed_when_removed=True)
    assert v["contract_complete"] is False
    assert v["reason"] == "E_HIDDEN_STATE"
    assert hidden_state_falsifier(False, False)["contract_complete"]
    assert hidden_state_falsifier(True, True)["contract_complete"]


# ── contracts ──────────────────────────────────────────────────────────

def test_a_node_needs_all_four_properties():
    ok = node_contract("fetch filings", ("ticker",), {"docs": "list"},
                       ("FOUND", "NOT_FOUND", "NO_ACCESS"))
    assert ok["ok"] is True and ok["swappable"] is True
    assert node_contract("do the thing that fetches filings",
                         ("t",), {"x": 1}, ("FOUND",))["missing"] == \
        ("task_nameable_in_three_words",)
    assert "structured_output" in node_contract(
        "fetch filings", ("t",), None, ("FOUND",))["missing"]
    assert node_contract("fetch filings", ("t",), {"x": 1},
                         ("VIBES",))["unknown_states"] == ("VIBES",)


def test_identical_values_from_different_configs_are_not_one_artifact():
    a = output_object({"n": 3}, "s1", "worker", ("in",),
                      {"temp": 0}, 1)
    b = output_object({"n": 3}, "s1", "worker", ("in",),
                      {"temp": 1}, 2)
    assert a["ok"] and b["ok"]
    assert same_artifact(a, b)["reason"] == "E_CONFIG_COLLISION"
    same = output_object({"n": 3}, "s1", "worker", ("in",),
                         {"temp": 0}, 99)
    assert same_artifact(a, same)["same"] is True   # seq is not identity


def test_an_output_without_provenance_is_refused():
    assert output_object({"n": 1}, None, "w", ("i",), {"c": 1}, 0)[
        "reason"] == "E_UNPROVENANCED_OUTPUT"
    assert output_object({"n": 1}, "s", "w", ("i",), {"c": 1}, -1)[
        "reason"] == "E_UNORDERED_OUTPUT"


def test_not_found_is_not_no_access():
    nf = failure_state("NOT_FOUND")
    na = failure_state("NO_ACCESS")
    assert nf["asserts_absence"] is True
    assert na["asserts_absence"] is False
    assert na["asserts_only_our_blindness"] is True
    assert collapse_failures("NOT_FOUND", "NO_ACCESS")["reason"] == \
        "E_FAILURE_STATE_COLLAPSE"
    assert len(eg.FAILURE_STATES) == 8


# ── primitives ─────────────────────────────────────────────────────────

def test_four_primitives_and_a_cycle_needs_evidence():
    assert eg.PRIMITIVES == ("CHAIN", "FAN", "ROUTER",
                             "CONTROLLED_CYCLE")
    assert primitive("FAN", branches=100)["ok"] is True
    assert primitive("FAN", branches=1)["reason"] == "E_FAN_OF_ONE"
    assert primitive("CONTROLLED_CYCLE")["reason"] == \
        "E_UNCONTROLLED_CYCLE"
    assert primitive("CONTROLLED_CYCLE",
                     terminates_on_evidence="coverage>=tau")["ok"]


# ── joins ──────────────────────────────────────────────────────────────

def test_ninety_six_of_a_hundred_may_continue():
    v = join_policy(settled=96, failed=4, coverage=0.96, tau=0.9)
    assert v["decision"] == "CONTINUE"
    assert v["failed"] == 4


def test_insufficient_coverage_holds_and_contradiction_fails():
    assert join_policy(50, 50, 0.5, 0.9)["decision"] == "HOLD"
    v = join_policy(100, 0, 1.0, 0.9, critical_contradiction=True)
    assert v["decision"] == "FAIL"


def test_a_join_the_next_node_does_not_need_is_a_barrier():
    v = join_policy(10, 0, 1.0, 0.9, next_needs_complete_set=False)
    assert v["reason"] == "E_IMPLICIT_BARRIER"


# ── routing authority ──────────────────────────────────────────────────

TABLE = {"LOW_RISK": "short_path", "HIGH_RISK": "audit_path",
         "UNKNOWN": "HOLD"}


def test_a_classifier_that_picks_the_path_minted_authority():
    v = route("LOW_RISK", "clf-v1", TABLE,
              classifier_selected_path="short_path")
    assert v["reason"] == "E_CLASSIFIER_MINTED_AUTHORITY"
    assert v["law"] == "the model may classify; the graph decides"


def test_the_table_is_deterministic_and_explainable():
    v = route("HIGH_RISK", "clf-v1", TABLE)
    assert v["selected_path"] == "audit_path"
    assert v["rule_id"] == "HIGH_RISK->audit_path"
    assert v["explainable"] is True


def test_unknown_never_falls_through_to_a_happy_path():
    assert route("WEIRD_LABEL", "clf-v1", TABLE)["label"] == "UNKNOWN"
    assert route("UNKNOWN", "clf-v1", TABLE)["selected_path"] == "HOLD"
    bad = {**TABLE, "UNKNOWN": "short_path"}
    assert route("UNKNOWN", "clf-v1", bad)["reason"] == \
        "E_UNKNOWN_ROUTED_TO_DEFAULT"


def test_every_route_is_replayable_after_the_fact():
    v = route_decision("HIGH_RISK", "clf-v1", "HIGH_RISK->audit_path",
                       "audit_path", ("art:1",))
    assert v["answers_why_this_route"] is True
    assert route_decision("HIGH_RISK", None, "r", "p", ("a",))[
        "reason"] == "E_UNREPLAYABLE_ROUTE"


# ── verification and promotion ─────────────────────────────────────────

def test_a_producer_cannot_approve_itself():
    assert verification_edge("worker_a", "worker_a", "VERIFICATION")[
        "reason"] == "E_SELF_APPROVAL"
    assert verification_edge("worker_a", "verifier_b",
                             "VERIFICATION")["ok"] is True


def test_a_late_verifier_lets_belief_destabilize():
    from execution_graph import verification_placement
    ok = verification_placement(unverified_propagation_steps=1,
                                max_latency=2)
    assert ok["ok"] is True and ok["within_bound"] is True
    late = verification_placement(5, max_latency=2)
    assert late["reason"] == "E_DELAYED_VERIFICATION"
    # a terminal node propagates to nothing, so latency is moot
    term = verification_placement(9, max_latency=2, is_terminal=True)
    assert term["ok"] is True


def test_the_promotion_chain_cannot_be_skipped_and_never_reaches_truth():
    assert promotion_step("GENERATION", "VERIFICATION")["ok"] is True
    v = promotion_step("GENERATION", "PERSISTENCE")
    assert v["reason"] == "E_STAGE_SKIPPED"
    assert v["skipped"] == ("VERIFICATION", "ADMISSION")
    t = promotion_step("PERSISTENCE", "TRUTH")
    assert t["reason"] == "E_PERSISTENCE_IS_NOT_TRUTH"


# ── state ──────────────────────────────────────────────────────────────

def test_references_travel_and_transcripts_do_not():
    assert pass_payload("transcript")["reason"] == \
        "E_TRANSCRIPT_PASSED"
    assert pass_payload("reference", ref="art:42")["ok"] is True
    assert pass_payload("reference")["reason"] == \
        "E_DANGLING_REFERENCE"


def test_a_retry_does_not_duplicate_an_artifact():
    s, r1 = idempotent_write({}, "art:1", {"v": 1})
    s2, r2 = idempotent_write(s, "art:1", {"v": 1})
    assert r1["written"] is True and r2["written"] is False
    assert s2 == s
    _, conflict = idempotent_write(s, "art:1", {"v": 2})
    assert conflict["reason"] == "E_CONFLICTING_REWRITE"


def test_the_run_answers_what_why_and_where():
    v = run_state("run1", "g-v1",
                  {"a": "COMPLETED", "b": "RUNNING", "c": "PENDING"},
                  ("art:1",), ({"rule_id": "LOW->short"},),
                  retry_budget=3, token_budget=1000,
                  permissions=("read",), approvals=(), receipts=())
    assert v["ok"] is True
    assert v["completed"] == ("a",) and v["current"] == ("b",)
    assert v["resume_from"] == ("c",)
    assert all(v["answers"].values())
    blind = run_state("run1", "g-v1", {"b": "RUNNING"}, (), (),
                      1, 1, (), (), ())
    assert blind["ok"] is False
    assert blind["reason"] == "E_UNRESUMABLE_RUN"


# ── economics ──────────────────────────────────────────────────────────

def test_a_hundred_agents_over_one_source_are_one_witness():
    v = evidence_roots(100, n_independent_roots=1,
                       same_model_same_source=True)
    assert v["n_effective_witnesses"] == 1
    assert v["consensus_illusion"] is True
    assert v["reason"] == "E_CONSENSUS_ILLUSION"
    real = evidence_roots(100, n_independent_roots=7)
    assert real["n_effective_witnesses"] == 7
    assert real["consensus_illusion"] is False


def test_breadth_must_be_priced_against_all_four_costs():
    val = {1: 10.0, 6: 30.0, 100: 40.0}
    z = lambda n: 0.0                                    # noqa: E731
    assert sizing(val, z, z, z, None)["reason"] == \
        "E_UNPRICED_BREADTH"
    # coordination and verification grow with N: the optimum is not 100
    v = sizing(val, lambda n: 0.1 * n, lambda n: 0.05 * n,
               lambda n: 0.02 * n * n, lambda n: 0.1 * n)
    assert v["ok"] is True
    assert v["n_star"] == 6
    assert v["net_by_n"][100] < v["net_by_n"][6]


def test_sometimes_the_answer_is_one_agent():
    val = {1: 10.0, 6: 10.5}
    v = sizing(val, lambda n: 0.5 * n, lambda n: 0.5 * n,
               lambda n: 0.5 * n, lambda n: 0.5 * n)
    assert v["n_star"] == 1
    assert deploy_graph(True, 1, False, False, False)["use"] == \
        "SINGLE_LOOP"
    g = deploy_graph(False, 12, True, True, True)
    assert g["deploy"] is True
    assert "route_controlled_authority" in g["because"]


def test_the_count_comes_last():
    good = ("TASK", "REAL_DEPENDENCIES", "GRAPH", "CONTRACTS",
            "AUTHORITY_GATES", "AGENT_COUNT")
    assert pipeline_order(good)["licensed"] is True
    v = pipeline_order(("TASK", "AGENT_COUNT"))
    assert v["reason"] == "E_COUNT_BEFORE_SHAPE"
    assert "REAL_DEPENDENCIES" in v["missing_before_count"]


def test_deterministic():
    a = output_object({"n": 1}, "s", "w", ("i",), {"c": 0}, 1)
    b = output_object({"n": 1}, "s", "w", ("i",), {"c": 0}, 1)
    assert eg.canon(a) == eg.canon(b)
