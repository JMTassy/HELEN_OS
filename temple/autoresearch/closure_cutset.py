#!/usr/bin/env python3
"""closure_cutset.py — minimal observable scheduler kernel for the autoresearch outbox.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none · PROPOSAL ONLY

    PacketGraph + PenDecisions → Closure → DecisionUnits → Priority_0 → ExactCutSet → Residual

Deliberately stupid and measurable. Every ranking field carries a provenance path
back to packet or receipt state. No predicted information gain, no model opinion.

    Priority_0(unit) = closes × confidence ÷ cost

  closes      |closure(unit)| — the head plus every unconsumed packet whose mark follows
              mechanically from one judgment on the head (ancestors via parent_epoch,
              packets it declares in `supersedes`, packets declaring `duplicate_of` it).
  confidence  1.0 if the head carries a receipt field (`falsifier_receipt` or
              `liveness_receipt`, a dict with `at` and `result`), else 0.5 (unverified).
  cost        number of distinct files in the head's `source_refs` (minimum 1).

The cut-set is exact: minimum number of decision units whose closures leave the
residual under the guard threshold, ties broken on total cost (dynamic programme,
closures are disjoint so sizes add).

This tool never marks the pen, never writes into the outbox, never touches the guard.
Its only output is a JSON report (default artifacts/closure_cutset.json) and a table.

Usage:
  python3 temple/autoresearch/closure_cutset.py                 # table + JSON report
  python3 temple/autoresearch/closure_cutset.py --bundle-by-file
  python3 temple/autoresearch/closure_cutset.py --threshold 5 --out artifacts/closure_cutset.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
try:
    from temple.autoresearch import operator_pen as pen  # type: ignore
except Exception:  # pragma: no cover — direct invocation from the file's directory
    import operator_pen as pen  # type: ignore

KERNEL_VERSION = "CLOSURE_CUTSET_V0"
RECEIPT_FIELDS = ("falsifier_receipt", "liveness_receipt")
CONFIDENCE_VERIFIED = 1.0
CONFIDENCE_UNVERIFIED = 0.5
DEFAULT_THRESHOLD = 5  # mirrors ci_outbox_guard --max-unconsumed
_EPOCH_RE = re.compile(r"^E(\d+)$")


# ---------------------------------------------------------------------------
# pure helpers
# ---------------------------------------------------------------------------

def _epoch_num(e: Any) -> int:
    m = _EPOCH_RE.match(str(e or ""))
    return int(m.group(1)) if m else -1


def _files(p: Dict[str, Any]) -> List[str]:
    refs = p.get("source_refs")
    if not refs and p.get("file"):
        refs = [p["file"]]
    if isinstance(refs, str):
        refs = [refs]
    out = []
    for r in refs or []:
        if isinstance(r, str) and r.strip():
            out.append(r.split(":")[0].strip())
    return sorted(set(out))


def _has_receipt(p: Dict[str, Any]) -> Optional[str]:
    for f in RECEIPT_FIELDS:
        r = p.get(f)
        if isinstance(r, dict) and r.get("at") and "result" in r:
            return f
    return None


# ---------------------------------------------------------------------------
# graph
# ---------------------------------------------------------------------------

def build_graph(packets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Edges among *unconsumed* packets only. Returns parents/children/supersedes maps
    with per-edge provenance (which packet field produced it)."""
    by_id = {p["packet_id"]: p for p in packets}
    by_epoch: Dict[str, str] = {}
    for p in packets:
        e = str(p.get("epoch") or "")
        if e and e not in by_epoch:
            by_epoch[e] = p["packet_id"]
    parent_of: Dict[str, Tuple[str, str]] = {}            # child -> (parent, provenance)
    absorbed_by: Dict[str, Tuple[str, str]] = {}          # packet -> (absorber, provenance)
    for p in packets:
        pid = p["packet_id"]
        pe = str(p.get("parent_epoch") or "")
        if pe and pe in by_epoch and by_epoch[pe] != pid:
            parent_of[pid] = (by_epoch[pe], "parent_epoch")
        elif p.get("parent_id") in by_id and p["parent_id"] != pid:
            parent_of[pid] = (p["parent_id"], "parent_id")
        for s in p.get("supersedes") or []:
            if s in by_id and s != pid:
                absorbed_by[s] = (pid, "supersedes")
        d = p.get("duplicate_of")
        if isinstance(d, str) and d in by_id and d != pid:
            absorbed_by[pid] = (d, "duplicate_of")
    children: Dict[str, List[str]] = defaultdict(list)
    for c, (par, _) in parent_of.items():
        children[par].append(c)
    return {"by_id": by_id, "parent_of": parent_of, "children": dict(children), "absorbed_by": absorbed_by}


