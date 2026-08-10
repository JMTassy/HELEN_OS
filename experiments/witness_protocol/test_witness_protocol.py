"""Negative protocol suite for the witness verifier — the attack table
from the protocol map, row by row, plus the positive control that keeps
a permanent-UNKNOWN verifier from being a false green.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from witness_core import (
    EMPTY_ALLOWED,
    FAIL,
    PASS,
    UNKNOWN,
    CoverageReceipt,
    aggregate,
    independent_components,
    package_hash,
    verify_witness,
)

X = {"package_id": "pkg-1",
     "items": [{"id": "a", "payload": 1},
               {"id": "b", "payload": 2},
               {"id": "c", "payload": 3}]}
XH = package_hash(X)
X_EMPTY = {"package_id": "pkg-empty", "items": []}


def _ev(*item_ids, xh=XH):
    return tuple({"item_id": i, "package_hash": xh, "data": f"checked:{i}"}
                 for i in item_ids)


def _receipt(checked=("a", "b", "c"), evidence=None, input_hash=XH, live=False):
    return CoverageReceipt(
        witness_id="w1", input_hash=input_hash, checked_ids=tuple(checked),
        evidence=_ev(*checked) if evidence is None else evidence,
        claims_live=live)


def p_true(x, evidence):
    return True


# --- positive control (required: permanent-UNKNOWN HAL is a false green) --

def test_positive_control_full_coverage_passes():
    r = verify_witness(_receipt(), X, p_true)
    assert r["verdict"] == PASS
    assert all(r["checks"].values())


# --- the attack table, row by row ----------------------------------------

def test_empty_parse_on_nonempty_package_unknown():
    r = verify_witness(_receipt(checked=(), evidence=()), X, p_true)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_COVERAGE_GAP"


def test_dropped_last_id_unknown():
    r = verify_witness(_receipt(checked=("a", "b")), X, p_true)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_COVERAGE_GAP"


def test_duplicate_ids_count_matches_unknown():
    # |checked| == 3 == |required| but the SET is short: no dup inflation.
    r = verify_witness(
        _receipt(checked=("a", "b", "b"), evidence=_ev("a", "b", "b")),
        X, p_true)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_DUPLICATE_IDS"


def test_stale_input_hash_unknown():
    r = verify_witness(_receipt(input_hash="deadbeef"), X, p_true)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_STALE_BIND"


def test_evidence_from_other_package_fails():
    foreign = _ev("a", "b", "c", xh=package_hash({"package_id": "other", "items": []}))
    r = verify_witness(_receipt(evidence=foreign), X, p_true)
    assert r["verdict"] == FAIL
    assert r["reason"] == "E_FOREIGN_EVIDENCE"


def test_pass_with_zero_evidence_unknown():
    r = verify_witness(_receipt(evidence=()), X, p_true)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_VACUOUS"


def test_parser_exception_yields_unknown_not_crash():
    def exploding_predicate(x, evidence):
        raise RuntimeError("parser blew up")
    r = verify_witness(_receipt(), X, exploding_predicate)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_PREDICATE_ERROR"


def test_true_empty_under_empty_allowed_may_pass():
    r = verify_witness(
        CoverageReceipt(witness_id="w1", input_hash=package_hash(X_EMPTY)),
        X_EMPTY, p_true, empty_policy=EMPTY_ALLOWED)
    assert r["verdict"] == PASS


# --- laws beyond the table -----------------------------------------------

def test_claims_live_flag_never_trusted():
    # Flipping live=True on a broken receipt changes nothing; the verdict
    # is recomputed, not read.
    broken = verify_witness(_receipt(checked=("a",), live=True), X, p_true)
    assert broken["verdict"] == UNKNOWN
    a = verify_witness(_receipt(live=True), X, p_true)
    b = verify_witness(_receipt(live=False), X, p_true)
    assert a == b


def test_predicate_false_under_live_fails():
    r = verify_witness(_receipt(), X, lambda x, e: False)
    assert r["verdict"] == FAIL
    assert r["reason"] == "E_PREDICATE_FALSE"


def test_ill_typed_receipt_unknown():
    r = verify_witness({"live": True, "trust_me": 1}, X, p_true)
    assert r["verdict"] == UNKNOWN
    assert r["reason"] == "E_ILL_TYPED"


def test_no_admit_surface_exists():
    import witness_core
    exported = {n for n in dir(witness_core) if not n.startswith("_")}
    assert not any("admit" in n.lower() for n in exported)  # HAL_PASS ⊬ ADMIT


# --- aggregation + independence ------------------------------------------

def test_aggregation_fail_dominates_unknown_taints():
    P_, U_, F_ = {"verdict": PASS}, {"verdict": UNKNOWN}, {"verdict": FAIL}
    assert aggregate([P_, P_, P_]) == PASS
    assert aggregate([P_, U_, P_]) == UNKNOWN
    assert aggregate([P_, U_, F_]) == FAIL
    assert aggregate([]) == UNKNOWN  # empty panel proves nothing


def test_two_receipts_do_not_imply_two_witnesses():
    assert independent_components(["w1", "w2"], []) == 2
    assert independent_components(["w1", "w2"], [("w1", "w2")]) == 1
    assert independent_components(["w1", "w1"], []) == 1  # duplicate receipt
    assert independent_components(["w1", "w2", "w3"], [("w1", "w2")]) == 2


def test_verifier_deterministic():
    a = verify_witness(_receipt(), X, p_true)
    b = verify_witness(_receipt(), X, p_true)
    assert a == b
