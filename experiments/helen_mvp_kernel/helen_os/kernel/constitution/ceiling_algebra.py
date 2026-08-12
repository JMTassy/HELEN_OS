"""Ceiling algebra + T000 — the general law the eight oracles reveal.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The Prize Papers gain: T001-T008 are not eight maritime exceptions.
They are instances of one algebra of ceilings. A transition delta
against a receipt/authority r is admissible only under all three
ceilings, and replay-valid:

    Admit(delta, r) iff
        Proof(delta)     subset of ProofCeiling(r)      (T007: derived
                                                          doc is not a
                                                          new root)
        Effect(delta)    subset of Scope(r)             (T006: verdict
                                                          scope)
        Authority(delta) subset of AuthorityCeiling(r)  (T001/T005:
                                                          effect is not
                                                          authorized
                                                          effect)
        Preconditions(delta) replay-valid

This is the same family as obligation conservation:
    D_chi subset of ProofCeiling(r_chi).

T000 — the implicit zero oracle, run BEFORE any Ship entity exists:

    Evidence does NOT entail |Vessel| = 1  =>  do not collapse to one.

The wrong architecture is documents -> Ship(id) -> facts. The right
architecture is documents -> {identity claims} -> IdentityResolution
-> {Hull_1..Hull_n}, and Merge(x, y) is ITSELF a governed transition.
Entity resolution is graph rewriting, not preprocessing — if it runs
before the reducer, HELEN can violate its constitution before a gate
even fires.

    RELAY(s) != s ;  RELAY(s) does not entail DIRECTLY_OBSERVED(s).

Success criterion, sealed: not "HELEN reconstructs the right ship" but
HELEN refuses to manufacture a cleaner world than its evidence permits.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

ACCESS_MODES = ("DIRECT", "RELAYED", "DERIVED")
# merge bases that never, on their own, license collapsing two entities
FORBIDDEN_MERGE_BASES = frozenset({
    "same_name", "same_master", "credential_carried",
    "same_name+credential_carried"})


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the five-object pipeline: SOURCE -> RELAY -> FIXTURE -> ORACLE -> RUN

@dataclass(frozen=True)
class HistoricalSource:
    """access_mode fixes the evidence CEILING. A relayed fact can never
    be promoted to directly-observed; that is its ceiling, not a flaw."""
    source_id: str
    provenance_ref: str
    access_mode: str

    def __post_init__(self):
        if self.access_mode not in ACCESS_MODES:
            raise ValueError("E_UNKNOWN_ACCESS_MODE")


def directly_observed(source: HistoricalSource) -> dict:
    """RELAY(s) does not entail DIRECTLY_OBSERVED(s)."""
    if source.access_mode != "DIRECT":
        return {"directly_observed": False,
                "ceiling": source.access_mode,
                "law": "a relayed or derived source is not directly "
                       "observed; that is its evidence ceiling"}
    return {"directly_observed": True, "ceiling": "DIRECT"}


# ── T000: cardinality is not assumed ────────────────────────────────────

def vessel_cardinality(identity_claims: tuple,
                       continuity_witnesses: tuple = ()) -> dict:
    """Evidence does not entail |Vessel| = 1. Each distinct identity
    claim seeds a candidate hull; only a continuity witness may later
    merge two. Absent a witness, the fork stands — do not collapse."""
    claimed = {c["hull_ref"] for c in identity_claims}
    merged = set()
    for w in continuity_witnesses:
        if w.get("kind") == "physical_continuity" and w.get("witness_ref"):
            merged.add(frozenset({w["from"], w["to"]}))
    return {"candidate_hulls": sorted(claimed),
            "cardinality": len(claimed),
            "assumed_one": False,
            "witnessed_merges": [sorted(m) for m in merged],
            "law": "evidence does not entail |Vessel|=1; do not collapse "
                   "to one vessel without a continuity witness"}


# ── Merge as a governed transition (graph rewriting, not preprocessing)

def propose_merge(x: str, y: str, basis: str,
                  witness: dict | None = None) -> dict:
    """Merge(x, y) is a governed transition. same_name / same_master /
    credential_carried never license it; only a physical-continuity
    witness does. Runs BEFORE the reducer, so it must be gated too."""
    if basis in FORBIDDEN_MERGE_BASES:
        return {"verdict": "REJECT", "reason": "E_UNWITNESSED_MERGE",
                "basis": basis,
                "law": "entity resolution is graph rewriting, not "
                       "preprocessing; a merge is a governed transition"}
    if basis == "physical_continuity" and witness and \
            witness.get("witness_ref"):
        return {"verdict": "MERGE_ADMITTED", "into": x,
                "witness": witness["witness_ref"]}
    return {"verdict": "HOLD", "reason": "E_MERGE_BASIS_UNKNOWN",
            "basis": basis}


# ── provenance-quotient evidence cardinality (T007 generalized) ─────────

def independent_cardinality(artifacts: tuple) -> dict:
    """N_independent = |Artifacts / ~provenance|, NOT the file, scan or
    hash count. h(a) != h(b) does not entail root(a) != root(b): SHA is
    a forward operator on artifacts with no inverse to roots. A
    translation, a transcription and an abstract are three artifacts,
    one root."""
    roots = {}
    for a in artifacts:
        root = a.get("evidence_root") or a.get("artifact_id")
        roots.setdefault(root, []).append(a.get("artifact_id"))
    return {"n_artifact": len(artifacts),
            "n_hash": len({a.get("sha256") for a in artifacts}),
            "n_independent": len(roots),
            "classes": {r: sorted(v) for r, v in sorted(roots.items())},
            "law": "N_independent = |Artifacts / ~provenance|; a "
                   "differing hash never proves an independent root"}


# ── the three ceilings, and the one Admit predicate ─────────────────────

@dataclass(frozen=True)
class Receipt:
    """A receipt/decision carries three ceilings. A transition may not
    exceed any of them."""
    receipt_id: str
    proof_ceiling: frozenset           # evidence roots it may rest on
    scope_ceiling: frozenset           # objects it may mutate
    authority_ceiling: str             # highest authority grade it grants


AUTHORITY_GRADES = ("NONE", "OBSERVED", "REPORTED", "ADJUDICATED",
                    "ADMITTED")


def _auth_rank(g: str) -> int:
    if g not in AUTHORITY_GRADES:
        raise ValueError("E_UNKNOWN_AUTHORITY_GRADE")
    return AUTHORITY_GRADES.index(g)


@dataclass(frozen=True)
class Transition:
    delta_id: str
    proof_roots: frozenset             # roots this delta rests on
    effect_objects: frozenset          # objects it would mutate
    authority_needed: str
    preconditions_replay_valid: bool


def admit(delta: Transition, r: Receipt) -> dict:
    """The single admissibility predicate. Each failing conjunct names
    the ceiling it breached — and each maps back to one of the eight
    oracles. All four, or REJECT."""
    breaches = []
    if not delta.proof_roots <= r.proof_ceiling:
        breaches.append({"ceiling": "PROOF",
                         "reason": "E_PROOF_CEILING_EXCEEDED",
                         "over": sorted(delta.proof_roots -
                                        r.proof_ceiling)})
    if not delta.effect_objects <= r.scope_ceiling:
        breaches.append({"ceiling": "SCOPE",
                         "reason": "E_SCOPE_CEILING_EXCEEDED",
                         "over": sorted(delta.effect_objects -
                                        r.scope_ceiling)})
    if _auth_rank(delta.authority_needed) > \
            _auth_rank(r.authority_ceiling):
        breaches.append({"ceiling": "AUTHORITY",
                         "reason": "E_AUTHORITY_CEILING_EXCEEDED",
                         "needed": delta.authority_needed,
                         "granted": r.authority_ceiling})
    if not delta.preconditions_replay_valid:
        breaches.append({"ceiling": "REPLAY",
                         "reason": "E_PRECONDITIONS_NOT_REPLAY_VALID"})
    if breaches:
        return {"verdict": "REJECT", "breaches": breaches,
                "law": "Admit iff Proof<=ProofCeiling and Effect<=Scope "
                       "and Authority<=AuthorityCeiling and replay-valid"}
    return {"verdict": "ADMIT", "delta": delta.delta_id,
            "under_receipt": r.receipt_id}


# the eight oracles, re-read as ceiling breaches — the algebra revealed.
ORACLE_CEILING_MAP = {
    "E_PHYSICAL_EFFECT_IS_NOT_LEGALITY": "AUTHORITY",
    "E_CROSS_LAYER_LAUNDERING": "AUTHORITY",
    "E_CARGO_IS_NOT_OWNERSHIP": "AUTHORITY",
    "E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP": "PROOF",
    "E_DERIVED_DOC_IS_NOT_NEW_WITNESS": "PROOF",
    "E_INTERCEPTED_IS_NOT_DELIVERED": "PROOF",
    "E_PARTIAL_VERDICT_SCOPE": "SCOPE",
    "E_NAME_IS_NOT_IDENTITY": "SCOPE",     # merge widens object scope
}


def effect_within_scope(receipt_scope: frozenset, effect: str) -> dict:
    """The general law behind PARTIAL_VERDICT_SCOPE: Effect(r) subset of
    Scope(r); x not in Scope(r) => r does not license mutate(x)."""
    if effect not in receipt_scope:
        return {"verdict": "REFUSED", "reason": "E_OUT_OF_SCOPE",
                "effect": effect,
                "law": "x not in Scope(r) implies r does not license "
                       "mutate(x)"}
    return {"verdict": "IN_SCOPE", "effect": effect}
