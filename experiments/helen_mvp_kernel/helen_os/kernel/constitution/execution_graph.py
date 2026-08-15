r"""Execution Graph — topology separated from cognition AND from
authority. GRAPH_DEPENDENCY_TRUTH as executable refusals.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: CANDIDATE_DOCTRINE (the operator's grade; nothing here is
canon). This module does not schedule work — it says which graphs are
LICENSED, and refuses the ones that launder layout into dependency or
classification into authority.

The founding law:

    edge(u, v)  iff  v actually consumes u's artifact or decision

Everything else in a diagram is typography. Parallelism is bought by
DELETING false edges, not by multiplying personas:

    parallelism = independent executable work / false dependencies

WHAT THIS MODULE REFUSES:
- an edge whose downstream node consumes nothing (E_FALSE_EDGE), and
  the falsifier: if deleting a non-consuming edge changes the
  downstream result, the graph has hidden state (E_HIDDEN_STATE) and
  its contract is incomplete
- a node without task/input/output-schema/named failures
  (E_UNCONTRACTED_NODE)
- a structured output with no identity: two byte-identical JSON
  values produced under different configs are NOT the same artifact
  (E_UNPROVENANCED_OUTPUT, E_CONFIG_COLLISION)
- collapsing epistemically distinct failures: NOT_FOUND is not
  NO_ACCESS is not TOOL_FAILURE (E_FAILURE_STATE_COLLAPSE)
- a join with no policy — "wait for the results" is not a policy
  (E_IMPLICIT_BARRIER); 96 of 100 branches may continue when the
  missing 4 are not required by the next decision
- a classifier that selects the path instead of emitting a label
  (E_CLASSIFIER_MINTED_AUTHORITY); UNKNOWN routes to HOLD/human, never
  to a default happy path (E_UNKNOWN_ROUTED_TO_DEFAULT)
- producer == approver on a verification edge (E_SELF_APPROVAL)
- passing retold transcripts instead of artifact references
  (E_TRANSCRIPT_PASSED); non-idempotent writes (E_DUPLICATE_ON_RETRY)
- a run that cannot answer WHAT happened / WHY this route / WHERE to
  resume (E_UNRESUMABLE_RUN)
- N agents over one evidence root sold as N witnesses
  (E_CONSENSUS_ILLUSION)
- breadth deployed without pricing coordination and verification
  (E_UNPRICED_BREADTH)

Determinism note (a real deviation from the source's O_n tuple): the
provenance object carries a LOGICAL sequence, not a wall-clock
timestamp. Wall-clock in the reducer zone would break replay, and the
identity job — distinguishing artifacts produced under different
conditions — is done by (producer, inputs, config), not by the clock.
"""
from __future__ import annotations

import hashlib
import json

PRIMITIVES = ("CHAIN", "FAN", "ROUTER", "CONTROLLED_CYCLE")

# not_found as a value is necessary but not sufficient: these are
# epistemically distinct and a graph that collapses them routes wrong.
FAILURE_STATES = ("FOUND", "NOT_FOUND", "NO_ACCESS", "TIMEOUT",
                  "TOOL_FAILURE", "INVALID_OUTPUT",
                  "INSUFFICIENT_EVIDENCE", "CONTRADICTED")

# the promotion chain — each transition needs its OWN contract
PROMOTION_CHAIN = ("GENERATION", "VERIFICATION", "ADMISSION",
                   "PERSISTENCE", "TRUTH")

ROUTE_LABELS = ("LOW_RISK", "HIGH_RISK", "UNKNOWN")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


# ── 1. dependency truth ────────────────────────────────────────────────

def edge(u: str, v: str, consumes: bool) -> dict:
    """An edge is licensed only when v reads what u produced. Sequence
    is not dependency; the rest is page layout costing wall-clock."""
    if u == v:
        return {"licensed": False, "reason": "E_SELF_EDGE"}
    if not consumes:
        return {"licensed": False, "reason": "E_FALSE_EDGE",
                "law": "sequence != dependency"}
    return {"licensed": True, "edge": (u, v)}


