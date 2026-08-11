"""The E_raw deep-dive trace, witnessed: the synthetic semantic trap
(compound PR + 15 syndicated reposts + credited-but-similar posters +
a scoped zero-hit search) run through the REAL modules, plus the
half-life mechanics for standing nutrients. All data synthetic fixture.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_memory import (
    EDGE_TYPES,
    Census,
    EvidenceGraph,
    Nutrient,
    absence_verdict,
    atomize,
    ingest_packet,
)


@pytest.fixture()
def trap():
    """E_raw: the four artifacts, injected through the M01 door."""
    g = EvidenceGraph()
    arts = [{"source_id": "ART1", "family": "synthetic_fixture",
             "locator": "fixture://article-1", "retrieved_at": "2026-08-10",
             "content": "UZIK, historical partner of the Calvi on the Rocks "
                        "festival, signs this new visual identity and the "
                        "Manucurist collaboration.",
             "rights_basis": "operator_owns_fixture"}]
    for i in range(15):  # the PR syndicate: identical text, minor blogs
        arts.append({"source_id": f"BLOG{i:02d}", "family": "synthetic_fixture",
                     "locator": f"fixture://blog-{i:02d}",
                     "retrieved_at": "2026-08-10",
                     "content": arts[0]["content"],
                     "rights_basis": "operator_owns_fixture",
                     "derived_from": "ART1"})
    for sid, body in [("POSTER18", "poster-2018-bytes+credit:AgencyX"),
                      ("POSTER19", "poster-2019-bytes+credit:UZIK")]:
        arts.append({"source_id": sid, "family": "synthetic_fixture",
                     "locator": f"fixture://{sid}", "retrieved_at": "2026-08-10",
                     "content": body, "rights_basis": "operator_owns_fixture"})
    report = ingest_packet(g, {"packet_id": "PKT-ERAW", "provided_by": "operator",
                               "artifacts": arts})
    assert len(report["registered"]) == 18
    return g


ALL16 = ("ART1",) + tuple(f"BLOG{i:02d}" for i in range(15))


# --- Step 1: M02 scission — proof of c1 cannot launder c2/c3 --------------

def test_step1_compound_narrative_is_scissioned(trap):
    parts = atomize("UZIK, historical partner of the Calvi on the Rocks "
                    "festival, signs this new visual identity and the "
                    "Manucurist collaboration.")
    assert len(parts) >= 3                     # forced scission, never bulk
    c1 = trap.add_claim("uzik", "PARTNER_OF", "calvi", "2003-2026", ALL16)
    c2 = trap.add_claim("uzik", "CREATIVE_CREDIT", "calvi_visual_identity",
                        "2019", ("ART1",))
    c3 = trap.add_claim("uzik", "ORGANIZED", "manucurist_collab", "2024", ("ART1",))
    assert len({c1.claim_id, c2.claim_id, c3.claim_id}) == 3
    # contamination physically blocked: the bundled form cannot enter at all
    with pytest.raises(ValueError, match="E_COMPOUND_CLAIM"):
        trap.add_claim("uzik", "CREATIVE_CREDIT",
                       "visual_identity and manucurist_collab", "2024", ("ART1",))


# --- Step 2: M04 — the consensus of 16 is mathematically zeroed -----------

def test_step2_sixteen_instances_one_lineage(trap):
    c1 = trap.add_claim("uzik", "PARTNER_OF", "calvi", "2003-2026", ALL16)
    assert len(c1.source_ids) == 16
    assert trap.independent_origins(c1) == 1   # support weight = 1, not 16


# --- Step 3: M06 — similarity preserved, authorship transport blocked -----

def test_step3_glyph_trap_disjoint_authorship(trap):
    trap.add_claim("poster_2018", "CREATIVE_CREDIT", "agency_x", "2018",
                   ("POSTER18",))
    trap.add_claim("poster_2019", "CREATIVE_CREDIT", "uzik", "2019",
                   ("POSTER19",))
    sim = trap.add_claim("poster_2018", "VISUAL_SIMILARITY_CANDIDATE",
                         "poster_2019", "2018-2019", ("POSTER18", "POSTER19"),
                         evidence_class="visual")
    assert sim.relation == "VISUAL_SIMILARITY_CANDIDATE"   # observation preserved
    assert "SAME_DESIGNER" not in EDGE_TYPES   # the collapse is unrepresentable
    assert trap.authorship_verdict("poster_2018", "agency_x") == "CREDITED"
    assert trap.authorship_verdict("poster_2019", "uzik") == "CREDITED"
    assert trap.authorship_verdict("poster_2018", "uzik") == "UNKNOWN"
    with pytest.raises(ValueError, match="E_GLYPH_TRAP"):
        trap.add_claim("poster_2018", "CREATIVE_CREDIT", "uzik", "2018",
                       ("POSTER18",), evidence_class="visual")


# --- Step 4: M05 — absence stays scoped -----------------------------------

CENSUS = Census("census-v1", "2026-08",
                frozenset({("uzik_manucurist_calvi", "2003-2010", "press",
                            "PARTNER_OF")}))


def test_step4_zero_hits_never_becomes_never_existed(trap):
    r = absence_verdict(trap, CENSUS, "uzik_manucurist_calvi", "PARTNER_OF",
                        "2003-2010", "press")
    assert r["verdict"] == "ABSENT_AFTER_SEARCH"
    assert r["coverage"]["cell"][1] == "2003-2010"       # bounded, not absolute
    out = absence_verdict(trap, CENSUS, "uzik_manucurist_calvi", "PARTNER_OF",
                          "1995-2002", "press")
    assert out["verdict"] == "UNKNOWN"                   # outside census: nothing


# --- Section III: the compiled nutrient -----------------------------------

def _nutrient(trap):
    c1 = trap.add_claim("uzik", "PARTNER_OF", "calvi", "2003-2026", ALL16)
    c3 = trap.add_claim("uzik", "ORGANIZED", "manucurist_collab", "2024", ("ART1",))
    return Nutrient(
        "nut_uzik_calvi_001",
        "partnership and collaboration supported at lineage weight 1; "
        "visual identity credit contested by glyph trap",
        support=(c1.claim_id, c3.claim_id),
        absent_after_search=(("census-v1", "uzik_manucurist_calvi",
                              "2003-2010", "press", "PARTNER_OF"),),
        independence_clusters=1,
        visual_status="HIGH_SIMILARITY_DISJOINT_AUTHORSHIP",
        replay_receipt="rp-001")


def test_nutrient_compiles_standing_but_never_admitted(trap):
    n, vit = _nutrient(trap).revalidate(trap, CENSUS)
    assert n.status == "STANDING" and vit["vitality"] == 1.0
    assert n.self_refuted is False
    assert n.authority is False and n.admission is False   # awaits Γ, holds nothing


# --- The half-life mechanics ----------------------------------------------

def test_decay_is_event_indexed_not_clocked(trap):
    # Same graph, same census, any number of re-checks: identical result.
    n = _nutrient(trap)
    a = n.revalidate(trap, CENSUS)
    b = n.revalidate(trap, CENSUS)
    assert a == b                       # no clock anywhere in the decay law


def test_witness_loss_decays_before_it_kills(trap):
    n = _nutrient(trap)
    # Frame event: one syndicate blog loses its receipt. Replay is strict —
    # c1 (which cites BLOG00) fails, c3 and the absence survive: 2 of 3.
    trap.sources["BLOG00"] = trap.sources["BLOG00"].__class__(
        **{**trap.sources["BLOG00"].__dict__, "retrieval_receipt": ""})
    n2, vit = n.revalidate(trap, CENSUS)
    assert 0.5 <= vit["vitality"] < 1.0
    assert n2.status == "DECAYING"      # gate-ineligible, re-derivation ordered


def test_half_life_crossing_forces_compost(trap):
    n = _nutrient(trap)
    # Frame events kill the majority of witnesses: both supports lose replay.
    for sid in ("ART1", "BLOG00"):
        trap.sources[sid] = trap.sources[sid].__class__(
            **{**trap.sources[sid].__dict__, "retrieval_receipt": ""})
    # ART1 breaks c3 entirely and c1 partially; also supersede the census.
    n2, vit = n.revalidate(trap, Census("census-v2", "2026-09", frozenset()))
    assert vit["vitality"] < 0.5
    assert n2.status == "COMPOSTED"     # forcefully decomposed, back to the pile


def test_census_supersession_revokes_absences(trap):
    # Coverage expansion is a decay tick: an absence earned under census-v1
    # is not transportable to census-v2 without re-search.
    n = _nutrient(trap)
    n2, vit = n.revalidate(trap, Census("census-v2", "2026-09", frozenset()))
    assert vit["vitality"] < 1.0
    assert n2.status == "DECAYING"
    assert any(kind == "absence" and not ok for kind, _c, ok in vit["checks"])
