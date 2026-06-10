"""
test_evaluator.py — /init ranking quality scorer tests.
NON_SOVEREIGN. Tests scoring math only.
"""
from helen_kernel.evaluator import (
    coherence_score,
    evaluate,
    stability_score,
    top3_accuracy,
)


# --- top3_accuracy ---

def test_top3_accuracy_exact_match():
    assert top3_accuracy(["a", "b", "c"], ["a", "b", "c"]) == 1.0


def test_top3_accuracy_partial_match():
    assert top3_accuracy(["a", "x", "c"], ["a", "b", "c"]) == 2 / 3


def test_top3_accuracy_no_match():
    assert top3_accuracy(["x", "y", "z"], ["a", "b", "c"]) == 0.0


def test_top3_accuracy_empty_ranked():
    assert top3_accuracy([], ["a", "b", "c"]) == 0.0


def test_top3_accuracy_empty_truth():
    assert top3_accuracy(["a"], []) == 0.0


def test_top3_accuracy_only_first_three_ranked_count():
    # 4th and 5th items in ranked should not affect score
    assert top3_accuracy(["x", "x", "x", "a", "b"], ["a", "b", "c"]) == 0.0


# --- coherence_score ---

def test_coherence_score_perfect():
    ranked = ["a", "b", "c", "d", "e"]
    gt = ["a", "b", "c", "d", "e"]
    assert coherence_score(ranked, gt) == 1.0


def test_coherence_score_empty_inputs():
    assert coherence_score([], ["a", "b"]) == 0.0
    assert coherence_score(["a", "b"], []) == 0.0


def test_coherence_score_no_overlap():
    assert coherence_score(["x", "y", "z"], ["a", "b", "c"]) == 0.0


def test_coherence_score_bounded():
    ranked = ["c", "b", "a"]
    gt = ["a", "b", "c"]
    score = coherence_score(ranked, gt)
    assert 0.0 <= score <= 1.0


# --- stability_score ---

def test_stability_score_identical_runs():
    assert stability_score(["a", "b", "c"], ["a", "b", "c"]) == 1.0


def test_stability_score_no_overlap():
    assert stability_score(["a", "b", "c"], ["x", "y", "z"]) == 0.0


def test_stability_score_partial():
    s = stability_score(["a", "b", "c"], ["a", "x", "z"])
    assert s == 1 / 3


def test_stability_score_empty():
    assert stability_score([], ["a"]) == 0.0


# --- evaluate (composite) ---

def test_evaluate_perfect_score():
    ranked = ["a", "b", "c", "d", "e"]
    gt = ["a", "b", "c", "d", "e"]
    weights = {"recency_weight": 0.4}
    result = evaluate(ranked, gt, weights, stability_ranked=ranked)
    assert result.score == 1.0
    assert result.top3_accuracy == 1.0
    assert result.coherence == 1.0
    assert result.stability == 1.0


def test_evaluate_returns_eval_result():
    from helen_kernel.evaluator import EvalResult
    result = evaluate(["a"], ["a"], {})
    assert isinstance(result, EvalResult)


def test_evaluate_score_formula():
    # Force known values: acc=1.0, coh computed, stab=1.0 (no stability_ranked)
    ranked = ["a", "b", "c"]
    gt = ["a", "b", "c"]
    weights = {}
    result = evaluate(ranked, gt, weights)
    # stability defaults to 1.0 when stability_ranked is None
    assert result.stability == 1.0
    expected = round(0.5 * result.top3_accuracy + 0.3 * result.coherence + 0.2 * 1.0, 4)
    assert result.score == expected


def test_evaluate_carries_weights():
    weights = {"recency_weight": 0.99}
    result = evaluate(["a"], ["a"], weights)
    assert result.weights_used == weights


def test_evaluate_details_contain_top5_and_truth():
    ranked = ["a", "b", "c", "d", "e", "f"]
    gt = ["a", "b", "c"]
    result = evaluate(ranked, gt, {})
    assert result.details["ranked_top5"] == ["a", "b", "c", "d", "e"]
    assert result.details["ground_truth_top3"] == ["a", "b", "c"]