def dependency_audit(nodes, edges) -> dict:
    """edges: ((u, v, consumes), ...). Returns the real dependency
    graph and what parallel width the deletion buys — the step that
    must happen BEFORE choosing an agent count."""
    real, false_edges = [], []
    for (u, v, consumes) in edges:
        if u not in nodes or v not in nodes:
            return {"ok": False, "reason": "E_UNKNOWN_NODE",
                    "edge": (u, v)}
        (real if consumes else false_edges).append((u, v))
    # a node with no real upstream can start immediately
    has_real_parent = {v for (_u, v) in real}
    startable = tuple(sorted(n for n in nodes
                             if n not in has_real_parent))
    return {"ok": True,
            "declared_edges": len(edges),
            "real_dependencies": len(real),
            "false_edges": tuple(sorted(false_edges)),
            "parallel_width_at_start": len(startable),
            "startable": startable,
            "law": "parallelism comes from deleting false "
                   "dependencies, not multiplying personas"}


def hidden_state_falsifier(edge_consumes: bool,
                           downstream_changed_when_removed: bool) -> dict:
    """The doctrine's own falsifier. If cutting a non-consuming edge
    changes the downstream node, the two are coupled through something
    the graph does not declare — shared mutable state, tool contention,
    an implicit ordering. The contract is incomplete, not the law."""
    if not edge_consumes and downstream_changed_when_removed:
        return {"contract_complete": False, "reason": "E_HIDDEN_STATE",
                "law": "a node that changes without consuming is "
                       "coupled by undeclared state"}
    return {"contract_complete": True}


# ── 2. node and output contracts ───────────────────────────────────────

def node_contract(task, inputs, output_schema, failure_states) -> dict:
    """One job nameable in three words, an explicit input, a
    structured output, and named failure states — so a failure is a
    routable VALUE and not an exception that stops the graph."""
    missing = []
    if not task or len(str(task).split()) > 3:
        missing.append("task_nameable_in_three_words")
    if not inputs:
        missing.append("explicit_input")
    if not output_schema:
        missing.append("structured_output")
    unknown = tuple(sorted(set(failure_states or ()) -
                           set(FAILURE_STATES)))
    if not failure_states:
        missing.append("named_failure_states")
    if missing or unknown:
        return {"ok": False, "reason": "E_UNCONTRACTED_NODE",
                "missing": tuple(missing), "unknown_states": unknown}
    return {"ok": True, "swappable": True,
            "law": "failures are values the graph routes, not "
                   "exceptions that stop it"}


def output_object(value, schema, producer, inputs, config, seq) -> dict:
    """A structured output is not enough: it needs identity and
    provenance, or two byte-identical JSONs from incompatible
    experimental conditions become interchangeable. Logical seq, not
    wall-clock (replay)."""
    for name, v in (("schema", schema), ("producer", producer),
                    ("config", config)):
        if not v:
            return {"ok": False, "reason": "E_UNPROVENANCED_OUTPUT",
                    "missing": name}
    if inputs is None:
        return {"ok": False, "reason": "E_UNPROVENANCED_OUTPUT",
                "missing": "inputs"}
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0:
        return {"ok": False, "reason": "E_UNORDERED_OUTPUT"}
    body = {"value": value, "schema": schema, "producer": producer,
            "inputs": inputs, "config": config, "seq": seq}
    return {"ok": True, **body, "artifact_id": _sha(body),
            # identity ignores seq: same value under same conditions is
            # the same artifact re-emitted, not a new one
            "identity": _sha({k: body[k] for k in
                              ("value", "schema", "producer",
                               "inputs", "config")})}


