"""Tests for tools/validators/doctrine_gate.py — the pointer-resolving gate.

Complements tests/test_claim_classification.py (the §4 harness, which
classifies syntactically): this gate RESOLVES pointers against the disk —
the mechanical form of the locked invariant:
  No location → no doctrine. No test → no gate. No replay → no admission.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.validators.doctrine_gate import evaluate_claim, scan_markdown, default_resolver


def C(**kw):
    base = {"CLAIM_ID": "T", "STRATUM": "HYPOTHESIS", "TEXT": "x could y",
            "EVIDENCE": "NONE", "ADMISSION_STATUS": "UNADMITTED",
            "CLAIM_FORCE": "DESCRIPTIVE", "FAILURE_MODE": "falsifier",
            "IMPLEMENTATION_STATE": "CONCEPT", "TEST_POINTER": "NONE",
            "ARTIFACT_POINTER": "NONE"}
    base.update(kw)
    return base


def test_resolver_finds_real_files_rejects_ghosts() -> None:
    assert default_resolver("CLAUDE.md") is True
    assert default_resolver("GHOST_FILE_THAT_DOES_NOT_EXIST.md") is False
    assert default_resolver("NONE") is False


def test_invariant_without_receipt_rejected() -> None:
    r = evaluate_claim(C(STRATUM="INVARIANT", ADMISSION_STATUS="ADMITTED"))
    assert r["decision"] == "REJECTED"
    assert "NO_RECEIPT_FOR_INVARIANT" in r["reason_codes"]


def test_fictional_receipt_rejected_by_resolution() -> None:
    r = evaluate_claim(C(STRATUM="INVARIANT", ADMISSION_STATUS="ADMITTED",
                         EVIDENCE="GHOST_RECEIPT.md",
                         IMPLEMENTATION_STATE="GENERALIZED"))
    assert r["decision"] == "REJECTED"
    assert "FICTIONAL_RECEIPT" in r["reason_codes"]


def test_valid_invariant_with_resolving_pointers_verifies() -> None:
    r = evaluate_claim(C(STRATUM="INVARIANT", ADMISSION_STATUS="ADMITTED",
                         TEXT="the validator rejects sovereign writes",
                         EVIDENCE="src/wul_packet_validator.py",
                         IMPLEMENTATION_STATE="RECEIPTED",
                         TEST_POINTER="tests/test_wul_packet_validator.py",
                         ARTIFACT_POINTER="src/wul_packet_validator.py"))
    assert r["decision"] == "ADMITTED"           # verified, not newly admitted


def test_implementation_inflation_rejected() -> None:
    r = evaluate_claim(C(STRATUM="INVARIANT", ADMISSION_STATUS="ADMITTED",
                         EVIDENCE="CLAUDE.md", IMPLEMENTATION_STATE="CONCEPT"))
    assert "IMPLEMENTATION_INFLATION" in r["reason_codes"]


def test_unfalsifiable_hypothesis_rejected() -> None:
    r = evaluate_claim(C(FAILURE_MODE="NONE"))
    assert "UNFALSIFIABLE_HYPOTHESIS" in r["reason_codes"]


def test_proof_verb_without_test_rejected_allowed_phrases_pass() -> None:
    bad = evaluate_claim(C(TEXT="this governs the kernel and proves safety"))
    assert "PROOF_VERB_WITHOUT_TEST" in bad["reason_codes"]
    ok = evaluate_claim(C(TEXT="this is designed to mirror the kernel boundary"))
    assert ok["decision"] == "KEEP"


def test_cross_layer_promotion_rejected() -> None:
    r = evaluate_claim(C(REQUESTED_PROMOTION="INVARIANT"))
    assert "CROSS_LAYER_PROMOTION" in r["reason_codes"]


def test_proposer_validator_separation_enforced() -> None:
    r = evaluate_claim(C(REQUESTED_PROMOTION="DOCTRINE", PROPOSER="a", VALIDATOR="a",
                         TEST_POINTER="Makefile", ARTIFACT_POINTER="CLAUDE.md"))
    assert "PROPOSER_IS_VALIDATOR" in r["reason_codes"]
    ok = evaluate_claim(C(REQUESTED_PROMOTION="DOCTRINE", PROPOSER="a", VALIDATOR="b",
                          TEST_POINTER="Makefile", ARTIFACT_POINTER="CLAUDE.md"))
    assert ok["decision"] == "ADMISSION_CANDIDATE"


def test_assertive_without_test_downgrades_not_rejects() -> None:
    r = evaluate_claim(C(CLAIM_FORCE="ASSERTIVE"))
    assert r["decision"] == "KEEP"
    assert "FORCE_STATE_MISMATCH_DOWNGRADE" in r["reason_codes"]
    assert r["current_stratum"] == "DOCTRINE"


def test_self_exemption_rejected() -> None:
    r = evaluate_claim(C(TEXT="this claim could stand, being exempt from this protocol"))
    assert "SELF_EXEMPTION" in r["reason_codes"]


def test_malformed_stratum_fails_closed() -> None:
    r = evaluate_claim({"CLAIM_ID": "X", "STRATUM": "VIBES", "TEXT": "?"})
    assert r["decision"] == "REJECTED"
    assert "MALFORMED_STRATUM" in r["reason_codes"]


def test_scan_rejects_bad_json_claim_block(tmp_path) -> None:
    (tmp_path / "doc.md").write_text("intro\n```claim\n{ not json\n```\n")
    results = scan_markdown(tmp_path)
    assert len(results) == 1
    assert results[0][1]["decision"] == "REJECTED"
    assert "BAD_JSON_CLAIM_BLOCK" in results[0][1]["reason_codes"]


def test_scan_evaluates_valid_block(tmp_path) -> None:
    (tmp_path / "doc.md").write_text(
        '```claim\n{"CLAIM_ID": "S1", "STRATUM": "HYPOTHESIS", '
        '"TEXT": "x could y", "FAILURE_MODE": "z fails", '
        '"CLAIM_FORCE": "DESCRIPTIVE", "IMPLEMENTATION_STATE": "CONCEPT"}\n```\n')
    results = scan_markdown(tmp_path)
    assert results[0][1]["decision"] == "KEEP"
