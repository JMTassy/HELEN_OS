#!/usr/bin/env python3
"""FRICTION 1 — fingerprint differ: names WHERE and HOW two ledgers bifurcated.

Takes 2+ LEDGER_DEVICE_FINGERPRINT_V1 documents and reports, per ledger:
the first divergent seq, and a classified suspicion for the cause.

    python3 ledger_diff.py imac.fingerprint.json macbook.fingerprint.json

The suspicion classifier is deliberately conservative: it reports the
narrowest explanation the evidence supports and says UNKNOWN otherwise.
Naming the mechanism is the point; guessing it is not.

NON_SOVEREIGN. authority=false. Read-only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCHEMA = "LEDGER_DEVICE_FINGERPRINT_V1"


def load(p: str) -> dict:
    doc = json.loads(Path(p).read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise SystemExit(f"{p}: not a {SCHEMA} document")
    return doc


def classify(a: dict, b: dict, first_div: dict | None) -> list[str]:
    """Narrowest supported explanations for a divergence. Conservative."""
    s = []

    if a.get("rows") != b.get("rows"):
        s.append(
            f"ROW_COUNT_DIFFERS ({a.get('rows')} vs {b.get('rows')}) — one device "
            "has events the other never saw (live daemon writes / unsynced work). "
            "Most common cause; check before suspecting corruption.")

    if (a.get("raw_sha256") != b.get("raw_sha256")
            and a.get("content_sha256") == b.get("content_sha256")):
        s.append(
            "BYTES_DIFFER_CONTENT_IDENTICAL — same events, different file bytes. "
            f"line_ending {a.get('line_ending')} vs {b.get('line_ending')}, "
            f"trailing_newline {a.get('trailing_newline')} vs {b.get('trailing_newline')}. "
            "Encoding/EOL normalization, not a ledger fork.")

    if first_div and first_div.get("kind") == "payload_hash":
        tampered = [lbl for lbl, side in (("A", first_div.get("a", {})),
                                          ("B", first_div.get("b", {})))
                    if side.get("tamper")]
        s.append(
            f"PAYLOAD_DRIFT at seq {first_div['seq']} — same position, different "
            "payload content. Inspect that event's payload on both devices: "
            "float repr, timestamp leak into hashed core, or dict ordering.")
        if tampered:
            s.append(
                f"TAMPER_FLAG on device(s) {', '.join(tampered)} at seq "
                f"{first_div['seq']} — the payload does not match its own stored "
                "payload_hash. The payload was edited after the hash was written.")

    if first_div and first_div.get("kind") == "cum_hash_only":
        s.append(
            f"CHAIN_DRIFT at seq {first_div['seq']} — payloads match but chain "
            "hashes differ. Ordering or a prior insertion/deletion upstream; "
            "the payload at this seq is innocent.")

    ia, ib = a.get("integrity", {}), b.get("integrity", {})
    for label, integ in (("A", ia), ("B", ib)):
        if integ.get("payload_hash_mismatch") or integ.get("cum_hash_mismatch"):
            s.append(
                f"SELF_INCONSISTENT_{label} — this device's ledger does not "
                "recompute against itself (before any cross-device comparison). "
                "Fix locally first; cross-device diff is meaningless until then.")
        if integ.get("linkage_breaks"):
            s.append(
                f"LINKAGE_BREAK_{label} — {integ['linkage_breaks']} place(s) where "
                "prev_cum_hash does not point at the previous cum_hash.")

    if not s:
        s.append("NO_DIVERGENCE_DETECTED at fingerprint resolution.")
    return s


def first_divergence(a: dict, b: dict) -> dict | None:
    """Locate the first divergent seq, preferring per-seq data over checkpoints."""
    pa, pb = a.get("per_seq"), b.get("per_seq")
    if pa and pb:
        common = sorted(set(pa) & set(pb), key=int)
        for k in common:
            ra, rb = pa[k], pb[k]
            if ra["p"] != rb["p"]:
                return {"seq": int(k), "kind": "payload_hash",
                        "a": ra, "b": rb, "resolution": "exact"}
            if ra["c"] != rb["c"]:
                return {"seq": int(k), "kind": "cum_hash_only",
                        "a": ra, "b": rb, "resolution": "exact"}
        only_a = sorted(set(pa) - set(pb), key=int)
        only_b = sorted(set(pb) - set(pa), key=int)
        if only_a or only_b:
            return {"seq": int((only_a or only_b)[0]), "kind": "seq_missing",
                    "a": {"only_in_A": only_a[:5]} if only_a else {"only_in_A": []},
                    "b": {"only_in_B": only_b[:5]} if only_b else {"only_in_B": []},
                    "resolution": "exact"}
        return None

    ca, cb = a.get("checkpoints", {}), b.get("checkpoints", {})
    for k in sorted(set(ca) & set(cb), key=int):
        if ca[k] != cb[k]:
            return {"seq": int(k), "kind": "cum_hash_only",
                    "a": {"c": ca[k]}, "b": {"c": cb[k]},
                    "resolution": f"checkpoint (±stride) — rerun with per_seq for exact"}
    return None


def compare(doc_a: dict, doc_b: dict) -> None:
    la, lb = doc_a["label"], doc_b["label"]
    print("=" * 68)
    print(f"LEDGER DIVERGENCE REPORT — {la} vs {lb}")
    print("=" * 68)

    print("\n-- DEVICE --")
    da, db = doc_a["device"], doc_b["device"]
    for key in sorted(set(da) | set(db)):
        va, vb = da.get(key), db.get(key)
        mark = "  " if va == vb else "!!"
        print(f" {mark} {key:24} {la}={va}")
        if va != vb:
            print(f"    {'':24} {lb}={vb}")

    by_path_b = {l["path"].split("/")[-1]: l for l in doc_b["ledgers"]}
    for a in doc_a["ledgers"]:
        name = a["path"].split("/")[-1]
        b = by_path_b.get(name)
        print(f"\n-- LEDGER: {name} --")
        if b is None:
            print(f"    absent from {lb} fingerprint — cannot compare")
            continue
        if not a.get("present") or not b.get("present"):
            print(f"    present: {la}={a.get('present')} {lb}={b.get('present')}")
            continue

        print(f"    rows          {la}={a['rows']}  {lb}={b['rows']}")
        print(f"    raw_sha256    {a['raw_sha256'][:16]}…  {b['raw_sha256'][:16]}…"
              f"  {'MATCH' if a['raw_sha256'] == b['raw_sha256'] else 'DIFFER'}")
        print(f"    content_sha   {a.get('content_sha256','')[:16]}…  "
              f"{b.get('content_sha256','')[:16]}…"
              f"  {'MATCH' if a.get('content_sha256') == b.get('content_sha256') else 'DIFFER'}")
        print(f"    final_cum     {a['final_cum_hash'][:16]}…  {b['final_cum_hash'][:16]}…"
              f"  {'MATCH' if a['final_cum_hash'] == b['final_cum_hash'] else 'DIFFER'}")

        div = first_divergence(a, b)
        if div:
            print(f"\n    FIRST DIVERGENT SEQ: {div['seq']}  "
                  f"({div['kind']}, {div['resolution']})")
            print(f"      {la}: {div.get('a')}")
            print(f"      {lb}: {div.get('b')}")
        else:
            print("\n    no divergence located at fingerprint resolution")

        print("\n    SUSPICION:")
        for line in classify(a, b, div):
            print(f"      · {line}")

    print()


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    docs = [load(p) for p in sys.argv[1:]]
    for i in range(len(docs) - 1):
        compare(docs[i], docs[i + 1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
