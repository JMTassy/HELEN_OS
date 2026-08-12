"""The completeness test on a vendor sales document: does the 1918
welding book produce a prohibition the four ceilings cannot hold?
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import welding_1918 as w
from completeness import CEILING_BASIS, compile_to_ceiling
from welding_1918 import WELDING_1918_PROHIBITIONS, corpus_completeness


def test_the_vendor_corpus_maps_completely_no_fifth_ceiling():
    r = corpus_completeness()
    assert r["completeness_verdict"] == "MAPS_COMPLETELY"
    assert r["needs_fifth_ceiling"] is False
    assert r["unmapped"] == []


def test_every_prohibition_lands_in_one_of_the_four_ceilings():
    for p in WELDING_1918_PROHIBITIONS:
        assert p["ceiling"] in CEILING_BASIS, p["finding"]


def test_every_prohibition_carries_a_real_ocr_anchor():
    for p in WELDING_1918_PROHIBITIONS:
        assert p["ocr"] and len(p["ocr"]) > 10, p["finding"]


def test_census_linked_prohibitions_agree_with_the_harness():
    """Where a welding prohibition names an existing census key, the
    harness must independently compile that key to the same ceiling."""
    for p in WELDING_1918_PROHIBITIONS:
        if p["census"]:
            c = compile_to_ceiling(p["census"])
            assert c["axis"] == "SAFETY"
            assert c["ceiling"] == p["ceiling"], (p["finding"], c)


def test_a_sales_document_launders_mostly_on_the_proof_ceiling():
    """The characteristic finding: a vendor document's laundering is
    PROOF-heavy — claiming more than the evidence supports."""
    dist = corpus_completeness()["ceiling_distribution"]
    assert dist.get("PROOF", 0) >= 4
    assert "PROOF" in dist and "SCOPE" in dist and "REPLAY" in dist


def test_the_images_are_not_accessed_never_asserted_absent():
    """The archive.org images could not be fetched; the corpus records
    NOT_ACCESSED and rests no claim on them."""
    assert "NOT_ACCESSED" in w.CORPUS["images"]
    assert w.CORPUS["access_mode"] == "RELAYED"
    img = next(p for p in WELDING_1918_PROHIBITIONS
               if "images" in p["finding"])
    assert img["census"] == "DocumentNotFound != EventDidNotOccur"


def test_completeness_stays_evidence_never_proof():
    r = corpus_completeness()
    assert "never PROVEN" in r["epistemic_status"]
    assert "NotObserved != Impossible" in r["epistemic_status"]


def test_deterministic():
    assert w.canon(corpus_completeness()) == w.canon(corpus_completeness())
