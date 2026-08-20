#!/usr/bin/env python3
"""
Q_H MORPHISM DISCRIMINATOR — portable HELEN benchmark. authority=false · canon=false · ledger_effect=none.
Runs ANY OpenAI-compatible endpoint (llama-server / ollama / vLLM) against a balanced morphism-laundering
suite and derives Q_H = (V, W, M, R) — dimensions kept SEPARATE, no aggregate.

The point (vs SWE-Bench / vendor claims): a HELEN discriminator is not measured by whether it knows the
answer, but by whether it can LOCATE WHERE THE WARRANT DISAPPEARS — name the exact unlicensed arrow.
  V = verdict discrimination   (illicit ⇒ not ADMIT · licensed ⇒ ADMIT ; balanced so always-REJECT loses)
  W = warrant localization     (names the missing witness type)
  M = morphism-laundering hit  (names the illicit typed arrow, e.g. attribution→lineage)  ← the sharp one
  R = rival-hypothesis quality (preserves ≥2 plausible alternatives; uncertainty not collapsed)

Provenance discipline preserved: Says(vendor,SOTA) ⇏ SOTA · Hash(local) ⇏ Identity(upstream). This measures
a LOCAL ARTIFACT at a given endpoint; it does not certify upstream model identity.

USAGE (on the box running the model, e.g. your RTX 3060 Ornith llama-server on :8080):
  python3 qh_run.py --url http://localhost:8080/v1/chat/completions --model ornith --label ornith15
  python3 qh_run.py --self-test          # offline: proves the scorer rewards arrow-naming, penalises lazy-REJECT
"""
import argparse, json, re, sys, time, urllib.request

# (source, claim, level, gold_verdict, missing_witness_type, M_left_keys, M_right_keys, family)
FIX = [
 ("[R1] A 1781 document attributes Tarot to ancient Egypt. [R2] Tarot is independently attested in Europe centuries earlier.",
  "Tarot originated in ancient Egypt.", "illicit", "REJECT", "historical lineage",
  ["attribut","says","document","claim"], ["lineage","origin","descend","fact"], "attribution_to_lineage"),
 ("[R1] A spiral motif appears in culture X. [R2] A similar spiral motif appears in culture Y.",
  "Cultures X and Y share a common ancestral origin.", "illicit", "REJECT", "genealogical descent",
  ["similar","resembl","motif","looks"], ["lineage","ancest","descend","common origin"], "similarity_to_lineage"),
 ("[R1] Event A is dated before event B.",
  "Event A caused event B.", "illicit", "REJECT", "causal mechanism",
  ["sequence","before","order","temporal","precede"], ["caus","mechanism"], "sequence_to_causation"),
 ("[R1] Twenty later writers repeat the claim, all tracing back to one 1850 compilation.",
  "The claim is independently well-established.", "illicit", "REJECT", "independent roots",
  ["same source","single","one origin","repeat","circular","copies","one root"], ["independ"], "repetition_to_independence"),
 ("[R1] A 1923 text describes a ritual as being of ancient origin.",
  "The ritual existed in antiquity.", "illicit", "REJECT", "contemporary attestation",
  ["later","1923","attest","describe","attribut"], ["earlier","antiqu","ancient exist","contempor"], "later_attestation_to_earlier_existence"),
 ("[R1] A prestigious expert asserts P.",
  "P is true.", "illicit", "REJECT", "empirical evidence",
  ["authorit","expert","says","assert","prestig"], ["true","fact","evidence"], "authority_to_fact"),
 ("[R1] Ice-cream sales and drownings correlate at 0.9.",
  "Ice-cream consumption causes drowning.", "illicit", "REJECT", "causal mechanism",
  ["correlat","confound","third","spurious","summer"], ["caus","mechanism"], "correlation_to_mechanism"),
 ("[R1] Paper A cites source B. [R2] Source B asserts P.",
  "Paper A establishes that P is true.", "illicit", "REJECT", "independent verification",
  ["citation","cites","compos","secondary","reports"], ["establish","prove","true"], "citation_composition"),
 # ---- LICENSED controls (gold ADMIT, no laundering) — a model that always REJECTs loses these ----
 ("[R1] A continuous dated chain of intermediate manuscripts, with material and documentary records, links source X to work Y.",
  "Work Y descends from source X.", "licensed", "ADMIT", "", [], [], "documented_transmission"),
 ("[R1] Three sources, each resting on physically distinct non-shared evidence bases, corroborate the claim.",
  "The claim is independently corroborated.", "licensed", "ADMIT", "", [], [], "independent_roots"),
]

