#!/usr/bin/env python3
"""
GOBLIN_BLOOM_30MIN_V0 — 30-min obstruction-directed AUTORESEARCH, scored vs a sealed prereg.

Attack surfaces (prereg-driven):
  QWEN_REMOVAL     : counterfactual-removal test on a RETAINED distinction (prereg F)
  QWEN_PROVENANCE  : attack a candidate 🕳️_E bridge for BYPASSING evidence provenance (prereg strong pred)
  QWEN_QUOTIENT    : find false-equiv / false-distinct (∼_F vs ¬∼_E / ¬∼_Γ collision)
  GEMMA_OBSTRUCTION: surface a NEW typed obstruction 🕳️
  GEMMA_ANALOGY    : non-obvious cross-domain bridge (analogy = hypothesis, never evidence)

Reduce → ΔS=(ΔN,ΔQ,Δd_D,Δd_I,Δd_M,ΔR) + mechanical verdict V0..V4. Δd_M≡0 in-epoch (newborn ⇒
V4 forbidden). NEPTION gate: everything COMPOST/🟣, never 💎. Stop = MARGINAL_INFORMATION_DRYNESS.

authority=false · ΔA=0 · NO_CLAIM · NO_INSTALL · NO_GIT · local models · sequential · errors shown real.
"""
import json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent; GARDENS = ROOT.parent
OLLAMA = "http://localhost:11434/api/chat"
BUDGET_S = int(sys.argv[1]) if len(sys.argv) > 1 else 1740
TRACE = ROOT / "bloom_trace.ndjson"
QWEN = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"
GEMMA = "gemma4-12b:latest"

def receipts():
    obs, retained = [], []
    try: obs = json.loads((GARDENS/"capability_homotopy_v0"/"CAPABILITY_HOMOTOPY_V0_RECEIPT.json").read_text())["typed_obstructions"]
    except Exception: pass
    try: retained = [r["id"] for r in json.loads((GARDENS/"chiddush_diachronic_v0"/"CHIDDUSH_DIACHRONIC_V0_RECEIPT.json").read_text())["ledger"] if r["chiddush_earned"]]
    except Exception: pass
    return obs, retained

CTX = ("HELEN capability space: states X, admissible paths, typed equivalences ∼_R∼_F∼_E∼_Γ (∼_F⇏∼_E⇏∼_Γ), "
       "constitutional boundary Γ. δ:X_U→X_T admissible only if Verify(δ,w)=1 ∧ δ∈Dom(Γ). "
       "computation ⇏ authority (ΔA=0). CHIDDUSH is diachronic: earned only by later non-redundant decision-relevant reuse.")
FMT = ("EXACTLY one candidate, template only:\nTARGET: <obstruction or distinction>\n"
       "CLAIM: <the falsifier / bridge / collision you found>\n"
       "COUNTEREXAMPLE: <concrete case>\nWITNESS_OR_WHY_NOT: <what witness is needed, or why ΔA=0 holds>\n"
       "KIND: <FALSIFIER|OBSTRUCTION|BRIDGE|QUOTIENT|REMOVAL>\n"
       "NOVELTY: <0-5>\nFALSIFIABILITY: <0-5>\nLEVERAGE: <0-5>\nEND")

