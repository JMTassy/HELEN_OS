"""MATERIAL-WITNESS BOUNDARY — the resource a reading's status consumes. 🔵 OBSERVED · authority=false.

Named by the Codex Sinaiticus/Bezae chiddush and sharpened by Scrivener's own 1864 practice:
he recorded every physical stroke he could trace, but refused to restore letters merely because
they could be *conjectured* — only exceptional bracketed cases. That is a clean historical
implementation of one law:

    RecoverableByInference ≠ MateriallyWitnessed        →  D(r) cannot substitute for M(r)

A reading's epistemic status follows the WARRANT ACTUALLY CONSUMED, not the plausibility of the
resulting reading. Four resources, four states:

  M(r) material attestation  · T(r) recoverable physical trace · D(r) replayable derivation
    WITNESSED             M(r) ≥ 1
    WITNESSED_CORRECTION  M(r) ≥ 1 and the alteration is itself a visible correction (a corrector's
                          ink is material evidence — never a conjecture; it just adds a temporal layer)
    RECONSTRUCTED_TRACE   M(r) = 0 but T(r): partial trace recoverable (uncertain, preserve — NOT conjecture)
    CONJECTURE            M(r) = 0, T(r) = 0, D(r) > 0 (editor supplies a plausible reading)
    UNSUPPORTED           M(r) = 0, T(r) = 0, D(r) = 0

Hard invariants:
  1. D(r) ⊬ WITNESSED — no amount of derivational persuasiveness promotes to a material state.
  2. Correction ⊬ Conjecture — a visible correction is material; it changes the temporal layer, not the type.
  3. Correctness discovered later ⊬ a retroactive witness — class changes only when MATERIAL/TRACE changes,
     never because the conjecture was argued more strongly or later proved right.
  4. Interpolated / SingularReading ⊬ CONJECTURE and ⊬ N_epi=0 — a reading physically in the manuscript is
     WITNESSED even if singular or an interpolation; that is a genealogical claim about an EARLIER state,
     scored separately by epistemic_roots (N_epi ⊬ warrant), not by this classifier.
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass

INTERNAL_CRITERIA = frozenset({
    "explains_variants", "lectio_difficilior", "intrinsic_fit", "coherence",
})

WITNESSED = "WITNESSED"
WITNESSED_CORRECTION = "WITNESSED_CORRECTION"
RECONSTRUCTED_TRACE = "RECONSTRUCTED_TRACE"
CONJECTURE = "CONJECTURE"
UNSUPPORTED = "UNSUPPORTED"

_MATERIAL_STATES = frozenset({WITNESSED, WITNESSED_CORRECTION})


@dataclass(frozen=True)
class Reading:
    material: int = 0            # M(r): count of material attestations physically present
    trace: bool = False         # T(r): partial physical trace recoverable from an obscured/erased locus
    derivation: tuple = ()      # D(r): editor's derivational/coherence criteria
    is_correction: bool = False # the material alteration is a visible scribal correction (temporal layer)
    corrects: str = ""          # (optional) the prior first-hand reading this correction supersedes


def classify(r: Reading) -> str:
    """Type by the warrant actually consumed. Material first; a correction is material; a trace is its
    own uncertain state; only with NO material/trace does derivation produce (at most) a conjecture."""
    if r.material >= 1:
        return WITNESSED_CORRECTION if r.is_correction else WITNESSED
    if r.trace:
        return RECONSTRUCTED_TRACE
    return CONJECTURE if (set(r.derivation) & INTERNAL_CRITERIA) else UNSUPPORTED


def conjecture_grade(r: Reading):
    """MOTIVATED iff a conjecture carries transcriptional probability (explains_variants); else UNMOTIVATED;
    None if not a conjecture."""
    if classify(r) != CONJECTURE:
        return None
    return "MOTIVATED" if "explains_variants" in (set(r.derivation) & INTERNAL_CRITERIA) else "UNMOTIVATED"


def admissible_as_conjecture(r: Reading) -> bool:
    return conjecture_grade(r) == "MOTIVATED"


def may_serve_as_root(r: Reading) -> bool:
    """Only a materially-witnessed reading may be cited as an independent root for another claim.
    A trace is uncertain; a conjecture is not evidence. Neither may inflate another claim's N_epi."""
    return classify(r) in _MATERIAL_STATES


def witness_states(r: Reading):
    """Temporal layers materially present at a locus: a corrected reading witnesses BOTH the first hand
    (W0, superseded) and the correction (W1). An artifact carries its own state-transition history."""
    if classify(r) == WITNESSED_CORRECTION:
        return ("W0:" + (r.corrects or "original_hand"), "W1:correction")
    if classify(r) in (WITNESSED, RECONSTRUCTED_TRACE):
        return ("W0:original_hand",)
    return ()
