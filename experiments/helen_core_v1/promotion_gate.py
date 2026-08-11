"""Promotion Gate Calculus — ported against CORE_V1 primitives.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Convergence port: the other frame derived this from the state side; this
frame already had the transition side (validate_transition_declaration,
the status ladder, admission_gate). This module unifies them so the two
frames' calculi are provably one object.

    STATE_n  ->  CANDIDATE  ->  GATE  ->  RECEIPT  ->  STATE_{n+1}

The core law:  P_n(x) does not imply P_{n+1}(x). No property crosses a
boundary without an explicit gate. And the deeper law:

    EVERY PROMOTION MUST NAME ITS LOSS.

A single gate governs three previously-separate promotions:

    G = (delta_semantic, delta_authority, delta_storage)

  semantic : status rung on the CORE_V1 ladder (hypothesis..admitted)
  authority: authority grade gained (0 by default; >0 needs justification)
  storage  : location class (local_private / sot_proposals / remote_public)
             — Supported(x) does NOT imply Publishable(x).

Promote is a fail-closed PARTIAL function:  Promote(x, G) ~> y | REJECT.
A denial produces a NEGATIVE receipt and mutates nothing:

    DENIAL in HISTORY ;  DENIAL not in STATE_MUTATION ;  S_post = S_pre.

Deterministic: sha256 over canonical JSON; no wall-time, no randomness.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from core_v1 import (
    STATUSES,
    TRANSITION_DECLARATION_FIELDS,
    WitnessReceipt,
    canon,
    validate_transition_declaration,
)

# ── storage / location lattice: content admissibility != publishability ─
# Ordered from most private to most public. A promotion UP this lattice
# is a location promotion and needs its own gate leg.
LOCATION_ORDER = ("local_private", "sot_proposals", "remote_public")


def _loc_rank(loc: str) -> int:
    if loc not in LOCATION_ORDER:
        raise ValueError(f"E_UNKNOWN_LOCATION:{loc}")
    return LOCATION_ORDER.index(loc)


def _h(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class State:
    """A governed state at layer n: content + its three coordinates."""
    content_id: str
    status: str                       # semantic rung
    authority: int                    # authority grade (0 = A=0)
    location: str                     # storage class

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"E_UNTYPED_STATUS:{self.status}")
        _loc_rank(self.location)

    def hash(self) -> str:
        return _h((self.content_id, self.status, self.authority, self.location))


@dataclass(frozen=True)
class Gate:
    """G = (delta_semantic, delta_authority, delta_storage) + the four
    mandatory boundary declarations, a witness, and a pre_hash binding.

    The four questions are CORE_V1's TRANSITION_DECLARATION_FIELDS; a gate
    that omits any of them is not a gate."""
    gate_id: str
    target_status: str                # semantic delta (destination rung)
    authority_gain: int               # delta_authority
    target_location: str              # storage delta (destination class)
    declaration: dict                 # the four questions (+3), validated
    witness: WitnessReceipt | None
    pre_hash: str                     # binds the gate to a specific pre-state

    def __post_init__(self):
        if self.target_status not in STATUSES:
            raise ValueError(f"E_UNTYPED_TARGET_STATUS:{self.target_status}")
        _loc_rank(self.target_location)


@dataclass(frozen=True)
class Receipt:
    """R = (pre, delta, gate, witness, post). Says: THIS object, bound to
    THIS pre-state, crossed THIS gate with THESE witnesses and produced
    THIS post-state. A negative receipt has post == pre."""
    verdict: str                      # ADMITTED | DENIED
    pre_hash: str
    gate_id: str
    delta: dict
    witness_id: str
    post_hash: str
    reason: str = "OK"


def _reject(state: State, gate: Gate, reason: str) -> Receipt:
    """Fail-closed denial: a NEGATIVE receipt. S_post = S_pre — the denial
    is recorded (returned to the caller for the ledger) but mutates
    nothing about the governed state."""
    return Receipt(verdict="DENIED", pre_hash=state.hash(), gate_id=gate.gate_id,
                   delta={}, witness_id=(gate.witness.witness_id
                                         if gate.witness else ""),
                   post_hash=state.hash(),   # post == pre, by law
                   reason=reason)


def promote(state: State, gate: Gate) -> tuple[State | None, Receipt]:
    """The fail-closed partial function. Returns (new_state, receipt) on
    ADMIT, or (None, negative_receipt) on any denial. Every denial path
    leaves the input state byte-identical."""
    # STALE_PRE_STATE: the gate must be bound to THIS pre-state.
    if gate.pre_hash != state.hash():
        return None, _reject(state, gate, "E_STALE_PRE_STATE")

    # NO_GATE / UNDECLARED_LOSS / HIDDEN_ASSUMPTION: the four questions.
    ok, why = validate_transition_declaration(gate.declaration)
    if not ok:
        return None, _reject(state, gate, why)   # E_UNDECLARED_ARROW
    if not gate.declaration.get("tolerated_loss", "").strip():
        return None, _reject(state, gate, "E_UNDECLARED_LOSS")

    # SEMANTIC: one rung at a time, and every rung above 'reported' costs
    # an independent witness with a raw harness (the ladder law).
    si, ti = STATUSES.index(state.status), STATUSES.index(gate.target_status)
    if ti != si + 1:
        return None, _reject(state, gate, "E_STATUS_SKIP")   # P_n !-> P_{n+2}
    if gate.target_status != "reported":
        w = gate.witness
        if w is None:
            return None, _reject(state, gate, "E_MISSING_WITNESS")
        if not w.independent:
            return None, _reject(state, gate, "E_FAKE_WITNESS_PRODUCER_ADJACENT")
        if not w.raw_harness_ref:
            return None, _reject(state, gate, "E_FAKE_WITNESS_NO_HARNESS")

    # AUTHORITY: no implicit gain. Any authority_gain > 0 must be
    # explicitly justified in the declaration AND witnessed.
    if gate.authority_gain > 0:
        if not gate.declaration.get("authority_requirements", "").strip() \
                or gate.declaration.get("authority_requirements") == "none":
            return None, _reject(state, gate, "E_IMPLICIT_AUTHORITY_GAIN")
        if gate.witness is None:
            return None, _reject(state, gate, "E_UNWITNESSED_AUTHORITY")

    # STORAGE: Supported(x) !-> Publishable(x). A location promotion (up
    # the lattice) needs the gate to explicitly target it AND declare
    # reversibility for the outward move.
    if _loc_rank(gate.target_location) > _loc_rank(state.location):
        if not gate.declaration.get("failure_rollback", "").strip():
            return None, _reject(state, gate, "E_IRREVERSIBLE_LOCATION_PROMOTION")

    # all legs pass -> ADMIT. Construct the post-state and a bound receipt.
    post = State(content_id=state.content_id, status=gate.target_status,
                 authority=state.authority + gate.authority_gain,
                 location=gate.target_location)
    delta = {"semantic": [state.status, gate.target_status],
             "authority": gate.authority_gain,
             "storage": [state.location, gate.target_location]}
    receipt = Receipt(verdict="ADMITTED", pre_hash=state.hash(),
                      gate_id=gate.gate_id, delta=delta,
                      witness_id=(gate.witness.witness_id if gate.witness else ""),
                      post_hash=post.hash())
    return post, receipt


def replay(state: State, gate: Gate, receipt: Receipt) -> dict:
    """Replay must reproduce the result. A divergence is a first-order
    error, not a warning."""
    post, fresh = promote(state, gate)
    reproduced_post = post.hash() if post else state.hash()
    if reproduced_post != receipt.post_hash:
        return {"replay": "DIVERGENCE", "reason": "E_POST_HASH_DIVERGENCE"}
    if fresh.verdict != receipt.verdict:
        return {"replay": "DIVERGENCE", "reason": "E_VERDICT_DIVERGENCE"}
    return {"replay": "REPRODUCED", "verdict": fresh.verdict}
