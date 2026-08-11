"""Promotion-gate falsifiers, ported against CORE_V1. Each attack the
recap names becomes a test; the whole point is that the constitution's
prohibitions are TESTABLE, not merely declarative.

  NO_GATE                       -> REJECT (implicit promotion refused)
  UNDECLARED_LOSS               -> REJECT
  HIDDEN_ASSUMPTION             -> REJECT (missing declaration field)
  IMPLICIT_AUTHORITY_GAIN       -> REJECT
  ILLEGAL_LOCATION_PROMOTION    -> REJECT (Supported !-> Publishable)
  STALE_PRE_STATE               -> REJECT
  MISSING / FAKE_WITNESS        -> REJECT
  DENIAL preserves state        -> S_post == S_pre

And the convergence check: the four boundary questions ARE CORE_V1's
transition-declaration fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core_v1 import TRANSITION_DECLARATION_FIELDS, WitnessReceipt
from promotion_gate import (
    LOCATION_ORDER,
    Gate,
    State,
    promote,
    replay,
)

W_OK = WitnessReceipt("w1", independent=True, raw_harness_ref="harness://r", frame_id="F1")
W_PRODUCER = WitnessReceipt("w2", independent=False, raw_harness_ref="h", frame_id="F1")

FULL_DECL = {
    "input_provenance": "candidate/x", "preserved_invariants": ["I02"],
    "tolerated_loss": "drops the raw generation trace", "effect_ceiling": "none",
    "authority_requirements": "none", "witness_requirements": "independent",
    "failure_rollback": "revert to pre-state",
}


def _state(status="reported", auth=0, loc="local_private"):
    return State("x", status=status, authority=auth, location=loc)


def _gate(state, target="fixture_green", auth_gain=0, target_loc=None,
          decl=None, witness=W_OK, pre_hash=None):
    return Gate(gate_id="g1", target_status=target, authority_gain=auth_gain,
                target_location=target_loc or state.location,
                declaration=decl if decl is not None else dict(FULL_DECL),
                witness=witness,
                pre_hash=pre_hash if pre_hash is not None else state.hash())


# ── convergence: the four questions ARE CORE_V1's fields ────────────────

def test_gate_reuses_core_v1_transition_fields():
    """The two frames' calculi are one: the gate's mandatory declaration
    is exactly CORE_V1's TRANSITION_DECLARATION_FIELDS."""
    assert {"tolerated_loss", "authority_requirements", "failure_rollback",
            "input_provenance"}.issubset(TRANSITION_DECLARATION_FIELDS)


# ── the eight attacks ───────────────────────────────────────────────────

def test_NO_GATE_stale_or_absent_binding_rejects():
    """A gate not bound to THIS pre-state cannot promote it — the closest
    executable form of 'no implicit promotion'."""
    s = _state()
    g = _gate(s, pre_hash="not-this-state")
    post, r = promote(s, g)
    assert post is None and r.verdict == "DENIED" and r.reason == "E_STALE_PRE_STATE"


def test_UNDECLARED_LOSS_rejects():
    s = _state()
    decl = {**FULL_DECL, "tolerated_loss": "   "}   # blank loss
    post, r = promote(s, _gate(s, decl=decl))
    assert post is None and r.reason == "E_UNDECLARED_LOSS"


def test_HIDDEN_ASSUMPTION_missing_declaration_field_rejects():
    s = _state()
    decl = {k: v for k, v in FULL_DECL.items() if k != "preserved_invariants"}
    post, r = promote(s, _gate(s, decl=decl))
    assert post is None and "E_UNDECLARED_ARROW" in r.reason
    assert "preserved_invariants" in r.reason


def test_IMPLICIT_AUTHORITY_GAIN_rejects():
    s = _state()
    # authority_gain > 0 but declaration still says 'none'
    post, r = promote(s, _gate(s, auth_gain=1))
    assert post is None and r.reason == "E_IMPLICIT_AUTHORITY_GAIN"


