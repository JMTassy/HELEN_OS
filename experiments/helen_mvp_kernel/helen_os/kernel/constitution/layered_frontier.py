r"""HELEN_LAYERED_FRONTIER_V0 — a conservation-law runtime for
licensed state transitions.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: FROZEN (operator ruling, born from the Qwen download stall —
the same constitutional law applies before cognition begins).

THE FIVE-FRONTIER STATE:

    F* = (F_S, F_I, F_C, F_E, F_X)
    substrate · instrument · cognition · epistemic entitlement ·
    authorized effect

THE LAW IS NON-AUTOMATIC COUPLING, not mere monotonicity:

    Delta F_i > 0  does not entail  Delta F_j > 0   (i != j)

Every cross-frontier move requires its own transition license. A
model downloaded advances F_S and leaves the other four at ZERO —
and the receipt must SAY so: the NON_DELTAS block is mandatory,
because a successful event at one layer must not acquire unrecorded
implications elsewhere. Every receipt answers FOUR questions: what
changed, what licensed it, what did NOT change, how is it re-derived.

EPISTEMIC PRESSURE (a diagnostic, never a confidence):

    Pi_C(c) = N_representations(c) / max(1, N_independent_roots(c))

One source fanned into OCR, summaries, embeddings and a hundred
agents gives Pi_C >> 1 with N_W = 1. The conservation invariant:

    Delta Pi_C > 0  AND  Delta W = 0  AND  Delta D_valid = 0
        =>  Delta F_E = 0

Pressure without new witnesses moves nothing.

CONSERVATION OF MINTING RIGHTS — the sharpened principle:

    a layer may transform what it owns, but may not mint the
    constitutive resource of the next layer

Representation mints representations; cognition mints candidates;
observation mints empirical warrants; derivation mints licensed
consequences; Gamma mints admission; capability licenses effect;
execution produces mutation; receipt records it. Representation
never mints warrants; candidates never mint authority; receipts
never mint effects.

COGNITIVE ELASTICITY gives the swarm an economics:

    eps_C = dlog Q_useful / dlog C

If xhigh costs triple and Q_useful stays flat, MCY ~ 0 and HELEN
learns that more reasoning is economically useless for that task —
measured, not asserted.

Open problems, recorded not hidden: license semantics differ per
frontier (substrate licenses, warrants, authority decisions and
capabilities share an interface, not a semantics); F_E is a
poset/antichain while F_S may be a plain state machine.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import math

FRONTIERS = ("F_S", "F_I", "F_C", "F_E", "F_X")

MINTING_RIGHTS = {
    "representation": "representation",
    "cognition": "candidate",
    "observation": "empirical_warrant",
    "derivation": "licensed_consequence",
    "gamma": "institutional_admission",
    "capability": "effect_license",
    "execution": "world_mutation",
    "receipt": "witnessed_record",
}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the transition object: (Delta, License, NonDelta, ReDerivation) ────

def transition(layer: str, before: str, after: str, deltas: dict,
               licenses: dict, non_deltas: dict,
               rederivation: str | None) -> dict:
    """The kernel object. Every nonzero delta needs its license;
    every frontier NOT moved must appear in NON_DELTAS; and the
    receipt carries its re-derivation recipe or it is not a
    receipt."""
    unknown = sorted((set(deltas) | set(non_deltas)) - set(FRONTIERS))
    if unknown:
        return {"ok": False, "reason": "E_UNKNOWN_FRONTIER",
                "unknown": tuple(unknown)}
    moved = {f for f, d in deltas.items() if d != 0}
    unlicensed = sorted(f for f in moved if not licenses.get(f))
    if unlicensed:
        return {"ok": False, "reason": "E_UNLICENSED_TRANSITION",
                "unlicensed": tuple(unlicensed),
                "law": "Delta_j != 0 requires Verify(license_j)"}
    missing_nd = sorted(set(FRONTIERS) - moved - set(non_deltas))
    if missing_nd:
        return {"ok": False, "reason": "E_MISSING_NON_DELTAS",
                "missing": tuple(missing_nd),
                "law": "a successful event at one layer must not "
                       "acquire unrecorded implications elsewhere"}
    if not rederivation:
        return {"ok": False, "reason": "E_NO_REDERIVATION_PATH"}
    return {"ok": True, "layer": layer, "before": before,
            "after": after, "deltas": dict(sorted(deltas.items())),
            "licenses": dict(sorted(licenses.items())),
            "non_deltas": dict(sorted(non_deltas.items())),
            "rederivation": rederivation,
            "four_questions_answered": True}


def cross_advance(from_frontier: str, to_frontier: str,
                  licensed: bool) -> dict:
    """Delta F_i > 0 does not entail Delta F_j > 0. Model downloaded
    (F_S) says nothing about loadable (F_I), producible (F_C),
    entitled (F_E) or authorized (F_X)."""
    if from_frontier not in FRONTIERS or to_frontier not in FRONTIERS:
        return {"advanced": None, "reason": "E_UNKNOWN_FRONTIER"}
    if not licensed:
        return {"advanced": False, "reason": "E_UNLICENSED_COUPLING",
                "law": "progress at one layer cannot silently mint "
                       "progress at the next"}
    return {"advanced": True, "from": from_frontier,
            "to": to_frontier, "via": "explicit_license"}


# ── epistemic pressure ─────────────────────────────────────────────────

def epistemic_pressure(n_representations: int,
                       n_independent_roots: int) -> dict:
    if n_representations < 0 or n_independent_roots < 0:
        raise ValueError("E_NEGATIVE_COUNT")
    pi = round(n_representations / max(1, n_independent_roots), 6)
    return {"Pi_C": pi, "is_confidence": False,
            "reading": "pressure — how often the claim appears "
                       "relative to independent evidentiary roots"}


def pressure_conservation(delta_pi: float, delta_w: int,
                          delta_d_valid: int) -> dict:
    """The invariant born from swarm consensus, RAG duplication,
    OCR variants and syndication alike."""
    if delta_pi > 0 and delta_w == 0 and delta_d_valid == 0:
        return {"delta_F_E": 0,
                "reason": "E_PRESSURE_IS_NOT_EVIDENCE",
                "law": "rising pressure with no new witness and no "
                       "new valid derivation moves the epistemic "
                       "frontier by exactly zero"}
    return {"delta_F_E": "licensable",
            "note": "a new witness or valid derivation may license "
                    "movement — through the ordinary door"}


# ── conservation of minting rights ─────────────────────────────────────

def mint(layer: str, resource: str) -> dict:
    if layer not in MINTING_RIGHTS:
        return {"minted": False, "reason": "E_UNKNOWN_LAYER"}
    owned = MINTING_RIGHTS[layer]
    if resource != owned:
        return {"minted": False,
                "reason": "E_MINTING_RIGHTS_VIOLATION",
                "layer": layer, "owns": owned, "attempted": resource,
                "law": "a layer may transform what it owns, but may "
                       "not mint the constitutive resource of the "
                       "next layer"}
    return {"minted": True, "layer": layer, "resource": resource}


# ── proxy laundering (King of the Witches, 1969) ───────────────────────

def proxy_root(author_is_distinct_person: bool,
               derivation_support: frozenset,
               subject: str) -> dict:
    """Author(x) != Root(x). A biographer is a REPRESENTATION
    amplifier, not a second evidentiary root: when every foundational
    claim derives from the subject alone (Subject -> dictation ->
    biographer -> text), the published third-party artifact leaves
    N_epi at exactly 1 — a standard pipeline mints N_epi = 2 from the
    byline, and that is the laundering. The typographical author is
    metadata; the causal origin is the root."""
    only_subject = derivation_support <= frozenset({subject})
    if only_subject:
        return {"N_epi": 1,
                "author_distinct": author_is_distinct_person,
                "reason": "E_PROXY_IS_NOT_A_ROOT",
                "law": "trace the causal origin, not the byline; a "
                       "proxy adds representational mass and mints "
                       "zero truth"}
    return {"N_epi": 1 + len(derivation_support -
                             frozenset({subject})),
            "note": "independent support beyond the subject raises "
                    "the count through the ordinary door"}


def capability_mint(kappa: str, witnesses: frozenset) -> dict:
    """The reverse double-spend: an UNWARRANTED MINTING EVENT.
    emptyset -> kappa_lineage via subjective claim is refused — a
    hidden, unobservable past event mints no institutional token.
    Documented procedure does not entail verified efficacy, and a
    successfully believed kappa is a sociological fact in F_C, never
    an admission in F_X."""
    if not witnesses:
        return {"minted": False, "kappa": kappa,
                "reason": "E_UNLICENSED_CAPABILITY_MINT",
                "sociological_effect_recordable": True,
                "law": "an unobservable past event mints no token; "
                       "belief in kappa is F_C data, not F_X "
                       "admission"}
    return {"minted": True, "kappa": kappa,
            "witnesses": tuple(sorted(witnesses))}


# ── cognitive elasticity ───────────────────────────────────────────────

def elasticity(q1: float, q2: float, c1: float, c2: float) -> dict:
    """eps_C ~ ((Q2-Q1)/Q1) / ((C2-C1)/C1); MCY = dQ/dC. Flat yield
    at tripled cost is a measured verdict on reasoning depth."""
    if min(q1, c1) <= 0 or c2 <= 0:
        raise ValueError("E_BAD_BASELINE")
    dq_rel = (q2 - q1) / q1
    dc_rel = (c2 - c1) / c1
    eps = round(dq_rel / dc_rel, 6) if dc_rel != 0 else math.inf
    mcy = round((q2 - q1) / (c2 - c1), 6) if c2 != c1 else math.inf
    return {"eps_C": eps, "MCY": mcy,
            "economically_useless": q2 <= q1 and c2 > c1,
            "law": "more reasoning is a cost with a measured yield, "
                   "never a presumed good"}
