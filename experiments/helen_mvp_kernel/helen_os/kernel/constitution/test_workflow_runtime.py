"""Phase A item 3, adversarially tested: the LLM records and never
advances; undeclared jumps die at runtime; a gated edge needs an
approval that cannot come from the requester; replay refolds the
history or declares the instance corrupt; and no operation mutates
its input.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import workflow_runtime as wf
from workflow_runtime import (
    advance,
    approve,
    boot,
    define_workflow,
    record_step,
    replay,
    start_instance,
)

STATES = ("NEW_DOCUMENT", "CLASSIFY", "EXTRACT", "VERIFY",
          "HUMAN_REVIEW", "WRITE_RESULT", "AUDIT")
EDGES = (("NEW_DOCUMENT", "CLASSIFY"), ("CLASSIFY", "EXTRACT"),
         ("EXTRACT", "VERIFY"), ("VERIFY", "HUMAN_REVIEW"),
         ("HUMAN_REVIEW", "WRITE_RESULT"), ("WRITE_RESULT", "AUDIT"))
GATES = (("HUMAN_REVIEW", "WRITE_RESULT"),)


def _platform():
    s = boot()
    s, _ = define_workflow(s, "doc", STATES, EDGES, GATES)
    s, _ = start_instance(s, "doc", "d1", requested_by="user")
    return s


# ── definition discipline ──────────────────────────────────────────────

def test_an_edge_to_an_undeclared_state_dies_at_definition():
    s = boot()
    _, r = define_workflow(s, "bad", ("A", "B"),
                           (("A", "PAID"),), ())
    assert r["reason"] == "E_UNDECLARED_STATE"


def test_a_gate_must_sit_on_a_declared_edge():
    s = boot()
    _, r = define_workflow(s, "bad", ("A", "B"), (("A", "B"),),
                           (("B", "A"),))
    assert r["reason"] == "E_GATE_OFF_ALPHABET"


# ── the LLM records; the engine moves ──────────────────────────────────

def test_the_model_records_a_result_and_state_does_not_move():
    s = _platform()
    s, r = record_step(s, "d1", "CLASSIFY", "invoice", by="llm")
    assert r["ok"] is True
    assert r["state_moved"] is False
    assert r["state"] == "NEW_DOCUMENT"


def test_the_llm_cannot_advance_at_runtime():
    s = _platform()
    _, r = advance(s, "d1", "CLASSIFY", by="llm")
    assert r["ok"] is False
    assert r["reason"] == "E_LLM_IS_NOT_STATE_AUTHORITY"
    _, r2 = advance(s, "d1", "CLASSIFY", by="operator")
    assert r2["reason"] == "E_UNKNOWN_STATE_AUTHORITY"


def test_only_declared_edges_move():
    s = _platform()
    _, r = advance(s, "d1", "AUDIT", by="workflow_engine")
    assert r["reason"] == "E_UNDECLARED_TRANSITION"
    s, ok = advance(s, "d1", "CLASSIFY", by="workflow_engine")
    assert ok["ok"] is True and ok["to"] == "CLASSIFY"


# ── the human gate and the debtor/creditor law ─────────────────────────

def _to_review(s):
    for to in ("CLASSIFY", "EXTRACT", "VERIFY", "HUMAN_REVIEW"):
        s, r = advance(s, "d1", to, by="workflow_engine")
        assert r["ok"] is True
    return s


def test_a_gated_edge_without_approval_holds():
    s = _to_review(_platform())
    _, r = advance(s, "d1", "WRITE_RESULT", by="workflow_engine")
    assert r["reason"] == "E_UNAPPROVED_GATE"
    assert r["gate"] == ("HUMAN_REVIEW", "WRITE_RESULT")


def test_the_requester_may_not_approve_its_own_instance():
    s = _to_review(_platform())
    _, r = approve(s, "d1", ("HUMAN_REVIEW", "WRITE_RESULT"),
                   approver="user")
    assert r["ok"] is False
    assert r["reason"] == "E_SELF_APPROVAL"


def test_an_independent_approval_opens_the_gate():
    s = _to_review(_platform())
    s, ap = approve(s, "d1", ("HUMAN_REVIEW", "WRITE_RESULT"),
                    approver="reviewer")
    assert ap["ok"] is True
    s, r = advance(s, "d1", "WRITE_RESULT", by="workflow_engine")
    assert r["ok"] is True
    s, r2 = advance(s, "d1", "AUDIT", by="workflow_engine")
    assert r2["ok"] is True


# ── replay wins over narrative ─────────────────────────────────────────

def test_replay_refolds_the_history_to_the_stored_state():
    s = _to_review(_platform())
    v = replay(s, "d1")
    assert v["ok"] is True
    assert v["replayed_state"] == v["stored_state"] == "HUMAN_REVIEW"


def test_a_tampered_state_field_is_caught_by_replay():
    """The stored field is a cache; the history is the truth."""
    s = _to_review(_platform())
    inst = dict(s["instances"]["d1"])
    inst["state"] = "AUDIT"                    # narrative tampering
    tampered = dict(s)
    tampered["instances"] = {**s["instances"], "d1": inst}
    v = replay(tampered, "d1")
    assert v["ok"] is False
    assert v["reason"] == "E_HISTORY_MISMATCH"


def test_a_tampered_history_is_caught_by_refold():
    s = _to_review(_platform())
    inst = dict(s["instances"]["d1"])
    inst["history"] = inst["history"] + (
        {"seq": 999, "from": "HUMAN_REVIEW", "to": "AUDIT"},)
    tampered = dict(s)
    tampered["instances"] = {**s["instances"], "d1": inst}
    v = replay(tampered, "d1")
    assert v["ok"] is False        # HUMAN_REVIEW->AUDIT is undeclared


# ── purity and determinism ─────────────────────────────────────────────

def test_no_operation_mutates_its_input_state():
    s = _platform()
    frozen = wf.canon(s)
    record_step(s, "d1", "CLASSIFY", "x", "llm")
    advance(s, "d1", "CLASSIFY", by="workflow_engine")
    approve(s, "d1", ("HUMAN_REVIEW", "WRITE_RESULT"), "reviewer")
    assert wf.canon(s) == frozen


def test_deterministic_replay_of_the_whole_platform():
    assert wf.canon(_to_review(_platform())) == \
        wf.canon(_to_review(_platform()))
