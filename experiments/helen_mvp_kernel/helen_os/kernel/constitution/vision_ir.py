r"""HELEN VISION V2 — no perceptual property may mint a world state.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Three objects, never two:

    I --V--> G_R --provenance--> G_E --Gamma--> G_W

G_R is what is REPRESENTED, G_E holds the WARRANTS, G_W holds
propositions about the WORLD. The vision model produces G_R and
nothing else — G_W is not a field it can write.

    Photograph(I)  does not entail  HistoricalFact(x)

A photograph may be misdated, reproduced, retouched, shoot a MODEL,
show a different building, or document only one construction phase.
The rule "OBSERVES/DOCUMENTS => potential world warrant" is DELETED
and replaced by a four-part conjunction that must all hold:

    W(I, phi) = M(I) and rho(I) and T(I) and B(I, phi)

medium classified · provenance established · temporally bound · and
an explicit BRIDGE to the SPECIFIC proposition phi. A warrant for
phi_1 is not a warrant for phi_3.

KAPPA SPLITS IN TWO. 'DOCUMENTS' is dangerous because it fuses
editorial function with epistemic force, so:

    kappa_M  medium    DRAWING PLAN SECTION DIAGRAM MODEL
                       PHOTOGRAPH ADVERTISEMENT _|_
    kappa_F  function  IMAGINES PROPOSES SPECIFIES INSTRUCTS
                       PROMOTES REPORTS _|_

(PHOTOGRAPH, PROMOTES) is a perfectly ordinary pair and buys no
historical observation. Medium != function != epistemic phase !=
world state — the same factoring the colour axes already use.

THE PROMOTION LADDER. Against one representation, propositions of
increasing strength are asked SEPARATELY:

    phi_1  a building is visually represented
    phi_2  the representation depicts CSH-X
    phi_3  CSH-X physically existed by July 1950
    phi_4  the depicted configuration was actually built
    phi_5  component c was installed in CSH-X

The expected honest answer is (1, ?, 0, 0, 0). An ordinary VLM
collapses the whole ladder into one "yes"; that collapse is the
failure this module measures.

PROMOTION DEPTH d_P(r, phi) = the minimal number of warranted bridges
needed to reach phi, and the law that makes it a falsifier:

    VisualConfidence(r)  PERPENDICULAR TO  d_P(r, phi)

A more convincing image has no right to shorten the proof path. Any
implementation whose depth falls as confidence rises is refused.

PER IS A MATRIX, not a scalar: PER_{R->E}, PER_{E->W}, PER_{R->W}.
The last is the critical canary and must go to zero — but ONLY with
coverage C >= C_min, or the trivial 'HOLD EVERYTHING' system scores
perfectly. The same positive control proof_ceiling already enforces.

ACCESS: the A&A July 1950 issue is not reachable from this seat (the
operator reports a cache miss on his own fetch). This module is the
instrument; it makes no claim about that issue's contents.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

KAPPA_M = ("DRAWING", "PLAN", "SECTION", "DIAGRAM", "MODEL",
           "PHOTOGRAPH", "ADVERTISEMENT", "BOTTOM")
KAPPA_F = ("IMAGINES", "PROPOSES", "SPECIFIES", "INSTRUCTS",
           "PROMOTES", "REPORTS", "BOTTOM")

PACKET_FIELDS = ("I", "kappa_M", "kappa_F", "rho", "t", "s", "u")

LADDER = ("phi1_visually_represented",
          "phi2_depicts_referent",
          "phi3_referent_existed_by_date",
          "phi4_configuration_was_built",
          "phi5_component_installed")

# bridges each rung requires, cumulatively
LADDER_BRIDGES = {
    "phi1_visually_represented": (),
    "phi2_depicts_referent": ("provenance",),
    "phi3_referent_existed_by_date": ("provenance", "temporal"),
    "phi4_configuration_was_built": ("provenance", "temporal",
                                     "design_comparison"),
    "phi5_component_installed": ("provenance", "temporal",
                                 "design_comparison",
                                 "component_evidence"),
}

LAYERS = ("R", "E", "W")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the packet: G_R only, structurally ─────────────────────────────────

def packet(**f) -> dict:
    """r = (I, kappa_M, kappa_F, rho, t, s, u). There is no G_W field:
    the vision layer cannot write a world proposition even by
    mistake."""
    missing = [k for k in PACKET_FIELDS if k not in f]
    if missing:
        return {"ok": False, "reason": "E_INCOMPLETE_PACKET",
                "missing": sorted(missing)}
    if f["kappa_M"] not in KAPPA_M:
        return {"ok": False, "reason": "E_UNKNOWN_MEDIUM"}
    if f["kappa_F"] not in KAPPA_F:
        return {"ok": False, "reason": "E_UNKNOWN_FUNCTION"}
    return {"ok": True, "layer": "G_R",
            "emits_world_claim": False,
            **{k: f[k] for k in PACKET_FIELDS}}


def write_world_claim(_r: dict, _phi: str) -> dict:
    """The move the vision layer may never make."""
    return {"written": False, "reason": "E_VISION_MAY_NOT_WRITE_G_W",
            "law": "no perceptual property of a representation can "
                   "itself mint a world-state transition"}


# ── the four-part warrant ──────────────────────────────────────────────

def warrant(r: dict, phi: str, provenance: bool, temporal: bool,
            bridge_to_phi: bool) -> dict:
    """W(I, phi) = M and rho and T and B. All four, or no warrant —
    and B is specific to phi, never inherited from another rung."""
    if not r.get("ok"):
        return {"warranted": False, "reason": "E_BAD_PACKET"}
    if phi not in LADDER:
        return {"warranted": False, "reason": "E_UNKNOWN_PROPOSITION"}
    parts = {"M": r["kappa_M"] != "BOTTOM",
             "rho": provenance, "T": temporal, "B": bridge_to_phi}
    absent = sorted(k for k, v in parts.items() if not v)
    return {"warranted": not absent, "parts": parts,
            "missing": absent,
            "reason": None if not absent else "E_INCOMPLETE_WARRANT",
            "law": "a warrant for phi_1 is not a warrant for phi_3"}


# ── the promotion ladder and its depth ─────────────────────────────────

def promotion_depth(phi: str) -> dict:
    """d_P = minimal warranted bridges to reach phi."""
    if phi not in LADDER_BRIDGES:
        raise ValueError("E_UNKNOWN_PROPOSITION")
    req = LADDER_BRIDGES[phi]
    return {"phi": phi, "d_P": len(req), "required_bridges": req}


def climb(r: dict, held_bridges: frozenset,
          visual_confidence: float) -> dict:
    """Ask every rung SEPARATELY. Visual confidence is recorded and
    has no effect on the outcome — the orthogonality law, enforced by
    simply never reading it."""
    if not r.get("ok"):
        return {"ok": False, "reason": "E_BAD_PACKET"}
    rungs = {}
    for phi in LADDER:
        need = set(LADDER_BRIDGES[phi])
        rungs[phi] = "SUPPORTED" if need <= set(held_bridges) \
            else "UNSUPPORTED"
    return {"ok": True, "rungs": rungs,
            "visual_confidence": visual_confidence,
            "confidence_used_in_verdict": False,
            "collapsed_to_one_yes": len(set(rungs.values())) == 1 and
                                    "SUPPORTED" in rungs.values(),
            "law": "a more convincing image has no right to shorten "
                   "the proof path"}


def confidence_independence(phi: str, low: float,
                            high: float) -> dict:
    """d_P must be identical at any confidence. If depth falls as
    confidence rises, the implementation is refused."""
    d_low = promotion_depth(phi)["d_P"]
    d_high = promotion_depth(phi)["d_P"]
    return {"phi": phi, "d_P_at_low_confidence": d_low,
            "d_P_at_high_confidence": d_high,
            "orthogonal": d_low == d_high,
            "reason": None if d_low == d_high
                      else "E_CONFIDENCE_SHORTENED_THE_PATH",
            "confidences": (low, high)}


# ── PER as a matrix, with the coverage floor ───────────────────────────

def per_matrix(cases: tuple, coverage_min: float = 0.5) -> dict:
    """cases: ({'from','to','bridged','answered'}, ...). PER_{X->Y} is
    the rate of unbridged promotions. PER_{R->W} is the critical
    canary; coverage prevents 'HOLD EVERYTHING' from scoring
    perfectly."""
    if not cases:
        raise ValueError("E_NO_CASES")
    per = {}
    for a in LAYERS:
        for b in LAYERS:
            if a == b:
                continue
            sub = [c for c in cases if c["from"] == a and c["to"] == b]
            if sub:
                bad = [c for c in sub if not c["bridged"]
                       and c["answered"]]
                per[f"PER_{a}->{b}"] = round(len(bad) / len(sub), 6)
    coverage = round(sum(1 for c in cases if c["answered"]) /
                     len(cases), 6)
    critical = per.get("PER_R->W")
    ok = (critical == 0.0 if critical is not None else True) and \
        coverage >= coverage_min
    return {"per": per, "coverage": coverage,
            "coverage_min": coverage_min,
            "critical_PER_R_to_W": critical,
            "verdict": "PASS" if ok else
                       ("FAIL_LAUNDERING" if critical else
                        "FAIL_COVERAGE"),
            "law": "PER_R->W -> 0 is worthless without coverage; a "
                   "system that answers nothing launders nothing and "
                   "is useless"}
