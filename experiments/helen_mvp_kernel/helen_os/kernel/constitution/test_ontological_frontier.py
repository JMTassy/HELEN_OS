"""EPIS-CYCLE-ONT-01, falsified: the proposer may not discharge its own
obligation (the one attack every predicate-shaped check in this
codebase passes); Qwen mints no witness by compressing; a representation
holds no referent status until r* is crossed; and Gamma grows on
discharged crossings, never on epochs, proposals or agreement.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import ontological_frontier as of
from ontological_frontier import (
    compression_is_not_evidence,
    cross,
    crossing_obligation,
    discharge,
    epoch,
    gamma_growth,
    generator_independence,
    inherits_status,
    role_may,
    terminate,
)


def _ob(**over):
    f = {"claim": "CSH-X was built to the published plan",
         "referent": "CSH-X",
         "required_witness": "construction photograph with provenance",
         "created_by": "HER"}
    f.update(over)
    return crossing_obligation(**f)


# ── role isolation ─────────────────────────────────────────────────────

def test_each_role_holds_exactly_the_powers_it_was_granted():
    assert role_may("HER", "propose")["licensed"] is True
    assert role_may("HAL_F", "attack")["licensed"] is True
    assert role_may("HAL_W", "witness")["licensed"] is True
    assert role_may("HAL_X", "cross")["licensed"] is True
    assert role_may("QWEN", "compress")["licensed"] is True


def test_the_generator_may_not_witness_attack_or_cross():
    for p in ("attack", "witness", "cross", "compress"):
        v = role_may("HER", p)
        assert v["licensed"] is False
        assert v["reason"] == "E_ROLE_LACKS_POWER"


def test_the_witness_supplies_and_does_not_decide():
    assert role_may("HAL_W", "cross")["licensed"] is False


def test_the_gate_may_not_propose_or_witness_its_own_case():
    assert role_may("HAL_X", "propose")["licensed"] is False
    assert role_may("HAL_X", "witness")["licensed"] is False


def test_only_the_gate_is_promotional():
    promotional = [r for r, p in of.ROLES.items() if p["promotional"]]
    assert promotional == ["HAL_X"]


def test_unknown_roles_and_powers_are_refused():
    assert role_may("GPT", "cross")["reason"] == "E_UNKNOWN_ROLE"
    assert role_may("HER", "vibes")["reason"] == "E_UNKNOWN_POWER"


def test_compression_mints_no_witness():
    v = compression_is_not_evidence("QWEN", before=40000, after=2000)
    assert v["ok"] is True
    assert v["witnesses_added"] == 0
    assert v["promotional"] is False


def test_a_non_compressor_may_not_compress():
    assert compression_is_not_evidence("HAL_X", 10, 5)["reason"] == \
        "E_ROLE_LACKS_POWER"


# ── the debt, and the debtor who may not be the creditor ───────────────

def test_an_obligation_is_created_open_on_the_representation_side():
    ob = _ob()
    assert ob["ok"] is True
    assert ob["state"] == of.OPEN
    assert ob["side"] == of.REPRESENTATION


def test_an_obligation_that_cannot_name_its_witness_is_refused():
    v = crossing_obligation(claim="c", referent="r", created_by="HER")
    assert v["ok"] is False and v["reason"] == "E_UNTYPED_OBLIGATION"
    assert v["missing"] == ["required_witness"]


def test_a_role_without_propose_cannot_create_an_obligation():
    assert _ob(created_by="QWEN")["reason"] == "E_ROLE_LACKS_POWER"


def test_the_proposer_may_not_discharge_its_own_obligation():
    """THE attack of this module. Every four-part predicate in
    vision_ir would return True here: the witness exists, the medium is
    classified, the bridge is named. Only the identity check refuses."""
    v = discharge(_ob(), by="HER", witness="photo:AA_1950_p31")
    assert v["discharged"] is False
    assert v["reason"] == "E_SELF_DISCHARGE"


def test_the_role_table_alone_already_blocks_the_fused_role():
    """HAL_X cannot even open an obligation, so the two powers never
    meet through the constructor."""
    assert _ob(created_by="HAL_X")["reason"] == "E_ROLE_LACKS_POWER"


def test_the_identity_check_is_independent_of_the_role_table():
    """The falsifier that matters: hand-build the state a fused
    propose+cross role would produce, bypassing the constructor. If
    self-discharge were only prevented by the role table, this would
    pass — separation of powers would be a table entry, not a law."""
    fused = {"ok": True, "state": of.OPEN, "side": of.REPRESENTATION,
             "claim": "c", "referent": "r", "required_witness": "w",
             "created_by": "HAL_X"}
    v = discharge(fused, by="HAL_X", witness="a real witness")
    assert v["discharged"] is False
    assert v["reason"] == "E_SELF_DISCHARGE"


def test_a_second_gate_could_lawfully_discharge_that_same_obligation():
    """The positive control on the identity check: it refuses SELF,
    not the act. Otherwise 'never discharge anything' would score
    perfectly."""
    fused = {"ok": True, "state": of.OPEN, "side": of.REPRESENTATION,
             "claim": "c", "referent": "r", "required_witness": "w",
             "created_by": "HER"}
    v = discharge(fused, by="HAL_X", witness="a real witness")
    assert v["discharged"] is True


def test_a_role_without_crossing_power_may_not_discharge():
    assert discharge(_ob(), by="HAL_F", witness="w")["reason"] == \
        "E_ROLE_LACKS_POWER"


def test_discharge_by_assertion_is_refused():
    v = discharge(_ob(), by="HAL_X", witness=None)
    assert v["discharged"] is False
    assert v["reason"] == "E_UNDISCHARGED_CROSSING"


def test_a_witness_from_a_role_that_cannot_witness_is_refused():
    v = discharge(_ob(), by="HAL_X", witness="w",
                  witness_supplied_by="QWEN")
    assert v["reason"] == "E_ROLE_LACKS_POWER"


def test_the_lawful_discharge_needs_three_distinct_roles():
    v = discharge(_ob(), by="HAL_X", witness="photo:AA_1950_p31",
                  witness_supplied_by="HAL_W")
    assert v["discharged"] is True
    assert v["state"] == of.DISCHARGED
    assert v["discharged_by"] == "HAL_X"
    assert v["witness_supplied_by"] == "HAL_W"


def test_a_refuted_crossing_is_closed_and_that_is_a_result():
    v = terminate(_ob(), by="HAL_F",
                  refutation="the plan was revised after the shoot")
    assert v["terminated"] is True and v["state"] == of.TERMINATED


def test_only_the_attacker_may_terminate():
    assert terminate(_ob(), by="HAL_X", refutation="x")["reason"] == \
        "E_ROLE_LACKS_POWER"


# ── r*: the frontier ───────────────────────────────────────────────────

def test_a_representation_holds_no_referent_status_before_crossing():
    v = inherits_status("drawing of CSH-X", "EXISTED_1950",
                        crossed=False)
    assert v["inherited_status"] is None
    assert v["reason"] == "E_INHERITED_WITHOUT_CROSSING"


def test_an_undischarged_obligation_holds_at_the_frontier():
    ob = _ob()
    bad = discharge(ob, by="HER", witness="w")          # self-discharge
    v = cross(ob, bad, by="HAL_X")
    assert v["verdict"] == of.HOLD
    assert v["crossed"] is False
    assert v["side"] == of.REPRESENTATION
    assert v["reason"] == "E_INHERITED_WITHOUT_CROSSING"
    assert v["blocked_by"] == "E_SELF_DISCHARGE"


def test_a_discharged_obligation_crosses():
    ob = _ob()
    ok = discharge(ob, by="HAL_X", witness="photo:AA_1950_p31",
                   witness_supplied_by="HAL_W")
    v = cross(ob, ok, by="HAL_X")
    assert v["verdict"] == of.PROMOTE
    assert v["crossed"] is True
    assert v["side"] == of.INSTANTIATION
    assert v["witness"] == "photo:AA_1950_p31"


def test_no_other_role_may_stand_at_the_frontier():
    ob = _ob()
    ok = discharge(ob, by="HAL_X", witness="w")
    for r in ("HER", "HAL_F", "HAL_W", "QWEN"):
        v = cross(ob, ok, by=r)
        assert v["crossed"] is False
        assert v["verdict"] == of.TERMINATE
        assert v["reason"] == "E_ROLE_LACKS_POWER"


# ── the epoch, and what Gamma is allowed to do ─────────────────────────

def test_an_epoch_yields_pre_claims_and_promotes_nothing():
    v = epoch(k=7, proposals=12, attacks=12, discharged=0)
    assert v["ok"] is True
    assert v["pre_claims"] == 12
    assert v["canon_promoted_by_this_epoch"] == 0


def test_an_epoch_cannot_discharge_more_than_it_proposed():
    assert epoch(1, proposals=3, attacks=3, discharged=4)["reason"] == \
        "E_MORE_DISCHARGED_THAN_PROPOSED"


def test_negative_counts_are_refused():
    with pytest.raises(ValueError, match="E_NEGATIVE_COUNT"):
        epoch(1, -1, 0, 0)
    with pytest.raises(ValueError, match="E_NEGATIVE_COUNT"):
        gamma_growth(-1, 0, 0)


def test_forty_epochs_of_exploration_buy_no_canon():
    v = gamma_growth(epochs=40, proposals=480,
                     discharged_crossings=0)
    assert v["d_gamma_d_exploration"] == 0
    assert v["gamma_growth_licensed"] == 0


def test_a_discharged_crossing_is_the_only_thing_that_grows_gamma():
    v = gamma_growth(epochs=40, proposals=480,
                     discharged_crossings=2)
    assert v["gamma_growth_licensed"] == 2
    assert v["d_gamma_d_exploration"] == 0


def test_gamma_constant_in_time_is_named_as_a_misreading():
    """A canon that can never grow cannot learn — paralysis dressed as
    safety, the defect proof_ceiling's positive control exists for."""
    v = gamma_growth(1, 1, 1)
    assert v["bound"] == "d|Gamma|/d|G| = 0"
    assert v["misreading_refused"] == "|Gamma| constant in time"


def test_twelve_proposals_from_one_model_are_one_generator():
    v = generator_independence(proposals=12, n_generators=1)
    assert v["N_effective_on_hypotheses"] == 1
    assert v["independence_licensed"] is False
    assert v["reason"] == "E_SINGLE_GENERATOR"


def test_distinct_generators_do_buy_independence():
    v = generator_independence(proposals=12, n_generators=3)
    assert v["N_effective_on_hypotheses"] == 3
    assert v["independence_licensed"] is True


def test_effective_count_never_exceeds_the_proposal_count():
    assert generator_independence(2, 9)["N_effective_on_hypotheses"] \
        == 2


def test_no_proposals_is_refused():
    with pytest.raises(ValueError, match="E_NO_PROPOSALS"):
        generator_independence(0, 1)


def test_deterministic():
    assert of.canon(gamma_growth(40, 480, 2)) == \
        of.canon(gamma_growth(40, 480, 2))
