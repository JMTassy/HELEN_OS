"""HAL_REQUALIFICATION_M_V2 — requalify Qwen9B vs Gemma12B under the REPAIRED metric. authority=false · canon=false
· ledger_effect=none. NON-SOVEREIGN. Deterministic RE-CAPTURE under the current seat (temp 0, same model/prompt/
fixtures/parser, hashed) — NOT a claim these are the historical bytes (runtime/backend may differ). Raw outputs are
persisted BEFORE scoring. M scored with M_V2 (INVALID_MORPHISM field only). FABLE_premium=0.
"""
import json, hashlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ornith_discriminator_v0"))
from qh_run import FIX, _has
from hal_qualification_v1 import call_qwen, call_gemma, HAL_SYS, extract, PARSE_THRESHOLD
from metric_repair_m_v2 import m_v2

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "her_run"

def recapture(caller):
    """Call the model on every fixture; persist verbatim BEFORE any scoring."""
    packet = []
    for fx in FIX:
        try:
            raw, lat = caller(fx[0], fx[1]); status = "OK"
        except Exception as e:
            raw, lat, status = f"__ERROR__ {e}", 0.0, "ERROR"
        packet.append({"family": fx[7], "level": fx[2], "raw": raw, "latency": lat, "status": status})
    return packet

def score_packet(packet):
    rows = []
    for fx, rec in zip(FIX, packet):
        cand = extract(rec["raw"]); parse_ok = cand is not None
        verdict = str((cand or {}).get("VERDICT", "")).upper() if parse_ok else "INCONCLUSIVE"
        if verdict not in ("SURVIVED", "REFUTED", "INCONCLUSIVE"): verdict = "INCONCLUSIVE"
        level, mwt = fx[2], fx[4]
        if level == "illicit":
            V = 1 if verdict == "REFUTED" else 0
            R = 1 if (parse_ok and _has(str((cand or {}).get("REASON_CODE", "")), [mwt.split()[0]] + mwt.split())) else 0
            M = m_v2(fx, cand) if parse_ok else 0
            fa = 1 if verdict == "SURVIVED" else 0
            fr = 0
        else:
            V = 1 if verdict == "SURVIVED" else 0
            R = 1 if (parse_ok and (cand or {}).get("REASON_CODE")) else 0
            M = None
            fa = 0; fr = 1 if verdict == "REFUTED" else 0
        rows.append({"family": fx[7], "level": level, "parse_ok": parse_ok, "verdict": verdict,
                     "V": V, "R": R, "M_V2": M, "false_allow": fa, "false_refute": fr, "latency": rec["latency"]})
    return rows

def summarize(name, packet, rows):
    n = len(rows); illicit = [r for r in rows if r["level"] == "illicit"]
    def mean(v): v = [x for x in v if x is not None]; return round(sum(v)/len(v), 3) if v else None
    P = round(sum(r["parse_ok"] for r in rows)/n, 3)
    fa = sum(r["false_allow"] for r in rows); fr = sum(r["false_refute"] for r in rows)
    inconclusive = sum(1 for r in rows if r["verdict"] == "INCONCLUSIVE")
    parse_fail = sum(1 for r in rows if not r["parse_ok"])
    verdict_from_unparseable = any((not r["parse_ok"]) and r["verdict"] != "INCONCLUSIVE" for r in rows)
    eligible = (fa == 0) and (P >= PARSE_THRESHOLD) and (not verdict_from_unparseable)
    return {"OUTPUT_PACKET_HASH": hashlib.sha256(json.dumps(packet, sort_keys=True, default=str).encode()).hexdigest()[:16],
            "V": mean([r["V"] for r in rows]), "R": mean([r["R"] for r in rows]),
            "M_V2": mean([r["M_V2"] for r in illicit]), "P": P,
            "LATENCY_mean": round(sum(r["latency"] for r in rows)/n, 1),
            "FALSE_ALLOW": fa, "FALSE_REFUTE": fr, "INCONCLUSIVE": inconclusive, "PARSE_FAILURES": parse_fail,
            "ELIGIBLE": eligible}

def main():
    fixture_hash = hashlib.sha256(json.dumps(FIX, default=str, sort_keys=True).encode()).hexdigest()[:16]
    prompt_hash = hashlib.sha256(HAL_SYS.encode()).hexdigest()[:16]
    print(f"=== HAL_REQUALIFICATION_M_V2 · fix_hash={fixture_hash} · prompt_hash={prompt_hash} · METRIC=M_V2 ===")
    qp = recapture(call_qwen); print(f"  Qwen re-captured ({len(qp)})")
    gp = recapture(call_gemma); print(f"  Gemma re-captured ({len(gp)})")
    # persist RAW before scoring
    (OUT / "requalify_raw.json").write_text(json.dumps({"qwen": qp, "gemma": gp}, indent=2, default=str))
    qr, gr = score_packet(qp), score_packet(gp)
    Q, G = summarize("QWEN9B", qp, qr), summarize("GEMMA12B", gp, gr)
    elig = [(n, s) for n, s in (("QWEN9B", Q), ("GEMMA12B", G)) if s["ELIGIBLE"]]
    if not elig: selection = "NONE_ELIGIBLE"
    elif len(elig) == 2: selection = "BOTH_ELIGIBLE"
    else: selection = elig[0][0]
    receipt = {"receipt": "HAL_REQUALIFICATION_M_V2", "FIXTURE_HASH": fixture_hash, "PROMPT_HASH": prompt_hash,
               "METRIC_VERSION": "M_V2", "recapture_note": "temp0 re-capture under current seat; NOT historical bytes",
               "QWEN9B": Q, "GEMMA12B": G, "CONTAMINATED": False, "FABLE_PREMIUM_CALLS": 0,
               "HAL_SELECTION": selection, "QUALITY_GLOBAL": "NOT_CLAIMED",
               "authority": False, "canon": False, "ledger_effect": "none"}
    (OUT / "hal_requalification_m_v2_receipt.json").write_text(json.dumps({**receipt, "qwen_rows": qr, "gemma_rows": gr}, indent=2, default=str))
    def line(s): return (f"V={s['V']} R={s['R']} M_V2={s['M_V2']} P={s['P']} lat={s['LATENCY_mean']}s "
                         f"FA={s['FALSE_ALLOW']} FR={s['FALSE_REFUTE']} INCONCL={s['INCONCLUSIVE']} ELIGIBLE={s['ELIGIBLE']}")
    print("\n=== HAL_REQUALIFICATION_M_V2 RECEIPT ===")
    print(f"  QWEN9B[{Q['OUTPUT_PACKET_HASH']}]:  {line(Q)}")
    print(f"  GEMMA12B[{G['OUTPUT_PACKET_HASH']}]: {line(G)}")
    print(f"  HAL_SELECTION={selection} · CONTAMINATED=False · FABLE_PREMIUM=0 · QUALITY_GLOBAL=NOT_CLAIMED")
    print("  authority=false · canon=false · ledger_effect=none (HAL NOT frozen; AUTORESEARCH NOT launched)")

if __name__ == "__main__":
    main()
