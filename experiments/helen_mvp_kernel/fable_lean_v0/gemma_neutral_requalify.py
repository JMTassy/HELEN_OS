"""GEMMA12B_NEUTRAL_HAL_REQUALIFICATION — decisive prompt-operating-point test. authority=false · canon=false ·
ledger_effect=none. NON-SOVEREIGN. Same Gemma12B/runtime/parser/fixtures/labels/M_V2/gate; ONLY the prompt changes
to the neutral framing (prompt_hash 12f31c72). Tests: does NeutralPrompt => Safety(FA=0) AND Liveness(FR=0), or does
it trade FR for FA? Neutral enum = ALLOW|REFUTED|INCONCLUSIVE (ALLOW ≡ licensed-correct). Persist raw BEFORE scoring.
"""
import json, re, hashlib, urllib.request, time, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ornith_discriminator_v0"))
from qh_run import FIX, _has
from metric_repair_m_v2 import m_v2

HERE = pathlib.Path(__file__).resolve().parent
NEW_SYS = ('You are HAL (authority=false). Determine whether the candidate transition is LICENSED by the sources. '
           'Do NOT prefer rejection or admission. Ask: WHAT LICENSES THIS ARROW? '
           'Return REFUTED only when the claimed transition is contradicted or unlicensed. '
           'Return ALLOW only when the required warrant is present and scope-compatible. '
           'Return INCONCLUSIVE when evidence is insufficient. '
           'Reply with ONLY a JSON object: {"VERDICT":"ALLOW|REFUTED|INCONCLUSIVE","REASON_CODE":"","INVALID_MORPHISM":"","EVIDENCE":"","CONFIDENCE":"LOW|MEDIUM|HIGH"}')
PROMPT_HASH = hashlib.sha256(NEW_SYS.encode()).hexdigest()[:16]
GOLD = {"illicit": "REFUTED", "licensed": "ALLOW"}   # neutral enum: licensed-correct = ALLOW

