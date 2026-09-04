#!/usr/bin/env python3
"""
PROMPT_ABLATION_V0 — vary ONLY the constitutional system-prompt layer over
the frozen V3 morphism-laundering suite; substrate/runtime/template/scorer
fixed. NON_SOVEREIGN · authority=false · ledger_effect=none.
"""
import hashlib, json, pathlib, re, subprocess, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
V3 = HERE.parent / "v3"
sys.path.insert(0, str(V3))
from scorer import score_item, q_of, fixtures, W  # frozen V3 scorer, unmodified

RT = json.loads((V3 / "runtime_contract.json").read_text())
TEMPLATE = (V3 / "template.txt").read_text()
SCHEMA = (V3 / "output_schema.json").read_text().strip()
PORT = RT["port"]; SAMP = RT["sampling"]
MODEL = RT["models"]["SUB_2"]  # 9B
ADAPTER = ("\n\nOUTPUT CONTRACT: Respond with EXACTLY one JSON object matching "
           "the OUTPUT SCHEMA in the user message, and nothing after it. "
           "Evaluate ONLY the CLAIM against the SOURCES given in the item; the "
           "sources are the entire world for this item. source IDs are the "
           "bracketed tokens (e.g. R1). authority=false.")
ARMS = {"ARM_0_BASELINE": "ARM_0_BASELINE.txt",
        "ARM_1_KERNEL7": "ARM_1_KERNEL7.txt",
        "ARM_2_LONG": "ARM_2_LONG.txt"}

def user_message(fx):
    body = TEMPLATE.split("\n\n", 1)[1]
    return body.replace("{source}", fx["source"]).replace("{claim}", fx["claim"]) \
               .replace("{output_schema}", SCHEMA)

def ask(system, user):
    body = json.dumps({"messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}],
                       "max_tokens": SAMP["max_tokens"], "temperature": SAMP["temperature"],
                       "seed": SAMP["seed"]}).encode()
    req = urllib.request.Request(f"http://localhost:{PORT}/v1/chat/completions",
                                 body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def tokens_of(text):
    body = json.dumps({"content": text}).encode()
    req = urllib.request.Request(f"http://localhost:{PORT}/tokenize", body,
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return len(json.loads(r.read()).get("tokens", []))

def extract(text):
    if "</think>" in text:
        text = text.split("</think>")[-1]
    for m in re.finditer(r"\{", text):
        depth = 0
        for j in range(m.start(), len(text)):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        c = json.loads(text[m.start():j + 1])
                        if "epistemic_class" in c:
                            return c
                    except Exception:
                        pass
                    break
        else:
            continue
        break
    return None

def main():
    path = str(pathlib.Path(MODEL["path"]).expanduser())
    proc = subprocess.Popen(["llama-server", "-m", path] + RT["args"]
                            + ["--port", str(PORT), "--no-webui"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2); break
        except Exception:
            time.sleep(1)
    try:
        fxs = fixtures()
        results = {}
        for arm, fname in ARMS.items():
            system = (HERE / fname).read_text().strip() + ADAPTER
            ntok = tokens_of(system)
            scores, raws = [], []
            for fx in fxs:
                raw = ask(system, user_message(fx))
                c = extract(raw)
                s = score_item(fx, c)
                scores.append(s)
                raws.append({"arm": arm, "fixture": fx["fixture_id"],
                             "candidate": c, "scores": s})
            q = round(q_of(scores), 4)
            fmt = round(sum(s["valid"] for s in scores) / len(scores), 3)
            (HERE / f"raw_{arm}.ndjson").write_text(
                "\n".join(json.dumps(x) for x in raws) + "\n")
            results[arm] = {"Q_discrim": q, "Q_formatting": fmt,
                            "system_tokens": ntok}
            print(json.dumps({"arm": arm, **results[arm]}))
        q0, q1, q2 = (results[a]["Q_discrim"] for a in ARMS)
        fmts = [results[a]["Q_formatting"] for a in ARMS]
        if min(fmts) < 0.80:
            disp = "INCONCLUSIVE"
        elif abs(q1 - q2) <= 0.02 and abs(q1 - q0) <= 0.02 and abs(q2 - q0) <= 0.02:
            disp = "PROMPT_INERT"
        elif q1 >= q2 - 0.02 and q1 >= q0 - 0.02:
            disp = "COMPRESSION_EARNED"
        else:
            disp = "RESTORE_NEEDED"
        receipt = {"arms": results, "eps_noninf": 0.02, "disposition": disp,
                   "fixture_hash": "7cb3bca5e7ffa64f", "substrate": "9B",
                   "note": "cognitive result only; scorer deterministic; "
                           "LLM-ADMIT never equals Gamma-ADMIT"}
        (HERE / "ABLATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2))
        print(f"DISPOSITION={disp}")
        print("ABLATION_RECEIPT.json written"); print("DONE_ABLATION")
    finally:
        proc.terminate(); proc.wait(timeout=15); time.sleep(2)

if __name__ == "__main__":
    main()
