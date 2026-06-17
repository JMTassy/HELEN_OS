#!/usr/bin/env python3
"""
WUL_REDUCER_V0 — reference reducer (NON-SOVEREIGN / NO_SHIP).

Executable companion to docs/wul/REDUCER_SPEC_V0.md. The reducer is the admission
boundary: it computes whether a candidate WUL claim may pass each rung of the
admission ladder. It does NOT create truth, confer authority, write the ledger, or
self-authorize canon. authority=false · canon=NO_SHIP · ledger_effect=none.

Hardening (this sync, BED 02/03 of the ALIVE GARDEN map):
  ③ REPLAY-DERIVED PREDICATES — `typed`, `has_hash`, `gate_green`, `seal_valid`,
     `det_replay` are DERIVED (recomputed / replay-attested), never trusted as
     caller-supplied flags on the claim. A claim cannot describe its own validity.
  ② UN-SELF-CONFERRABLE SEAL — CanonAdmit requires an external seal OBJECT bound to
     the candidate hash, issued by a role outside the proposer, whose receipt is known
     to the replay context. A bare `human_seal=true` flag is ignored.

Determinism (Kτ/Kρ): pure function of (state, target, claim, replay_context). No
wall-clock, no RNG, no env/UI state. Same inputs → same verdict. Unlisted → fail closed.

Spec: docs/wul/REDUCER_SPEC_V0.md  ·  schema: docs/specs/wul_claim_schema_v0.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

# ── States (admission ladder) ───────────────────────────────────────────────
S0_SYMBOL = "S0_SYMBOL"
S1_CLAIM = "S1_CLAIM"
S2_TYPED = "S2_TYPED"
S3_RECEIPTED = "S3_RECEIPTED"
S4_JUDGED = "S4_JUDGED"
S5_ADMITTED = "S5_ADMITTED"
S6_REPLAYABLE = "S6_REPLAYABLE"
S_REJECTED = "S_REJECTED"
S_SUPERSEDED = "S_SUPERSEDED"
S_TERMINAL = "S_TERMINAL"

LADDER = [S0_SYMBOL, S1_CLAIM, S2_TYPED, S3_RECEIPTED,
          S4_JUDGED, S5_ADMITTED, S6_REPLAYABLE]

# Terminal labels (sealed)
TERMINAL_ADMITTED = "TERMINAL_ADMITTED"
TERMINAL_REJECTED = "TERMINAL_REJECTED"
TERMINAL_REPLAYABLE = "TERMINAL_REPLAYABLE"
TERMINAL_SUPERSEDED = "TERMINAL_SUPERSEDED"

# L3 frozen set — S_TERMINAL only. S_REJECTED and S_SUPERSEDED are PRE-terminal:
# they each have one lawful exit (→ S_TERMINAL); all other moves are
# REJECT_FORBIDDEN_TRANSITION, not REJECT_TERMINAL_FROZEN (§2.2 / T3b).
TERMINAL_STATES = frozenset({
    S_TERMINAL,
    TERMINAL_ADMITTED, TERMINAL_REJECTED, TERMINAL_REPLAYABLE, TERMINAL_SUPERSEDED,
})

# ── Closed reject enum (no free-form reasons inside the kernel) ──────────────
REJECT_BAD_STATE = "REJECT_BAD_STATE"
REJECT_FORBIDDEN_TRANSITION = "REJECT_FORBIDDEN_TRANSITION"
REJECT_NO_HASH = "REJECT_NO_HASH"
REJECT_NO_RECEIPT = "REJECT_NO_RECEIPT"
REJECT_GATE_RED = "REJECT_GATE_RED"
REJECT_TERMINAL_FROZEN = "REJECT_TERMINAL_FROZEN"
REJECT_TERMINAL_CONFLICT = "REJECT_TERMINAL_CONFLICT"
REJECT_SPEC_CEILING = "REJECT_SPEC_CEILING"
REJECT_CEILING_EXCEEDED = "REJECT_CEILING_EXCEEDED"   # DEPRECATED — not in closed 11-code spec enum; use REJECT_SPEC_CEILING (L2) or REJECT_BAD_STATE (L6)
REJECT_REASON_MISSING = "REJECT_REASON_MISSING"
REJECT_REPLAY_MISMATCH = "REJECT_REPLAY_MISMATCH"
REJECT_HUMAN_SEAL_MISSING = "REJECT_HUMAN_SEAL_MISSING"

REJECT_CODES = frozenset({
    REJECT_BAD_STATE, REJECT_FORBIDDEN_TRANSITION, REJECT_NO_HASH,
    REJECT_NO_RECEIPT, REJECT_GATE_RED, REJECT_TERMINAL_FROZEN,
    REJECT_TERMINAL_CONFLICT, REJECT_SPEC_CEILING, REJECT_CEILING_EXCEEDED,
    REJECT_REASON_MISSING, REJECT_REPLAY_MISMATCH, REJECT_HUMAN_SEAL_MISSING,
})

# ── Explicit forbidden-transition matrix (the executable constitution) ───────
# Skip-edges that must never be legal, with the specific reject code each raises.
# The ladder also fails closed on any unlisted edge; this matrix pins the headline
# illegal promotions so spec and tests agree on a single object.
FORBIDDEN_TRANSITIONS = {
    (S0_SYMBOL, S2_TYPED): REJECT_FORBIDDEN_TRANSITION,
    (S0_SYMBOL, S3_RECEIPTED): REJECT_FORBIDDEN_TRANSITION,
    (S0_SYMBOL, S5_ADMITTED): REJECT_FORBIDDEN_TRANSITION,
    (S1_CLAIM, S3_RECEIPTED): REJECT_FORBIDDEN_TRANSITION,
    (S1_CLAIM, S5_ADMITTED): REJECT_FORBIDDEN_TRANSITION,
    (S2_TYPED, S5_ADMITTED): REJECT_FORBIDDEN_TRANSITION,
    (S3_RECEIPTED, S6_REPLAYABLE): REJECT_FORBIDDEN_TRANSITION,
    (S4_JUDGED, S6_REPLAYABLE): REJECT_FORBIDDEN_TRANSITION,
}

# Authority-level ranking for the SPEC ceiling (L2): a lower-level artifact may
# not claim higher-level authority.
_LEVEL_RANK = {"DOCS": 0, "SANDBOX": 0, "SPEC": 1, "PROPOSAL": 1, "KERNEL": 3}

# Closed taxonomies for the DERIVED typecheck (③).
_CLAIM_CLASSES = frozenset({"OBSERVED", "INFERRED", "STRUCTURAL", "FORMAL", "SPECULATIVE"})
_TRUTH_STATUS = frozenset({"UNVERIFIED", "SUPPORTED", "REVIEWED", "ADMITTED",
                           "SEALED", "REPLAYABLE", "REJECTED", "SUPERSEDED"})


def _rank_level(level: Optional[str]) -> int:
    return _LEVEL_RANK.get(level or "DOCS", 0)


def _ladder_rank(state: Optional[str]) -> int:
    return LADDER.index(state) if state in LADDER else -1


def _legal_target(current: str) -> Optional[str]:
    """The single legal forward rung from `current` (None if none)."""
    if current in LADDER:
        i = LADDER.index(current)
        return LADDER[i + 1] if i + 1 < len(LADDER) else S_TERMINAL
    return None


# ── DERIVED facts (③) — the heart of the BED 03 hardening ────────────────────

def compute_candidate_hash(candidate: dict) -> str:
    """Canonical content hash. Excludes evidence_hash / external_seal (no circularity).
    This is what `evidence_hash` must equal to count as a real receipt."""
    core = {
        "content": candidate.get("content"),
        "claim_class": candidate.get("claim_class"),
        "truth_status": candidate.get("truth_status"),
        "evidence": candidate.get("evidence"),
    }
    blob = json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(blob).hexdigest()


@dataclass(frozen=True)
class ReplayContext:
    """Attestations DERIVED from the replay trace — the only source for predicates
    the reducer cannot recompute locally. NOT supplied by the claim. Absent context
    ⇒ everything fails closed."""
    gate_attested: bool = False          # K8∧Kτ∧Kρ∧K-wul∧LEGORACLE replayed green
    replay_deterministic: bool = False   # re-derivation reproduced the trace
    known_receipts: frozenset = field(default_factory=frozenset)


@dataclass(frozen=True)
class DerivedFacts:
    typed: bool
    has_hash: bool
    has_receipt: bool
    gate_green: bool
    seal_valid: bool
    det_replay: bool


def verify_external_seal(candidate: dict, seal: Optional[dict],
                         rc: ReplayContext) -> bool:
    """② Un-self-conferrable: a seal is valid only if it is an OBJECT bound to the
    candidate hash, issued by an external OPERATOR role distinct from the proposer,
    whose receipt is known to the replay context (not to the candidate)."""
    if not isinstance(seal, dict):
        return False
    return (
        seal.get("candidate_hash") == compute_candidate_hash(candidate)
        and seal.get("issuer_role") == "OPERATOR"
        and seal.get("issuer") not in (None, candidate.get("proposer"))
        and seal.get("receipt_hash") in rc.known_receipts
    )


def derive_facts(candidate: dict, replay_context: Optional[ReplayContext] = None) -> DerivedFacts:
    """Compute predicates — do NOT read them off the claim. asserted ⊬ derived."""
    rc = replay_context or ReplayContext()
    typed = (candidate.get("claim_class") in _CLAIM_CLASSES
             and candidate.get("truth_status", "UNVERIFIED") in _TRUTH_STATUS)
    has_hash = (candidate.get("evidence_hash") is not None
                and candidate.get("evidence_hash") == compute_candidate_hash(candidate))
    has_receipt = bool(candidate.get("evidence"))
    gate_green = bool(rc.gate_attested)                       # from replay, not claim
    seal_valid = verify_external_seal(candidate, candidate.get("external_seal"), rc)
    det_replay = bool(rc.replay_deterministic)                # from replay, not claim
    return DerivedFacts(typed, has_hash, has_receipt, gate_green, seal_valid, det_replay)


@dataclass(frozen=True)
class Verdict:
    allow: bool
    next_state: Optional[str] = None
    reject_code: Optional[str] = None

    def __post_init__(self):
        # L5 — reason required: a rejection must carry a typed reason code.
        if not self.allow and self.reject_code not in REJECT_CODES:
            object.__setattr__(self, "reject_code", REJECT_REASON_MISSING)


def reduce_step(current: str, target: str, claim: dict,
                replay_context: Optional[ReplayContext] = None) -> Verdict:
    """Deterministic single transition. Fail-closed: anything unlisted → REJECT."""
    g = claim.get
    facts = derive_facts(claim, replay_context)

    # S_REJECTED and S_SUPERSEDED are PRE-terminal: each has exactly one lawful exit
    # (→ S_TERMINAL). All other moves are REJECT_FORBIDDEN_TRANSITION — NOT
    # REJECT_TERMINAL_FROZEN. L3 applies to S_TERMINAL only (§2.2 / T3b).
    if current == S_REJECTED:
        if target == S_TERMINAL:
            return Verdict(True, S_TERMINAL)
        return Verdict(False, reject_code=REJECT_FORBIDDEN_TRANSITION)
    if current == S_SUPERSEDED:
        if target == S_TERMINAL:
            return Verdict(True, S_TERMINAL)
        return Verdict(False, reject_code=REJECT_FORBIDDEN_TRANSITION)

    # L3 — terminal frozen: no exit from S_TERMINAL (the absorbing sink).
    if current in TERMINAL_STATES:
        return Verdict(False, reject_code=REJECT_TERMINAL_FROZEN)

    # L7 — terminal boolean consistency: claim.terminal must equal (current ∈ pre-terminal).
    declared_terminal = g("terminal")
    if declared_terminal is not None:
        if bool(declared_terminal) != (current in (S_REJECTED, S_SUPERSEDED)):
            return Verdict(False, reject_code=REJECT_BAD_STATE)

    # L4 — terminal conflict: same canonical id cannot have conflicting terminal verdicts.
    pt, nt = g("prior_terminal_state"), g("new_terminal_state")
    if pt and nt and pt != nt and g("same_canonical_id"):
        return Verdict(False, reject_code=REJECT_TERMINAL_CONFLICT)

    # L2 — SPEC ceiling: (a) authority-level ceiling; (b) SPECULATIVE hard cap (Ⓢ ↛ ✅).
    if _rank_level(g("level")) > _rank_level(g("spec_allowed_level", "KERNEL")):
        return Verdict(False, reject_code=REJECT_SPEC_CEILING)
    if (g("claim_class") == "SPECULATIVE"
            and target in LADDER and _ladder_rank(target) > _ladder_rank(S4_JUDGED)):
        return Verdict(False, reject_code=REJECT_SPEC_CEILING)

    # Rejection edge (any non-terminal → S_REJECTED) — reason required (L5).
    if target == S_REJECTED:
        if not g("reason_code"):
            return Verdict(False, reject_code=REJECT_REASON_MISSING)
        return Verdict(True, next_state=S_REJECTED)

    # Supersession edge (ADMITTED|REPLAYABLE → S_SUPERSEDED) — successor recorded.
    if target == S_SUPERSEDED:
        if current in (S5_ADMITTED, S6_REPLAYABLE) and g("successor_id"):
            return Verdict(True, next_state=S_SUPERSEDED)
        return Verdict(False, reject_code=REJECT_FORBIDDEN_TRANSITION)

    # L6 — max-state ceiling: target must not exceed claim's declared max_admission_state.
    max_st = g("max_state")
    if max_st and max_st in LADDER and target in LADDER:
        if _ladder_rank(target) > _ladder_rank(max_st):
            return Verdict(False, reject_code=REJECT_BAD_STATE)

    # Forbidden transition: only the immediate next rung is legal; the explicit
    # matrix pins specific skip-edges, the ladder fails closed on the rest.
    legal = _legal_target(current)
    if target != legal:
        return Verdict(False,
                       reject_code=FORBIDDEN_TRANSITIONS.get((current, target),
                                                             REJECT_FORBIDDEN_TRANSITION))

    # Per-edge guards — every predicate below is a DERIVED fact, never a claim flag.
    if current == S0_SYMBOL:                       # → S1: claim form
        return (Verdict(True, S1_CLAIM) if g("claim_form")
                else Verdict(False, reject_code=REJECT_BAD_STATE))
    if current == S1_CLAIM:                         # → S2: typed (derived typecheck)
        return (Verdict(True, S2_TYPED) if facts.typed
                else Verdict(False, reject_code=REJECT_BAD_STATE))
    if current == S2_TYPED:                         # → S3: receipt + hash (L1)
        if not facts.has_hash:
            return Verdict(False, reject_code=REJECT_NO_HASH)
        if not facts.has_receipt:
            return Verdict(False, reject_code=REJECT_NO_RECEIPT)
        return Verdict(True, S3_RECEIPTED)
    if current == S3_RECEIPTED:                     # → S4: gates green (replay-attested)
        return (Verdict(True, S4_JUDGED) if facts.gate_green
                else Verdict(False, reject_code=REJECT_GATE_RED))
    if current == S4_JUDGED:                        # → S5: Admit(c) (NOT canon)
        ok, code = admit(facts)
        return Verdict(True, S5_ADMITTED) if ok else Verdict(False, reject_code=code)
    if current == S5_ADMITTED:                      # → S6: external seal + det replay
        if not facts.seal_valid:                    # ② CanonAdmit needs an external seal
            return Verdict(False, reject_code=REJECT_HUMAN_SEAL_MISSING)
        if not facts.det_replay:
            return Verdict(False, reject_code=REJECT_REPLAY_MISMATCH)
        return Verdict(True, S6_REPLAYABLE)
    if current == S6_REPLAYABLE:                    # → terminal
        return Verdict(True, S_TERMINAL)
    return Verdict(False, reject_code=REJECT_BAD_STATE)


def admit(facts: DerivedFacts) -> tuple[bool, Optional[str]]:
    """Admit(c) = Typed ∧ HasReceipt ∧ HasHash ∧ GateGreen.  (Admit ≠ Canon — the
    external seal is checked only at the S5→S6 boundary, not here.) Operates on
    DERIVED facts. Returns (ok, failing_reject_code)."""
    if not facts.typed:
        return False, REJECT_BAD_STATE
    if not facts.has_hash:
        return False, REJECT_NO_HASH
    if not facts.has_receipt:
        return False, REJECT_NO_RECEIPT
    if not facts.gate_green:
        return False, REJECT_GATE_RED
    return True, None


def can_admit(claim: dict, replay_context: Optional[ReplayContext] = None) -> bool:
    """Admit(c) boolean — kernel-admissibility (NOT canon)."""
    return admit(derive_facts(claim, replay_context))[0]


def canon_admit(claim: dict, replay_context: Optional[ReplayContext] = None) -> bool:
    """CanonAdmit(c) = Admit(c) ∧ verified-external-seal. The reducer may COMPUTE this
    but cannot CONFER the seal — the seal must be an external object (② un-self-
    conferrable). A claim that merely sets human_seal=true does not pass."""
    facts = derive_facts(claim, replay_context)
    return admit(facts)[0] and facts.seal_valid


def run_ladder(claim: dict,
               replay_context: Optional[ReplayContext] = None) -> tuple[str, Optional[str]]:
    """Walk S0→S6 applying every guard. Returns (final_state_or_S_REJECTED, terminal).
    The only happy path ends (S6_REPLAYABLE, TERMINAL_REPLAYABLE)."""
    state = S0_SYMBOL
    for nxt in LADDER[1:]:
        v = reduce_step(state, nxt, claim, replay_context)
        if not v.allow:
            return S_REJECTED, TERMINAL_REJECTED
        state = v.next_state
    return S6_REPLAYABLE, TERMINAL_REPLAYABLE
