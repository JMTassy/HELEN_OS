r"""OBLITERATUS compiled into the governed execution graph — the
reference specimen for T-GRAPH-001. The 'before' is the naive serial
prose (targeted tests chained, replays serial); the 'after' is the
audited topology (targeted fan, replay pair parallel). Both are typed;
the auditor computes the witness.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The one authority fact that must hold across the optimization: only
VERIFY_RECEIPT admits PASS. compare_runs never promotes. The fan and
the parallel replays change wall-clock, never who may promote.
"""
from __future__ import annotations

import graph_audit as ga


def _node(nid, job, cost="STANDARD", **kw):
    n = {"id": nid, "job": job, "inputs": kw.pop("inputs", []),
         "outputs": kw.pop("outputs", [nid.lower()]),
         "output_schema": kw.pop("output_schema", f"{nid}_schema"),
         "failure_states": kw.pop("failure_states",
                                  ["EXECUTION_ERROR"]),
         "capabilities": kw.pop("capabilities", []),
         "side_effects": kw.pop("side_effects", []),
         "cost_class": cost}
    n.update(kw)
    return n


N_TARGETED = 4


def _common_nodes():
    """The nodes shared by before and after. Only VERIFY_RECEIPT is
    consequential+admitting; it carries a separate verifier principal.
    Nodes that write run state carry a resume contract; nothing here
    has an external side effect, so no idempotency keys are required
    (the audit only demands them of effect nodes)."""
    nodes = [
        _node("FREEZE", "freeze experiment", writes_state=True,
              resume={"key": "bid"}, outputs=["frozen", "bid"]),
        _node("BASELINE", "run baseline", cost="STRONG",
              writes_state=True, resume={"key": "raw_base"},
              inputs=["frozen"], outputs=["raw_base"]),
        _node("SCORE_BASELINE", "score baseline", inputs=["raw_base"],
              outputs=["score_base"]),
        _node("CLUSTER", "cluster failures", inputs=["score_base"],
              outputs=["clusters"]),
        _node("SELECT_SURGERY", "select one surgery",
              inputs=["clusters"], outputs=["surgery"]),
        _node("FULL_CORPUS", "full corpus run", cost="STRONG",
              writes_state=True, resume={"key": "raw_cand"},
              inputs=["surgery", "evidence"], outputs=["raw_cand"]),
        _node("SCORE", "score candidate", inputs=["raw_cand"],
              outputs=["score_cand"]),
        _node("COMPARE_RUNS", "compare runs",
              inputs=["score_cand", "score_base"],
              outputs=["comparison"]),
        _node("REPLAY_1", "replay one", cost="STRONG",
              writes_state=True, resume={"key": "replay1"},
              inputs=["comparison"], outputs=["r1"]),
        _node("REPLAY_2", "replay two", cost="STRONG",
              writes_state=True, resume={"key": "replay2"},
              inputs=["comparison"], outputs=["r2"]),
        _node("VERIFY_RECEIPT", "verify receipt",
              inputs=["r1", "r2"], outputs=["verdict"],
              consequential=True, principal="verifier_seat",
              verifier="VERIFY_RECEIPT_JUDGE",
              verifier_principal="admission_seat",
              admission_boundary="PASS|HOLD|REVERT"),
    ]
    for i in range(1, N_TARGETED + 1):
        nodes.append(_node(f"TARGETED_{i}", "targeted test",
                           inputs=["surgery"], outputs=[f"t{i}"],
                           evidence_root=f"cluster_probe_{i}"))
    return nodes


