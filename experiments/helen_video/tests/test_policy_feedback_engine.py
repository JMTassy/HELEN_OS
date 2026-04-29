"""Policy Feedback Engine — invariant and functional tests."""
import ast
import hashlib
import json
from pathlib import Path

import pytest

from helen_video.policy_feedback_engine import (
    AUTHORITY,
    DEFAULT_WEIGHTS,
    POLICY_CANDIDATE_STATUS,
    analyze_traces,
    make_policy_candidate,
    policy_receipt,
    propose_weights,
    verify_policy_receipt,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _entry(status="ACCEPTED", pipeline_score=0.8, output_score=0.9,
           entry_hash=None, failure_class=None):
    return {
        "status": status,
        "entry_hash": entry_hash or hashlib.sha256(status.encode()).hexdigest(),
        "receipt": {
            "pipeline_score": pipeline_score,
            "output_score": output_score,
            "failure_class": failure_class,
        },
    }


def _good_ledger():
    return [
        _entry("ACCEPTED", pipeline_score=0.9, output_score=0.9, entry_hash="aaa"),
        _entry("ACCEPTED", pipeline_score=0.8, output_score=0.85, entry_hash="bbb"),
        _entry("REJECTED", pipeline_score=0.3, output_score=0.4, entry_hash="ccc",
               failure_class="low_coherence"),
    ]


# ── invariant: status is always POLICY_CANDIDATE ─────────────────────────────

def test_make_policy_candidate_status():
    c = make_policy_candidate(_good_ledger())
    assert c["status"] == POLICY_CANDIDATE_STATUS


def test_make_policy_candidate_never_active():
    c = make_policy_candidate(_good_ledger())
    assert c["status"] not in {"ACTIVE", "ACCEPTED", "APPROVED", "PROMOTED"}


def test_activation_requires_reducer():
    c = make_policy_candidate(_good_ledger())
    assert c["activation_requires"] == "REDUCER_ADMISSION"


# ── invariant: authority is non-sovereign ─────────────────────────────────────

def test_authority_is_non_sovereign():
    c = make_policy_candidate(_good_ledger())
    assert c["authority"] == "NON_SOVEREIGN_POLICY_PROPOSAL"
    assert c["receipt"]["authority"] == "NON_SOVEREIGN_POLICY_PROPOSAL"


# ── invariant: receipt binds traces + weights ─────────────────────────────────

def test_policy_receipt_verifies():
    entries = _good_ledger()
    c = make_policy_candidate(entries)
    assert verify_policy_receipt(c["receipt"], entries, c["proposed_weights"]) is True


def test_policy_receipt_fails_on_different_entries():
    entries = _good_ledger()
    c = make_policy_candidate(entries)
    tampered = entries + [_entry("ACCEPTED", entry_hash="zzz")]
    assert verify_policy_receipt(c["receipt"], tampered, c["proposed_weights"]) is False


def test_policy_receipt_fails_on_different_weights():
    entries = _good_ledger()
    c = make_policy_candidate(entries)
    forged_weights = {**c["proposed_weights"], "pipeline_weight": 0.99}
    assert verify_policy_receipt(c["receipt"], entries, forged_weights) is False


def test_policy_receipt_has_required_fields():
    entries = _good_ledger()
    c = make_policy_candidate(entries)
    r = c["receipt"]
    required = {"receipt_hash", "trace_digest", "weight_digest", "authority", "timestamp"}
    assert required <= set(r.keys())


# ── invariant: never mutates input entries ────────────────────────────────────

def test_make_policy_candidate_does_not_mutate_entries():
    entries = _good_ledger()
    snapshots = [dict(e) for e in entries]
    make_policy_candidate(entries)
    assert entries == snapshots


def test_propose_weights_does_not_mutate_current_weights():
    current = dict(DEFAULT_WEIGHTS)
    snapshot = dict(current)
    analysis = analyze_traces(_good_ledger())
    propose_weights(analysis, current)
    assert current == snapshot


# ── analyze_traces: correct bucketing ────────────────────────────────────────

def test_analyze_traces_counts_correctly():
    entries = [
        _entry("ACCEPTED"), _entry("ACCEPTED"),
        _entry("REJECTED"), _entry("PENDING"),
    ]
    a = analyze_traces(entries)
    assert a["n_accepted"] == 2
    assert a["n_rejected"] == 1
    assert a["n_review"] == 1


def test_analyze_traces_empty():
    a = analyze_traces([])
    assert a["n_accepted"] == 0
    assert a["n_rejected"] == 0


def test_analyze_traces_failure_classes_collected():
    entries = [
        _entry("REJECTED", failure_class="low_coherence"),
        _entry("REJECTED", failure_class="binding_mismatch"),
    ]
    a = analyze_traces(entries)
    assert "low_coherence" in a["failure_classes"]
    assert "binding_mismatch" in a["failure_classes"]


# ── propose_weights: bounds enforced ─────────────────────────────────────────

def test_proposed_weights_within_bounds():
    for _ in range(10):
        entries = [_entry("REJECTED")] * 10 + [_entry("ACCEPTED")] * 2
        a = analyze_traces(entries)
        w = propose_weights(a)
        assert 0.1 <= w["pipeline_weight"] <= 0.9
        assert 0.1 <= w["output_weight"] <= 0.9
        assert 1.0 <= w["continuity_multiplier"] <= 20.0
        assert 0.0 <= w["failure_penalty"] <= 10.0


def test_proposed_weights_normalize_to_one():
    a = analyze_traces(_good_ledger())
    w = propose_weights(a)
    assert abs(w["pipeline_weight"] + w["output_weight"] - 1.0) < 1e-5


def test_propose_weights_empty_traces_returns_base():
    a = analyze_traces([])
    w = propose_weights(a, DEFAULT_WEIGHTS)
    assert w == DEFAULT_WEIGHTS


def test_high_rejection_rate_increases_failure_penalty():
    entries = [_entry("REJECTED")] * 8 + [_entry("ACCEPTED")] * 2
    a = analyze_traces(entries)
    w = propose_weights(a, {**DEFAULT_WEIGHTS, "failure_penalty": 0.0})
    assert w["failure_penalty"] > 0.0


# ── make_policy_candidate: full fields ───────────────────────────────────────

def test_candidate_has_all_required_fields():
    c = make_policy_candidate(_good_ledger())
    required = {"policy_id", "status", "authority", "proposed_weights",
                "analysis_summary", "receipt", "activation_requires"}
    assert required <= set(c.keys())


def test_candidate_proposed_weights_has_all_keys():
    c = make_policy_candidate(_good_ledger())
    for k in DEFAULT_WEIGHTS:
        assert k in c["proposed_weights"]


def test_candidate_analysis_summary_has_counts():
    c = make_policy_candidate(_good_ledger())
    s = c["analysis_summary"]
    assert "n_accepted" in s
    assert "n_rejected" in s
    assert "n_review" in s


def test_candidate_policy_id_stable_when_provided():
    entries = _good_ledger()
    c = make_policy_candidate(entries, policy_id="fixed-id")
    assert c["policy_id"] == "fixed-id"


# ── invariant: no IO, no ledger writes ───────────────────────────────────────

def test_engine_has_no_forbidden_imports():
    import helen_video.policy_feedback_engine as mod
    tree = ast.parse(Path(mod.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
    forbidden = {"subprocess", "socket", "urllib", "requests", "httpx",
                 "video_ledger", "remotion_wrapper", "admissibility_gate",
                 "sequence_optimizer"}
    assert not (imported & forbidden)


def test_engine_has_no_ledger_write_calls():
    import helen_video.policy_feedback_engine as mod
    tree = ast.parse(Path(mod.__file__).read_text())
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    # Only file-IO method names — list.append() is legitimate
    forbidden = {"write_text", "write_bytes", "write", "open"}
    assert not (set(calls) & forbidden)


def test_engine_has_no_public_activation_methods():
    import helen_video.policy_feedback_engine as mod
    public = [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n))]
    forbidden = {"activate", "promote", "ship", "deliver", "accept", "approve"}
    assert not (set(public) & forbidden)
