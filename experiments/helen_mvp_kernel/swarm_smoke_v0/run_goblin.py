#!/usr/bin/env python3
"""SWARM_SMOKE_V0 — one isolated Qwen goblin. argv[1] in {G1,G2,G3}.
enable_thinking=false (chat_template_kwargs) — distinct from HTTP timeout.
Isolated: receives frozen corpus + question only; no other goblin output."""
import json, pathlib, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PRE = json.loads((HERE / "preflight.json").read_text())
gid = sys.argv[1]

corpus_text = "\n\n".join(
    f"=== {m['path']} (sha {m['sha256'][:12]}) ===\n"
    + (HERE / m["path"]).read_text()
    for m in PRE["corpus_manifest"])

SCHEMA = json.dumps(PRE["output_schema"], indent=1)
SYS = (
 "You are an isolated HELEN discriminator goblin. You inspect a small frozen "
 "corpus and answer ONE bounded question. authority=false. You do NOT admit, "
 "recommend, or synthesize. Output STRICT JSON matching the schema, nothing else.")
USER = (
 f"CAMPAIGN: SWARM_SMOKE_V0  GOBLIN: {gid}  task_hash: {PRE['task_hash']}\n\n"
 f"BOUNDED QUESTION (answer only this):\n{PRE['question']}\n\n"
 f"The corpus below is the entire world for this task. Cite evidence as "
 f"path:line using the exact filenames shown.\n\nCORPUS:\n{corpus_text}\n\n"
 f"OUTPUT SCHEMA (return one object, {PRE['budget']['max_claims']} claims max, "
 f"<= {PRE['budget']['max_words']} words total, each claim needs predicate, "
 f"object, scope, evidence_refs, candidate_falsifier):\n{SCHEMA}\n\n"
 f"Set goblin_id={gid}, campaign_id=SWARM_SMOKE_V0, task_hash={PRE['task_hash']}, "
 f"authority=false, ledger_effect=none.")

body = json.dumps({
    "messages": [{"role": "system", "content": SYS},
                 {"role": "user", "content": USER}],
    "max_tokens": PRE["budget"]["max_output_tokens"],
    "temperature": 0, "seed": 0,
    "chat_template_kwargs": {"enable_thinking": False}}).encode()
req = urllib.request.Request("http://localhost:8094/v1/chat/completions", body,
                            {"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=PRE["budget"]["timeout_seconds"]) as r:
    j = json.loads(r.read())
raw = j["choices"][0]["message"]["content"]
out = {"goblin_id": gid, "raw": raw, "usage": j.get("usage", {}),
       "latency_s": round(time.time() - t0, 1),
       "enable_thinking": False, "finish_reason": j["choices"][0].get("finish_reason")}
(HERE / f"{gid}_raw.json").write_text(json.dumps(out, indent=2))
print(gid, out["latency_s"], "s ct=", out["usage"].get("completion_tokens"),
      "finish=", out["finish_reason"])
