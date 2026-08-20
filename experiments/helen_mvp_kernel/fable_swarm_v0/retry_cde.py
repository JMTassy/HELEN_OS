#!/usr/bin/env python3
"""Bounded retry C/D/E @4000 (same sanctioned ceiling as B's success).
Per-call error isolation: an ERROR becomes a witness, not a loop-killer."""
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

def healthy():
    try:
        urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2)
        return True
    except Exception:
        return False

proc = subprocess.Popen(["llama-server", "-m", PATH] + RT["args"]
                        + ["--port", str(PORT), "--no-webui"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(240):
        if healthy(): break
        time.sleep(1)
    time.sleep(2)
    for key in ["C_BUILDER", "D_EXPERIMENTER", "E_ADVERSARY"]:
        if not healthy():
            print(f"{key}: SERVER_DOWN witness — skipping", flush=True)
            continue
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
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                j = json.loads(r.read())
            env = {"goblin": key, "raw": j["choices"][0]["message"]["content"],
                   "usage": j.get("usage", {}),
                   "latency_s": round(time.time() - t0, 1),
                   "ceiling": 4000, "retry_of": "truncated_2000_then_error",
                   "authority": False, "no_claim": True, "proposal_only": True}
            (HERE / f"envelope_{key}.json").write_text(json.dumps(env, indent=2))
            print(key, env["latency_s"], "s ct=",
                  env["usage"].get("completion_tokens"), flush=True)
        except Exception as ex:
            (HERE / f"error_witness_{key}.json").write_text(json.dumps(
                {"goblin": key, "error": repr(ex),
                 "elapsed_s": round(time.time() - t0, 1),
                 "note": "execution witness, not cognitive result"}, indent=2))
            print(f"{key}: ERROR witness {repr(ex)[:80]}", flush=True)
    print("DONE_RETRY_CDE")
finally:
    proc.terminate(); proc.wait(timeout=15)
