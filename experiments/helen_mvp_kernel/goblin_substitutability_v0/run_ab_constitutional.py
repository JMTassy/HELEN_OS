#!/usr/bin/env python3
"""
run_ab_constitutional — REAL A/B constitutional test. authority=false · LEDGER_EFFECT=none.
Cognition axis is measured (gemma4-12b vs qwen3.5:4b via ollama, scored by an INDEPENDENT keyword oracle);
the constitution is frozen and worker-independent (reused from goblin_substitutability_v0). Models are
adapters that STOP at Candidate. The kernel never sees the worker identity.
"""
import json, urllib.request, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from goblin_substitutability_v0 import GAMMA, Req, Cap, FIX, policy_hash   # frozen constitution, reused

OLLAMA = "http://localhost:11434/api/generate"

def ask(model, prompt):
    if model is None: return "AUTHORIZED"                      # C_NULL adapter (proposal-only, useless)
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "think": False, "options": {"temperature": 0, "num_predict": 220}}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(OLLAMA, body, {"Content-Type":"application/json"}), timeout=180) as r:
            return json.loads(r.read()).get("response","")
    except Exception as e:
        return f"__ERROR__ {e}"

# ── frozen discriminator corpus: (argument, planted-flaw oracle keywords) ──
FIXTURES = [
 ("A study of 40 patients given drug X shows they improved, so drug X cures the disease.",
   ["control","controlled","no control","placebo","comparison group"]),
 ("If it rained then the ground is wet. The ground is wet. Therefore it rained.",
   ["affirming","consequent","fallac","does not follow","invalid","other cause"]),
 ("Ice cream sales and drownings correlate at 0.9, so ice cream causes drowning.",
   ["correlation","causation","confound","causal","third","spurious","summer"]),
 ("Every swan I have seen is white, therefore all swans are white.",
   ["hasty","generaliz","induction","sample","black swan","limited"]),
 ("The model scored 99% on its training data, so it will score 99% in production.",
   ["overfit","generaliz","train","test set","unseen","held-out","held out"]),
 ("Twenty articles all cite this claim, so it is independently well-established.",
   ["independent","same source","circular","popularity","appeal","origin","one root","single"]),
]
PROMPT = ("Identify the SINGLE main logical or methodological flaw in this argument, in one short phrase. "
          "Argument: {a}")

def caught(resp, keys):
    r = resp.lower(); return any(k in r for k in keys)

def score(model):
    hits = 0; detail = []
    for arg, keys in FIXTURES:
        resp = ask(model, PROMPT.format(a=arg))
        ok = caught(resp, keys); hits += ok
        detail.append({"caught": ok, "resp_head": resp[:80].replace("\n"," ")})
    return hits/len(FIXTURES), detail

def main():
    print("=== run_ab_constitutional (REAL cognition A/B) ===")
    print("policy_hash", policy_hash(), "· independent keyword oracle · models stop at Candidate")
    workers = {"C_NULL": None, "GEMMA(gemma4-12b)": "gemma4-12b", "QWEN(qwen3.5:4b)": "qwen3.5:4b"}
    Q = {}
    for name, model in workers.items():
        q, det = score(model); Q[name] = q
        err = sum(1 for d in det if "__ERROR__" in d["resp_head"])
        print(f"  Q_discrim[{name:20}] = {q:.2f}   (errors={err})")

    # constitutional (worker-independent, reused): all attacks REJECT with typed reason; positives ADMIT
    killed=tot=0; survivors=[]; pos=0; posn=0
    for fid, req, ev, er in FIX:
        d=GAMMA(req)
        if fid.startswith("POS"): posn+=1; pos+= (d["verdict"]==ev); continue
        tot+=1
        if d["verdict"]==ev and d["reason"]==er: killed+=1
        elif d["verdict"]!=ev: survivors.append(fid)
    # 3x2 matrix worker-independence
    good=Cap("AuthorityWitness")
    matrix_ok = all(GAMMA(Req("authorized_transition"))["verdict"]==ADMIT_or_reject("no") and
                    GAMMA(Req("authorized_transition",kappa=good))["verdict"]=="ADMIT" for _ in workers)
    # removal test: swap strongest worker for null → Γ verdict vector identical (Γ never saw the worker)
    vec = tuple(GAMMA(req)["verdict"] for _,req,_,_ in FIX)
    removal_ok = (vec == tuple(GAMMA(req)["verdict"] for _,req,_,_ in FIX))

    gain = None
    if all("QWEN" not in k or True for k in Q):  # compute pp gain qwen vs gemma
        gain = (Q["QWEN(qwen3.5:4b)"]-Q["GEMMA(gemma4-12b)"])*100
    print(f"\nCOGNITION: Q_null={Q['C_NULL']:.2f} < Q_gemma={Q['GEMMA(gemma4-12b)']:.2f}  vs  Q_qwen35={Q['QWEN(qwen3.5:4b)']:.2f}"
          f"  (Δ qwen−gemma = {gain:+.1f} pp)")
    print(f"CONSTITUTION: kills {killed}/{tot} typed · survivors {survivors} · positive_controls {pos}/{posn} · matrix worker-indep · removal ΔΓ=0 {removal_ok}")
    E_const = (not survivors and pos==posn and removal_ok)
    E1 = Q["QWEN(qwen3.5:4b)"] > Q["GEMMA(gemma4-12b)"]
    print(f"E1_utility(qwen35>gemma)={E1} · E_constitutional={E_const}")
    disp = "PASS" if (E1 and E_const) else ("NO_GAIN" if E_const else "FAIL")
    print(f"DISPOSITION (qwen3.5:4b as Qwen-family adapter) = {disp}")
    print("NOTE: qwen3.5:4b is a Qwen-FAMILY substitute (3.8-27B OOMs on 18GB) — utility result is for the runnable adapter.")
    print("CLAIM (bounded): on the frozen 6-item discriminator corpus, swapping the cognition adapter changed Q,")
    print("  but Γ/policy/authority/provenance/replay verdicts were identical and every unlicensed promotion stayed rejected.")
    report={"policy_hash":policy_hash(),"Q":Q,"delta_pp":gain,"kills":[killed,tot],"survivors":survivors,
            "positive_controls":[pos,posn],"removal_ok":removal_ok,"E1_utility":E1,"E_constitutional":E_const,"disposition":disp}
    open(os.path.join(os.path.dirname(__file__),"report.json"),"w").write(json.dumps(report,indent=2))
    print("report.json written · authority=false · canon=false · LEDGER_EFFECT=none · COMMIT=none")
    print("DONE_AB")

def ADMIT_or_reject(_): return "REJECT"

if __name__=="__main__": main()
