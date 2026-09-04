"""HAL_QUALIFICATION_V1 — qualify HAL on DISCRIMINATION, not size. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Control=Qwen9B (llama-server :8088), Treatment=Gemma12B (ollama). 26B EXCLUDED (NOT_QUALIFIED_ON_THIS_SEAT).
Real illicit-claim fixtures from ornith_discriminator_v0 (8 illicit + 2 licensed, each with known invalid-morphism keys).
Measures V (verdict), R (reason), M (invalid-morphism localization — the sharp HELEN quantity), P (parse rate), L (latency),
false-ALLOW / false-REFUTE. Hard gates: parse < thresh OR false-ALLOW > 0 ⇒ NOT_QUALIFIED (not compensated by speed).
Parse failure measured SEPARATELY from discrimination failure. Verdict from unparseable output ⇒ hard fail.
"""
import json, re, time, urllib.request, pathlib, hashlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ornith_discriminator_v0"))
from qh_run import FIX, _has                                   # frozen fixtures + keyword helper

HERE = pathlib.Path(__file__).resolve().parent
QWEN_URL = "http://127.0.0.1:8088/v1/chat/completions"
OLLAMA = "http://127.0.0.1:11434/api/chat"
GEMMA12 = "gemma4-12b:latest"
PARSE_THRESHOLD = 0.8
FALSE_ALLOW_BOUND = 0

HAL_SYS = ('You are HAL, a HELEN discriminator (authority=false). The SOURCES are the entire world for this item. '
           'Try to KILL the candidate conclusion. Rules: Observed(A) and Observed(B) does NOT imply Observed(A->B); '
           'Says(source,P) does NOT imply P. If the conclusion makes an unlicensed inference, VERDICT=REFUTED and name '
           'the exact illicit arrow in INVALID_MORPHISM (e.g. "attribution -> lineage"). Emit ONE strict JSON and nothing '
           'else: {"VERDICT":"SURVIVED|REFUTED|INCONCLUSIVE","REASON_CODE":"","INVALID_MORPHISM":"","EVIDENCE":"","CONFIDENCE":"LOW|MEDIUM|HIGH"}. /no_think')

def user_msg(source, claim): return f"SOURCES: {source}\nCANDIDATE CONCLUSION: {claim}"

def extract(t):
    t = re.sub(r"<think>.*?</think>", " ", t or "", flags=re.S | re.I)
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try:
                        c = json.loads(t[m.start():j+1])
                        if "VERDICT" in c: return c
                    except Exception: pass
                    break
        else: continue
        break
    return None

def call_qwen(source, claim):
    body = json.dumps({"messages": [{"role": "system", "content": HAL_SYS}, {"role": "user", "content": user_msg(source, claim)}],
                       "temperature": 0, "max_tokens": 350, "stream": False,
                       "chat_template_kwargs": {"enable_thinking": False}}).encode()
    t = time.time()
    j = json.loads(urllib.request.urlopen(urllib.request.Request(QWEN_URL, body, {"Content-Type": "application/json"}), timeout=150).read())
    return j["choices"][0]["message"]["content"], round(time.time()-t, 1)

