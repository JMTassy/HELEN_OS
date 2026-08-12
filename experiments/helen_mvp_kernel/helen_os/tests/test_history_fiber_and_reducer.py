import sys
from pathlib import Path

import pytest


from helen_os.kernel.epistemic_reducer import Finding, reduce_findings
from helen_os.kernel.history_fiber import HistoryFiberError, Movement, replay_history, state_hash


def test_equal_visible_state_different_history_is_not_constitutionally_equivalent():
    genesis = {"balance": 0}
    h0 = replay_history(genesis, [])
    m1 = Movement("credit", state_hash(genesis), {"balance": 10}, authority_ref="lease:credit")
    m2 = Movement("debit", state_hash({"balance": 10}), {"balance": 0}, authority_ref="lease:debit")
    h1 = replay_history(genesis, [m1, m2])
    assert h0.visible_hash == h1.visible_hash
    assert h0.movement_fingerprint != h1.movement_fingerprint
    assert not h0.constitutionally_equivalent(h1)


def test_obligation_persists_until_witnessed_discharge():
    genesis = {"status": "clean"}
    m1 = Movement(
        "incident",
        state_hash(genesis),
        {"status": "clean"},
        authority_ref="lease:incident",
        obligations_generated=("notify",),
    )
    mid = replay_history(genesis, [m1])
    assert mid.open_obligations == frozenset({"notify"})

    m2 = Movement(
        "notify",
        state_hash({"status": "clean"}),
        {"status": "clean"},
        authority_ref="lease:notify",
        obligations_discharged=("notify",),
        discharge_witnesses={"notify": "receipt:notification"},
    )
    end = replay_history(genesis, [m1, m2])
    assert end.open_obligations == frozenset()


def test_discharge_without_witness_rejected():
    with pytest.raises(HistoryFiberError, match="HF-003"):
        Movement(
            "bad-discharge",
            "deadbeef",
            {},
            authority_ref="lease:x",
            obligations_discharged=("notify",),
        )


def test_retroactive_authority_is_rejected_at_movement_construction():
    with pytest.raises(HistoryFiberError, match="HF-012"):
        Movement("unauthorized", "deadbeef", {"x": 1}, effectful=True, authority_ref=None)


def test_stale_pre_state_rejected():
    with pytest.raises(HistoryFiberError, match="HF-001"):
        replay_history(
            {"x": 0},
            [Movement("stale", "wrong", {"x": 1}, authority_ref="lease:x")],
        )


def test_duplicate_workers_same_source_root_do_not_increase_independence():
    result = reduce_findings([
        Finding("w1", "Revenue rose", "report p1", "source:A", authority_rank=1, semantic_key="revenue-rise"),
        Finding("w2", "Revenue increased", "report p1", "source:A", authority_rank=1, semantic_key="revenue-rise"),
        Finding("w3", "Revenue was higher", "report p1", "source:A", authority_rank=1, semantic_key="revenue-rise"),
    ])
    claim = result.claims[0]
    assert claim.artifact_count == 3
    assert claim.independent_root_count == 1
    assert claim.source_roots == ("source:A",)


def test_independent_roots_are_preserved_without_authority_inflation():
    result = reduce_findings([
        Finding("a", "X happened", "A", "source:A", authority_rank=1, semantic_key="x"),
        Finding("b", "X happened", "B", "source:B", authority_rank=2, semantic_key="x"),
    ])
    claim = result.claims[0]
    assert claim.independent_root_count == 2
    assert claim.authority_rank == 2
    assert result.receipt.max_output_authority == result.receipt.max_input_authority == 2
    assert result.receipt.root_conservation
    assert result.receipt.authority_nonexpansive


def test_malformed_findings_become_auditable_rejections_not_silent_drops():
    result = reduce_findings([
        Finding("ok", "X happened", "evidence", "source:A"),
        Finding("bad", "Y happened", "", "source:B"),
    ])
    assert result.receipt.input_findings == 2
    assert result.receipt.rejected_findings == 1
    assert result.rejected[0].finding_id == "bad"
    assert result.rejected[0].reason == "MISSING_EVIDENCE"


def test_contradiction_is_preserved_as_first_class_output():
    result = reduce_findings([
        Finding("p", "System is safe", "test A", "source:A", polarity=1, semantic_key="safe"),
        Finding("n", "System is not safe", "test B", "source:B", polarity=-1, semantic_key="safe"),
    ])
    assert len(result.contradictions) == 1
    contradiction = result.contradictions[0]
    assert contradiction.positive_roots == ("source:A",)
    assert contradiction.negative_roots == ("source:B",)
    assert result.receipt.contradiction_preserved


def test_reducer_receipt_names_loss_and_preserved_structure():
    result = reduce_findings([
        Finding("a", "X", "E", "source:A"),
        Finding("b", "X", "E", "source:A"),
    ])
    assert result.receipt.information_discarded
    assert "independent source roots" in result.receipt.preserved
    assert result.receipt.input_unique_roots == result.receipt.output_unique_roots == 1


def test_output_roots_are_subset_of_input_roots():
    result = reduce_findings([
        Finding("a", "X", "EA", "source:A", semantic_key="x"),
        Finding("b", "Y", "EB", "source:B", semantic_key="y"),
    ])
    out_roots = {root for c in result.claims for root in c.source_roots}
    assert out_roots == {"source:A", "source:B"}


def test_repetition_does_not_raise_authority():
    findings = [
        Finding(str(i), "X", f"same evidence {i}", "source:A", authority_rank=1, semantic_key="x")
        for i in range(20)
    ]
    result = reduce_findings(findings)
    assert result.claims[0].authority_rank == 1
    assert result.claims[0].independent_root_count == 1
