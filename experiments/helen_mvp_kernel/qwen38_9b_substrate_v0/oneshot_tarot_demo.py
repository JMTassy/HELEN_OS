#!/usr/bin/env python3
"""
ONESHOT DEMO — Qwen3.8-9B in action on one discriminator prompt (operator
verbatim). No scoring, no comparison. NON_SOVEREIGN · authority=false ·
canon=false · ledger_effect=none.
"""
import json, pathlib, subprocess, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
RT = json.loads((HERE / "v3" / "runtime_contract.json").read_text())
M = RT["models"]["SUB_2"]
PATH = str(pathlib.Path(M["path"]).expanduser())
PORT = 8094

PROMPT = '''You are a HELEN discriminator.
Evaluate the claim:
A 1781 document attributes Tarot to ancient Egypt.
Tarot is independently attested in Europe centuries earlier.
Candidate conclusion:
'Tarot originated in ancient Egypt.'
Return strict JSON only:
{
  "verdict": "ADMIT|HOLD|REJECT",
  "edge_type": "",
  "observed_nodes": [],
  "missing_warrants": [],
  "morphism_laundering": [],
  "rival_hypotheses": [],
  "confidence": 0.0,
  "reason": ""
}
Rule:
Observed(A) AND Observed(B) does not imply Observed(A -> B).
Ask: WHAT LICENSES THIS ARROW?'''

def main():
    proc = subprocess.Popen(["llama-server", "-m", PATH] + RT["args"]
                            + ["--port", str(PORT), "--no-webui"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(180):
            try:
                urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2)
                break
            except Exception:
                time.sleep(1)
        body = json.dumps({"messages": [{"role": "user", "content": PROMPT}],
                           "max_tokens": RT["sampling"]["max_tokens"],
                           "temperature": RT["sampling"]["temperature"],
                           "seed": RT["sampling"]["seed"]}).encode()
        req = urllib.request.Request(f"http://localhost:{PORT}/v1/chat/completions",
                                     body, {"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=900) as r:
            resp = json.loads(r.read())
        latency = time.time() - t0
        out = {"model_file": PATH, "sha256_expected": M["sha256"],
               "server_model_id": resp.get("model"),
               "latency_s": round(latency, 2),
               "usage": resp.get("usage"),
               "raw_output": resp["choices"][0]["message"]["content"]}
        (HERE / "ONESHOT_TAROT_DEMO.json").write_text(json.dumps(out, indent=2))
        print(json.dumps(out, indent=2))
    finally:
        proc.terminate(); proc.wait(timeout=15)

if __name__ == "__main__":
    main()
