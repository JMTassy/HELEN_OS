#!/usr/bin/env python3
"""Fleet Loop V1 — zero-credit dry run against a mocked provider.

NON_SOVEREIGN. $0. No network, no credits, no ledger writes.
Exercises the mechanics of docs/proposals/HELEN_DIRECTOR_FLEET_LOOP_V1.md:
  - concurrency throttle (cap shared across families, high-water asserted)
  - shot loop: <=4 candidates, ONE variable changed per retry
  - queue-stall -> COST_ORPHAN (billed, abandoned, never retried)
  - FLEET_GENERATION_RECEIPT_V1 sidecar per generation
  - hard credit-budget stop (ships partial winners + receipts)
  - operator_rating stays null — the fleet never rates

The mock provider is seeded-deterministic: same seed, same run, replayable.
Real provider integration is gated on operator GO FLEET per the proposal.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

FLEET_CONCURRENCY_CAP = 6
MAX_CANDIDATES = 4
QUEUE_STALL_TICKS = 18  # mock analog of the 3-min queued-state abort
VARIABLE_CYCLE = ["NONE(first)", "camera", "lighting", "speed"]
WIN_SCORE = 0.72  # mock nomination threshold (stand-in for visual triage)


class MockProvider:
    """Deterministic stand-in for Seedance I2V submission + polling."""

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.jobs: dict[int, dict] = {}
        self.next_id = 0

    def submit(self, prompt_key: str) -> int:
        jid = self.next_id
        self.next_id += 1
        roll = self.rng.random()
        if roll < 0.08:  # global queue stall (SKILL.md §15.2 failure mode)
            self.jobs[jid] = {"kind": "stall"}
        elif roll < 0.16:  # provider-side failure
            self.jobs[jid] = {"kind": "fail", "done_at": self.rng.randint(3, 9)}
        else:
            self.jobs[jid] = {
                "kind": "ok",
                "done_at": self.rng.randint(3, 12),
                "score": round(self.rng.uniform(0.35, 0.98), 2),
            }
        self.jobs[jid]["age"] = 0
        return jid

    def poll(self, jid: int) -> tuple[str, float | None]:
        job = self.jobs[jid]
        job["age"] += 1
        if job["kind"] == "stall":
            return ("queued", None)
        if job["age"] < job["done_at"]:
            return ("running", None)
        if job["kind"] == "fail":
            return ("failed", None)
        return ("completed", job["score"])


def run_fleet(shots: list[dict], budget: int, seed: int, label: str,
              receipts_dir: Path) -> dict:
    provider = MockProvider(seed)
    receipts: list[dict] = []
    credits = budget
    active: dict[int, dict] = {}  # jid -> shot state
    queue = [dict(s, candidate=0, status="PENDING") for s in shots]
    high_water = 0
    tick = 0

    def emit(shot, jid, status):
        receipts.append({
            "schema": "FLEET_GENERATION_RECEIPT_V1",
            "run": label,
            "shot_id": shot["shot_id"],
            "family": shot["family"],
            "candidate_index": shot["candidate"],
            "prompt_sha256": f"mock:{label}:{shot['shot_id']}:c{shot['candidate']}",
            "model": "mock_seedance_2_0",
            "variable_changed": VARIABLE_CYCLE[shot["candidate"] - 1],
            "result_url_sha256": f"mock:job:{jid}",
            "status": status,
            "operator_rating": None,
        })

    def submit_next():
        nonlocal credits
        for shot in queue:
            if shot["status"] != "PENDING" or len(active) >= FLEET_CONCURRENCY_CAP:
                continue
            if credits <= 0:
                shot["status"] = "BUDGET_STOP"
                continue
            credits -= 1  # every submission bills, orphans included
            shot["candidate"] += 1
            shot["status"] = "ACTIVE"
            jid = provider.submit(f"{shot['shot_id']}:c{shot['candidate']}")
            active[jid] = shot

    submit_next()
    while active:
        tick += 1
        high_water = max(high_water, len(active))
        for jid in list(active):
            shot = active[jid]
            state, score = provider.poll(jid)
            if state == "queued" and provider.jobs[jid]["age"] >= QUEUE_STALL_TICKS:
                emit(shot, jid, "COST_ORPHAN")  # billed; never retried
                shot["status"] = "PENDING" if shot["candidate"] < MAX_CANDIDATES else "BLOCKED"
                del active[jid]
            elif state == "failed":
                emit(shot, jid, "FAILED")
                shot["status"] = "PENDING" if shot["candidate"] < MAX_CANDIDATES else "BLOCKED"
                del active[jid]
            elif state == "completed":
                won = score >= WIN_SCORE
                emit(shot, jid, "WON" if won else "KILLED")
                if won:
                    shot["status"] = "WON"
                elif shot["candidate"] < MAX_CANDIDATES:
                    shot["status"] = "PENDING"
                else:
                    shot["status"] = "BLOCKED"
                del active[jid]
        submit_next()

    # ── invariant assertions ──────────────────────────────────────────────
    assert high_water <= FLEET_CONCURRENCY_CAP, "throttle breached"
    assert all(r["operator_rating"] is None for r in receipts), "fleet rated"
    assert all(s["status"] in ("WON", "BLOCKED", "BUDGET_STOP") for s in queue), \
        "non-terminal shot"
    assert len(receipts) == budget - credits, "generation without receipt"

    out = receipts_dir / f"fleet_dryrun_{label}_receipts.ndjson"
    out.write_text("".join(json.dumps(r) + "\n" for r in receipts))
    tally = {s: sum(1 for r in receipts if r["status"] == s)
             for s in ("WON", "KILLED", "FAILED", "COST_ORPHAN")}
    return {
        "label": label, "shots": len(queue), "ticks": tick,
        "won": sum(1 for s in queue if s["status"] == "WON"),
        "blocked": sum(1 for s in queue if s["status"] == "BLOCKED"),
        "budget_stopped": sum(1 for s in queue if s["status"] == "BUDGET_STOP"),
        "credits_spent": budget - credits, "budget": budget,
        "high_water": high_water, "receipts": len(receipts),
        "by_status": tally, "receipts_file": str(out),
    }


def main() -> int:
    receipts_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    receipts_dir.mkdir(parents=True, exist_ok=True)

    pilot = [{"shot_id": f"W-{i:02d}", "family": "water"} for i in range(1, 7)]
    stress = [{"shot_id": f"{fam[0].upper()}-{i:02d}", "family": fam}
              for fam in ("water", "presence", "interior") for i in range(1, 7)]

    results = [
        run_fleet(pilot, budget=24, seed=42, label="pilot", receipts_dir=receipts_dir),
        run_fleet(stress, budget=40, seed=42, label="stress", receipts_dir=receipts_dir),
    ]
    for r in results:
        print(json.dumps(r, indent=2))
    print("ALL INVARIANTS HELD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
