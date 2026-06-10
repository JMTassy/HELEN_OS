"""test_aura_score.py — HD-002: AuraMetrics integration with complexity_extractor.

Acceptance criteria:
  1. AuraMetrics can consume clutter and overcomplexity_flag from extractor output.
  2. Existing tests remain green (checked by pytest suite, not here).
  3. Regression test covers overbuilt composite graph.
  4. No canon or reducer mutation.
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pytest

from helen_video.aura_score import AuraMetrics, AuraVerdict, evaluate, from_complexity
from helen_video.complexity_extractor import ComplexityMetrics, extract


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_metrics(overlay_count=0, depth=1, clutter=0.0, overcomplexity=0.0, flag=False):
    return ComplexityMetrics(
        overlay_count=overlay_count,
        stream_count=1,
        depth=depth,
        clutter=clutter,
        overcomplexity=overcomplexity,
        flag=flag,
    )


# ── 1. AuraMetrics consumes clutter from ComplexityMetrics ───────────────────

def test_from_complexity_reads_clutter():
    m = _make_metrics(clutter=0.8, overcomplexity=0.0, flag=False)
    score = from_complexity(m)
    assert score.clutter == 0.8


def test_from_complexity_reads_overcomplexity():
    m = _make_metrics(clutter=0.0, overcomplexity=0.7, flag=False)
    score = from_complexity(m)
    assert score.overcomplexity == 0.7


def test_from_complexity_reads_flag():
    m = _make_metrics(clutter=0.0, overcomplexity=0.0, flag=True)
    score = from_complexity(m)
    assert score.overcomplexity_flag is True


# ── 2. Clean graph → CLEAR ────────────────────────────────────────────────────

def test_clean_graph_is_clear():
    m = _make_metrics(clutter=0.0, overcomplexity=0.0, flag=False)
    score = from_complexity(m)
    assert score.verdict == AuraVerdict.CLEAR
    assert score.aura_score > 0.60


def test_clear_has_no_notes():
    m = _make_metrics(clutter=0.0, overcomplexity=0.0, flag=False)
    score = from_complexity(m)
    assert score.notes == ()


# ── 3. overcomplexity_flag hard-floors score ──────────────────────────────────

def test_flag_forces_veto():
    m = _make_metrics(clutter=0.0, overcomplexity=0.0, flag=True)
    score = from_complexity(m)
    assert score.verdict == AuraVerdict.VETO


def test_flag_caps_aura_score():
    m = _make_metrics(clutter=0.0, overcomplexity=0.0, flag=True)
    score = from_complexity(m)
    assert score.aura_score <= 0.20


def test_flag_adds_note():
    m = _make_metrics(clutter=0.0, overcomplexity=0.0, flag=True)
    score = from_complexity(m)
    assert any("overcomplexity_flag" in n for n in score.notes)


# ── 4. CAUTION band ──────────────────────────────────────────────────────────

def test_moderate_clutter_is_caution():
    # clutter=0.8, overcomplexity=0.45 → raw=1-(0.32+0.18)=0.50 → CAUTION
    m = _make_metrics(clutter=0.8, overcomplexity=0.45, flag=False)
    score = from_complexity(m)
    assert score.verdict == AuraVerdict.CAUTION


def test_caution_note_includes_clutter():
    m = _make_metrics(clutter=0.6, overcomplexity=0.0, flag=False)
    score = from_complexity(m)
    assert any("clutter" in n for n in score.notes)


# ── 5. Regression: overbuilt composite graph ──────────────────────────────────

OVERBUILT_GRAPH = (
    "[v0][v1]overlay=x=0:y=0[o1];"
    "[o1][v2]overlay=x=100:y=0[o2];"
    "[o2][v3]overlay=x=200:y=0[o3];"
    "[o3]split[s1][s2];"
    "[s1][a1]blend=all_mode=addition[b1];"
    "[b1][s2]overlay=x=0:y=100[final]"
)

def test_overbuilt_graph_extracted_flag_is_true():
    m = extract(OVERBUILT_GRAPH)
    assert m.flag is True

def test_overbuilt_graph_clutter_at_cap():
    m = extract(OVERBUILT_GRAPH)
    assert m.clutter == 1.0

def test_overbuilt_graph_aura_score_veto():
    m = extract(OVERBUILT_GRAPH)
    score = from_complexity(m)
    assert score.verdict == AuraVerdict.VETO

def test_overbuilt_graph_aura_score_floored():
    m = extract(OVERBUILT_GRAPH)
    score = from_complexity(m)
    assert score.aura_score <= 0.20

def test_overbuilt_graph_has_veto_note():
    m = extract(OVERBUILT_GRAPH)
    score = from_complexity(m)
    assert any("overcomplexity_flag" in n for n in score.notes)


# ── 6. Extra penalty propagates ───────────────────────────────────────────────

def test_extra_penalty_lowers_score():
    base = evaluate(0.0, 0.0, False, extra_penalty=0.0)
    penalised = evaluate(0.0, 0.0, False, extra_penalty=0.5)
    assert penalised.aura_score < base.aura_score


def test_extra_penalty_validation():
    with pytest.raises(ValueError):
        evaluate(0.0, 0.0, False, extra_penalty=1.5)


# ── 7. Direct evaluate() matches from_complexity() ───────────────────────────

def test_evaluate_matches_from_complexity():
    m = _make_metrics(clutter=0.4, overcomplexity=0.3, flag=False)
    via_convenience = from_complexity(m)
    via_direct = evaluate(0.4, 0.3, False)
    assert via_convenience == via_direct


# ── 8. Input validation ───────────────────────────────────────────────────────

def test_invalid_clutter_raises():
    with pytest.raises(ValueError):
        evaluate(1.5, 0.0, False)

def test_invalid_overcomplexity_raises():
    with pytest.raises(ValueError):
        evaluate(0.0, -0.1, False)


# ── 9. AuraMetrics is immutable ──────────────────────────────────────────────

def test_aurametrics_is_frozen():
    m = _make_metrics()
    score = from_complexity(m)
    with pytest.raises((AttributeError, TypeError)):
        score.verdict = AuraVerdict.CLEAR  # type: ignore[misc]


# ── 10. No canon / reducer mutation ──────────────────────────────────────────

def test_no_module_level_state_mutation():
    import helen_video.aura_score as mod
    before = dict(vars(mod))
    from_complexity(_make_metrics())
    after = dict(vars(mod))
    # Only __pycache__ keys are allowed to differ
    added = {k for k in after if k not in before and not k.startswith("_")}
    assert not added, f"Module state mutated: {added}"