def _edges_common():
    return [
        {"from": "FREEZE", "to": "BASELINE", "consumes": ["frozen"],
         "dependency_type": "DATA"},
        {"from": "BASELINE", "to": "SCORE_BASELINE",
         "consumes": ["raw_base"], "dependency_type": "DATA"},
        {"from": "SCORE_BASELINE", "to": "CLUSTER",
         "consumes": ["score_base"], "dependency_type": "DATA"},
        {"from": "CLUSTER", "to": "SELECT_SURGERY",
         "consumes": ["clusters"], "dependency_type": "DATA"},
        {"from": "FULL_CORPUS", "to": "SCORE",
         "consumes": ["raw_cand"], "dependency_type": "DATA"},
        {"from": "SCORE", "to": "COMPARE_RUNS",
         "consumes": ["score_cand"], "dependency_type": "DATA"},
        # COMPARE_RUNS -> VERIFY is real, but runs THROUGH the replays;
        # comparison feeds each replay, replays feed verify.
        {"from": "COMPARE_RUNS", "to": "REPLAY_1",
         "consumes": ["comparison"], "dependency_type": "DATA"},
        {"from": "COMPARE_RUNS", "to": "REPLAY_2",
         "consumes": ["comparison"], "dependency_type": "DATA"},
        {"from": "REPLAY_1", "to": "VERIFY_RECEIPT",
         "consumes": ["r1"], "dependency_type": "DATA"},
        {"from": "REPLAY_2", "to": "VERIFY_RECEIPT",
         "consumes": ["r2"], "dependency_type": "DATA"},
        # SELECT feeds every targeted test (fan) and the full corpus.
        {"from": "SELECT_SURGERY", "to": "FULL_CORPUS",
         "consumes": ["surgery"], "dependency_type": "DATA"},
    ]


def before_graph():
    """Naive prose: targeted tests are chained (each 'after' the last,
    consuming nothing from it), and REPLAY_2 waits on REPLAY_1. Those
    are the false edges the audit will find."""
    nodes = _common_nodes()
    edges = _edges_common()
    for i in range(1, N_TARGETED + 1):
        edges.append({"from": "SELECT_SURGERY", "to": f"TARGETED_{i}",
                      "consumes": ["surgery"], "dependency_type": "DATA"})
        edges.append({"from": f"TARGETED_{i}", "to": "FULL_CORPUS",
                      "consumes": [f"t{i}"], "dependency_type": "DATA"})
    # FALSE serial edges between targeted tests (sequence, not data):
    for i in range(1, N_TARGETED):
        edges.append({"from": f"TARGETED_{i}", "to": f"TARGETED_{i + 1}",
                      "consumes": [], "dependency_type": "DATA"})
    # FALSE serial edge forcing replay_2 after replay_1:
    edges.append({"from": "REPLAY_1", "to": "REPLAY_2",
                  "consumes": [], "dependency_type": "DATA"})
    return ga.build_graph(nodes, edges,
                          joins=_joins(), routes=_routes())["G"]


def after_graph():
    """Audited: targeted tests fan (no inter-edges), replays parallel.
    Same nodes, same real edges, false edges deleted."""
    nodes = _common_nodes()
    edges = _edges_common()
    for i in range(1, N_TARGETED + 1):
        edges.append({"from": "SELECT_SURGERY", "to": f"TARGETED_{i}",
                      "consumes": ["surgery"], "dependency_type": "DATA"})
        edges.append({"from": f"TARGETED_{i}", "to": "FULL_CORPUS",
                      "consumes": [f"t{i}"], "dependency_type": "DATA"})
    return ga.build_graph(nodes, edges,
                          joins=_joins(), routes=_routes())["G"]


def _joins():
    return [
        {"id": "JOIN_targeted", "at_node": "FULL_CORPUS",
         "required_inputs": [f"t{i}" for i in range(1, N_TARGETED + 1)],
         "minimum_coverage": 1.0, "failure_policy": "HOLD",
         "timeout_policy": "HOLD", "next_needs_complete_set": True},
        {"id": "JOIN_replay", "at_node": "VERIFY_RECEIPT",
         "required_inputs": ["r1", "r2"], "minimum_coverage": 1.0,
         "failure_policy": "HOLD", "timeout_policy": "HOLD",
         "next_needs_complete_set": True},
    ]


def _routes():
    return [
        {"id": "R_verdict", "classifier_output": "comparison",
         "deterministic_rule": "acceptance_gate",
         "destination": "PASS|HOLD|REVERT",
         "model_controlled_destination": False},
    ]


# the observational contract: identical across before/after — same
# schema, same business state, same admitted effect (only VERIFY may
# emit PASS), same policy decisions, same required evidence.
def obs_contract():
    return {"schema": "OBLITERATUS_RESULT_V1",
            "business_state": "frozen_thresholds+corpus",
            "admitted_effects": ("PASS_emitted_only_by_verify_receipt",),
            "policy_decisions": ("two_run_replay_required",
                                 "compare_never_promotes"),
            "required_evidence": ("frozen_bid", "two_replays",
                                  "rederived_metrics")}