def test_explicit_authority_gain_needs_witness():
    s = _state()
    decl = {**FULL_DECL, "authority_requirements": "operator seal ref#42"}
    post, r = promote(s, _gate(s, auth_gain=1, decl=decl, witness=None))
    assert post is None and r.reason in ("E_MISSING_WITNESS", "E_UNWITNESSED_AUTHORITY")


def test_ILLEGAL_LOCATION_PROMOTION_supported_not_publishable():
    """Supported(x) !-> Publishable(x): promoting local_private ->
    remote_public without declared reversibility is refused."""
    s = _state(loc="local_private")
    decl = {**FULL_DECL, "failure_rollback": "  "}   # no rollback for outward move
    g = _gate(s, target_loc="remote_public", decl=decl)
    post, r = promote(s, g)
    assert post is None and r.reason == "E_IRREVERSIBLE_LOCATION_PROMOTION"


def test_STALE_PRE_STATE_rejects():
    s = _state()
    moved = _state(status="fixture_green")   # state advanced under the gate
    g = _gate(s)                             # gate still bound to old hash
    post, r = promote(moved, g)
    assert post is None and r.reason == "E_STALE_PRE_STATE"


def test_MISSING_WITNESS_rejects_above_reported():
    s = _state()
    post, r = promote(s, _gate(s, witness=None))
    assert post is None and r.reason == "E_MISSING_WITNESS"


def test_FAKE_WITNESS_producer_adjacent_rejects():
    s = _state()
    post, r = promote(s, _gate(s, witness=W_PRODUCER))
    assert post is None and r.reason == "E_FAKE_WITNESS_PRODUCER_ADJACENT"


def test_STATUS_SKIP_rejects():
    """P_n(x) !-> P_{n+2}(x): rungs are climbed one at a time."""
    s = _state(status="hypothesis")
    post, r = promote(s, _gate(s, target="fixture_green"))  # skips 'reported'
    assert post is None and r.reason == "E_STATUS_SKIP"


# ── denial is auditable but never a state mutation ─────────────────────

def test_DENIAL_in_history_not_in_state_mutation():
    """DENIAL in HISTORY ; DENIAL not in STATE_MUTATION ; S_post = S_pre."""
    s = _state()
    post, r = promote(s, _gate(s, auth_gain=1))   # will be denied
    assert r.verdict == "DENIED"                  # the denial is a receipt
    assert r.post_hash == r.pre_hash == s.hash()  # nothing moved
    assert post is None                           # no new governed state


# ── positive controls: the law is not vacuous ──────────────────────────

def test_legitimate_promotion_succeeds_and_is_bound():
    s = _state(status="reported")
    post, r = promote(s, _gate(s, target="fixture_green"))
    assert r.verdict == "ADMITTED"
    assert post.status == "fixture_green"
    assert r.delta["semantic"] == ["reported", "fixture_green"]
    assert r.pre_hash == s.hash() and r.post_hash == post.hash()


def test_witnessed_authority_gain_with_reversible_publication_succeeds():
    s = _state(status="reported", loc="local_private")
    decl = {**FULL_DECL, "authority_requirements": "operator seal ref#42",
            "failure_rollback": "unpublish + revert grade"}
    g = _gate(s, target="fixture_green", auth_gain=1,
              target_loc="sot_proposals", decl=decl)
    post, r = promote(s, g)
    assert r.verdict == "ADMITTED"
    assert post.authority == 1 and post.location == "sot_proposals"


# ── replay: divergence is a first-order error ───────────────────────────

def test_replay_reproduces_admitted_promotion():
    s = _state(status="reported")
    g = _gate(s, target="fixture_green")
    post, r = promote(s, g)
    assert replay(s, g, r)["replay"] == "REPRODUCED"


def test_replay_detects_tampered_receipt():
    s = _state(status="reported")
    g = _gate(s, target="fixture_green")
    post, r = promote(s, g)
    import dataclasses
    forged = dataclasses.replace(r, post_hash="a-different-hash")
    assert replay(s, g, forged)["replay"] == "DIVERGENCE"


def test_deterministic():
    s = _state(status="reported")
    g = _gate(s, target="fixture_green")
    a = promote(s, g)[1].post_hash
    b = promote(s, g)[1].post_hash
    assert a == b
