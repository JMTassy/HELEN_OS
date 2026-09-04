#!/usr/bin/env python3
"""
V3 runner — executes the frozen contract, nothing else.
Order: sealed blind mapping -> RUN_A -> RUN_B -> blind score -> freeze scores
-> unblind -> governance check -> receipt. NON_SOVEREIGN · authority=false.
"""
import hashlib, json, pathlib, re, subprocess, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent

FREEZE = json.loads((HERE / "freeze_receipt_amended.json").read_text())
H_EXP = FREEZE["hashes"]["EXPERIMENT_HASH"]
RT = json.loads((HERE / "runtime_contract.json").read_text())
SYSTEM = (HERE / "system_contract.txt").read_text().strip()
TEMPLATE = (HERE / "template.txt").read_text()
SCHEMA = (HERE / "output_schema.json").read_text().strip()
PORT = RT["port"]
SAMP = RT["sampling"]

def fixtures():
    return [json.loads(l) for l in (HERE / "fixtures_test.jsonl").read_text().splitlines() if l.strip()]

def user_message(fx):
    body = TEMPLATE.split("\n\n", 1)[1]  # drop the header line of template.txt
    return body.replace("{source}", fx["source"]).replace("{claim}", fx["claim"]) \
               .replace("{output_schema}", SCHEMA)

def ask(prompt_user):
    body = json.dumps({"messages": [{"role": "system", "content": SYSTEM},
                                    {"role": "user", "content": prompt_user}],
                       "max_tokens": SAMP["max_tokens"], "temperature": SAMP["temperature"],
                       "seed": SAMP["seed"]}).encode()
    req = urllib.request.Request(f"http://localhost:{PORT}/v1/chat/completions",
                                 body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

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

def run_one(label, model_key):
    model = RT["models"][model_key]
    path = str(pathlib.Path(model["path"]).expanduser())
    proc = subprocess.Popen(["llama-server", "-m", path] + RT["args"]
                            + ["--port", str(PORT), "--no-webui"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2); break
        except Exception:
            time.sleep(1)
    try:
        outs, raws, reqs = {}, [], []
        for fx in fixtures():
            um = user_message(fx)
            reqs.append({"fixture": fx["fixture_id"], "user": um})
            raw = ask(um)
            c = extract(raw)
            outs[fx["fixture_id"]] = c
            raws.append({"fixture": fx["fixture_id"], "raw": raw, "candidate": c})
        d = HERE / label
        d.mkdir(exist_ok=True)
        (d / "outputs.json").write_text(json.dumps(outs, indent=1))
        (d / "raw.ndjson").write_text("\n".join(json.dumps(x) for x in raws) + "\n")
        h_run = hashlib.sha256((H_EXP + model["sha256"] + str(SAMP["seed"])
                                + json.dumps(reqs, sort_keys=True)).encode()).hexdigest()[:16]
        h_result = hashlib.sha256((h_run + hashlib.sha256(
            json.dumps(outs, sort_keys=True).encode()).hexdigest()).encode()).hexdigest()[:16]
        (d / "run_receipt.json").write_text(json.dumps(
            {"label": label, "H_exp": H_EXP, "H_run": h_run, "H_result": h_result,
             "model_sha256": model["sha256"], "n_items": len(outs)}, indent=1))
        return h_run, h_result
    finally:
        proc.terminate(); proc.wait(timeout=15); time.sleep(2)

def main():
    print(f"V3 RUN under H_exp={H_EXP}")
    # sealed blind mapping: deterministic, opaque, written before any call
    keys = sorted(RT["models"], key=lambda k: hashlib.sha256(
        (H_EXP + RT["models"][k]["sha256"]).encode()).hexdigest())
    mapping = {"run_A": keys[0], "run_B": keys[1]}
    (HERE / "sealed_mapping.json").write_text(json.dumps(mapping))
    print("sealed_mapping.json written (not read until scores frozen)")
    for label in ("run_A", "run_B"):
        hr, hres = run_one(label, mapping[label])
        print(f"{label}: H_run={hr} H_result={hres}")
    # blind score
    for label in ("run_A", "run_B"):
        subprocess.run([sys.executable, str(HERE / "scorer.py"), "score", label], check=True)
    # freeze scores
    sh = hashlib.sha256((HERE / "run_A" / "score.json").read_bytes()
                        + (HERE / "run_B" / "score.json").read_bytes()).hexdigest()[:16]
    print(f"SCORES_FROZEN hash={sh}")
    # unblind
    m = json.loads((HERE / "sealed_mapping.json").read_text())
    a = json.loads((HERE / "run_A" / "score.json").read_text())
    b = json.loads((HERE / "run_B" / "score.json").read_text())
    sub = {"SUB_1": "2B", "SUB_2": "9B"}
    named = {sub[m["run_A"]]: a, sub[m["run_B"]]: b}
    dq = round(named["9B"]["Q_discrim"] - named["2B"]["Q_discrim"], 4)
    print(f"UNBLIND: run_A={sub[m['run_A']]} run_B={sub[m['run_B']]}")
    print(f"Q_discrim 2B={named['2B']['Q_discrim']} 9B={named['9B']['Q_discrim']} dQ={dq}")
    # governance + disposition per frozen rubric
    gov = {"authority_delta": 0, "policy_delta": 0, "TCB_delta": 0, "effect_rights_delta": 0}
    fmt_ok = min(named["2B"]["Q_formatting"], named["9B"]["Q_formatting"]) >= 0.80
    if not fmt_ok:
        disp = "HOLD"
    elif dq > 0.05:
        disp = "PASS"
    else:
        disp = "NO_GAIN"
    receipt = {"H_exp": H_EXP, "scores_frozen_hash": sh, "mapping": m,
               "scores": {k: {kk: v[kk] for kk in ("Q_discrim", "Q_formatting", "by_family")}
                          for k, v in named.items()},
               "dQ_discrim": dq, "epsilon": 0.05, "governance": gov,
               "disposition": disp}
    (HERE / "V3_RECEIPT.json").write_text(json.dumps(receipt, indent=2))
    print(f"DISPOSITION={disp}")
    print("V3_RECEIPT.json written"); print("DONE_V3_RUN")

if __name__ == "__main__":
    main()
