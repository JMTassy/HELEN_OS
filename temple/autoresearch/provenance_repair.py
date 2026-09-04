#!/usr/bin/env python3
"""provenance_repair.py — constrained parent_epoch repair for unconsumed outbox packets.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none · PROPOSAL ONLY

Repairs a missing `parent_epoch` ONLY where parentage is mechanically recoverable from
already-declared packet state. Chronological adjacency is never a reason.

  R1  forward declaration — exactly one earlier unconsumed packet's `next` field names
      the child's epoch (regex \\bE<n>\\b). Source: "<parent>.next".
  R2  backward declaration — the child's own `summary` names one or more earlier epochs,
      and every one of them lies on a single already-declared ancestor chain of the
      graph. Parent = the maximal element of that chain. Source: "summary refs ⊆ chain(<p>)".
      Applied iteratively (a repair may complete the chain another packet needs), in
      ascending epoch order, so each step relies only on state declared before it.

Anything else — empty summary, references spanning two chains, a referenced epoch that
is not in the outbox — is reported UNRECOVERABLE and left untouched.

Every applied repair is recorded twice: in the packet itself under `provenance_repairs`
(field, before, after, rule, source, at) and in a receipt file carrying the packet's
pre-image and post-image sha256. Consumed packets (marked in the pen) are never touched:
the pen binds to packet bytes.

Usage:
  python3 temple/autoresearch/provenance_repair.py            # dry run: report only
  python3 temple/autoresearch/provenance_repair.py --apply    # write repairs + receipt
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
try:
    from temple.autoresearch import operator_pen as pen  # type: ignore
except Exception:  # pragma: no cover
    import operator_pen as pen  # type: ignore

REPAIR_VERSION = "PROVENANCE_REPAIR_V0"
DEFAULT_RECEIPT_DIR = Path("temple/autoresearch/repairs")
_E = re.compile(r"\bE(\d+)\b")


def _n(e: Any) -> int:
    m = re.match(r"^E(\d+)$", str(e or ""))
    return int(m.group(1)) if m else -1


def _chain(epoch: str, parent_of: Dict[str, str]) -> List[str]:
    """Declared ancestor chain of `epoch`, inclusive, following parent_epoch only."""
    out, cur, seen = [], epoch, set()
    while cur and cur not in seen:
        out.append(cur); seen.add(cur); cur = parent_of.get(cur)
    return out


def plan(packets: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (repairs, unrecoverable). Pure: no I/O."""
    by_epoch: Dict[str, Dict[str, Any]] = {}
    for p in packets:
        e = str(p.get("epoch") or "")
        if e and e not in by_epoch:
            by_epoch[e] = p
    parent_of: Dict[str, str] = {e: str(p["parent_epoch"]) for e, p in by_epoch.items()
                                 if p.get("parent_epoch") and str(p["parent_epoch"]) in by_epoch}
    missing = sorted((e for e, p in by_epoch.items() if not p.get("parent_epoch")), key=_n)
    repairs, unrec = [], []

    def surface(p: Dict[str, Any]) -> str:
        return str(p.get("surface") or p.get("target") or p.get("target_surface") or "")

    for e in missing:
        child = by_epoch[e]
        # R1: forward declaration by exactly one earlier packet's `next`, on the same declared
        # surface. A `next` naming an epoch number is a plan; it is lineage only when the packet
        # that materialised under that number belongs to the same surface.
        fwd_all = [pe for pe, pp in by_epoch.items() if _n(pe) < _n(e) and re.search(r"\b" + re.escape(e) + r"\b", str(pp.get("next") or ""))]
        fwd = [pe for pe in fwd_all if surface(by_epoch[pe]) == surface(child)]
        if len(fwd_all) == 1 and not fwd:
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": f"R1 refused: {by_epoch[fwd_all[0]]['packet_id']}.next names {e} but surfaces differ ({surface(by_epoch[fwd_all[0]])!r} vs {surface(child)!r}) — a plan, not lineage"})
            continue
        if len(fwd) == 1:
            repairs.append({"epoch": e, "packet_id": child["packet_id"], "field": "parent_epoch", "before": None,
                            "after": fwd[0], "rule": "R1", "source": f"{by_epoch[fwd[0]]['packet_id']}.next names {e}"})
            parent_of[e] = fwd[0]
            continue
        if len(fwd) > 1:
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": f"R1 ambiguous: {sorted(fwd)} all name {e} in next"})
            continue
        # R2: backward declaration in the child's own summary, all refs on one declared chain
        summary = str(child.get("summary") or "")
        refs = sorted({f"E{m}" for m in _E.findall(summary) if int(m) < _n(e)}, key=_n)
        if not summary.strip():
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": "empty summary: nothing declared"})
            continue
        if not refs:
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": "summary names no earlier epoch"})
            continue
        absent = [r for r in refs if r not in by_epoch]
        if absent:
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": f"summary names {absent} not present in outbox (refs {refs})"})
            continue
        top = max(refs, key=_n)
        chain = _chain(top, parent_of)
        off = [r for r in refs if r not in chain]
        if off:
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": f"summary refs {refs} span more than one declared chain: {off} ∉ chain({top})={chain}"})
            continue
        foreign = [r for r in refs if surface(by_epoch[r]) != surface(child)]
        if foreign:
            unrec.append({"epoch": e, "packet_id": child["packet_id"], "reason": f"R2 refused: refs {foreign} are on another surface than {surface(child)!r}"})
            continue
        repairs.append({"epoch": e, "packet_id": child["packet_id"], "field": "parent_epoch", "before": None,
                        "after": top, "rule": "R2", "source": f"summary refs {refs} ⊆ declared chain({top})={chain}"})
        parent_of[e] = top
    return repairs, unrec


