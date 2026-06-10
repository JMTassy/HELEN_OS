"""
autoresearch_loop.py — Bounded parameter search over /init ranking weights.
NON_SOVEREIGN. Mutates ranking_config only.
Never touches: ledger, memory, identity, reducer, replay, schemas.
Authority: NONE | Admission: FORBIDDEN
"""
import copy
from typing import Callable

from helen_kernel.evaluator import evaluate
from helen_kernel.experiment_log import ExperimentEntry, ExperimentLog


IMMUTABLE_PATHS = frozenset({
    "reducer", "ledger", "replay", "schemas",
    "memory_identity", "init_contract", "authority_model",
})

MUTABLE_PARAMS = frozenset({
    "recency_weight", "relevance_weight", "coherence_weight",
    "compression_threshold", "routing_score_floor",
})


def _assert_no_sovereign_mutation(weights: dict) -> None:
    for key in weights:
        if key in IMMUTABLE_PATHS:
            raise ValueError(f"SOVEREIGN_MUTATION_BLOCKED: '{key}' is immutable")


def _mutable_keys(weights: dict) -> list[str]:
    return sorted(k for k in weights if k in MUTABLE_PARAMS)


def _mutate_weights(weights: dict, epoch: int, step: float = 0.05) -> dict:
    """
    Perturb one MUTABLE_PARAM per epoch (round-robin by epoch index).
    Direction alternates by epoch parity. Values clamped to [0.0, 1.0].
    Deterministic — no random() calls.
    """
    mutated = copy.deepcopy(weights)
    keys = _mutable_keys(weights)
    if not keys:
        return mutated
    key = keys[epoch % len(keys)]
    direction = 1 if epoch % 2 == 0 else -1
    mutated[key] = round(max(0.0, min(1.0, weights[key] + direction * step)), 4)
    return mutated


def _describe_failure(ranked: list[str], ground_truth: list[str]) -> str:
    top3 = set(ranked[:3])
    gt3 = set(ground_truth[:3])
    missed = sorted(gt3 - top3)
    wrong = sorted(top3 - gt3)
    parts = []
    if missed:
        parts.append(f"missed={missed}")
    if wrong:
        parts.append(f"spurious={wrong}")
    return "; ".join(parts) if parts else "no_improvement"


def run_autoresearch(
    init_fn: Callable[[dict], list[str]],
    ground_truth: list[str],
    initial_weights: dict,
    epochs: int = 10,
    step: float = 0.05,
) -> tuple[dict, ExperimentLog]:
    """
    Run bounded autoresearch over /init ranking weights.

    Args:
        init_fn:        weights -> ranked thread ids (never mutates state)
        ground_truth:   ideal /init top-N thread ids
        initial_weights: starting ranking_config (MUTABLE_PARAMS only)
        epochs:         hard epoch cap
        step:           per-epoch mutation magnitude

    Returns:
        (best_weights, experiment_log)
    """
    _assert_no_sovereign_mutation(initial_weights)

    log = ExperimentLog()
    current_weights = copy.deepcopy(initial_weights)

    before_top3 = init_fn(current_weights)[:3]
    baseline = evaluate(before_top3, ground_truth, current_weights)
    current_score = baseline.score

    for epoch in range(epochs):
        candidate = _mutate_weights(current_weights, epoch=epoch, step=step)
        _assert_no_sovereign_mutation(candidate)

        ranked = init_fn(candidate)
        result = evaluate(ranked, ground_truth, candidate)

        outcome = "KEEP" if result.score > current_score else "REJECT"

        log.record(ExperimentEntry(
            epoch=epoch,
            weights=candidate,
            score=result.score,
            top3_accuracy=result.top3_accuracy,
            coherence=result.coherence,
            stability=result.stability,
            outcome=outcome,
            before_top3=before_top3,
            after_top3=ranked[:3],
            failure_case=_describe_failure(ranked, ground_truth) if outcome == "REJECT" else None,
        ))

        if outcome == "KEEP":
            current_weights = candidate
            current_score = result.score
            before_top3 = ranked[:3]

    return current_weights, log
