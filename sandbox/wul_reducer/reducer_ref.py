"""
WUL reducer — NON-SOVEREIGN REFERENCE implementation.

authority      = false
canon          = NO_SHIP
kernel_effect  = none
ledger_effect  = none

This is NOT the sovereign reducer. The sovereign reducer lives in helen_os/governance/**
and is MAYOR-routed, not written by the non-sovereign shell. This module is a *reference
oracle* whose only purpose is to make the conformance vectors in REDUCER_SPEC_V0 (§5, T1-T7)
fail MECHANICALLY rather than rhetorically. It implements, as a pure deterministic function:

  - §2 transition graph (legal moves + forbidden moves with explicit REJECT codes)
  - §3 Admit(c) predicate (the PENDING_REVIEW -> ADMITTED guard)
  - §4 passage laws L1-L5 (the five schema $comments, executable)

Spec: docs/wul/REDUCER_SPEC_V0.md   (the contract this oracle satisfies)

Determinism (§6): reduce() is a pure function of (claim, target). No wall-clock, no RNG,
no I/O. Same inputs -> same verdict. Any timestamp lives in the claim, not the reducer.

Reject-code reconciliation (two spec articulations converge):
  on-disk spec E_*        operator articulation REJECT_*
  -------------------     ---------------------------------
  E_SKIP_REVIEW       <-> REJECT_FORBIDDEN_TRANSITION (PENDING->ADMITTED)
  E_NO_HASH           <-> REJECT_NO_HASH
  E_SPEC_CEILING      <-> REJECT_SPEC_CEILING
  E_TERMINAL_FROZEN   <-> REJECT_TERMINAL_FROZEN
  E_TERMINAL_CONSIST  <-> REJECT_TERMINAL_CONFLICT (L4)
  E_REASON_REQUIRED   <-> REJECT_REASON_MISSING    (L5)
  E_REPLAY_FAIL       <-> REJECT_REPLAY_MISMATCH
This module uses the on-disk E_* codes (the repo SOT artifact).
"""

# ── ladder ranks (off-ladder terminals excluded) ──────────────────────────────
_RANK = {
    "PENDING": 0,
    "PENDING_REVIEW": 1,
    "ADMITTED": 2,
    "SEALED": 3,
    "REPLAYABLE": 4,
}
_TERMINAL = {"REJECTED", "SUPERSEDED"}


def _rank(state):
    return _RANK.get(state, -1)


def ALLOW(next_state):
    return ("ALLOW", next_state)


def REJECT(code):
    return ("REJECT", code)


