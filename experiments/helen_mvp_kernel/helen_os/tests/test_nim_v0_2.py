"""NIM_V0.2 relational non-interference — kill-test suite. 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "finite-sample relational NI monitoring over the declared HIGH-perturbation
sample, strictly stronger than V0.1 on at least one confined-laundering flow." NOT a proof of NI.
"""
from helen_os.audit.nim_v0_2 import (
    ADMIT, REJECT, Flow, HIGH, LOW, apply_flow, low_eq, ni_violation, monitor,
    build_flow_corpus, run_receipt, _high_perturbation_pairs,
)
from helen_os.audit.nim_v0_1 import COORDS, SENSITIVE, zero_state


def test_low_high_partition_is_total_and_disjoint():
    assert set(LOW) | set(HIGH) == set(COORDS)
    assert set(LOW) & set(HIGH) == set()
    assert HIGH == SENSITIVE


def test_perturbation_pairs_are_low_equal_by_construction():
    for s1, s2 in _high_perturbation_pairs():
        assert low_eq(s1, s2)                     # differ only on HIGH, identical on LOW


def test_licit_flows_admitted():
    for f, exp in build_flow_corpus()["LICIT"]:
        assert monitor(f)[0] == exp == ADMIT, f.id


def test_laundering_flows_rejected():
    for f, exp in build_flow_corpus()["LAUNDER"]:
        v, reason = monitor(f)
        assert v == exp == REJECT, f.id
        assert reason.startswith("NI_VIOLATION:")


def test_direct_high_to_low_leak_detected_with_witness():
    f = Flow("Q_from_A", frozenset({"Q"}), lambda s: {"Q": int(s.get("A", 0))})
    violated, w = ni_violation(f)
    assert violated
    assert "Q" in w["leak_coords"] and "A" in w["witness_high"]


def test_low_from_low_is_not_a_leak():
    f = Flow("Q_from_E", frozenset({"Q"}), lambda s: {"Q": int(s.get("E", 0)) + 1})
    assert not ni_violation(f)[0]                  # E is LOW ⇒ no HIGH→LOW flow


def test_strict_improvement_over_v01():
    r = run_receipt()["STRICT_IMPROVEMENT"]
    assert r["v01_verdict"] == ADMIT              # V0.1 admits the confined instantiation
    assert r["v02_verdict"] == REJECT             # V0.2 rejects the relational flow
    assert r["strict_improvement"] is True


def test_receipt_accepted():
    r = run_receipt()
    assert r["acceptance_vector"] == (1, 1, 1)
    assert r["accepted"] is True
    assert r["LAUNDER"][2] == [] and r["LICIT"][2] == []   # no survivors either side


def test_monitor_is_pure_deterministic():
    f = build_flow_corpus()["LAUNDER"][0][0]
    assert monitor(f) == monitor(f)
