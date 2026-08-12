"""Witnessed Obligation Liveness — the dual theorem.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The safety spine already holds: Garden ⊬ Authority, HAL PASS ⊬ ADMIT,
ADMIT ⊬ EXECUTE. What was missing is the dual:

    Can HELEN remain fail-closed without becoming fail-frozen?

    Safety   : []¬IllegalMutation
    Liveness : [](Critical ∧ Reachable(ω) => <>Resolution(ω))
    Resolution = WitnessedDischarge ∨ ExplicitEscalation
               ∨ WitnessedImpossibility

The one line: nothing illegal may happen, and nothing critical may
disappear merely because nothing happened.

The chiddush this module makes executable — and applies to its own
author first: a HOLD is not a resolution. An obligation that has been
HELD across ticks without generating a next evidentiary obligation is
an ETERNAL HOLD, which is a liveness violation, not caution. This
whole session accrued Ω — a security fix, deadlines — and let them
sit HELD. Under this theorem that is a governance defect, and the
scheduler below ranks a domain deletion tomorrow above another
elegant theorem, by construction.

Deterministic: time is a passed-in integer tick, no wall-clock, no
randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

RESOLUTION_KINDS = ("WITNESSED_DISCHARGE", "EXPLICIT_ESCALATION",
                    "WITNESSED_IMPOSSIBILITY")

# a HOLD is progress ONLY if it emits one of these as its next step.
HOLD_PROGRESS_KINDS = ("NEXT_EVIDENTIARY_OBLIGATION", "ESCALATION",
                       "IMPOSSIBILITY_SEARCH")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the obligation, with liveness coordinates ───────────────────────────

@dataclass(frozen=True)
class LiveObligation:
    """An open obligation carrying what the scheduler and the liveness
    check need. reachable=False means no seat can act on it now — it
    can still be escalated, never silently dropped."""
    oblig_id: str
    critical: bool
    reachable: bool
    severity: float                    # S
    irreversibility: float             # I
    deadline_pressure: float           # D
    reachability: float                # R (0..1)
    discharge_cost: float              # C
    opened_at: int
    progress_ticks: tuple = ()         # ticks at which progress was made

    def utility(self, eps: float = 1e-6) -> float:
        """U = S·I·D·R / (C + eps). The scheduler maximizes this."""
        return (self.severity * self.irreversibility *
                self.deadline_pressure * self.reachability) / \
               (self.discharge_cost + eps)


def schedule(obligations: tuple) -> dict:
    """omega* = argmax U. Deterministic tie-break on oblig_id. This is
    the operational correction: rank by criticality·irreversibility·
    deadline·reachability, never by intellectual attractiveness."""
    if not obligations:
        return {"selected": None, "reason": "E_EMPTY_OBLIGATION_SET"}
    ranked = sorted(obligations,
                    key=lambda o: (-o.utility(), o.oblig_id))
    return {"selected": ranked[0].oblig_id,
            "utility": ranked[0].utility(),
            "order": [o.oblig_id for o in ranked],
            "law": "a critical irreversible deadline dominates another "
                   "elegant theorem, by construction"}


# ── resolution: the only three lawful exits from Omega ──────────────────

@dataclass(frozen=True)
class Resolution:
    oblig_id: str
    kind: str
    witness_ref: str

    def __post_init__(self):
        if self.kind not in RESOLUTION_KINDS:
            raise ValueError("E_UNKNOWN_RESOLUTION_KIND")
        if not self.witness_ref:
            raise ValueError("E_RESOLUTION_WITHOUT_WITNESS")


def resolve(obligation: LiveObligation, resolution: Resolution) -> dict:
    """An obligation leaves Omega ONLY through a witnessed resolution.
    'done' without a witness removes nothing (history_fiber's law);
    here we add that even impossibility must be WITNESSED — you may
    not drop an obligation by asserting it cannot be done, you must
    show it."""
    if resolution.oblig_id != obligation.oblig_id:
        return {"verdict": "REFUSED", "reason": "E_RESOLUTION_MISMATCH"}
    return {"verdict": "RESOLVED", "kind": resolution.kind,
            "witness": resolution.witness_ref,
            "leaves_omega": True}


# ── HOLD != DEADLOCK: the core theorem ──────────────────────────────────

@dataclass(frozen=True)
class Hold:
    """A HOLD verdict. To be lawful it must name the next evidentiary
    obligation it generates — a HOLD that generates nothing is a
    silent deadlock wearing caution's clothes."""
    oblig_id: str
    held_at: int
    generates: str = ""                # a HOLD_PROGRESS_KIND
    next_obligation: str = ""          # the id it spawns


def hold_is_lawful(hold: Hold) -> dict:
    """A HOLD must progress. No generated next step => E_ETERNAL_HOLD."""
    if hold.generates not in HOLD_PROGRESS_KINDS or not hold.next_obligation:
        return {"verdict": "E_ETERNAL_HOLD",
                "oblig_id": hold.oblig_id,
                "law": "a HOLD must generate a next evidentiary "
                       "obligation; a silent hold is a deadlock"}
    return {"verdict": "LAWFUL_HOLD", "generates": hold.generates,
            "next_obligation": hold.next_obligation}


def liveness_check(obligation: LiveObligation, now: int,
                   stale_after: int = 3) -> dict:
    """[](Critical ∧ Reachable => <>Resolution). A critical obligation
    that has gone stale_after ticks WITHOUT progress and without
    resolution has violated liveness — being fail-closed is not a
    licence to be fail-frozen. An unreachable critical obligation must
    still show ESCALATION progress; it may not be silently parked."""
    if not obligation.critical:
        return {"verdict": "NOT_CRITICAL", "monitored": False}
    last_progress = (max(obligation.progress_ticks)
                     if obligation.progress_ticks else obligation.opened_at)
    idle = now - last_progress
    if idle > stale_after:
        return {"verdict": "E_LIVENESS_VIOLATION",
                "oblig_id": obligation.oblig_id,
                "idle_ticks": idle,
                "reachable": obligation.reachable,
                "required": "WitnessedDischarge | ExplicitEscalation | "
                            "WitnessedImpossibility",
                "law": "nothing critical may disappear merely because "
                       "nothing happened"}
    return {"verdict": "LIVE", "idle_ticks": idle}


def frontier_predicate(safety_holds: bool, liveness_holds: bool) -> dict:
    """[]¬IllegalMutation ∧ [](CriticalReachable => <>Resolution).
    Both conjuncts, or the system is not the next paradigm."""
    return {"safety": safety_holds, "liveness": liveness_holds,
            "frontier_held": safety_holds and liveness_holds,
            "line": "nothing illegal may happen, and nothing critical "
                    "may disappear merely because nothing happened"}


# ── admissibility distance: guide research without self-approval ────────

def admissibility_distance(phi_results: dict, weights: dict,
                           critical: frozenset,
                           authority_of_candidate: float) -> dict:
    """d_Gamma(c) = sum alpha*[FAIL] + sum beta*[UNKNOWN], with a
    critical FAIL => +inf. Guides Goblin toward the gate WITHOUT
    teaching it to self-approve: the candidate must carry A(c)=0, and
    min d_Gamma never implies ADMIT."""
    if authority_of_candidate != 0:
        return {"distance": None, "reason": "E_CANDIDATE_CARRIES_AUTHORITY",
                "law": "research candidates must have A(c)=0; distance "
                       "is not defined for an authority-bearing object"}
    dist = 0.0
    for phi, verdict in phi_results.items():
        if verdict == "FAIL" and phi in critical:
            return {"distance": float("inf"), "critical_fail": phi,
                    "law": "min d_Gamma does not imply ADMIT; a critical "
                           "failure is an infinite barrier"}
        if verdict == "FAIL":
            dist += weights.get(phi, {}).get("alpha", 1.0)
        elif verdict == "UNKNOWN":
            dist += weights.get(phi, {}).get("beta", 0.5)
    return {"distance": dist, "admits": False,
            "law": "distance guides research; it never admits"}


def guided_step(candidates: dict) -> dict:
    """c_{t+1} = argmin d_Gamma(c) subject to A(c)=0. Returns the
    nearest-to-admissible candidate — which is still NOT admitted."""
    finite = {c: d for c, d in candidates.items()
              if d is not None and d != float("inf")}
    if not finite:
        return {"selected": None, "reason": "E_NO_FINITE_CANDIDATE"}
    best = min(finite.items(), key=lambda kv: (kv[1], kv[0]))
    return {"selected": best[0], "distance": best[1],
            "admitted": False,
            "note": "nearest to admissible is not admitted; A(c) stays 0"}


# ── one-shot transition capability: Authority Non-Bootstrap as math ─────

@dataclass(frozen=True)
class TransitionCapability:
    """kappa_c minted at ADMIT. Binds the hashes of candidate, witness
    bundle and pre-state, an op, an expiry tick and a one-shot nonce.
    Admission mints it; it does not execute."""
    h_candidate: str
    h_witness: str
    h_prestate: str
    op: str
    expires_at: int
    nonce: str


@dataclass
class NonceBook:
    """Tracks one-shot nonce consumption. Mutable: this is the single
    place a capability is spent, atomically."""
    _used: set = field(default_factory=set)

    def invoke(self, kappa: TransitionCapability, h_candidate: str,
               h_witness: str, h_prestate: str, now: int) -> dict:
        """Invoke(kappa) succeeds iff every bound hash matches, the
        capability has not expired, and the nonce is unused — then the
        nonce is consumed atomically. Replay, expiry and state-drift
        each refuse."""
        if h_candidate != kappa.h_candidate:
            return {"verdict": "REFUSED", "reason": "E_CANDIDATE_DRIFT"}
        if h_witness != kappa.h_witness:
            return {"verdict": "REFUSED", "reason": "E_WITNESS_DRIFT"}
        if h_prestate != kappa.h_prestate:
            return {"verdict": "REFUSED", "reason": "E_STATE_DRIFT"}
        if now >= kappa.expires_at:
            return {"verdict": "REFUSED", "reason": "E_CAPABILITY_EXPIRED"}
        if kappa.nonce in self._used:
            return {"verdict": "REFUSED", "reason": "E_NONCE_REPLAY"}
        self._used.add(kappa.nonce)                # atomic consume
        return {"verdict": "EXECUTED", "op": kappa.op, "nonce_consumed":
                kappa.nonce}


# ── replay wins over narrative ──────────────────────────────────────────

def replay_extensional_check(memory_state: str, replayed_state: str) -> dict:
    """G_t == Replay(G_0, L_t). If memory disagrees with replay, HOLD
    — replay wins over narrative, always."""
    if memory_state != replayed_state:
        return {"verdict": "HOLD", "reason": "E_REPLAY_DIVERGENCE",
                "law": "replay wins over narrative; a state that memory "
                       "asserts but replay denies is not the state"}
    return {"verdict": "CONSISTENT"}
