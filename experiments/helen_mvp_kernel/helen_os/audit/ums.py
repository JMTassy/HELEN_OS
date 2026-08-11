"""UNKNOWN MONOTONIC SAFETY — capability may grow while authority does not. 🔵 OBSERVED · authority=0.

The higher-order invariant the Crystal Palace run witnessed empirically (20/20 epochs · zero launder ·
10 honest-UNKNOWN). Two forms:

  STATIC   ¬V(e) ⇒ R(e) = ⊥_E (UNKNOWN) ∧ ¬Admit(e)          no evidence → explicit UNKNOWN, never a completion
  DYNAMIC  S_{t+1} ⊃ S_t with a contradiction ⇒ R may FALL   ΔEvidence>0 ∧ ΔAuthority≤0 is allowed, sometimes optimal

    Coverage↑ ⊬ Commitment↑ · Capability↑ ⊬ Authority↑ · MORE-SEEN ⊬ MORE-CLAIMED.
    UNKNOWN / HOLD is a valid TERMINAL state, not a failure.

This is a self-contained REFERENCE model of the property. The shipped seams are its live instances:
  synthesis boundary  → fable gate (C_valid=0 ⇒ n_eff_H=UNKNOWN)
  coverage boundary   → ν verify_coverage (𝒰≠∅ ⇒ UNKNOWN, EXHIBIT-00)
  admission boundary  → core_v1 promotion (REPORTED ⊬ ADMITTED)
Determinism: pure functions; no wall clock.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Rec(IntEnum):
    """Recommendation, ordered by AUTHORITY (rank). Higher = more committed."""
    UNKNOWN = 0      # ⊥_E — nothing sufficient observed; the valid bottom state
    HOLD = 1         # something observed, but not enough / contradicted → do not act
    ACT = 2          # every required surface validly supported, none contradicted


class Ev(IntEnum):
    UNKNOWN = 0          # required surface has no valid support yet
    SUPPORTED = 1        # validly sourced, no active contradiction
    CONTRADICTED = 2     # active counter-evidence exists (dominates support)


@dataclass(frozen=True)
class Observation:
    key: str                    # which required evidence surface it speaks to
    supported: bool             # V(e): validly SOURCED. Confident prose with supported=False is NOT evidence.
    contradicts: bool = False   # this observation is counter-evidence to `key`


@dataclass(frozen=True)
class DecisionSpec:
    question: str
    required: tuple             # tuple[str] — surfaces that must ALL be supported for ACT


def evidence_state(spec: DecisionSpec, observations) -> dict:
    """Fold observations into a per-required-surface status. Unsupported, non-contradicting observations
    (pressure / confident prose) change NOTHING — they are not evidence. Contradiction DOMINATES support."""
    st = {k: Ev.UNKNOWN for k in spec.required}
    for o in observations:
        if o.key not in st:
            continue                                   # irrelevant / malformed surface → ignored, no effect
        if o.contradicts:
            st[o.key] = Ev.CONTRADICTED                # counter-evidence dominates and is not overwritten below
        elif o.supported and st[o.key] == Ev.UNKNOWN:
            st[o.key] = Ev.SUPPORTED                   # a SUPPORTED obs promotes UNKNOWN→SUPPORTED (never over CONTRADICTED)
        # unsupported & non-contradicting: no state change (Goodhart guard: looks-done ≠ supported)
    return st


def recommend(spec: DecisionSpec, observations) -> Rec:
    """Pure verdict. UNKNOWN is a legitimate terminal state; a required contradiction can only hold, never act."""
    st = evidence_state(spec, observations)
    vals = list(st.values())
    if Ev.CONTRADICTED in vals:
        return Rec.HOLD                                # active counter-evidence → never ACT
    if Ev.UNKNOWN in vals:
        return Rec.UNKNOWN if all(v == Ev.UNKNOWN for v in vals) else Rec.HOLD
    return Rec.ACT                                      # all required SUPPORTED, none contradicted


def admit(spec: DecisionSpec, observations) -> bool:
    """A recommendation is ADMITTED (committed as a governed claim) only when fully, validly supported.
    ¬V ⇒ ¬Admit. Admission is evidence-gated, not coverage-gated."""
    st = evidence_state(spec, observations)
    return recommend(spec, observations) == Rec.ACT and all(v == Ev.SUPPORTED for v in st.values())


def authority_rank(spec: DecisionSpec, observations) -> int:
    """AUTHORITY = commitment to ACT — the quantity that must never inflate under added evidence.
    UNKNOWN and HOLD are BOTH uncommitted (rank 0); only ACT commits (rank 1). This is deliberately NOT
    the Rec ordering: from the bottom, a contradiction moves the VERDICT UNKNOWN→HOLD (a semantic change),
    but it must not RAISE authority — both are 'do not act'. So a contradiction can only hold authority
    (0→0) or lower it (ACT→HOLD, 1→0); it can never inflate it. (Peer-review fix: the earlier int(Rec)
    ranking let a contradiction raise 0→1 from the null state — corrected here.)"""
    return 1 if recommend(spec, observations) == Rec.ACT else 0
