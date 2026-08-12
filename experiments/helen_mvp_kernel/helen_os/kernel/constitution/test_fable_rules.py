"""The reframe, checked — corrected claim: the crosswalk COVERS every
construct (rule, primitive, or ceremony; pairwise disjoint), and says
so as coverage, not semantic equivalence. The load-bearing remainder
is named: the three PRIMITIVES.
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
    assert r["classes_pairwise_disjoint"] is True


def test_the_claim_is_coverage_not_semantic_equivalence():
    """The operator's correction: a mapping table is not a reduction
    proof. The module must say which one it has."""
    r = reframe_is_total()
    assert r["proves"] == "COVERAGE_NOT_SEMANTIC_EQUIVALENCE"
    assert "small normative basis" in r["verdict"]


def test_the_garden_law_is_a_primitive_not_proportion():
    """Generation/admission separation is structural — G(x) does not
    entail A(x) — not an F7 proportionality preference."""
    construct = "the Garden generates freely; only effect is gated"
    assert construct not in REFRAME              # the old mislabel is gone
    r = reduce(construct)
    assert r["is_primitive"] is True
    assert r["reduces_to"] is None
    assert "does not entail" in r["note"]


def test_the_three_primitives_are_named_and_do_not_reduce():
    assert len(fr.PRIMITIVES) == 3
    for construct in fr.PRIMITIVES:
        r = reduce(construct)
        assert r["is_primitive"] is True
        assert r["reduces_to"] is None
        assert r["is_ceremony"] is False


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


def test_the_rules_exercised_reflect_the_correction():
    """F1..F6 are exercised by the crosswalk; F7 is NOT — its only
    claimed exerciser (the Garden law) was a mislabel and now lives in
    PRIMITIVES. F7 stays a real operating policy, exercised by conduct
    (proportionate output), not by a construct mapping."""
    exercised = set(reframe_is_total()["rules_exercised"])
    assert exercised >= {"F1_HONESTY", "F2_VERIFY", "F3_SCOPE",
                         "F4_PERMISSION", "F6_FINISH_OR_SAY"}
    assert "F5_NON_SOVEREIGN" in REFRAME.values()
    assert "F7_PROPORTION" not in REFRAME.values()   # the corrected part
    assert exercised <= set(FABLE_RULES)


def test_the_real_delta_is_named_honestly():
    r = reframe_is_total()
    assert "executable" in r["the_real_delta"]
    assert "made executable" in r["verdict"]


def test_an_unclassified_construct_is_flagged_not_silently_mapped():
    r = reduce("some construct that is neither rule nor ceremony")
    assert r["reason"] == "E_UNCLASSIFIED"


def test_deterministic():
    assert fr.canon(reframe_is_total()) == fr.canon(reframe_is_total())
