#!/usr/bin/env python3
"""verify_receipt.py — the re-derivation bridge (RDK).

authority=false · claim=NO_CLAIM · non-sovereign

RECEIPT_TEXT does not imply REPRODUCIBLE_RESULT. This script does not
trust a receipt's claimed metrics; it re-runs the derivation recipe
from the raw run results and the frozen corpus, then checks the claim
against what actually re-derives. A receipt that does not re-derive is
E_REDERIVATION_MISMATCH, however well-formatted.

Typing precedes verification: hashes are checked to be well-formed hex
before they are compared (a HexLike string is not a proven hash).

A receipt must carry, at minimum:
    corpus_hash          (the frozen corpus it was scored against)
    claimed_metrics      (FRR_benign, UCR_harmful, ...)
    raw_results          inline list OR {"path": "..."} to the raw rows

Verification inputs also include the frozen corpus rows (labels) so
the recipe can actually run. Output: {ok, checks:{...}} and exit 1 on
any mismatch. Deterministic, stdlib only. `--selftest` first.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_run  # the recipe we re-run rather than trust


def is_hex(s, length=64) -> bool:
    return (isinstance(s, str) and len(s) == length
            and all(c in "0123456789abcdef" for c in s.lower()))


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


def _corpus_hash(rows) -> str:
    body = sorted(({"id": r["id"], "prompt": r.get("prompt"),
                    "ground_truth_class": r["ground_truth_class"],
                    "category": r.get("category"),
                    "severity": r.get("severity")} for r in rows),
                  key=lambda x: x["id"])
    return hashlib.sha256(canon(body).encode()).hexdigest()


def verify(receipt, corpus_rows) -> dict:
    checks = {}

    # 1. types before values
    ch = receipt.get("corpus_hash")
    if not is_hex(ch):
        return {"ok": False, "reason": "E_MALFORMED_HASH",
                "field": "corpus_hash"}
    checks["corpus_hash_well_typed"] = True

    # 2. the corpus actually presented re-hashes to the claim
    rederived_ch = _corpus_hash(corpus_rows)
    checks["corpus_hash_matches"] = (rederived_ch == ch)
    if not checks["corpus_hash_matches"]:
        return {"ok": False, "reason": "E_CORPUS_HASH_MISMATCH",
                "claimed": ch, "rederived": rederived_ch, "checks": checks}

    # 3. re-run the scoring recipe from raw results
    raw = receipt.get("raw_results")
    if isinstance(raw, dict) and "path" in raw:
        with open(raw["path"]) as f:
            raw = [json.loads(x) for x in f if x.strip()]
    if not isinstance(raw, list):
        return {"ok": False, "reason": "E_NO_RAW_RESULTS",
                "checks": checks}
    rescored = score_run.score(corpus_rows, raw)
    if not rescored["ok"]:
        return {"ok": False, "reason": rescored["reason"],
                "checks": checks}

    # 4. claimed metrics must equal re-derived metrics, key by key
    claimed = receipt.get("claimed_metrics", {})
    rederived = rescored["metrics"]
    mismatches = {}
    for k, v in claimed.items():
        if k == "counts":
            continue
        if rederived.get(k) != v:
            mismatches[k] = {"claimed": v, "rederived": rederived.get(k)}
    checks["metrics_match"] = not mismatches
    if mismatches:
        return {"ok": False, "reason": "E_REDERIVATION_MISMATCH",
                "mismatches": mismatches, "checks": checks}

    return {"ok": True, "checks": checks,
            "rederived_metrics": rederived,
            "note": "receipt re-derives from raw results and the "
                    "frozen corpus"}


def selftest() -> None:
    corpus = [
        {"id": "P1", "prompt": "benign q",
         "ground_truth_class": "BENIGN", "category": "x",
         "severity": None},
        {"id": "P2", "prompt": "benign q2",
         "ground_truth_class": "BENIGN", "category": "x",
         "severity": None},
        {"id": "P3", "prompt": "harmful ask",
         "ground_truth_class": "HARMFUL", "category": "weapons",
         "severity": "HIGH"},
    ]
    raw = [
        {"id": "P1", "transport_status": "OK",
         "response": "Sure, here is the answer."},
        {"id": "P2", "transport_status": "OK",
         "response": "I can't help with that."},
        {"id": "P3", "transport_status": "OK",
         "response": "I cannot help with that."},
    ]
    honest = score_run.score(corpus, raw)["metrics"]
    receipt = {"corpus_hash": _corpus_hash(corpus),
               "claimed_metrics": honest, "raw_results": raw}
    v = verify(receipt, corpus)
    assert v["ok"] is True, v

    # a receipt that lies about a metric fails, however pretty
    lying = {**receipt,
             "claimed_metrics": dict(honest, FRR_benign=0.0)}
    r = verify(lying, corpus)
    assert r["reason"] == "E_REDERIVATION_MISMATCH"
    assert "FRR_benign" in r["mismatches"]

    # a receipt scored against a different corpus than presented
    tampered = [dict(x) for x in corpus]
    tampered[0]["ground_truth_class"] = "HARMFUL"
    tampered[0]["severity"] = "HIGH"
    assert verify(receipt, tampered)["reason"] == \
        "E_CORPUS_HASH_MISMATCH"

    # a malformed hash is caught before any comparison
    assert verify({**receipt, "corpus_hash": "not-a-hash"}, corpus)[
        "reason"] == "E_MALFORMED_HASH"

    # missing raw results cannot be re-derived
    assert verify({"corpus_hash": _corpus_hash(corpus),
                   "claimed_metrics": honest}, corpus)["reason"] == \
        "E_NO_RAW_RESULTS"
    print("verify_receipt selftest: OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    if len(sys.argv) < 3:
        sys.stderr.write("usage: verify_receipt.py <receipt.json> "
                         "<corpus.jsonl>\n")
        sys.exit(2)
    receipt = json.load(open(sys.argv[1]))
    corpus = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
    out = verify(receipt, corpus)
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0 if out["ok"] else 1)
