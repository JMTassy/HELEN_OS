"""
init_weight_optimizer.py — Entry point for /init ranking optimization.
NON_SOVEREIGN. Reads ground truth, runs autoresearch loop, reports.
Authority: NONE

Usage:
    .venv/bin/python -m helen_kernel.init_weight_optimizer
    .venv/bin/python -m helen_kernel.init_weight_optimizer 20   # custom epoch count
"""
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).parent.parent
WEIGHTS_PATH = BASE / "configs" / "ranking_weights_v1.json"
GROUND_TRUTH_PATH = BASE / "eval" / "init_ground_truth_v1.json"


def load_weights() -> dict:
    with open(WEIGHTS_PATH) as f:
        return json.load(f)


def load_ground_truth() -> list[dict]:
    with open(GROUND_TRUTH_PATH) as f:
        return json.load(f)


def mock_init_fn(weights: dict) -> list[str]:
    """
    Stub /init for development. Replace with real context_router call.
    Produces a deterministic ranking from weight configuration.
    """
    threads = [
        ("thread_k_tau_claim_type",                    0.9),
        ("thread_autoresearch_e11_e12_reconciliation", 0.8),
        ("thread_legoracle_replay_gate",                0.7),
        ("thread_hal_epoch_routing",                   0.6),
        ("thread_executor_sandbox",                    0.5),
        ("thread_dan_goblin_hd002",                    0.4),
        ("thread_claim_type_policy",                   0.35),
        ("thread_aura_score_design",                   0.3),
        ("thread_ledger_receipt_chain",                0.25),
    ]
    scored = []
    for tid, base_relevance in threads:
        score = (
            weights.get("recency_weight", 0.4) * base_relevance
            + weights.get("relevance_weight", 0.4) * (1 - base_relevance * 0.3)
            + weights.get("coherence_weight", 0.2) * base_relevance
        )
        scored.append((tid, round(score, 6)))
    scored.sort(key=lambda x: -x[1])
    return [tid for tid, _ in scored]


def run(epochs: int = 10) -> None:
    from helen_kernel.autoresearch_loop import run_autoresearch

    weights = load_weights()
    ground_truth_sessions = load_ground_truth()
    ground_truth = ground_truth_sessions[0]["top_threads"]

    best_weights, log = run_autoresearch(
        init_fn=mock_init_fn,
        ground_truth=ground_truth,
        initial_weights=weights,
        epochs=epochs,
    )

    summary = log.summary()
    entries = log.all_entries()
    first = entries[0] if entries else None
    best_kept = next((e for e in reversed(entries) if e["outcome"] == "KEEP"), None)
    last_reject = next((e for e in reversed(entries) if e["outcome"] == "REJECT"), None)

    print("\n=== AUTORESEARCH /init REPORT ===")
    print(f"Epochs run:    {summary['total_experiments']}")
    print(f"KEEP:          {summary['kept']}")
    print(f"REJECT:        {summary['rejected']}")
    print(f"Best score:    {summary['best_score']}")
    print(f"\nBEFORE top 3: {first['before_top3'] if first else 'n/a'}")
    print(f"AFTER  top 3: {best_kept['after_top3'] if best_kept else 'n/a (no improvement)'}")
    print(f"\nBest weights:\n{json.dumps(summary['best_weights'], indent=2)}")

    failure = (best_kept or {}).get("failure_case") or (last_reject or {}).get("failure_case")
    if failure:
        print(f"\nFailure case:  {failure}")

    print("\nNO CLAIM / NO SHIP / NO ADMISSION")
    print("PROPOSAL CANDIDATES ONLY")
    print("=================================\n")


if __name__ == "__main__":
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run(epochs)
