#!/usr/bin/env python3
"""Final A/E attempt: PROMPT CLOSURE fix (not a ceiling escalation).
Same 4000 ceiling; the ask is bounded to cap think-channel overrun."""
import json, pathlib, sys, time, urllib.request
HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / "swarm_goblins.py").read_text()
ns = {"__file__": str(HERE / "swarm_goblins.py")}
exec(src.split("def ask(")[0], ns)
key = sys.argv[1]
CLOSURE = ("\n\nHARD BOUNDS: at most 3 items per list field, each item ONE short "
           "sentence. proposal field: at most 3 sentences. Do not enumerate "
           "alternatives in your head — pick your single best answer directly. "
           "Total response under 300 words.")
prompt = (ns["CONTEXT"] + "\n\n" + ns["ROLES"][key] + "\n\n" + ns["SCHEMA"]
          + CLOSURE + "\n\nEnvelope: authority=false, no_claim=true.")
body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                   "max_tokens": 4000, "temperature": 0, "seed": 0}).encode()
req = urllib.request.Request("http://localhost:8094/v1/chat/completions", body,
                             {"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=540) as r:
    j = json.loads(r.read())
env = {"goblin": key, "raw": j["choices"][0]["message"]["content"],
       "usage": j.get("usage", {}), "latency_s": round(time.time() - t0, 1),
       "ceiling": 4000, "instrument_fix": "prompt_closure (declared; ceiling unchanged)",
       "retry_of": "double_truncated_2000_4000",
       "authority": False, "no_claim": True, "proposal_only": True}
(HERE / f"envelope_{key}.json").write_text(json.dumps(env, indent=2))
print(key, env["latency_s"], "s ct=", env["usage"].get("completion_tokens"))
