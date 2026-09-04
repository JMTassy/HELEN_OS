#!/usr/bin/env python3
"""
BUILD_EVENTS — project REAL typed state (chaos-garden object files + hard-CHIDDUSH
gate verdicts) into an AgentEvent NDJSON bus for the Garden Scope UI.

Every event is a projection of a receipt/object field. No event is hand-authored.
    D:(H,Θ)→V  ·  ΔX=ΔP=ΔE=ΔA=0  ·  NO_CLAIM
Event schema (typed, presentation-bound):
    {seq, agent, type, name, seed, detail, verdict, fitness}
    type ∈ SPAWN | VERDICT   (more types appear once runners emit them live)
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GARDEN = ROOT.parent / "async_wulmath_chaos_garden_v1"
OBJS = GARDEN / "objects"
GATE = GARDEN / "HARD_CHIDDUSH_GATE_RECEIPT.json"
OUT = ROOT / "traces" / "garden_events.ndjson"


def main():
    events, seq = [], 0
    # 1) SPAWN events — one per real garden object file, ordered (stream, epoch)
    objs = []
    for f in sorted(OBJS.glob("*.json")):
        o = json.loads(f.read_text())
        if o.get("name"):
            objs.append(o)
    objs.sort(key=lambda o: (o["stream"], o["epoch"]))
    for o in objs:
        seq += 1
        events.append({"seq": seq, "agent": o["stream"], "type": "SPAWN",
                       "name": o["name"], "seed": o.get("formal_seed", ""),
                       "detail": o.get("strange", "")[:120], "verdict": "", "fitness": None})
    # 2) CROSS_POLLINATE events — real parent→child hyperedges from the chaos receipt
    CHAOS = GARDEN / "ASYNC_WULMATH_CHAOS_GARDEN_V1_RECEIPT.json"
    if CHAOS.exists():
        ch = json.loads(CHAOS.read_text())
        for c in ch.get("cross_pollination_detail", []):
            if c.get("name") and c.get("parent"):
                seq += 1
                events.append({"seq": seq, "agent": c.get("tag", "CROSS"), "type": "CROSS_POLLINATE",
                               "name": c["name"], "parent": c["parent"], "seed": c.get("seed", ""),
                               "detail": "", "verdict": "", "fitness": None})
    # 3) VERDICT events — one per real gate verdict (the adversarial collapse)
    if GATE.exists():
        gt = json.loads(GATE.read_text())
        for v in gt.get("all_verdicts", []):
            seq += 1
            events.append({"seq": seq, "agent": "HAL_GATE", "type": "VERDICT",
                           "name": v["name"], "seed": "", "detail": "",
                           "verdict": v["verdict"], "fitness": v.get("fitness")})
    OUT.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n")
    n_spawn = sum(1 for e in events if e["type"] == "SPAWN")
    n_verd = sum(1 for e in events if e["type"] == "VERDICT")
    print(f"wrote {len(events)} typed events → {OUT.relative_to(ROOT)}  "
          f"({n_spawn} SPAWN · {n_verd} VERDICT)")


if __name__ == "__main__":
    main()
