#!/usr/bin/env python3
"""build_init_goldset.py — Phase 0 of INIT_RANKING_2H loop.

Gold set from OPERATOR TRUTH ONLY (consumption_log.ndjson marks).
Deterministic: no randomness, no wall clock in case construction.
NON_SOVEREIGN · authority=false · ledger_effect=none
"""
import json
import itertools
from pathlib import Path

LOG = Path("temple/autoresearch/consumption_log.ndjson")
OUTBOX = Path("temple/autoresearch/outbox")
OUT = Path("scratchpad/init_goldset_v1.json")

VALUE = {"acted": 2, "deferred": 1, "rejected": 0}

def features(d: dict) -> dict:
    text = (str(d.get("summary", "")) + " " + " ".join(d.get("risk_flags", []))).lower()
    return {
        "finding_type": d.get("finding_type", "unknown"),
        "n_flags": len(d.get("risk_flags", [])),
        "n_refs": len(d.get("source_refs", [])),
        "summary_len": len(str(d.get("summary", ""))),
        "severity_kw": sum(k in text for k in
                           ("ci", "kernel", "regression", "gate", "blocked",
                            "structural", "drift", "unconsumed")),
        "lexical_noise_kw": int("signals=[" in str(d.get("summary", ""))),
    }

def main() -> None:
    dec = {}
    for line in LOG.read_text().splitlines():
        if line.strip():
            e = json.loads(line)
            dec[e["packet_id"]] = e["decision"]

    packets = {}
    for p in sorted(OUTBOX.glob("AR-*.json")):
        d = json.loads(p.read_text())
        pid = d.get("packet_id", p.stem)
        if pid not in dec:
            continue  # operator truth only — unmarked packets forbidden
        packets[pid] = {"packet_id": pid, "decision": dec[pid],
                        "value": VALUE[dec[pid]], "features": features(d)}

    positives = sorted([p for p in packets.values() if p["value"] > 0],
                       key=lambda p: (-p["value"], p["packet_id"]))
    negatives = sorted([p for p in packets.values() if p["value"] == 0],
                       key=lambda p: p["packet_id"])
    assert len(positives) >= 3, "need >=3 operator-positive packets"

    cases = []
    triples = list(itertools.combinations(range(len(positives)), 3))  # C(5,3)=10
    for ci, tri in enumerate(triples):
        pos = [positives[i] for i in tri]
        truth_top3 = [p["packet_id"] for p in
                      sorted(pos, key=lambda p: (-p["value"], p["packet_id"]))]
        for w in range(2):  # two deterministic distractor windows per triple
            start = (ci * 5 + w * 13) % (len(negatives) - 4)
            distractors = negatives[start:start + 4]
            cases.append({
                "case_id": f"case-{ci:02d}-{w}",
                "candidates": sorted([p["packet_id"] for p in pos + distractors]),
                "approved_top3": truth_top3,
                "distractors": [p["packet_id"] for p in distractors],
            })

    gold = {
        "schema": "INIT_GOLDSET_V1",
        "authority": False, "ledger_effect": "none",
        "truth_source": "temple/autoresearch/consumption_log.ndjson (operator marks only)",
        "n_cases": len(cases),
        "packets": packets,
        "cases": cases,
    }
    OUT.write_text(json.dumps(gold, indent=1, ensure_ascii=False))
    print(f"gold set: {len(cases)} cases, {len(packets)} packets "
          f"({len(positives)} positive / {len(negatives)} negative) → {OUT}")

if __name__ == "__main__":
    main()
