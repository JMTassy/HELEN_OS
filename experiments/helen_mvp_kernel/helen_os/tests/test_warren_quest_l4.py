"""Executable witness for the L4 Village Cross market packet.

Checks: druid audit inequality, the two-boards price reconciliation
(tau=0 vs tau=0.5 snapshots), communal-compost conservation, and the
curiosity stall's Law-1 mirror rule. Stdlib only. authority=false.
"""

import json
from pathlib import Path

PACKET = Path(__file__).resolve().parents[2] / "warren_quests" / "l4_village_cross.json"


def _load():
    return json.loads(PACKET.read_text(encoding="utf-8"))


def _price(base, sensitivity, tau):
    return round(base * (1.0 + sensitivity * tau))


def test_packet_parses_and_declares_no_authority():
    q = _load()
    assert q["schema"] == "WARREN_QUEST_PACKET_V1"
    assert q["authority"] is False and q["canon"] is False
    assert q["ledger_effect"] == "none"


def test_druid_audit_scenarios_match_law3_inequality():
    q = _load()
    lam = q["economy"]["lambda"]
    for s in q["economy"]["druid_audit"]["scenarios"]:
        allowed = s["wallet"] <= lam * s["composted"] + 1e-9
        assert (s["verdict"] == "TRADE") == allowed, s


def test_two_design_boards_reconcile_as_toxicity_snapshots():
    """Board A (tau=0) vs board B (tau=0.5): the operator's price
    discrepancy is weather, not error — witnessed per item."""
    for item in _load()["price_law"]["items"]:
        assert _price(item["base"], item["sensitivity"], 0.0) == item["tau0_price"], item["id"]
        assert _price(item["base"], item["sensitivity"], 0.5) == item["tau05_price"], item["id"]


def test_communal_compost_conserves_and_respects_law3():
    e = _load()["economy"]
    c = e["communal_compost"]
    mint = e["lambda"] * e["kappa"] * c["berry_basket_w0"]
    assert abs(mint - c["mint_per_basket"]) < 1e-9
    assert abs(c["split"]["player"] + c["split"]["village_fund"] - mint) < 1e-9


def test_curiosity_stall_is_a_mirror_not_a_menu():
    """Every stall item must cite a source event from a prior quest —
    Law 1 sells only what the player's own replay strip contains."""
    stall = _load()["curiosity_stall"]
    known_quests = {"L2_GERALDS_BRIDGE", "L3_STONE_CIRCLE"}
    assert stall["stock"], "empty stall"
    for item in stall["stock"]:
        assert item["from"] in known_quests, item["id"]
    assert "replay strip" in stall["availability"]


def test_garden_booster_subsidy_is_cheapest_relief_when_sick():
    """At high toxicity the booster's low sensitivity makes the cure
    relatively cheaper than vanity goods — design intent, witnessed."""
    items = {i["id"]: i for i in _load()["price_law"]["items"]}
    hat, booster = items["MUSHROOM_HAT"], items["GARDEN_BOOSTER"]
    tau = 1.0
    hat_inflation = _price(hat["base"], hat["sensitivity"], tau) / hat["base"]
    booster_inflation = _price(booster["base"], booster["sensitivity"], tau) / booster["base"]
    assert booster_inflation < hat_inflation
