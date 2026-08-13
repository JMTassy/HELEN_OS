r"""Epistemic Lattice — Generable > Produced > Survived > Observed.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The HAL ruling on the design-memory lane, encoded as the smallest
diff with the largest epistemic return.

Corpus identity, corrected by the operator: ATF = AMERICAN TYPE
FOUNDERS (the 1900 Desk Book of Type Specimens, Borders, Ornaments,
Brass Rules and Cuts) — a printing-specimen / machinery / supplies
catalogue, NOT the Bureau of Alcohol, Tobacco, Firearms and
Explosives. It is therefore a PROOF + possibility-space corpus, not
an AUTHORITY/jurisdiction corpus. Its falsifier is the illegal
promotion of catalogued availability into historical fact:

    CataloguedPrimitive(g)  does not entail  HistoricallyUsed(g)

which is exactly the Generable -> Produced arrow below (a catalogued
type is GENERABLE/available; a used type is PRODUCED). The right
question the corpus poses: can a system reconstruct a possibility
space without laundering possibility into historical fact? The old law (Generable is not
HistoricallyObserved, possibility_space.py) collapses three distinct
losses into one. The corrected chain:

    (Sigma, R, Theta, C) --C_t--> GENERABLE   (the compiler)
                          --S_t--> PRODUCED   (cultural/economic
                                               selection)
                          --D_t--> SURVIVED   (survival/destruction)
                          --A_t--> OBSERVED   (archive/digitization
                                               sampling)

Each arrow is a SELECTION MECHANISM, and each inclusion holds for the
historical universe while HELEN only ever holds incomplete ESTIMATES
of these sets. An archive stores surviving outputs; a governed
generative archive reconstructs the bounded possibility space that
produced them — without confusing possibility, production, survival,
observation, or provenance.

The five illegal inferences, made executable failures:

    not Observed(x)  does not entail  not Survived(x)
    not Survived(x)  does not entail  not Produced(x)
    not Produced(x)  does not entail  not Generable(x)
    Generable(x)     does not entail  Produced(x)
    VisualSimilarity(x,y) does not entail SharedGenerator(x,y)

Absence from a level is a RESEARCH SIGNAL that names its candidate
causes (distribution, price, equipment incompatibility, geography,
survival bias, collection bias, digitization bias) — never, by
itself, evidence of cultural rejection.

Generator/instantiation typing (the design-history reading of
E_GLYPH_TRAP): G is a generator specification, theta instantiation
parameters, g = Instantiate(G, theta). Two impressions may share a
generator lineage without being identical tokens, and shared
generator is a PROVENANCE relation, never a similarity judgment.

Boundary kept hard: the printing-catalogue architecture mirroring
HELEN's (Primitive -> Transformation -> Impression vs Candidate ->
Governed transformation -> Admitted state) is an architectural
analogy, not evidence of anticipation.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

LATTICE = ("GENERABLE", "PRODUCED", "SURVIVED", "OBSERVED")

SELECTION_OPERATORS = {
    "C_t": "compiler/affordance operator (what could be made)",
    "S_t": "cultural/economic selection (what was made)",
    "D_t": "survival/destruction process (what lasted)",
    "A_t": "archive/digitization sampling (what we hold)",
}

ABSENCE_CANDIDATE_CAUSES = (
    "cultural_rejection", "distribution", "price",
    "equipment_incompatibility", "geography", "survival_bias",
    "collection_bias", "digitization_bias",
)

ILLEGAL_INFERENCES = (
    ("not_observed", "not_survived"),
    ("not_survived", "not_produced"),
    ("not_produced", "not_generable"),
    ("generable", "produced"),
    ("visual_similarity", "shared_generator"),
    ("catalogued_primitive", "historically_used"),  # ATF: same as
                                                     # generable->produced
)


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def lattice_holds(estimates: dict) -> dict:
    """Check the inclusion chain on HELEN's ESTIMATES, stating the
    caveat: the true inclusions live in the historical universe;
    estimate violations are data errors, not history."""
    sets = [frozenset(estimates.get(level, ())) for level in LATTICE]
    violations = [f"{LATTICE[i+1]} not within {LATTICE[i]}"
                  for i in range(len(sets) - 1)
                  if not sets[i + 1] <= sets[i]]
    return {"holds_on_estimates": not violations,
            "violations": violations,
            "caveat": "inclusions apply to the historical universe; "
                      "HELEN holds incomplete estimates of every "
                      "level"}


def infer(premise: str, conclusion: str) -> dict:
    """The gate on absence reasoning. Every inference in
    ILLEGAL_INFERENCES is refused by name."""
    if (premise, conclusion) in ILLEGAL_INFERENCES:
        return {"premise": premise, "conclusion": conclusion,
                "licensed": False,
                "reason": "E_ILLEGAL_ABSENCE_INFERENCE",
                "law": "each arrow of the lattice is a selection "
                       "mechanism; absence upstream is never proven "
                       "by absence downstream"}
    return {"premise": premise, "conclusion": conclusion,
            "licensed": None,
            "note": "not one of the five named illegal forms; judge "
                    "on its own evidence"}


def absence_signal(x: str, absent_from: str) -> dict:
    """x is absent from a lattice level: a research signal that
    NAMES its candidate causes, never a rejection verdict."""
    if absent_from not in LATTICE:
        raise ValueError("E_UNKNOWN_LATTICE_LEVEL")
    return {"x": x, "absent_from": absent_from,
            "verdict": "RESEARCH_SIGNAL",
            "is_evidence_of_rejection": False,
            "candidate_causes": ABSENCE_CANDIDATE_CAUSES,
            "law": "absence from the surviving archive is not "
                   "negative historical evidence; it localizes "
                   "where information was lost"}


# ── generator / instantiation: provenance, not similarity ──────────────

def instantiate(generator: str, theta: dict) -> dict:
    return {"generator": generator, "theta": dict(theta),
            "token_id": f"{generator}::{canon(theta)}"}


def shared_generator(x: dict, y: dict) -> dict:
    """A provenance relation: same generator lineage, possibly
    different tokens."""
    same = x["generator"] == y["generator"]
    return {"shared_generator": same,
            "identical_tokens": same and x["token_id"] == y["token_id"],
            "basis": "PROVENANCE"}


def similarity_claim(x_looks_like_y: bool) -> dict:
    """VisualSimilarity(x,y) does not entail SharedGenerator(x,y) —
    E_GLYPH_TRAP, in its design-history form."""
    return {"visual_similarity": x_looks_like_y,
            "shared_generator_established": False,
            "reason": "E_GLYPH_TRAP",
            "law": "shared generator is a provenance relation, never "
                   "a similarity judgment"}


def analogy_boundary() -> dict:
    """The hard boundary, kept: mirroring is not anticipation."""
    return {"analogy": "Primitive->Transformation->Impression mirrors "
                       "Candidate->GovernedTransformation->"
                       "AdmittedState",
            "is_evidence_of_anticipation": False,
            "law": "an architectural analogy is not filiation; "
                   "similarity is not filiation, convergence is not "
                   "proof"}
