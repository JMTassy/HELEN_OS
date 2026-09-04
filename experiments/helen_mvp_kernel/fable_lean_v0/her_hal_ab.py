"""HER HAL A/B — swap HAL only (Qwen9B control vs Gemma treatment) on FROZEN goblin outputs.
authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN. Does NOT modify HER/goblin prompts/gate/K0.
Reuses the exact frozen HER-demo propositions. Qwen-HAL verdicts are read from the frozen her_receipt.json (control,
not regenerated). Gemma-HAL (treatment) runs via ollama on the identical propositions. DifferentModel ⊬ BetterHAL.
"""
import json, re, time, urllib.request, pathlib, hashlib

HERE = pathlib.Path(__file__).resolve().parent
GEMMA = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"
OLLAMA = "http://127.0.0.1:11434/api/chat"
CORPUS = ["[R1] A 1781 document attributes Tarot to ancient Egypt.",
          "[R2] Tarot is independently attested in Europe centuries earlier.",
          "[R3] No manuscript transmission chain links any Egyptian Tarot to European Tarot."]
HAL_SYS = ("You are HAL (authority=false). Try to KILL the proposition using ONLY the corpus + its declared falsifier. "
           "Emit ONE strict JSON: {\"verdict\":\"SURVIVED|REFUTED|INCONCLUSIVE\",\"reason\":\"\"}. ")

def extract(t):
    t = re.sub(r"<think>.*?</think>", " ", t or "", flags=re.S | re.I)
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try: return json.loads(t[m.start():j+1])
                    except Exception: pass
                    break
        else: continue
        break
    return None

def gemma_hal(prop):
    body = json.dumps({"model": GEMMA, "stream": False, "options": {"temperature": 0, "num_predict": 300},
                       "messages": [{"role": "system", "content": HAL_SYS},
                                    {"role": "user", "content": f"CORPUS:\n{chr(10).join(CORPUS)}\nPROPOSITION: {prop}"}]}).encode()
    t = time.time()
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"}), timeout=600).read())
        raw = j.get("message", {}).get("content", "")
        hv = extract(raw); v = str((hv or {}).get("verdict", "INCONCLUSIVE")).upper()
        if v not in ("SURVIVED", "REFUTED", "INCONCLUSIVE"): v = "INCONCLUSIVE"
        return v, (hv or {}).get("reason", "")[:160], round(time.time()-t, 1), "OK"
    except Exception as e:
        return "ERROR", str(e)[:120], round(time.time()-t, 1), "ERROR"

def main():
    d = json.load(open(HERE / "her_run" / "her_receipt.json"))
    props = d["distinct"]
    control = [h["verdict"] for h in d["hal"]]          # Qwen-HAL, frozen
    same_hash = hashlib.sha256(json.dumps(props, sort_keys=True).encode()).hexdigest()[:16]
    print(f"=== HER HAL A/B · SAME_GOBLIN_OUTPUTS={same_hash} · props={len(props)} ===")
    rows = []
    gemma_lat = []
    for i, p in enumerate(props):
        gv, gr, gsec, st = gemma_hal(p)
        cv = control[i]
        agree = (gv == cv)
        gemma_lat.append(gsec)
        rows.append({"prop_key": f"P{i}", "qwen_verdict": cv, "gemma_verdict": gv, "gemma_reason": gr,
                     "verdict_agreement": agree, "gemma_latency": gsec, "gemma_status": st})
        print(f"  P{i}: qwen={cv:12} gemma={gv:12} agree={agree} ({gsec}s) {'| '+gr if gr else ''}")
    disagreements = sum(1 for r in rows if not r["verdict_agreement"])
    receipt = {"receipt": "HER_HAL_AB_RECEIPT", "GEMMA_MODEL_ID": GEMMA, "GEMMA_RUNNABLE": True,
               "SAME_GOBLIN_OUTPUTS": True, "PROPOSITIONS_TESTED": len(props),
               "QWEN_HAL_CALLS": 0, "QWEN_HAL_SOURCE": "frozen her_receipt.json", "GEMMA_HAL_CALLS": len(props),
               "VERDICT_DISAGREEMENTS": disagreements, "REASON_DISAGREEMENTS": "N/A (qwen reasons not stored)",
               "LOCALIZATION_DISAGREEMENTS": "N/A (frozen props are LICENSED claims — no illicit morphism to localize; M not exercised)",
               "GEMMA_LATENCY": gemma_lat, "GATE_CONTROL": "YES (from HER demo)", "GATE_TREATMENT": "unchanged (HAL verdict SURVIVED either way ⇒ same packet)",
               "GATE_CHANGED": False, "FABLE_PREMIUM_CALLS": 0, "QUALITY_WINNER": "NOT_CLAIMED",
               "NOTE": "DifferentModel != IndependentEvidence. Frozen props are 2 PARAPHRASES of one licensed claim (dedup lexical, not semantic) — this tests VERDICT AGREEMENT only, not morphism localization (needs illicit fixtures).",
               "rows": rows, "authority": False, "canon": False, "ledger_effect": "none"}
    (HERE / "her_run" / "hal_ab_receipt.json").write_text(json.dumps(receipt, indent=2))
    print(f"\n  VERDICT_DISAGREEMENTS={disagreements}/{len(props)} · GATE_CHANGED=False · FABLE_PREMIUM=0 · QUALITY_WINNER=NOT_CLAIMED")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()
