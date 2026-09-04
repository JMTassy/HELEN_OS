#!/usr/bin/env python3
"""
Vertical slice: real SEED → MIRROR∥NULL∥ROLE → graph (collide/quotient) → HAL → DETECTOR → render.
Four separated objects; each step only reads the append-only trace. FABLE_CALLS=0 · ΔA=0.
"""
import json
from collections import defaultdict
from pathlib import Path
import jspace as J
import transforms as TR

ROOT = Path(__file__).resolve().parent
TRACE = ROOT / "jspace_demo.ndjson"


def build_content_and_events(tr):
    # HER: born seed
    J.emit(tr, "HER", "BORN", "b0", payload={"assertion": TR.SEED["assertion"], "invariant": "SEED"})
    # JESTER: frame transforms (content producers → TRANSFORMED events)
    for name, bid in [("MIRROR", "b1"), ("NULL", "b2"), ("ROLE", "b3")]:
        c = TR.TRANSFORMS[name](TR.SEED)
        J.emit(tr, "JESTER", "TRANSFORMED", bid, parents=["b0"],
               payload={"theta": c["theta"], "invariant": c["invariant"],
                        "x_star": c.get("x_star"), "executable": c.get("executable", False),
                        "content": c["content"]})


def graph_reduce(tr):
    groups = defaultdict(list)
    for e in tr:
        if e["event_type"] == "TRANSFORMED" and e["payload"].get("invariant"):
            groups[e["payload"]["invariant"]].append(e["branch"])
    for inv, members in groups.items():
        if len(members) >= 2:
            J.emit(tr, "CONTROL", "COLLIDED", inv, parents=members, payload={"invariant": inv})
            J.emit(tr, "CONTROL", "QUOTIENTED", members[0], parents=members,
                   payload={"equivalence": "≡".join(members) + f" by {inv}", "invariant": inv})


def hal_attack(tr):
    execmap = {e["branch"]: e["payload"].get("executable", False) for e in tr if e["event_type"] == "TRANSFORMED"}
    invmap = {e["branch"]: e["payload"].get("invariant") for e in tr if e["event_type"] == "TRANSFORMED"}
    xmap = {e["branch"]: e["payload"].get("x_star") for e in tr if e["event_type"] == "TRANSFORMED"}
    members = defaultdict(list); cls_exec = defaultdict(bool)
    for b, inv in invmap.items():
        members[inv].append(b)
        if execmap.get(b): cls_exec[inv] = True
    for b in invmap: J.emit(tr, "HAL", "ATTACKED", b, parents=[b])
    for inv, mem in members.items():
        if cls_exec[inv]:
            rep = next(b for b in mem if execmap.get(b))
            J.emit(tr, "HAL", "SURVIVED", rep, parents=[rep])
            J.emit(tr, "HAL", "DISCRIMINATOR", rep, parents=[rep],
                   payload={"x_star": xmap[rep], "executable": True})
        else:
            for b in mem:
                J.emit(tr, "HAL", "KILLED", b, parents=[b], payload={"reason": "no executable discriminator"})


def detect(tr):
    g = J.build_graph(tr)
    blooms = J.detect_blooms(tr, g, seed_classes={"SEED"}, min_frames=2)
    for bl in blooms:
        J.emit(tr, "DETECTOR", "BLOOM", bl["class"], payload={"witness": bl["witness"]})
    return blooms


def build_trace():
    tr = []
    build_content_and_events(tr)   # content ≠
    graph_reduce(tr)               # graph computation ≠
    hal_attack(tr)                 # attack/discriminate ≠
    blooms = detect(tr)            # detector (only source of BLOOM)
    return tr, blooms


def main():
    tr, blooms = build_trace()
    TRACE.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in tr) + "\n")
    print(J.render(tr, blooms))
    print(f"\ntrace → {TRACE.name}  ({len(tr)} events · {len(blooms)} bloom)")


if __name__ == "__main__":
    main()
