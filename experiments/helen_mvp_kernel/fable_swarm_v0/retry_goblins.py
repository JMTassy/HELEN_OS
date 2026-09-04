#!/usr/bin/env python3
"""Retry the 5 truncated goblins at 4000-token ceiling (instrument fix,
declared). Reuses CONTEXT/ROLES/SCHEMA from swarm_goblins.py source."""
import json, pathlib, subprocess, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / "swarm_goblins.py").read_text()
ns = {"__file__": str(HERE / "swarm_goblins.py")}
exec(src.split("def ask(")[0], ns)
CONTEXT, ROLES, SCHEMA = ns["CONTEXT"], ns["ROLES"], ns["SCHEMA"]

RT = json.loads((HERE.parent / "qwen38_9b_substrate_v0" / "v3" /
                 "runtime_contract.json").read_text())
PATH = str(pathlib.Path(RT["models"]["SUB_2"]["path"]).expanduser())
PORT = 8094
RETRY = ["A_ARCHITECT", "B_FALSIFIER", "C_BUILDER", "D_EXPERIMENTER", "E_ADVERSARY"]

proc = subprocess.Popen(["llama-server", "-m", PATH] + RT["args"]
                        + ["--port", str(PORT), "--no-webui"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(240):
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2)
            break
        except Exception:
            time.sleep(1)
    time.sleep(2)
    for key in RETRY:
        prompt = (CONTEXT + "\n\n" + ROLES[key] + "\n\n" + SCHEMA +
                  "\n\nEnvelope: authority=false, no_claim=true. "
                  "Be concise; think briefly.")
        body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                           "max_tokens": 4000, "temperature": 0,
                           "seed": 0}).encode()
        req = urllib.request.Request(
            f"http://localhost:{PORT}/v1/chat/completions", body,
            {"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=900) as r:
            j = json.loads(r.read())
        env = {"goblin": key, "raw": j["choices"][0]["message"]["content"],
               "usage": j.get("usage", {}),
               "latency_s": round(time.time() - t0, 1),
               "ceiling": 4000, "retry_of": "truncated_2000",
               "authority": False, "no_claim": True, "proposal_only": True}
        (HERE / f"envelope_{key}.json").write_text(json.dumps(env, indent=2))
        print(key, env["latency_s"], "s ct=",
              env["usage"].get("completion_tokens"), flush=True)
    print("DONE_RETRY")
finally:
    proc.terminate(); proc.wait(timeout=15)
