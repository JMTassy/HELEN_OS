"""Ceiling completeness harness — the algebra tests itself.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The closure: a growing list of domain-specific prohibitions collapsed
into ONE admission invariant.

    Admit(delta, r) iff
        Proof(delta)     subset of ProofCeiling(r)      what may I claim
        Effect(delta)    subset of Scope(r)             what may I change
        Authority(delta) subset of AuthorityCeiling(r)  what may this
                                                        actor decide
        ReplayValid(Preconditions(delta))               reconstructible
                                                        from admitted
                                                        state

The success criterion is no longer "find T009". It is:

    does there exist a delta that passes all four ceilings and is
    nevertheless constitutionally invalid?

If one exists, the algebra is incomplete. If heterogeneous corpora
(Prize Papers, Crystal Palace, ATF, Sound Toll, Crew Lists) keep
failing to produce one, evidence accumulates that the archival rules
are the projection of a small governed-transition algebra.

This harness makes the test executable:
  1. compile_to_ceiling: every SAFETY prohibition built this session
     maps to PROOF / SCOPE / AUTHORITY / REPLAY. An unmapped safety
     falsifier is diagnostic — the constitution must grow.
  2. THE HONEST FINDING: the liveness falsifiers (HOLD != DEADLOCK,
     the scheduler, witnessed resolution) do NOT map to the four
     ceilings, because those are SAFETY predicates (what may NOT
     happen) and liveness is the DUAL (what MUST eventually happen).
     That is not an unmapped safety rule; it is the second axis the
     frontier already carries (Safety AND Liveness).
  3. ontology_effect: ΔOntology != empty => Effect != empty =>
     admission required. Merge/dedup/alias-collapse/canonicalization/
     record-linkage change |E| and are therefore SCOPE effects, never
     innocent preprocessing.
  4. completeness_probe: attempt to exhibit a delta passing all four
     ceilings yet invalid. Reports NONE_WITNESSED — and, by the
     possibility-space law applied REFLEXIVELY, reports completeness
     as UNKNOWN, never PROVEN. NotObserved(counterexample) does not
     entail Impossible(counterexample). The constitution polices its
     own completeness claim with its own law.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

CEILING_BASIS = ("PROOF", "SCOPE", "AUTHORITY", "REPLAY")

# the duality the operator named — each ceiling answers one question.
CEILING_QUESTION = {
    "PROOF": "what may I claim?",
    "SCOPE": "what may I change?",
    "AUTHORITY": "what may this actor decide?",
    "REPLAY": "can the transition be reconstructed from admitted state?",
}

# the safety axis vs the liveness axis. The four ceilings are SAFETY.
SAFETY_AXIS = "[]¬IllegalMutation"
LIVENESS_AXIS = "[](CriticalReachable => <>Resolution)"


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the census: every SAFETY prohibition -> its ceiling ─────────────────
# curated to the genuine constitutional non-implications built across
# the session (not the type-guards). Each maps to exactly one ceiling.

SAFETY_PROHIBITION_CENSUS = {
    # PROOF — evidence sufficiency; what may I claim
    "extraction != truth": "PROOF",
    "projection != evidence": "PROOF",
    "convergence != proof": "PROOF",
    "retrieval density != epistemic independence": "PROOF",
    "summary != verdict": "PROOF",
    "title != content": "PROOF",
    "clone != original": "PROOF",
    "existence != proof": "PROOF",
    "derived doc != new witness": "PROOF",
    "document location != authorship": "PROOF",
    "intercepted != delivered": "PROOF",
    "glyph != type": "PROOF",
    "Generable != HistoricallyObserved": "PROOF",
    "NotObserved != Impossible": "PROOF",
    "Observed(A) & Observed(B) != Observed(A.B)": "PROOF",
    "artifact authenticity != claim truth": "PROOF",
    "DocumentNotFound != EventDidNotOccur": "PROOF",
    # SCOPE — what may I change; ontology effects
    "partial verdict scope": "SCOPE",
    "name != identity (merge)": "SCOPE",
    "effect out of scope": "SCOPE",
    "corpus boundary": "SCOPE",
    "same archive != independent witnesses": "SCOPE",
    # AUTHORITY — what may this actor decide
    "capability != authority": "AUTHORITY",
    "captured != lawfully captured": "AUTHORITY",
    "ADMIT != EXECUTE": "AUTHORITY",
    "HAL PASS != ADMIT": "AUTHORITY",
    "credential != permission (cross-layer)": "AUTHORITY",
    "cargo != ownership": "AUTHORITY",
    "learning != authority": "AUTHORITY",
    "authority laundering (later != earlier)": "AUTHORITY",
    "motif has no authority": "AUTHORITY",
    "person != economic instrument": "AUTHORITY",
    "min distance != admit": "AUTHORITY",
    "confidence != admission": "AUTHORITY",
    # REPLAY — reconstructible from admitted state; arrow of time
    "state != lawful history": "REPLAY",
    "stored state != replayed state": "REPLAY",
    "compensation != erasure": "REPLAY",
    "court judgment != world history": "REPLAY",
    "valid at intake != valid at execution": "REPLAY",
    "cursor before durable closure": "REPLAY",
    "history rewrite": "REPLAY",
    "local receipt != global history": "REPLAY",
    "capacity/environment precondition": "REPLAY",
    "enumeration != provenance closure": "REPLAY",
}

# the liveness prohibitions — deliberately NOT mapped to a safety
# ceiling. They are the DUAL axis, not unmapped safety rules.
LIVENESS_PROHIBITIONS = frozenset({
    "HOLD != DEADLOCK",
    "eternal hold is a liveness violation",
    "nothing critical disappears because nothing happened",
    "obligation persists until witnessed discharge",
    "impossibility must be witnessed not asserted",
})


def compile_to_ceiling(prohibition: str) -> dict:
    """Map a safety prohibition to its ceiling. A liveness prohibition
    reports LIVENESS_AXIS (correct, not unmapped). Anything else is
    E_UNMAPPED — the diagnostic that the constitution must grow."""
    if prohibition in SAFETY_PROHIBITION_CENSUS:
        c = SAFETY_PROHIBITION_CENSUS[prohibition]
        return {"prohibition": prohibition, "ceiling": c,
                "axis": "SAFETY", "question": CEILING_QUESTION[c]}
    if prohibition in LIVENESS_PROHIBITIONS:
        return {"prohibition": prohibition, "ceiling": None,
                "axis": "LIVENESS",
                "note": "the dual axis; the four safety ceilings cannot "
                        "represent a MUST-eventually predicate, and are "
                        "not meant to"}
    return {"prohibition": prohibition, "ceiling": None,
            "axis": "UNMAPPED", "reason": "E_UNMAPPED",
            "law": "a safety falsifier that maps to no ceiling is "
                   "diagnostic: the constitution must grow"}


def census_is_total() -> dict:
    """Every safety prohibition maps to exactly one of the four
    ceilings; every ceiling is used; no safety prohibition is
    unmapped."""
    used = {SAFETY_PROHIBITION_CENSUS[p] for p in SAFETY_PROHIBITION_CENSUS}
    unmapped = [p for p in SAFETY_PROHIBITION_CENSUS
                if SAFETY_PROHIBITION_CENSUS[p] not in CEILING_BASIS]
    return {"safety_prohibitions": len(SAFETY_PROHIBITION_CENSUS),
            "ceilings_used": sorted(used),
            "all_four_used": set(used) == set(CEILING_BASIS),
            "unmapped": unmapped,
            "total": not unmapped and set(used) == set(CEILING_BASIS),
            "liveness_prohibitions": len(LIVENESS_PROHIBITIONS),
            "axes": (SAFETY_AXIS, LIVENESS_AXIS)}


# ── the ontology-effect theorem ─────────────────────────────────────────

ONTOLOGY_CHANGING_OPS = frozenset({
    "merge", "dedup", "alias_collapse", "identity_stitch",
    "canonicalize_entity", "record_linkage", "event_coalesce"})


def ontology_effect(op: str, entities_before: int,
                    entities_after: int) -> dict:
    """ΔOntology != empty => Effect != empty => admission required.
    An operation that changes the cardinality of the represented world
    is an EFFECT (a SCOPE-ceiling transition), never innocent
    preprocessing — this is WHY Merge must be governed, generalized
    beyond ships."""
    delta = entities_after - entities_before
    changes_ontology = op in ONTOLOGY_CHANGING_OPS or delta != 0
    if changes_ontology:
        return {"op": op, "delta_cardinality": delta,
                "has_effect": True, "ceiling": "SCOPE",
                "requires_admission": True,
                "law": "normalization that changes ontology is an "
                       "effect; it must pass the ceiling algebra before "
                       "mutation"}
    return {"op": op, "delta_cardinality": 0, "has_effect": False,
            "requires_admission": False,
            "note": "a pure representation transform changes no "
                    "ontology and needs no admission"}


# ── the adversarial completeness probe ──────────────────────────────────

@dataclass(frozen=True)
class CandidateDelta:
    """A candidate for the incompleteness question: does it pass all
    four ceilings yet remain invalid?"""
    delta_id: str
    proof_ok: bool
    scope_ok: bool
    authority_ok: bool
    replay_ok: bool
    independently_invalid: bool        # invalid for a reason OUTSIDE
    #                                    the four ceilings, if any


def is_counterexample(c: CandidateDelta) -> bool:
    """A counterexample passes all four ceilings AND is still invalid.
    Its existence would prove the algebra incomplete."""
    return (c.proof_ok and c.scope_ok and c.authority_ok and c.replay_ok
            and c.independently_invalid)


def completeness_probe(candidates: tuple) -> dict:
    """Search the candidate set for a counterexample. Report NONE_
    WITNESSED if none — and, by the possibility-space law applied
    reflexively, report completeness as UNKNOWN, never PROVEN: absence
    of a witnessed counterexample does not entail its impossibility."""
    counterexamples = [c.delta_id for c in candidates
                       if is_counterexample(c)]
    if counterexamples:
        return {"verdict": "ALGEBRA_INCOMPLETE",
                "counterexamples": counterexamples,
                "law": "a delta passing all four ceilings yet invalid "
                       "proves the ceiling algebra incomplete"}
    return {"verdict": "NO_COUNTEREXAMPLE_WITNESSED",
            "completeness": "UNKNOWN",
            "candidates_checked": len(candidates),
            "law": "NotObserved(counterexample) does not entail "
                   "Impossible(counterexample); completeness is UNKNOWN, "
                   "never PROVEN — the constitution polices its own "
                   "completeness claim with its own law"}


# corpora that have so far failed to produce a counterexample — the
# accumulating (not conclusive) evidence base.
CORPORA_SEARCHED = ("crystal_palace_1851", "atf_desk_book",
                    "prize_papers_hca32", "uzik_google_street")
