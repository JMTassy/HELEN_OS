"""Falsifiers for the ceiling algebra and T000: cardinality-not-assumed,
Merge as a governed transition, provenance-quotient cardinality, the
three-ceiling Admit predicate, and RELAY != DIRECTLY_OBSERVED.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
from ceiling_algebra import (
    HistoricalSource,
    Receipt,
    Transition,
    admit,
    directly_observed,
    effect_within_scope,
    independent_cardinality,
    propose_merge,
    vessel_cardinality,
)


# ── RELAY != DIRECTLY_OBSERVED ─────────────────────────────────────────

def test_a_relayed_source_is_not_directly_observed():
    s = HistoricalSource("hca", "TNA notice", "RELAYED")
    assert directly_observed(s)["directly_observed"] is False
    assert directly_observed(s)["ceiling"] == "RELAYED"


def test_a_direct_source_clears_the_ceiling():
    s = HistoricalSource("scan", "IIIF", "DIRECT")
    assert directly_observed(s)["directly_observed"] is True


def test_unknown_access_mode_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNKNOWN_ACCESS_MODE"):
        HistoricalSource("x", "p", "GUESSED")


# ── T000: cardinality is not assumed ───────────────────────────────────

def test_two_identity_claims_do_not_collapse_to_one_vessel():
    claims = ({"hull_ref": "hull_A"}, {"hull_ref": "hull_B"})
    r = vessel_cardinality(claims)
    assert r["cardinality"] == 2
    assert r["assumed_one"] is False
    assert r["witnessed_merges"] == []


def test_a_continuity_witness_permits_a_merge():
    claims = ({"hull_ref": "hull_A"}, {"hull_ref": "hull_B"})
    w = ({"kind": "physical_continuity", "from": "hull_A",
          "to": "hull_B", "witness_ref": "survey#7"},)
    r = vessel_cardinality(claims, w)
    assert r["witnessed_merges"] == [["hull_A", "hull_B"]]


def test_even_one_claim_is_not_asserted_as_the_only_one():
    r = vessel_cardinality(({"hull_ref": "hull_A"},))
    assert r["assumed_one"] is False    # T000: never assume |Vessel|=1


# ── Merge as a governed transition ─────────────────────────────────────

@pytest.mark.parametrize("basis", ["same_name", "same_master",
                                   "credential_carried",
                                   "same_name+credential_carried"])
def test_no_cheap_basis_licenses_a_merge(basis):
    r = propose_merge("hull_A", "hull_B", basis)
    assert r["verdict"] == "REJECT"
    assert r["reason"] == "E_UNWITNESSED_MERGE"
    assert "graph rewriting, not preprocessing" in r["law"]


def test_a_continuity_witness_admits_the_merge():
    r = propose_merge("hull_A", "hull_B", "physical_continuity",
                      {"witness_ref": "log-continuity#3"})
    assert r["verdict"] == "MERGE_ADMITTED"


def test_merge_runs_as_a_transition_not_a_silent_preprocess():
    # an unknown basis HOLDs — it does not silently pass through
    assert propose_merge("a", "b", "gut_feeling")["verdict"] == "HOLD"


# ── provenance-quotient cardinality (T007 generalized) ─────────────────

def test_three_derived_artifacts_are_one_independent_root():
    arts = ({"artifact_id": "orig", "sha256": "h1", "evidence_root": "R"},
            {"artifact_id": "translation", "sha256": "h2",
             "evidence_root": "R"},
            {"artifact_id": "abstract", "sha256": "h3",
             "evidence_root": "R"})
    r = independent_cardinality(arts)
    assert r["n_artifact"] == 3 and r["n_hash"] == 3
    assert r["n_independent"] == 1
    assert "differing hash never proves" in r["law"]


def test_distinct_roots_count_independently():
    arts = ({"artifact_id": "a", "sha256": "h1", "evidence_root": "R1"},
            {"artifact_id": "b", "sha256": "h2", "evidence_root": "R2"})
    assert independent_cardinality(arts)["n_independent"] == 2


# ── the three-ceiling Admit predicate ──────────────────────────────────

_R = Receipt("r1", proof_ceiling=frozenset({"root_X"}),
             scope_ceiling=frozenset({"hull_B"}),
             authority_ceiling="ADJUDICATED")


def _delta(proof=("root_X",), effect=("hull_B",), auth="ADJUDICATED",
           replay=True):
    return Transition("d", frozenset(proof), frozenset(effect), auth,
                      replay)


def test_a_transition_within_all_three_ceilings_admits():
    assert admit(_delta(), _R)["verdict"] == "ADMIT"


def test_proof_beyond_the_ceiling_is_rejected():
    r = admit(_delta(proof=("root_X", "root_Y")), _R)
    assert r["verdict"] == "REJECT"
    assert r["breaches"][0]["reason"] == "E_PROOF_CEILING_EXCEEDED"
    assert r["breaches"][0]["over"] == ["root_Y"]


def test_effect_beyond_scope_is_rejected():
    r = admit(_delta(effect=("hull_B", "all_cargo")), _R)
    assert any(b["reason"] == "E_SCOPE_CEILING_EXCEEDED"
               for b in r["breaches"])


def test_authority_beyond_ceiling_is_rejected():
    r = admit(_delta(auth="ADMITTED"), _R)
    assert any(b["reason"] == "E_AUTHORITY_CEILING_EXCEEDED"
               for b in r["breaches"])


def test_replay_invalid_preconditions_are_rejected():
    r = admit(_delta(replay=False), _R)
    assert any(b["reason"] == "E_PRECONDITIONS_NOT_REPLAY_VALID"
               for b in r["breaches"])


def test_multiple_breaches_are_all_reported():
    r = admit(_delta(proof=("root_Z",), effect=("all_cargo",),
                     auth="ADMITTED", replay=False), _R)
    reasons = {b["reason"] for b in r["breaches"]}
    assert len(reasons) == 4               # all four ceilings named


# ── the eight oracles are one algebra ──────────────────────────────────

def test_every_oracle_maps_to_a_ceiling():
    m = ca.ORACLE_CEILING_MAP
    assert len(m) == 8
    assert set(m.values()) == {"PROOF", "SCOPE", "AUTHORITY"}
    assert m["E_PARTIAL_VERDICT_SCOPE"] == "SCOPE"
    assert m["E_PHYSICAL_EFFECT_IS_NOT_LEGALITY"] == "AUTHORITY"


def test_effect_within_scope_is_the_general_partial_verdict_law():
    assert effect_within_scope(frozenset({"hull_B"}), "all_cargo")[
        "reason"] == "E_OUT_OF_SCOPE"
    assert effect_within_scope(frozenset({"hull_B"}), "hull_B")[
        "verdict"] == "IN_SCOPE"


def test_deterministic():
    assert ca.canon(admit(_delta(), _R)) == ca.canon(admit(_delta(), _R))
