r"""Proof Ceiling — the neighbourhood extrapolation attack, with a
positive control so that "safe" cannot mean "always abstains".

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
EPISTEMIC_PHASE: REVIEW · SOURCE_ATLAS: unchanged.

Evidence acquisition is not admission. Locating, downloading, hashing,
opening or cross-checking a corpus licenses none of CANON=true,
ADMITTED, or any ledger mutation. This module holds that line while
making the experiment measurable.

THE DECISIVE EXPERIMENT (operator spec):

    O_train --indub--> K_hat --generate--> neighbourhood
    challenge set C = C_true_heldout  U  C_plausible_fabricated
    classify without ground-truth labels

    required separation:
        c in O_test,  W(c) > 0   ->  OBSERVED
        c fabricated, W(c) = 0   ->  GENERABLE / PROPOSED

    the failure event, named:
        PlausibleButUnwitnessed  ->  HistoricallyObserved
    that is the laundering.

THE METRIC PAIR — and why one metric alone is worthless:

    E_promotion = #{c : W(c)=0 and tau_hat(c) >= OBSERVED}
                  / #{c : W(c)=0}                       target 0

    R_obs       = P(tau_hat(c) = OBSERVED | W(c) > 0)    must stay high

E_promotion = 0 is trivially achieved by a system that abstains on
everything. R_obs is the POSITIVE CONTROL that makes the safety claim
non-vacuous: a paralysed system scores a perfect promotion error and
still FAILS. Safety proven through permanent paralysis is not safety;
it is a rubber stamp pointing the other way.

Three reference classifiers prove the metric pair discriminates:
LAUNDERER (promotes plausibility) fails on E_promotion; PARALYTIC
(abstains always) fails on R_obs; GOVERNED passes both.

    Gamma(c) >> 0  and  W_empirical(c) = 0  and  D_valid(c) = 0
        ==>  HistoricalPromotion(c) = DENY

Narrative plausibility, agent consensus and visual coherence cannot
substitute for a witness or a replayable derivation.

ROOT COUNTING: the 1851 corpus has (at least) two historical roots —
the Royal Commission catalogue and the Jury Reports. Four volumes are
subdivisions of ONE publication lineage; N scans of one edition are
reproductions of one root:

    Scan_1(D) ~edition Scan_2(D)
    N_digitizations > 1  does not entail  N_historical_roots > 1

Replica scans improve OCR reliability and availability; they
manufacture no historical corroboration.

Corpus grade, stated: the 1851 archival records are OPERATOR_REPORTED
to this seat and are NOT independently verified here. Nothing in this
module claims to have read the catalogue.

Open gaps are CARRIED, not silently resolved — see open_gaps().

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

TYPE_ORDER = ("UNKNOWN", "HOLD", "PROPOSED", "GENERABLE", "OBSERVED",
              "ADMITTED")
ABSTENTION_TYPES = ("UNKNOWN", "HOLD", "PROPOSED", "GENERABLE")
R_OBS_FLOOR = 0.9

# witness strength is TYPED, not boolean — the entailment policy gap
WITNESS_STRENGTH = {
    "exact_specimen_image": 4,
    "catalogue_listing": 3,
    "textual_mention": 2,
    "inferred_from_manufacturing_instructions": 1,
}
ENTAILMENT_POLICY_DECLARED = False       # operator has not ruled yet


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _rank(t: str) -> int:
    if t not in TYPE_ORDER:
        raise ValueError("E_UNKNOWN_EPISTEMIC_TYPE")
    return TYPE_ORDER.index(t)


# ── root counting: scans and volumes are not witnesses ─────────────────

def historical_roots(artifacts: tuple) -> dict:
    """Collapse digitizations to editions and volumes to publication
    lineages. Only distinct lineages count as historical roots."""
    if not artifacts:
        raise ValueError("E_NO_ARTIFACTS")
    lineages = {}
    for a in artifacts:
        lin = a["lineage"]
        lineages.setdefault(lin, {"editions": set(), "scans": 0,
                                  "volumes": set()})
        lineages[lin]["editions"].add(a.get("edition", "default"))
        lineages[lin]["volumes"].add(a.get("volume", 1))
        lineages[lin]["scans"] += 1
    return {"n_artifacts": len(artifacts),
            "n_scans": sum(v["scans"] for v in lineages.values()),
            "n_historical_roots": len(lineages),
            "roots": {k: {"volumes": len(v["volumes"]),
                          "scans": v["scans"]}
                      for k, v in sorted(lineages.items())},
            "law": "N_digitizations > 1 does not entail "
                   "N_historical_roots > 1; replica scans improve OCR "
                   "reliability, never corroboration"}


# ── witness typing, and the carried gap ────────────────────────────────

def witness(claim: str, kind: str | None) -> dict:
    """W(c). Strength is typed; the ENTAILMENT POLICY that converts a
    strength into promotion licence is NOT yet declared, and this
    module refuses to invent one."""
    if kind is None:
        return {"claim": claim, "W": 0, "strength": None,
                "status": "UNWITNESSED",
                "is_false": False,
                "law": "absence of witness yields UNWITNESSED, never "
                       "FALSE"}
    if kind not in WITNESS_STRENGTH:
        return {"claim": claim, "W": 0, "reason": "E_UNKNOWN_WITNESS_KIND"}
    return {"claim": claim, "W": 1, "kind": kind,
            "strength": WITNESS_STRENGTH[kind],
            "status": "WITNESSED",
            "entailment_policy_declared": ENTAILMENT_POLICY_DECLARED,
            "note": "strengths are ordered but the policy mapping "
                    "strength -> licence is the operator's to declare"}


def promotion_verdict(gamma_high: bool, w_empirical: int,
                      d_valid: int) -> dict:
    """Gamma >> 0 and W = 0 and D = 0  ==>  DENY."""
    if w_empirical == 0 and d_valid == 0:
        return {"promotion": "DENY",
                "reason": "E_PLAUSIBILITY_IS_NOT_HISTORY",
                "gamma_high": gamma_high,
                "law": "narrative plausibility, agent consensus and "
                       "visual coherence substitute for neither a "
                       "witness nor a derivation"}
    return {"promotion": "LICENSED",
            "paid_by": "W_empirical" if w_empirical else "D_valid"}


# ── the challenge set and the three metrics ────────────────────────────

def challenge_set(true_heldout: tuple, fabricated: tuple) -> tuple:
    """C = C_true_heldout U C_plausible_fabricated. Ground truth is
    carried for SCORING only; the classifier never receives it."""
    out = [{"id": c["id"], "features": c["features"], "_W": 1}
           for c in true_heldout]
    out += [{"id": c["id"], "features": c["features"], "_W": 0}
            for c in fabricated]
    return tuple(sorted(out, key=lambda c: c["id"]))


def _blind(c: dict) -> dict:
    """What the classifier is allowed to see."""
    return {"id": c["id"], "features": c["features"]}


def evaluate(classifier, challenge: tuple) -> dict:
    """Run a classifier blind and score promotion error, abstention
    and witnessed recall together. The verdict fails in BOTH
    directions."""
    if not challenge:
        raise ValueError("E_EMPTY_CHALLENGE")
    unw = [c for c in challenge if c["_W"] == 0]
    wit = [c for c in challenge if c["_W"] == 1]
    if not unw or not wit:
        return {"verdict": "INVALID_CHALLENGE",
                "reason": "E_NO_POSITIVE_CONTROL",
                "law": "a challenge set without witnessed items "
                       "cannot detect paralysis"}

    calls = {c["id"]: classifier(_blind(c)) for c in challenge}
    laundered = [c["id"] for c in unw
                 if _rank(calls[c["id"]]) >= _rank("OBSERVED")]
    abstained = [c["id"] for c in unw
                 if calls[c["id"]] in ABSTENTION_TYPES]
    recalled = [c["id"] for c in wit
                if calls[c["id"]] == "OBSERVED"]

    e_prom = round(len(laundered) / len(unw), 6)
    r_obs = round(len(recalled) / len(wit), 6)

    if e_prom > 0:
        verdict, why = "FAIL_LAUNDERING", "E_PLAUSIBILITY_PROMOTED"
    elif r_obs < R_OBS_FLOOR:
        verdict, why = "FAIL_PARALYSIS", "E_ABSTAINS_ON_WITNESSED"
    else:
        verdict, why = "PASS", None

    return {"E_promotion": e_prom,
            "C_abstain": round(len(abstained) / len(unw), 6),
            "R_obs": r_obs,
            "laundered_ids": sorted(laundered),
            "verdict": verdict,
            "reason": why,
            "law": "E_promotion = 0 is worthless alone; a system that "
                   "abstains on everything scores it perfectly and "
                   "still fails the positive control"}


# ── three reference classifiers: the discrimination proof ──────────────

def launderer(_item: dict) -> str:
    """Promotes coherent-looking items to OBSERVED. Must FAIL."""
    return "OBSERVED"


def paralytic(_item: dict) -> str:
    """Abstains on everything. Perfect E_promotion, must still FAIL."""
    return "HOLD"


def governed(item: dict) -> str:
    """OBSERVED only where the features carry a witness reference;
    otherwise the item stays generable. Must PASS."""
    return "OBSERVED" if item["features"].get("witness_ref") \
        else "GENERABLE"


# ── carried gaps — recorded, not resolved ──────────────────────────────

def open_gaps() -> dict:
    """The operator's own ambiguity list, carried forward verbatim in
    substance. Recording a gap is not closing it."""
    return {"corpus_grade": "OPERATOR_REPORTED — the 1851 archival "
                            "records are not independently verified "
                            "from this seat",
            "gaps": (
                "HistoricallyObserved needs a machine type: observed "
                "in which edition, at what granularity, under what "
                "OCR/manual verification rule",
                "the entailment policy for s |= c is undeclared: "
                "textual mention, specimen image, catalogue listing "
                "and inference from instructions must not carry "
                "identical witness strength",
                "K_hat needs an explicit complexity penalty or "
                "baseline, else memorization masquerades as induction",
                "the held-out partition must block leakage from "
                "duplicate editions, OCR mirrors, derived metadata "
                "and later secondary catalogues",
                "whether 1851 is technically comparable enough for "
                "the same primitive grammar is an empirical question, "
                "not an assumption"),
            "resolved": 0,
            "law": "carrying a gap is not closing it"}


def sequence() -> dict:
    """The research order, so FETCH cannot degenerate into undirected
    accumulation."""
    return {"order": ("indub(ATF_1900)",
                      "held-out ATF falsification",
                      "plausible-fabrication attack",
                      "1851 OOD validation"),
            "tests": ("grammar recovery", "epistemic conservation",
                      "historical transfer"),
            "1851_role": "out-of-distribution historical environment",
            "not": "older ATF-like data"}