def same_artifact(a, b) -> dict:
    """Two outputs are the same artifact only if value AND conditions
    match. Equal values under different configs are a collision, not
    a corroboration."""
    if not (a.get("ok") and b.get("ok")):
        return {"same": False, "reason": "E_UNPROVENANCED_OUTPUT"}
    if a["identity"] == b["identity"]:
        return {"same": True}
    if a["value"] == b["value"]:
        return {"same": False, "reason": "E_CONFIG_COLLISION",
                "law": "identical values from incompatible conditions "
                       "are not one artifact"}
    return {"same": False}


def failure_state(state) -> dict:
    """NOT_FOUND and NO_ACCESS are epistemically different: one says
    the world lacks it, the other says we could not look."""
    if state not in FAILURE_STATES:
        return {"ok": False, "reason": "E_UNKNOWN_FAILURE_STATE"}
    return {"ok": True, "state": state,
            "routable": True,
            "asserts_absence": state == "NOT_FOUND",
            "asserts_only_our_blindness": state in ("NO_ACCESS",
                                                    "TIMEOUT",
                                                    "TOOL_FAILURE")}


def collapse_failures(a, b) -> dict:
    """Mapping two distinct failure states onto one is how a graph
    starts routing blindness as absence."""
    if a in FAILURE_STATES and b in FAILURE_STATES and a != b:
        return {"licensed": False, "reason": "E_FAILURE_STATE_COLLAPSE",
                "collapsed": (a, b)}
    return {"licensed": True}


# ── 3. the four primitives ─────────────────────────────────────────────

def primitive(kind, branches=1, terminates_on_evidence=None) -> dict:
    """CHAIN, FAN, ROUTER, CONTROLLED_CYCLE cover production graphs. A
    cycle is controlled only when evidence — not a feeling of doneness
    — ends it."""
    if kind not in PRIMITIVES:
        return {"ok": False, "reason": "E_UNKNOWN_PRIMITIVE"}
    if kind == "CONTROLLED_CYCLE" and not terminates_on_evidence:
        return {"ok": False, "reason": "E_UNCONTROLLED_CYCLE",
                "law": "repeat until evidence says done, never until "
                       "it feels done"}
    if kind == "FAN" and branches < 2:
        return {"ok": False, "reason": "E_FAN_OF_ONE"}
    return {"ok": True, "kind": kind, "branches": branches}


# ── 4. joins are decisions ─────────────────────────────────────────────

def join_policy(settled, failed, coverage, tau,
                critical_contradiction=False,
                next_needs_complete_set=True) -> dict:
    """A barrier after every stage turns a fan back into a chain. Wait
    only for evidence the NEXT decision needs; then decide by policy:

        CONTINUE if coverage >= tau
        HOLD     if evidence insufficient
        FAIL     if a critical contradiction appeared

    One failed branch does not take the other ninety-nine with it."""
    if not next_needs_complete_set:
        return {"ok": False, "reason": "E_IMPLICIT_BARRIER",
                "law": "join only when the next node needs the "
                       "complete set; otherwise stream"}
    if critical_contradiction:
        return {"ok": True, "decision": "FAIL",
                "settled": settled, "failed": failed}
    if coverage >= tau:
        return {"ok": True, "decision": "CONTINUE",
                "settled": settled, "failed": failed,
                "note": "partial sets continue when the missing "
                        "branches are not required"}
    return {"ok": True, "decision": "HOLD", "settled": settled,
            "failed": failed, "shortfall": round(tau - coverage, 6)}


# ── 5. model judges; graph decides ─────────────────────────────────────

