"""Phase A item 5, adversarially tested: the ground never moves under
a client inside a major; removal without deprecation dies even across
a major; unknown endpoint and unauthorized are one answer; and an
internal goblin_trace field physically cannot cross the wire.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import api_runtime as api
from api_runtime import (
    boot,
    contract_digest,
    define_contract,
    deprecate,
    evolve,
    request,
    respond,
)

V1 = {
    "get_document": {
        "capability": "docs.read",
        "request": {"doc_id": "string", "verbose": "bool"},
        "required": ("doc_id",),
        "response": {"doc_id": "string", "title": "string",
                     "state": "string"},
    },
    "create_task": {
        "capability": "tasks.write",
        "request": {"title": "string", "priority": "int"},
        "required": ("title",),
        "response": {"task_id": "string"},
    },
}


def _platform():
    s = boot()
    s, r = define_contract(s, "1.0", V1)
    assert r["ok"] is True
    return s


# ── the contract ───────────────────────────────────────────────────────

def test_the_digest_is_content_addressed_and_stable():
    a = _platform()
    b = _platform()
    assert contract_digest(a, "1.0")["digest"] == \
        contract_digest(b, "1.0")["digest"]
    assert contract_digest(a, "9.9")["reason"] == "E_UNKNOWN_VERSION"


def test_a_required_field_must_be_declared():
    s = boot()
    _, r = define_contract(s, "1.0", {
        "e": {"capability": "c.x", "request": {}, "required": ("ghost",),
              "response": {}}})
    assert r["reason"] == "E_REQUIRED_NOT_DECLARED"


def test_unknown_types_die_at_definition():
    s = boot()
    _, r = define_contract(s, "1.0", {
        "e": {"capability": "c.x", "request": {"f": "vibes"},
              "required": (), "response": {}}})
    assert r["reason"] == "E_UNKNOWN_TYPE"


# ── evolution: the ground does not move ────────────────────────────────

def test_adding_an_endpoint_and_an_optional_field_is_lawful():
    s = _platform()
    v2 = {**V1, "get_document": {**V1["get_document"],
                                 "request": {**V1["get_document"]["request"],
                                             "format": "string"}},
          "ping": {"capability": "sys.read", "request": {},
                   "required": (), "response": {"ok": "bool"}}}
    s, r = evolve(s, "1.0", "1.1", v2)
    assert r["ok"] is True


def test_removing_an_endpoint_in_a_minor_is_breaking():
    s = _platform()
    v2 = {k: v for k, v in V1.items() if k != "create_task"}
    _, r = evolve(s, "1.0", "1.1", v2)
    assert r["reason"] == "E_BREAKING_CHANGE_IN_MINOR"
    assert any("create_task" in b for b in r["breaks"])


def test_dropping_or_retyping_a_response_field_is_breaking():
    s = _platform()
    v2 = dict(V1)
    v2["get_document"] = {**V1["get_document"],
                          "response": {"doc_id": "string",
                                       "title": "int"}}
    _, r = evolve(s, "1.0", "1.1", v2)
    assert r["reason"] == "E_BREAKING_CHANGE_IN_MINOR"
    breaks = " ".join(r["breaks"])
    assert "state: dropped" in breaks and "title: string->int" in breaks


def test_an_optional_field_may_not_become_required_in_a_minor():
    s = _platform()
    v2 = dict(V1)
    v2["get_document"] = {**V1["get_document"],
                          "required": ("doc_id", "verbose")}
    _, r = evolve(s, "1.0", "1.1", v2)
    assert r["reason"] == "E_BREAKING_CHANGE_IN_MINOR"


def test_removal_without_deprecation_dies_even_across_a_major():
    s = _platform()
    v2 = {k: v for k, v in V1.items() if k != "create_task"}
    _, r = evolve(s, "1.0", "2.0", v2)
    assert r["reason"] == "E_REMOVAL_WITHOUT_DEPRECATION"
    assert r["endpoint"] == "create_task"


def test_deprecate_then_remove_across_a_major_is_the_lawful_path():
    s = _platform()
    s, d = deprecate(s, "1.0", "create_task", sunset="2.0")
    assert d["ok"] is True
    v2 = {"get_document": V1["get_document"]}
    s, r = evolve(s, "1.0", "2.0", v2)
    assert r["ok"] is True


def test_an_undated_deprecation_is_a_threat_not_a_plan():
    s = _platform()
    _, r = deprecate(s, "1.0", "create_task", sunset="")
    assert r["reason"] == "E_UNDATED_DEPRECATION"


# ── the boundary, inbound ──────────────────────────────────────────────

def test_unknown_endpoint_and_unauthorized_are_one_answer():
    s = _platform()
    ghost = request(s, "1.0", "nonexistent", {}, authorized=True)
    denied = request(s, "1.0", "get_document", {"doc_id": "d"},
                     authorized=False)
    assert ghost["reason"] == denied["reason"] == "E_NOT_FOUND"


def test_validation_runs_before_any_handler():
    s = _platform()
    missing = request(s, "1.0", "get_document", {}, True)
    assert missing["reason"] == "E_MISSING_FIELD"
    undeclared = request(s, "1.0", "get_document",
                         {"doc_id": "d", "goblin": 1}, True)
    assert undeclared["reason"] == "E_UNDECLARED_FIELD"
    badtype = request(s, "1.0", "create_task",
                      {"title": "t", "priority": True}, True)
    assert badtype["reason"] == "E_TYPE_MISMATCH"


def test_a_lawful_request_reports_deprecation_state():
    s = _platform()
    s, _ = deprecate(s, "1.0", "create_task", "2.0")
    r = request(s, "1.0", "create_task", {"title": "t"}, True)
    assert r["ok"] is True
    assert r["deprecated"] is True and r["sunset"] == "2.0"


# ── the boundary, outbound ─────────────────────────────────────────────

def test_goblin_trace_physically_cannot_cross_the_wire():
    s = _platform()
    r = respond(s, "1.0", "create_task",
                {"task_id": "t1", "goblin_trace": "HER->HAL"})
    assert r["ok"] is False
    assert r["reason"] == "E_UNDECLARED_RESPONSE_FIELD"
    assert r["leaked"] == ("goblin_trace",)


def test_a_declared_field_cannot_be_silently_absent():
    s = _platform()
    r = respond(s, "1.0", "get_document", {"doc_id": "d"})
    assert r["reason"] == "E_INCOMPLETE_RESPONSE"
    assert set(r["absent"]) == {"state", "title"}


def test_a_conforming_response_passes():
    s = _platform()
    assert respond(s, "1.0", "create_task", {"task_id": "t1"})[
        "ok"] is True


# ── purity and determinism ─────────────────────────────────────────────

def test_no_operation_mutates_its_input_state():
    s = _platform()
    frozen = api.canon(s)
    evolve(s, "1.0", "1.1", V1)
    deprecate(s, "1.0", "create_task", "2.0")
    request(s, "1.0", "get_document", {"doc_id": "d"}, True)
    assert api.canon(s) == frozen


def test_deterministic_replay():
    assert api.canon(_platform()) == api.canon(_platform())
