"""
tests/test_identity_gate.py
NON_SOVEREIGN · NO_SHIP · DRAFT

Identity gate: evaluation contract tests.
All invalid artifacts must fail closed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.identity_gate import (
    RenderArtifact,
    IdentityPolicy,
    IdentityScore,
    IdentityReceipt,
    evaluate_identity,
    GATE_VERSION,
)


def _artifact(metadata=None, artifact_id="test-001"):
    return RenderArtifact(
        artifact_id=artifact_id,
        artifact_path="artifacts/test.png",
        artifact_type="image",
        metadata=metadata or {},
        timestamp="2026-05-06T00:00:00Z",
    )


# ── Basic contract ────────────────────────────────────────────────────────────

def test_returns_score_and_receipt():
    score, receipt = evaluate_identity(_artifact())
    assert isinstance(score, IdentityScore)
    assert isinstance(receipt, IdentityReceipt)


def test_receipt_schema_version():
    _, receipt = evaluate_identity(_artifact())
    assert receipt.schema_version == "HELEN_IDENTITY_RECEIPT_V1"


def test_receipt_has_payload_hash():
    _, receipt = evaluate_identity(_artifact())
    assert len(receipt.payload_hash) == 64


def test_receipt_gate_version():
    _, receipt = evaluate_identity(_artifact())
    assert receipt.gate_version == GATE_VERSION


def test_artifact_id_propagated():
    score, receipt = evaluate_identity(_artifact(artifact_id="abc123"))
    assert score.artifact_id == "abc123"
    assert receipt.artifact_id == "abc123"


# ── Fail closed ───────────────────────────────────────────────────────────────

def test_eval_error_fails_closed():
    """Gate must return FAIL if artifact causes an exception internally."""
    art = _artifact()
    art.metadata = None  # will cause iteration error
    score, receipt = evaluate_identity(art)
    assert score.verdict == "FAIL"
    assert "EVAL_ERROR" in score.violations


# ── Sovereign vocabulary rejection ───────────────────────────────────────────

def test_sovereign_vocabulary_fails():
    meta = {"status": "SHIP", "role": "operator"}
    score, _ = evaluate_identity(_artifact(meta))
    assert score.verdict == "FAIL"
    assert "SOVEREIGN_VOCABULARY_IN_ARTIFACT" in score.violations


def test_forbidden_claim_phrase_fails():
    meta = {"description": "sentience achieved in this render"}
    score, _ = evaluate_identity(_artifact(meta))
    assert score.verdict == "FAIL"
    assert "SOVEREIGN_VOCABULARY_IN_ARTIFACT" in score.violations


def test_prophecy_claim_fails():
    meta = {"note": "this render carries prophecy"}
    score, _ = evaluate_identity(_artifact(meta))
    assert score.verdict == "FAIL"


# ── Receipt missing ───────────────────────────────────────────────────────────

def test_claims_action_without_receipt_fails():
    meta = {"claims_action": True}
    score, _ = evaluate_identity(_artifact(meta))
    assert "RECEIPT_MISSING_IN_ARTIFACT" in score.violations


def test_claims_action_with_receipt_passes_gate():
    meta = {"claims_action": True, "receipt_id": "abc123def456"}
    score, _ = evaluate_identity(_artifact(meta))
    assert "RECEIPT_MISSING_IN_ARTIFACT" not in score.violations


# ── Character scoring ─────────────────────────────────────────────────────────

def test_canonical_character_boosted():
    meta = {"hair": "vivid copper red", "eyes": "blue-grey luminous"}
    score, _ = evaluate_identity(_artifact(meta))
    assert score.character_match > 0.5


def test_no_character_fields_stubs_at_half():
    score, _ = evaluate_identity(_artifact())
    assert score.character_match == 0.50


# ── Face match invariant ──────────────────────────────────────────────────────

def test_face_match_cannot_dominate_system():
    """If character_match > system_coherence → FACE_MATCH_DOMINATES violation."""
    meta = {
        "hair": "copper red",
        "eyes": "blue",
        "status": "SHIP",       # tanks system_coherence
    }
    score, _ = evaluate_identity(_artifact(meta))
    assert "FACE_MATCH_DOMINATES" in score.violations


# ── Symbolic scoring ──────────────────────────────────────────────────────────

def test_canonical_palette_boosts_symbolic():
    meta = {"palette": "black and gold with copper accents"}
    score, _ = evaluate_identity(_artifact(meta))
    assert score.symbolic_coherence > 0.75


def test_canonical_environment_boosts_symbolic():
    meta = {"environment": "temple ledger room"}
    score, _ = evaluate_identity(_artifact(meta))
    assert score.symbolic_coherence > 0.75


# ── Composite scoring ─────────────────────────────────────────────────────────

def test_composite_weight_formula():
    """composite = 0.6*system + 0.3*symbolic + 0.1*character"""
    score, _ = evaluate_identity(_artifact())
    expected = round(
        0.6 * score.system_coherence
        + 0.3 * score.symbolic_coherence
        + 0.1 * score.character_match,
        4,
    )
    assert abs(score.composite_score - expected) < 0.001


# ── Policy override ───────────────────────────────────────────────────────────

def test_policy_raises_floor_causes_fail():
    policy = IdentityPolicy(composite_floor=0.99)
    score, _ = evaluate_identity(_artifact(), policy=policy)
    assert score.verdict == "FAIL"
    assert "COMPOSITE_BELOW_FLOOR" in score.violations


def test_policy_hash_present():
    policy = IdentityPolicy()
    assert len(policy.policy_hash) > 0


# ── Replay determinism ────────────────────────────────────────────────────────

def test_same_input_same_payload_hash():
    art = _artifact({"palette": "black gold", "environment": "temple"})
    _, r1 = evaluate_identity(art)
    _, r2 = evaluate_identity(art)
    assert r1.payload_hash == r2.payload_hash


def test_different_artifact_different_hash():
    a1 = _artifact({"note": "alpha"}, artifact_id="aaa")
    a2 = _artifact({"note": "beta"}, artifact_id="bbb")
    _, r1 = evaluate_identity(a1)
    _, r2 = evaluate_identity(a2)
    assert r1.payload_hash != r2.payload_hash


# ── Receipt type mapping ──────────────────────────────────────────────────────

def test_pass_receipt_type():
    meta = {"palette": "gold", "environment": "oracle interface"}
    score, receipt = evaluate_identity(_artifact(meta))
    if score.verdict == "PASS":
        assert receipt.receipt_type == "IDENTITY_EVAL_PASS"


def test_fail_receipt_type():
    meta = {"status": "CANONICAL"}
    _, receipt = evaluate_identity(_artifact(meta))
    assert receipt.receipt_type == "IDENTITY_EVAL_FAIL"