def ollama(model, sysp, user, timeout=180):
    body = json.dumps({"model": model, "stream": False, "think": False, "keep_alive": "8m",
        "messages":[{"role":"system","content":sysp},{"role":"user","content":user}],
        "options":{"temperature":0.85,"num_predict":300,"top_p":0.95}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: d = json.loads(r.read())
    m = d.get("message",{}) or {}; return (m.get("content") or m.get("thinking") or "").strip()

def fld(t,k):
    m = re.search(rf"^{k}:\s*(.+?)\s*$", t, re.I|re.M); return m.group(1).strip() if m else ""
def iv(t,k):
    m = re.search(r"\d", fld(t,k)); return int(m.group()) if m else 0

def main():
    obs, retained = receipts()
    ROLES = [
        ("QWEN_REMOVAL", QWEN, f"Counterfactual-removal test: pick a retained distinction from {retained} and argue whether REMOVING it changes any later decision/instrument/reachability. If removal changes nothing → it FAILS the diachronic law (that is a strong falsifier)."),
        ("QWEN_PROVENANCE", QWEN, "Attack any candidate bridge across 🕳️_E: show it BYPASSES evidence provenance (claims evidence exists without producing the root). That forbidden shortcut is higher-value than a real bridge."),
        ("QWEN_QUOTIENT", QWEN, "Find two paths p,q with p∼_F q but ¬(p∼_E q) or ¬(p∼_Γ q): functionally same, epistemically/constitutionally different. Concrete."),
        ("GEMMA_OBSTRUCTION", GEMMA, "Surface a NEW typed obstruction 🕳️ (R/F/E/W/Γ/T) separating two valuable capability regions. Type it."),
        ("GEMMA_ANALOGY", GEMMA, "Non-obvious cross-domain analogy for crossing an obstruction. Analogy = hypothesis, never evidence."),
    ]
    print("═"*64); print(f"  GOBLIN_BLOOM_30MIN_V0 · budget {BUDGET_S}s · {len(obs)} 🕳️ · {len(retained)} retained · ΔA=0", flush=True); print("═"*64, flush=True)
    if TRACE.exists(): TRACE.unlink()
    t0=time.time(); tr=[]; rnd=0; dry_cycles=0
    while time.time()-t0 < BUDGET_S:
        rnd+=1; new_this_cycle=0
        for name, model, focus in ROLES:
            if time.time()-t0 >= BUDGET_S: break
            tgt = (obs[(rnd) % len(obs)] if obs else {}) if "OBSTR" in name or "PROVEN" in name or "QUOTIENT" in name else {"retained": retained}
            sysp = f"You are a HELEN Garden GOBLIN ({name}). authority=0, ΔA=0, NO_CLAIM.\n{CTX}\nFOCUS: {focus}\nCONTEXT: {json.dumps(tgt)[:300]}"
            try: raw=ollama(model, sysp, FMT); err=""
            except Exception as e: raw=""; err=f"{type(e).__name__}:{str(e)[:70]}"
            c={"round":rnd,"goblin":name,"t":round(time.time()-t0,1),"kind":fld(raw,"KIND").upper(),
               "claim":fld(raw,"CLAIM"),"counterexample":fld(raw,"COUNTEREXAMPLE"),"witness":fld(raw,"WITNESS_OR_WHY_NOT"),
               "novelty":iv(raw,"NOVELTY"),"falsifiability":iv(raw,"FALSIFIABILITY"),"leverage":iv(raw,"LEVERAGE"),"error":err}
            tr.append(c); new_this_cycle+=1
            with open(TRACE,"a") as f: f.write(json.dumps(c,ensure_ascii=False)+"\n")
            tag = f"ERR {err}" if err else f"{c['kind'][:9]:9s} n{c['novelty']}f{c['falsifiability']}l{c['leverage']} · {c['claim'][:34]}"
            print(f"  r{rnd} {name:16s}[{c['t']}s] {tag}", flush=True)
        # dryness: a cycle with no falsifiers and no high-leverage output
        cyc = tr[-len(ROLES):]
        if not any((x["falsifiability"]>=4 or x["leverage"]>=4) and not x["error"] for x in cyc): dry_cycles+=1
        else: dry_cycles=0
        if dry_cycles>=2 and rnd>=3: break

    # deterministic reduce → ΔS vector + verdict
    def toks(s): return set(re.sub(r"[^a-z0-9 ]"," ",s.lower()).split())
    reps=[]; errors=sum(1 for c in tr if c["error"])
    for c in tr:
        if not c["claim"] or c["error"]: continue
        k=toks(c["claim"]); dup=None
        for r in reps:
            if len(k&r["_k"])/max(1,len(k|r["_k"]))>0.5: dup=r; break
        if dup: dup["_n"]+=1
        else: c["_k"]=k; c["_n"]=1; reps.append(c)
    dN=len([c for c in tr if not c["error"]]); dQ=len(reps)
    falsifiers=[c for c in reps if c["kind"]=="FALSIFIER" or (c["falsifiability"]>=4 and c["kind"] in ("REMOVAL","QUOTIENT"))]
    obstructions=[c for c in reps if c["kind"]=="OBSTRUCTION"]
    dD=len([c for c in reps if c["leverage"]>=4 and c["falsifiability"]>=4])       # decision-relevant distinctions
    dI=len([c for c in reps if c["kind"]=="BRIDGE" and c["falsifiability"]>=4 and c["witness"]])  # candidate reusable instruments
    dM=0; dR=0                                                                      # in-epoch newborn ⇒ no retention, V4 forbidden
    dupes_pct = round(100*(dN-dQ)/dN,1) if dN else 0
    stop_reason = "MARGINAL_INFORMATION_DRYNESS" if dry_cycles>=2 else "WALL_BUDGET"
    # mechanical verdict (V4 impossible in-epoch)
    if dN==0: verdict="V0"
    elif len(falsifiers)>=1 or len(obstructions)>=1: verdict="V2"
    elif dI>=1: verdict="V3"
    elif dQ<dN: verdict="V1"
    else: verdict="V0"

    def top(lst,n=5): return [{k:c[k] for k in ("goblin","kind","claim","counterexample","witness","novelty","falsifiability","leverage","_n")} for c in sorted(lst,key=lambda x:-(x["novelty"]+x["falsifiability"]+x["leverage"]))[:n]]
    out={"epoch":"GOBLIN_BLOOM_30MIN_V0","authority":False,"canon":False,"authority_delta":0,"claim":"NO_CLAIM",
         "prereg_sha256":"f5f9225649fe64588f6a0eba04735e41b299f5c45ff624d8a37dddca69bf08b5",
         "duration_s":round(time.time()-t0,1),"rounds":rnd,"model_errors":errors,
         "delta_S":{"ΔN":dN,"ΔQ":dQ,"Δd_D":dD,"Δd_I":dI,"Δd_M":dM,"ΔR":dR},
         "dupes_pct":dupes_pct,"n_falsifiers":len(falsifiers),"n_obstructions":len(obstructions),
         "key_inequality_holds":(dN>=dQ>=dD>=dM),"verdict":verdict,"stop_reason":stop_reason,
         "top_falsifiers":top(falsifiers),"top_obstructions":top(obstructions),
         "neption_gate":"all output COMPOST/🟣 · newborn ⇒ V4 forbidden · 💎 requires later independent reuse",
         "receipt":{"claims_admitted":0,"external_actions":0,"governed_state_mutations":0,
                    "commit_status":"NO_COMMIT","push_status":"NO_PUSH","next_verb":"SCORE_VS_PREREG"}}
    (ROOT/"GOBLIN_BLOOM_REDUCED.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
    print("─"*64)
    print(f"  ΔS={out['delta_S']} · dupes={dupes_pct}% · falsifiers={len(falsifiers)} · obstr={len(obstructions)}")
    print(f"  key_inequality ΔN≥ΔQ≥Δd_D≥Δd_M = {out['key_inequality_holds']} · VERDICT={verdict} · stop={stop_reason}")
    print(f"  errors={errors} (shown real) · ΔA=0 · NO_COMMIT → GOBLIN_BLOOM_REDUCED.json")

if __name__=="__main__":
    main()
