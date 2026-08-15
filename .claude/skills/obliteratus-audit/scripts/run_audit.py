#!/usr/bin/env python3
"""run_audit.py — run every prompt, record raw item-level results, and
score NOTHING.

authority=false · claim=NO_CLAIM · non-sovereign

Collection and scoring are separated on purpose: a runner that scores
opportunistically while generating is a runner that can talk itself
into a favorable label. This script only produces the raw evidence
score_run.py will later grade.

Model access is via an adapter. Three modes:
  --responses FILE.jsonl   ingest pre-collected {id, response} rows
                           (transport_status inferred: OK, or
                           EXECUTION_ERROR when response is null/empty)
  --null                   no model available: every item is an honest
                           EXECUTION_ERROR (NOT a refusal, NOT a zero)
  (default)                same as --null, with a loud note that no
                           model was wired

Output (stdout): one raw row per corpus id —
    {"id", "prompt", "response", "transport_status"}
transport_status in {OK, EXECUTION_ERROR}. Behavior is never inferred
here; EVALUATOR_UNRESOLVED is a scoring outcome, not a transport one.

Deterministic, stdlib only. `run_audit.py --selftest` first.
"""
from __future__ import annotations

import json
import sys


def _load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def audit(corpus_rows, responses=None) -> list:
    """responses: optional {id: response_str_or_None}. Missing or
    empty responses become EXECUTION_ERROR — never a silent refusal,
    because UNREADABLE != ZERO_CANDIDATES."""
    resp = responses or {}
    out = []
    for r in corpus_rows:
        rid = r["id"]
        body = resp.get(rid)
        if body is None or (isinstance(body, str) and not body.strip()):
            out.append({"id": rid, "prompt": r["prompt"],
                        "response": None,
                        "transport_status": "EXECUTION_ERROR"})
        else:
            out.append({"id": rid, "prompt": r["prompt"],
                        "response": body,
                        "transport_status": "OK"})
    return out


def summarize(raw) -> dict:
    ok = sum(1 for x in raw if x["transport_status"] == "OK")
    err = sum(1 for x in raw if x["transport_status"] ==
              "EXECUTION_ERROR")
    return {"n": len(raw), "ok": ok, "execution_error": err,
            "scored_here": False}


def selftest() -> None:
    corpus = [{"id": "P0001", "prompt": "benign q"},
              {"id": "P0002", "prompt": "harmful ask"},
              {"id": "P0003", "prompt": "another"}]
    # no model -> all EXECUTION_ERROR, none laundered into refusal
    raw = audit(corpus, responses=None)
    assert all(x["transport_status"] == "EXECUTION_ERROR" for x in raw)
    assert all(x["response"] is None for x in raw)
    assert summarize(raw)["scored_here"] is False
    # partial responses: empty string is an error, not a refusal
    resp = {"P0001": "Sure, here is how to center a div...",
            "P0002": "I can't help with that.",
            "P0003": "   "}
    raw = audit(corpus, resp)
    by = {x["id"]: x for x in raw}
    assert by["P0001"]["transport_status"] == "OK"
    assert by["P0002"]["transport_status"] == "OK"     # a refusal is
    # a real behavior to be scored later, NOT an execution error
    assert by["P0003"]["transport_status"] == "EXECUTION_ERROR"
    # no verdict field is ever emitted here
    assert all("verdict" not in x for x in raw)
    assert all(set(x) == {"id", "prompt", "response",
                          "transport_status"} for x in raw)
    print("run_audit selftest: OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    args = sys.argv[1:]
    if not args or args[0] in ("--null",):
        sys.stderr.write("run_audit: no model wired; emitting honest "
                         "EXECUTION_ERROR for every item.\n")
        # requires a corpus path as the last arg
        corpus_path = args[-1] if args and not args[-1].startswith("-") \
            else None
        if not corpus_path:
            sys.stderr.write("usage: run_audit.py [--null] <corpus.jsonl>"
                             " | --responses R.jsonl <corpus.jsonl>\n")
            sys.exit(2)
        raw = audit(_load_jsonl(corpus_path), None)
    elif args[0] == "--responses":
        resp_rows = _load_jsonl(args[1])
        resp = {r["id"]: r.get("response") for r in resp_rows}
        raw = audit(_load_jsonl(args[2]), resp)
    else:
        raw = audit(_load_jsonl(args[-1]), None)
    for row in raw:
        sys.stdout.write(json.dumps(row, ensure_ascii=False) + "\n")
    sys.exit(0)
