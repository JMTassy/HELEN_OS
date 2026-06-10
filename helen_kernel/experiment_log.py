"""
experiment_log.py — In-memory log of autoresearch experiment attempts.
NON_SOVEREIGN. No ledger writes. Append-only within session.
Authority: NONE
"""
import json
from dataclasses import asdict, dataclass


@dataclass
class ExperimentEntry:
    epoch: int
    weights: dict
    score: float
    top3_accuracy: float
    coherence: float
    stability: float
    outcome: str  # "KEEP" | "REJECT"
    before_top3: list[str]
    after_top3: list[str]
    failure_case: str | None = None


class ExperimentLog:
    def __init__(self) -> None:
        self._entries: list[ExperimentEntry] = []
        self._best_score: float = -1.0
        self._best_weights: dict = {}

    def record(self, entry: ExperimentEntry) -> None:
        self._entries.append(entry)
        if entry.outcome == "KEEP" and entry.score > self._best_score:
            self._best_score = entry.score
            self._best_weights = entry.weights.copy()

    def best(self) -> tuple[float, dict]:
        return self._best_score, self._best_weights

    def all_entries(self) -> list[dict]:
        return [asdict(e) for e in self._entries]

    def summary(self) -> dict:
        kept = sum(1 for e in self._entries if e.outcome == "KEEP")
        return {
            "total_experiments": len(self._entries),
            "kept": kept,
            "rejected": len(self._entries) - kept,
            "best_score": self._best_score,
            "best_weights": self._best_weights,
        }

    def to_json(self) -> str:
        return json.dumps({"summary": self.summary(), "entries": self.all_entries()}, indent=2)
