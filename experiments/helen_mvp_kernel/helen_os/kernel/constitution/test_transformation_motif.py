"""Falsifiers for M, the Transformation Motif — and for batch 2 of the
atlas it draws on. The motif carries no authority; the label mints no
type; the ladder promotes one layer per declared gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "gates" / "effect_gate"))
sys.path.insert(0, str(_HERE.parents[2] / "research" / "crystal_palace"))

import transformation_motif as tm
from effect_gate import Admission
from transformation_motif import (
    Guard,
    TransformationMotif,
    authority_over_consequence,
    compose,
    decompose_self_acting,
    execute_motif,
    layer_promotion,
)


# ── the motif type: complete or nonexistent, and authority-free ─────────

def test_guard_vocabulary_is_closed_and_conditions_required():
    with pytest.raises(ValueError, match="E_UNKNOWN_GUARD_TYPE"):
        Guard("G_vibes", "x > 0")
    with pytest.raises(ValueError, match="E_GUARD_WITHOUT_CONDITION"):
        Guard("G_time", "")


def test_motif_with_missing_field_is_unconstructible():
    with pytest.raises(ValueError, match="E_MOTIF_FIELD_MISSING:reset"):
        TransformationMotif("m", "in", Guard("G_time", "t=t*"),
                            "do", "seen", reset="")


def test_motif_type_has_no_authority_surface():
    m = tm.MOTIF_1851_INSTANCES[0]
    for banned in ("authority", "lease", "admit"):
        assert not any(banned in f for f in m.__dataclass_fields__), banned


# ── the central refusal: E_MOTIF_HAS_NO_AUTHORITY ───────────────────────

def test_mutation_motif_refuses_to_run_bare():
    doffing = tm.MOTIF_1851_INSTANCES[0]           # 1851 ran this bare
    r = execute_motif(doffing, guard_satisfied=True)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_MOTIF_HAS_NO_AUTHORITY"
    assert "not a license" in r["law"]


def test_mutation_motif_runs_under_flow_context():
    doffing = tm.MOTIF_1851_INSTANCES[0]
    r = execute_motif(doffing, True, lease_ref="L1",
                      admission=Admission("jm", "doff"))
    assert r["verdict"] == "EXECUTED_UNDER_FLOW"
    # lease without admission is still not enough
    assert execute_motif(doffing, True, lease_ref="L1")["verdict"] == \
        "REFUSED"


def test_governance_class_is_governed_too():
    interlock = next(m for m in tm.MOTIF_1851_INSTANCES
                     if m.motif_id == "railway_interlock")
    assert execute_motif(interlock, True)["reason"] == \
        "E_MOTIF_HAS_NO_AUTHORITY"


def test_observational_motifs_run_on_their_guard_alone():
    recorder = next(m for m in tm.MOTIF_1851_INSTANCES
                    if m.motif_id == "atmospheric_recording")
    assert execute_motif(recorder, True)["verdict"] == "EXECUTED"
    assert execute_motif(recorder, False)["verdict"] == "IDLE"


# ── composition computes governance, grants none ────────────────────────

def test_compose_flags_governance_without_granting_it():
    f = compose(tm.MOTIF_1851_INSTANCES)
    assert f["governance_required"] is True
    assert "grants none" in f["note"]
    observational_only = tuple(
        m for m in tm.MOTIF_1851_INSTANCES
        if m.effect_class in ("observational", "audit",
                              "decision_support"))
    assert compose(observational_only)["governance_required"] is False


# ── the effect ladder ───────────────────────────────────────────────────

def test_recommendation_ranks_below_mutation():
    course = next(m for m in tm.MOTIF_1851_INSTANCES
                  if m.motif_id == "course_recommendation")
    doffing = tm.MOTIF_1851_INSTANCES[0]
    a, b = authority_over_consequence(course), \
        authority_over_consequence(doffing)
    assert a["rank"] < b["rank"]          # COMPUTE/RECOMMEND != EXECUTE
    assert "NOT a rudder mutation" in course.observable


def test_governance_and_audit_sit_beside_the_ladder():
    for mid, role in (("railway_interlock", "restricts"),
                      ("autochronograph_stamp", "records")):
        m = next(x for x in tm.MOTIF_1851_INSTANCES if x.motif_id == mid)
        v = authority_over_consequence(m)
        assert v["on_ladder"] is False and role in v["role"]


# ── SELF-ACTING types nothing ───────────────────────────────────────────

def test_the_label_alone_mints_no_motif():
    r = decompose_self_acting("self-acting mule")
    assert r["verdict"] == "CANDIDATE_LABEL_ONLY"
    assert r["reason"] == "E_LABEL_IS_NOT_A_TYPE"
    assert set(r["missing_fields"]) == {
        "trigger", "state_sensed", "transition", "effect", "reset"}


def test_five_witnessed_fields_mint_the_motif():
    r = decompose_self_acting(
        "duplex lathe return", trigger=Guard("G_threshold", "cut done"),
        state_sensed="tool position", transition="quick return",
        effect="tool at start", reset="advance feed",
        witness="wellcome:546")
    assert r["verdict"] == "DECOMPOSED"
    assert r["motif"].guard.guard_type == "G_threshold"


# ── the five-layer ladder: one layer, one declared gate ─────────────────

def test_layer_skip_is_refused():
    r = layer_promotion("possible", "implemented", gate={})
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_LAYER_SKIP"


def test_no_gate_no_propagation():
    assert layer_promotion("implemented", "authorized", None)["reason"] \
        == "E_NO_GATE"


def test_gate_must_declare_all_four_fields():
    partial = {"information_loss": "detail dropped",
               "authority_gain": "none"}
    r = layer_promotion("conceived", "implemented", partial)
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_GATE_UNDECLARED"
    assert set(r["missing"]) == {"assumptions_added", "reversibility"}
    full = {**partial, "assumptions_added": "prototype = design",
            "reversibility": "reversible"}
    assert layer_promotion("conceived", "implemented",
                           full)["verdict"] == "PROMOTED"


# ── batch 2 of the atlas ────────────────────────────────────────────────

def test_batch2_freezes_with_lineage_to_batch1():
    import atlas_v1_batch2 as b2
    r = b2.freeze_batch2()
    assert r["candidate_count"] == 6
    assert r["contamination"] == ()
    assert r["predecessor_freeze_hash"] == \
        __import__("atlas_v0").freeze_batch1()["freeze_hash"]
    assert r["exclusion_lifted"] == ("sensor_to_record",)


def test_dollond_entered_with_its_contradiction_on_record():
    import atlas_v1_batch2 as b2
    ids = {m.motif_id for m in b2.MOTIFS_B2}
    assert "sensor_to_record" in ids
    rec = b2.FRAMES_B2["CP-DOLLOND"]
    assert any("unresolved" in c for c in rec.contradictions)


def test_the_building_stays_outside_the_vol1_atlas():
    import atlas_v1_batch2 as b2
    from crystal_palace import atlas_scope_check
    palace = b2.PALACE_MOTIFS[0]
    r = atlas_scope_check("vol1", palace)
    assert r["verdict"] == "REJECT" and r["reason"] == "E_CORPUS_BOUNDARY"
    assert palace.motif_id not in {m.motif_id for m in b2.all_motifs()}


def test_every_hal_ship_item_maps_to_a_frozen_motif():
    import atlas_v1_batch2 as b2
    frozen = {m.motif_id for m in b2.all_motifs()}
    for claim, motif_id in b2.HAL_SHIP.items():
        assert motif_id in frozen, (claim, motif_id)
    assert len(b2.HAL_SHIP) == 10
    assert len(b2.HAL_HOLD) == 4 and len(b2.HAL_NO_SHIP) == 5


def test_every_1851_motif_instance_cites_an_atlas_frame():
    import atlas_v1_batch2 as b2
    in_frame = b2.C_VOL1_B2.pages_in_frame
    for m in tm.MOTIF_1851_INSTANCES:
        assert m.witness in in_frame, m.motif_id


# ── determinism ─────────────────────────────────────────────────────────

def test_deterministic():
    import atlas_v1_batch2 as b2
    assert tm.canon(b2.freeze_batch2()) == tm.canon(b2.freeze_batch2())
    assert tm.canon(compose(tm.MOTIF_1851_INSTANCES)) == \
        tm.canon(compose(tm.MOTIF_1851_INSTANCES))
