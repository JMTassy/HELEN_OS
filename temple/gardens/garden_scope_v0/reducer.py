#!/usr/bin/env python3
"""
R — the ONE canonical reducer for Garden J-space.   J_t = R(e_1..e_t)

This is the single source of typed truth. BOTH projections (CLI garden_scope,
browser /api/jspace) must consume R's output — never recompute their own. That
is what makes  CLI(E) ~ Browser(E)  hold by construction.

R is a pure left-fold over immutable typed AgentEvents, so  Replay(E_1:t)=J_t.
COMPOST STAYS IN THE GRAPH:  J_memory = J_surviving ∪ J_dead.
NO_SILENT_TRANSITION:  a VERDICT for a never-SPAWNed name is an orphan (violation).
Only sigma=survive crosses Φ into `population`.  ΔX=ΔP=ΔE=ΔA=0 · NO_CLAIM.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "traces" / "garden_events.ndjson"

# verdict → Garden-local state σ  (semantics → typed state; presentation is downstream)
SIGMA = {"SURVIVES": "survive", "EVIDENCE_NEEDED": "hold", "RENAMING_ONLY": "compost"}


def _norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load(path=EVENTS):
    out = []
    for ln in Path(path).read_text().splitlines():
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def reduce(events):
    """Pure left-fold: ordered events → typed J. Deterministic, replayable."""
    events = sorted(events, key=lambda e: e.get("seq", 0))   # canonical order
    nodes, order, edges, orphans, witnessed = {}, [], [], [], 0
    for e in events:
        t, name = e.get("type"), e.get("name", "")
        k = _norm(name)
        if t == "SPAWN":
            if k not in nodes:
                nodes[k] = {"name": name, "agent": e.get("agent"), "seed": e.get("seed", ""),
                            "detail": e.get("detail", ""), "sigma": "possibility",
                            "verdict": None, "fitness": None, "born_seq": e.get("seq")}
                order.append(k)
            witnessed += 1
        elif t == "CROSS_POLLINATE":
            if k not in nodes:                        # child born by cross-pollination
                nodes[k] = {"name": name, "agent": e.get("agent"), "seed": e.get("seed", ""),
                            "detail": e.get("detail", ""), "sigma": "possibility",
                            "verdict": None, "fitness": None, "born_seq": e.get("seq")}
                order.append(k)
            edges.append({"type": "CROSS", "src": e.get("parent"), "dst": name,
                          "tau": "cross_pollinate", "seq": e.get("seq")})
            witnessed += 1
        elif t == "VERDICT":
            if k not in nodes:                        # verdict without spawn = UNWITNESSED
                orphans.append(name)
                continue
            v = (e.get("verdict") or "").upper()
            nodes[k]["sigma"] = SIGMA.get(v, "hold")
            nodes[k]["verdict"] = v
            nodes[k]["fitness"] = e.get("fitness")
            edges.append({"type": "VERDICT", "src": name, "verdict": v, "seq": e.get("seq")})
            witnessed += 1
    vals = [nodes[k] for k in order]
    by = lambda s: [n for n in vals if n["sigma"] == s]
    J = {
        "events_reduced": len(events),
        "population": by("survive"),        # below Φ — earned
        "hold": by("hold"),                 # above Φ — unresolved (🟡)
        "possibility": by("possibility"),   # above Φ — dreamed, not yet judged
        "graveyard": by("compost"),         # dead, retained (☠), with verdict as reason
        "hyperedges": edges,
        "x_star": [n for n in vals if n["sigma"] == "survive" and (n.get("fitness") or 0) >= 0.5],
        "orphans": orphans,                 # NO_SILENT_TRANSITION violations (must be [])
        "counters": {
            "spawned": len(vals), "typed": len(by("survive")), "hold": len(by("hold")),
            "compost": len(by("compost")), "possibility": len(by("possibility")),
            "cross": sum(1 for e in edges if e["type"] == "CROSS"),
            "witnessed_events": witnessed, "orphans": len(orphans),
        },
        "law": "J_t=R(e_1..e_t) · below-Φ=survive only · COMPOST retained · ΔA=0 · NO_CLAIM",
    }
    return J


LIVE_SIGMA = {"HOLD": "hold", "COMPOST": "compost", "CHIDDUSH_CANDIDATE": "candidate"}


def reduce_live(events):
    """R for the LIVE producer ops (PROPOSE/MUTATE/COUNTERFEIT/DISCRIMINATE/HOLD/…).
    Same discipline: pure fold, COMPOST retained, orphan = witnessed-without-birth."""
    events = sorted(events, key=lambda e: e.get("trace_seq", 0))
    nodes, order, edges, xstar, orphans = {}, [], [], [], []
    for e in events:
        op, oid, par = e.get("op"), e.get("object_id"), e.get("parent_ids") or []
        if op in ("PROPOSE", "MUTATE", "CROSS"):
            if oid not in nodes:
                nodes[oid] = {"id": oid, "actor": e.get("actor"), "sigma": "possibility",
                              "distinction": e.get("distinction", ""), "op_born": op}
                order.append(oid)
            for p in par:
                edges.append({"a": p, "b": oid, "kind": "MUTATE" if op == "MUTATE" else "CROSS"})
        elif op in ("COUNTERFEIT", "ATTACK"):
            tgt = oid if oid in nodes else (par[0] if par else None)
            if tgt in nodes: edges.append({"a": tgt, "b": tgt, "kind": "ATTACK"})
            else: orphans.append(e.get("event_id"))
        elif op == "DISCRIMINATE":
            for p in par:
                if p in nodes: edges.append({"a": p, "b": p, "kind": "DISCRIMINATE"}); xstar.append(oid)
                else: orphans.append(e.get("event_id"))
        elif op in LIVE_SIGMA:
            tgt = oid if oid in nodes else (par[0] if par else None)
            if tgt in nodes: nodes[tgt]["sigma"] = LIVE_SIGMA[op]
            else: orphans.append(e.get("event_id"))
        # CONTROL/RUN_END: no J mutation
    vals = [nodes[k] for k in order]
    by = lambda s: [n for n in vals if n["sigma"] == s]
    return {"events_reduced": len(events), "population": by("survive"),
            "candidate": by("candidate"), "hold": by("hold"), "possibility": by("possibility"),
            "graveyard": by("compost"), "hyperedges": edges, "x_star": xstar, "orphans": orphans,
            "counters": {"nodes": len(vals), "possibility": len(by("possibility")),
                         "hold": len(by("hold")), "candidate": len(by("candidate")),
                         "compost": len(by("compost")), "x_star": len(xstar),
                         "attacks": sum(1 for x in edges if x["kind"] == "ATTACK"),
                         "orphans": len(orphans)},
            "law": "live R · ∀δ∃!e · COMPOST retained · ΔA=0 · NO_CLAIM"}


def _cli(J):
    c = J["counters"]
    print("═" * 60)
    print(f"  J-SPACE = R(events)   ·   {J['events_reduced']} events reduced")
    print("═" * 60)
    print(f"  possibility {c['possibility']:2}   hold {c['hold']:2}   "
          f"compost {c['compost']:2}   cross-edges {c['cross']}")
    print(f"  ── Φ ──  typed(below) {c['typed']}   x* {len(J['x_star'])}   "
          f"orphans {c['orphans']}")
    print("─" * 60)
    if J["population"]:
        for n in J["population"]:
            print(f"  🟣 {n['name'][:44]}  fit={n['fitness']}")
    else:
        print("  (( below Φ empty — HELEN dreamed more than reality kept ))")
    print("─" * 60)
    for e in J["hyperedges"]:
        if e["type"] == "CROSS":
            print(f"  🧬 {e['src'][:24]:24} ──CROSS──▶ {e['dst'][:24]}")
    print(f"\n  NO_SILENT_TRANSITION: {'✓ HOLDS' if not J['orphans'] else '✗ VIOLATED'}")


if __name__ == "__main__":
    _cli(reduce(load()))
