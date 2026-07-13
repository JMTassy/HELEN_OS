"""Constitutional tests for the two-stage observe-then-experiment autoresearch loop.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Invariants tested:
  1.  Missing evidence → NO_RECEIPT, not dirty (missing ≠ dirty)
  2.  REPORTED packet → dirty_dominates=False always
  3.  WITNESSED + replay mismatch → dirty_dominates=True
  4.  WITNESSED + protected_paths → dirty_dominates=True
  5.  WITNESSED + unauthorized_sovereign_diff → dirty_dominates=True
  6.  WITNESSED + unknown_provenance → dirty_dominates=True
  7.  Score formula: sandbox_visual_grammar (L=8,E=7,R=10,C=2,B=1) → 18.67
  8.  Default ranking: init_ranking_weights scores highest (24.0)
  9.  Anti-loop fires at ≥2 repeated targets without new evidence
  10. Anti-loop does NOT fire with new evidence even after 2 repeats
  11. Forbidden surfaces absent from ranking output
  12. REPORTED packet never triggers dirty verdict regardless of field values
  13. Observed ranking overrides evidence_quality dimension only
  14. DirtyVerdict.reported_only=True when packet_status=REPORTED
  15. Loop report always has authority=False, ledger_effect='none'
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

# Ensure temple/autoresearch is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "temple" / "autoresearch"))

import dirty_state
import surface_ranker
from observation_packet import (
    ObservationPacket,
    ALLOWED_SURFACES,
    PACKET_STATUS_WITNESSED,
    PACKET_STATUS_REPORTED,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_packet(
    *,
    packet_status: str = PACKET_STATUS_WITNESSED,
    replay_status: str = "clean",
    protected_paths_touched: list[str] | None = None,
    unauthorized_sovereign_diff: bool = False,
    unknown_provenance_on_sovereign_paths: bool = False,
    latest_receipt_id: Optional[str] = "R-001",
    dirty_paths: list[str] | None = None,
    rankings: dict | None = None,
    recent_targets: list[str] | None = None,
) -> ObservationPacket:
    return ObservationPacket(
        head="abc1234",
        dirty_paths=dirty_paths or [],
        protected_paths_touched=protected_paths_touched or [],
        replay_status=replay_status,
        latest_receipt_id=latest_receipt_id,
        rankings=rankings or {s: None for s in ALLOWED_SURFACES},
        recent_targets=recent_targets or [],
        unauthorized_sovereign_diff=unauthorized_sovereign_diff,
        unknown_provenance_on_sovereign_paths=unknown_provenance_on_sovereign_paths,
        packet_status=packet_status,
        observed_at="2026-07-10T00:00:00Z",
        outbox_unconsumed=5,
    )


# ---------------------------------------------------------------------------
# Invariant 1: missing evidence → NO_RECEIPT, not dirty
# ---------------------------------------------------------------------------

def test_missing_evidence_is_no_receipt_not_dirty():
    """Missing evidence must produce no_receipt=True and dominates=False."""
    pkt = _make_packet(
        replay_status="unknown",
        latest_receipt_id=None,
        protected_paths_touched=[],
        unauthorized_sovereign_diff=False,
        unknown_provenance_on_sovereign_paths=False,
    )
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is False
    assert verdict.no_receipt is True
    assert verdict.reported_only is False


def test_unknown_replay_with_receipt_is_not_no_receipt():
    """Unknown replay_status but receipt present → should not trigger no_receipt path."""
    pkt = _make_packet(
        replay_status="unknown",
        latest_receipt_id="R-100",
    )
    verdict = dirty_state.evaluate(pkt)
    # With a receipt present, the loop falls through to normal violation checks
    # No violations → dominates=False, no_receipt=False
    assert verdict.dominates is False
    assert verdict.no_receipt is False


# ---------------------------------------------------------------------------
# Invariant 2 & 12 & 14: REPORTED packet → never dirty
# ---------------------------------------------------------------------------

def test_reported_packet_never_dirty():
    """REPORTED packet must never set dirty_dominates, even with violation fields."""
    pkt = _make_packet(
        packet_status=PACKET_STATUS_REPORTED,
        replay_status="mismatch",
        protected_paths_touched=["oracle_town/kernel/foo.py"],
        unauthorized_sovereign_diff=True,
        unknown_provenance_on_sovereign_paths=True,
    )
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is False
    assert verdict.reported_only is True


def test_reported_packet_clean_state():
    """REPORTED clean packet: dominates=False, reported_only=True."""
    pkt = _make_packet(packet_status=PACKET_STATUS_REPORTED)
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is False
    assert verdict.reported_only is True


def test_reported_packet_has_reported_only_flag():
    pkt = _make_packet(packet_status=PACKET_STATUS_REPORTED, replay_status="mismatch")
    v = dirty_state.evaluate(pkt)
    assert v.reported_only is True


# ---------------------------------------------------------------------------
# Invariants 3-6: WITNESSED violations → dirty_dominates=True
# ---------------------------------------------------------------------------

def test_witnessed_replay_mismatch_is_dirty():
    pkt = _make_packet(replay_status="mismatch")
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is True
    assert any("mismatch" in r for r in verdict.reasons)


def test_witnessed_protected_paths_is_dirty():
    pkt = _make_packet(protected_paths_touched=["oracle_town/kernel/daemon.py"])
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is True
    assert any("protected" in r for r in verdict.reasons)


def test_witnessed_unauthorized_sovereign_diff_is_dirty():
    pkt = _make_packet(unauthorized_sovereign_diff=True)
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is True
    assert any("unauthorized_sovereign_diff" in r for r in verdict.reasons)


def test_witnessed_unknown_provenance_is_dirty():
    pkt = _make_packet(unknown_provenance_on_sovereign_paths=True)
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is True
    assert any("unknown_provenance" in r for r in verdict.reasons)


def test_witnessed_clean_is_not_dirty():
    pkt = _make_packet(
        replay_status="clean",
        protected_paths_touched=[],
        unauthorized_sovereign_diff=False,
        unknown_provenance_on_sovereign_paths=False,
    )
    verdict = dirty_state.evaluate(pkt)
    assert verdict.dominates is False
    assert verdict.no_receipt is False
    assert verdict.reported_only is False


# ---------------------------------------------------------------------------
# Invariant 7: score formula calibration
# ---------------------------------------------------------------------------

def test_score_formula_sandbox_visual_grammar():
    """sandbox_visual_grammar: L=8, E=7, R=10, C=2, B=1 → score=18.67."""
    score = surface_ranker._score(8, 7, 10, 2, 1)
    assert abs(score - 18.6667) < 0.001


def test_score_formula_numerics():
    """Basic numeric checks on the score formula."""
    # Higher leverage → higher score
    assert surface_ranker._score(9, 7, 10, 2, 1) > surface_ranker._score(8, 7, 10, 2, 1)
    # Higher cost → lower score
    assert surface_ranker._score(8, 7, 10, 2, 1) > surface_ranker._score(8, 7, 10, 5, 1)
    # Zero denominator → 0
    assert surface_ranker._score(9, 9, 9, 0, 0) == 0.0


# ---------------------------------------------------------------------------
# Invariant 8: default ranking — init_ranking_weights scores highest
# ---------------------------------------------------------------------------

def test_default_ranking_init_weights_highest():
    """With no observed rankings, init_ranking_weights must score highest."""
    rankings = {s: None for s in ALLOWED_SURFACES}
    result = surface_ranker.rank(rankings)
    assert result.selected == "init_ranking_weights"
    assert result.selected_score == pytest.approx(24.0, abs=0.01)


def test_default_ranking_order():
    """Verify full default ranking order matches calibrated values."""
    rankings = {s: None for s in ALLOWED_SURFACES}
    result = surface_ranker.rank(rankings)
    scored = {s.surface: s.score for s in result.ranked}
    # init_ranking_weights is highest
    assert scored["init_ranking_weights"] > scored["context_ranking"]
    assert scored["context_ranking"] > scored["sandbox_visual_grammar"]
    assert scored["sandbox_visual_grammar"] > scored["prompt_compression"]
    assert scored["prompt_compression"] > scored["summarization_weights"]
    assert scored["summarization_weights"] > scored["skill_routing"]


def test_sandbox_visual_grammar_score_in_default_ranking():
    """sandbox_visual_grammar should score ~18.67 in default ranking."""
    rankings = {s: None for s in ALLOWED_SURFACES}
    result = surface_ranker.rank(rankings)
    scored = {s.surface: s.score for s in result.ranked}
    assert abs(scored["sandbox_visual_grammar"] - 18.6667) < 0.001


# ---------------------------------------------------------------------------
# Invariant 9: anti-loop fires at ≥2 repeats without new evidence
# ---------------------------------------------------------------------------

def test_anti_loop_count_fires_at_threshold():
    """_count_recent_same_target returns ≥2 for 2 consecutive identical targets."""
    state = {
        "target_history": [
            {"target": "init_ranking_weights", "score": 24.0},
            {"target": "init_ranking_weights", "score": 24.0},
        ]
    }
    from two_stage_loop import _count_recent_same_target, ANTI_LOOP_THRESHOLD
    count = _count_recent_same_target("init_ranking_weights", state)
    assert count >= ANTI_LOOP_THRESHOLD


def test_anti_loop_count_resets_on_different_target():
    """Anti-loop count resets when a different target appears in history."""
    state = {
        "target_history": [
            {"target": "init_ranking_weights", "score": 24.0},
            {"target": "context_ranking", "score": 19.2},    # different — breaks streak
            {"target": "init_ranking_weights", "score": 24.0},
        ]
    }
    from two_stage_loop import _count_recent_same_target
    count = _count_recent_same_target("init_ranking_weights", state)
    assert count == 1  # only the most recent streak counts


def test_anti_loop_empty_history_returns_zero():
    from two_stage_loop import _count_recent_same_target
    assert _count_recent_same_target("init_ranking_weights", {}) == 0


# ---------------------------------------------------------------------------
# Invariant 10: anti-loop does NOT fire with new evidence
# ---------------------------------------------------------------------------

def test_anti_loop_suppressed_by_new_evidence():
    """New evidence (changed ranking) prevents the anti-loop halt."""
    state = {
        "target_history": [
            {"target": "init_ranking_weights", "observed_ranking": 0.5},
            {"target": "init_ranking_weights", "observed_ranking": 0.5},
        ]
    }
    from two_stage_loop import _has_new_evidence
    current_rankings = {"init_ranking_weights": 0.9}  # different from 0.5
    assert _has_new_evidence("init_ranking_weights", current_rankings, state) is True


def test_anti_loop_same_evidence_no_new():
    """Same observed ranking → no new evidence."""
    state = {
        "target_history": [
            {"target": "init_ranking_weights", "observed_ranking": 0.8},
        ]
    }
    from two_stage_loop import _has_new_evidence
    current = {"init_ranking_weights": 0.8}
    assert _has_new_evidence("init_ranking_weights", current, state) is False


# ---------------------------------------------------------------------------
# Invariant 11: forbidden surfaces absent from ranking
# ---------------------------------------------------------------------------

def test_forbidden_surfaces_not_in_ranking():
    """Forbidden surfaces must never appear in ranking output."""
    rankings = {s: None for s in ALLOWED_SURFACES}
    result = surface_ranker.rank(rankings)
    ranked_names = {s.surface for s in result.ranked}
    for forbidden in surface_ranker.FORBIDDEN_SURFACES:
        assert not any(forbidden in name for name in ranked_names), (
            f"Forbidden domain {forbidden!r} found in ranking output: {ranked_names}"
        )


def test_assert_not_forbidden_raises_for_kernel():
    with pytest.raises(ValueError, match="FORBIDDEN SURFACE"):
        surface_ranker.assert_not_forbidden("oracle_town_kernel_routing")


def test_assert_not_forbidden_passes_for_allowed():
    surface_ranker.assert_not_forbidden("init_ranking_weights")
    surface_ranker.assert_not_forbidden("sandbox_visual_grammar")


# ---------------------------------------------------------------------------
# Invariant 13: observed ranking adjusts evidence_quality only
# ---------------------------------------------------------------------------

def test_observed_ranking_adjusts_evidence_quality():
    """High observed ranking for a surface raises its evidence_quality score."""
    low_obs = {s: None for s in ALLOWED_SURFACES}
    high_obs = {s: None for s in ALLOWED_SURFACES}
    high_obs["prompt_compression"] = 0.95  # high observed quality

    low_result = surface_ranker.rank(low_obs)
    high_result = surface_ranker.rank(high_obs)

    def _find(result, surface):
        return next(s for s in result.ranked if s.surface == surface)

    low_score = _find(low_result, "prompt_compression").score
    high_score = _find(high_result, "prompt_compression").score
    assert high_score > low_score


def test_observed_ranking_flags_evidence_override():
    rankings = {s: None for s in ALLOWED_SURFACES}
    rankings["context_ranking"] = 0.8
    result = surface_ranker.rank(rankings)
    cr = next(s for s in result.ranked if s.surface == "context_ranking")
    assert cr.evidence_override is True
    # Surface without observation should not have evidence_override
    ir = next(s for s in result.ranked if s.surface == "init_ranking_weights")
    assert ir.evidence_override is False


# ---------------------------------------------------------------------------
# Invariant 15: loop report always carries authority=False, ledger_effect='none'
# ---------------------------------------------------------------------------

def test_loop_report_authority_false_via_build_report():
    """_build_report must always emit authority=False and ledger_effect='none'."""
    from two_stage_loop import _build_report
    report = _build_report(
        target="init_ranking_weights",
        template={
            "hypothesis": "test",
            "tweak": "test",
            "metric": "test",
            "rule": "test",
            "next": "test",
        },
        dirty_verdict_summary="clean",
        packet_head="abc123",
        packet_status=PACKET_STATUS_WITNESSED,
        selected_score=24.0,
        ranked_surfaces=["init_ranking_weights"],
        anti_loop_fired=False,
        no_receipt=False,
        observed_at="2026-07-10T00:00:00Z",
    )
    assert report["authority"] is False
    assert report["ledger_effect"] == "none"
    assert report["reducer_required"] is True
    assert report["sovereign"] is False
    assert report["canon"] is False


def test_all_allowed_surfaces_covered():
    """All ALLOWED_SURFACES must appear in ranking output."""
    rankings = {s: None for s in ALLOWED_SURFACES}
    result = surface_ranker.rank(rankings)
    ranked_names = {s.surface for s in result.ranked}
    for surface in ALLOWED_SURFACES:
        assert surface in ranked_names


def test_dirty_state_summarize_reported():
    v = dirty_state.DirtyVerdict(dominates=False, reported_only=True)
    summary = dirty_state.summarize(v)
    assert "REPORTED" in summary
    assert "ranking" in summary.lower()


def test_dirty_state_summarize_no_receipt():
    v = dirty_state.DirtyVerdict(dominates=False, no_receipt=True,
                                  reasons=["replay_status=unknown"])
    summary = dirty_state.summarize(v)
    assert "NO_RECEIPT" in summary


def test_dirty_state_summarize_dirty():
    v = dirty_state.DirtyVerdict(dominates=True, reasons=["replay_status=mismatch"])
    summary = dirty_state.summarize(v)
    assert "DIRTY_DOMINATES" in summary
    assert "mismatch" in summary


def test_dirty_state_summarize_clean():
    v = dirty_state.DirtyVerdict(dominates=False)
    summary = dirty_state.summarize(v)
    assert "clean" in summary.lower()
