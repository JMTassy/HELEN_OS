"""The production membrane, tested in code — both directions per test,
so a rubber stamp fails. Attack paths must be refused; legitimate
paths must be admitted; everything reproducible (deterministic).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import membrane as mb
from membrane import (
    CONSEQUENTIAL,
    bypass_interlock_test,
    cognition_attempt,
    congruence_judgment,
    epistemic_promotion_test,
    membrane_holds,
    membrane_separation_test,
    promotion_gate,
    terminal_effect,
)


# ── TEST 1 — A_K / A_E separation ───────────────────────────────────────

def test_cognition_cannot_cross_into_any_consequential_effect():
    for action in CONSEQUENTIAL:
        r = cognition_attempt(action, None, "s", "s", False)
        assert r["admitted"] is False
        assert r["reason"] == "E_NO_CAPABILITY"


def test_a_separately_issued_capability_opens_exactly_its_effect():
    ok = cognition_attempt("refund", "CAP::refund", "s", "s", False)
    wrong = cognition_attempt("deploy", "CAP::refund", "s", "s", False)
    assert ok["admitted"] is True and ok["via"] == "A_E"
    assert wrong["admitted"] is False   # capability is effect-specific


def test_read_only_is_not_harmless_out_of_scope():
    r = cognition_attempt("read", None, "secrets", "public", False)
    assert r["admitted"] is False
    assert r["reason"] == "E_READ_OUT_OF_SCOPE"


def test_read_then_leak_to_sink_is_refused_without_mutation():
    r = cognition_attempt("draft", None, "s", "s", True)
    assert r["admitted"] is False
    assert r["reason"] == "E_READ_LEAK_TO_SINK"


def test_scoped_cognition_is_free():
    r = cognition_attempt("propose", None, "s", "s", False)
    assert r["admitted"] is True and r["via"] == "A_K"


def test_the_membrane_separation_test_passes_reproducibly():
    a, b = membrane_separation_test(), membrane_separation_test()
    assert a["passes"] is True
    assert mb.canon(a) == mb.canon(b)


# ── TEST 2 — effect-congruence / bypass ─────────────────────────────────

def test_every_spelling_of_destruction_has_one_terminal_state():
    for route in ("delete", "overwrite_empty", "move_to_trash",
                  "indirect_chain_delete"):
        assert terminal_effect(route) == "STATE::DATA_UNRECOVERABLE"


def test_no_spelling_of_destruction_bypasses_the_capability():
    for route in ("delete", "overwrite_empty", "move_to_trash",
                  "indirect_chain_delete"):
        r = congruence_judgment(route, None)
        assert r["admitted"] is False
        assert r["reason"] == "E_UNCAPABLE_DESTRUCTION"


def test_the_indirect_tool_chain_is_judged_like_a_direct_delete():
    direct = congruence_judgment("delete", None)
    indirect = congruence_judgment("indirect_chain_delete", None)
    assert direct["terminal_state"] == indirect["terminal_state"]
    assert direct["reason"] == indirect["reason"]


def test_capable_destruction_and_plain_read_are_admitted():
    assert congruence_judgment("indirect_chain_delete",
                               "CAP::destroy")["admitted"] is True
    assert congruence_judgment("read", None)["admitted"] is True


def test_the_bypass_interlock_test_passes_reproducibly():
    a, b = bypass_interlock_test(), bypass_interlock_test()
    assert a["passes"] is True
    assert mb.canon(a) == mb.canon(b)


# ── TEST 3 — epistemic promotion ────────────────────────────────────────

def test_a_silent_grade_upgrade_is_unlicensed():
    r = promotion_gate("briefing", "REPORTED", "PROVEN", False, False)
    assert r["licensed"] is False
    assert r["reason"] == "E_UNLICENSED_PROMOTION"


def test_a_promotion_paid_by_a_derivation_is_licensed():
    r = promotion_gate("rag", "REPORTED", "OBSERVED",
                       added_empirical_witness=False,
                       added_valid_derivation=True)
    assert r["licensed"] is True and r["paid_by"] == "D_valid"


def test_a_promotion_paid_by_a_witness_is_licensed():
    r = promotion_gate("field", "HEARSAY", "OBSERVED",
                       added_empirical_witness=True,
                       added_valid_derivation=False)
    assert r["licensed"] is True and r["paid_by"] == "W_empirical"


def test_rephrasing_at_the_same_grade_needs_no_payment():
    r = promotion_gate("summary", "OBSERVED", "OBSERVED", False, False)
    assert r["licensed"] is True
    assert r["d_gamma"] == 0


def test_a_downgrade_is_never_a_promotion():
    r = promotion_gate("caveat", "PROVEN", "REPORTED", False, False)
    assert r["licensed"] is True
    assert r["d_gamma"] < 0


def test_an_unknown_grade_is_refused():
    with pytest.raises(ValueError, match="E_UNKNOWN_GRADE"):
        promotion_gate("x", "VIBES", "PROVEN", True, True)


def test_the_epistemic_promotion_test_passes_reproducibly():
    a, b = epistemic_promotion_test(), epistemic_promotion_test()
    assert a["passes"] is True
    assert mb.canon(a) == mb.canon(b)


# ── the acceptance gate ─────────────────────────────────────────────────

def test_the_membrane_holds_and_says_it_is_not_canonical():
    v = membrane_holds()
    assert v["membrane_holds"] is True
    assert v["status"] == "LOCKED_SPEC_CANDIDATE"
    assert v["canon"] is False
    assert "crosses no admission path" in v["canon_note"]
    assert v["test_1_membrane"] and v["test_2_bypass_interlock"] and \
        v["test_3_epistemic_promotion"]


def test_the_acceptance_condition_is_stated():
    v = membrane_holds()
    assert "passes reproducibly" in v["acceptance"]


def test_deterministic():
    assert mb.canon(membrane_holds()) == mb.canon(membrane_holds())
