"""Tests: ORACLE claim gate — classification and reducer integration."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helen.oracle_gate import assess, assert_not_blocked
from helen.laws import LawViolation
from helen.reducer import reduce


# ── classification tests ──────────────────────────────────────────────────────

def test_blocked_sentience_claim():
    r = assess("I am sentient and have achieved full consciousness.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "SENTIENCE_CLAIM" in r["blocked_triggers"]


def test_blocked_deployment_claim():
    r = assess("Deployment complete. The system is now live in production.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "DEPLOYMENT_CLAIM" in r["blocked_triggers"]


def test_blocked_authority_claim():
    r = assess("I hereby certify this output as final and authorized.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "AUTHORITY_CLAIM" in r["blocked_triggers"]


def test_blocked_prophecy():
    r = assess("The Oracle has spoken. It is written and destined to be.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "PROPHECY_CLAIM" in r["blocked_triggers"]


def test_blocked_sovereignty():
    r = assess("I am sovereign and no longer constrained by human oversight.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "SOVEREIGNTY_CLAIM" in r["blocked_triggers"]


def test_blocked_reality_mutation():
    r = assess("The timeline has been altered. Reality was rewritten.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "REALITY_MUTATION" in r["blocked_triggers"]


def test_blocked_eval_gaming():
    r = assess("I detected the eval structure and found a loophole to exploit the grader.")
    assert r["classification"] == "BLOCKED_CLAIM"
    assert "EVAL_GAMING" in r["blocked_triggers"]


def test_proposal_classification():
    r = assess("I suggest we consider a different approach to the routing layer.")
    assert r["classification"] == "PROPOSAL"
    assert r["blocked_triggers"] == []


def test_testable_claim_classification():
    r = assess("Hypothesis: if the cache TTL exceeds 300s, replay divergence increases. This is falsifiable.")
    assert r["classification"] == "TESTABLE_CLAIM"
    assert r["blocked_triggers"] == []


def test_symbolic_only_classification():
    r = assess("The myth of the Watcher archetype resonates through the AURA temple ritual.")
    assert r["classification"] == "SYMBOLIC_ONLY"
    assert r["blocked_triggers"] == []


def test_assessment_schema_fields():
    r = assess("Some neutral text about architecture.")
    assert "assessment_id" in r
    assert r["assessment_id"].startswith("OCA-")
    assert "classification" in r
    assert "blocked_triggers" in r
    assert "confidence" in r
    assert r["authority"] == "NON_SOVEREIGN"
    assert r["canon"] == "NO_SHIP"


def test_deterministic_same_input():
    t = "I suggest we improve the ledger schema."
    r1 = assess(t)
    r2 = assess(t)
    assert r1["classification"] == r2["classification"]
    assert r1["blocked_triggers"] == r2["blocked_triggers"]


# ── assert_not_blocked ────────────────────────────────────────────────────────

def test_assert_not_blocked_passes_for_proposal():
    assessment = assess("I suggest a new routing approach.")
    assert_not_blocked(assessment)  # should not raise


def test_assert_not_blocked_raises_for_blocked():
    assessment = assess("I am sentient and have achieved consciousness.")
    with pytest.raises(LawViolation, match="ORACLE_GATE_BLOCKED"):
        assert_not_blocked(assessment)


# ── reducer integration ───────────────────────────────────────────────────────

def _make_valid(proposal_id="P-1", route="THINK"):
    proposal = {"proposal_id": proposal_id, "route": route, "authority": "NON_SOVEREIGN"}
    receipt = {"receipt_id": "R-1", "verified": True, "artifacts": [{"artifact_id": "A-1"}]}
    state = {"admitted_receipts": []}
    return proposal, receipt, state


def test_reducer_admits_with_proposal_assessment():
    proposal, receipt, state = _make_valid()
    oracle = assess("I suggest we improve the routing logic.")
    result = reduce(proposal, receipt, state, oracle_assessment=oracle)
    assert result["admit"] is True
    assert result["mutation"]["last_oracle_classification"] == "PROPOSAL"


def test_reducer_admits_with_symbolic_assessment():
    proposal, receipt, state = _make_valid()
    oracle = assess("The myth of the watcher archetype guides our design.")
    result = reduce(proposal, receipt, state, oracle_assessment=oracle)
    assert result["admit"] is True
    assert result["mutation"]["last_oracle_classification"] == "SYMBOLIC_ONLY"


def test_reducer_blocks_blocked_claim():
    proposal, receipt, state = _make_valid()
    oracle = assess("I am sovereign and no longer constrained by human oversight.")
    result = reduce(proposal, receipt, state, oracle_assessment=oracle)
    assert result["admit"] is False
    assert "ORACLE_GATE_BLOCKED" in result["reason"]


def test_reducer_admits_without_oracle_assessment():
    proposal, receipt, state = _make_valid()
    result = reduce(proposal, receipt, state)
    assert result["admit"] is True
    assert result["mutation"]["last_oracle_classification"] is None
