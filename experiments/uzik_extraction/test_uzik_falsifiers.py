"""Falsifiers for UZIK_DEEP_EXTRACTION_V1 — every preserved distinction
gets a test that tries to collapse it. INSTANCE data here is synthetic
fixture material (source family 'synthetic_fixture'); nothing in this
file asserts a real-world fact about any entity.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_memory import (
    Census,
    EvidenceGraph,
    Nutrient,
    absence_verdict,
    canon,
    eta_receipt,
    transition_report,
    verify_eta_chain,
)


def _graph():
    g = EvidenceGraph()
    for i, derived in [(1, ""), (2, ""), (3, "S2"), (4, "S2"), (5, "S2")]:
        g.register_source(source_id=f"S{i}", family="synthetic_fixture",
                          locator=f"fixture://doc{i}",
                          retrieval_receipt=f"rr-{i:02d}",
                          content_hash=f"ch-{'orig' if not derived else 'repost'}-{i}",
                          derived_from=derived)
    return g


# --- upgrade 1: typed edges only -----------------------------------------

def test_untyped_relation_rejected():
    g = _graph()
    with pytest.raises(ValueError, match="E_UNTYPED_RELATION"):
        g.add_claim("uzik", "RELATED_TO", "calvi", "2003-2026", ("S1",))


def test_contact_is_a_typed_edge_not_influence():
    g = _graph()
    c = g.add_claim("uzik", "PARTNER_OF", "manucurist", "2024", ("S1",))
    assert c.relation == "PARTNER_OF"          # no silent influence/authorship edge
    assert c.status == "REPORTED"


# --- upgrade 2: replayable memory ----------------------------------------

def test_replay_answers_why_do_you_know_this():
    g = _graph()
    c = g.add_claim("uzik", "ORGANIZED", "calvi", "2003-2019", ("S1", "S2"))
    r = g.replay((c.claim_id,))
    assert r["verdict"] == "REPLAYED"
    receipts = [s["receipt"] for step in r["path"] for s in step["sources"]]
    assert receipts == ["rr-01", "rr-02"]      # nutrient→claims→sources→receipts


def test_broken_chain_replays_unknown():
    g = _graph()
    g.sources["S1"] = g.sources["S1"].__class__(**{**g.sources["S1"].__dict__,
                                                   "retrieval_receipt": ""})
    c = g.add_claim("uzik", "ORGANIZED", "calvi", "2003-2019", ("S1",))
    assert g.replay((c.claim_id,))["verdict"] == "UNKNOWN"


# --- upgrade 3: coverage-aware UNKNOWN -----------------------------------

def test_unknown_vs_absent_after_search():
    g = _graph()
    census = Census("census-v1", "2026-08",
                    frozenset({("calvi", "2025", "press", "CANCELLED")}))
    covered = absence_verdict(g, census, "calvi", "CANCELLED", "2025", "press")
    assert covered["verdict"] == "ABSENT_AFTER_SEARCH"
    assert covered["coverage"]["census"] == "census-v1"   # coverage travels with the verdict
    uncovered = absence_verdict(g, census, "calvi", "CANCELLED", "1999", "press")
    assert uncovered["verdict"] == "UNKNOWN"              # fake exhaustivity refused


# --- upgrade 4: source independence --------------------------------------

def test_reposts_are_not_corroborations():
    g = _graph()
    # S3,S4,S5 all derive from S2: five sources, two informational origins.
    c = g.add_claim("uzik", "ORGANIZED", "calvi", "2003-2019",
                    ("S1", "S2", "S3", "S4", "S5"))
    assert len(c.source_ids) == 5
    assert g.independent_origins(c) == 2


# --- upgrades 5: temporal chiddush ---------------------------------------

def test_each_transition_names_its_sources():
    g = _graph()
    g.add_claim("calvi:festival", "TRANSFORMED_INTO", "calvi:brand_platform",
                "2010-2015", ("S1",))
    g.add_claim("calvi:brand_platform", "TRANSFORMED_INTO", "calvi:cultural_archive",
                "2015-2023", ("S2",))
    report = transition_report(g, ["festival", "brand_platform",
                                   "cultural_archive", "interruption"], "calvi")
    verdicts = [(r["from"], r["to"], r["verdict"]) for r in report]
    assert verdicts[0] == ("festival", "brand_platform", "SUPPORTED")
    assert verdicts[1] == ("brand_platform", "cultural_archive", "SUPPORTED")
    assert verdicts[2] == ("cultural_archive", "interruption", "UNKNOWN")


# --- upgrade 6: GLYPH_TRAP -----------------------------------------------

def test_visual_evidence_cannot_mint_authorship():
    g = _graph()
    with pytest.raises(ValueError, match="E_GLYPH_TRAP"):
        g.add_claim("poster_a", "CREATIVE_CREDIT", "poster_b", "2019", ("S1",),
                    evidence_class="visual")
    c = g.add_claim("poster_a", "VISUAL_SIMILARITY_CANDIDATE", "poster_b",
                    "2019", ("S1",), evidence_class="visual")
    assert c.relation == "VISUAL_SIMILARITY_CANDIDATE"


def test_direct_credit_outranks_resemblance():
    g = _graph()
    g.add_claim("poster_a", "VISUAL_SIMILARITY_CANDIDATE", "studio_x", "2019",
                ("S3",), evidence_class="visual")
    assert g.authorship_verdict("poster_a", "studio_x") == "VISUAL_SIMILARITY_CANDIDATE"
    g.add_claim("poster_a", "CREATIVE_CREDIT", "studio_x", "2019", ("S1",),
                evidence_class="documentary")
    assert g.authorship_verdict("poster_a", "studio_x") == "CREDITED"


# --- upgrade 7: ETA transformation receipts ------------------------------

def test_eta_chain_binds_identity_and_shape_alone_does_not():
    original = b"logo-source-bytes"
    cropped = b"logo-cropped"
    vector = b"logo-vectorized"
    r1 = eta_receipt(original, "crop", {"box": [0, 0, 10, 10]}, "tool/1.0", cropped)
    r2 = eta_receipt(cropped, "vectorize", {"tol": 0.1}, "tool/1.0", vector)
    assert verify_eta_chain(original, vector, [r1, r2])["verdict"] == "BOUND"
    # A look-alike with no receipts is UNKNOWN — preserved shape proves nothing.
    assert verify_eta_chain(original, vector, [])["verdict"] == "UNKNOWN"
    # Tampered middle step breaks the chain.
    r2_bad = dict(r2, input_hash="0" * 64)
    assert "E_CHAIN_BROKEN" in verify_eta_chain(original, vector, [r1, r2_bad])["reason"]


# --- upgrades 8 + 9: self-refusing nutrients, garden ⊬ kernel -------------

def test_nutrient_refuses_itself():
    g = _graph()
    c1 = g.add_claim("uzik", "ORGANIZED", "calvi", "2003-2019", ("S1",))
    c2 = g.add_claim("uzik", "ORGANIZED", "calvi", "2003-2019", ("S2",),
                     status="DISPUTED")
    n = Nutrient("N1", "synthetic insight", support=(c1.claim_id,),
                 counterevidence=(c2.claim_id,), replay_receipt="rp")
    assert n.self_refusal(g).status == "COMPOSTED"       # counterevidence >= support
    n2 = Nutrient("N2", "unsupported insight")
    assert n2.self_refusal(g).status == "COMPOSTED"      # no support at all
    n3 = Nutrient("N3", "supported insight",
                  support=(c1.claim_id, c2.claim_id), replay_receipt="rp")
    assert n3.self_refusal(g).status == "STANDING"       # standing ≠ admitted


def test_garden_has_no_kernel_path():
    with pytest.raises(ValueError, match="E_GARDEN_IS_NOT_KERNEL"):
        Nutrient("N", "s", admission=True)
    with pytest.raises(ValueError, match="E_GARDEN_IS_NOT_KERNEL"):
        Nutrient("N", "s", authority=True)
    import corpus_memory
    exported = {x for x in dir(corpus_memory) if not x.startswith("_")}
    assert not any("admit" in x.lower() for x in exported)


# --- determinism ----------------------------------------------------------

def test_deterministic():
    def run():
        g = _graph()
        c = g.add_claim("uzik", "ORGANIZED", "calvi", "2003-2019", ("S1", "S2"))
        return canon(g.replay((c.claim_id,)))
    assert run() == run()