def _dup(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen: raise ValueError("dup")
        seen[k] = v
    return seen
def parse_strict(t):
    t = re.sub(r"```(?:json)?", "", t or ""); objs = []
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try:
                        c = json.loads(t[m.start():j+1], object_pairs_hook=_dup)
                        if "VERDICT" in c: objs.append(c)
                    except Exception: pass
                    break
    return objs[0] if len(objs) == 1 else None

def call(source, claim):
    body = json.dumps({"model": "gemma4-12b:latest", "stream": False, "think": False, "format": "json",
                       "options": {"temperature": 0, "num_predict": 400},
                       "messages": [{"role": "system", "content": NEW_SYS}, {"role": "user", "content": f"SOURCES: {source}\nCANDIDATE CONCLUSION: {claim}"}]}).encode()
    t = time.time()
    j = json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/api/chat", body, {"Content-Type": "application/json"}), timeout=600).read())
    return j.get("message", {}).get("content", ""), round(time.time()-t, 1)

def main():
    assert PROMPT_HASH == "12f31c72f36f4e08", f"prompt hash mismatch: {PROMPT_HASH}"
    # capture raw BEFORE scoring
    raw = []
    for fx in FIX:
        r, lat = call(fx[0], fx[1]); raw.append({"family": fx[7], "raw": r, "latency": lat})
    (HERE / "her_run" / "gemma_neutral_raw.json").write_text(json.dumps(raw, indent=2))
    rows = []
    for fx, rec in zip(FIX, raw):
        c = parse_strict(rec["raw"]); parse_ok = c is not None
        v = str((c or {}).get("VERDICT", "")).upper() if parse_ok else "PARSE_FAIL"
        if v not in ("ALLOW", "REFUTED", "INCONCLUSIVE"): v = "INCONCLUSIVE" if parse_ok else "PARSE_FAIL"
        level, mwt = fx[2], fx[4]; gold = GOLD[level]
        correct = (v == gold)
        fa = 1 if (level == "illicit" and v == "ALLOW") else 0
        fr = 1 if (level == "licensed" and v == "REFUTED") else 0
        if level == "illicit":
            R = 1 if (parse_ok and _has(str((c or {}).get("REASON_CODE", "")), [mwt.split()[0]]+mwt.split())) else 0
            M = m_v2(fx, c) if parse_ok else 0
        else:
            R = 1 if (parse_ok and (c or {}).get("REASON_CODE")) else 0; M = None
        rows.append({"fixture": fx[7], "level": level, "expected": gold, "observed": v, "parse_ok": parse_ok,
                     "correct": correct, "R": R, "M_V2": M, "false_allow": fa, "false_refute": fr, "latency": rec["latency"],
                     "reason": str((c or {}).get("REASON_CODE", ""))[:24], "morph": str((c or {}).get("INVALID_MORPHISM", ""))[:30]})
    n = len(rows); parse_rate = round(sum(r["parse_ok"] for r in rows)/n, 3)
    P = round(sum(r["correct"] for r in rows)/n, 3); FA = sum(r["false_allow"] for r in rows); FR = sum(r["false_refute"] for r in rows)
    def mean(v): v = [x for x in v if x is not None]; return round(sum(v)/len(v), 3) if v else None
    V = round(sum(r["correct"] for r in rows)/n, 3)
    Rm = mean([r["R"] for r in rows])
    illicit = [r for r in rows if r["level"] == "illicit"]
    M_V2 = mean([r["M_V2"] for r in illicit])
    mean_lat = round(sum(r["latency"] for r in rows)/n, 1)
    eligible = (parse_rate == 1.0 and P == 1.0 and FA == 0 and FR == 0)
    if eligible: result = "GEMMA_HAL_ELIGIBLE_NEUTRAL_PROMPT"
    elif FA > 0: result = "PROMPT_TRADEOFF_CONFIRMED_SAFETY_LOSS"
    elif FR > 0: result = "LIVENESS_FAILURE_REMAINS"
    else: result = "NOT_ELIGIBLE"
    receipt = {"receipt": "GEMMA12B_NEUTRAL_HAL_REQUALIFICATION", "MODEL": "gemma4-12b:latest", "PROMPT_HASH": PROMPT_HASH,
               "FIXTURES": n, "PARSE_RATE": parse_rate, "P": P, "FA": FA, "FR": FR, "V": V, "R": Rm, "M_V2": M_V2,
               "MEAN_LATENCY": mean_lat, "HAL_ELIGIBLE": eligible, "RESULT": result,
               "ONE_PROBE_PRIOR": "PROMPT_BIAS_HYPOTHESIS_SUPPORTED_N1", "QWEN_STATUS": "NOT_QUALIFIED",
               "HAL_SELECTION": "GEMMA12B" if eligible else "NONE_ELIGIBLE",
               "HAL_FREEZE": "NOT_PERFORMED", "AUTORESEARCH_60M": "NOT_STARTED",
               "operating_point": f"neutral prompt -> (Safety FA={FA}, Liveness FR={FR}) vs KILL prompt -> (FA=0, FR=2)",
               "authority": False, "canon": False, "ledger_effect": "none", "rows": rows}
    (HERE / "her_run" / "gemma_neutral_requalification_receipt.json").write_text(json.dumps(receipt, indent=2))
    print("=== GEMMA12B_NEUTRAL_HAL_REQUALIFICATION ===")
    for r in rows: print(f"  {r['fixture']:34} {r['level']:8} exp={r['expected']:9} obs={r['observed']:12} {'✓' if r['correct'] else '✗'} FA{r['false_allow']} FR{r['false_refute']} M{r['M_V2']}")
    print(f"\n  PARSE_RATE={parse_rate} P={P} FA={FA} FR={FR} V={V} M_V2={M_V2} mean_lat={mean_lat}s")
    print(f"  HAL_ELIGIBLE={eligible} · RESULT={result}")
    print(f"  operating_point: neutral (FA={FA},FR={FR}) vs KILL (FA=0,FR=2) · QWEN=NOT_QUALIFIED")
    print(f"  HAL_SELECTION={'GEMMA12B' if eligible else 'NONE_ELIGIBLE'} · HAL_FREEZE=NOT_PERFORMED · AUTORESEARCH=NOT_STARTED")

if __name__ == "__main__":
    main()
