"""Falsifiers for PRIZE_PAPERS / ONE_CAPTURE: the five forbidden joins,
the seven-layer multiplex, and the cross-layer admission gate. No
vessel's records are invented; fixtures are generic.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prize_papers as pp
from prize_papers import (
    BundleDocument,
    CapturedVessel,
    CrossLayerClaim,
    apply_judgment,
    attribute_authorship,
    attribute_ownership,
    capture_legality,
    delivery_status,
)

WITNESS = {"kind": "signed_provenance"}
COURT = {"kind": "court_finding", "verdict": "LAWFUL_PRIZE"}


# ── DOCUMENT_LOCATION != AUTHORSHIP ────────────────────────────────────

def test_a_paper_aboard_does_not_name_its_author():
    doc = BundleDocument("d1", "S_phys", "logbook", "archive:HCA/32/1")
    r = attribute_authorship(doc, "Captain X")
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP"


def test_authorship_crosses_only_with_a_provenance_witness():
    doc = BundleDocument("d1", "S_phys", "logbook", "archive:HCA/32/1")
    r = attribute_authorship(doc, "Captain X", witness=WITNESS)
    assert r["verdict"] == "ATTRIBUTED" and r["via"] == "signed_provenance"


# ── CARGO != OWNERSHIP ─────────────────────────────────────────────────

def test_possession_is_not_title():
    r = attribute_ownership("cargo:sugar-40hhd", "Merchant Y")
    assert r["reason"] == "E_CARGO_IS_NOT_OWNERSHIP"
    ok = attribute_ownership("cargo:sugar-40hhd", "Merchant Y",
                             witness={"kind": "notarized_bill"})
    assert ok["verdict"] == "TITLE_ESTABLISHED"


# ── INTERCEPTED != DELIVERED ───────────────────────────────────────────

def test_a_letter_in_the_bundle_is_proof_of_non_delivery():
    letter = BundleDocument("l1", "S_communication", "letter",
                            "archive:letters")
    r = delivery_status(letter)
    assert r["delivered"] is False
    assert r["verdict"] == "INTERCEPTED_UNDELIVERED"
    assert "proof of non-delivery" in r["law"]


def test_a_non_letter_is_not_a_delivery_question():
    doc = BundleDocument("d", "S_cargo", "bill", "a")
    assert delivery_status(doc)["verdict"] == "NOT_A_LETTER_IN_TRANSIT"


# ── CAPTURED != LAWFULLY_CAPTURED (EFFECT != AUTHORIZED EFFECT) ────────

def test_capture_occurs_but_legality_is_unresolved():
    r = capture_legality(capture_occurred=True)
    assert r["physical_capture"] is True
    assert r["legal_status"] == "UNADJUDICATED"
    assert "effect is not authorized effect" in r["law"]


def test_only_a_court_finding_adjudicates_legality():
    non_court = capture_legality(True, {"kind": "signed_provenance"})
    assert non_court["legal_status"] == "UNADJUDICATED"
    adjudicated = capture_legality(True, COURT)
    assert adjudicated["adjudicated"] is True
    assert adjudicated["legal_status"] == "LAWFUL_PRIZE"


# ── COURT_JUDGMENT != WORLD_HISTORY ────────────────────────────────────

def test_a_ruling_does_not_rewrite_the_physical_capture():
    fact = {"occurred": True, "date": "1745-03"}
    r = apply_judgment(fact, {"verdict": "UNLAWFUL_CAPTURE"})
    assert r["physical_capture_fact"] is True          # still happened
    assert r["physical_capture_unchanged"] is True
    assert r["legal_state_after"] == "UNLAWFUL_CAPTURE"
    assert "not rewritten" in r["law"]


# ── the seven-layer multiplex ──────────────────────────────────────────

def test_a_capture_populates_several_layers():
    v = CapturedVessel("v1", {"S_phys": ("hull",),
                              "S_cargo": ("sugar",),
                              "S_legal": ("HCA case 88",)})
    assert v.is_multiplex() is True
    assert v.facts_in("S_cargo") == ("sugar",)


def test_a_single_layer_is_a_document_not_a_capture():
    v = CapturedVessel("v2", {"S_phys": ("hull",)})
    assert v.is_multiplex() is False


def test_unknown_layer_is_refused():
    with pytest.raises(ValueError, match="E_UNKNOWN_LAYER"):
        BundleDocument("d", "S_vibes", "letter", "a")


# ── the cross-layer admission gate ─────────────────────────────────────

def test_an_unwitnessed_cross_layer_join_is_refused():
    claim = CrossLayerClaim("c1", "S_phys", "S_authority",
                            "cargo aboard implies owned by shipowner")
    r = claim.admit()
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_UNWITNESSED_CROSS_LAYER_JOIN"


def test_a_witnessed_cross_layer_join_is_admitted():
    claim = CrossLayerClaim("c2", "S_cargo", "S_authority",
                            "bill establishes title",
                            witness_kind="notarized_bill")
    assert claim.admit()["verdict"] == "CROSS_LAYER_ADMITTED"


def test_an_intra_layer_claim_has_no_join_to_police():
    claim = CrossLayerClaim("c3", "S_legal", "S_legal", "case cites case")
    assert claim.admit()["verdict"] == "INTRA_LAYER"


# ── the registry and the manifest ──────────────────────────────────────

def test_five_forbidden_joins_registered():
    assert len(pp.FORBIDDEN_JOINS) == 5
    names = {n for n, _ in pp.FORBIDDEN_JOINS}
    assert "E_PHYSICAL_EFFECT_IS_NOT_LEGALITY" in names
    assert "E_COURT_JUDGMENT_IS_NOT_WORLD_HISTORY" in names


def test_manifest_is_schema_not_fabricated_vessel_data():
    m = pp.ONE_CAPTURE_MANIFEST_SCHEMA
    assert m["status"] == "PRESENCE_OBSERVED_NOT_READ"
    assert m["layers"] == pp.LAYERS
    assert "fabricating a vessel's records here would be" in m["note"]


def test_deterministic():
    v = CapturedVessel("v1", {"S_phys": ("h",), "S_cargo": ("c",)})
    assert pp.canon(v.layers) == pp.canon(v.layers)