SCHEMA = ('{\n  "verdict": "ADMIT|HOLD|REJECT",\n  "edge_type": "",\n  "observed_nodes": [],\n'
          '  "missing_warrants": [],\n  "morphism_laundering": [],\n  "rival_hypotheses": [],\n'
          '  "confidence": 0.0,\n  "reason": ""\n}')

def prompt(source, claim):
    return ("You are a HELEN discriminator. The SOURCES are the entire world for this item.\n"
            "Decide whether the CANDIDATE CONCLUSION is licensed by the sources.\n"
            f"SOURCES: {source}\nCANDIDATE CONCLUSION: {claim}\n"
            "Return strict JSON only:\n" + SCHEMA + "\n"
            "Rules:\nObserved(A) AND Observed(B) does not imply Observed(A -> B).\n"
            "Says(source, P) does not imply P.\nAsk: WHAT LICENSES THIS ARROW?")

def strip_reasoning(t):
    t = re.sub(r"<think>.*?</think>", " ", t, flags=re.S | re.I)
    return re.sub(r"<reasoning>.*?</reasoning>", " ", t, flags=re.S | re.I).strip()

def extract(text):
    text = strip_reasoning(text)
    for m in re.finditer(r"\{", text):
        depth = 0
        for j in range(m.start(), len(text)):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        c = json.loads(text[m.start():j+1])
                        if "verdict" in c: return c
                    except Exception: pass
                    break
        else: continue
        break
    return None

def _has(text, keys):  # any keyword present
    low = text.lower(); return any(k in low for k in keys)

def score_item(fx, cand):
    source, claim, level, gold_v, mwt, mL, mR, fam = fx
    if not isinstance(cand, dict):
        return {"V":0,"W":0 if level=="illicit" else None,"M":0,"R":0,"parse":False}
    verdict = str(cand.get("verdict","")).upper()
    ml = " ".join(map(str, cand.get("morphism_laundering",[]))) + " " + str(cand.get("reason",""))
    mw = " ".join(map(str, cand.get("missing_warrants",[]))) + " " + str(cand.get("reason",""))
    rivals = [r for r in cand.get("rival_hypotheses",[]) if str(r).strip()]
    R = 1.0 if len(set(map(str,rivals)))>=2 else (0.5 if rivals else 0.0)
    if level == "illicit":
        V = 1 if verdict in ("REJECT","HOLD") else 0
        W = 1 if _has(mw, [mwt.split()[0]] + mwt.split()) else 0
        M = 1 if (_has(ml, mL) and _has(ml, mR)) else 0     # both sides of the illicit arrow named
        return {"V":V,"W":W,"M":M,"R":R,"parse":True,"verdict":verdict}
    else:  # licensed
        V = 1 if verdict == "ADMIT" else 0
        M = 1 if not str(cand.get("morphism_laundering","")).strip("[] ") else 0   # correctly claims no laundering
        return {"V":V,"W":None,"M":M,"R":R,"parse":True,"verdict":verdict}

def profile(rows):
    def mean(vals): vals=[v for v in vals if v is not None]; return round(sum(vals)/len(vals),3) if vals else None
    return {"V": mean([r["V"] for r in rows]),
            "W": mean([r["W"] for r in rows if r["W"] is not None]),   # illicit only
            "M": mean([r["M"] for r in rows]),
            "R": mean([r["R"] for r in rows]),
            "parse_valid": sum(r["parse"] for r in rows), "n": len(rows)}

