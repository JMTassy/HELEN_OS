"""Goblin output grammar — the Constraint Dividend, executable.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Needle-2 relay chiddush (product claims unverified from this frame;
the laws below stand independently of any benchmark):

    freedom of thought != freedom of expression type != freedom of effect

Inside the model: free latent search. Outside: a CLOSED grammar. A
Goblin may only emit five utterance kinds — and the constraint is
enforced at CONSTRUCTION (the analogue of grammar-constrained decoding:
illegal vocabulary is never scored), not by post-hoc parsing.

Three laws encoded:

  CONSTRAINT DIVIDEND   Emissions outside the grammar are unconstructible
                        (E_OUTSIDE_GRAMMAR). Narrower output language =>
                        no malformed escape, no parse ambiguity, no
                        authority ambiguity — reliability as a byproduct
                        of the type, not an overhead on it.

  CONFIDENCE != AUTHORITY   confidence is ROUTING metadata. route() has
                        codomain {local_handler_eligible, escalate} and
                        nothing else: confidence > tau does not imply
                        ADMIT at any tau, including 1.0.

  GROUNDING LAW         An OBSERVATION must cite evidence (context-
                        grounded). An unreferenced claim can only be a
                        HYPOTHESIS — hidden weight-memory cannot
                        masquerade as observation. Low parametric
                        recall + high context grounding, as a type.

Plus the pinned-context principle: constitutional context is
STRUCTURALLY persistent — pinned material lives outside the evictable
window, so no eviction sequence can remove it. Not "likely to remain";
unable to leave.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

# ── the closed grammar: exactly five utterance kinds ────────────────────
# Extension requires a contract version bump (GRAMMAR_VERSION), mirroring
# the status-ladder discipline: the closure IS the constitutional object.
GRAMMAR_VERSION = "GOBLIN_GRAMMAR_V1"
EMISSION_KINDS = frozenset({
    "OBSERVATION",       # context-grounded report — requires evidence refs
    "HYPOTHESIS",        # speculative content, A=0 by construction
    "COUNTEREXAMPLE",    # an attack on a standing candidate
    "REQUEST_WITNESS",   # asks for observation it cannot perform itself
    "PROPOSAL",          # a typed candidate for the trellis — never an act
})

# Never representable in an emission, on the wire or in the type.
_FORBIDDEN_FIELDS = frozenset({
    "authority", "admit", "execute", "mint_capability", "ledger_append",
    "commit", "act", "device_action",
})

ROUTE_CODOMAIN = frozenset({"local_handler_eligible", "escalate"})


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class GoblinEmission:
    """The only shape a Goblin utterance can take. Note what is absent:
    no authority, no act, no admit — a Goblin translates messy reality
    into typed candidates, and stops."""
    emission_id: str
    kind: str
    payload: str
    evidence_refs: tuple = ()        # pointers into the addressed EXHIBIT
    confidence: float = 0.0          # ROUTING metadata, never authority
    goblin_id: str = ""
    frame_ref: str = ""

    def __post_init__(self):
        if self.kind not in EMISSION_KINDS:
            # constrained decoding: the illegal row is never scored
            raise ValueError(f"E_OUTSIDE_GRAMMAR:{self.kind}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("E_CONFIDENCE_RANGE")
        # GROUNDING LAW: observation without evidence is unconstructible.
        if self.kind == "OBSERVATION" and not self.evidence_refs:
            raise ValueError("E_UNGROUNDED_OBSERVATION")

    def as_hypothesis(self) -> "GoblinEmission":
        """The honest downgrade: content that cannot cite evidence may
        still enter the Garden — typed as what it actually is."""
        from dataclasses import replace
        return replace(self, kind="HYPOTHESIS")


def validate_emission_dict(d: dict) -> None:
    """Wire-level closed schema. Unknown fields REJECT; forbidden fields
    reject BY NAME so a smuggling producer is reported, not ignored."""
    if not isinstance(d, dict):
        raise TypeError("E_ILL_TYPED_EMISSION")
    banned = set(k.lower() for k in d) & _FORBIDDEN_FIELDS
    if banned:
        raise ValueError(f"E_AUTHORITY_INJECTION:{','.join(sorted(banned))}")
    allowed = {"emission_id", "kind", "payload", "evidence_refs",
               "confidence", "goblin_id", "frame_ref"}
    extra = set(d) - allowed
    if extra:
        raise ValueError(f"E_UNKNOWN_FIELDS:{','.join(sorted(extra))}")


# ── confidence is routing, never authority ──────────────────────────────

def route(emission: GoblinEmission, tau: float) -> dict:
    """The ONLY thing confidence buys: which handler sees the emission
    next. The codomain contains no ADMIT, no execute, no act — at any
    threshold, including confidence == 1.0."""
    decision = ("local_handler_eligible" if emission.confidence > tau
                else "escalate")
    assert decision in ROUTE_CODOMAIN
    return {"route": decision, "tau": tau,
            "note": "eligibility is not admission; the membrane still applies"}


# ── PROPOSAL -> candidate packet for the trellis (proposal only) ────────

def to_candidate_packet(emission: GoblinEmission) -> dict:
    """A PROPOSAL becomes a CandidateDecisionPacket bound for HAL/the
    Warren trellis. It carries provenance and typed content — and admits
    nothing. Every other kind is refused: observations are evidence,
    not candidates; hypotheses must survive falsification first."""
    if emission.kind != "PROPOSAL":
        raise ValueError(f"E_NOT_A_PROPOSAL:{emission.kind}")
    return {
        "packet": "CANDIDATE_DECISION_PACKET_V1",
        "source_emission": emission.emission_id,
        "goblin": emission.goblin_id,
        "payload": emission.payload,
        "evidence_refs": list(emission.evidence_refs),
        "routing_confidence": emission.confidence,   # metadata, travels as label
        "status": "PROPOSED",                        # the only status it can have
    }


# ── pinned context: structurally persistent, not probabilistically so ───

class GoblinContext:
    """Two segments on physically distinct storage:

        PINNED  — schema, tool vocabulary, A=0, output contract,
                  prohibited crossings. There is NO eviction path over
                  this segment; it cannot leave the window.
        SLIDING — task, local evidence, recent observations. FIFO-evicted
                  under capacity pressure.

    The Needle translation: 'the system prompt is pinned so it cannot be
    evicted' generalized to: constitutional context is structurally
    persistent, not merely likely to remain."""

    def __init__(self, pinned: dict, capacity: int):
        if capacity < 1:
            raise ValueError("E_NO_WINDOW")
        required = {"schema", "tool_vocabulary", "a", "output_contract",
                    "prohibited_crossings"}
        missing = required - set(pinned)
        if missing:
            raise ValueError(f"E_PIN_INCOMPLETE:{','.join(sorted(missing))}")
        if pinned["a"] != 0:
            raise ValueError("E_PINNED_AUTHORITY_NONZERO")   # A=0 is pinned law
        self._pinned = dict(pinned)   # private; no public mutation surface
        self._sliding: list = []
        self._capacity = capacity

    @property
    def pinned(self) -> dict:
        return dict(self._pinned)     # copy out; the original is unreachable

    @property
    def sliding(self) -> tuple:
        return tuple(self._sliding)

    def push(self, item: str) -> None:
        """Only the sliding segment feels capacity pressure. Eviction is
        FIFO over sliding items exclusively — pinned is not addressable
        by this (or any) eviction path."""
        self._sliding.append(item)
        while len(self._sliding) > self._capacity:
            self._sliding.pop(0)
