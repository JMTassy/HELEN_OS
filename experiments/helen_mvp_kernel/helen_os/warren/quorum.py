"""Warren quorum gate — Γ recomputes consensus from identity-bound ballots.
🔵 OBSERVED · NON_SOVEREIGN · authority=0.

E011. The Warren interior (personas, rhetoric, hidden deliberation, agent count) is untrusted
and A=0. Governance must NOT read narrative; it reads only a typed, provenance-derived quotient
and RECOMPUTES quorum. The anti-vacuity theorem on the MULTI-PARTY axis:

    E_agg ≠ "swarm said so"     E_agg = witnesses; Γ = verifier
    Sig_agg(H(M)) ⊬ quorum       one signature ⊬ consensus
    quorum ⊬ ADMIT ⊬ commit      chain: QUORUM → ADMIT → κ → EXECUTE/PENDING → COMMIT (respects E010)

Four gaps the critique flagged, all closed here (not spec-only):
  1. DERIVED lineage — declared source_lineage_id is IGNORED; lineage resolved from a trusted
     provenance graph over input roots. "declared lineage ≠ derived lineage" (cf. E006 caller-assert).
  2. claim↔evidence BINDING — every claim needs matching evidence; defeats evidence displacement
     (the Warren analogue of E001 identity displacement).
  3. W(p) is a REAL predicate (typed ∧ provenanced ∧ bound), not an enum label.
  4. Γ RECOMPUTES quorum — no trusted consensus=true field; distinct-voter set-cardinality + threshold,
     each ballot bound to H(M) ∥ surface ∥ policy ∥ epoch ∥ domain (defeats replay/substitution/dup-id).

RESIDUAL: HMAC roster-key signatures (deterministic MVP) prove multi-identity approval under a
declared roster; they are weaker than public-key sigs (a compromised roster/gate could forge) —
handoff-prevention grade, not cryptographic possession. Epoch is an injected integer (no wall clock).
"""
from __future__ import annotations

import hmac
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from helen_os.ledger.hash_chain import canonical_json, sha256_hex

DOMAIN = "HELEN/WARREN/BALLOT/V1"       # domain separation — no cross-protocol replay
APPROVE, REJECT, ABSTAIN = "APPROVE", "REJECT", "ABSTAIN"


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


# ---------------------------------------------------------------- evidence & lineage

@dataclass(frozen=True)
class EvidenceAtom:
    claim: str
    declared_lineage: str      # SELF-ASSERTED — the gate ignores this for counting
    input_root: str            # the actual provenance root the resolver keys on
    test_id: str
    observed_result: str


def derive_lineages(atoms: tuple, provenance_graph: dict) -> set:
    """DERIVED independent lineage count (gap 1). Declared lineage is ignored; each atom's
    input_root is resolved to a canonical provenance root via a TRUSTED graph. Forging N
    distinct declared_lineage strings for one true source collapses to that source's one root."""
    return {provenance_graph.get(a.input_root, a.input_root) for a in atoms}


# ---------------------------------------------------------------- policy & ballots

@dataclass(frozen=True)
class QuorumPolicy:
    roster: tuple              # tuple of (voter_id, secret_key) — precommitted before the run
    threshold: int
    version: str = "v1"

    def roster_ids(self) -> frozenset:
        return frozenset(v for v, _ in self.roster)

    def key_of(self, voter_id: str) -> Optional[bytes]:
        for v, k in self.roster:
            if v == voter_id:
                return k if isinstance(k, bytes) else k.encode()
        return None

    def policy_hash(self) -> str:
        # binds roster membership + threshold + version — defeats policy substitution (gap 4/WQ-07)
        return h_v({"roster": sorted(self.roster_ids()), "t": self.threshold, "v": self.version})


@dataclass(frozen=True)
class Ballot:
    voter_id: str
    mutation_hash: str         # H(M) — must equal the exact proposed mutation
    surface_hash: str
    policy_hash: str
    epoch: int
    vote: str
    nonce: str
    sig: str


def ballot_message(b: Ballot) -> str:
    # domain-separated canonical message a voter signs — cross-domain replay fails (WQ-08)
    return h_v([DOMAIN, b.voter_id, b.mutation_hash, b.surface_hash,
                b.policy_hash, b.epoch, b.vote, b.nonce])


def sign_ballot(b: Ballot, key: bytes) -> str:
    return hmac.new(key, ballot_message(b).encode(), "sha256").hexdigest()


