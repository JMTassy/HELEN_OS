"""Falsifiers for the design-memory grammar, plus a REAL chiddush run
against operators WITNESSED IN-FRAME.

Frame note: five ATF Desk Book border specimen pages were delivered
directly into this frame (not fetched — the proxy blocks egress). So the
operators below are witnessed-in-frame observations, cited to the
specimen headers/numbers actually visible, not hypotheses about a corpus
I cannot read. The bibliographic metadata (1902, 1,168 pages) remains
HYPOTHESIS; the operator evidence is OBSERVED.

IP-safe (per repo rule): the corpus yields ABSTRACT operators (fill,
scale, repeat, tile-enclose, corner-resolve). No specimen border is
reproduced; chiddush recombines operators into an ORIGINAL composition —
"constrained recombination rather than stylistic imitation."
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import design_memory as dm
from design_memory import (
    AVAILABLE,
    UNREACHABLE,
    Composition,
    Corpus,
    DesignMemory,
    Moodboard,
    Operator,
    Primitive,
    RagIndex,
    apply_transform,
    chiddush,
    chiddush_score,
    find_similar,
    recover_grammar,
    shared_lineage,
)


# ═══ witnessed-in-frame corpus: operators cited to delivered specimens ══
# The flagship witness is the OPEN/TINT pairing: the same motif printed
# both ways at identical size and price is `fill` caught as an operator.

W_FILL = Operator("fill", (("mode", "tint"),),
                  source_ref="ATF border page: '18 POINT No 3 OPEN' vs "
                             "'18 POINT No 3 TINT' — same motif, same size")
W_SCALE = Operator("scale", (("pt", 24),),
                   source_ref="ATF: same fleur motif at 18/24 POINT, paired")
W_REPEAT = Operator("repeat", (("axis", "linear"),),
                    source_ref="ATF: every border is a linear motif repeat")
W_TILE = Operator("tile_enclose", (("shape", "square"),),
                  source_ref="ATF 'No 2405' starburst enclosed in square tile")
W_CORNER = Operator("corner_resolve", (("style", "L_piece"),),
                    source_ref="ATF: each border ships a matching L corner piece")

ATF_CORPUS = Corpus(
    corpus_id="ATF_border_specimens_in_frame",
    availability=AVAILABLE,
    operators=frozenset({"fill", "scale", "repeat", "tile_enclose",
                         "corner_resolve"}),
    primitives=frozenset({"fleur", "quatrefoil", "leaf_sprig", "disc",
                          "chevron", "interlace", "daisy", "teardrop"}))


# ── law 1: WITNESSED OPERATOR — an uncited operator is invention ────────

def test_operator_without_source_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNWITNESSED_OPERATOR"):
        Operator("fill", (("mode", "tint"),), source_ref="")


def test_witnessed_operator_constructs_and_carries_its_source():
    assert W_FILL.source_ref.startswith("ATF border page")
    t = apply_transform(Primitive("p1", "fleur"), W_FILL)
    assert t.lineage() == ("p1", "fill", W_FILL.source_ref)


# ── law 2: LINEAGE CLOSURE — chiddush recombines, never invents operators ─

def _original_border():
    """An ORIGINAL composition: fleur primitive, tinted, scaled, repeated,
    corner-resolved. Every operator is witnessed in ATF_CORPUS. Novelty is
    in the COMBINATION, not in any new operator."""
    fleur = Primitive("new-fleur-variant", "fleur")
    return Composition(
        "helen-receipt-border-v0",
        parts=(apply_transform(fleur, W_FILL),
               apply_transform(fleur, W_SCALE),
               apply_transform(fleur, W_REPEAT),
               apply_transform(fleur, W_CORNER)),
        layout="rectangular_frame", spacing="tight", color="mono",
        ornament="corner_L")


def test_chiddush_admits_a_lineage_closed_original():
    r = chiddush(ATF_CORPUS, _original_border())
    assert r["verdict"] == "CANDIDATE_PROPOSED"
    assert r["artifact"].lineage_closed is True
    assert r["artifact"].novelty_source == "recombination"
    assert r["lineage"]                      # non-empty, every part traced
    assert "A=0" in r["note"]                # candidate only, provenance kept


def test_chiddush_rejects_an_operator_outside_the_1902_corpus():
    """The Crystal Palace law made concrete: a 1902 letterpress corpus has
    fill/scale/repeat/tile — but NOT gradient-mesh. A chiddush that
    smuggles a modern operator the archive never had is UNSUPPORTED
    INVENTION, refused — not scored low. The archive's historical boundary
    IS the constraint."""
    anachronism = Operator("gradient_mesh", (("stops", 8),),
                           source_ref="modern vector tool, NOT in ATF corpus")
    bad = Composition("smuggled", parts=(
        apply_transform(Primitive("p", "fleur"), W_FILL),
        apply_transform(Primitive("p", "fleur"), anachronism)))
    r = chiddush(ATF_CORPUS, bad)
    assert r["verdict"] == "REJECT"
    assert r["reason"] == "E_UNSUPPORTED_INVENTION"
    assert r["operators_outside_K"] == ["gradient_mesh"]


# ── law 3: RECOVER != PROOF — recovered grammar is abductive ────────────

def test_recovered_grammar_is_hypothesis_grade():
    g = recover_grammar(ATF_CORPUS, family=("No1234", "No2405"))
    assert g.status == "HYPOTHESIS"           # "could have produced", never proof
    assert g.operators == ATF_CORPUS.operators
    assert "abductive" in g.basis


# ── law 4: UNREACHABLE => UNKNOWN — no read, no grammar ─────────────────

def test_unreachable_corpus_yields_unknown_never_fabricated_grammar():
    """This frame's actual state for the 1,168 full pages: unreachable.
    Recovery and chiddush must return UNKNOWN, never invent a grammar."""
    dark = Corpus("full_deskbook_1168pp", UNREACHABLE)
    assert recover_grammar(dark, ())["status"] if isinstance(
        recover_grammar(dark, ()), dict) else recover_grammar(dark, ()).status == "UNKNOWN"
    g = recover_grammar(dark, ())
    assert g.status == "UNKNOWN" and g.operators == frozenset()
    assert chiddush(dark, _original_border())["verdict"] == "UNKNOWN"
    assert chiddush(dark, _original_border())["reason"] == "E_CORPUS_UNREACHABLE"


# ── law 5: RESEMBLANCE != LINEAGE — GLYPH_TRAP for artifacts ────────────

def test_visual_resemblance_is_not_shared_derivation():
    """Two borders may look alike with DISJOINT operator provenance. Only
    overlapping operator lineage is shared derivation; resemblance mints a
    candidate, never a claim of common origin."""
    p = Primitive("m", "fleur")
    a = Composition("a", parts=(apply_transform(p, W_FILL),))
    # b uses a DIFFERENTLY-sourced fill operator — looks identical, other lineage
    other_fill = Operator("fill", (("mode", "tint"),),
                          source_ref="a DIFFERENT specimen entirely")
    b = Composition("b", parts=(apply_transform(p, other_fill),))
    s = shared_lineage(a, b)
    assert s["shared_derivation"] is False    # same look, disjoint provenance
    assert s["overlap"] == []
    # identical lineage DOES count as shared derivation (positive control)
    assert shared_lineage(a, a)["shared_derivation"] is True


# ── the three operations never collapse ─────────────────────────────────

def test_retrieval_recovers_no_operators():
    r = find_similar(ATF_CORPUS, "star border", matches=("No2405", "No7"))
    assert r.recovers_operators is False      # 'looks like', nothing more
    assert not hasattr(r, "operators")


def test_design_memory_is_a_four_tuple_distinct_from_moodboard_and_rag():
    dmem = DesignMemory(source="ATF", grammar=ATF_CORPUS.operators,
                        lineage=(("fleur", "fill"),), generator="chiddush")
    assert dmem.tuple_arity() == 4
    assert Moodboard("ATF").tuple_arity() == 1        # source only
    assert RagIndex("ATF", "cosine").tuple_arity() == 2  # source + retrieval
    # the distinction is structural: only DesignMemory carries grammar+generator
    assert not hasattr(Moodboard("ATF"), "grammar")
    assert not hasattr(RagIndex("ATF", "x"), "generator")


# ── the objective: laundering costs more than fidelity earns ────────────

def test_unsupported_invention_penalized_harder_than_coherence_rewarded():
    # grounded novelty beats pure imitation AND beats ungrounded invention
    grounded_novel = chiddush_score(novelty=0.8, coherence=0.9, unsupported=0.0)
    pure_imitation = chiddush_score(novelty=0.0, coherence=1.0, unsupported=0.0)
    ungrounded = chiddush_score(novelty=0.9, coherence=0.9, unsupported=0.6)
    assert grounded_novel > pure_imitation    # chiddush > imitation
    assert grounded_novel > ungrounded        # groundedness dominates
    # mu > lambda: one unit of laundering costs more than one unit of
    # coherence earns
    assert chiddush_score(0, 1, 1) < chiddush_score(0, 0, 0)


def test_deterministic():
    a = dm.canon(chiddush(ATF_CORPUS, _original_border())["lineage"])
    b = dm.canon(chiddush(ATF_CORPUS, _original_border())["lineage"])
    assert a == b
