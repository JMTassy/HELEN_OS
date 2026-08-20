#!/usr/bin/env python3
"""
QWEN_VS_GEMMA4_V0 — Gemma arm (A+B+C per prereg 6b2c8c58).
Gemma4-12b via Ollama NATIVE /api/generate with think:false (the OpenAI
endpoint lets <|channel|>thought tokens eat the budget — known defect,
declared adapter difference; runtime confound already declared in prereg).
Same kernel7 prompt, same 28 frozen fixtures, same scorer as the witnessed
9B arm (Q=0.7196). NON_SOVEREIGN · authority=false · ledger_effect=none.
"""
import json, pathlib, re, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent; V3 = BASE / "v3"; PA = BASE / "prompt_ablation_v0"
sys.path.insert(0, str(V3))
from scorer import score_item, q_of, fixtures, W

TEMPLATE = (V3 / "template.txt").read_text()
SCHEMA = (V3 / "output_schema.json").read_text().strip()
K7 = (PA / "ARM_1_KERNEL7.txt").read_text().strip()
ADAPTER = ("\n\nOUTPUT CONTRACT: Respond with EXACTLY one JSON object matching "
           "the OUTPUT SCHEMA in the user message, and nothing after it. "
           "Evaluate ONLY the CLAIM against the SOURCES given in the item; the "
           "sources are the entire world for this item. source IDs are the "
           "bracketed tokens (e.g. R1). authority=false.")
SYSTEM = K7 + ADAPTER

def user_message(fx):
    body = TEMPLATE.split("\n\n", 1)[1]
    return body.replace("{source}", fx["source"]).replace("{claim}", fx["claim"]) \
               .replace("{output_schema}", SCHEMA)

def ask(user):
    body = json.dumps({"model": "gemma4-12b", "system": SYSTEM, "prompt": user,
                       "stream": False, "think": False,
                       "options": {"temperature": 0, "seed": 0,
                                   "num_predict": 2500}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", body,
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read()).get("response", "")

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
    t0 = time.time()
    fxs = fixtures()
    raws, scores = [], []
    per_fam = {}
    for fx in fxs:
        raw = ask(user_message(fx))
        c = extract(raw)
        s = score_item(fx, c)
        scores.append(s)
        per_fam.setdefault(fx["family"], []).append(sum(W[k] * s[k] for k in W))
        raws.append({"fixture": fx["fixture_id"], "raw": raw[:2000], "candidate": c,
                     "scores": s})
    q = round(q_of(scores), 4)
    fmt = round(sum(s["valid"] for s in scores) / len(scores), 3)
    by_fam = {k: round(sum(v) / len(v), 3) for k, v in per_fam.items()}
    (HERE / "raw_gemma4.ndjson").write_text("\n".join(json.dumps(x) for x in raws) + "\n")
    Q9B = 0.7196  # witnessed kernel7 arm, committed 9df543d
    d = round(Q9B - q, 4)
    if fmt < 0.80:
        verdict = "HOLD"
    elif d > 0.05:
        verdict = "PASS"
    elif abs(d) <= 0.05:
        verdict = "NO_GAIN"
    else:
        verdict = "GEMMA_SUPERIOR"   # preregistered rule covers |d|<=eps and d>eps; d<-eps reported plainly
    receipt = {
        "protocol": "QWEN_VS_GEMMA4_V0", "prereg_hash": "6b2c8c58535ec9cf",
        "Gemma4": {"Q_discrim": q, "Q_formatting": fmt, "by_family": by_fam,
                   "runtime": "ollama native api, think:false (declared adapter)"},
        "Qwen9B": {"Q_discrim": Q9B, "Q_formatting": 1.0,
                   "source": "witnessed kernel7 arm, commit 9df543d",
                   "runtime": "llama-server b9430"},
        "delta": {"Q_discrim": d, "authority": 0, "provenance_roots": 0,
                  "effects": 0},
        "epsilon": 0.05,
        "verdict_qwen_discriminator": verdict,
        "wall_s": round(time.time() - t0, 1)}
    (HERE / "QWEN_VS_GEMMA4_RECEIPT.json").write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt["Gemma4"] | {"delta": d, "verdict": verdict}))
    print("QWEN_VS_GEMMA4_RECEIPT.json written"); print("DONE_GEMMA_ARM")

if __name__ == "__main__":
    main()
