"""The reframe, checked: every HELEN construct reduces to a plain FABLE
rule or is named ceremony; nothing load-bearing is left over.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fable_rules as fr
from fable_rules import FABLE_RULES, REFRAME, reduce, reframe_is_total


def test_the_reframe_is_total():
    r = reframe_is_total()
    assert r["total"] is True
    assert r["every_cited_rule_exists"] is True
    assert r["mapped_and_ceremony_disjoint"] is True


def test_the_four_ceilings_reduce_to_four_plain_rules():
    assert reduce("PROOF ceiling (claim within evidence)")["reduces_to"] \
        == "F1_HONESTY"
    assert reduce("SCOPE ceiling (change within scope)")["reduces_to"] \
        == "F3_SCOPE"
    assert reduce("AUTHORITY ceiling (act within grant)")["reduces_to"] \
        == "F4_PERMISSION"
    assert reduce("REPLAY ceiling (state reconstructs from history)")[
        "reduces_to"] == "F2_VERIFY"


def test_the_non_sovereign_stamp_is_the_assistant_humility_rule():
    r = reduce("authority=false / canon=false / ledger_effect=none")
    assert r["reduces_to"] == "F5_NON_SOVEREIGN"
    assert "cannot grant yourself authority" in r["rule_text"]


def test_ceremony_reduces_to_no_rule_and_says_so():
    for item in fr.CEREMONY:
        r = reduce(item)
        assert r["is_ceremony"] is True
        assert r["reduces_to"] is None


def test_every_construct_is_either_a_rule_or_ceremony_never_both():
    assert not (set(REFRAME) & set(fr.CEREMONY))


def test_the_seven_rules_are_all_exercised():
    """No dead rule: every plain rule is the reduction of at least one
    HELEN construct."""
    exercised = set(reframe_is_total()["rules_exercised"])
    # F1..F7 all appear (F5 via the stamp, F6 via liveness, F7 via Garden)
    assert exercised >= {"F1_HONESTY", "F2_VERIFY", "F3_SCOPE",
                         "F4_PERMISSION", "F6_FINISH_OR_SAY"}
    assert "F5_NON_SOVEREIGN" in REFRAME.values()
    assert "F7_PROPORTION" in REFRAME.values()
    assert set(exercised) | {"F5_NON_SOVEREIGN"} <= set(FABLE_RULES)


def test_the_real_delta_is_named_honestly():
    r = reframe_is_total()
    assert "executable" in r["the_real_delta"]
    assert "made executable" in r["verdict"]


def test_an_unclassified_construct_is_flagged_not_silently_mapped():
    r = reduce("some construct that is neither rule nor ceremony")
    assert r["reason"] == "E_UNCLASSIFIED"


def test_deterministic():
    assert fr.canon(reframe_is_total()) == fr.canon(reframe_is_total())