def reduce(claim, target):
    """Pure reducer. claim: dict of fields; target: requested next admission_state.

    Returns ("ALLOW", next_state) or ("REJECT", code). Fail-closed: any move not
    explicitly legal is REJECT(E_FORBIDDEN).
    """
    state = claim["admission_state"]
    terminal = claim.get("terminal", state in _TERMINAL)

    # ── L4 TERMINAL CONSISTENCY (checked before any action) ───────────────────
    # terminal == (admission_state in {REJECTED, SUPERSEDED})
    if terminal != (state in _TERMINAL):
        return REJECT("E_TERMINAL_CONSIST")

    # ── L5 REJECTION REASON REQUIRED ──────────────────────────────────────────
    if terminal and claim.get("rejection_reason") is None:
        return REJECT("E_REASON_REQUIRED")

    # ── L3 TERMINAL FROZEN (no exit from REJECTED/SUPERSEDED) ──────────────────
    if state in _TERMINAL:
        return REJECT("E_TERMINAL_FROZEN")

    # ── L2 SPECULATIVE CEILING (WUL_CORE firewall: Ⓢ ↛ ✅/⚰️/🔁) ───────────────
    # Dedicated law — caps regardless of max_admission_state, checked before max-rank.
    if claim.get("claim_class") == "SPECULATIVE" and target in ("ADMITTED", "SEALED", "REPLAYABLE"):
        return REJECT("E_SPEC_CEILING")

    # ── max_admission_state invariant (every transition) ──────────────────────
    max_state = claim.get("max_admission_state", "REPLAYABLE")
    if target not in _TERMINAL and _rank(target) > _rank(max_state):
        return REJECT("E_STATE_GT_MAX")

    # ── rejection edge: any non-terminal -> REJECTED (reason required) ─────────
    if target == "REJECTED":
        if claim.get("rejection_reason") is None:
            return REJECT("E_REASON_REQUIRED")
        return ALLOW("REJECTED")

    # ── supersede edge: ADMITTED|SEALED -> SUPERSEDED ─────────────────────────
    if target == "SUPERSEDED":
        if state in ("ADMITTED", "SEALED"):
            return ALLOW("SUPERSEDED")
        return REJECT("E_FORBIDDEN")

    # ── PENDING ───────────────────────────────────────────────────────────────
    if state == "PENDING":
        if target == "PENDING_REVIEW":
            if claim.get("evidence"):
                return ALLOW("PENDING_REVIEW")
            return REJECT("E_NO_RECEIPT")
        if target in ("ADMITTED", "SEALED", "REPLAYABLE"):
            return REJECT("E_SKIP_REVIEW")
        return REJECT("E_FORBIDDEN")

    # ── PENDING_REVIEW -> ADMITTED : the Admit(c) guard (§3) ───────────────────
    if state == "PENDING_REVIEW":
        if target == "ADMITTED":
            return _admit(claim)
        if target in ("SEALED", "REPLAYABLE"):
            return REJECT("E_SKIP_SEAL")
        if _rank(target) < _rank(state):
            return REJECT("E_REVERSE")
        return REJECT("E_FORBIDDEN")

    # ── ADMITTED ──────────────────────────────────────────────────────────────
    if state == "ADMITTED":
        if target == "SEALED":
            return ALLOW("SEALED")
        if target == "REPLAYABLE":
            return REJECT("E_SKIP_SEAL")   # must pass through SEAL first
        if _rank(target) < _rank(state):
            return REJECT("E_REVERSE")
        return REJECT("E_FORBIDDEN")

    # ── SEALED ────────────────────────────────────────────────────────────────
    if state == "SEALED":
        if target == "REPLAYABLE":
            if claim.get("replay_check") == "PASS":
                return ALLOW("REPLAYABLE")
            return REJECT("E_REPLAY_FAIL")
        if _rank(target) < _rank(state):
            return REJECT("E_REVERSE")     # no backward arrow out of SEALED
        return REJECT("E_FORBIDDEN")

    # ── REPLAYABLE (terminal-immutable fact) ──────────────────────────────────
    if state == "REPLAYABLE":
        return REJECT("E_FORBIDDEN")

    return REJECT("E_FORBIDDEN")


def _admit(claim):
    """Admit(c) for PENDING_REVIEW -> ADMITTED (§3 + §4 laws, ordered fail-closed)."""
    # L2 SPECULATIVE CEILING (checked first: Spec class caps regardless of other fields)
    if claim.get("claim_class") == "SPECULATIVE":
        return REJECT("E_SPEC_CEILING")
    # L1 NO-HASH-NO-PROMOTE
    if claim.get("evidence_hash") is None:
        return REJECT("E_NO_HASH")
    # HasReceipt
    if not claim.get("evidence"):
        return REJECT("E_NO_RECEIPT")
    # GateGreen (K8 ∧ Kτ ∧ Kρ ∧ K-wul ∧ LEGORACLE)
    if not claim.get("gate_green", False):
        return REJECT("E_GATE_RED")
    # CanonAdmit clause: HumanSeal (operator only — reducer cannot self-confer)
    if not claim.get("human_seal", False):
        return REJECT("E_NO_SEAL")
    return ALLOW("ADMITTED")
