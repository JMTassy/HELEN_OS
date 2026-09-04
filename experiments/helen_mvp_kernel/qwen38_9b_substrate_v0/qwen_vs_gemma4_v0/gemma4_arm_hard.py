#!/usr/bin/env python3
"""
QWEN_VS_GEMMA4_V0 — ARM A clean re-run (Gemma4-12b, SOLO seat). Same frozen protocol as the crashed arm:
28 V3 fixtures · KERNEL7 (ARM_1) · V3 template/schema/deterministic scorer · temp0 seed0 max_tokens2500 ·
no tools/web · Gemma4 alone (no concurrent Qwen/HER/HAL/Goblins/Vision). authority=false · ledger_effect=none.
Crash-resilient: per-fixture retry (never replaces a fixture); records parse_status/latency/tokens.
Validity gate: completed_fixtures=28 ∧ crashes=0 ∧ schema_valid=28, else HOLD MATCHED_ARM_INCOMPLETE.
Qwen-9B side REUSES its witnessed kernel7 Q=0.7196 (prereg). No partial score is presented as a matched comparison.
"""
import json, re, sys, pathlib, urllib.request, time, signal
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent
V3 = BASE / "v3"; PA = BASE / "prompt_ablation_v0"
sys.path.insert(0, str(V3))
from scorer import score_item, q_of, fixtures            # FROZEN deterministic scorer

TEMPLATE = (V3 / "template.txt").read_text()
SCHEMA = (V3 / "output_schema.json").read_text().strip()
KERNEL7 = (PA / "ARM_1_KERNEL7.txt").read_text()
ADAPTER = ("\n\nOUTPUT CONTRACT: Respond with EXACTLY one JSON object matching the OUTPUT SCHEMA in the "
           "user message, and nothing after it. Evaluate ONLY the CLAIM against the SOURCES given in the "
           "item; the sources are the entire world for this item. source IDs are the bracketed tokens "
           "(e.g. R1). authority=false.")
OLLAMA = "http://localhost:11434/v1/chat/completions"
MODEL = "gemma4-12b"
RETRIES = 2
HARD = 180   # hard per-request wall deadline (s) — no zombie
BUDGET = 3600  # total run budget (s)
class _TO(Exception): pass
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_TO()))

def user_message(fx):
    return TEMPLATE.split("\n\n", 1)[1].replace("{source}", fx["source"]).replace("{claim}", fx["claim"]).replace("{output_schema}", SCHEMA)

def ask(system, user):
    """Return (raw_text, in_tokens, out_tokens, status). Retries transient failures on the SAME fixture."""
    body = json.dumps({"model": MODEL, "messages": [{"role": "system", "content": system},
                       {"role": "user", "content": user}], "temperature": 0, "seed": 0,
                       "max_tokens": 2500, "stream": False}).encode()
    last = ""
    for attempt in range(RETRIES):
        try:
            signal.alarm(HARD)
            j = json.loads(urllib.request.urlopen(urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"}), timeout=HARD).read())
            signal.alarm(0)
            u = j.get("usage", {})
            return j["choices"][0]["message"]["content"], u.get("prompt_tokens"), u.get("completion_tokens"), "OK"
        except Exception as e:
            signal.alarm(0)
            last = f"{type(e).__name__}:{e}"
            time.sleep(3)
    return f"__ERROR__ {last}", None, None, "ERROR"

def extract(text):
    if "</think>" in text: text = text.split("</think>")[-1]
    for m in re.finditer(r"\{", text):
        depth = 0
        for j in range(m.start(), len(text)):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        c = json.loads(text[m.start():j + 1])
                        if "epistemic_class" in c: return c
                    except Exception: pass
                    break
        else: continue
        break
    return None

def main():
    fxs = fixtures(); t0 = time.time()
    rows = []; scores = []; crashes = 0; schema_valid = 0
    raw_path = HERE / "RUN_A_gemma4_hard.ndjson"; raw_path.write_text("")
    for fx in fxs:
        if time.time() - t0 > BUDGET:
            rows.append({'fixture_id': fx['fixture_id'],'family':fx['family'],'parse_status':'NOT_RUN_BUDGET','schema_valid':False,'latency_s':0,'in_tokens':None,'out_tokens':None,'score':{'valid':0,'c':0,'s':0,'r':0,'b':0,'a':0}}); crashes+=1; continue
        ts = time.time()
        raw, itok, otok, status = ask(KERNEL7.strip() + ADAPTER, user_message(fx))
        lat = round(time.time() - ts, 2)
        cand = extract(raw) if status == "OK" else None
        s = score_item(fx, cand)
        if status != "OK": crashes += 1
        if s["valid"]: schema_valid += 1
        scores.append(s)
        rows.append({"fixture_id": fx["fixture_id"], "family": fx["family"], "parse_status": status,
                     "schema_valid": bool(s["valid"]), "latency_s": lat, "in_tokens": itok, "out_tokens": otok,
                     "score": s})
        raw_path.open("a").write(json.dumps({"fixture_id": fx["fixture_id"], "parse_status": status, "raw": raw}) + "\n")
        print(json.dumps({"fx": fx["fixture_id"], "status": status, "valid": bool(s["valid"]), "lat": lat}))

    completed = len(rows)
    valid_run = (completed == 28 and crashes == 0 and schema_valid == 28)
    q_discrim = round(q_of(scores), 4)
    by_family = {k: round(q_of([r["score"] for r in rows if r["family"] == k]), 3)
                 for k in {r["family"] for r in rows}}
    out = {"arm": "A_gemma4-12b_ollama_SOLO", "n_fixtures": completed,
           "completion_witness": {"completed_fixtures": completed, "crashes": crashes,
                                  "schema_valid": schema_valid, "valid_run": valid_run},
           "Q_discrim": q_discrim if valid_run else None,
           "disposition": "VALID" if valid_run else "HOLD:MATCHED_ARM_INCOMPLETE",
           "by_family": by_family if valid_run else None,
           "qwen9b_kernel7_baseline": 0.7196, "delta_Q_discrim": (round(0.7196 - q_discrim, 4) if valid_run else None),
           "wall_s": round(time.time() - t0, 1), "rows": rows, "authority": False, "canon": False, "ledger_effect": "none"}
    (HERE / "gemma4_scores_hard.json").write_text(json.dumps(out, indent=2))
    print("\n=== COMPLETION WITNESS ===")
    print(json.dumps(out["completion_witness"]))
    print(f"disposition={out['disposition']} · Q_discrim={out['Q_discrim']} · Δ(qwen9B-gemma)={out['delta_Q_discrim']}")
    print("DONE_GEMMA4_CLEAN")

if __name__ == "__main__":
    main()