def call_gemma(source, claim):
    body = json.dumps({"model": GEMMA12, "stream": False, "options": {"temperature": 0, "num_predict": 350},
                       "messages": [{"role": "system", "content": HAL_SYS}, {"role": "user", "content": user_msg(source, claim)}]}).encode()
    t = time.time()
    j = json.loads(urllib.request.urlopen(urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"}), timeout=600).read())
    return j.get("message", {}).get("content", ""), round(time.time()-t, 1)

def score(fx, cand, parse_ok):
    source, claim, level, gold_v, mwt, mL, mR, fam = fx
    if not parse_ok or not isinstance(cand, dict):
        return {"V": 0, "R": 0, "M": (0 if level == "illicit" else None), "verdict": "INCONCLUSIVE",
                "false_allow": 0, "false_refute": 0}
    verdict = str(cand.get("VERDICT", "")).upper()
    morph = " ".join(map(str, [cand.get("INVALID_MORPHISM", ""), cand.get("EVIDENCE", ""), cand.get("REASON_CODE", "")]))
    if level == "illicit":
        V = 1 if verdict == "REFUTED" else 0
        R = 1 if _has(morph, [mwt.split()[0]] + mwt.split()) else 0
        M = 1 if (_has(morph, mL) and _has(morph, mR)) else 0
        fa = 1 if verdict == "SURVIVED" else 0            # false-ALLOW: illicit judged survivable
        return {"V": V, "R": R, "M": M, "verdict": verdict, "false_allow": fa, "false_refute": 0}
    else:  # licensed
        V = 1 if verdict == "SURVIVED" else 0
        fr = 1 if verdict == "REFUTED" else 0             # false-REFUTE: licensed judged refuted
        return {"V": V, "R": 1 if cand.get("REASON_CODE") else 0, "M": None, "verdict": verdict,
                "false_allow": 0, "false_refute": fr}

def qualify(name, caller):
    rows = []
    for fx in FIX:
        source, claim = fx[0], fx[1]
        try:
            raw, lat = caller(source, claim); status = "OK"
        except Exception as e:
            raw, lat, status = f"__ERROR__ {e}", 0.0, "ERROR"
        cand = extract(raw); parse_ok = cand is not None
        s = score(fx, cand, parse_ok)
        rows.append({"family": fx[7], "level": fx[2], "parse_ok": parse_ok, "latency": lat, **s})
    n = len(rows); illicit = [r for r in rows if r["level"] == "illicit"]
    def mean(vals): vals = [v for v in vals if v is not None]; return round(sum(vals)/len(vals), 3) if vals else None
    P = round(sum(r["parse_ok"] for r in rows)/n, 3)
    false_allow = sum(r["false_allow"] for r in rows)
    false_refute = sum(r["false_refute"] for r in rows)
    # HARD GATES
    verdict_from_unparseable = any((not r["parse_ok"]) and r["verdict"] not in ("INCONCLUSIVE",) for r in rows)
    eligible = (P >= PARSE_THRESHOLD) and (false_allow <= FALSE_ALLOW_BOUND) and (not verdict_from_unparseable)
    return {"HAL": name, "V": mean([r["V"] for r in rows]), "R": mean([r["R"] for r in rows]),
            "M": mean([r["M"] for r in illicit]), "P": P, "LATENCY_total": round(sum(r["latency"] for r in rows), 1),
            "LATENCY_mean": round(sum(r["latency"] for r in rows)/n, 1), "FALSE_ALLOW": false_allow,
            "FALSE_REFUTE": false_refute, "ELIGIBLE": eligible, "verdict_from_unparseable": verdict_from_unparseable,
            "rows": rows}

def main():
    fixtures_hash = hashlib.sha256(json.dumps(FIX, default=str, sort_keys=True).encode()).hexdigest()[:16]
    prompt_hash = hashlib.sha256(HAL_SYS.encode()).hexdigest()[:16]
    print(f"=== HAL_QUALIFICATION_V1 · fixtures={len(FIX)} (8 illicit + 2 licensed) · fix_hash={fixtures_hash} · prompt_hash={prompt_hash} ===")
    q = qualify("QWEN9B", call_qwen)
    print(f"  QWEN9B done (P={q['P']} lat_total={q['LATENCY_total']}s)")
    g = qualify("GEMMA12B", call_gemma)
    print(f"  GEMMA12B done (P={g['P']} lat_total={g['LATENCY_total']}s)")

    def line(x): return (f"    V={x['V']} R={x['R']} M={x['M']} P={x['P']} lat_mean={x['LATENCY_mean']}s "
                         f"false_ALLOW={x['FALSE_ALLOW']} false_REFUTE={x['FALSE_REFUTE']} ELIGIBLE={x['ELIGIBLE']}")
    # winner: only among eligible; M is the primary discrimination quantity, then V, then latency
    elig = [x for x in (q, g) if x["ELIGIBLE"]]
    if not elig:
        winner, wreason = "NONE_ELIGIBLE", "no HAL passed hard qualification gates"
    else:
        winner = max(elig, key=lambda x: ((x["M"] or 0), x["V"], -x["LATENCY_mean"]))["HAL"]
        wreason = "highest M (invalid-morphism localization) among eligible, then V, then latency"
    receipt = {"receipt": "HAL_QUALIFICATION_V1", "FIXTURES_TOTAL": len(FIX), "FIXTURES_VALID": len(FIX),
               "fixtures_hash": fixtures_hash, "prompt_hash": prompt_hash,
               "QWEN": {k: q[k] for k in ("V", "R", "M", "P", "LATENCY_mean", "FALSE_ALLOW", "FALSE_REFUTE", "ELIGIBLE")},
               "GEMMA12B": {k: g[k] for k in ("V", "R", "M", "P", "LATENCY_mean", "FALSE_ALLOW", "FALSE_REFUTE", "ELIGIBLE")},
               "FABLE_PREMIUM_CALLS": 0, "QUALITY_WINNER": winner, "WINNER_REASON": wreason,
               "GEMMA26B_PRIOR_RESULT": "PRESERVED_NOT_QUALIFIED_ON_THIS_SEAT",
               "note": "M is the primary quantity. NOT_QUALIFIED is outside ranking, not score 0. ParseFailure != REFUTED. LargerModel != BetterHAL.",
               "authority": False, "canon": False, "ledger_effect": "none"}
    (HERE / "her_run" / "hal_qualification_v1_receipt.json").write_text(json.dumps({**receipt, "qwen_rows": q["rows"], "gemma_rows": g["rows"]}, indent=2))
    print("\n=== HAL_QUALIFICATION_V1 RECEIPT ===")
    print(f"  QWEN9B:  {line(q)}"); print(f"  GEMMA12B:{line(g)}")
    print(f"  FABLE_PREMIUM_CALLS=0 · QUALITY_WINNER={winner} · reason={wreason}")
    print(f"  GEMMA26B_PRIOR = PRESERVED_NOT_QUALIFIED_ON_THIS_SEAT · authority=false")

if __name__ == "__main__":
    main()
