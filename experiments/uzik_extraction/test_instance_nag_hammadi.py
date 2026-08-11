"""INSTANCE run: PKT-NH-001 — Arthur 1979, 'Feminine Motifs in Eight
Nag Hammadi Documents', operator-supplied.

First real evidence packet through UZIK_DEEP_EXTRACTION_V1. The organe
stays generic; everything corpus-specific lives here as INSTANCE data.

Critical provenance fact encoded honestly: every tractate quotation,
every church-father report, every cited scholar reaches this frame
THROUGH the dissertation. All secondary sources are derived_from
DISS-1979, so the independence clusterer must collapse the entire
packet to lineage weight 1. 'Widely attested' is unmintable from this
packet alone — that refusal is the machine working.

Rights basis: operator-supplied scholarly quotation scope; claims are
typed pointers into the document, not reproductions of it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_memory import (
    Census,
    EvidenceGraph,
    Nutrient,
    absence_verdict,
    atomize,
    canon,
    ingest_packet,
    transition_report,
)

RIGHTS = "operator_supplied_quotation_scope_arthur_1979"


def _packet():
    arts = [{
        "source_id": "DISS-1979",
        "family": "dissertation",
        "locator": "Arthur, R.H., Feminine Motifs in Eight Nag Hammadi Documents, GTU Berkeley 1979",
        "retrieved_at": "2026-08-11",
        "content": "operator-pasted OCR of the full dissertation text",
        "rights_basis": RIGHTS,
    }]
    # Everything else arrives THROUGH the dissertation: derived sources.
    for sid, loc in [
        ("ORIG-WORLD", "NHC II.5 as quoted in DISS-1979"),
        ("HYP-ARCH", "NHC II.4 as quoted in DISS-1979"),
        ("EUGNOSTOS", "NHC III.3/V.1 as quoted in DISS-1979"),
        ("SJC", "NHC III.4/BG 8502.3 as quoted in DISS-1979"),
        ("THUNDER", "NHC VI.2 as quoted in DISS-1979"),
        ("IRENAEUS", "Adversus Haereses as quoted in DISS-1979"),
        ("EPIPHANIUS", "Panarion 39-40 as quoted in DISS-1979"),
        ("HIPPOLYTUS", "Refutatio as quoted in DISS-1979"),
        ("KRAUSE-1964", "Krause, Mullus Festschrift, as cited in DISS-1979"),
        ("YAMAUCHI", "Pre-Christian Gnosticism, as cited in DISS-1979"),
    ]:
        arts.append({"source_id": sid, "family": "quoted_via_dissertation",
                     "locator": loc, "retrieved_at": "2026-08-11",
                     "content": f"content of {sid} as mediated by DISS-1979",
                     "rights_basis": RIGHTS, "derived_from": "DISS-1979"})
    return {"packet_id": "PKT-NH-001", "provided_by": "operator", "artifacts": arts}


@pytest.fixture()
def nh():
    g = EvidenceGraph()
    report = ingest_packet(g, _packet())
    assert len(report["registered"]) == 11 and not report["refused"]
    return g


# The dissertation's own coverage, frozen as census v1: what the 1979
# survey actually swept. Post-1979 scholarship is OUTSIDE every cell.
CENSUS_NH = Census("census-nh-v1-arthur1979", "1979",
                   frozenset({
                       ("term_gnosticism", "nh_corpus", "dissertation_survey", "ORGANIZED"),
                       ("explicit_christianity", "apoc_adam", "dissertation_survey", "ORGANIZED"),
                   }))


# --- M02: the thesis sentence is scissioned before entry ------------------

def test_thesis_sentence_atomized(nh):
    parts = atomize("The Hypostasis of the Archons is a Christianized, "
                    "patriarchalized, and defeminized summary of On the "
                    "Origin of the World.")
    assert len(parts) >= 3   # three properties, three claims — no bundle


# --- M03+M06: dependence direction is earned, resemblance is not ----------

def test_dependence_claim_carries_its_error_evidence(nh):
    # Direction OrigWorld -> HypArch is argued from ASYMMETRIC evidence:
    # inherited misspelling TCOEIN, the ANAEI corruption propagated into
    # an impossible conjunctive, the elliptic CICHANE sentence whose
    # antecedent exists only in the source. Directional evidence is the
    # documentary class; it may mint DERIVED_FROM.
    c1 = nh.add_claim("hyp_arch", "DERIVED_FROM", "orig_world",
                      "pre-350CE", ("DISS-1979", "ORIG-WORLD", "HYP-ARCH"),
                      evidence_class="documentary")
    assert c1.relation == "DERIVED_FROM"
    # But the SAME conclusion from mere parallel-passage resemblance is
    # trapped: resemblance-class evidence cannot mint lineage.
    with pytest.raises(ValueError, match="E_GLYPH_TRAP"):
        nh.add_claim("hyp_arch", "DERIVED_FROM", "orig_world",
                     "pre-350CE", ("DISS-1979",), evidence_class="visual")


def test_isis_parallels_stay_similarity_candidates(nh):
    # The 'I am' form parallels between Thunder and the Isis aretalogies:
    # the dissertation itself concludes shared tradition, no literary
    # connection. The machine can only say what the evidence class allows.
    sim = nh.add_claim("thunder", "VISUAL_SIMILARITY_CANDIDATE",
                       "isis_aretalogies", "pre-300CE",
                       ("DISS-1979", "THUNDER"), evidence_class="visual")
    assert sim.relation == "VISUAL_SIMILARITY_CANDIDATE"
    assert nh.authorship_verdict("thunder", "isis_aretalogies") == \
        "VISUAL_SIMILARITY_CANDIDATE"   # never SAME_TRADITION-as-fact


# --- M04: the whole packet is one lineage ----------------------------------

def test_everything_collapses_to_lineage_weight_one(nh):
    c = nh.add_claim("sophia_jesus_christ", "DERIVED_FROM", "eugnostos",
                     "pre-350CE",
                     ("DISS-1979", "EUGNOSTOS", "SJC", "KRAUSE-1964"))
    assert len(c.source_ids) == 4
    assert nh.independent_origins(c) == 1   # all roads lead through DISS-1979


# --- M03: hostile-source hearsay is typed, never promoted -----------------

def test_heresiologist_claims_enter_as_reported_disputed(nh):
    c = nh.add_claim("simon_magus", "COFOUNDED_REPORTED", "gnosticism",
                     "2nd_century_reports", ("DISS-1979", "IRENAEUS"),
                     status="DISPUTED")
    assert c.relation == "COFOUNDED_REPORTED"   # the type itself says 'reported'
    assert c.status == "DISPUTED"               # polemic source, flagged by DISS


# --- M05: absence claims bounded to the 1979 sweep -------------------------

def test_absences_are_1979_bounded(nh):
    # 'The term gnosticism lacks within the NH texts' — inside census: scoped.
    r = absence_verdict(nh, CENSUS_NH, "term_gnosticism", "ORGANIZED",
                        "nh_corpus", "dissertation_survey")
    assert r["verdict"] == "ABSENT_AFTER_SEARCH"
    assert r["coverage"]["census"] == "census-nh-v1-arthur1979"
    # Post-1979 scholarship is outside every declared cell: bare UNKNOWN.
    r2 = absence_verdict(nh, CENSUS_NH, "term_gnosticism", "ORGANIZED",
                         "post_1979_scholarship", "journals")
    assert r2["verdict"] == "UNKNOWN"


# --- M08: the defeminization gradient, transition by transition -----------

def _enter_transitions(nh):
    nh.add_claim("pair2:pagan_letter", "TRANSFORMED_INTO",
                 "pair2:christian_dialogue", "eugnostos_to_sjc",
                 ("DISS-1979", "EUGNOSTOS", "SJC", "KRAUSE-1964"))
    nh.add_claim("pair3:mythological_sophia", "TRANSFORMED_INTO",
                 "pair3:patriarchalized_summary", "origworld_to_hyparch",
                 ("DISS-1979", "ORIG-WORLD", "HYP-ARCH"))
    # Pair 4 (Thunder -> Gospel of Truth): the dissertation SAYS they are
    # 'not related in any direct literary manner' — so no transition claim
    # is entered, and the machine must refuse to narrate one.


def test_fourth_pair_transition_stays_unknown(nh):
    _enter_transitions(nh)
    report = transition_report(nh, ["pagan_letter", "christian_dialogue"], "pair2")
    assert report[0]["verdict"] == "SUPPORTED"
    report3 = transition_report(nh, ["mythological_sophia",
                                     "patriarchalized_summary"], "pair3")
    assert report3[0]["verdict"] == "SUPPORTED"
    # Pair 4: thematic contrast is not lineage. Un-evidenced gap stays open.
    report4 = transition_report(nh, ["goddess_aretalogy", "sophia_as_plane"],
                                "pair4")
    assert report4[0]["verdict"] == "UNKNOWN"
    assert report4[0]["claims"] == []


# --- M09: the thesis compiles as a self-refutable nutrient ----------------

def _compile_nutrient(nh):
    c1 = nh.add_claim("hyp_arch", "DERIVED_FROM", "orig_world",
                      "pre-350CE", ("DISS-1979", "ORIG-WORLD", "HYP-ARCH"))
    c2 = nh.add_claim("sophia_jesus_christ", "DERIVED_FROM", "eugnostos",
                      "pre-350CE", ("DISS-1979", "EUGNOSTOS", "SJC", "KRAUSE-1964"))
    c4 = nh.add_claim("pair2:pagan_letter", "TRANSFORMED_INTO",
                      "pair2:christian_dialogue", "eugnostos_to_sjc",
                      ("DISS-1979", "KRAUSE-1964"))
    c5 = nh.add_claim("pair3:mythological_sophia", "TRANSFORMED_INTO",
                      "pair3:patriarchalized_summary", "origworld_to_hyparch",
                      ("DISS-1979", "ORIG-WORLD", "HYP-ARCH"))
    # Counterevidence the dissertation itself reports: Yamauchi reads the
    # Illuminator passages as NT allusions -> attacks the pre-Christian
    # premise of pair 1.
    cy = nh.add_claim("apoc_adam", "DERIVED_FROM", "new_testament",
                      "contested", ("DISS-1979", "YAMAUCHI"), status="DISPUTED")
    return Nutrient(
        "NUT-NH-001",
        "Within the four document pairs surveyed by Arthur 1979, "
        "Christianization is accompanied by defeminization of creation "
        "and redemption motifs; supported by two literary-dependence "
        "chains; fourth pair is thematic contrast only, not lineage.",
        support=(c1.claim_id, c2.claim_id, c4.claim_id, c5.claim_id),
        counterevidence=(cy.claim_id,),
        unknowns=("dating of Apocalypse of Adam", "composite seams in both II.4/II.5",
                  "post-1979 scholarship entirely outside census"),
        absent_after_search=(("census-nh-v1-arthur1979", "term_gnosticism",
                              "nh_corpus", "dissertation_survey", "ORGANIZED"),),
        independence_clusters=1,
        visual_status="FORM_PARALLELS_HELD_AT_CANDIDATE",
        replay_receipt="rp-nh-001")


def test_nutrient_stands_at_lineage_weight_one(nh):
    n, vit = _compile_nutrient(nh).revalidate(nh, CENSUS_NH)
    assert n.status == "STANDING" and vit["vitality"] == 1.0
    assert n.self_refuted is False
    assert n.independence_clusters == 1     # single-witness, said out loud
    assert n.authority is False and n.admission is False


def test_new_census_decays_the_1979_absences(nh):
    # The day a post-1979 census is declared, the absence witnesses decay
    # and the nutrient drops to DECAYING until re-searched. Time does not
    # rot this nutrient; scholarship coverage does.
    n = _compile_nutrient(nh)
    n2, vit = n.revalidate(nh, Census("census-nh-v2", "2026", frozenset()))
    assert n2.status == "DECAYING"
    assert vit["vitality"] < 1.0


def test_deterministic(nh):
    a = canon(_compile_nutrient(nh).__dict__)
    b = canon(_compile_nutrient(nh).__dict__)
    assert a == b


if __name__ == "__main__":
    g = EvidenceGraph()
    ingest_packet(g, _packet())
    _enter_transitions(g)
    n, vit = _compile_nutrient(g).revalidate(g, CENSUS_NH)
    print(json.dumps({"nutrient": n.__dict__, "vitality": vit["vitality"]},
                     indent=1, ensure_ascii=False, default=str))
