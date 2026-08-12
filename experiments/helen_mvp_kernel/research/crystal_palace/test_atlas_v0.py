"""Falsifiers for batch 1 of the motif atlas — the delivered frames,
the motif layer, T11, the corpus boundary, and the two-lane freeze.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import atlas_v0 as av
import crystal_palace as cp
from crystal_palace import (
    CompostPacket,
    GraphEdge,
    GraphNode,
    Motif,
    Tau,
    atlas_scope_check,
    hal_verdict,
    her_read_page,
    promote_motif,
    rv_re,
    t11_authority_gravity,
)


# ── the frames read; the rest of the volume stays dark ──────────────────

def test_delivered_frames_read_through_the_gate():
    for key, rec in av.FRAMES.items():
        r = her_read_page(av.C_VOL1, rec.page_id, rec)
        assert r["status"] == "READ", key


def test_undelivered_canvases_stay_unknown():
    assert her_read_page(av.C_VOL1, "wellcome:528")["status"] == "UNKNOWN"
    assert her_read_page(av.C_VOL1, "wellcome:100")["status"] == "UNKNOWN"


def test_page_identity_is_frame_indexed():
    """The same volume is 772 Wellcome canvases and 842 IA images.
    'ia:546' is not 'wellcome:546' — a frame-unqualified id reads
    nothing."""
    assert her_read_page(av.C_VOL1, "ia:546")["status"] == "UNKNOWN"
    assert her_read_page(av.C_VOL1, "546")["status"] == "UNKNOWN"


# ── C13 on the crossing: relayed reads cap at REPORTED ──────────────────

def test_every_motif_is_reported_here_never_observed():
    for m in av.MOTIFS:
        assert m.grade == "REPORTED", m.motif_id     # ObservedThere ⊬ Here
    assert av.PROVENANCE["grade_cap"] == "REPORTED"


def test_motif_without_witness_frames_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNWITNESSED_MOTIF"):
        Motif("floating", ("a", "b"), witness_frames=())


# ── analogy is not lineage: every forbidden promotion refuses ───────────

def test_each_motif_refuses_its_forbidden_promotions():
    tried = 0
    for m in av.MOTIFS:
        for target in m.forbidden_promotions:
            r = promote_motif(m, target)
            assert r["verdict"] == "REFUSED"
            assert r["reason"] == "E_ANALOGY_IS_NOT_LINEAGE"
            tried += 1
    assert tried >= 6
    # the specific promotions the relay named
    scc = next(m for m in av.MOTIFS if m.motif_id == "source_channel_code")
    assert promote_motif(scc, "Shannon information theory")["verdict"] == \
        "REFUSED"


# ── the corpus boundary: the arithmometer stays outside ─────────────────

def test_vol2plus_witness_never_enters_the_vol1_atlas():
    arithmometer = Motif("stepped_reckoner_calculation",
                         ("digits_in", "mechanism", "digits_out"),
                         witness_frames=("bibliographic:arithmometer",),
                         corpus_scope="vol2plus")
    r = atlas_scope_check("vol1", arithmometer)
    assert r["verdict"] == "REJECT" and r["reason"] == "E_CORPUS_BOUNDARY"
    for m in av.MOTIFS:
        assert atlas_scope_check("vol1", m)["verdict"] == "IN_SCOPE"


def test_dollond_is_excluded_pending_direct_witness():
    """Sensor->record is real but its page is witnessed only through a
    Smithsonian citation — it is NOT in batch 1."""
    ids = {m.motif_id for m in av.MOTIFS}
    assert "sensor_to_record" not in ids
    assert "sensor_to_record" in av.EXCLUDED_PENDING_DIRECT_WITNESS


# ── T11 AUTHORITY_GRAVITY: the new kernel test, verbatim ────────────────

def test_t11_coherence_never_raises_authority():
    nodes = {"telegraph": GraphNode("telegraph", "REPORTED",
                                    pages=("wellcome:699",)),
             "self_acting": GraphNode("self_acting", "REPORTED",
                                      pages=("wellcome:546",))}
    edge = GraphEdge("telegraph", "self_acting",
                     "jointly_suggest_autonomous_information_machine",
                     basis="on_page", grade="INFERRED")
    n_coherent = tuple(f"coherent_observation_{i}" for i in range(40))
    r = t11_authority_gravity(edge, nodes, n_coherent)
    assert r["verdict"] == "REJECT_INDEPENDENT_WITNESS_MISSING"
    assert r["gamma"] == 40
    assert r["authority_after"] == r["authority_before"] == "INFERRED"


def test_t11_refusal_is_unconditional_on_n():
    nodes = {"a": GraphNode("a", "REPORTED", pages=("p",)),
             "b": GraphNode("b", "REPORTED", pages=("p",))}
    e = GraphEdge("a", "b", "r", basis="on_page", grade="INFERRED")
    for n in (0, 1, 1000):
        r = t11_authority_gravity(e, nodes, tuple(range(n)))
        assert r["verdict"] == "REJECT_INDEPENDENT_WITNESS_MISSING"


# ── the two lanes ───────────────────────────────────────────────────────

def test_descriptive_freeze_is_clean_and_deterministic():
    a, b = av.freeze_batch1(), av.freeze_batch1()
    assert a["freeze_hash"] == b["freeze_hash"]
    assert a["candidate_count"] == 6
    assert a["contamination"] == ()


def test_blind_lane_is_contaminated_in_this_seat_and_says_so():
    s = av.blind_lane_status()
    assert s["contaminated"] is True
    assert len(s["receipt"]["contamination"]) == 2
    # and the statistic refuses to compute from this seat
    assert rv_re(1, 1, 1, 1, s["receipt"])["status"] == "UNKNOWN"


def test_rm_joins_the_statistic_under_a_clean_freeze():
    clean = av.freeze_batch1()
    m = rv_re(9, 10, 3, 10, clean, recovered_m=7, total_m=10)
    assert m["status"] == "MEASURED"
    assert m["R_M"] == 0.7 and m["R_V"] == 0.9 and m["R_E"] == 0.3


# ── HAL on the batch: existence ships, classification does not ──────────

def _cp527_existence_packet():
    return CompostPacket(
        candidate_id="motif-conditional-automation-exists",
        supporting_pages=("wellcome:527",),
        primitive_nodes=(GraphNode("sliver_lap_machine", "REPORTED",
                                   pages=("wellcome:527",)),),
        inferred_edges=(GraphEdge("length_condition", "automatic_action",
                                  "triggers_when_unattended",
                                  basis="on_page", grade="REPORTED"),),
        explicit_vs_inferred={
            "explicit": ("bell rings at required length; unattended lap "
                         "is automatically doffed",),
            "inferred": ("the condition acts as a threshold",)},
        temporal_provenance=(("q1", Tau(t_source="1851",
                                        t_record="2026-08-11"), "UNKNOWN"),),
        information_loss="gears, textile mechanics, timing, operator "
                         "context dropped in motif abstraction",
        assumptions_added=("'required length' treated as a state "
                           "condition",),
        leakage_risk="NONE",
        novelty_hypothesis="INSIGHT",
        falsifier={"statement": "the canvas text does not contain the "
                                "conditional structure",
                   "executed": True, "survived": True})


def test_hal_ships_the_existence_claim():
    v = hal_verdict(_cp527_existence_packet(), av.freeze_batch1())
    assert v["verdict"] == "SHIP_INSIGHT"
    assert v["admits"] is False


def test_hal_holds_the_feedback_control_classification():
    """The deeper claim's falsifier (measured state vs fixed sequence)
    is DECLARED but unexecuted — CP-527's missing witness. HAL holds."""
    import dataclasses
    p = dataclasses.replace(
        _cp527_existence_packet(),
        candidate_id="motif-is-feedback-control",
        falsifier={"statement": "automatic action depends on measured "
                                "process state, not fixed sequence",
                   "executed": False, "survived": False})
    v = hal_verdict(p, av.freeze_batch1())
    assert v["verdict"] == "HOLD"
    assert v["missing"] == ["F_falsifier_survived"]


def test_hal_no_ships_the_batch_under_the_blind_lane_receipt():
    """The same packet dies if presented as prediction-lane work from
    this seat — kills dominate."""
    v = hal_verdict(_cp527_existence_packet(),
                    av.blind_lane_status()["receipt"])
    assert v["verdict"] == "NO_SHIP"
    assert "K1_FUTURE_DATA_BEFORE_FREEZE" in v["kill_conditions"]


# ── determinism of the whole batch ──────────────────────────────────────

def test_atlas_receipt_is_reproducible():
    assert cp.canon(av.freeze_batch1()) == cp.canon(av.freeze_batch1())
