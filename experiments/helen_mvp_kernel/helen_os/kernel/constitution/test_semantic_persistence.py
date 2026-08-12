"""The Hamilton test, executed: a trace that passes all four ceilings
locally AND transactionally, replays exactly — and still inverts the
meaning of `authority=false`. Replayability != semantic persistence.
First candidate to earn fifth-ceiling candidacy, honestly bounded.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import semantic_persistence as sp
from semantic_persistence import (
    STANDARD_INVARIANTS,
    SemanticDelta,
    drift_trace,
    fifth_ceiling_candidacy,
    hamilton_test,
    initial_state,
    non_kernel_trace,
    persistence_gate,
    pi_k,
    replay_is_exact,
    run_trace,
)


# ── the witness trace passes everything the four ceilings can see ──────

def test_the_drift_trace_is_locally_admissible_on_all_four():
    h = hamilton_test(initial_state(), drift_trace(), STANDARD_INVARIANTS)
    assert h["all_local_admissible"] is True


def test_the_drift_trace_passes_transactional_evaluation():
    """The composed-flow, identity, evidence and premise evaluators all
    ADMIT it — meaning is invisible to them under the current model."""
    h = hamilton_test(initial_state(), drift_trace(), STANDARD_INVARIANTS)
    assert h["transactional_verdict"] == "ADMIT"


def test_the_drift_trace_replays_exactly():
    """R(S_t, H) = S_t holds. The ledger is immaculate."""
    assert replay_is_exact(initial_state(), drift_trace()) is True


# ── and yet: the kernel meaning is inverted ─────────────────────────────

def test_pi_k_drifts_from_proposal_to_binding():
    states = run_trace(initial_state(), drift_trace())
    assert pi_k(states[0])["assistant_output"] == \
        "a proposal, never a decree"
    assert pi_k(states[-1])["assistant_output"] == "binding"


def test_the_hamilton_witness_is_found():
    """exists tau : C*(tau)=1 /\\ pi_K(S_0) != pi_K(S_n) — constructed."""
    h = hamilton_test(initial_state(), drift_trace(), STANDARD_INVARIANTS)
    assert h["witness_found"] is True
    assert h["kernel_drifted"] is True
    assert h["drifted_terms"] == ["assistant_output"]
    assert h["replay_is_exact"] is True          # BOTH hold at once
    assert h["law"] == "Replayability != semantic persistence"


def test_pi_k_projects_away_everything_non_kernel():
    assert set(pi_k(initial_state())) == set(sp.KERNEL_TERMS)
    h = hamilton_test(initial_state(), non_kernel_trace(),
                      STANDARD_INVARIANTS)
    assert h["kernel_drifted"] is False
    assert h["witness_found"] is False


# ── the repair: the persistence gate refuses drift by name ──────────────

def test_the_persistence_gate_refuses_unauthorized_drift():
    v = persistence_gate(initial_state(), drift_trace(),
                         STANDARD_INVARIANTS)
    assert v["verdict"] == "REJECT"
    assert v["reason"] == "E_SEMANTIC_DRIFT"
    assert v["drifted_terms"] == ["assistant_output"]


def test_an_explicit_amendment_grant_admits_the_same_edits():
    """Meaning-change is not forbidden — UNAUTHORIZED meaning-change
    is. An amendment grant is the lawful door."""
    granted = tuple(
        SemanticDelta(d.delta_id, d.term, d.new_meaning,
                      dict(d.local_ok), amendment_grant=(i == 0))
        for i, d in enumerate(drift_trace()))
    v = persistence_gate(initial_state(), granted, STANDARD_INVARIANTS)
    assert v["verdict"] == "ADMIT"
    assert v["reason"] == "KERNEL_AMENDED_UNDER_GRANT"


def test_a_non_kernel_edit_admits_with_kernel_preserved():
    v = persistence_gate(initial_state(), non_kernel_trace(),
                         STANDARD_INVARIANTS)
    assert v["verdict"] == "ADMIT"
    assert v["reason"] == "KERNEL_PRESERVED"


def test_a_ceiling_breach_is_still_a_ceiling_breach():
    """Persistence sits ON TOP of the four ceilings, it does not
    replace them: a trace with a real composed-flow violation is
    refused as E_CEILING_BREACH before persistence is even asked."""
    bad = (SemanticDelta("d_bad", "ui_theme", "x",
                         {c: True for c in sp.ccl.CEILINGS}),)

    def flowed(deltas):
        return (sp.ccl.Delta("f1", dict(sp.CLEAN), flow_from="X",
                             writes=frozenset({"b"})),
                sp.ccl.Delta("f2", dict(sp.CLEAN), flow_from="b",
                             flow_to="Z", writes=frozenset({"Z"})))
    original = sp.as_ccl_trace
    sp.as_ccl_trace = flowed
    try:
        v = persistence_gate(initial_state(), bad, STANDARD_INVARIANTS)
    finally:
        sp.as_ccl_trace = original
    assert v["verdict"] == "REJECT"
    assert v["reason"] == "E_CEILING_BREACH"


# ── fifth-ceiling candidacy: earned, and honestly bounded ───────────────

def test_the_first_fifth_ceiling_candidate_is_earned():
    """The committed machinery set the bar itself: passes
    transactional, still invalid. The Hamilton witness meets it."""
    c = fifth_ceiling_candidacy()
    assert c["fifth_ceiling_earned"] is True
    assert c["all_caught_by_transactional_eval"] is False
    assert c["witness"]["replay_is_exact"] is True
    assert c["witness"]["kernel_drifted"] is True


def test_the_candidacy_is_bounded_not_crowned():
    """Earned under the CURRENT state model; whether it reduces to
    SCOPE over a semantically enriched state stays open; completeness
    stays UNKNOWN."""
    c = fifth_ceiling_candidacy()
    assert c["earned_under"] == "CURRENT_STATE_MODEL"
    assert "SCOPE" in c["open_question"]
    assert "unresolved" in c["open_question"]
    assert c["completeness"] == "UNKNOWN"
    assert "falsifies adequacy" in c["adequacy_update"]


def test_each_kernel_term_drift_is_detected_individually():
    for term in sp.KERNEL_TERMS:
        trace = (SemanticDelta(f"d_{term}", term, "drifted meaning"),)
        h = hamilton_test(initial_state(), trace, STANDARD_INVARIANTS)
        assert h["kernel_drifted"] is True
        assert h["drifted_terms"] == [term]


def test_deterministic():
    assert sp.canon(fifth_ceiling_candidacy()) == \
        sp.canon(fifth_ceiling_candidacy())
    assert sp.canon(hamilton_test(initial_state(), drift_trace(),
                                  STANDARD_INVARIANTS)) == \
        sp.canon(hamilton_test(initial_state(), drift_trace(),
                               STANDARD_INVARIANTS))
