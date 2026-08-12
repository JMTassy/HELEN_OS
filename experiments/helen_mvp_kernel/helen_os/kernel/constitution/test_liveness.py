"""Falsifiers for Witnessed Obligation Liveness — HOLD != DEADLOCK,
the obligation scheduler, witnessed resolution, admissibility distance
without self-approval, the one-shot transition capability, and the
combined safety-and-liveness frontier predicate.

The scheduler fixture uses THIS session's own Omega, generically:
a domain-deletion deadline must outrank an elegant theorem.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import liveness as lv
from liveness import (
    Hold,
    LiveObligation,
    NonceBook,
    Resolution,
    TransitionCapability,
    admissibility_distance,
    frontier_predicate,
    guided_step,
    hold_is_lawful,
    liveness_check,
    replay_extensional_check,
    resolve,
    schedule,
)


# ── HOLD != DEADLOCK ────────────────────────────────────────────────────

def test_a_hold_that_generates_nothing_is_an_eternal_hold():
    silent = Hold("o1", held_at=5)
    r = hold_is_lawful(silent)
    assert r["verdict"] == "E_ETERNAL_HOLD"
    assert "deadlock" in r["law"]


def test_a_hold_that_spawns_a_next_obligation_is_lawful():
    progressing = Hold("o1", held_at=5,
                       generates="NEXT_EVIDENTIARY_OBLIGATION",
                       next_obligation="o1-evidence-request")
    r = hold_is_lawful(progressing)
    assert r["verdict"] == "LAWFUL_HOLD"
    assert r["next_obligation"] == "o1-evidence-request"


def test_a_hold_generating_an_unknown_kind_is_refused():
    bad = Hold("o1", 5, generates="just_waiting", next_obligation="x")
    assert hold_is_lawful(bad)["verdict"] == "E_ETERNAL_HOLD"


# ── the liveness temporal check ─────────────────────────────────────────

def _crit(oid, opened, progress=(), reachable=True):
    return LiveObligation(oid, critical=True, reachable=reachable,
                          severity=1.0, irreversibility=1.0,
                          deadline_pressure=1.0, reachability=1.0,
                          discharge_cost=1.0, opened_at=opened,
                          progress_ticks=progress)


def test_a_stale_critical_obligation_violates_liveness():
    """Held 4 ticks past its last progress with no resolution — being
    fail-closed is not a licence to be fail-frozen."""
    o = _crit("sec-fix", opened=0)
    r = liveness_check(o, now=5, stale_after=3)
    assert r["verdict"] == "E_LIVENESS_VIOLATION"
    assert r["idle_ticks"] == 5
    assert "nothing critical may disappear" in r["law"]


def test_recent_progress_keeps_an_obligation_live():
    o = _crit("sec-fix", opened=0, progress=(4,))
    assert liveness_check(o, now=5, stale_after=3)["verdict"] == "LIVE"


def test_an_unreachable_critical_obligation_is_still_monitored():
    """Unreachable does not mean silently parkable — it must still
    show escalation progress or it violates liveness."""
    o = _crit("jmttt-deadline", opened=0, reachable=False)
    r = liveness_check(o, now=9, stale_after=3)
    assert r["verdict"] == "E_LIVENESS_VIOLATION"
    assert r["reachable"] is False


def test_non_critical_obligations_are_not_liveness_monitored():
    o = LiveObligation("branch-cleanup", critical=False, reachable=True,
                       severity=0.1, irreversibility=0.1,
                       deadline_pressure=0.1, reachability=1.0,
                       discharge_cost=1.0, opened_at=0)
    assert liveness_check(o, now=100)["monitored"] is False


# ── the scheduler: obligations, not intellectual attractiveness ────────

def test_the_deadline_dominates_the_elegant_theorem():
    """This session's own Omega, generically: a domain deletion
    tomorrow vs another architecture build."""
    domain = LiveObligation("domain-deletion-tomorrow", True, False,
                            severity=1.0, irreversibility=1.0,
                            deadline_pressure=1.0, reachability=0.8,
                            discharge_cost=0.2, opened_at=0)
    theorem = LiveObligation("elegant-new-theorem", False, True,
                             severity=0.3, irreversibility=0.1,
                             deadline_pressure=0.1, reachability=1.0,
                             discharge_cost=1.0, opened_at=0)
    sec = LiveObligation("command-injection-fix", True, True,
                         severity=0.9, irreversibility=0.5,
                         deadline_pressure=0.3, reachability=0.9,
                         discharge_cost=0.4, opened_at=0)
    r = schedule((theorem, domain, sec))
    assert r["selected"] == "domain-deletion-tomorrow"
    assert r["order"][0] == "domain-deletion-tomorrow"
    assert r["order"][-1] == "elegant-new-theorem"


def test_empty_omega_selects_nothing():
    assert schedule(())["reason"] == "E_EMPTY_OBLIGATION_SET"


def test_utility_is_deadline_and_reachability_weighted():
    reachable = _crit("a", 0)
    unreachable = LiveObligation("b", True, False, 1.0, 1.0, 1.0,
                                 reachability=0.0, discharge_cost=1.0,
                                 opened_at=0)
    assert reachable.utility() > unreachable.utility()  # R=0 sinks it


# ── witnessed resolution: the only three exits ─────────────────────────

def test_resolution_requires_a_witness_and_a_known_kind():
    with pytest.raises(ValueError, match="E_RESOLUTION_WITHOUT_WITNESS"):
        Resolution("o1", "WITNESSED_DISCHARGE", "")
    with pytest.raises(ValueError, match="E_UNKNOWN_RESOLUTION_KIND"):
        Resolution("o1", "JUST_DROPPED_IT", "w")


def test_impossibility_must_be_witnessed_not_asserted():
    o = _crit("unreachable-task", 0)
    r = resolve(o, Resolution("unreachable-task",
                              "WITNESSED_IMPOSSIBILITY",
                              "search-receipt#executed"))
    assert r["verdict"] == "RESOLVED" and r["leaves_omega"] is True


def test_a_resolution_for_the_wrong_obligation_is_refused():
    o = _crit("o1", 0)
    r = resolve(o, Resolution("o2", "EXPLICIT_ESCALATION", "w"))
    assert r["reason"] == "E_RESOLUTION_MISMATCH"


# ── admissibility distance: guide without self-approval ────────────────

def test_a_critical_failure_is_an_infinite_barrier():
    r = admissibility_distance(
        {"phi_safety": "FAIL", "phi_budget": "PASS"},
        weights={}, critical=frozenset({"phi_safety"}),
        authority_of_candidate=0.0)
    assert r["distance"] == float("inf")
    assert "does not imply ADMIT" in r["law"]


def test_distance_sums_noncritical_fails_and_unknowns():
    r = admissibility_distance(
        {"phi_a": "FAIL", "phi_b": "UNKNOWN", "phi_c": "PASS"},
        weights={"phi_a": {"alpha": 2.0}, "phi_b": {"beta": 0.5}},
        critical=frozenset(), authority_of_candidate=0.0)
    assert r["distance"] == 2.5 and r["admits"] is False


def test_a_candidate_carrying_authority_has_no_distance():
    r = admissibility_distance({}, {}, frozenset(),
                               authority_of_candidate=1.0)
    assert r["reason"] == "E_CANDIDATE_CARRIES_AUTHORITY"


def test_guided_step_picks_nearest_but_never_admits():
    r = guided_step({"c1": 3.0, "c2": 1.5, "c3": float("inf"),
                     "c4": None})
    assert r["selected"] == "c2" and r["admitted"] is False


def test_no_finite_candidate_yields_no_step():
    assert guided_step({"c1": float("inf")})["reason"] == \
        "E_NO_FINITE_CANDIDATE"


# ── one-shot transition capability ─────────────────────────────────────

def _kappa(expires=10, nonce="n1"):
    return TransitionCapability("hc", "hw", "hg", "SEND", expires, nonce)


def test_a_capability_executes_once_then_never_again():
    book = NonceBook()
    k = _kappa()
    first = book.invoke(k, "hc", "hw", "hg", now=1)
    assert first["verdict"] == "EXECUTED"
    second = book.invoke(k, "hc", "hw", "hg", now=2)
    assert second["reason"] == "E_NONCE_REPLAY"


def test_state_witness_or_candidate_drift_refuses():
    book = NonceBook()
    assert book.invoke(_kappa(), "OTHER", "hw", "hg", 1)["reason"] == \
        "E_CANDIDATE_DRIFT"
    assert book.invoke(_kappa(), "hc", "OTHER", "hg", 1)["reason"] == \
        "E_WITNESS_DRIFT"
    assert book.invoke(_kappa(), "hc", "hw", "OTHER", 1)["reason"] == \
        "E_STATE_DRIFT"


def test_an_expired_capability_refuses():
    book = NonceBook()
    assert book.invoke(_kappa(expires=5), "hc", "hw", "hg",
                       now=5)["reason"] == "E_CAPABILITY_EXPIRED"


# ── replay wins over narrative ─────────────────────────────────────────

def test_memory_disagreeing_with_replay_holds():
    r = replay_extensional_check("G_narrative", "G_replayed")
    assert r["verdict"] == "HOLD" and r["reason"] == "E_REPLAY_DIVERGENCE"
    assert replay_extensional_check("G", "G")["verdict"] == "CONSISTENT"


# ── the combined frontier predicate ────────────────────────────────────

def test_frontier_needs_both_safety_and_liveness():
    assert frontier_predicate(True, True)["frontier_held"] is True
    assert frontier_predicate(True, False)["frontier_held"] is False
    assert frontier_predicate(False, True)["frontier_held"] is False
    assert "nothing critical may disappear" in \
        frontier_predicate(True, True)["line"]


def test_deterministic():
    o = (_crit("a", 0), _crit("b", 0))
    assert lv.canon(schedule(o)) == lv.canon(schedule(o))