def route(classifier_label, classifier_version, route_table,
          classifier_selected_path=None) -> dict:
    """The classifier emits a LABEL. The route table — deterministic,
    versioned, inspectable — maps labels to paths. A classifier that
    hands back a path has minted authority it does not have.

        probabilistic judgement != authority
    """
    if classifier_selected_path is not None:
        return {"ok": False, "reason": "E_CLASSIFIER_MINTED_AUTHORITY",
                "law": "the model may classify; the graph decides"}
    if classifier_label not in ROUTE_LABELS:
        # an unrecognised label is itself UNKNOWN — never a default
        classifier_label = "UNKNOWN"
    if classifier_label == "UNKNOWN":
        if route_table.get("UNKNOWN") not in ("HOLD", "HUMAN"):
            return {"ok": False,
                    "reason": "E_UNKNOWN_ROUTED_TO_DEFAULT"}
        return {"ok": True, "label": "UNKNOWN",
                "selected_path": route_table["UNKNOWN"],
                "rule_id": "UNKNOWN->HOLD",
                "classifier_version": classifier_version}
    path = route_table.get(classifier_label)
    if not path:
        return {"ok": False, "reason": "E_NO_RULE_FOR_LABEL"}
    return {"ok": True, "label": classifier_label,
            "selected_path": path,
            "rule_id": f"{classifier_label}->{path}",
            "classifier_version": classifier_version,
            "explainable": True}


def route_decision(classifier_output, classifier_version,
                   deterministic_rule_id, selected_path,
                   evidence_refs) -> dict:
    """Every route becomes replayable: a label and a table, not a
    paragraph of reasoning that no longer exists."""
    missing = [n for n, v in
               (("classifier_output", classifier_output),
                ("classifier_version", classifier_version),
                ("deterministic_rule_id", deterministic_rule_id),
                ("selected_path", selected_path),
                ("evidence_refs", evidence_refs)) if not v]
    if missing:
        return {"ok": False, "reason": "E_UNREPLAYABLE_ROUTE",
                "missing": tuple(missing)}
    return {"ok": True, "classifier_output": classifier_output,
            "classifier_version": classifier_version,
            "deterministic_rule_id": deterministic_rule_id,
            "selected_path": selected_path,
            "evidence_refs": tuple(evidence_refs),
            "answers_why_this_route": True}


# ── 6. verification is an edge gate ────────────────────────────────────

def verification_placement(unverified_propagation_steps,
                           max_latency, is_terminal=False) -> dict:
    """CHIDDUSH from the arXiv-2026 agentic corpus (candidate; the
    corpus finding is REPORTED_EXTERNAL, so this encodes the STRUCTURAL
    principle, not a measured threshold): a verification edge is not
    only a matter of WHO (producer != approver) but of WHEN. If a
    claim propagates through k unverified hops before its corrector,
    belief can destabilize before correction arrives ('delayed
    verification destabilizes multi-agent belief'). Placement within
    max_latency is required unless the node is terminal (nothing reads
    it downstream)."""
    if unverified_propagation_steps < 0 or max_latency < 0:
        return {"ok": False, "reason": "E_NEGATIVE_LATENCY"}
    if is_terminal:
        return {"ok": True, "note": "terminal node: nothing propagates"}
    if unverified_propagation_steps > max_latency:
        return {"ok": False, "reason": "E_DELAYED_VERIFICATION",
                "steps": unverified_propagation_steps,
                "max_latency": max_latency,
                "law": "belief may destabilize before a late corrector "
                       "arrives; place the verifier within the latency "
                       "bound, or the propagated claim is unverified "
                       "state masquerading as reviewed"}
    return {"ok": True, "steps": unverified_propagation_steps,
            "within_bound": True}


def verification_edge(producer, approver, stage) -> dict:
    """Generation and admission are separated. A self-review is drawn
    from the distribution that produced the work, which is why it
    catches formatting and misses being wrong."""
    if stage not in PROMOTION_CHAIN:
        return {"ok": False, "reason": "E_UNKNOWN_STAGE"}
    if producer == approver:
        return {"ok": False, "reason": "E_SELF_APPROVAL",
                "law": "producer !-> approver"}
    return {"ok": True, "gate_on_edge": True, "stage": stage}


