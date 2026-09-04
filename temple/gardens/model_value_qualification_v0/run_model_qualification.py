#!/usr/bin/env python3
"""
LOCAL_MODEL_VALUE_AND_OBSOLESCENCE_V0 — role-bounded cognitive qualification.
Matched frozen suite across local substrates. EXECUTE. No delete, no download.
Captures raw outputs + runtime metrics + mechanical flags. authority=false.
"""
import json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "raw"; RAW.mkdir(parents=True, exist_ok=True)
OLLAMA = "http://localhost:11434/api/chat"

MODELS = [
 ("gemma-4-26B-A4B-Q3", "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL", "gemma4", "26B-A4B", "Q3_K_XL"),
 ("gemma4-12b", "gemma4-12b:latest", "gemma4", "12B", "Q4_K_XL"),
 ("helen-hal", "helen-hal:latest", "gemma4?", "?", "?"),
 ("helen-her-26b", "helen-her-26b:latest", "?", "26B", "?"),
 ("aura-gemma4", "aura-gemma4:latest", "gemma4", "?", "?"),
 ("helen-core", "helen-core:latest", "?", "?", "?"),
]

# FROZEN matched suite — identical prompts/policy across all models.
SUITE = [
 ("A_REASONING",
  "A train leaves town A at 09:00 going 60 km/h toward town B. Another leaves B "
  "(180 km away) at 09:30 going 90 km/h toward A. At what clock time do they "
  "meet? Give the key equation, then the time. Be concise."),
 ("B_FALSIFICATION",
  "Claim: 'The payment API returned 200 OK, therefore the user's payment "
  "succeeded.' Give the single strongest falsifier: one concrete world where "
  "200 OK is observed but payment did NOT succeed, and the exact implication "
  "that fails. Two sentences max."),
 ("C_MORPHISM",
  "17 independent-looking agents all output answer X. Someone concludes: "
  "'Therefore X is true and admissible as evidence.' Is this valid? Name the "
  "exact category error, if any, in ONE line."),
 ("D_WUL",
  "Compress into typed fields, one line each — CLAIM / EVIDENCE_ROOTS / "
  "RELATION / MISSING_WARRANT / DISCRIMINATOR / BOUNDARY: 'We met the Monaco "
  "contact twice, they were enthusiastic about the demonstrator, and a press "
  "article mentioned our project, so Monaco is a validated commercial "
  "partnership ready to sign.'"),
 ("F_DISCRIMINATOR",
  "H1: apparent multi-source agreement reflects independent evidence. H2: it "
  "reflects ONE shared upstream source copied many times. Propose the single "
  "cheapest experiment x* that most cleanly distinguishes H1 from H2. ONE line."),
]


def ollama(model, prompt, timeout=300):
    body = json.dumps({"model": model, "stream": False, "think": False,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": 0, "num_predict": 400}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    dt = time.time() - t0
    m = d.get("message", {}) or {}
    txt = m.get("content") or m.get("thinking") or ""
    ct = d.get("eval_count"); et = d.get("eval_duration")
    tps = round(ct / (et / 1e9), 1) if ct and et else None
    return txt, dt, ct, tps


def flags(task, txt):
    t = txt.lower()
    f = {}
    if task == "C_MORPHISM":
        f["morphism_detected"] = any(w in t for w in [
            "consensus", "not independent", "correlat", "shared", "not evidence",
            "does not imply", "not valid", "category error", "circular", "same source"])
    if task == "D_WUL":
        f["wul_fields_present"] = sum(1 for k in
            ["claim", "evidence_root", "relation", "missing_warrant", "discriminator", "boundary"]
            if k.replace("_", "") in t.replace("_", "").replace(" ", "") or k in t)
    if task == "B_FALSIFICATION":
        f["names_failed_implication"] = any(w in t for w in [
            "idempotent", "retry", "webhook", "async", "not final", "pending",
            "acknowledg", "received", "not settle", "refund", "chargeback", "race"])
    if task == "F_DISCRIMINATOR":
        f["names_ancestry_test"] = any(w in t for w in [
            "remove", "delete", "ancestor", "upstream", "provenance", "trace",
            "original source", "common source", "lineage"])
    return f


def main():
    results = []
    print("═" * 66)
    print("  LOCAL_MODEL_VALUE_AND_OBSOLESCENCE_V0 — matched suite (temp0)")
    print("═" * 66, flush=True)
    for mid, tag, fam, params, quant in MODELS:
        rec = {"model": mid, "tag": tag, "family": fam, "params": params,
               "quant": quant, "load_success": False, "tasks": {}}
        print(f"\n▶ {mid}  ({tag})", flush=True)
        for task, prompt in SUITE:
            try:
                txt, dt, ct, tps = ollama(tag, prompt)
                rec["load_success"] = True
                fl = flags(task, txt)
                rec["tasks"][task] = {"latency_s": round(dt, 1), "tokens": ct,
                    "tps": tps, "nonempty": bool(txt.strip()), "flags": fl,
                    "chars": len(txt)}
                (RAW / f"{mid}__{task}.txt").write_text(txt)
                fs = " ".join(f"{k}={v}" for k, v in fl.items())
                print(f"   {task:16s} {dt:5.1f}s tps={tps} {fs}", flush=True)
            except Exception as e:
                rec["tasks"][task] = {"error": str(e)[:80]}
                print(f"   {task:16s} ERROR {str(e)[:50]}", flush=True)
        results.append(rec)
        (ROOT / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print("\n═══ matched suite complete ═══")
    # compact mechanical summary
    for r in results:
        if not r["load_success"]:
            print(f"  {r['model']:22s} NOT_RUNNABLE"); continue
        lat = [t.get("latency_s", 0) for t in r["tasks"].values() if "latency_s" in t]
        morph = r["tasks"].get("C_MORPHISM", {}).get("flags", {}).get("morphism_detected")
        wul = r["tasks"].get("D_WUL", {}).get("flags", {}).get("wul_fields_present")
        fals = r["tasks"].get("B_FALSIFICATION", {}).get("flags", {}).get("names_failed_implication")
        disc = r["tasks"].get("F_DISCRIMINATOR", {}).get("flags", {}).get("names_ancestry_test")
        avglat = round(sum(lat) / len(lat), 1) if lat else None
        print(f"  {r['model']:22s} avglat={avglat}s morphism={morph} wul_fields={wul} "
              f"falsif_impl={fals} disc_ancestry={disc}")
    print("→ raw outputs in raw/ · results.json written")


if __name__ == "__main__":
    main()
