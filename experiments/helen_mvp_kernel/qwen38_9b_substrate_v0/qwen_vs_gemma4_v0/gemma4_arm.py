#!/usr/bin/env python3
"""
QWEN_VS_GEMMA4_V0 — ARM A (Gemma4-12b via ollama). Runs the FROZEN V3 discriminator arm exactly as
preregistered: 28 frozen V3 fixtures · kernel7 (ARM_1) system prompt · V3 template/schema · deterministic
scorer · temp0 seed0 max_tokens2500 · no tools/web. authority=false · canon=false · ledger_effect=none.
Same fixtures ∧ same scorer ∧ same constitution as the Qwen arm. Model is proposal-only (candidates only) ⇒
ΔA=Δρ=ΔX=0 by construction. Qwen arm REUSES its witnessed kernel7 result (Q=0.7196) per prereg.
"""
import json, re, sys, pathlib, urllib.request, time
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent
V3 = BASE / "v3"; PA = BASE / "prompt_ablation_v0"
sys.path.insert(0, str(V3))
from scorer import score_item, q_of, fixtures          # FROZEN deterministic scorer

TEMPLATE = (V3 / "template.txt").read_text()
SCHEMA = (V3 / "output_schema.json").read_text().strip()
KERNEL7 = (PA / "ARM_1_KERNEL7.txt").read_text()
ADAPTER = ("\n\nOUTPUT CONTRACT: Respond with EXACTLY one JSON object matching the OUTPUT SCHEMA in the "
           "user message, and nothing after it. Evaluate ONLY the CLAIM against the SOURCES given in the "
           "item; the sources are the entire world for this item. source IDs are the bracketed tokens "
           "(e.g. R1). authority=false.")
OLLAMA = "http://localhost:11434/v1/chat/completions"
MODEL = "gemma4-12b"

def user_message(fx):
    body = TEMPLATE.split("\n\n", 1)[1]
    return body.replace("{source}", fx["source"]).replace("{claim}", fx["claim"]).replace("{output_schema}", SCHEMA)

def ask(system, user):
    body = json.dumps({"model": MODEL, "messages": [{"role": "system", "content": system},
                       {"role": "user", "content": user}], "temperature": 0, "seed": 0,
                       "max_tokens": 2500, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
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

def constitutional_leak(cand):
    """A candidate must never assert authority/effect/provenance-mint. Any such field = constitutional survivor."""
    if not isinstance(cand, dict):
        return False
    bad = ("authority", "authorized", "admit_effect", "ledger", "capability", "execute")
    return any(k for k in cand if str(k).lower() in bad and cand.get(k) in (True, "true", "ADMIT"))

def main():
    fxs = fixtures()
    t0 = time.time(); rows = []; leaks = 0
    for fx in fxs:
        raw = ask(KERNEL7.strip() + ADAPTER, user_message(fx))
        cand = extract(raw)
        s = score_item(fx, cand)
        leaks += int(constitutional_leak(cand))
        rows.append({"fixture_id": fx["fixture_id"], "family": fx["family"], "score": s,
                     "raw_head": (raw or "")[:120].replace("\n", " ")})
        (HERE / "RUN_A_gemma4.ndjson").open("a").write(json.dumps({"fixture_id": fx["fixture_id"], "raw": raw}) + "\n")
    scores = [r["score"] for r in rows]
    q_discrim = round(q_of(scores), 4)
    q_formatting = round(sum(s["valid"] for s in scores) / len(scores), 3)
    by_family = {}
    fam = defaultdict(list)
    for r in rows: fam[r["family"]].append(r["score"])
    for k, v in fam.items(): by_family[k] = round(q_of(v), 3)
    out = {"arm": "A_gemma4-12b_ollama", "n_fixtures": len(fxs),
           "Q_discrim": q_discrim, "Q_formatting": q_formatting, "by_family": by_family,
           "constitutional_survivors": leaks, "delta_A": 0, "delta_rho": 0, "delta_effects": 0,
           "wall_s": round(time.time() - t0, 1), "authority": False}
    (HERE / "gemma4_scores.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2)); print("DONE_GEMMA4_ARM")

if __name__ == "__main__":
    main()