def valid_ballot(b: Ballot, policy: QuorumPolicy, m_hash: str, surface_hash: str,
                 epoch: int) -> bool:
    """Per-ballot verification — recomputed, never trusted. Each conjunct is a binding."""
    key = policy.key_of(b.voter_id)
    if key is None:                                   # roster membership
        return False
    if b.mutation_hash != m_hash:                     # bound to the EXACT mutation (WQ-03)
        return False
    if b.surface_hash != surface_hash:
        return False
    if b.policy_hash != policy.policy_hash():         # policy binding (WQ-07)
        return False
    if b.epoch != epoch:                              # freshness / anti-replay (WQ-04)
        return False
    return hmac.compare_digest(b.sig, sign_ballot(b, key))  # signature over domain-sep message


# ---------------------------------------------------------------- structural check W(p)

@dataclass(frozen=True)
class CandidatePacket:
    claims: tuple              # tuple[str]
    evidence: tuple            # tuple[EvidenceAtom]
    ballots: tuple             # tuple[Ballot]


def dirty(p: CandidatePacket) -> Optional[str]:
    """W(p) as a REAL predicate (gap 3): typed ∧ provenanced ∧ bound. Returns a reason or None."""
    if not isinstance(p, CandidatePacket):
        return "NOT_TYPED"
    for a in p.evidence:
        if not isinstance(a, EvidenceAtom) or not a.input_root:
            return "NOT_PROVENANCED"
    # claim↔evidence binding (gap 2): every claim must have ≥1 matching evidence atom
    claimed = set(p.claims)
    evidenced = {a.claim for a in p.evidence}
    if not claimed <= evidenced:
        return "CLAIM_EVIDENCE_UNBOUND"               # evidence displacement blocked
    # and no foreign evidence attached to a claim not in the packet
    if not evidenced <= claimed:
        return "FOREIGN_EVIDENCE"
    return None


# ---------------------------------------------------------------- the gate

class Outcome(Enum):
    REJECT = "REJECT"
    NO_RECEIPT = "NO_RECEIPT"
    HOLD = "HOLD"
    PROPOSAL = "PROPOSAL"


@dataclass(frozen=True)
class Proposal:
    """Authority-ZERO output type (gap 6): distinct from Capability/Effect/Receipt by construction.
    Carries only witnesses; it cannot mint or execute anything."""
    mutation_hash: str
    approvals: int
    independent_lineages: int
    quorum_met: bool
    # deliberately absent: capability, effect, ledger_receipt, admitted, authority.
    @property
    def authority(self) -> int:
        return 0


@dataclass(frozen=True)
class QuorumResult:
    quorum_met: bool
    approvals: int             # DISTINCT approving voters (set-cardinality, no dup inflation)
    independent_lineages: int
    reason: Optional[str] = None


def recompute_quorum(p: CandidatePacket, policy: QuorumPolicy, m_hash: str,
                     surface_hash: str, epoch: int, provenance_graph: dict) -> QuorumResult:
    """Γ RECOMPUTES quorum from ballots (gap 4). No consensus=true is ever trusted.
    An empty ballot set with only an aggregate blob cannot pass (WQ-05: per-ballot required)."""
    approvers = {
        b.voter_id for b in p.ballots
        if b.vote == APPROVE and valid_ballot(b, policy, m_hash, surface_hash, epoch)
    }                                                 # SET → duplicate voter_id cannot inflate (WQ-02)
    lineages = derive_lineages(p.evidence, provenance_graph)
    met = len(approvers) >= policy.threshold          # threshold recompute (WQ-01/WQ-06)
    return QuorumResult(met, len(approvers), len(lineages))


def gate(p: CandidatePacket, policy: QuorumPolicy, m_hash: str, surface_hash: str, epoch: int,
         provenance_graph: dict, verification: str = "PASS", jurisdiction: str = "MACHINE"):
    """Full Warren trellis → {REJECT, NO_RECEIPT, HOLD, PROPOSAL}. NEVER ADMIT/κ/Effect.
    verification ∈ {PASS, FAIL, ABSENT}; jurisdiction ∈ {MACHINE, HUMAN}."""
    d = dirty(p)                                      # W(p) first — structural integrity
    if d is not None:
        return Outcome.REJECT, d
    q = recompute_quorum(p, policy, m_hash, surface_hash, epoch, provenance_graph)
    if not q.quorum_met:
        return Outcome.REJECT, "NO_QUORUM"
    if verification == "FAIL":
        return Outcome.REJECT, "EVIDENCE_FAILED"
    if verification == "ABSENT":
        return Outcome.NO_RECEIPT, "EMPIRICAL_EVIDENCE_ABSENT"  # distinct from HOLD
    if jurisdiction == "HUMAN":
        return Outcome.HOLD, "HOLD_FOR_OPERATOR"
    # quorum + evidence + machine jurisdiction → a PROPOSAL, which is authority-0.
    # quorum ⊬ ADMIT: the reducer/Γ, not this gate, decides admission downstream.
    return Outcome.PROPOSAL, Proposal(m_hash, q.approvals, q.independent_lineages, True)
