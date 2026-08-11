"""Falsifiers for HAL pass 2: GATE != INVARIANT demonstrated on three
rungs, compositional admissibility, latent compositions, namespace
semantics, root counting, four-axis novelty — and the board test that
every SHIP verdict cites an executable that actually imports.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "effect_gate"))
sys.path.insert(0, str(_HERE.parent / "crystal_palace"))

import kernel_invariants as ki
from kernel_invariants import (
    BoundedBudget,
    LatentComposition,
    NoveltyDecomposition,
    compose_adjacent,
    compositional_admissibility,
    decode,
    freeze_latent_set,
    independent_roots,
    recommend,
    run_gate_only,
    run_with_invariant,
    witness_composition,
)

# One gated spend, then an ungated "maintenance" path — the coverage hole.
STEPS = ({"amount": 60.0, "gated": True},
         {"amount": 60.0, "gated": False})


# ── GATE != INVARIANT: the three rungs ──────────────────────────────────

def test_rung1_gate_only_reaches_forbidden_state_silently():
    r = run_gate_only(budget=100.0, steps=STEPS)
    assert r["forbidden_state_reached"] is True
    assert r["detected"] is False           # the silence IS the finding


def test_rung1_gate_does_refuse_when_actually_consulted():
    all_gated = tuple({**s, "gated": True} for s in STEPS)
    r = run_gate_only(100.0, all_gated)
    assert r["forbidden_state_reached"] is False   # coverage was total


def test_rung2_invariant_catches_the_same_hole_on_any_path():
    r = run_with_invariant(100.0, STEPS)
    assert r["verdict"] == "E_INVARIANT_VIOLATION"
    assert r["at_step"] == 1 and r["detected"] is True


def test_rung3_the_type_cannot_express_the_forbidden_state():
    with pytest.raises(ValueError, match="E_UNREPRESENTABLE_STATE"):
        BoundedBudget(allocated=100.0, spent=120.0)
    assert BoundedBudget(100.0, 99.0).spent == 99.0


def test_the_ladder_is_ordered():
    assert ki.SAFETY_STRENGTH == ("gated", "invariant_checked",
                                  "structurally_impossible")


# ── LOCAL ⊬ COMPOSITIONAL ──────────────────────────────────────────────

def test_two_valid_leases_compose_into_an_inadmissible_state():
    r = compositional_admissibility(amounts=(60.0, 60.0),
                                    lease_caps=(60.0, 60.0),
                                    shared_budget=100.0)
    assert r["local_admissible"] is True     # each inside its lease
    assert r["compositional_admissible"] is False
    assert r["joint_total"] == 120.0


def test_composition_can_also_be_fine():
    r = compositional_admissibility((30.0, 30.0), (60.0, 60.0), 100.0)
    assert r["local_admissible"] and r["compositional_admissible"]


# ── COMPOSABLE != COMPOSED ─────────────────────────────────────────────

def _latent():
    return compose_adjacent(
        "state_dependent_regulation",
        ("mechanized_measurement", "conditional_automation"),
        interface_map=(("measurement_value", "length_condition"),))


def test_nothing_composed_is_born_witnessed():
    lat = _latent()
    assert lat.status == "ADJACENT_POSSIBLE"
    with pytest.raises(TypeError):
        LatentComposition("x", ("a", "b"), (("o", "i"),),
                          status="WITNESSED")      # init=False: no door


def test_promotion_demands_a_page():
    lat = _latent()
    r = witness_composition(lat)
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_COMPOSABLE_IS_NOT_COMPOSED"
    ok = witness_composition(lat, page_witness="wellcome:531")
    assert ok["verdict"] == "WITNESSED_COMPOSITION"


def test_composition_requires_declared_interface_and_two_motifs():
    with pytest.raises(ValueError, match="E_NO_DECLARED_INTERFACE"):
        compose_adjacent("x", ("a", "b"), ())
    with pytest.raises(ValueError, match="E_NOTHING_TO_COMPOSE"):
        compose_adjacent("x", ("a",), (("o", "i"),))


def test_latent_freeze_is_deterministic_and_all_adjacent():
    a, b = freeze_latent_set((_latent(),)), freeze_latent_set((_latent(),))
    assert a == b and a["all_adjacent_possible"] is True


# ── NO NAMESPACE, NO SEMANTICS ─────────────────────────────────────────

def test_same_movement_different_codebooks_different_symbols():
    m = "left-left-right"
    c1, c2 = {m: "A"}, {m: "B"}
    assert decode(m, c1)["symbol"] == "A"
    assert decode(m, c2)["symbol"] == "B"


def test_movement_alone_decodes_to_nothing():
    r = decode("left-left-right")
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_NO_NAMESPACE"


# ── ROOTS, NOT PASSAGES ────────────────────────────────────────────────

def test_thirty_passages_one_catalogue_one_root():
    ws = tuple({"root": "official_catalogue_1851", "passage": f"p{i}"}
               for i in range(30))
    r = independent_roots(ws)
    assert r["passages"] == 30 and r["independent_roots"] == 1
    ws2 = ws + ({"root": "patent_office_ledger_1852", "passage": "x"},)
    assert independent_roots(ws2)["independent_roots"] == 2


# ── NOVELTY IS FOUR-AXIS ───────────────────────────────────────────────

def test_novelty_axes_never_self_aggregate():
    n = NoveltyDecomposition(0.0, 0.2, 0.9, 0.4)
    with pytest.raises(ValueError, match="E_WEIGHTS_UNDECLARED"):
        n.aggregate({"n_composition": 1.0})
    full = {"n_primitive": 1.0, "n_motif": 1.0, "n_composition": 1.0,
            "n_governance": 1.0}
    assert n.aggregate(full) == pytest.approx(1.5)


# ── MODEL-OPTIMAL != WORLD-ADMISSIBLE ──────────────────────────────────

def test_recommendation_never_executes():
    r = recommend("great-circle course 047",
                  ("ice fields", "prevailing winds"))
    assert r["executes"] is False
    assert r["world_admissibility"] == "UNKNOWN"


# ── the HAL board: every SHIP cites a real executable ──────────────────

def test_her_compost_is_frozen_and_the_board_covers_it():
    import hal_pass2 as hp
    f = hp.freeze_her_pass2()
    assert f["items"] == 12 and f["her_pass2_hash"]
    assert {b["id"] for b in hp.HAL_PASS2_BOARD} == set(range(1, 13))


def test_every_ship_verdict_resolves_to_an_importable_executable():
    """A law that exists only as prose has not shipped."""
    import hal_pass2 as hp
    for b in hp.HAL_PASS2_BOARD:
        if b["verdict"].startswith("SHIP"):
            mod_name, attr = b["executable"].split(":")
            mod = importlib.import_module(mod_name)
            assert hasattr(mod, attr), (b["id"], b["executable"])
        else:
            assert b["executable"] is None and b["missing"]


def test_the_flagged_chiddush_is_a_kernel_correction():
    import hal_pass2 as hp
    item9 = next(b for b in hp.HAL_PASS2_BOARD if b["id"] == 9)
    assert item9["verdict"] == "SHIP_KERNEL_CORRECTION"
    assert "prose never" in item9["note"]
