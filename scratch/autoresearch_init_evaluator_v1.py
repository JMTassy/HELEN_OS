#!/usr/bin/env python3
"""autoresearch_init_evaluator_v1.py — Phase 1 FROZEN evaluator.

score = 0.7*Top3Match + 0.2*OrderScore + 0.1*Stability
METRIC IS FROZEN FOR THE RUN. Mutable surface = ranker WEIGHTS only.
NON_SOVEREIGN · authority=false · ledger_effect=none
"""
import json
import sys
from pathlib import Path

GOLD = Path("scratchpad/init_goldset_v1.json")

TYPE_SCORE = {"risk": 3.0, "test_gap": 2.5, "doc_gap": 1.5,
              "proposal": 1.0, "quest_candidate": 0.5, "compost_candidate": 0.2}

BASELINE = {  # mirrors current triage TYPE_PRIORITY intuition
    "w_type": 1.0, "w_flags": 0.0, "w_severity": 0.0,
    "w_refs": 0.0, "w_noise": 0.0, "w_len": 0.0,
}

def rank_score(f: dict, w: dict) -> float:
    return (w["w_type"] * TYPE_SCORE.get(f["finding_type"], 0.0)
            + w["w_flags"] * f["n_flags"]
            + w["w_severity"] * f["severity_kw"]
            + w["w_refs"] * min(f["n_refs"], 5)
            - w["w_noise"] * f["lexical_noise_kw"]
            - w["w_len"] * (f["summary_len"] / 200.0))

def rank(candidates, packets, w):
    return sorted(candidates,
                  key=lambda pid: (-rank_score(packets[pid]["features"], w), pid))

def evaluate(weights: dict) -> dict:
    gold = json.loads(GOLD.read_text())
    packets, cases = gold["packets"], gold["cases"]
    top3_hits, order_hits, stable = 0, 0.0, 0
    for c in cases:
        r1 = rank(c["candidates"], packets, weights)
        r2 = rank(list(reversed(c["candidates"])), packets, weights)  # input-order shuffle
        stable += int(r1 == r2)
        got3, want3 = r1[:3], c["approved_top3"]
        top3_hits += int(set(got3) == set(want3))
        order_hits += sum(a == b for a, b in zip(got3, want3)) / 3.0
    n = len(cases)
    top3, order, stab = top3_hits / n, order_hits / n, stable / n
    return {"Top3Match": round(top3, 4), "OrderScore": round(order, 4),
            "Stability": round(stab, 4),
            "score": round(0.7 * top3 + 0.2 * order + 0.1 * stab, 4)}

if __name__ == "__main__":
    w = dict(BASELINE)
    if len(sys.argv) > 1:
        w.update(json.loads(sys.argv[1]))
    print(json.dumps({"weights": w, **evaluate(w)}))
