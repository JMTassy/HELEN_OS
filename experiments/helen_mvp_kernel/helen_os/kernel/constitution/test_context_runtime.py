"""Phase A item 7, adversarially tested: model output cannot enter or
be promoted to OBSERVED; the derived index is never authoritative and
never survives erasure; retrieval counts roots and cannot un-flag a
contradiction; an assembly is structurally ephemeral and refuses to
become truth; cross-tenant and absent are one answer everywhere.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import context_runtime as cx
from context_runtime import (
    assemble_context,
    authoritative_read,
    boot,
    context_invariant,
    erase_evidence,
    link,
    persist_assembly,
    promote_evidence,
    provision_tenant,
    rebuild_index,
    register_evidence,
    retrieve,
)


def _platform():
    s = boot()
    s, _ = provision_tenant(s, "A")
    s, _ = provision_tenant(s, "B")
    s, _ = register_evidence(s, "A", "e1", "sha:1", "msg:171b",
                             "OBSERVED", "human")
    s, _ = register_evidence(s, "A", "e2", "sha:2", "fwd:171b",
                             "REPORTED", "system")
    s, _ = register_evidence(s, "A", "e3", "sha:3", "llm:run9",
                             "MODEL_DERIVED", "model")
    s, _ = register_evidence(s, "B", "b1", "sha:9", "msg:zz",
                             "OBSERVED", "human")
    s, _ = link(s, "A", "e2", "e1", "derives_from")
    s, _ = rebuild_index(s, "A")
    return s


# ── admission ──────────────────────────────────────────────────────────

def test_evidence_enters_only_fully_typed():
    s = boot()
    s, _ = provision_tenant(s, "A")
    _, r = register_evidence(s, "A", "x", "", "src", "OBSERVED",
                             "human")
    assert r["reason"] == "E_UNPROVENANCED_EVIDENCE"
    _, r = register_evidence(s, "A", "x", "sha:1", None, "OBSERVED",
                             "human")
    assert r["reason"] == "E_UNPROVENANCED_EVIDENCE"
    _, r = register_evidence(s, "A", "x", "sha:1", "src", "VIBES",
                             "human")
    assert r["reason"] == "E_UNKNOWN_GRADE"


def test_a_model_is_an_author_never_a_root():
    s = boot()
    s, _ = provision_tenant(s, "A")
    _, r = register_evidence(s, "A", "m1", "sha:m", "llm:run",
                             "OBSERVED", "model")
    assert r["reason"] == "E_MODEL_OUTPUT_AS_OBSERVED"
    s, ok = register_evidence(s, "A", "m1", "sha:m", "llm:run",
                              "MODEL_DERIVED", "model")
    assert ok["ok"] is True


def test_model_derived_can_never_be_promoted_to_observed():
    s = _platform()
    _, r = promote_evidence(s, "A", "e3", "OBSERVED",
                            witness="human:jm")
    assert r["reason"] == "E_MODEL_SELF_PROMOTION"


def test_reported_rises_only_with_a_named_witness():
    s = _platform()
    _, r = promote_evidence(s, "A", "e2", "OBSERVED", witness=None)
    assert r["reason"] == "E_UNWITNESSED_PROMOTION"
    s, ok = promote_evidence(s, "A", "e2", "OBSERVED",
                             witness="primary:msg:171b")
    assert ok["grade"] == "OBSERVED"


# ── the one-answer law everywhere ──────────────────────────────────────

def test_cross_tenant_and_absent_are_one_answer():
    s = _platform()
    cross = authoritative_read(s, "B", "e1")     # A's row, from B
    absent = authoritative_read(s, "B", "nope")
    assert cross == absent
    assert cross["reason"] == "E_UNKNOWN_EVIDENCE"
    _, lc = link(s, "B", "b1", "e1", "supports")   # cross-tenant edge
    _, la = link(s, "B", "b1", "ghost", "supports")
    assert lc["reason"] == la["reason"] == "E_UNKNOWN_EVIDENCE"


def test_edges_are_typed_and_never_reflexive():
    s = _platform()
    _, r = link(s, "A", "e1", "e2", "resembles")
    assert r["reason"] == "E_UNKNOWN_EDGE_KIND"
    _, r = link(s, "A", "e1", "e1", "supports")
    assert r["reason"] == "E_SELF_EDGE"


# ── derived index ──────────────────────────────────────────────────────

def test_retrieval_is_never_authoritative_and_reports_lag():
    s = _platform()
    r = retrieve(s, "A", ("e1", "e2"))
    assert r["ok"] is True and r["authoritative"] is False
    assert r["index_lag"] == 0
    s, _ = register_evidence(s, "A", "e4", "sha:4", "msg:new",
                             "OBSERVED", "human")
    r2 = retrieve(s, "A", ("e1",))
    assert r2["index_lag"] > 0            # the store moved on


def test_retrieval_counts_roots_not_items():
    """e2 derives_from e1: two items, one root — three artifacts are
    not three witnesses at read time either."""
    s = _platform()
    r = retrieve(s, "A", ("e1", "e2"))
    assert r["n_items"] == 2
    assert r["n_roots"] == 1


def test_a_registered_contradiction_is_flagged_at_read_time():
    s = _platform()
    s, _ = register_evidence(s, "A", "e5", "sha:5", "msg:other",
                             "OBSERVED", "human")
    s, _ = link(s, "A", "e1", "e5", "contradicts")
    s, _ = rebuild_index(s, "A")
    r = retrieve(s, "A", ("e1", "e5"))
    assert r["contradictions"] == (("e1", "e5"),)
    lone = retrieve(s, "A", ("e5",))
    assert lone["contradictions"] == ()


def test_the_index_never_answers_for_the_other_tenant():
    s = _platform()
    s, _ = rebuild_index(s, "B")
    r = retrieve(s, "B", ("e1",))
    assert r["reason"] == "E_UNKNOWN_EVIDENCE"


# ── ephemeral assembly ─────────────────────────────────────────────────

def test_an_assembly_cites_registered_rows_only():
    s = _platform()
    r = assemble_context(s, "A", ("e1", "raw text pasted in"), 10)
    assert r["reason"] == "E_UNSOURCED_CONTEXT_ITEM"
    r = assemble_context(s, "A", ("e1", "ghost"), 10)
    assert r["reason"] == "E_UNKNOWN_EVIDENCE"


def test_an_assembly_is_ephemeral_and_flags_cannot_be_suppressed():
    s = _platform()
    frozen = cx.canon(s)
    r = assemble_context(s, "A", ("e1", "e2"), 10)
    assert r["ok"] is True and r["ephemeral"] is True
    assert r["persisted"] is False
    assert r["response_grade"] == "REPRESENTATION"
    assert r["n_roots"] == 1
    assert cx.canon(s) == frozen          # no state was written
    sup = assemble_context(s, "A", ("e1",), 10,
                           suppress_contradictions=True)
    assert sup["reason"] == "E_CONTRADICTION_SUPPRESSED"


def test_the_budget_is_enforced_in_the_data_path():
    s = _platform()
    r = assemble_context(s, "A", ("e1", "e2", "e3"), budget_items=2)
    assert r["reason"] == "E_CONTEXT_BUDGET"


def test_persisting_an_assembly_is_refused_always():
    s = _platform()
    a = assemble_context(s, "A", ("e1",), 10)
    s2, r = persist_assembly(s, "A", a)
    assert r["reason"] == "E_CONTEXT_PERSISTED_AS_TRUTH"
    assert r["persisted"] is False
    assert cx.canon(s2) == cx.canon(s)


# ── erasure ────────────────────────────────────────────────────────────

def test_erasure_is_total_and_leaves_a_content_free_tombstone():
    s = _platform()
    s, r = erase_evidence(s, "A", "e1")
    assert r["ok"] is True and len(r["tombstone"]) == 16
    after = authoritative_read(s, "A", "e1")
    never = authoritative_read(s, "A", "never_was")
    assert after == never                 # indistinguishable
    assert "e1" not in s["tenants"]["A"]["index"]
    assert all("e1" not in (a, b)
               for (a, b, _k) in s["tenants"]["A"]["edges"])
    inv = context_invariant(s)
    assert inv["holds"] is True


def test_a_ghost_index_entry_breaks_the_invariant():
    s = _platform()
    # hand-forge the breach: index keeps a row the store lost
    t = dict(s["tenants"]["A"])
    t["store"] = {k: v for k, v in t["store"].items() if k != "e1"}
    s2 = {**s, "tenants": {**s["tenants"], "A": t}}
    inv = context_invariant(s2)
    assert inv["holds"] is False
    assert "e1@A" in inv["orphan_index_entries"]


# ── purity and determinism ─────────────────────────────────────────────

def test_no_operation_mutates_its_input_state():
    s = _platform()
    frozen = cx.canon(s)
    register_evidence(s, "A", "zz", "sha:z", "src", "OBSERVED",
                      "human")
    promote_evidence(s, "A", "e2", "OBSERVED", "w")
    link(s, "A", "e1", "e3", "supports")
    rebuild_index(s, "A")
    erase_evidence(s, "A", "e1")
    persist_assembly(s, "A", {})
    assert cx.canon(s) == frozen


def test_deterministic_replay():
    assert cx.canon(_platform()) == cx.canon(_platform())
    a = assemble_context(_platform(), "A", ("e1", "e2"), 10)
    b = assemble_context(_platform(), "A", ("e1", "e2"), 10)
    assert a["assembly_digest"] == b["assembly_digest"]
