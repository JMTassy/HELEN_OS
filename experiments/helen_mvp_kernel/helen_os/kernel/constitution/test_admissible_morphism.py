"""The six adversarial fixtures for the Admissible Causal Morphism
kernel, named in the ruling:

  1. orphan state
  2. duplicated lease
  3. evidence cloning
  4. locally-valid-but-globally-invalid composition
  5. retroactive authority
  6. equal-final-state / different-lawful-history

plus the positive control (a clean admission) and the two-graph law.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import admissible_morphism as am
from admissible_morphism import (
    CandidateMorphism,
    Graphs,
    LeaseBook,
    admit,
    authority_nonexpansive,
    constitutional_equiv,
    extensional_equiv,
    normalize,
    project_evidence,
)

# trivial gate/invariant for the fixtures: gate always agrees, the
# invariant forbids one poisoned state so I(S_t+1) has teeth.
GATE = lambda root, m: True                       # noqa: E731
INV = lambda s: s != "root:forbidden"             # noqa: E731


def _m(m_id="m1", src="root:s0", tgt="root:s1", lease="L1",
       t_auth=10, t_eff=15, ev=("transcript#1",), delta=0.0):
    return CandidateMorphism(m_id, source_root=src, target=tgt,
                             transformation="send", evidence_roots=frozenset(ev),
                             lease_id=lease, t_authorized=t_auth,
                             t_effect=t_eff, quantity_delta=delta)


def _book(**grants):
    b = LeaseBook()
    for k, v in (grants or {"L1": 1}).items():
        b.grant(k, v)
    return b


# ── positive control ────────────────────────────────────────────────────

def test_a_complete_candidate_is_admitted_and_mutates_the_world():
    r = admit(_m(), frozenset({"root:s0"}), _book(L1=1), INV, GATE, t_now=15)
    assert r["verdict"] == "ADMITTED" and r["world_mutates"] is True
    assert r["proof"].receipt and len(r["proof"].premises) == 5


# ── fixture 1: orphan state ─────────────────────────────────────────────

def test_orphan_state_cannot_anchor_a_transition():
    """A source root not in the world graph is an orphan — no lawful
    path leads to it, so nothing may be built on it."""
    r = admit(_m(src="root:nowhere"), frozenset({"root:s0"}),
              _book(L1=1), INV, GATE, t_now=15)
    assert r["verdict"] == "REJECTED" and r["reason"] == "E_ORPHAN_STATE"
    assert r["world_mutates"] is False and "orphan" in r["law"]


def test_orphan_reject_does_not_spend_the_lease():
    book = _book(L1=1)
    admit(_m(src="root:nowhere"), frozenset({"root:s0"}), book, INV,
          GATE, 15)
    assert book.available("L1") is True            # a doomed candidate is free


# ── fixture 2: duplicated lease ─────────────────────────────────────────

def test_a_single_use_lease_admits_once_then_is_exhausted():
    world = frozenset({"root:s0"})
    book = _book(L1=1)
    first = admit(_m("m1", tgt="root:s1"), world, book, INV, GATE, 15)
    assert first["verdict"] == "ADMITTED"
    second = admit(_m("m2", tgt="root:s2"), world, book, INV, GATE, 15)
    assert second["verdict"] == "REJECTED"
    assert second["reason"] == "E_LEASE_EXHAUSTED"
    assert "authority is linear" in second["law"]


# ── fixture 3: evidence cloning ─────────────────────────────────────────

def test_projection_cannot_manufacture_evidential_rank():
    """One transcript, five projections, still rank 1. Deterministic
    transformation conserves provenance roots."""
    roots = frozenset({"transcript#1042"})
    for view in ("crm", "deck", "email", "summary", "forecast"):
        p = project_evidence(roots, view)
        assert p["roots_out"] == roots and p["rank"] == 1
    # and ordinary cognition is authority-nonexpansive
    flat = authority_nonexpansive(1.0, "consensus_of_five_models")
    assert flat["expanded"] is False
    lifted = authority_nonexpansive(
        1.0, "signature", external_witness={"kind": "signature",
                                            "receipt": "sig:abc"})
    assert lifted["expanded"] is True and lifted["a_out"] == 2.0


def test_a_fake_external_witness_without_receipt_does_not_expand():
    r = authority_nonexpansive(1.0, "x",
                               external_witness={"kind": "signature"})
    assert r["expanded"] is False


# ── fixture 4: locally valid, globally invalid composition ─────────────

def test_two_local_admits_on_one_lease_break_the_global_history():
    """Each admit() would pass in isolation; sharing one single-use
    lease makes the COMPOSITION unlawful. Local receipt validity is
    not global history validity."""
    world = frozenset({"root:s0"})
    book = _book(L1=1)                              # ONE use, two morphisms
    r1 = admit(_m("m1", src="root:s0", tgt="root:s1"), world, book, INV,
               GATE, 15)
    # after m1 the world advances; m2 builds on s1 but the lease is gone
    r2 = admit(_m("m2", src="root:s1", tgt="root:s2"),
               frozenset({"root:s0", "root:s1"}), book, INV, GATE, 16)
    assert r1["verdict"] == "ADMITTED"
    assert r2["verdict"] == "REJECTED"             # the shared lease is spent
    assert r2["reason"] == "E_LEASE_EXHAUSTED"


def test_non_composable_history_is_caught_by_normalization():
    admitted = ((None, "root:s1", "root:s0"),
                (None, "root:s3", "root:s2"))       # s1 != s2: torn
    with pytest.raises(ValueError, match="E_NON_COMPOSABLE_HISTORY"):
        normalize("root:s0", admitted)


# ── fixture 5: retroactive authority ────────────────────────────────────

def test_authority_after_the_effect_is_refused():
    r = admit(_m(t_auth=20, t_eff=15), frozenset({"root:s0"}),
              _book(L1=1), INV, GATE, t_now=15)
    assert r["verdict"] == "REJECTED"
    assert r["reason"] == "E_RETROACTIVE_AUTHORITY"


def test_retroactive_reject_also_costs_no_lease():
    book = _book(L1=1)
    admit(_m(t_auth=20, t_eff=15), frozenset({"root:s0"}), book, INV,
          GATE, 15)
    assert book.available("L1") is True


# ── fixture 6: equal final state, different lawful history ─────────────

def test_same_final_state_is_not_constitutional_equivalence():
    """Two histories reach root:sZ. One spent lease L1 on evidence e1;
    the other spent L2 on e2. Extensionally equal, constitutionally
    distinct."""
    h1 = {"final_state": "root:sZ", "authority_path": ("L1",),
          "evidence_roots": frozenset({"e1"}), "leases_spent": ("L1",)}
    h2 = {"final_state": "root:sZ", "authority_path": ("L2",),
          "evidence_roots": frozenset({"e2"}), "leases_spent": ("L2",)}
    assert extensional_equiv(h1["final_state"], h2["final_state"]) is True
    c = constitutional_equiv(h1, h2)
    assert c["extensional"] is True
    assert c["constitutional"] is False
    assert "does not imply" in c["law"]


def test_identical_lawful_histories_are_constitutionally_equal():
    h = {"final_state": "root:sZ", "authority_path": ("L1",),
         "evidence_roots": frozenset({"e1"}), "leases_spent": ("L1",)}
    assert constitutional_equiv(h, dict(h))["constitutional"] is True


# ── the two graphs: W ⊊ A ───────────────────────────────────────────────

def test_rejected_morphisms_touch_audit_never_world():
    g = Graphs()
    world = frozenset({"root:s0"})
    book = _book(L1=1)
    good = _m("m1")
    g.record(good, admit(good, world, book, INV, GATE, 15))
    bad = _m("m2", src="root:nowhere")
    g.record(bad, admit(bad, world, _book(L1=1), INV, GATE, 15))
    assert len(g.world_edges) == 1                 # only the admitted one
    assert len(g.audit_edges) == 2                 # both attempts
    assert g.subset_holds() is True                # W subset of A


# ── the poststate invariant has teeth ──────────────────────────────────

def test_a_morphism_into_a_forbidden_state_is_refused():
    r = admit(_m(tgt="root:forbidden"), frozenset({"root:s0"}),
              _book(L1=1), INV, GATE, 15)
    assert r["reason"] == "E_POSTSTATE_INVARIANT"


# ── determinism ─────────────────────────────────────────────────────────

def test_deterministic():
    a = admit(_m(), frozenset({"root:s0"}), _book(L1=1), INV, GATE, 15)
    b = admit(_m(), frozenset({"root:s0"}), _book(L1=1), INV, GATE, 15)
    assert a["proof"].receipt == b["proof"].receipt