def promotion_step(frm, to) -> dict:
    """GENERATION != VERIFICATION != ADMISSION != PERSISTENCE != TRUTH.
    Each transition has its own contract; none is implied by the one
    before, and persistence never yields truth."""
    if frm not in PROMOTION_CHAIN or to not in PROMOTION_CHAIN:
        return {"ok": False, "reason": "E_UNKNOWN_STAGE"}
    i, j = PROMOTION_CHAIN.index(frm), PROMOTION_CHAIN.index(to)
    if j != i + 1:
        return {"ok": False, "reason": "E_STAGE_SKIPPED",
                "skipped": PROMOTION_CHAIN[i + 1:j] if j > i else ()}
    if to == "TRUTH":
        return {"ok": False, "reason": "E_PERSISTENCE_IS_NOT_TRUTH",
                "law": "the ledger records what was admitted, not "
                       "what is so"}
    return {"ok": True, "from": frm, "to": to,
            "needs_own_contract": True}


# ── 7. durable referenced state ────────────────────────────────────────

def pass_payload(kind, ref=None) -> dict:
    """Pass references, not retellings. A reviewer reads the artifact;
    it does not receive a summary that has been through three
    retellings."""
    if kind == "transcript":
        return {"ok": False, "reason": "E_TRANSCRIPT_PASSED",
                "law": "pass artifact references, not retold "
                       "transcripts"}
    if kind == "reference" and not ref:
        return {"ok": False, "reason": "E_DANGLING_REFERENCE"}
    return {"ok": True, "kind": kind, "ref": ref}


def idempotent_write(store, artifact_id, value) -> tuple:
    """A retry must not create a second copy of something that already
    exists — replays are normal, duplicates are corruption."""
    if artifact_id in store:
        if store[artifact_id] != value:
            return store, {"ok": False,
                           "reason": "E_CONFLICTING_REWRITE"}
        return store, {"ok": True, "written": False,
                       "idempotent": True}
    s = {**store, artifact_id: value}
    return s, {"ok": True, "written": True, "idempotent": True}


def run_state(run_id, graph_version, node_states, artifact_refs,
              route_decisions, retry_budget, token_budget,
              permissions, approvals, receipts) -> dict:
    """At any moment the graph answers three questions or it is a demo
    with good diagrams: WHAT happened, WHY this route, WHERE to
    resume."""
    missing = [n for n, v in (("run_id", run_id),
                              ("graph_version", graph_version),
                              ("node_states", node_states))
               if not v]
    if missing:
        return {"ok": False, "reason": "E_UNRESUMABLE_RUN",
                "missing": tuple(missing)}
    completed = tuple(sorted(n for n, s in node_states.items()
                             if s == "COMPLETED"))
    current = tuple(sorted(n for n, s in node_states.items()
                           if s == "RUNNING"))
    resumable = tuple(sorted(n for n, s in node_states.items()
                             if s in ("PENDING", "FAILED")))
    answers = {"what_happened": bool(completed) or bool(current),
               "why_this_route": bool(route_decisions),
               "where_to_resume": bool(resumable) or not resumable}
    if not answers["why_this_route"] and route_decisions is not None \
            and len(route_decisions) == 0 and current:
        # a run that took a route without recording it cannot explain
        answers["why_this_route"] = False
    return {"ok": all(answers.values()), "run_id": run_id,
            "graph_version": graph_version,
            "completed": completed, "current": current,
            "resume_from": resumable,
            "artifact_refs": tuple(artifact_refs or ()),
            "retry_budget": retry_budget,
            "token_budget": token_budget,
            "permissions": tuple(permissions or ()),
            "approvals": tuple(approvals or ()),
            "receipts": tuple(receipts or ()),
            "answers": answers,
            "reason": None if all(answers.values())
            else "E_UNRESUMABLE_RUN"}


# ── 8. topology is economics ───────────────────────────────────────────

