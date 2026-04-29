"""Sequence Optimizer — invariant and functional tests."""
import ast
import math
from itertools import permutations
from pathlib import Path

import pytest

from helen_video.sequence_optimizer import sequence_score, best_sequence


# ── helpers ───────────────────────────────────────────────────────────────────

def _clip(
    id="c1",
    character="HELEN",
    scene="oracle_town",
    duration=5.0,
    style="cinematic",
    pipeline_score=0.8,
    output_score=0.9,
    operator_decision="KEEP",
):
    return {
        "id": id,
        "character": character,
        "scene": scene,
        "duration": duration,
        "style": style,
        "pipeline_score": pipeline_score,
        "output_score": output_score,
        "operator_decision": operator_decision,
    }


# ── sequence_score: operator_decision gate ────────────────────────────────────

def test_non_keep_clip_returns_neg_inf():
    seq = [_clip(operator_decision="REJECT")]
    assert sequence_score(seq) == -float("inf")


def test_any_non_keep_in_sequence_returns_neg_inf():
    seq = [_clip(id="a"), _clip(id="b", operator_decision="PENDING"), _clip(id="c")]
    assert sequence_score(seq) == -float("inf")


def test_all_keep_clips_return_positive_score():
    seq = [_clip(id="a"), _clip(id="b")]
    assert sequence_score(seq) > 0.0


def test_empty_sequence_returns_zero():
    assert sequence_score([]) == 0.0


# ── sequence_score: clip contribution ────────────────────────────────────────

def test_single_clip_score_is_pipeline_plus_output_halved():
    clip = _clip(pipeline_score=0.6, output_score=0.8)
    expected = 0.5 * 0.6 + 0.5 * 0.8
    assert sequence_score([clip]) == pytest.approx(expected)


def test_continuity_bonus_added_from_second_clip():
    a = _clip(id="a", character="HELEN", scene="oracle_town")
    b = _clip(id="b", character="HELEN", scene="oracle_town")
    # Both clips identical → continuity = 1.0 → bonus = 5.0
    single_score = sequence_score([a])
    pair_score = sequence_score([a, b])
    assert pair_score > single_score + 4.9  # at least near +5


def test_low_continuity_gives_smaller_bonus():
    a = _clip(id="a", character="HELEN",  scene="oracle_town", style="cinematic", duration=5.0)
    b = _clip(id="b", character="RALPH",  scene="temple",      style="abstract",  duration=30.0)
    # character mismatch + scene mismatch + duration gap > 2 + style mismatch → score = 0.0
    bonus = 0.0 * 5.0
    base = (0.5 * a["pipeline_score"] + 0.5 * a["output_score"] +
            0.5 * b["pipeline_score"] + 0.5 * b["output_score"])
    assert sequence_score([a, b]) == pytest.approx(base + bonus)


# ── best_sequence: returns the optimal ordering ───────────────────────────────

def test_best_sequence_prefers_high_continuity_order():
    helen_a = _clip(id="h1", character="HELEN", scene="oracle_town")
    helen_b = _clip(id="h2", character="HELEN", scene="oracle_town")
    ralph   = _clip(id="r1", character="RALPH", scene="temple")

    result = best_sequence([ralph, helen_a, helen_b])
    assert result is not None
    # The two HELEN clips should be adjacent (either order) for max continuity
    ids = [c["id"] for c in result]
    idx_h1 = ids.index("h1")
    idx_h2 = ids.index("h2")
    assert abs(idx_h1 - idx_h2) == 1


def test_best_sequence_returns_none_when_no_keep_clip():
    clips = [_clip(operator_decision="REJECT"), _clip(operator_decision="PENDING")]
    assert best_sequence(clips) is None


def test_best_sequence_single_keep_clip():
    c = _clip()
    result = best_sequence([c])
    assert result == [c]


def test_best_sequence_empty_input():
    result = best_sequence([])
    assert result == []


def test_best_sequence_scores_higher_than_worst_permutation():
    a = _clip(id="a", character="HELEN", scene="oracle_town", pipeline_score=0.9, output_score=0.9)
    b = _clip(id="b", character="HELEN", scene="oracle_town", pipeline_score=0.9, output_score=0.9)
    c = _clip(id="c", character="RALPH", scene="temple",      pipeline_score=0.9, output_score=0.9)

    best = best_sequence([a, b, c])
    assert best is not None
    best_s = sequence_score(best)
    # Verify it beats at least one other ordering
    scores = [sequence_score(list(p)) for p in permutations([a, b, c])]
    assert best_s >= max(scores) - 1e-9


# ── invariant: no mutation ────────────────────────────────────────────────────

def test_sequence_score_does_not_mutate_clips():
    clips = [_clip(id="a"), _clip(id="b")]
    snapshots = [dict(c) for c in clips]
    sequence_score(clips)
    assert clips == snapshots


def test_best_sequence_does_not_mutate_input():
    clips = [_clip(id="a"), _clip(id="b")]
    snapshots = [dict(c) for c in clips]
    best_sequence(clips)
    assert clips == snapshots


# ── invariant: deterministic ──────────────────────────────────────────────────

def test_sequence_score_is_deterministic():
    seq = [_clip(id="a"), _clip(id="b")]
    assert sequence_score(seq) == sequence_score(seq)


def test_best_sequence_is_deterministic():
    clips = [_clip(id="a"), _clip(id="b"), _clip(id="c", character="RALPH", scene="temple")]
    r1 = best_sequence(clips)
    r2 = best_sequence(clips)
    assert [c["id"] for c in r1] == [c["id"] for c in r2]


# ── invariant: no IO / no ledger / no Remotion ───────────────────────────────

def test_optimizer_has_no_io_imports():
    import helen_video.sequence_optimizer as mod
    tree = ast.parse(Path(mod.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
    forbidden = {"subprocess", "socket", "urllib", "requests", "httpx",
                 "video_ledger", "remotion_wrapper", "admissibility_gate"}
    assert not (imported & forbidden), f"Forbidden imports: {imported & forbidden}"


def test_optimizer_has_no_public_deliver_methods():
    import helen_video.sequence_optimizer as mod
    public = [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n))]
    forbidden = {"deliver", "ship", "accept", "reject", "evaluate", "append"}
    assert not (set(public) & forbidden)
