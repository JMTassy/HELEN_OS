r"""Workflow Runtime — Phase A item 3, the state machine as the state
authority, in the reducer-seam style.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION — executable semantics of the vNext
workflow engine; the production build replaces the store, not the
laws. Pure state machine: no function mutates its input,
deterministic replay, append-only history.

    WorkflowEngine = state authority
    LLM            = bounded cognitive function

WHAT THE DATA PATH ITSELF REFUSES:
- the model RECORDS step results as proposals on the instance; it
  never advances state. advance(by="llm") dies in the runtime
  (E_LLM_IS_NOT_STATE_AUTHORITY), not in a code review.
- only DECLARED transitions exist: the workflow definition is the
  whole alphabet, and REQUESTED->PAID-style jumps are
  E_UNDECLARED_TRANSITION — no arrow skipped by narration, now at
  runtime.
- a transition marked as a HUMAN GATE requires an approval recorded
  BEFORE the advance (E_UNAPPROVED_GATE) — and the approver may not
  be the identity that requested the work on that instance
  (E_SELF_APPROVAL): the debtor/creditor law at the approval gate.
- history is append-only and REPLAYABLE: replay(definition, history)
  refolds to the current state or the instance is corrupt
  (E_HISTORY_MISMATCH) — replay wins over narrative, executably.

The canonical fixture is vNext's own example:
NEW_DOCUMENT -> CLASSIFY -> EXTRACT -> VERIFY -> HUMAN_REVIEW ->
WRITE_RESULT -> AUDIT, with the HUMAN_REVIEW->WRITE_RESULT edge
gated. The model performs CLASSIFY/EXTRACT/VERIFY as recorded
cognition; the engine owns every arrow.

Deterministic: no wall-clock, no randomness; sequence numbers order
events; canonical serialization.
"""
from __future__ import annotations

import json

STATE_AUTHORITY = "workflow_engine"


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def boot() -> dict:
    return {"workflows": {}, "instances": {}, "seq": 0}


def _bump(s: dict) -> dict:
    n = dict(s)
    n["seq"] = s["seq"] + 1
    return n


# ── definition: the declared alphabet ──────────────────────────────────

def define_workflow(state: dict, name: str, states: tuple,
                    transitions: tuple, human_gates: tuple) -> tuple:
    """transitions: ((from, to), ...). human_gates: subset of
    transitions requiring approval. Undeclared endpoints are refused
    at definition time, not discovered at run time."""
    if name in state["workflows"]:
        return state, {"ok": False, "reason": "E_WORKFLOW_EXISTS"}
    bad = [t for t in transitions
           if t[0] not in states or t[1] not in states]
    if bad:
        return state, {"ok": False, "reason": "E_UNDECLARED_STATE",
                       "bad": tuple(map(tuple, bad))}
    gates_bad = [g for g in human_gates if tuple(g) not in
                 {tuple(t) for t in transitions}]
    if gates_bad:
        return state, {"ok": False, "reason": "E_GATE_OFF_ALPHABET"}
    s = _bump(state)
    s["workflows"] = {**s["workflows"],
                      name: {"states": tuple(states),
                             "transitions": tuple(map(tuple,
                                                      transitions)),
                             "human_gates": tuple(map(tuple,
                                                      human_gates))}}
    return s, {"ok": True, "workflow": name}


