r"""Corpus Protocol — historical adversarial testing of a FROZEN
governance calculus.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The operator's refinement: do not let the corpus programme become
another source of doctrine. The discipline, executable:

1. FREEZE before opening each corpus:
       C_0 = (P, S, A, R)
       M_0 = (alpha, beta, rho, R, chi)
   The frozen pair is hashed; extraction runs against that version.

2. PREREGISTER D -> expected lessons BEFORE extraction. Opening a
   corpus without preregistration is refused (E_UNREGISTERED_CORPUS).

3. CLASSIFY every discovered failure into exactly one of:
       ALREADY_REPRESENTABLE      (the calculus covers it)
       NEW_PARAMETERIZATION       (an existing invariant, new numbers)
       CANDIDATE_NEW_INVARIANT    (the ONLY class that is chiddush)
       NOT_RELEVANT
   Historical storytelling cannot silently expand the theory.

4. VALUE CRITERION. Value(D) > 0 iff D falsifies an existing
   invariant, reveals non-closure under composition, exposes a
   missing metrology variable, or changes a measurable risk bound.
   Everything else goes into the history notebook, not the
   architecture.

The corpus order, as ruled (Hamilton -> statistical quality control
is one continuous thread: precision artifact -> precision process ->
statistical admission -> risk-calibrated verifier):

    HAMILTON -> QUALITY_CONTROL -> BOILER -> RAIL -> NAVIGATION ->
    TELEGRAPH -> AVIATION -> PHARMACOPEIA -> PATENT

The quality-control crosswalk (NIST framing, relayed): acceptance
sampling separates consumer's risk (accepting bad product) from
producer's risk (rejecting good product), and is fundamentally an
ACCEPT/REJECT decision, not an estimate of lot quality. Hence:

    admission decision != world-model estimation

— a gate need not know exactly how trustworthy a trace is in order
to decide the available witness is insufficient for admission.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import hashlib
import json

FROZEN_CALCULUS = ("PROOF", "SCOPE", "AUTHORITY", "REPLAY")
FROZEN_METROLOGY = ("alpha", "beta", "rho", "R", "chi")

CORPUS_ORDER = ("HAMILTON", "QUALITY_CONTROL", "BOILER", "RAIL",
                "NAVIGATION", "TELEGRAPH", "AVIATION", "PHARMACOPEIA",
                "PATENT")

# corpora handed over by the operator out of sequence — the paste is
# the grant; they still pass the same preregistration discipline
OPERATOR_SUPPLIED = ("MESMERISM_1844", "MILITARY_SEA_DICTIONARY_1711")

FINDING_CLASSES = ("ALREADY_REPRESENTABLE", "NEW_PARAMETERIZATION",
                   "CANDIDATE_NEW_INVARIANT", "NOT_RELEVANT")

VALUE_FLAGS = ("falsifies_existing_invariant",
               "reveals_non_closure_under_composition",
               "exposes_missing_metrology_variable",
               "changes_measurable_risk_bound")

QC_CROSSWALK = {
    "consumer_risk": "alpha (false admission)",
    "producer_risk": "beta (false rejection)",
    "lot": "trace population",
    "sampling_plan": "evaluation protocol",
    "OC_curve": "verifier discrimination curve",
}

PROGRAMME = ("historical adversarial testing of a frozen governance "
             "calculus")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def freeze() -> dict:
    """C_0 and M_0, hashed. Every extraction cites this version."""
    payload = canon({"C_0": FROZEN_CALCULUS, "M_0": FROZEN_METROLOGY})
    return {"C_0": FROZEN_CALCULUS, "M_0": FROZEN_METROLOGY,
            "frozen_hash": hashlib.sha256(
                payload.encode()).hexdigest()[:16],
            "law": "freeze the calculus and the metrology vector "
                   "BEFORE opening the corpus"}


def preregister(corpus: str, expected_lessons: tuple) -> dict:
    """D -> L_hat_D, before extraction, against the frozen version."""
    if corpus not in CORPUS_ORDER and corpus not in OPERATOR_SUPPLIED:
        return {"registered": False, "reason": "E_UNKNOWN_CORPUS",
                "corpus": corpus}
    if not expected_lessons:
        return {"registered": False, "reason": "E_EMPTY_PREREGISTRATION",
                "note": "a preregistration with no expectations is "
                        "not a preregistration"}
    return {"registered": True, "corpus": corpus,
            "expected_lessons": tuple(expected_lessons),
            "against": freeze()["frozen_hash"],
            "law": "preregistration precedes extraction"}


def open_corpus(corpus: str, registration: dict) -> dict:
    """Extraction may begin only on a registered corpus at the
    current frozen version."""
    if not registration.get("registered") or \
            registration.get("corpus") != corpus:
        return {"opened": False, "reason": "E_UNREGISTERED_CORPUS"}
    if registration.get("against") != freeze()["frozen_hash"]:
        return {"opened": False, "reason": "E_STALE_FREEZE",
                "note": "the calculus changed since preregistration; "
                        "re-freeze and re-register"}
    return {"opened": True, "corpus": corpus,
            "mode": PROGRAMME}


def classify_finding(finding: str, cls: str) -> dict:
    """Exactly one of the four classes; only CANDIDATE_NEW_INVARIANT
    is chiddush."""
    if cls not in FINDING_CLASSES:
        return {"finding": finding, "classified": False,
                "reason": "E_UNKNOWN_FINDING_CLASS"}
    return {"finding": finding, "classified": True, "class": cls,
            "is_constitutional_chiddush":
                cls == "CANDIDATE_NEW_INVARIANT",
            "law": "only a candidate new invariant counts as "
                   "constitutional chiddush; storytelling does not "
                   "expand the theory"}


def value_of(finding: str, **flags) -> dict:
    """Value(D) > 0 iff at least one of the four flags holds. Unknown
    flags are refused, not silently counted."""
    unknown = sorted(k for k in flags if k not in VALUE_FLAGS)
    if unknown:
        return {"finding": finding, "value_positive": None,
                "reason": "E_UNKNOWN_VALUE_FLAG", "unknown": unknown}
    hits = sorted(k for k in VALUE_FLAGS if flags.get(k))
    positive = bool(hits)
    return {"finding": finding, "value_positive": positive,
            "grounds": hits,
            "destination": "architecture" if positive
                           else "history_notebook",
            "law": "everything else goes into the history notebook, "
                   "not the architecture"}


def information_gain_gate(corpus: str, expected_ig: float,
                         epsilon: float, sampled: bool) -> dict:
    """The scan pipeline's gate: SOURCE FREEZE -> STRUCTURAL SAMPLE ->
    DISCRIMINATE -> {deep extraction if IG > eps, STOP otherwise}.

    Scanning old data to maximize DISCRIMINATION, not accumulation. A
    corpus does not earn a swarm by existing; it earns one by being
    expected to separate surviving hypotheses. Deep extraction before
    the structural sample is refused — that is accumulation wearing a
    protocol."""
    if not sampled:
        return {"corpus": corpus, "deep_extraction": False,
                "reason": "E_SAMPLE_BEFORE_EXTRACTION",
                "law": "structural sample precedes deep extraction"}
    if expected_ig <= epsilon:
        return {"corpus": corpus, "deep_extraction": False,
                "verdict": "STOP", "expected_IG": expected_ig,
                "epsilon": epsilon,
                "law": "a corpus that separates nothing earns no "
                       "swarm"}
    return {"corpus": corpus, "deep_extraction": True,
            "verdict": "EXTRACT", "expected_IG": expected_ig}


def coder_common_mode(n_corpora: int, n_coders: int,
                      blind: bool) -> dict:
    """The Mesmerism finding applied to the corpus matrix: N corpora
    coded by ONE instrument share a common mode. Distinct sources do
    not buy independence when the measuring apparatus is single —
    N_effective on the measurement is the number of independent
    CODERS, not the number of corpora."""
    effective = n_coders if blind else 1
    return {"n_corpora": n_corpora, "n_coders": n_coders,
            "blind": blind,
            "N_effective_on_measurement": effective,
            "cross_cell_comparison_licensed": blind and n_coders >= 2,
            "reason": None if (blind and n_coders >= 2)
                      else "E_CODER_COMMON_MODE",
            "law": "fifteen corpora through one unblinded coder is "
                   "one measurement repeated fifteen times"}


def qc_thread() -> dict:
    """Hamilton -> quality control, one continuous thread; and the
    NIST-framed distinction the gate already lives by."""
    return {"order": CORPUS_ORDER,
            "next_after_hamilton": CORPUS_ORDER[1],
            "thread": ("precision artifact", "precision process",
                       "statistical admission",
                       "risk-calibrated verifier"),
            "crosswalk": QC_CROSSWALK,
            "law": "admission decision != world-model estimation; a "
                   "gate need not estimate trustworthiness to decide "
                   "the witness is insufficient"}
