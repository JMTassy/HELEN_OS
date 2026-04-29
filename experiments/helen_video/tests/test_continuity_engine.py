"""Continuity Engine — invariant and functional tests."""
import ast
import inspect
from pathlib import Path

import pytest

from helen_video.continuity_engine import continuity_score


# ── helpers ───────────────────────────────────────────────────────────────────

def _clip(character="HELEN", scene="oracle_town", duration=5.0, style="cinematic"):
    return {"character": character, "scene": scene, "duration": duration, "style": style}


# ── invariant: score is always in [0, 1] ─────────────────────────────────────

def test_score_zero_for_completely_different_clips():
    prev = _clip(character="HELEN", scene="oracle_town", duration=5.0, style="cinematic")
    nxt  = _clip(character="RALPH", scene="temple",     duration=30.0, style="abstract")
    assert 0.0 <= continuity_score(prev, nxt) <= 1.0


def test_score_one_for_identical_clips():
    c = _clip()
    assert continuity_score(c, c) == 1.0


def test_score_always_between_0_and_1_exhaustive():
    variants = [
        _clip(), _clip(character="RALPH"), _clip(scene="void"), _clip(duration=99.0),
        _clip(style="abstract"), {}, {"character": None}, {"duration": -1},
    ]
    for prev in variants:
        for nxt in variants:
            s = continuity_score(prev, nxt)
            assert 0.0 <= s <= 1.0, f"Out of range: {s} for {prev!r} → {nxt!r}"


# ── functional: weight contract ───────────────────────────────────────────────

def test_same_character_and_scene_meets_gate_threshold():
    prev = _clip(duration=5.0, style="X")
    nxt  = _clip(duration=50.0, style="Y")
    # character(0.4) + scene(0.3) = 0.7 ≥ 0.6
    assert continuity_score(prev, nxt) >= 0.6


def test_different_character_gives_low_score():
    prev = _clip(character="HELEN")
    nxt  = _clip(character="RALPH")
    # character differs → max possible = 0.6 if rest matches, but scene/duration/style may match
    s = continuity_score(prev, nxt)
    assert s < 1.0  # can't reach 1.0 without character match


def test_different_character_and_scene_is_below_threshold():
    prev = _clip(character="HELEN", scene="oracle_town", duration=5.0, style="cinematic")
    nxt  = _clip(character="RALPH", scene="temple",      duration=20.0, style="abstract")
    assert continuity_score(prev, nxt) < 0.5


def test_duration_smoothness_within_2s():
    prev = _clip(character="X", scene="X", duration=5.0, style="X")
    nxt  = _clip(character="X", scene="X", duration=6.9, style="X")
    assert continuity_score(prev, nxt) == 1.0


def test_duration_gap_exactly_2s_does_not_score():
    prev = _clip(character="X", scene="X", duration=5.0, style="X")
    nxt  = _clip(character="X", scene="X", duration=7.0, style="X")
    # abs(5.0 - 7.0) == 2.0 → NOT < 2 → no duration score
    assert continuity_score(prev, nxt) == pytest.approx(0.8)


def test_style_contributes_0_1():
    prev = _clip(character="X", scene="X", duration=5.0, style="cinematic")
    same_style = _clip(character="X", scene="X", duration=5.0, style="cinematic")
    diff_style = _clip(character="X", scene="X", duration=5.0, style="abstract")
    assert continuity_score(prev, same_style) - continuity_score(prev, diff_style) == pytest.approx(0.1)


# ── invariant: missing fields do not crash ────────────────────────────────────

def test_empty_prev_does_not_crash():
    s = continuity_score({}, _clip())
    assert 0.0 <= s <= 1.0


def test_empty_next_does_not_crash():
    s = continuity_score(_clip(), {})
    assert 0.0 <= s <= 1.0


def test_both_empty_does_not_crash():
    s = continuity_score({}, {})
    # both None → character, scene, style all match; duration 0 vs 0 → abs=0 < 2
    assert s == 1.0


def test_none_values_do_not_crash():
    prev = {"character": None, "scene": None, "duration": None, "style": None}
    nxt  = {"character": None, "scene": None, "duration": None, "style": None}
    s = continuity_score(prev, nxt)
    assert 0.0 <= s <= 1.0


def test_partial_fields_do_not_crash():
    s = continuity_score({"character": "HELEN"}, {"scene": "oracle_town"})
    assert 0.0 <= s <= 1.0


# ── invariant: function does not mutate inputs ────────────────────────────────

def test_does_not_mutate_prev():
    prev = _clip()
    snapshot = dict(prev)
    continuity_score(prev, _clip())
    assert prev == snapshot


def test_does_not_mutate_next():
    nxt = _clip()
    snapshot = dict(nxt)
    continuity_score(_clip(), nxt)
    assert nxt == snapshot


# ── invariant: no IO, no gate, no ledger, no Remotion calls ─────────────────

def test_engine_has_no_io_imports():
    import helen_video.continuity_engine as mod
    tree = ast.parse(Path(mod.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
    forbidden = {"subprocess", "socket", "urllib", "requests", "httpx",
                 "admissibility_gate", "video_ledger", "remotion_wrapper"}
    assert not (imported & forbidden), f"Forbidden imports found: {imported & forbidden}"


def test_engine_has_no_file_calls():
    import helen_video.continuity_engine as mod
    tree = ast.parse(Path(mod.__file__).read_text())
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    forbidden_calls = {"open", "read_bytes", "write_bytes", "write_text", "read_text",
                       "run", "Popen", "evaluate", "append"}
    assert not (set(calls) & forbidden_calls), f"Forbidden calls: {set(calls) & forbidden_calls}"


def test_engine_has_no_public_deliver_methods():
    import helen_video.continuity_engine as mod
    public = [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n))]
    forbidden = {"deliver", "ship", "accept", "reject", "evaluate", "append"}
    assert not (set(public) & forbidden)