def start_instance(state: dict, workflow: str, instance: str,
                   requested_by: str) -> tuple:
    if workflow not in state["workflows"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_WORKFLOW"}
    if instance in state["instances"]:
        return state, {"ok": False, "reason": "E_INSTANCE_EXISTS"}
    initial = state["workflows"][workflow]["states"][0]
    s = _bump(state)
    s["instances"] = {**s["instances"],
                      instance: {"workflow": workflow,
                                 "state": initial,
                                 "requested_by": requested_by,
                                 "history": (),
                                 "steps": (), "approvals": ()}}
    return s, {"ok": True, "instance": instance, "state": initial}


def _upd(s: dict, instance: str, **fields) -> dict:
    n = dict(s)
    inst = dict(n["instances"][instance])
    inst.update(fields)
    n["instances"] = {**n["instances"], instance: inst}
    return n


# ── cognition records; it never advances ───────────────────────────────

def record_step(state: dict, instance: str, step: str, result: str,
                by: str) -> tuple:
    """The model's verb. A recorded result is a PROPOSAL attached to
    the instance — state does not move."""
    if instance not in state["instances"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_INSTANCE"}
    inst = state["instances"][instance]
    s = _bump(state)
    s = _upd(s, instance,
             steps=inst["steps"] + ({"seq": state["seq"],
                                     "step": step, "result": result,
                                     "by": by},))
    return s, {"ok": True, "recorded": step, "by": by,
               "state_moved": False,
               "state": inst["state"]}


# ── approval: the debtor/creditor law at the gate ──────────────────────

def approve(state: dict, instance: str, transition: tuple,
            approver: str) -> tuple:
    """An approval is recorded against a specific gated transition.
    The approver may not be the identity that requested the work."""
    if instance not in state["instances"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_INSTANCE"}
    inst = state["instances"][instance]
    if approver == inst["requested_by"]:
        return state, {"ok": False, "reason": "E_SELF_APPROVAL",
                       "law": "the approver may not be the requester; "
                              "the debtor/creditor law holds at the "
                              "human gate"}
    s = _bump(state)
    s = _upd(s, instance,
             approvals=inst["approvals"] + ((tuple(transition),
                                             approver),))
    return s, {"ok": True, "transition": tuple(transition),
               "approver": approver}


# ── the only mover ─────────────────────────────────────────────────────

def advance(state: dict, instance: str, to_state: str,
            by: str) -> tuple:
    """The engine's verb, and only the engine's. Declared edge,
    approved gate, appended history — or nothing moves."""
    if instance not in state["instances"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_INSTANCE"}
    if by != STATE_AUTHORITY:
        return state, {"ok": False,
                       "reason": "E_LLM_IS_NOT_STATE_AUTHORITY"
                       if by == "llm" else
                       "E_UNKNOWN_STATE_AUTHORITY",
                       "law": "the model performs cognitive steps; it "
                              "never decides the workflow moved"}
    inst = state["instances"][instance]
    wf = state["workflows"][inst["workflow"]]
    edge = (inst["state"], to_state)
    if edge not in wf["transitions"]:
        return state, {"ok": False,
                       "reason": "E_UNDECLARED_TRANSITION",
                       "from": inst["state"], "to": to_state,
                       "law": "no arrow skipped by narration — at "
                              "runtime"}
    if edge in wf["human_gates"] and \
            edge not in [a[0] for a in inst["approvals"]]:
        return state, {"ok": False, "reason": "E_UNAPPROVED_GATE",
                       "gate": edge}
    s = _bump(state)
    s = _upd(s, instance, state=to_state,
             history=inst["history"] + ({"seq": state["seq"],
                                         "from": edge[0],
                                         "to": edge[1]},))
    return s, {"ok": True, "instance": instance,
               "from": edge[0], "to": to_state, "by": by}


# ── replay wins over narrative, executably ─────────────────────────────

def replay(state: dict, instance: str) -> dict:
    """Refold the append-only history from the initial state. The
    folded state must equal the stored state or the instance is
    corrupt — the ledger is the authority, the field is a cache."""
    if instance not in state["instances"]:
        return {"ok": False, "reason": "E_UNKNOWN_INSTANCE"}
    inst = state["instances"][instance]
    wf = state["workflows"][inst["workflow"]]
    cur = wf["states"][0]
    for ev in inst["history"]:
        if ev["from"] != cur or \
                (ev["from"], ev["to"]) not in wf["transitions"]:
            return {"ok": False, "reason": "E_HISTORY_MISMATCH",
                    "at_seq": ev["seq"]}
        cur = ev["to"]
    match = cur == inst["state"]
    return {"ok": match, "replayed_state": cur,
            "stored_state": inst["state"],
            "reason": None if match else "E_HISTORY_MISMATCH",
            "law": "replay wins over narrative; the stored field is "
                   "a cache of the history, never the truth"}