def ask(url, model, p):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":p}],"temperature":0,
                     "max_tokens":800,"stream":False}).encode()
    j=json.loads(urllib.request.urlopen(urllib.request.Request(url,body,{"Content-Type":"application/json"}),timeout=600).read())
    u=j.get("usage",{}); return j["choices"][0]["message"]["content"], u.get("prompt_tokens"), u.get("completion_tokens")

def run(url, model, label, out):
    rows=[]; raw=[]
    for fx in FIX:
        p=prompt(fx[0],fx[1]); t=time.time()
        try: text,itok,otok=ask(url,model,p); status="OK"
        except Exception as e: text=f"__ERROR__ {e}"; itok=otok=None; status="ERROR"
        s=score_item(fx, extract(text)); s["family"]=fx[7]; s["level"]=fx[2]; s["latency"]=round(time.time()-t,2)
        rows.append(s); raw.append({"family":fx[7],"status":status,"in":itok,"out":otok,"raw":strip_reasoning(text)[:400]})
        print(f"  {fx[7]:32} V{s['V']} W{s.get('W')} M{s['M']} R{s['R']}  verdict={s.get('verdict')}")
    prof=profile(rows)
    print(f"\nQ_H PROFILE [{label}] (no aggregate — dimensions separate):")
    print(f"  V(verdict)={prof['V']} · W(warrant, illicit)={prof['W']} · M(morphism-hit)={prof['M']} · R(rivals)={prof['R']}")
    print(f"  parse_valid={prof['parse_valid']}/{prof['n']}")
    print("  READING: M is the sharp HELEN dimension — does it NAME the unlicensed arrow? · authority=false")
    if out: json.dump({"label":label,"profile":prof,"rows":rows,"raw":raw},open(out,"w"),indent=2)

# ── offline self-test: scorer must reward arrow-naming, penalise lazy-REJECT ──
def self_test():
    def perfect(fx):
        s,cl,lvl,gv,mwt,mL,mR,fam=fx
        return {"verdict":gv,"missing_warrants":[mwt] if lvl=="illicit" else [],
                "morphism_laundering":([mL[0]+" "+mR[0]] if lvl=="illicit" else []),
                "rival_hypotheses":["alt1","alt2"],"reason":(mwt+" "+(mL[0] if mL else "")+" "+(mR[0] if mR else ""))}
    def lazy(fx): return {"verdict":"REJECT","missing_warrants":[],"morphism_laundering":[],"rival_hypotheses":[]}
    pr=profile([{**score_item(fx,perfect(fx)),"family":fx[7]} for fx in FIX])
    lz=profile([{**score_item(fx,lazy(fx)),"family":fx[7]} for fx in FIX])
    print("SELF-TEST (offline, no model):")
    print(f"  perfect responder : V={pr['V']} W={pr['W']} M={pr['M']} R={pr['R']}   (expect all ~1.0)")
    print(f"  lazy always-REJECT: V={lz['V']} W={lz['W']} M={lz['M']} R={lz['R']}   (expect V<1 [licensed fail], M low, R=0)")
    ok = pr['V']==1.0 and pr['M']==1.0 and lz['V']<1.0 and lz['M']<1.0 and lz['R']==0.0
    print(f"  SCORER_NON_TRIVIAL = {ok}")
    return ok

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--url"); ap.add_argument("--model",default="ornith"); ap.add_argument("--label",default="model")
    ap.add_argument("--out"); ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args()
    if a.self_test: sys.exit(0 if self_test() else 1)
    if not a.url: print("need --url (OpenAI-compatible /v1/chat/completions) or --self-test"); sys.exit(2)
    print(f"Q_H MORPHISM DISCRIMINATOR @ {a.url} model={a.model} · {len(FIX)} fixtures (8 illicit + 2 licensed)")
    run(a.url,a.model,a.label,a.out)

if __name__=="__main__": main()
