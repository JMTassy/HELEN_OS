"""
evaluator.py — /init context ranking quality scorer.
NON_SOVEREIGN. Produces scores, not verdicts.
Authority: NONE

truth_score = 0.5 * top3_accuracy + 0.3 * coherence + 0.2 * stability
"""
from dataclasses import dataclass


@dataclass
class EvalResult:
    score: float
    top3_accuracy: float
    coherence: float
    stability: float
    weights_used: dict
    details: dict


def top3_accuracy(ranked: list[str], ground_truth: list[str]) -> float:
    if not ground_truth or not ranked:
        return 0.0
    hits = sum(1 for item in ranked[:3] if item in ground_truth[:3])
    return hits / max(len(ground_truth[:3]), 1)


def coherence_score(ranked: list[str], ground_truth: list[str]) -> float:
    """Spearman-like rank correlation over top-5. Bounded [0, 1]."""
    if not ranked or not ground_truth:
        return 0.0
    n = min(len(ranked), len(ground_truth), 5)
    if n == 0:
        return 0.0
    gt_index = {item: i for i, item in enumerate(ground_truth[:n])}
    rank_index = {item: i for i, item in enumerate(ranked[:n])}
    common = set(gt_index) & set(rank_index)
    if not common:
        return 0.0
    d_sq = sum((gt_index[k] - rank_index[k]) ** 2 for k in common)
    n_c = len(common)
    spearman = 1 - (6 * d_sq) / max(n_c * (n_c ** 2 - 1), 1)
    return max(0.0, min(1.0, (spearman + 1) / 2))


def stability_score(results_a: list[str], results_b: list[str]) -> float:
    """Fraction of top-3 items shared between two runs with identical weights."""
    if not results_a or not results_b:
        return 0.0
    top3_a = set(results_a[:3])
    return len(top3_a & set(results_b[:3])) / max(len(top3_a), 1)


def evaluate(
    ranked: list[str],
    ground_truth: list[str],
    weights_used: dict,
    stability_ranked: list[str] | None = None,
) -> EvalResult:
    acc = top3_accuracy(ranked, ground_truth)
    coh = coherence_score(ranked, ground_truth)
    stab = stability_score(ranked, stability_ranked) if stability_ranked is not None else 1.0
    score = 0.5 * acc + 0.3 * coh + 0.2 * stab
    return EvalResult(
        score=round(score, 4),
        top3_accuracy=round(acc, 4),
        coherence=round(coh, 4),
        stability=round(stab, 4),
        weights_used=weights_used,
        details={
            "ranked_top5": ranked[:5],
            "ground_truth_top3": ground_truth[:3],
        },
    )
