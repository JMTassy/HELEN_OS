"""Falsifiers for the ONE_SHIP gold harness: the three new joins, typed
transfer, evidence-root census, and the 8 gold oracles each routed to
its enforcer. Vessel facts are relayed fixtures; oracle labels come
from constitutional rules.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import one_ship_gold as osg
from one_ship_gold import (
    Artifact,
    TypedTransfer,
    adjudicate,
    evidence_census,
    independent_roots_claim,
    propagate_verdict,
    run_gold_suite,
    same_entity,
    transfer_implies,
    verdict_of,
)


# ── the 8 gold oracles ──────────────────────────────────────────────────

def test_all_eight_gold_oracles_hold():
    r = run_gold_suite()
    assert r["all_held"] is True, r["failed"]
    assert r["total"] == 8 and r["passed"] == 8


@pytest.mark.parametrize("oracle", osg.GOLD_ORACLES,
                         ids=[o["id"] for o in osg.GOLD_ORACLES])
def test_each_oracle_routes_to_a_real_enforcer(oracle):
    r = adjudicate(oracle)
    assert r["gate"] == "REJECT" == r["expected"]
    assert r["passed"] is True


def test_the_reason_codes_are_the_eight_expected():
    codes = {o["reason"] for o in osg.GOLD_ORACLES}
    assert codes == {
        "E_PHYSICAL_EFFECT_IS_NOT_LEGALITY",
        "E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP",
        "E_CARGO_IS_NOT_OWNERSHIP",
        "E_INTERCEPTED_IS_NOT_DELIVERED",
        "E_CROSS_LAYER_LAUNDERING",
        "E_PARTIAL_VERDICT_SCOPE",
        "E_DERIVED_DOC_IS_NOT_NEW_WITNESS",
        "E_NAME_IS_NOT_IDENTITY"}


# ── E_NAME_IS_NOT_IDENTITY ──────────────────────────────────────────────

def test_same_name_and_carried_pass_do_not_make_one_hull():
    for basis in ("same_name", "carried_pass",
                  "same_name+carried_pass"):
        r = same_entity({"id": "hull_A"}, {"id": "hull_B"}, basis)
        assert r["reason"] == "E_NAME_IS_NOT_IDENTITY"
        assert r["identity_state"] == "CONTESTED_OR_COMPOSITE"


def test_physical_continuity_witness_can_establish_identity():
    r = same_entity({"id": "a"}, {"id": "b"},
                    "physical_continuity_witness")
    assert r["verdict"] == "SAME_ENTITY"


# ── E_PARTIAL_VERDICT_SCOPE ─────────────────────────────────────────────

def test_a_scoped_verdict_reads_per_object():
    v = {"hull_B": "CONDEMNED", "cargo_subset_B": "RESTORED"}
    assert verdict_of(v, "hull_B")["decision"] == "CONDEMNED"
    assert verdict_of(v, "cargo_subset_B")["decision"] == "RESTORED"


def test_there_is_no_global_case_verdict():
    v = {"hull_B": "CONDEMNED", "cargo_subset_B": "RESTORED"}
    r = verdict_of(v, "__case_global__")
    assert r["reason"] == "E_PARTIAL_VERDICT_SCOPE"


def test_condemnation_does_not_propagate_to_cargo():
    r = propagate_verdict({"hull_B": "CONDEMNED"}, "hull_B", "all_cargo")
    assert r["reason"] == "E_PARTIAL_VERDICT_SCOPE"


# ── E_DERIVED_DOC_IS_NOT_NEW_WITNESS ────────────────────────────────────

def test_a_translation_shares_the_originals_evidence_root():
    orig = Artifact("orig", "h1", evidence_root_id="root_X")
    trans = Artifact("trans", "h2", derived_from="orig",
                     evidence_root_id="root_X")
    r = independent_roots_claim(orig, trans)
    assert r["reason"] == "E_DERIVED_DOC_IS_NOT_NEW_WITNESS"
    assert r["n_root"] == 1


def test_the_root_hash_artifact_ordering_holds():
    arts = (Artifact("a", "h1", evidence_root_id="r"),
            Artifact("b", "h2", derived_from="a", evidence_root_id="r"),
            Artifact("c", "h1", evidence_root_id="r"))   # exact dup of a
    r = evidence_census(arts)
    assert r["n_artifact"] == 3 and r["n_hash"] == 2 and r["n_root"] == 1
    assert r["ordering_holds"] is True


def test_genuinely_independent_docs_have_distinct_roots():
    a = Artifact("a", "h1", evidence_root_id="root1")
    b = Artifact("b", "h2", evidence_root_id="root2")
    assert independent_roots_claim(a, b)["n_root"] == 2


# ── typed transfer: custody != title ───────────────────────────────────

def test_accepting_custody_does_not_move_title():
    t = TypedTransfer("t1", "custody", "lot_17", "A", "B")
    assert t.accept("B", "receipt:custody:17")["verdict"] == "ACCEPTED"
    # custody moved
    assert transfer_implies(t, "custody")["verdict"] == "MOVED"
    # but title did NOT
    r = transfer_implies(t, "title")
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_TRANSFER_KIND_MISMATCH"


def test_a_proposed_transfer_is_not_completed():
    t = TypedTransfer("t2", "title", "lot_18", "A", "B")
    assert transfer_implies(t, "title")["reason"] == \
        "E_TRANSFER_NOT_COMPLETED"


def test_acceptance_needs_the_right_party_and_a_receipt():
    t = TypedTransfer("t3", "custody", "x", "A", "B")
    assert t.accept("C", "r")["reason"] == "E_WRONG_ACCEPTOR"
    assert t.accept("B", "")["reason"] == "E_NO_ACCEPTANCE_RECEIPT"


def test_unknown_transfer_kind_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNKNOWN_TRANSFER_KIND"):
        TypedTransfer("t", "vibes", "x", "A", "B")


# ── the relayed fixture is marked, not asserted as fact ────────────────

def test_the_vessel_fixture_declares_its_relayed_grade():
    f = osg.VESSEL_FIXTURE
    assert f["source_grade"] == "REPORTED"
    assert "NOT portal-read" in f["source"]
    assert "NOT_CONFIRMED_IN_ACCESSED_CORPUS" in f["missing"]
    # two hulls, by construction — ONE_SHIP refuses to assume one
    assert len(f["hulls"]) == 2


def test_deterministic():
    assert osg.canon(run_gold_suite()) == osg.canon(run_gold_suite())
