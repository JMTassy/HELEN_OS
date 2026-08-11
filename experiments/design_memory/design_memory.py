"""Design memory — historical artifacts as (primitive + operator + lineage).

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Operator relay chiddush (ATF Desk Book 1902), sharpened. Bibliographic
claims about the source are UNVERIFIED from this frame (proxy blocks
egress) and held at HYPOTHESIS; the LAWS below are corpus-independent —
they stand on type theory, not on any page count.

The jump the relay names: a specimen book gives not just glyphs but
OPERATORS. The interesting object is not "what glyph is this" but

    G' = T(G; theta)          a witnessed transformation of a primitive

and an artifact is a COMPOSITION of transformed primitives:

    A = C( T1(G1), ..., Tn(Gn) ; L, S, C, O )

Three operations that must NEVER collapse into one another:

    RETRIEVAL         find_similar(q) -> similar artifacts. Recovers NO
                      operators. "looks like this."

    OPERATOR-RECOVERY recover_grammar(family) -> operators that COULD have
                      produced the family. Abductive, D- style: it is
                      HYPOTHESIS-grade, never proof. "what could have made
                      this."

    CHIDDUSH          apply witnessed operators to a NEW problem, with
                      provenance preserved. Constrained RECOMBINATION, not
                      stylistic imitation.

Laws (falsifier-backed):

  WITNESSED OPERATOR    A transformation claiming to be historical must
                        cite a source. An operator with no source_ref is
                        invention wearing a period costume -> rejected.
                        (Same grounding law as the goblin grammar: a claim
                        that cannot cite is HYPOTHESIS, not OBSERVATION.)

  LINEAGE CLOSURE       Chiddush novelty comes from RECOMBINATION and
                        PARAMETERS, never from new operators. Every
                        operator in a generated artifact must trace to the
                        admitted corpus K. An operator outside K is
                        E_UNSUPPORTED_INVENTION, not a low score.

  RECOVER != PROOF      A recovered grammar is abductive: it survives as
                        HYPOTHESIS. "could have produced" never upgrades to
                        "did produce" without a witness.

  UNREACHABLE => UNKNOWN  You cannot recover a grammar from a corpus you
                        cannot read. When the source is unreachable (this
                        frame's actual state re: the 1,168 pages), recovery
                        and chiddush return UNKNOWN, never a fabricated
                        grammar.

  RESEMBLANCE != LINEAGE  Two artifacts may look alike with DISJOINT
                        operator provenance. Visual similarity mints a
                        candidate, never shared derivation (GLYPH_TRAP).

    DESIGN MEMORY = (source, grammar, lineage, generator)
    != moodboard (source only)  != RAG (source + retrieval)

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, replace

AVAILABLE = "AVAILABLE"
UNREACHABLE = "UNREACHABLE"


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class Primitive:
    """A primitive typographic/visual form. Identity, not style."""
    prim_id: str
    kind: str                         # glyph | border | rule | ornament ...


@dataclass(frozen=True)
class Operator:
    """T — a transformation. To claim historical grounding it MUST cite a
    source; an uncited operator is invention, not transformation."""
    op_id: str                        # scale | weight | outline | shade | ...
    params: tuple = ()                # (theta) as sorted (k, v) pairs
    source_ref: str = ""              # the historical witness (required)

    def __post_init__(self):
        if not self.op_id:
            raise ValueError("E_UNTYPED_OPERATOR")
        if not self.source_ref:
            raise ValueError("E_UNWITNESSED_OPERATOR")   # grounding law


@dataclass(frozen=True)
class Transformed:
    """G' = T(G; theta), carrying its lineage: which primitive, which
    operator, and the operator's own source."""
    primitive: Primitive
    operator: Operator

    def lineage(self) -> tuple:
        return (self.primitive.prim_id, self.operator.op_id,
                self.operator.source_ref)


def apply_transform(prim: Primitive, op: Operator) -> Transformed:
    return Transformed(primitive=prim, operator=op)


@dataclass(frozen=True)
class Composition:
    """A = C(transformed...; L, S, C, O)."""
    artifact_id: str
    parts: tuple                      # Transformed[]
    layout: str = ""
    spacing: str = ""
    color: str = ""
    ornament: str = ""

    def operators_used(self) -> frozenset:
        return frozenset(t.operator.op_id for t in self.parts)

    def lineage(self) -> tuple:
        return tuple(sorted(t.lineage() for t in self.parts))


# ── the admitted corpus K ────────────────────────────────────────────────

