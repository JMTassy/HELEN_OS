"""The Admissible Causal Morphism — the constitutional atom beneath
the Causal Commit Cell.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    m : S_t ⇢ S_{t+1}          candidate (dashed): not yet a transition
    pi : Admit(S_t, m, S_{t+1}) proof object
    (S_t, m, pi) |-> S_{t+1}    reality, only with the proof

The one law under everything:

    COMPUTATION MAY TRANSFORM REPRESENTATION; ONLY WITNESSED ADMISSION
    MAY INCREASE INSTITUTIONAL REALITY OR AUTHORITY.

This subsumes CONVERGENCE != PROOF, PROJECTION != EVIDENCE,
CAPABILITY != AUTHORITY, CLAIM != DEMONSTRATION, GATE != INVARIANT,
STATE != LAWFUL HISTORY.

The Kernel is a proof calculus, not a policy engine. Admission is one
inference rule:

    I(S_t)  G(S_t,m)  Authorized(m)  Supported(m)  I(m(S_t))
    -------------------------------------------------------- Admit
                    S_t --m--> m(S_t)

Two graphs, never one: the WORLD graph W holds only admitted
transitions; the AUDIT graph A holds every attempt (candidate,
admitted, held, rejected). W ⊊ A — a negative receipt changes A and
never W.

Resource discipline:
- AUTHORITY is LINEAR: a lease is consumed on admission (L ⊸ m); a
  second draw on a spent lease is refused. Two locally valid receipts
  that both spent one single-use lease compose into an invalid
  history.
- EVIDENCE is reusable but PROVENANCE-CONSERVING: Roots(f(x)) ⊆
  Roots(x). Deterministic transformation cannot manufacture
  evidential rank. Ordinary cognition is authority-nonexpansive:
  A(f(x)) <= A(x) unless f is an authorized promotion gate admitting
  a NEW external witness.

Equivalence: constitutional ⊊ extensional. Two histories reaching the
same final state are NOT equal if their authority paths, evidence
roots, or lease consumption differ.

Deterministic: time passed in, no randomness, canonical JSON.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace

# an external witness class is what a promotion gate needs; ordinary
# cognition has none of these and therefore cannot expand authority.
EXTERNAL_WITNESS_KINDS = frozenset({
    "independent_observation", "authorization", "signature", "payment",
    "physical_witness", "test_result", "human_ratification",
    "new_source", "successful_replay"})


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ── the linear authority resource ───────────────────────────────────────

@dataclass
class LeaseBook:
    """Authority as a consumable. spend() is the ⊸: once a single-use
    lease is drawn it leaves the available set. Mutable by design —
    this is the one place state is spent, and spending must be
    observable across a composition."""
    _remaining: dict = field(default_factory=dict)   # lease_id -> uses left

    def grant(self, lease_id: str, uses: int = 1) -> None:
        self._remaining[lease_id] = uses

    def available(self, lease_id: str) -> bool:
        return self._remaining.get(lease_id, 0) > 0

    def spend(self, lease_id: str) -> dict:
        if self._remaining.get(lease_id, 0) <= 0:
            return {"ok": False, "reason": "E_LEASE_EXHAUSTED",
                    "lease_id": lease_id}
        self._remaining[lease_id] -= 1
        return {"ok": True, "remaining": self._remaining[lease_id]}


# ── evidence: reusable, provenance-conserving ───────────────────────────

def project_evidence(roots_in: frozenset, transform: str) -> dict:
    """A deterministic transformation. Roots(f(x)) ⊆ Roots(x), always
    — the output can never carry a root the input did not."""
    return {"transform": transform, "roots_out": frozenset(roots_in),
            "rank": len(roots_in),
            "law": "deterministic transformation cannot manufacture "
                   "evidential rank"}


def authority_nonexpansive(a_in: float, transform: str,
                           external_witness: dict | None = None) -> dict:
    """Ordinary cognition: A(f(x)) <= A(x). Only an authorized gate
    admitting a genuine external witness may raise it."""
    if external_witness and external_witness.get("kind") in \
            EXTERNAL_WITNESS_KINDS and external_witness.get("receipt"):
        return {"a_out": a_in + 1.0, "expanded": True,
                "by": external_witness["kind"]}
    return {"a_out": min(a_in, a_in), "expanded": False,
            "law": "no summarize/cluster/vote/embed/consensus/"
                   "self-critique raises authority by computation"}


# ── the atom ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CandidateMorphism:
    """m : S_t ⇢ S_{t+1}. Dashed. A proposal, nothing more."""
    m_id: str
    source_root: str                   # S_t, by state-root identity
    target: str                        # proposed S_{t+1}
    transformation: str
    evidence_roots: frozenset
    lease_id: str
    t_authorized: int
    t_effect: int
    quantity_delta: float = 0.0


@dataclass(frozen=True)
class Proof:
    """pi : Admit(S_t, m, S_{t+1}). Exists ONLY when the inference rule
    discharges every premise."""
    m_id: str
    premises: tuple                    # the discharged premise names
    receipt: str


def admit(m: CandidateMorphism, world_roots: frozenset,
          leases: LeaseBook, invariant, gate,
          t_now: int) -> dict:
    """The single inference rule. Returns either a Proof (world
    mutates) or a negative receipt (only the audit graph mutates).

    Premise order matters: orphan-source and retroactive-authority are
    checked before the lease is spent, so a doomed candidate never
    consumes authority."""
    audit = {"m_id": m.m_id, "candidate_target": m.target}

    # I(S_t): the source must be a lawful, reachable world root
    if m.source_root not in world_roots:
        return _reject(m, "E_ORPHAN_STATE", audit,
                       law="a state without a lawful path is an orphan; "
                           "it cannot anchor a transition")
    # arrow of time: authority may not postdate effect
    if m.t_authorized > m.t_effect:
        return _reject(m, "E_RETROACTIVE_AUTHORITY", audit,
                       law="later evidence cannot manufacture earlier "
                           "missing authority")
    # G(S_t, m): the gate rule about the morphism
    if not gate(m.source_root, m):
        return _reject(m, "E_GATE_REFUSED", audit)
    # Supported(m): evidence closure non-empty
    if not m.evidence_roots:
        return _reject(m, "E_OPEN_EVIDENCE", audit)
    # I(m(S_t)): the post-state invariant
    if not invariant(m.target):
        return _reject(m, "E_POSTSTATE_INVARIANT", audit)
    # Authorized(m): spend the linear lease LAST, so rejects cost nothing
    drawn = leases.spend(m.lease_id)
    if not drawn["ok"]:
        return _reject(m, "E_LEASE_EXHAUSTED", audit,
                       law="authority is linear; a spent lease is not "
                           "available to a second morphism")
    receipt = canon_hash([m.m_id, m.source_root, m.target,
                          m.transformation, m.lease_id, m.t_effect,
                          sorted(m.evidence_roots)])
    return {"verdict": "ADMITTED", "world_mutates": True,
            "proof": Proof(m.m_id,
                           premises=("I(S_t)", "G(S_t,m)", "Authorized",
                                     "Supported", "I(S_t+1)"),
                           receipt=receipt),
            "new_world_root": m.target,
            "roots_conserved": frozenset(m.evidence_roots)}


def _reject(m: CandidateMorphism, reason: str, audit: dict,
            law: str = "") -> dict:
    out = {"verdict": "REJECTED", "reason": reason, "world_mutates": False,
           "audit_only": True,
           "negative_receipt": canon_hash(["REJECTED", m.m_id, reason]),
           **audit}
    if law:
        out["law"] = law
    return out


# ── the two graphs ──────────────────────────────────────────────────────

@dataclass
class Graphs:
    """W ⊊ A. admit() results are routed here; only ADMITTED touches W."""
    world_edges: list = field(default_factory=list)
    audit_edges: list = field(default_factory=list)

    def record(self, m: CandidateMorphism, result: dict) -> None:
        self.audit_edges.append((m.m_id, result["verdict"]))
        if result.get("world_mutates"):
            self.world_edges.append((m.source_root, m.target, m.m_id))

    def subset_holds(self) -> bool:
        world_ids = {e[2] for e in self.world_edges}
        audit_ids = {e[0] for e in self.audit_edges}
        return world_ids <= audit_ids and len(world_ids) <= len(audit_ids)


# ── replay as normalization; two equivalences ───────────────────────────

def normalize(s0: str, admitted: tuple) -> str:
    """Replay = normalization of the admitted-morphism composition.
    Each admitted morphism advances the root; a break is unlawful."""
    s = s0
    for proof, target, source in admitted:
        if source != s:
            raise ValueError("E_NON_COMPOSABLE_HISTORY")
        s = target
    return s


def extensional_equiv(h1_final: str, h2_final: str) -> bool:
    return h1_final == h2_final


def constitutional_equiv(h1: dict, h2: dict) -> dict:
    """≡_C ⊊ ≡_E. Equal final state is necessary, never sufficient:
    authority paths, evidence roots, and lease consumption must match
    too."""
    same_state = h1["final_state"] == h2["final_state"]
    same_auth = h1["authority_path"] == h2["authority_path"]
    same_roots = h1["evidence_roots"] == h2["evidence_roots"]
    same_leases = h1["leases_spent"] == h2["leases_spent"]
    return {"extensional": same_state,
            "constitutional": same_state and same_auth and same_roots
            and same_leases,
            "law": "S_final(1)=S_final(2) does not imply H1 ≡ H2"}
