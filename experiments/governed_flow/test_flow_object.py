"""Falsifiers for F, the Governed Flow Object — every boxed law from
the Director recap executes, plus one end-to-end cycle over a customer
call: one source, one trace, many bounded projections, a leased and
A_E-gated action, a receipt on the edge, and a replay that converges.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "effect_gate"))

import flow_object as fo
from effect_gate import Admission, EffectProposal, NamedLoss
from flow_object import (
    FlowAction,
    Lease,
    Projection,
    Trace,
    TraceEdge,
    authority_conservation,
    authorize,
    canon,
    check_authority_acyclic,
    conserve,
    evidence_count,
    execute,
    flow_identity,
    invalidate,
    j_e,
    j_o,
    lease_valid,
    learn,
    revalidate,
    start_trace,
    state_grade,
)


# ── shared fixtures ─────────────────────────────────────────────────────

def _call_trace(actor="goblin_gemma"):
    t = start_trace("FLOW_17", "call_2026_08_11")
    t = t.add(TraceEdge("call_2026_08_11", "transcript", "transcribe",
                        actor, t=1))
    t = t.add(TraceEdge("transcript", "commitments", "extract_commitments",
                        actor, t=2))
    return t


LEASE = Lease("L1", subject="FLOW_17", capability="SEND_EMAIL",
              scope="one_message", resource="mailto:alex@example.com",
              t_start=10, t_end=20,
              constraints=(("message_hash", "abc123"),),
              issuer="principal:jm")

ACTION = FlowAction("a1", subject="FLOW_17", capability="SEND_EMAIL",
                    resource="mailto:alex@example.com",
                    fields=(("message_hash", "abc123"),))

SEND_LOSS = NamedLoss("message leaves as the principal's word; "
                      "not compostable", recoverable=False)


# ── flow identity != model identity ─────────────────────────────────────

def test_swapping_the_executor_leaves_flow_identity_unchanged():
    assert flow_identity(_call_trace("goblin_gemma")) == \
        flow_identity(_call_trace("claude")) == \
        flow_identity(_call_trace("human:jm"))


def test_changing_an_operator_changes_the_identity():
    a = _call_trace()
    b = start_trace("FLOW_17", "call_2026_08_11").add(
        TraceEdge("call_2026_08_11", "transcript", "summarize", "x", t=1))
    assert flow_identity(a) != flow_identity(b)


# ── the trace: causal DAG, receipts on edges ────────────────────────────

def test_edge_from_nowhere_is_refused():
    with pytest.raises(ValueError, match="E_EDGE_FROM_NOWHERE"):
        _call_trace().add(TraceEdge("ghost", "x", "op", "a", t=3))


def test_trace_refuses_a_cycle():
    t = _call_trace()
    with pytest.raises(ValueError, match="E_TRACE_CYCLE"):
        t.add(TraceEdge("commitments", "call_2026_08_11", "loop", "a", t=3))


def test_evidence_vocabulary_contains_no_true():
    assert "TRUE" not in fo.EVIDENCE_STATES        # extraction != truth
    with pytest.raises(ValueError, match="E_UNKNOWN_EVIDENCE_STATE"):
        TraceEdge("a", "b", "op", "x", t=1, evidence_state="TRUE")


# ── projection count != evidence count ──────────────────────────────────

def _five_views():
    return tuple(Projection(v, frozenset({"commitments"}))
                 for v in ("crm", "followup", "coaching", "faq", "deck"))


def test_five_views_from_one_call_are_one_witness():
    r = evidence_count(_call_trace(), _five_views())
    assert r["projection_count"] == 5
    assert r["evidence_count"] == 1
    assert r["independent_witnesses"] == ["call_2026_08_11"]


def test_invalidation_hits_only_dependent_views():
    views = _five_views() + (Projection("org_chart", frozenset({"other"})),)
    r = invalidate(views, "commitments")
    assert set(r["invalidated"]) == {"crm", "followup", "coaching",
                                     "faq", "deck"}
    assert r["untouched"] == ("org_chart",)


# ── cyclic intelligence ∧ acyclic authority ─────────────────────────────

def test_the_straight_authority_chain_is_acyclic():
    edges = (("observe", "propose"), ("propose", "authorize"),
             ("authorize", "act"), ("act", "receipt"))
    assert check_authority_acyclic(edges)["verdict"] == "ACYCLIC"


@pytest.mark.parametrize("bad_edge,name", [
    (("act", "authorize"), "retroactive self-authorization"),
    (("receipt", "authorize"), "receipt-minted permission"),
    (("learn", "authorize"), "self-installing policy"),
])
def test_every_authority_backedge_is_a_cycle(bad_edge, name):
    edges = (("observe", "propose"), ("propose", "authorize"),
             ("authorize", "act"), ("act", "receipt"),
             ("receipt", "learn"), bad_edge)
    v = check_authority_acyclic(edges)
    assert v["verdict"] == "E_AUTHORITY_CYCLE", name


# ── the lease: scope-bound, time-bound, issuer-bound ────────────────────

def test_lease_without_issuer_is_unconstructible():
    with pytest.raises(ValueError, match="E_LEASE_WITHOUT_ISSUER"):
        Lease("L2", "F", "C", "s", "r", 0, 1, issuer="")


def test_lease_validity_is_narrow():
    assert lease_valid(LEASE, ACTION, t=15)["valid"] is True
    assert lease_valid(LEASE, ACTION, t=25)["valid"] is False   # window
    other = FlowAction("a2", "FLOW_17", "SEND_EMAIL",
                       "mailto:someone_else@example.com",
                       fields=(("message_hash", "abc123"),))
    assert lease_valid(LEASE, other, t=15)["valid"] is False    # resource
    tampered = FlowAction("a3", "FLOW_17", "SEND_EMAIL",
                          "mailto:alex@example.com",
                          fields=(("message_hash", "OTHER"),))
    assert lease_valid(LEASE, tampered, t=15)["valid"] is False  # constraint


# ── valid at intake != valid at execution ───────────────────────────────

def test_authorize_then_expire_then_refuse():
    auth = authorize(ACTION, LEASE, t0=12, policy_version="v1")
    assert isinstance(auth, fo.AuthorizationRecord)
    r = revalidate(auth, ACTION, LEASE, t1=21, policy_version_now="v1")
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_STALE_AUTHORITY"


def test_policy_drift_and_revocation_break_the_chain():
    auth = authorize(ACTION, LEASE, t0=12, policy_version="v1")
    drift = revalidate(auth, ACTION, LEASE, 15, policy_version_now="v2")
    assert drift["reason"] == "E_POLICY_DRIFT"
    revoked = revalidate(auth, ACTION, LEASE, 15, "v1", revoked=True)
    assert revoked["reason"] == "E_CONSENT_REVOKED"


def test_execute_needs_revalidation_and_the_a_e_gate():
    auth = authorize(ACTION, LEASE, t0=12, policy_version="v1")
    reval = revalidate(auth, ACTION, LEASE, t1=15, policy_version_now="v1")
    prop = EffectProposal("a1", "send", "EMITTED", loss=SEND_LOSS)
    # revalidated but unadmitted -> A_E holds it
    held = execute(ACTION, auth, reval, prop, admission=None)
    assert held["executed"] is False and held["reason"].startswith("A_E:")
    # both gates -> executed, a typed ExecutionReceipt minted
    done = execute(ACTION, auth, reval, prop, Admission("jm", "a1"))
    assert isinstance(done, fo.ExecutionReceipt) and done.receipt_hash
    # stale reval -> the admission alone is not enough
    stale = revalidate(auth, ACTION, LEASE, t1=99, policy_version_now="v1")
    assert execute(ACTION, auth, stale, prop,
                   Admission("jm", "a1"))["executed"] is False


# ── four records, no collapse ───────────────────────────────────────────

def _executed_receipt():
    auth = authorize(ACTION, LEASE, 12, "v1")
    reval = revalidate(auth, ACTION, LEASE, 15, "v1")
    return execute(ACTION, auth, reval,
                   EffectProposal("a1", "send", "EMITTED", loss=SEND_LOSS),
                   Admission("jm", "a1"))


def test_the_four_record_kinds_are_distinct():
    kinds = {fo.ProposalReceipt().kind, fo.AuthorizationRecord().kind,
             fo.ExecutionReceipt().kind, fo.ReplayVerdict().kind}
    assert len(kinds) == 4


def test_an_execution_receipt_cannot_reenter_as_authorization():
    """The receipt-minted-permission cycle, killed at the TYPE level:
    yesterday's execution receipt is not today's permission."""
    receipt = _executed_receipt()
    r = revalidate(receipt, ACTION, LEASE, 15, "v1")
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_RECEIPT_KIND_MISMATCH"
    assert r["got"] == "EXECUTION_RECEIPT"
    e = execute(ACTION, receipt, {"verdict": "REVALIDATED", "t1": 15},
                EffectProposal("a1", "send", "EMITTED", loss=SEND_LOSS),
                Admission("jm", "a1"))
    assert e["executed"] is False
    assert e["reason"] == "E_RECEIPT_KIND_MISMATCH"


def test_a_proposal_receipt_authorizes_nothing():
    pr = fo.propose(EffectProposal("a1", "send", "EMITTED",
                                   loss=SEND_LOSS), t=11)
    assert isinstance(pr, fo.ProposalReceipt) and pr.content_hash
    r = revalidate(pr, ACTION, LEASE, 15, "v1")
    assert r["reason"] == "E_RECEIPT_KIND_MISMATCH"


def test_a_replay_verdict_neither_authorizes_nor_executes():
    rv = state_grade({"x": 1}, None, (), REGISTRY)
    assert revalidate(rv, ACTION, LEASE, 15, "v1")["reason"] == \
        "E_RECEIPT_KIND_MISMATCH"


# ── durable flow vs mutable instance ────────────────────────────────────

def test_identity_lives_in_the_flow_never_in_the_instance():
    """Kill the instance, restart with another executor: the durable
    (flow_id, trace, identity) triple is untouched."""
    trace = _call_trace()
    i1 = fo.FlowInstance("run-1", "FLOW_17", executor="goblin_gemma")
    i2 = fo.FlowInstance("run-2", "FLOW_17", executor="claude")
    assert i1.instance_id != i2.instance_id
    assert flow_identity(trace) == flow_identity(trace)   # instance-blind
    rebound = fo.rebind(i1, "human:jm")
    assert rebound.executor == "human:jm"
    assert rebound.flow_id == i1.flow_id and rebound.stage == i1.stage


def test_lifecycle_advances_one_stage_and_refuses_skips():
    inst = fo.FlowInstance("run-1", "FLOW_17", "goblin_gemma")
    inst = fo.advance(inst)
    assert inst.stage == "SENSE"
    inst = fo.jump(inst, "EXTRACT")
    assert inst.stage == "EXTRACT"
    with pytest.raises(ValueError, match="E_STAGE_SKIP"):
        fo.jump(inst, "ACT")          # the skipped stages ARE the gates


def test_quiescent_flows_do_not_advance():
    inst = fo.FlowInstance("run-1", "FLOW_17", "x", stage="QUIESCENT")
    with pytest.raises(ValueError, match="E_FLOW_QUIESCENT"):
        fo.advance(inst)
    with pytest.raises(ValueError, match="E_UNKNOWN_STAGE"):
        fo.FlowInstance("run-2", "FLOW_17", "x", stage="LIMBO")


# ── JUDGE = J_E ⊕ J_O ───────────────────────────────────────────────────

def test_supported_claim_does_not_permit_the_action():
    e = j_e("customer asked for SSO", ("transcript#t=1042",))
    assert e["verdict"] == "SUPPORTED"
    o = j_o(ACTION, leases=(), t=15)
    assert o["verdict"] == "REFUSED"        # evidence != permission
    assert "does not imply Permission" in o["note"]


def test_je_codomain_has_no_permission_and_jo_no_truth():
    assert "PERMITTED" not in j_e("c", ("x",)).values()
    assert "SUPPORTED" not in j_o(ACTION, (LEASE,), 15).values()


# ── conservation ────────────────────────────────────────────────────────

def test_material_balance_and_its_violation():
    assert conserve(100, 60, 30, 10)["verdict"] == "BALANCED"
    v = conserve(100, 60, 30, 5)
    assert v["verdict"] == "E_CONSERVATION_VIOLATION" and v["gap"] == 5


def test_executed_must_be_subset_of_authorized():
    ok = authority_conservation(frozenset({"a1"}), frozenset({"a1", "a2"}))
    assert ok["verdict"] == "CONSERVED"
    assert ok["unused_authorizations"] == ["a2"]
    bad = authority_conservation(frozenset({"a1", "rogue"}),
                                 frozenset({"a1"}))
    assert bad["verdict"] == "E_UNAUTHORIZED_EFFECT"
    assert bad["unauthorized"] == ["rogue"]


# ── replay: the three-rung state ladder ─────────────────────────────────

REGISTRY = {
    "transcribe": lambda s: {**s, "transcript": "words"},
    "extract_commitments": lambda s: {**s, "commitments": ["send SSO doc"]},
}


def test_state_without_path_is_weakest():
    g = state_grade({"x": 1}, None, (), REGISTRY)
    assert g.grade == "STORED_STATE_ONLY"


def test_replay_convergence_witnesses_the_transformation():
    edges = _call_trace().edges
    s0 = {"event": "call"}
    sn = {"event": "call", "transcript": "words",
          "commitments": ["send SSO doc"]}
    g = state_grade(sn, s0, edges, REGISTRY)
    assert g.grade == "WITNESSED_TRANSFORMATION"


def test_replay_divergence_demotes_to_claim():
    edges = _call_trace().edges
    g = state_grade({"event": "call", "transcript": "OTHER"},
                    {"event": "call"}, edges, REGISTRY)
    assert g.grade == "TRANSFORMATION_CLAIM"
    assert "E_REPLAY_DIVERGENCE" in g.detail


def test_unregistered_operator_cannot_replay():
    with pytest.raises(ValueError, match="E_OPERATOR_NOT_IN_REGISTRY"):
        state_grade({}, {}, (TraceEdge("a", "b", "mystery", "x", t=1),),
                    REGISTRY)


# ── LEARN tiers: budgets rise, and learning never mints a lease ─────────

def test_l0_is_free_and_ephemeral():
    r = learn("L0_EPHEMERAL", "prefer shorter subject lines")
    assert r["verdict"] == "ADOPTED" and r["persists"] is False


def test_l1_needs_a_receipt_l2_needs_the_principal_too():
    assert learn("L1_HEURISTIC", "x")["verdict"] == "HOLD"
    assert learn("L1_HEURISTIC", "x", receipt="r1")["verdict"] == "ADOPTED"
    l2 = learn("L2_INSTITUTIONAL", "x", receipt="r1")
    assert l2["reason"] == "E_AWAITING_PRINCIPAL"
    assert learn("L2_INSTITUTIONAL", "x", "r1",
                 Admission("jm", "mem1"))["verdict"] == "ADOPTED"


def test_l3_requires_the_full_meta_path_in_order():
    partial = tuple((s, "done") for s in ("proposal", "compile", "decide"))
    r = learn("L3_CONSTITUTIONAL", "new gate rule", "r1",
              Admission("jm", "c1"), meta_path=partial)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_META_PATH_INCOMPLETE"
    shuffled = tuple((s, "done") for s in
                     ("compile", "proposal", "attest", "decide",
                      "activate", "audit"))
    assert learn("L3_CONSTITUTIONAL", "x", "r1", Admission("jm", "c1"),
                 shuffled)["verdict"] == "REFUSED"
    full = tuple((s, "done") for s in fo.META_CHANGE_STAGES)
    assert learn("L3_CONSTITUTIONAL", "x", "r1", Admission("jm", "c1"),
                 full)["verdict"] == "ADOPTED"


def test_no_learn_result_ever_contains_a_lease():
    full = tuple((s, "done") for s in fo.META_CHANGE_STAGES)
    results = [learn("L0_EPHEMERAL", "x"),
               learn("L1_HEURISTIC", "x", "r"),
               learn("L2_INSTITUTIONAL", "x", "r", Admission("jm", "m")),
               learn("L3_CONSTITUTIONAL", "x", "r", Admission("jm", "c"),
                     full)]
    for r in results:
        assert "lease" not in canon(r).lower()   # learning != authority


def test_authority_order_puts_persistent_learning_above_action():
    assert fo.AUTHORITY_ORDER["LEARN_PERSISTENT"] > \
        fo.AUTHORITY_ORDER["ACT"] > fo.AUTHORITY_ORDER["JUDGE"] >= \
        fo.AUTHORITY_ORDER["PROJECT"] > fo.AUTHORITY_ORDER["SENSE"]


# ── the end-to-end cycle ────────────────────────────────────────────────

def test_one_full_governed_cycle():
    """WORLD -> SENSE -> EXTRACT -> JUDGE -> PROJECT -> lease -> ACT ->
    RECEIPT -> MEMORY -> REPLAY -> LEARN, on one customer call."""
    trace = _call_trace()
    views = _five_views()

    # projection multiplicity, one witness
    assert evidence_count(trace, views)["evidence_count"] == 1

    # judge splits
    assert j_e("committed to SSO doc", ("transcript",))["verdict"] == \
        "SUPPORTED"
    assert j_o(ACTION, (LEASE,), t=15)["verdict"] == "PERMITTED"

    # stage a proposal, then the three-step + A_E
    prop = EffectProposal("a1", "send", "EMITTED", loss=SEND_LOSS)
    pr = fo.propose(prop, t=11)
    auth = authorize(ACTION, LEASE, 12, "v1")
    reval = revalidate(auth, ACTION, LEASE, 15, "v1")
    done = execute(ACTION, auth, reval, prop, Admission("jm", "a1"))
    assert isinstance(done, fo.ExecutionReceipt)
    # four distinct records now exist for this one action
    assert {pr.kind, auth.kind, done.kind} == {
        "PROPOSAL_RECEIPT", "AUTHORIZATION_RECORD", "EXECUTION_RECEIPT"}

    # the receipt lands on an EDGE of the trace, not a node
    trace = trace.add(TraceEdge("commitments", "followup_sent",
                                "send_followup", "goblin_gemma", t=15,
                                lease_ref="L1",
                                receipt=done.receipt_hash))
    assert trace.edges[-1].receipt == done.receipt_hash

    # authority stayed acyclic and conserved
    assert check_authority_acyclic(
        (("observe", "propose"), ("propose", "authorize"),
         ("authorize", "act"), ("act", "receipt")))["verdict"] == "ACYCLIC"
    assert authority_conservation(
        frozenset({"a1"}), frozenset({"a1"}))["verdict"] == "CONSERVED"

    # replay witnesses the pre-action pipeline
    g = state_grade({"event": "call", "transcript": "words",
                     "commitments": ["send SSO doc"]},
                    {"event": "call"}, trace.edges[:2], REGISTRY)
    assert g.grade == "WITNESSED_TRANSFORMATION"

    # replay's verdict grades history and enters no gate
    assert g.kind == "REPLAY_VERDICT"

    # and the flow learns at L1 with the EXECUTION receipt in hand
    assert learn("L1_HEURISTIC", "follow up within a day",
                 receipt=done.receipt_hash)["verdict"] == "ADOPTED"


def test_everything_is_deterministic():
    a = canon(evidence_count(_call_trace(), _five_views()))
    b = canon(evidence_count(_call_trace(), _five_views()))
    assert a == b
    assert flow_identity(_call_trace()) == flow_identity(_call_trace())
