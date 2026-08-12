"""Possibility space — the design-memory triple.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Placement note: the original design_memory.py lives on the
claude/design-memory-* branches, OUTSIDE the CLAUDE.md-authorized
surface. Editing it there would repeat the scope violation. This
triple is a CONSTITUTION law — the generation-side twin of T000
(cardinality not assumed) and the ceiling algebra (O_t is a proper
subset of P_t is a scope ceiling on generation) — so it is built here,
in the authorized surface, carrying the design_memory vocabulary
(primitives, operators, corpus, generation).

The triple, from the ATF / possibility-space relay:

  1. O_t (subsetneq) P_t   the OBSERVED corpus is a PROPER subset of
     the POSSIBLE. A design catalogue never exhausts what its grammar
     could generate. Asserting observed = possible is refused unless a
     closure witness proves the grammar is finite and fully realized.

  2. absence != prohibition   an operator/motif ABSENT from the
     observed corpus is UNKNOWN, never FORBIDDEN. Negative evidence is
     witnessed, not assumed: not-catalogued is not not-allowed.

  3. Generable(x) (does not entail) HistoricallyObserved(x)   applying
     witnessed operators to produce a NEW form yields a HYPOTHESIS. It
     was generated; it was not thereby historically observed. Claiming
     otherwise is E_GENERABLE_IS_NOT_OBSERVED — a raise, not a habit.

This is the exact design-memory form of the crystal_palace laws
COMPOSABLE != COMPOSED and possible != conceived != implemented, and
of the maritime EFFECT != AUTHORIZED EFFECT: computation over a
grammar produces candidates, never facts about history.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

GENERATION_STATES = ("HYPOTHESIS", "CANDIDATE_PROPOSED")
ABSENCE_VERDICTS = ("UNKNOWN", "FORBIDDEN")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── 1. O_t (subsetneq) P_t ──────────────────────────────────────────────

@dataclass(frozen=True)
class PossibilitySpace:
    """observed subset of possible, PROPER by default. A construction
    where observed is not a subset of possible is incoherent; one where
    observed == possible needs a closure witness — a catalogue does not
    get to declare itself the whole grammar."""
    observed: frozenset
    possible: frozenset
    closure_witness: str = ""          # proof the grammar is exhausted

    def __post_init__(self):
        if not self.observed <= self.possible:
            raise ValueError("E_OBSERVED_EXCEEDS_POSSIBLE")
        if self.observed == self.possible and not self.closure_witness:
            raise ValueError("E_UNWITNESSED_CLOSURE")

    def is_proper(self) -> bool:
        return self.observed < self.possible

    def unobserved_possible(self) -> frozenset:
        """P_t \\ O_t — generable-but-not-yet-observed. Never empty
        without a closure witness."""
        return self.possible - self.observed


def assert_observed_exhausts_possible(space: PossibilitySpace) -> dict:
    """The forbidden generalization: 'the catalogue shows everything the
    grammar can do'. Refused without a closure witness."""
    if not space.closure_witness:
        return {"verdict": "REFUSED", "reason": "E_CLOSURE_UNWITNESSED",
                "unobserved": sorted(space.unobserved_possible()),
                "law": "O_t is a proper subset of P_t; a catalogue does "
                       "not exhaust its own grammar"}
    return {"verdict": "CLOSURE_WITNESSED", "via": space.closure_witness}


# ── 2. absence != prohibition ───────────────────────────────────────────

def absence_verdict(item: str, observed: frozenset,
                    prohibition_witness: str = "") -> dict:
    """An item not in the observed corpus is UNKNOWN. It becomes
    FORBIDDEN only with an explicit prohibition witness — negative
    evidence is witnessed, not inferred from silence."""
    if item in observed:
        return {"verdict": "PRESENT", "item": item}
    if prohibition_witness:
        return {"verdict": "FORBIDDEN", "item": item,
                "witness": prohibition_witness}
    return {"verdict": "UNKNOWN", "item": item,
            "law": "not-catalogued is not not-allowed; absence is not "
                   "prohibition"}


# ── 3. Generable(x) (does not entail) HistoricallyObserved(x) ──────────

@dataclass(frozen=True)
class Operator:
    """A witnessed design operator (fill, scale, repeat, corner...).
    Must cite where it was observed, or it is invention wearing a
    period costume."""
    op_id: str
    source_ref: str

    def __post_init__(self):
        if not self.source_ref:
            raise ValueError("E_UNWITNESSED_OPERATOR")


@dataclass(frozen=True)
class Generated:
    """The output of applying witnessed operators to primitives. Its
    state is HYPOTHESIS — generation is not observation."""
    form_id: str
    operators_used: tuple              # op_ids, all from the corpus
    state: str = "HYPOTHESIS"


def generate(primitive: str, operators: tuple,
             corpus_operators: frozenset) -> dict:
    """Apply witnessed operators to a primitive. Lineage closure: every
    operator must be in the corpus (absence there is unsupported
    invention, not low score). The result is a HYPOTHESIS."""
    used = tuple(o.op_id for o in operators)
    outside = sorted(set(used) - corpus_operators)
    if outside:
        return {"verdict": "REJECT", "reason": "E_UNSUPPORTED_INVENTION",
                "operators_outside_corpus": outside}
    return {"verdict": "GENERATED",
            "form": Generated(f"gen:{primitive}", used, "HYPOTHESIS"),
            "state": "HYPOTHESIS",
            "law": "generation over a grammar yields a candidate, not a "
                   "historical fact"}


def claim_historically_observed(generated: Generated,
                                historical_witness: str = "") -> dict:
    """The raise, not the habit. A generated form claimed as
    historically observed is refused unless an independent HISTORICAL
    witness (a dated artifact, not the generator) is produced."""
    if generated.state not in GENERATION_STATES:
        return {"verdict": "REFUSED", "reason": "E_UNKNOWN_GENERATION_STATE"}
    if not historical_witness:
        return {"verdict": "REFUSED",
                "reason": "E_GENERABLE_IS_NOT_OBSERVED",
                "form": generated.form_id,
                "law": "Generable(x) does not entail "
                       "HistoricallyObserved(x); the generator is not a "
                       "witness to history"}
    return {"verdict": "OBSERVED_WITH_WITNESS",
            "form": generated.form_id, "witness": historical_witness}


# ── the triple mapped onto the ceiling algebra ──────────────────────────
# possibility space IS a ceiling on generation: a generated form may be
# proposed within P_t but never asserted as an element of the observed
# O_t. This is the design-memory reading of Effect subset of Scope.

TRIPLE_CEILING_MAP = {
    "E_CLOSURE_UNWITNESSED": "SCOPE",          # observed does not fill P_t
    "E_GENERABLE_IS_NOT_OBSERVED": "PROOF",    # generation is not evidence
    "absence_is_UNKNOWN_not_FORBIDDEN": "PROOF",
}
