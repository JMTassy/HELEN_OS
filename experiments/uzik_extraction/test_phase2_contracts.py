"""Phase-2 contract falsifiers: M02 (epistemic contamination) and the
M01 ingestion door (rights freeze + SOURCE_STATE_DRIFT). Fixture data
remains synthetic; no real-world assertion enters."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_memory import EvidenceGraph, Nutrient, atomize, ingest_packet


def _packet(*artifacts):
    return {"packet_id": "PKT-TEST-01", "provided_by": "operator",
            "artifacts": list(artifacts)}


def _art(sid, content="doc body", rights="operator_owns_fixture", **kw):
    return {"source_id": sid, "family": "synthetic_fixture",
            "locator": f"fixture://{sid}", "retrieved_at": "2026-08-10",
            "content": content, "rights_basis": rights, **kw}


# --- M02: CLAIM_ATOMIZER / EPISTEMIC_CONTAMINATION ------------------------

def test_compound_claim_rejected_at_the_graph():
    g = EvidenceGraph()
    g.register_source(source_id="S1", family="synthetic_fixture",
                      locator="fixture://1", retrieval_receipt="rr",
                      content_hash="ch")
    with pytest.raises(ValueError, match="E_COMPOUND_CLAIM"):
        g.add_claim("uzik", "ORGANIZED", "calvi and bruit_de_fond",
                    "2003-2019", ("S1",))


def test_atomizer_scissions_compound_statements():
    parts = atomize("UZIK organized Calvi on the Rocks and "
                    "partnered with Manucurist; the 2025 edition was cancelled.")
    assert len(parts) == 3
    assert parts[0].startswith("UZIK organized")
    assert parts[1].startswith("partnered with")
    assert parts[2].startswith("the 2025 edition")


def test_atomizer_is_conservative_never_bundles():
    # Over-splitting is acceptable; returning fewer parts than statements
    # is the contamination failure.
    assert len(atomize("A and B and C")) == 3
    assert atomize("single statement") == ("single statement",)


# --- M01: ingestion door --------------------------------------------------

def test_rights_undeclared_is_refused():
    g = EvidenceGraph()
    report = ingest_packet(g, _packet(_art("S1", rights="")))
    assert report["registered"] == []
    assert report["refused"][0]["reason"] == "E_RIGHTS_UNDECLARED"
    assert "S1" not in g.sources


def test_state_hash_binds_content_not_url():
    g = EvidenceGraph()
    ingest_packet(g, _packet(_art("S1", content="version one")))
    ingest_packet(g, _packet(_art("S2", content="version one",
                                  )))  # same content, different locator id
    assert g.sources["S1"].content_hash == g.sources["S2"].content_hash


def test_source_state_drift_surfaced_not_absorbed():
    g = EvidenceGraph()
    ingest_packet(g, _packet(_art("S1", content="frozen text")))
    frozen = g.sources["S1"].content_hash
    report = ingest_packet(g, _packet(_art("S1", content="silently edited text")))
    assert report["drift"][0]["reason"] == "E_SOURCE_STATE_DRIFT"
    assert g.sources["S1"].content_hash == frozen   # the frozen record stands


def test_ingestion_registers_with_receipt_and_rights():
    g = EvidenceGraph()
    report = ingest_packet(g, _packet(_art("S1"), _art("S2", derived_from="S1")))
    assert report["registered"] == ["S1", "S2"]
    s = g.sources["S1"]
    assert s.rights_basis == "operator_owns_fixture"
    assert s.retrieval_receipt          # non-empty, hash-derived
    assert g.sources["S2"].derived_from == "S1"


# --- F09 surface: self_refuted field matches the frozen schema ------------

def test_nutrient_self_refuted_field():
    g = EvidenceGraph()
    n = Nutrient("N1", "unsupported").self_refusal(g)
    assert n.self_refuted is True
    assert n.status == "COMPOSTED"
