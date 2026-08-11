"""Falsifiers for the Crystal Palace HER/HAL harness.

Every kill condition executes. Every ⊬ is a raise or a refusal, not a
comment. The corpus is dark in this frame and the tests assert THAT too.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import crystal_palace as cp
from crystal_palace import (
    AVAILABLE,
    UNREACHABLE,
    C_1851,
    CompostPacket,
    Corpus1851,
    GraphEdge,
    GraphNode,
    NoveltyHypothesis,
    PageRecord,
    Tau,
    adjacent_possible,
    edge_authority,
    freeze_candidates,
    hal_verdict,
    her_read_page,
    promote_claim,
    rv_re,
)


# ── the frame fact: the corpus is dark, and the harness says so ─────────

def test_corpus_boots_unreachable_and_reads_return_unknown():
    assert C_1851.availability == UNREACHABLE
    r = her_read_page(C_1851, "p001")
    assert r["status"] == "UNKNOWN" and r["reason"] == "E_PAGE_NOT_IN_FRAME"


def test_a_delivered_page_reads_but_only_that_page():
    lit = Corpus1851("c", AVAILABLE, 842, frozenset({"p120"}))
    rec = PageRecord("p120", observed=("hydraulic press, exhibited",))
    assert her_read_page(lit, "p120", rec)["status"] == "READ"
    assert her_read_page(lit, "p121")["status"] == "UNKNOWN"
    # a record for the wrong page does not read either
    assert her_read_page(lit, "p120", PageRecord("p999"))["reason"] == \
        "E_NO_RECORD_FOR_PAGE"


# ── HER schema: no silent promotion ─────────────────────────────────────

def test_inference_appearing_in_observed_is_unconstructible():
    with pytest.raises(ValueError, match="E_SILENT_PROMOTION"):
        PageRecord("p1", observed=("steam governor regulates speed",),
                   inferred_claims=("steam governor regulates speed",))


def test_inference_in_explicit_claims_is_also_promotion():
    with pytest.raises(ValueError, match="E_SILENT_PROMOTION"):
        PageRecord("p1", explicit_claims=("x",), inferred_claims=("x",))


def test_confidence_is_bounded():
    with pytest.raises(ValueError, match="E_CONFIDENCE_RANGE"):
        PageRecord("p1", confidence=1.2)


# ── C1/K4: components are not a combination ─────────────────────────────

def test_observed_edge_from_component_existence_is_unconstructible():
    """Parts on shelves never witness the machine. The edge type itself
    refuses the promotion — this is C1 as a constructor law."""
    with pytest.raises(ValueError, match="E_COMPONENTS_ARE_NOT_A_COMBINATION"):
        GraphEdge("boiler", "governor", "regulates",
                  basis="component_existence", grade="OBSERVED")
    with pytest.raises(ValueError, match="E_COMPONENTS_ARE_NOT_A_COMBINATION"):
        GraphEdge("boiler", "governor", "regulates",
                  basis="component_existence", grade="REPORTED")


def test_component_existence_edge_at_hypothesis_is_the_legal_move():
    e = GraphEdge("boiler", "governor", "regulates",
                  basis="component_existence", grade="HYPOTHESIS")
    assert e.grade == "HYPOTHESIS"     # C3's legitimate adjacent-possible


# ── C4: authority gravity ───────────────────────────────────────────────

_NODES = {"press": GraphNode("press", "OBSERVED", pages=("p120",)),
          "pump": GraphNode("pump", "REPORTED", pages=("p121",))}


def test_edge_authority_capped_by_weakest_endpoint():
    e = GraphEdge("press", "pump", "drives", basis="on_page", grade="OBSERVED")
    v = edge_authority(e, _NODES)
    assert v["authority"] == "REPORTED"    # min(OBSERVED, REPORTED)


def test_twenty_convergent_pages_add_zero_authority():
    """Corpus coherence feels inevitable. It counts for nothing."""
    e = GraphEdge("press", "pump", "drives", basis="on_page",
                  grade="INFERRED")
    twenty = tuple(f"p{i}" for i in range(20))
    v = edge_authority(e, _NODES, convergent_pages=twenty)
    assert v["authority"] == "INFERRED"
    assert v["convergence_counted"] == 0
    assert v["convergent_pages_seen"] == 20


def test_one_external_witness_raises_by_exactly_one_grade():
    e = GraphEdge("press", "pump", "drives", basis="on_page",
                  grade="INFERRED")
    w = ({"kind": "external", "receipt": "patent office ledger 1852/331"},
         {"kind": "external", "receipt": "second archive"})
    v = edge_authority(e, _NODES, external_witnesses=w)
    assert v["authority"] == "REPORTED" and v["raised_by_external_witness"]
    # a witness without a receipt, or corpus convergence, raises nothing
    v2 = edge_authority(e, _NODES, external_witnesses=(
        {"kind": "external"}, {"kind": "corpus_convergence", "receipt": "x"}))
    assert v2["authority"] == "INFERRED"


# ── C3: adjacent possible is neighbourhood-closed ───────────────────────

def test_component_outside_neighbourhood_is_refused_not_scored():
    nk = frozenset({"steam_engine", "governor", "iron_frame"})
    bad = adjacent_possible(nk, ("steam_engine", "electric_motor"))
    assert bad["verdict"] == "REJECT"
    assert bad["components_outside_Nk"] == ["electric_motor"]
    good = adjacent_possible(nk, ("steam_engine", "governor"))
    assert good["verdict"] == "CANDIDATE" and good["status"] == "HYPOTHESIS"
    assert "Generable" in good["note"]     # Generable ⊬ HistoricallyObserved


# ── C5: the three forbidden promotions ──────────────────────────────────

@pytest.mark.parametrize("claim,target", list(cp.FORBIDDEN_PROMOTIONS.items()))
def test_semantic_shortcuts_refused_without_external_witness(claim, target):
    r = promote_claim(claim, target)
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_SEMANTIC_SHORTCUT"


def test_promotion_with_external_receipt_is_the_priced_door():
    r = promote_claim("described as patent", "verified patent",
                      witnesses=({"kind": "external",
                                  "receipt": "GB patent roll 1851"},))
    assert r["verdict"] == "PROMOTED_WITH_WITNESS"


# ── C6: three clocks never substitute ───────────────────────────────────

def test_observation_date_is_never_the_event_date():
    tau = Tau(t_event="1712", t_source="1851", t_record="2026-08-11")
    assert tau.observation_date() == "1851"    # not 1712
    assert tau.event_date() == "1712"


def test_event_date_is_never_backfilled_from_source():
    tau = Tau(t_source="1851")
    assert tau.event_date() == "UNKNOWN"       # not 1851


# ── C7: the freeze ──────────────────────────────────────────────────────

def test_freeze_is_deterministic_and_order_stable():
    a = freeze_candidates(("cand1", "cand2"))
    b = freeze_candidates(("cand1", "cand2"))
    assert a["freeze_hash"] == b["freeze_hash"]
    assert a["contamination"] == ()


def test_future_consult_before_freeze_is_remembered_not_laundered():
    log = ({"kind": "POST_1851_CONSULT", "what": "1876 patent index"},)
    r = freeze_candidates(("cand1",), access_log=log)
    assert r["contamination"] == log           # on the receipt, forever


def test_rv_re_refuses_without_a_clean_freeze():
    assert rv_re(8, 10, 2, 10)["status"] == "UNKNOWN"
    dirty = freeze_candidates(("c",), access_log=(
        {"kind": "POST_1851_CONSULT", "what": "hindsight"},))
    assert rv_re(8, 10, 2, 10, dirty)["status"] == "UNKNOWN"
    clean = freeze_candidates(("c",))
    m = rv_re(8, 10, 2, 10, clean)
    assert m["status"] == "MEASURED"
    assert m["R_V"] == 0.8 and m["R_E"] == 0.2 and m["chiddush_supported"]


# ── C2: the novelty measure never asserts itself ────────────────────────

def test_novelty_weighting_is_hypothesis_grade():
    n = NoveltyHypothesis()
    assert n.status == "HYPOTHESIS" and n.beta > n.alpha
    assert n.score(1.0, 1.0) == 5.0
    assert not hasattr(n, "verdict")


# ── HAL: kill conditions all fire ───────────────────────────────────────

def _clean_packet(**over):
    base = dict(
        candidate_id="cand-press-pump",
        supporting_pages=("p120", "p121"),
        primitive_nodes=(GraphNode("press", "OBSERVED", pages=("p120",)),),
        inferred_edges=(GraphEdge("press", "pump", "drives",
                                  basis="on_page", grade="INFERRED"),),
        explicit_vs_inferred={"explicit": ("press exhibited",),
                              "inferred": ("press could drive pump",)},
        temporal_provenance=(("q1", Tau(t_event="1848", t_source="1851"),
                              "1848"),),
        information_loss="compressed 2 pages to 1 candidate; prose dropped",
        assumptions_added=("assumes shared exhibition hall implies "
                           "physical proximity",),
        independent_witnesses=(),
        counterevidence=(),
        leakage_risk="NONE",
        novelty_hypothesis="INSIGHT",
        falsifier={"statement": "no page connects press to pump",
                   "executed": True, "survived": True})
    base.update(over)
    return CompostPacket(**base)


_CLEAN_FREEZE = freeze_candidates(("cand-press-pump",))
_DIRTY_FREEZE = freeze_candidates(("cand-press-pump",), access_log=(
    {"kind": "POST_1851_CONSULT", "what": "1890 patent gazette"},))


def test_k1_future_data_before_freeze_kills():
    v = hal_verdict(_clean_packet(), _DIRTY_FREEZE)
    assert v["verdict"] == "NO_SHIP"
    assert "K1_FUTURE_DATA_BEFORE_FREEZE" in v["kill_conditions"]


def test_k2_inference_as_observation_kills():
    p = _clean_packet(explicit_vs_inferred={
        "explicit": ("press could drive pump",),
        "inferred": ("press could drive pump",)})
    v = hal_verdict(p, _CLEAN_FREEZE)
    assert "K2_INFERENCE_AS_OBSERVATION" in v["kill_conditions"]


def test_k3_convergence_offered_as_witness_kills():
    p = _clean_packet(independent_witnesses=(
        {"kind": "corpus_convergence", "receipt": "20 more pages agree"},))
    v = hal_verdict(p, _CLEAN_FREEZE)
    assert "K3_CONVERGENCE_AS_WITNESS" in v["kill_conditions"]


def test_k4_prose_smuggled_combination_kills():
    p = _clean_packet(assumptions_added=(
        "components imply combination existed",))
    v = hal_verdict(p, _CLEAN_FREEZE)
    assert "K4_COMPONENTS_AS_COMBINATION" in v["kill_conditions"]


def test_k5_patent_word_as_patent_fact_kills():
    p = _clean_packet(assumptions_added=("verified patent",))
    v = hal_verdict(p, _CLEAN_FREEZE)
    assert "K5_PATENT_WORD_AS_PATENT_FACT" in v["kill_conditions"]


def test_k6_source_date_as_event_date_kills():
    p = _clean_packet(temporal_provenance=(
        ("q1", Tau(t_source="1851"), "1851"),))   # event backfilled
    v = hal_verdict(p, _CLEAN_FREEZE)
    assert "K6_SOURCE_DATE_AS_EVENT_DATE" in v["kill_conditions"]


# ── HAL: the four terminal states ───────────────────────────────────────

def test_clean_packet_ships_as_insight_and_only_insight():
    v = hal_verdict(_clean_packet(), _CLEAN_FREEZE)
    assert v["verdict"] == "SHIP_INSIGHT" and v["glyph"] == "🌹"
    assert v["admits"] is False
    for banned in ("HISTORICAL_FACT", "PATENT_FACT", "NOVELTY_CLAIM"):
        assert banned in v["does_not_license"]


def test_underwitnessed_packet_holds():
    p = _clean_packet(falsifier={"statement": "declared", "executed": False,
                                 "survived": False})
    v = hal_verdict(p, _CLEAN_FREEZE)
    assert v["verdict"] == "HOLD" and v["glyph"] == "🌿"
    assert v["missing"] == ["F_falsifier_survived"]


def test_strong_claims_escalate_even_when_gates_pass():
    for cls in ("HISTORICAL_FACT", "PATENT_CLAIM", "NOVELTY_CLAIM"):
        v = hal_verdict(_clean_packet(novelty_hypothesis=cls), _CLEAN_FREEZE)
        assert v["verdict"] == "ESCALATE" and v["glyph"] == "⚖️"


def test_kills_dominate_escalation():
    """A contaminated packet does not get to ESCALATE its way out."""
    v = hal_verdict(_clean_packet(novelty_hypothesis="PATENT_CLAIM"),
                    _DIRTY_FREEZE)
    assert v["verdict"] == "NO_SHIP"


# ── determinism ─────────────────────────────────────────────────────────

def test_hal_is_deterministic():
    a = cp.canon(hal_verdict(_clean_packet(), _CLEAN_FREEZE))
    b = cp.canon(hal_verdict(_clean_packet(), _CLEAN_FREEZE))
    assert a == b