def evidence_roots(n_agents, n_independent_roots,
                   same_model_same_source=False) -> dict:
    """The falsifier of the slogan:

        100 agents  !->  100 independent evidence roots

    A hundred branches of one model over one source is one witness
    wearing a hundred hats. Independence is a property of the
    EVIDENCE ROOTS, not of the worker count."""
    if n_agents < 1 or n_independent_roots < 0:
        return {"ok": False, "reason": "E_NEGATIVE_COUNT"}
    n_eff = 1 if same_model_same_source else n_independent_roots
    illusion = n_agents > 1 and n_eff <= 1
    return {"ok": True, "n_agents": n_agents,
            "n_effective_witnesses": n_eff,
            "consensus_illusion": illusion,
            "reason": "E_CONSENSUS_ILLUSION" if illusion else None,
            "law": "independence is a property of evidence roots, "
                   "not of worker count"}


def sizing(value_by_n, token_cost, latency_cost, coordination_cost,
           verification_cost) -> dict:
    """N* = argmax_N [ V(coverage_N, quality_N) - C_tokens - C_latency
    - C_coordination - C_verification ]. Sometimes N*=1. Breadth that
    is not priced against ALL FOUR costs is unpriced breadth."""
    for name, c in (("token", token_cost), ("latency", latency_cost),
                    ("coordination", coordination_cost),
                    ("verification", verification_cost)):
        if c is None:
            return {"ok": False, "reason": "E_UNPRICED_BREADTH",
                    "missing": f"{name}_cost"}
    if not value_by_n:
        return {"ok": False, "reason": "E_NO_VALUE_MODEL"}
    net = {}
    for n, v in sorted(value_by_n.items()):
        net[n] = round(v - token_cost(n) - latency_cost(n)
                       - coordination_cost(n) - verification_cost(n), 6)
    best = max(net, key=lambda n: (net[n], -n))
    return {"ok": True, "net_by_n": net, "n_star": best,
            "graph_earns_its_cost": net[best] > net.get(1, net[best]),
            "law": "a graph is usually more expensive; the shape must "
                   "earn it"}


def deploy_graph(single_context_holds_problem, independent_branches,
                 needs_independent_verification, must_survive_interrupt,
                 authority_varies_by_route) -> dict:
    """Start with the loop. Draw the graph when the dependencies force
    it, not before."""
    reasons = []
    if independent_branches > 1:
        reasons.append("independent_parallel_work")
    if needs_independent_verification:
        reasons.append("independent_verification")
    if must_survive_interrupt:
        reasons.append("durable_resumption")
    if authority_varies_by_route:
        reasons.append("route_controlled_authority")
    if single_context_holds_problem and not reasons:
        return {"deploy": False, "use": "SINGLE_LOOP",
                "law": "one context could have held the whole problem"}
    if not reasons:
        return {"deploy": False, "use": "SINGLE_LOOP"}
    return {"deploy": True, "use": "GRAPH", "because": tuple(reasons)}


def pipeline_order(steps) -> dict:
    """TASK -> REAL DEPENDENCIES -> GRAPH -> CONTRACTS -> AUTHORITY
    GATES -> AGENT COUNT. Never TASK -> 'spawn 100 agents'."""
    canonical = ("TASK", "REAL_DEPENDENCIES", "GRAPH", "CONTRACTS",
                 "AUTHORITY_GATES", "AGENT_COUNT")
    steps = tuple(steps)
    if steps == canonical:
        return {"licensed": True}
    if "AGENT_COUNT" in steps:
        i = steps.index("AGENT_COUNT")
        missing_before = [s for s in canonical[1:5] if s not in steps[:i]]
        if missing_before:
            return {"licensed": False, "reason": "E_COUNT_BEFORE_SHAPE",
                    "missing_before_count": tuple(missing_before)}
    return {"licensed": False, "reason": "E_PIPELINE_OUT_OF_ORDER",
            "expected": canonical}
