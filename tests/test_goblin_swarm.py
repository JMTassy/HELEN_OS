"""Constitutional tests for the goblin swarm layer: evidence bridge, FABLE gate,
operator-only outcome pen, and deterministic surface ranking.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Invariants tested:
  1.  evidence_bridge: missing loop_state file → all None (no invented signal)
  2.  evidence_bridge: malformed JSON → all None (fail-closed)
  3.  evidence_bridge: KEEP-only history → strong positive signal (0.9)
  4.  evidence_bridge: DISCARD-only history → strong negative signal (0.1)
  5.  evidence_bridge: MEASURED contributes +0.1 mild-positive bump
  6.  evidence_bridge: scores clamped to [0.05, 0.95] — evidence never certainty
  7.  evidence_bridge: PENDING/absent outcomes contribute nothing (stay None)
  8.  evidence_bridge: deterministic — same input twice → identical output
  9.  fable_validate: clean report passes; authority=true / ledger_effect≠none /
      forbidden TARGET / empty TWEAK / missing reducer_required all rejected
  10. fable_validate: sentinel HOLD_FOR_OPERATOR is a lawful halt (validates clean)
  11. record_outcome: KEEP/DISCARD is operator-only — goblin actor refused
  12. record_outcome: invalid outcome raises ValueError
  13. record_outcome: updates the most recent outcome-less entry only
  14. record_outcome: no file / no matching entry → False (no phantom writes)
  15. surface_ranker: 19.2 anti-loop tie resolves deterministically
      (context_ranking wins by alphabetical tie-break) and full order is stable
  16. ALLOWED_SURFACES is set-identical across evidence_bridge, surface_ranker,
      and observation_packet
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure temple/autoresearch is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "temple" / "autoresearch"))

import evidence_bridge
import goblin_swarm
import surface_ranker
from observation_packet import ALLOWED_SURFACES as OP_ALLOWED_SURFACES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_state(tmp_path: Path, history: list[dict]) -> Path:
    """Write a loop_state.json with the given target_history into tmp_path."""
    path = tmp_path / "loop_state.json"
    path.write_text(
        json.dumps({"target_history": history}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def _entry(target: str, outcome: str | None = None, **extra) -> dict:
    e = {"target": target, "score": 1.0, **extra}
    if outcome is not None:
        e["outcome"] = outcome
        # the bridge refuses KEEP/DISCARD not stamped by the operator;
        # fixtures model lawfully-recorded verdicts unless a test overrides
        if outcome in ("KEEP", "DISCARD") and "outcome_actor" not in extra:
            e["outcome_actor"] = "operator"
    return e


def test_evidence_bridge_refuses_unstamped_verdicts(tmp_path):
    """Forged KEEP/DISCARD without outcome_actor='operator' steers nothing."""
    path = _write_state(tmp_path, [
        _entry("skill_routing", "KEEP", outcome_actor="goblin_swarm"),
        {"target": "context_ranking", "score": 1.0, "outcome": "KEEP"},
    ])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["skill_routing"] is None
    assert rankings["context_ranking"] is None


def test_operator_can_upgrade_pending_and_measured(tmp_path):
    """The swarm stamps PENDING/MEASURED; the operator pen must still land."""
    path = _write_state(tmp_path, [
        _entry("prompt_compression", "PENDING", outcome_actor="goblin_swarm"),
    ])
    ok = goblin_swarm.record_outcome(
        "prompt_compression", "KEEP", loop_state_path=path, actor="operator",
        note="baseline acceptable",
    )
    assert ok is True
    entries = json.loads(path.read_text())["target_history"]
    assert entries[0]["outcome"] == "KEEP"
    assert entries[0]["outcome_actor"] == "operator"
    assert entries[0]["outcome_note"] == "baseline acceptable"
    # final verdicts are never rewritten
    assert goblin_swarm.record_outcome(
        "prompt_compression", "DISCARD", loop_state_path=path, actor="operator",
    ) is False


def test_goblins_cannot_upgrade_stamped_entries(tmp_path):
    """Goblin MEASURED only lands on outcome-less entries, never overwrites."""
    path = _write_state(tmp_path, [
        _entry("skill_routing", "PENDING", outcome_actor="goblin_swarm"),
    ])
    assert goblin_swarm.record_outcome(
        "skill_routing", "MEASURED", 1.0, loop_state_path=path,
    ) is False


def test_report_hash_excludes_wall_clock():
    """Content hashes must be replay-stable: volatile keys never contribute."""
    base = {"TARGET": "prompt_compression", "selected_score": 24.0}
    h1 = goblin_swarm._sha256_canon({**base, "observed_at": "2026-07-10T00:00:01Z"})
    h2 = goblin_swarm._sha256_canon({**base, "observed_at": "2026-07-10T23:59:59Z",
                                     "swarm_started": "x", "run_at": "y"})
    assert h1 == h2
    h3 = goblin_swarm._sha256_canon({**base, "selected_score": 19.2})
    assert h3 != h1


def test_measurers_cover_all_allowed_surfaces():
    """Every allowed surface has a deterministic baseline instrument."""
    assert set(goblin_swarm.MEASURERS) == set(surface_ranker.ALLOWED_SURFACES)
    for name, fn in goblin_swarm.MEASURERS.items():
        a, b = fn(), fn()
        assert a == b, f"measurer {name} not deterministic"
        assert isinstance(a, float)


def _clean_report(**overrides) -> dict:
    """A report that must pass fable_validate unmodified."""
    report = {
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "TARGET": "prompt_compression",
        "TWEAK": "trim CORE_PROMPT by 10%, revert by restoring the string",
        "RULE": "keep if token count drops with no invariant loss, else discard",
    }
    report.update(overrides)
    return report


# ---------------------------------------------------------------------------
# Invariant 1 & 2: evidence bridge fail-closed
# ---------------------------------------------------------------------------

def test_evidence_bridge_missing_file_all_none(tmp_path):
    """No loop_state file → every surface is None (missing evidence stays missing)."""
    rankings = evidence_bridge.observed_rankings(tmp_path / "does_not_exist.json")
    assert set(rankings) == set(evidence_bridge.ALLOWED_SURFACES)
    assert all(v is None for v in rankings.values())


def test_evidence_bridge_malformed_json_all_none(tmp_path):
    """Malformed JSON must fail closed to all-None, never raise."""
    path = tmp_path / "loop_state.json"
    path.write_text("{not json at all", encoding="utf-8")
    rankings = evidence_bridge.observed_rankings(path)
    assert all(v is None for v in rankings.values())


def test_evidence_bridge_non_list_history_all_none(tmp_path):
    """target_history that is not a list → fail-closed to all None."""
    path = tmp_path / "loop_state.json"
    path.write_text(json.dumps({"target_history": "corrupted"}), encoding="utf-8")
    rankings = evidence_bridge.observed_rankings(path)
    assert all(v is None for v in rankings.values())


# ---------------------------------------------------------------------------
# Invariants 3-6: signal formula
# ---------------------------------------------------------------------------

def test_evidence_bridge_keep_only_high_signal(tmp_path):
    """KEEP-only history → 0.5 + 0.4 = 0.9."""
    path = _write_state(tmp_path, [
        _entry("prompt_compression", "KEEP"),
        _entry("prompt_compression", "KEEP"),
    ])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["prompt_compression"] == pytest.approx(0.9)


def test_evidence_bridge_discard_only_low_signal(tmp_path):
    """DISCARD-only history → 0.5 - 0.4 = 0.1."""
    path = _write_state(tmp_path, [
        _entry("skill_routing", "DISCARD"),
        _entry("skill_routing", "DISCARD"),
    ])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["skill_routing"] == pytest.approx(0.1)


def test_evidence_bridge_measured_adds_bump(tmp_path):
    """MEASURED alone → neutral 0.5 plus the +0.1 data-exists bump = 0.6."""
    path = _write_state(tmp_path, [_entry("summarization_weights", "MEASURED")])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["summarization_weights"] == pytest.approx(0.6)


def test_evidence_bridge_measured_bump_on_balanced_history(tmp_path):
    """KEEP+DISCARD balances to 0.5; adding MEASURED lifts it by exactly 0.1."""
    balanced = [
        _entry("context_ranking", "KEEP"),
        _entry("context_ranking", "DISCARD"),
    ]
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    without = evidence_bridge.observed_rankings(_write_state(dir_a, balanced))
    with_measured = evidence_bridge.observed_rankings(
        _write_state(dir_b, balanced + [_entry("context_ranking", "MEASURED")])
    )
    assert without["context_ranking"] == pytest.approx(0.5)
    assert with_measured["context_ranking"] == pytest.approx(0.6)


def test_evidence_bridge_ceiling_clamp(tmp_path):
    """9×KEEP + 1×MEASURED → raw 0.96, clamped to ceiling 0.95."""
    history = [_entry("init_ranking_weights", "KEEP") for _ in range(9)]
    history.append(_entry("init_ranking_weights", "MEASURED"))
    path = _write_state(tmp_path, history)
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["init_ranking_weights"] == pytest.approx(0.95)
    assert all(v is None or 0.05 <= v <= 0.95 for v in rankings.values())


# ---------------------------------------------------------------------------
# Invariant 7: PENDING / absent contribute nothing
# ---------------------------------------------------------------------------

def test_evidence_bridge_pending_only_stays_none(tmp_path):
    """PENDING outcomes are proposals-only: no data, no signal."""
    path = _write_state(tmp_path, [
        _entry("prompt_compression", "PENDING"),
        _entry("prompt_compression", "PENDING"),
    ])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["prompt_compression"] is None


def test_evidence_bridge_absent_outcome_stays_none(tmp_path):
    """Entries with no outcome field at all contribute nothing."""
    path = _write_state(tmp_path, [
        _entry("sandbox_visual_grammar"),
        _entry("sandbox_visual_grammar"),
    ])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["sandbox_visual_grammar"] is None


def test_evidence_bridge_untouched_surfaces_stay_none(tmp_path):
    """Only surfaces with contributing outcomes get a score; the rest stay None."""
    path = _write_state(tmp_path, [_entry("prompt_compression", "KEEP")])
    rankings = evidence_bridge.observed_rankings(path)
    assert rankings["prompt_compression"] == pytest.approx(0.9)
    for surface in evidence_bridge.ALLOWED_SURFACES:
        if surface != "prompt_compression":
            assert rankings[surface] is None


# ---------------------------------------------------------------------------
# Invariant 8: evidence bridge determinism
# ---------------------------------------------------------------------------

def test_evidence_bridge_deterministic(tmp_path):
    """Same input read twice → byte-identical output dict."""
    path = _write_state(tmp_path, [
        _entry("prompt_compression", "KEEP"),
        _entry("skill_routing", "DISCARD"),
        _entry("summarization_weights", "MEASURED"),
        _entry("context_ranking", "PENDING"),
        _entry("init_ranking_weights"),
    ])
    first = evidence_bridge.observed_rankings(path)
    second = evidence_bridge.observed_rankings(path)
    assert first == second
    assert list(first.keys()) == list(second.keys())


# ---------------------------------------------------------------------------
# Invariants 9-10: FABLE validation gate (fail-closed)
# ---------------------------------------------------------------------------

def test_fable_clean_report_passes():
    verdict = goblin_swarm.fable_validate(_clean_report())
    assert verdict.ok is True
    assert verdict.reasons == []


def test_fable_rejects_authority_true():
    verdict = goblin_swarm.fable_validate(_clean_report(authority=True))
    assert verdict.ok is False
    assert any("authority" in r for r in verdict.reasons)


def test_fable_rejects_ledger_effect_not_none():
    verdict = goblin_swarm.fable_validate(_clean_report(ledger_effect="append"))
    assert verdict.ok is False
    assert any("ledger_effect" in r for r in verdict.reasons)


def test_fable_rejects_forbidden_target():
    verdict = goblin_swarm.fable_validate(_clean_report(TARGET="kernel_tuning"))
    assert verdict.ok is False
    assert any("TARGET" in r for r in verdict.reasons)


def test_fable_sentinel_hold_for_operator_passes():
    """Lawful halts validate clean — HOLD_FOR_OPERATOR is not a violation."""
    verdict = goblin_swarm.fable_validate(_clean_report(TARGET="HOLD_FOR_OPERATOR"))
    assert verdict.ok is True
    assert verdict.reasons == []


def test_fable_rejects_empty_tweak():
    verdict = goblin_swarm.fable_validate(_clean_report(TWEAK="   "))
    assert verdict.ok is False
    assert any("TWEAK" in r for r in verdict.reasons)


def test_fable_rejects_missing_reducer_required():
    report = _clean_report()
    del report["reducer_required"]
    verdict = goblin_swarm.fable_validate(report)
    assert verdict.ok is False
    assert any("reducer_required" in r for r in verdict.reasons)


# ---------------------------------------------------------------------------
# Invariants 11-14: outcome recording — operator-only verdicts
# ---------------------------------------------------------------------------

def test_record_outcome_goblin_keep_refused(tmp_path):
    """A goblin actor attempting KEEP must be refused (fail-closed)."""
    path = _write_state(tmp_path, [_entry("prompt_compression")])
    with pytest.raises(PermissionError, match="operator"):
        goblin_swarm.record_outcome(
            "prompt_compression", "KEEP",
            loop_state_path=path, actor="goblin_swarm",
        )
    # File must be untouched — the refusal happens before any read/write
    state = json.loads(path.read_text(encoding="utf-8"))
    assert "outcome" not in state["target_history"][0]


def test_record_outcome_goblin_discard_refused(tmp_path):
    path = _write_state(tmp_path, [_entry("prompt_compression")])
    with pytest.raises(PermissionError):
        goblin_swarm.record_outcome(
            "prompt_compression", "DISCARD", loop_state_path=path,
        )


def test_record_outcome_operator_keep_succeeds(tmp_path):
    path = _write_state(tmp_path, [_entry("prompt_compression")])
    ok = goblin_swarm.record_outcome(
        "prompt_compression", "KEEP", loop_state_path=path, actor="operator",
    )
    assert ok is True
    state = json.loads(path.read_text(encoding="utf-8"))
    entry = state["target_history"][0]
    assert entry["outcome"] == "KEEP"
    assert entry["outcome_actor"] == "operator"
    assert "outcome_at" in entry


def test_record_outcome_goblin_measured_allowed(tmp_path):
    """Goblins may record MEASURED (a number, not a verdict)."""
    path = _write_state(tmp_path, [_entry("summarization_weights")])
    ok = goblin_swarm.record_outcome(
        "summarization_weights", "MEASURED", 0.42, loop_state_path=path,
    )
    assert ok is True
    state = json.loads(path.read_text(encoding="utf-8"))
    entry = state["target_history"][0]
    assert entry["outcome"] == "MEASURED"
    assert entry["measured"] == pytest.approx(0.42)


def test_record_outcome_invalid_outcome_raises(tmp_path):
    path = _write_state(tmp_path, [_entry("prompt_compression")])
    with pytest.raises(ValueError, match="invalid outcome"):
        goblin_swarm.record_outcome(
            "prompt_compression", "SHIP_IT", loop_state_path=path, actor="operator",
        )


def test_record_outcome_updates_most_recent_outcome_less_only(tmp_path):
    """Only the most recent outcome-less entry for the target is updated."""
    path = _write_state(tmp_path, [
        _entry("prompt_compression", marker="older"),
        _entry("prompt_compression", "KEEP", marker="already_decided"),
        _entry("prompt_compression", marker="newest"),
    ])
    ok = goblin_swarm.record_outcome(
        "prompt_compression", "DISCARD", loop_state_path=path, actor="operator",
    )
    assert ok is True
    history = json.loads(path.read_text(encoding="utf-8"))["target_history"]
    assert history[2]["marker"] == "newest"
    assert history[2]["outcome"] == "DISCARD"
    assert "outcome" not in history[0]            # older pending entry untouched
    assert history[1]["outcome"] == "KEEP"        # existing verdict never overwritten


def test_record_outcome_no_matching_entry_returns_false(tmp_path):
    """All entries already decided (or wrong target) → False, file unchanged."""
    path = _write_state(tmp_path, [_entry("prompt_compression", "KEEP")])
    before = path.read_text(encoding="utf-8")
    ok = goblin_swarm.record_outcome(
        "prompt_compression", "DISCARD", loop_state_path=path, actor="operator",
    )
    assert ok is False
    assert path.read_text(encoding="utf-8") == before
    # Different target with no history at all
    assert goblin_swarm.record_outcome(
        "skill_routing", "MEASURED", loop_state_path=path,
    ) is False


def test_record_outcome_missing_file_returns_false(tmp_path):
    ok = goblin_swarm.record_outcome(
        "prompt_compression", "MEASURED",
        loop_state_path=tmp_path / "absent.json",
    )
    assert ok is False


# ---------------------------------------------------------------------------
# Invariant 15: surface ranker tie-break determinism
# ---------------------------------------------------------------------------

def test_ranker_anti_loop_tie_is_deterministic():
    """init_ranking_weights 24.0 × 0.8 penalty == context_ranking 19.2 exactly.

    The winner must be a pure function of inputs: alphabetical tie-break
    selects context_ranking, never a hash-order accident.
    """
    rankings = {s: None for s in surface_ranker.ALLOWED_SURFACES}
    result = surface_ranker.rank(
        rankings, anti_loop_targets=["init_ranking_weights"],
    )
    scored = {s.surface: s.score for s in result.ranked}
    assert scored["init_ranking_weights"] == pytest.approx(19.2)
    assert scored["context_ranking"] == pytest.approx(19.2)
    assert result.selected == "context_ranking"
    assert result.selected_score == pytest.approx(19.2)
    # Tied pair must be adjacent and alphabetically ordered
    order = [s.surface for s in result.ranked]
    assert order.index("context_ranking") + 1 == order.index("init_ranking_weights")


def test_ranker_full_order_stable_across_calls():
    """Repeated calls with identical inputs → identical full ranked order."""
    rankings = {s: None for s in surface_ranker.ALLOWED_SURFACES}
    orders = [
        tuple(
            (s.surface, s.score)
            for s in surface_ranker.rank(
                rankings, anti_loop_targets=["init_ranking_weights"],
            ).ranked
        )
        for _ in range(10)
    ]
    assert len(set(orders)) == 1


# ---------------------------------------------------------------------------
# Invariant 16: ALLOWED_SURFACES consistency across modules
# ---------------------------------------------------------------------------

def test_allowed_surfaces_consistent_across_modules():
    """evidence_bridge, surface_ranker, observation_packet must agree exactly."""
    eb = set(evidence_bridge.ALLOWED_SURFACES)
    sr = set(surface_ranker.ALLOWED_SURFACES)
    op = set(OP_ALLOWED_SURFACES)
    assert eb == sr == op


def test_allowed_surfaces_never_forbidden():
    """No allowed surface may match a forbidden domain substring."""
    for surface in surface_ranker.ALLOWED_SURFACES:
        surface_ranker.assert_not_forbidden(surface)