def heads_and_closures(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """A head is an unconsumed packet with no unconsumed child and not absorbed by
    another unconsumed packet. closure(head) = head + ancestors + absorbed packets,
    transitively, each packet attributed to exactly one head (the latest epoch wins,
    then lexicographic packet_id)."""
    by_id, parent_of, children, absorbed_by = (graph[k] for k in ("by_id", "parent_of", "children", "absorbed_by"))
    heads = [pid for pid in by_id if not children.get(pid) and pid not in absorbed_by]
    heads.sort(key=lambda h: (-_epoch_num(by_id[h].get("epoch")), h))
    absorbs: Dict[str, List[str]] = defaultdict(list)
    for a, (b, _) in absorbed_by.items():
        absorbs[b].append(a)
    claimed: Dict[str, str] = {}
    out: Dict[str, Dict[str, Any]] = {}
    for h in heads:
        members: List[Tuple[str, str]] = []
        stack = [(h, "head")]
        while stack:
            pid, why = stack.pop()
            if pid in claimed:
                continue
            claimed[pid] = h
            members.append((pid, why))
            par = parent_of.get(pid)
            if par:
                stack.append((par[0], f"ancestor:{par[1]}"))
            for a in absorbs.get(pid, []):
                stack.append((a, f"absorbed:{absorbed_by[a][1]}"))
        out[h] = {"members": [m for m, _ in members], "provenance": dict(members)}
    return out


# ---------------------------------------------------------------------------
# units, priority, cut-set
# ---------------------------------------------------------------------------

def decision_units(graph: Dict[str, Any], closures: Dict[str, Dict[str, Any]], bundle_by_file: bool) -> List[Dict[str, Any]]:
    by_id = graph["by_id"]
    groups: Dict[str, List[str]] = defaultdict(list)
    for h in closures:
        # a head with no source_refs shares no fix surface with anyone: never bundle it
        key = (_files(by_id[h]) or [h])[0] if bundle_by_file else h
        groups[key].append(h)
    units = []
    for key, hs in groups.items():
        hs = sorted(hs, key=lambda h: (-_epoch_num(by_id[h].get("epoch")), h))
        members = [m for h in hs for m in closures[h]["members"]]
        receipts = [(_has_receipt(by_id[h]), h) for h in hs]
        verified = all(r for r, _ in receipts)
        confidence = CONFIDENCE_VERIFIED if verified else CONFIDENCE_UNVERIFIED
        conf_src = ("receipt:" + ",".join(f"{h}.{r}" for r, h in receipts)) if verified else \
            "default:unverified(" + ",".join(h for r, h in receipts if not r) + ")"
        files = sorted({f for h in hs for f in _files(by_id[h])})
        cost = max(1, len(files))
        units.append({
            "unit_id": key if bundle_by_file else hs[0],
            "heads": hs,
            "epochs": [by_id[h].get("epoch") for h in hs],
            "closes": len(members),
            "closure": members,
            "confidence": confidence,
            "confidence_source": conf_src,
            "cost": cost,
            "cost_source": f"source_refs.files={len(files)}" + (":" + ";".join(files) if files else ":none→1"),
            "priority_0": round(len(members) * confidence / cost, 3),
        })
    units.sort(key=lambda u: (-u["priority_0"], -u["closes"], u["unit_id"]))
    return units


def exact_cutset(units: List[Dict[str, Any]], total: int, threshold: int) -> Dict[str, Any]:
    """Minimum-cardinality set of units with closed >= total-(threshold-1); ties on cost.
    Closures are disjoint, so a (count, closed) → min-cost DP is exact."""
    need = max(0, total - (threshold - 1))
    n = len(units)
    INF = float("inf")
    # dp[k][c] = (min cost, choice bitmask) using first i units, k chosen, c closed
    dp: List[Dict[int, Tuple[float, int]]] = [dict() for _ in range(n + 1)]
    dp[0][0] = (0.0, 0)
    for i, u in enumerate(units):
        for k in range(i, -1, -1):
            for c, (cost, mask) in list(dp[k].items()):
                nc, ncost, nmask = c + u["closes"], cost + u["cost"], mask | (1 << i)
                cur = dp[k + 1].get(nc)
                if cur is None or ncost < cur[0]:
                    dp[k + 1][nc] = (ncost, nmask)
    for k in range(0, n + 1):
        feasible = [(cost, mask, c) for c, (cost, mask) in dp[k].items() if c >= need]
        if feasible:
            cost, mask, closed = min(feasible)
            chosen = [units[i]["unit_id"] for i in range(n) if mask >> i & 1]
            return {"k": k, "cost": cost, "closed": closed, "residual": total - closed,
                    "need_closed": need, "members": chosen}
    return {"k": None, "cost": None, "closed": 0, "residual": total, "need_closed": need, "members": []}


def diagnostics(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Receipt-based only: a child that declares `discriminators` all contained in its
    parent's is a verification pass filed as a research child. Children that declare
    nothing are counted as undeclared, not judged."""
    by_id, parent_of = graph["by_id"], graph["parent_of"]
    verification_children, undeclared = [], []
    for c, (par, _) in parent_of.items():
        cd, pd = by_id[c].get("discriminators"), by_id[par].get("discriminators")
        if not isinstance(cd, list) or not cd:
            undeclared.append(c)
        elif not (set(cd) - set(pd or [])):
            verification_children.append({"child": c, "parent": par})
    return {"children": len(parent_of), "verification_children": verification_children,
            "undeclared_discriminators": len(undeclared)}


# ---------------------------------------------------------------------------
# duplicate discriminator  (fails closed)
#
#   Duplicate(a,b) = 1  iff  Closure(D_a) = Closure(D_b)   (declared discriminators)
#                       and  every other unit's scheduler trace is unchanged when a
#                            and b are merged into one head (protected bisimulation)
#   Undeclared discriminators on either side → UNDECIDABLE, never DUPLICATE.
# ---------------------------------------------------------------------------

def duplicate_test(a: str, b: str, open_packets: List[Dict[str, Any]], threshold: int = DEFAULT_THRESHOLD) -> Dict[str, Any]:
    by_id = {p["packet_id"]: p for p in open_packets}
    if a not in by_id or b not in by_id:
        return {"a": a, "b": b, "verdict": "UNDECIDABLE", "reasons": ["packet not in unconsumed set"]}
    reasons: List[str] = []
    da, db = by_id[a].get("discriminators"), by_id[b].get("discriminators")
    if not (isinstance(da, list) and da) or not (isinstance(db, list) and db):
        reasons.append("undeclared discriminators on " + ", ".join(x for x, d in ((a, da), (b, db)) if not (isinstance(d, list) and d)))
        return {"a": a, "b": b, "verdict": "UNDECIDABLE", "reasons": reasons}
    if set(da) != set(db):
        return {"a": a, "b": b, "verdict": "DISTINCT", "reasons": [f"Closure(D_a) ≠ Closure(D_b): {sorted(set(da) ^ set(db))} separate them"]}
    # protected bisimulation: merge b into a and compare every other unit's trace
    def trace(packets):
        g = build_graph(packets); cl = heads_and_closures(g)
        units = decision_units(g, cl, bundle_by_file=False)
        cut = exact_cutset(units, len(packets), threshold)
        return {u["unit_id"]: (u["closes"], u["confidence"], u["cost"]) for u in units}, cut["residual"]
    t0, r0 = trace(open_packets)
    merged = [dict(p, duplicate_of=a) if p["packet_id"] == b else p for p in open_packets]
    t1, r1 = trace(merged)
    others0 = {k: v for k, v in t0.items() if k not in (a, b)}
    others1 = {k: v for k, v in t1.items() if k not in (a, b)}
    if others0 != others1:
        changed = sorted(k for k in set(others0) | set(others1) if others0.get(k) != others1.get(k))
        return {"a": a, "b": b, "verdict": "DISTINCT", "reasons": [f"merging changes other units' traces: {changed}"]}
    if r0 != r1:
        return {"a": a, "b": b, "verdict": "DISTINCT", "reasons": [f"merging changes residual {r0} → {r1}"]}
    return {"a": a, "b": b, "verdict": "DUPLICATE", "reasons": ["Closure(D_a) = Closure(D_b)", "protected bisimulation holds", f"residual invariant {r0}"]}


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def _git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def compute(outbox: Path, log: Path, threshold: int, bundle_by_file: bool) -> Dict[str, Any]:
    packets = pen.load_packets(outbox)
    entries = pen.read_log(log)
    broken = pen.verify_chain(entries)
    if broken:
        raise SystemExit(f"❌ consumption log chain broken ({broken}) — kernel refuses to rank on an untrusted log")
    eff = pen.effective_decisions(entries)
    open_ = pen.unconsumed(packets, eff)
    graph = build_graph(open_)
    closures = heads_and_closures(graph)
    units = decision_units(graph, closures, bundle_by_file)
    total = len(open_)
    assert sum(u["closes"] for u in units) == total, "closures must partition the unconsumed set"
    cut = exact_cutset(units, total, threshold)
    acc, walk = 0, []
    for u in units:
        acc += u["closes"]
        walk.append({"unit_id": u["unit_id"], "closed_cum": acc, "residual_after": total - acc})
    return {
        "kernel": KERNEL_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(),
        "head": _git_head(), "authority": False, "canon": False, "ledger_effect": "none",
        "priority_formula": "closes * confidence / cost",
        "threshold": threshold, "packets": len(packets), "decided": len(eff), "unconsumed": total,
        "bundle_by_file": bundle_by_file, "heads": len(closures), "units": units,
        "cutset": cut, "priority_walk": walk, "diagnostics": diagnostics(graph),
    }


def render(rep: Dict[str, Any]) -> str:
    L = [f"CLOSURE CUT-SET · {rep['kernel']} · head {rep['head']} · unconsumed {rep['unconsumed']} · threshold {rep['threshold']} · units {len(rep['units'])}",
         f"{'unit':44} {'closes':>6} {'conf':>5} {'cost':>4} {'prio':>7}  {'resid':>5}  confidence_source"]
    for u, w in zip(rep["units"], rep["priority_walk"]):
        L.append(f"{u['unit_id'][:44]:44} {u['closes']:>6} {u['confidence']:>5.2f} {u['cost']:>4} {u['priority_0']:>7}  {w['residual_after']:>5}  {u['confidence_source'][:60]}")
    c = rep["cutset"]
    L.append(f"\nEXACT CUT-SET: {c['k']} decisions · cost {c['cost']} · closes {c['closed']} → residual {c['residual']} (need closed ≥ {c['need_closed']})")
    for m in c["members"]:
        L.append(f"  ● {m}")
    d = rep["diagnostics"]
    L.append(f"\nDIAGNOSTICS: {d['children']} children · {len(d['verification_children'])} verification-as-child (declared) · {d['undeclared_discriminators']} children with no declared discriminators")
    L.append("authority=false · this ranks; only the operator's pen consumes")
    return "\n".join(L)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outbox", type=Path, default=pen.DEFAULT_OUTBOX)
    ap.add_argument("--log", type=Path, default=pen.DEFAULT_LOG)
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    ap.add_argument("--bundle-by-file", action="store_true", help="one unit per top source_ref file")
    ap.add_argument("--out", type=Path, default=Path("artifacts/closure_cutset.json"))
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--duplicate", nargs=2, metavar=("A", "B"), action="append", help="run the duplicate discriminator on a pair (repeatable)")
    a = ap.parse_args(argv)
    if a.duplicate:
        packets = pen.load_packets(a.outbox)
        eff = pen.effective_decisions(pen.read_log(a.log))
        open_ = pen.unconsumed(packets, eff)
        for x, y in a.duplicate:
            v = duplicate_test(x, y, open_, a.threshold)
            print(f"{v['verdict']:11} {x} ~ {y}\n" + "".join(f"             · {r}\n" for r in v["reasons"]), end="")
        return 0
    rep = compute(a.outbox, a.log, a.threshold, a.bundle_by_file)
    print(render(rep))
    if not a.no_write:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n")
        print(f"\nreport → {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