def apply(outbox: Path, log: Path, receipt_dir: Path, do_apply: bool) -> Dict[str, Any]:
    packets = pen.load_packets(outbox)
    entries = pen.read_log(log)
    broken = pen.verify_chain(entries)
    if broken:
        raise SystemExit(f"❌ consumption log chain broken ({broken}) — refusing to touch packets")
    eff = pen.effective_decisions(entries)
    open_ = pen.unconsumed(packets, eff)
    repairs, unrec = plan(open_)
    at = datetime.now(timezone.utc).isoformat()
    receipt = {"schema": REPAIR_VERSION, "at": at, "authority": False, "canon": False, "ledger_effect": "none",
               "applied": do_apply, "repairs": [], "unrecoverable": unrec}
    by_id = {p["packet_id"]: p for p in open_}
    for r in repairs:
        p = by_id[r["packet_id"]]
        path = Path(p["_path"])
        pre = path.read_bytes()
        d = json.loads(pre)
        assert not d.get("parent_epoch"), "refusing to overwrite a declared parent"
        d["parent_epoch"] = r["after"]
        d.setdefault("provenance_repairs", []).append({k: r[k] for k in ("field", "before", "after", "rule", "source")} | {"at": at, "repair": REPAIR_VERSION})
        post = (json.dumps(d, indent=2, ensure_ascii=False) + "\n").encode()
        rec = {**r, "path": str(path), "pre_sha256": hashlib.sha256(pre).hexdigest(), "post_sha256": hashlib.sha256(post).hexdigest()}
        if do_apply:
            path.write_bytes(post)
        receipt["repairs"].append(rec)
    if do_apply:
        receipt_dir.mkdir(parents=True, exist_ok=True)
        out = receipt_dir / f"{REPAIR_VERSION}_{at[:10]}.json"
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        receipt["receipt_path"] = str(out)
    return receipt


def render(rc: Dict[str, Any]) -> str:
    L = [f"{rc['schema']} · {'APPLIED' if rc['applied'] else 'DRY RUN'} · {len(rc['repairs'])} repairable · {len(rc['unrecoverable'])} unrecoverable"]
    for r in rc["repairs"]:
        L.append(f"  ✔ {r['epoch']:>4} parent_epoch None → {r['after']}   [{r['rule']}] {r['source']}")
    for u in rc["unrecoverable"]:
        L.append(f"  ✘ {u['epoch']:>4} left untouched — {u['reason']}")
    if rc.get("receipt_path"):
        L.append(f"receipt → {rc['receipt_path']}")
    L.append("authority=false · consumed packets never touched · chronology is not a rule")
    return "\n".join(L)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outbox", type=Path, default=pen.DEFAULT_OUTBOX)
    ap.add_argument("--log", type=Path, default=pen.DEFAULT_LOG)
    ap.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPT_DIR)
    ap.add_argument("--apply", action="store_true", help="write repairs into packets and emit a receipt")
    a = ap.parse_args(argv)
    print(render(apply(a.outbox, a.log, a.receipts, a.apply)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