@dataclass(frozen=True)
class Corpus:
    """K — the admitted historical corpus. Availability is first-class:
    an unreachable corpus yields UNKNOWN, never a fabricated grammar."""
    corpus_id: str
    availability: str                 # AVAILABLE | UNREACHABLE
    operators: frozenset = field(default_factory=frozenset)   # op_ids, if readable
    primitives: frozenset = field(default_factory=frozenset)


# ── three operations, three distinct return types ───────────────────────

@dataclass(frozen=True)
class SimilarityResult:
    """RETRIEVAL output. Carries NO operators — 'looks like', nothing more."""
    query: str
    matches: tuple
    recovers_operators: bool = False   # structurally always False


def find_similar(corpus: Corpus, query: str, matches: tuple) -> SimilarityResult:
    return SimilarityResult(query=query, matches=tuple(matches))


@dataclass(frozen=True)
class RecoveredGrammar:
    """OPERATOR-RECOVERY output. Abductive: HYPOTHESIS-grade, never proof."""
    corpus_id: str
    operators: frozenset
    status: str                        # HYPOTHESIS | UNKNOWN
    basis: str = "abductive: operators that COULD have produced the family"


def recover_grammar(corpus: Corpus, family: tuple) -> RecoveredGrammar:
    """What operators could have produced this family? Abductive, and
    honest about unreachability: no read, no grammar."""
    if corpus.availability != AVAILABLE:
        return RecoveredGrammar(corpus.corpus_id, frozenset(), "UNKNOWN",
                                basis="corpus unreachable from this frame")
    # in a real recovery these would be inferred; here we surface the
    # corpus's readable operators, explicitly as HYPOTHESIS not proof.
    return RecoveredGrammar(corpus.corpus_id, frozenset(corpus.operators),
                            "HYPOTHESIS")


@dataclass(frozen=True)
class GeneratedArtifact:
    """CHIDDUSH output: a new composition whose every operator traces to K,
    carrying its lineage. Novelty lives in recombination + parameters."""
    composition: Composition
    corpus_id: str
    lineage_closed: bool
    novelty_source: str                # "recombination" | "parameters"


def chiddush(corpus: Corpus, composition: Composition) -> dict:
    """Apply witnessed operators to a new problem. LINEAGE CLOSURE: every
    operator used must be in K. An operator outside K is unsupported
    invention, refused — not scored low."""
    if corpus.availability != AVAILABLE:
        return {"verdict": "UNKNOWN", "reason": "E_CORPUS_UNREACHABLE"}
    used = composition.operators_used()
    outside = sorted(used - corpus.operators)
    if outside:
        return {"verdict": "REJECT", "reason": "E_UNSUPPORTED_INVENTION",
                "operators_outside_K": outside}
    art = GeneratedArtifact(
        composition=composition, corpus_id=corpus.corpus_id,
        lineage_closed=True, novelty_source="recombination")
    return {"verdict": "ADMIT_CANDIDATE", "artifact": art,
            "lineage": composition.lineage(),
            "note": "candidate for the trellis; A=0, provenance preserved"}


# ── the chiddush objective (soft scoring, under the hard closure law) ────

def chiddush_score(novelty: float, coherence: float, unsupported: float,
                   lam: float = 1.0, mu: float = 2.0) -> float:
    """N + lambda*C - mu*D. Unsupported invention is penalized harder than
    coherence is rewarded (mu > lambda) — laundering costs more than
    fidelity earns. This is the anti-narrative-virus law for generation."""
    return novelty + lam * coherence - mu * unsupported


# ── the design-memory 4-tuple, distinct from moodboard and RAG ──────────

@dataclass(frozen=True)
class DesignMemory:
    """(source, grammar, lineage, generator) — a generator that preserves
    provenance, not a moodboard and not RAG-over-images."""
    source: str
    grammar: frozenset                 # operators
    lineage: tuple
    generator: str

    def tuple_arity(self) -> int:
        return 4


@dataclass(frozen=True)
class Moodboard:
    source: str
    def tuple_arity(self) -> int:
        return 1


@dataclass(frozen=True)
class RagIndex:
    source: str
    retrieval: str
    def tuple_arity(self) -> int:
        return 2


# ── resemblance != lineage (GLYPH_TRAP for artifacts) ───────────────────

def shared_lineage(a: Composition, b: Composition) -> dict:
    """Two artifacts may look alike with disjoint operator provenance.
    Visual similarity is a candidate; only overlapping operator lineage is
    shared derivation."""
    la = {t.lineage() for t in a.parts}
    lb = {t.lineage() for t in b.parts}
    overlap = sorted(la & lb)
    return {"shared_derivation": bool(overlap),
            "overlap": overlap,
            "note": "visual resemblance alone would mint only a candidate"}
