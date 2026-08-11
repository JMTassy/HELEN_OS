"""The Temporal Chiddush Ladder — a historical benchmark for the
adjacent possible.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    1772 -> <=1850 -> 1851 -> 1862 -> 1876 -> 1893

Six corpora, six grammar layers. The elegant experiment runs BACKWARD
from Crystal Palace: freeze Adj(K_1850) from the Repertory of Patent
Inventions, hash it, and only then open the 1851 holdout.

    Precision = predicted motifs witnessed in 1851 / predicted motifs
    Recall    = 1851 motifs reconstructible from K_1850 / 1851 motifs

THE SEAT LAW, first-class: the predicting seat must never have read
the holdout. THIS seat has — atlas batches 1 and 2 were built in this
conversation — so this_seat_attestation() says so, permanently, and
score() refuses any freeze carrying a contaminated attestation
(E_SEAT_CONTAMINATED). This module is the referee and the instrument;
it is structurally incapable of being the predictor from here.

The negative control: run the same protocol from the 1772
Encyclopédie. If R(1772->1851) ~ R(1850->1851) and both are high, the
motif grammar is too generic to detect anything historically local —
the method indicts itself (E_GRAMMAR_TOO_GENERIC). Only
R(1850->1851) >> R(1772->1851) evidences genuine temporally-local
possibility detection.

Corpus reachability from this seat, probed 2026-08-12 (all CONNECT
403 through the proxy): encyclopedie.uchicago.edu blocked,
babel.hathitrust.org blocked, quod.lib.umich.edu blocked. Every rung
boots UNREACHABLE; frames enter by relay, as they did for 1851.

Absence law for deltas: a motif not witnessed in a later corpus is
NOT extinct — catalogues are samples, not censuses. motif_delta
reports 'not_witnessed_later', never 'removed'.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crystal_palace import UNREACHABLE, canon_hash  # noqa: E402

LADDER = (
    {"corpus_id": "encyclopedie_1772", "year": 1772,
     "grammar_layer": "human procedural grammar (H -> Process)",
     "role": "deep-time negative control",
     "availability": UNREACHABLE},
    {"corpus_id": "repertory_patents_le1850", "year": 1850,
     "grammar_layer": "invention/proposal grammar (Process -> Candidate)",
     "role": "blind precursor corpus — run FIRST",
     "availability": UNREACHABLE},
    {"corpus_id": "crystal_palace_1851", "year": 1851,
     "grammar_layer": "demonstrated capability grammar "
                      "(Candidate -> Demonstrated Machine)",
     "role": "HOLDOUT — already read in this seat",
     "availability": UNREACHABLE},
    {"corpus_id": "international_exhibition_1862", "year": 1862,
     "grammar_layer": "short-horizon mutation (Machine -> Improved "
                      "Composition)",
     "role": "forward prediction target",
     "availability": UNREACHABLE},
    {"corpus_id": "centennial_1876", "year": 1876,
     "grammar_layer": "industrial systems grammar (Machine_i -> System)",
     "role": "compositional/network stress test — target law: "
             "local admissibility != network admissibility",
     "availability": UNREACHABLE},
    {"corpus_id": "columbian_1893", "year": 1893,
     "grammar_layer": "network grammar (System -> Network)",
     "role": "electricity/communication horizon",
     "availability": UNREACHABLE},
)

RUN_ORDER = ("repertory_patents_le1850", "crystal_palace_1851",
             "encyclopedie_1772", "international_exhibition_1862",
             "centennial_1876")


def this_seat_attestation() -> dict:
    """The honest, permanent fact about THIS seat. Not configurable —
    an attestation you can edit is a costume."""
    return {"seat": "goblin-warren-builder-2026-08",
            "holdout_accessed": True,
            "basis": "crystal_palace atlas batches 1-2 built and read "
                     "in this conversation"}


# ── the backtest protocol: a state machine with one legal order ────────

@dataclass(frozen=True)
class Backtest:
    backtest_id: str
    precursor: str                    # corpus_id, e.g. repertory
    holdout: str                      # corpus_id, e.g. crystal palace 1851


def freeze_predictions(bt: Backtest, predictions: tuple,
                       attestation: dict) -> dict:
    """Hash Adj(K_precursor) with the predicting seat's attestation
    riding the receipt. A contaminated seat freezes — the receipt just
    says so, forever, and scoring will refuse it."""
    if not predictions:
        return {"verdict": "REFUSED", "reason": "E_EMPTY_PREDICTION_SET"}
    return {"state": "PREDICTIONS_FROZEN",
            "backtest_id": bt.backtest_id,
            "prediction_hash": canon_hash(sorted(predictions)),
            "prediction_count": len(predictions),
            "seat": attestation.get("seat", "UNDECLARED"),
            "seat_contaminated": bool(attestation.get("holdout_accessed",
                                                      True)),
            "holdout": bt.holdout}


def open_holdout(freeze_receipt: dict | None) -> dict:
    """The holdout opens ONLY over a freeze. Opening it first is the
    kill condition of the whole experiment."""
    if not freeze_receipt or freeze_receipt.get("state") != \
            "PREDICTIONS_FROZEN":
        return {"verdict": "REFUSED", "reason": "E_TARGET_BEFORE_FREEZE",
                "law": "no post-target prediction is a prediction"}
    return {"state": "HOLDOUT_OPEN",
            "over_freeze": freeze_receipt["prediction_hash"]}


def score(freeze_receipt: dict, opened: dict, predictions: tuple,
          witnessed_holdout_motifs: tuple) -> dict:
    """The referee. Refuses contaminated seats and out-of-order opens;
    otherwise computes precision/recall with denominators shown."""
    if freeze_receipt.get("seat_contaminated"):
        return {"verdict": "REFUSED", "reason": "E_SEAT_CONTAMINATED",
                "seat": freeze_receipt.get("seat"),
                "law": "a seat that has read the holdout cannot predict "
                       "it; this seat is disqualified by its own "
                       "attestation"}
    if opened.get("state") != "HOLDOUT_OPEN" or \
            opened.get("over_freeze") != freeze_receipt.get(
                "prediction_hash"):
        return {"verdict": "REFUSED", "reason": "E_SCORING_WITHOUT_ORDER"}
    if canon_hash(sorted(predictions)) != freeze_receipt["prediction_hash"]:
        return {"verdict": "REFUSED", "reason": "E_PREDICTIONS_SWAPPED"}
    p, w = frozenset(predictions), frozenset(witnessed_holdout_motifs)
    hits = p & w
    return {"verdict": "SCORED",
            "precision": len(hits) / len(p),
            "recall": len(hits) / len(w) if w else 0.0,
            "hits": sorted(hits),
            "predicted": len(p), "witnessed": len(w)}


# ── the negative control: generality indicts the method ────────────────

def generality_check(r_deep: float, r_near: float,
                     high: float = 0.6, margin: float = 0.2) -> dict:
    """Compare R(1772->1851) against R(1850->1851). If deep time
    predicts the holdout as well as near time, the grammar is
    detecting universals, not history."""
    if r_deep >= high and r_near >= high and (r_near - r_deep) < margin:
        return {"verdict": "E_GRAMMAR_TOO_GENERIC",
                "note": "the abstraction level predicts everything, "
                        "therefore evidences nothing local"}
    if r_near - r_deep >= margin:
        return {"verdict": "HISTORICALLY_LOCAL_SIGNAL",
                "gap": r_near - r_deep}
    return {"verdict": "METHOD_INCONCLUSIVE",
            "r_deep": r_deep, "r_near": r_near}


# ── motif mutation velocity, with the absence law ───────────────────────

def motif_delta(earlier: frozenset, later: frozenset) -> dict:
    """Delta M between adjacent rungs. A motif absent from the later
    catalogue is NOT extinct — a catalogue is a sample, not a census.
    The vocabulary of this function contains no 'removed'."""
    return {"new_in_later": sorted(later - earlier),
            "retained": sorted(earlier & later),
            "not_witnessed_later": sorted(earlier - later),
            "law": "not-catalogued is not extinct — a catalogue is a "
                   "sample, not a census; O_t is a proper subset of "
                   "P_t at every rung"}
