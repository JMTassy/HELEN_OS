"""Executable witness for the L3 Stone Circle tribunal packet.

Checks: Law 3 tight economy, belief-mints-nothing, sparkle/truth
independence (no shortcut learning), deterministic deck, trial structure.
Stdlib only. NON_SOVEREIGN. authority=false.
"""

import json
from pathlib import Path

PACKET = Path(__file__).resolve().parents[2] / "warren_quests" / "l3_stone_circle.json"


def _load():
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_packet_parses_and_declares_no_authority():
    q = _load()
    assert q["schema"] == "WARREN_QUEST_PACKET_V1"
    assert q["authority"] is False and q["canon"] is False
    assert q["ledger_effect"] == "none"


def test_belief_mints_nothing():
    """Confidence is not correctness is not income."""
    moves = _load()["economy"]["moves"]
    assert moves["BELIEVE"]["mint"] == 0
    assert moves["RESOLVE_TRUE"]["mint"] == 0     # truth pays in carved lessons, not coins
    assert moves["TEST"]["mint"] > 0
    assert moves["RESOLVE_FALSE"]["mint"] > 0     # rejection is compost — and it pays


def test_tested_false_pays_full_deposit():
    """A rigorously-tested false claim composts to completion: full value."""
    e = _load()["economy"]
    full = e["moves"]["TEST"]["mint"] + e["moves"]["RESOLVE_FALSE"]["mint"]
    assert abs(full - e["lambda"] * e["claim_deposit_w0"]) < 1e-9


def test_law3_bound_is_tight_for_max_run():
    q = _load()
    e = q["economy"]
    n = len(q["deck"])
    deposits = n * e["claim_deposit_w0"]
    # max ZOL: every claim tested; false ones resolved (full 10), true ones
    # carved (5 now + permanent lesson). Max COIN run tests everything and
    # composts nothing untested: false claims yield 10, true yield 5.
    n_false = sum(1 for c in q["deck"] if not c["truth"])
    n_true = n - n_false
    max_coin = n_false * 10 + n_true * 5
    assert max_coin <= e["lambda"] * deposits + 1e-9          # Law 3 holds
    # And full composting of everything (the theoretical ceiling) is tight:
    assert abs(e["lambda"] * deposits - n * 10) < 1e-9


def test_sparkle_truth_independence_no_shortcut():
    """The deck must not let players learn 'sparkle = false' (or true).
    All four quadrants of (sparkle-level, truth) must be inhabited."""
    deck = _load()["deck"]
    hi = lambda c: c["sparkle"] >= 4
    quadrants = {
        ("hi", True):  any(hi(c) and c["truth"] for c in deck),
        ("hi", False): any(hi(c) and not c["truth"] for c in deck),
        ("lo", True):  any(not hi(c) and c["truth"] for c in deck),
        ("lo", False): any(not hi(c) and not c["truth"] for c in deck),
    }
    assert all(quadrants.values()), f"missing quadrant: {quadrants}"


def test_deck_is_deterministic_and_complete():
    deck = _load()["deck"]
    ids = [c["id"] for c in deck]
    assert len(ids) == len(set(ids)) == 8
    for c in deck:
        assert isinstance(c["truth"], bool)        # fixed truth: replay-stable
        assert c["test"] and c["reveal"]           # every claim testable + revealable


def test_trial_structure_covers_deck():
    q = _load()
    assert sum(q["trial_structure"]["claims_per_trial"]) == len(q["deck"])
