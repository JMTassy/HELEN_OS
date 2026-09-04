#!/usr/bin/env python3
"""Run ONE goblin against an already-running :8094 server. argv[1]=key."""
import json, pathlib, sys, time, urllib.request
HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / "swarm_goblins.py").read_text()
ns = {"__file__": str(HERE / "swarm_goblins.py")}
exec(src.split("def ask(")[0], ns)
key = sys.argv[1]
prompt = (ns["CONTEXT"] + "\n\n" + ns["ROLES"][key] + "\n\n" + ns["SCHEMA"] +
          "\n\nEnvelope: authority=false, no_claim=true. Be concise; think briefly.")
body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                   "max_tokens": 4000, "temperature": 0, "seed": 0}).encode()
req = urllib.request.Request("http://localhost:8094/v1/chat/completions", body,
                             {"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=540) as r:
    j = json.loads(r.read())
env = {"goblin": key, "raw": j["choices"][0]["message"]["content"],
       "usage": j.get("usage", {}), "latency_s": round(time.time() - t0, 1),
       "ceiling": 4000, "retry_of": "truncated_2000_then_infra_kill",
       "authority": False, "no_claim": True, "proposal_only": True}
(HERE / f"envelope_{key}.json").write_text(json.dumps(env, indent=2))
print(key, env["latency_s"], "s ct=", env["usage"].get("completion_tokens"))
