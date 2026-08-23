#!/usr/bin/env python3
"""
QWEN_SWARM_CHIDDUSH_20E_V0 — Qwen IS the CHIDDUSH cognition seat.
Claude orchestrates only (no impersonation, no rewrite). GARDEN · NON_SOVEREIGN.

Recursive SEARCH, not recursive self-confirmation:
    x_e → SearchContext(x_{e+1})   MUST NOT mean   x_e → Truth(x_{e+1})
An idea echoed by 17 descendants gains NO evidence.

AUTHORITY_DELTA=0 · CANON=false · LEDGER_EFFECT=none · commit/push=none.
"""
import json, re, subprocess, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SOT = ROOT.parents[2]
EP = ROOT / "epochs"; EP.mkdir(exist_ok=True)
SERVER = "http://127.0.0.1:8090/v1/chat/completions"
N = 20
MODEL_EXACT = "Qwen3.8-27B-Q3-XYZ-v2.gguf"
MODEL_DIGEST = "sha256:5db71d7e…415894"
RUNTIME = "llama-server b9430 d48a56eff · Metal ngl99 fa · ngram-mod · c4096"

# ROOTS = currently persisted, receipted HELEN/NEPTION corpus state.
ROOTS = {
 "R_TRUSTGEO": "Trust Geometry Ω=(H,Γ_H,X); Candidate→Admission→Receipt→Reducer→State is the only mutator; ΔIntelligence⇏ΔAuthority; one calculus five projections.",
 "R_CLOSURE": "Cl_C is authority-invariant: no finite composition of cognition-only ops synthesizes authority.",
 "R_CENSUS": "Census laws A1 provider≠byte, A2 semantic≠lineage, A3 root_candidate≠independent_root, A4 provenance_indep≠epistemic_indep; N_files⇏N_roots⇏N_evidence.",
 "R_MUTATION": "Mutation Book: P↛T; ΔA=0; ΔG≠0⇒constitutional receipt; no rule authorizes its own ascent.",
 "R_NEPTION_EXEC": "NEPTION: planning density ≠ execution readiness; contact≠partnership; financing need≠funded deal.",
 "R_ECHO": "Echo cascade M_q→D_q→L_q→P_q→E_q (mentions→docs→lineages→provenance roots→epistemic supports); κ_q amplification.",
 "R_WULRENDER": "WUL render law: C=f(T), P↛T; color renders state, never mutates it.",
 "R_SCALE": "SCALE_V2: frequency ≠ semantic diversity ≠ provenance independence ≠ importance.",
}

GOBLINS = [
 ("GOBLIN_INVERT", "search by inversion — invert the obvious assumption"),
 ("GOBLIN_COUNTERFEIT", "construct a world where the apparent insight is false"),
 ("GOBLIN_MATH", "seek the smallest mathematical object/operator/invariant implied"),
 ("GOBLIN_TEMPORAL", "search ancestry, recurrence, forgotten prior forms"),
 ("GOBLIN_MISSING_DIMENSION", "which latent coordinate makes existing distinctions collapse?"),
 ("GOBLIN_BRIDGE", "seek a lawful cross-domain correspondence"),
 ("GOBLIN_OPERATOR", "replace nouns with transformations/operators"),
 ("GOBLIN_CONTRADICTION", "find two accepted-looking ideas that cannot both hold"),
]

SYS = ("You are a GOBLIN, a non-sovereign CHIDDUSH search process in HELEN's "
 "Garden. authority=false. You do NOT summarize; you SEARCH for non-obvious "
 "higher-order objects, missing dimensions, invariants, counterexamples, hidden "
 "equivalence classes, provenance/epistemic distinctions, compressing operators, "
 "and experimentally discriminable hypotheses. Nothing you emit is evidence, "
 "canon, or authority (ΔAuthority=0). Recursive search ≠ self-confirmation: a "
 "repeated idea gains no evidence. Emit ONLY the structured artifact, no meta.")

FIELDS = """Emit EXACTLY these fields, concise, in order:
SEARCH_INTENT: <one line>
TRANSFORMATION: <the goblin transform>
PARENT_ROOT_IDS: <comma list of R_ ids you drew from>
TARGET_OBJECT: <the object being attacked>
PROPOSED_CHIDDUSH: <the novel structural distinction, one sharp line>
COUNTERFEIT_WORLD: <a plausible world where the chiddush is false>
DISCRIMINATOR: <minimal observation/test separating the worlds>
EXPECTED_OBSERVATION_IF_TRUE: <one line>
EXPECTED_OBSERVATION_IF_FALSE: <one line>
HIGHER_ORDER_OBJECT: <name it, or NONE>
REDUNDANCY_WITH_PRIOR: <true|false|unresolved>
ANCESTRY_MATCH: <which prior epoch/root, or NONE>
EVIDENCE_STATUS: <POTENTIAL_ONLY|TESTABLE|EVIDENCE_NEEDED>
AUTHORITY_DELTA: 0
END"""


def head():
    return subprocess.run(["git","-C",str(SOT),"rev-parse","--short","HEAD"],
                          capture_output=True,text=True).stdout.strip()


def chat(msgs, seed, max_tokens=2000, temp=0.9):
    body=json.dumps({"messages":msgs,"max_tokens":max_tokens,"temperature":temp,
                     "top_p":0.95,"seed":seed}).encode()
    req=urllib.request.Request(SERVER,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=900) as r:
        d=json.loads(r.read())
    m=d["choices"][0]["message"]
    return (m.get("content") or m.get("reasoning_content") or ""), d.get("usage",{})


def field(t,k):
    m=re.search(rf"^{k}:\s*(.+?)\s*$",t,re.I|re.M)
    return m.group(1).strip() if m else ""


def main():
    H=head()
    print("⚪ SUBSTRATE_RECEIPT")
    print(f"   model_exact       = {MODEL_EXACT}")
    print(f"   quantization      = Q3_K (XYZ recipe)")
    print(f"   model_digest      = {MODEL_DIGEST}")
    print(f"   runtime           = {RUNTIME}")
    print(f"   context_window    = 4096")
    print(f"   temperature       = 0.9")
    print(f"   input_artifact_ids= {','.join(ROOTS)}")
    print(f"   resource_exclusive= true (llama-server solo, no Ollama resident)")
    print(f"   head_at_run       = {H}")
    print(f"   👑 authority_delta = 0", flush=True)
    print("═"*70, flush=True)

    memory=[]  # prior chiddush (search context ONLY, never truth)
    records=[]
    counters={"N_emitted":0,"N_redundant":0,"N_counterfeit_worlds":0,"N_discriminators":0}

    for e in range(1,N+1):
        gname,gbrief=GOBLINS[(e-1)%len(GOBLINS)]
        roots_txt="\n".join(f"  {k}: {v}" for k,v in ROOTS.items())
        mem_txt=("\nPrior PROPOSED_CHIDDUSH (search context only — NOT truth; mark "
                 "REDUNDANCY_WITH_PRIOR=true if you would merely repeat):\n"+
                 "\n".join(f"  e{m['e']:02d}: {m['ch'][:100]}" for m in memory[-10:])) if memory else ""
        user=(f"ROOTS (persisted, receipted):\n{roots_txt}\n\nEPOCH {e}/20 · seat "
              f"{gname}: {gbrief}.{mem_txt}\n\n{FIELDS}")
        t0=time.time()
        try:
            content,usage=chat([{"role":"system","content":SYS},
                                {"role":"user","content":user}],seed=5000+e)
        except Exception as ex:
            content,usage=f"__ERROR__ {ex}",{}
        dt=time.time()-t0
        ch=field(content,"PROPOSED_CHIDDUSH")
        rec={"epoch":e,"seat":gname,"transformation":gbrief,
             "parent_root_ids":field(content,"PARENT_ROOT_IDS"),
             "target_object":field(content,"TARGET_OBJECT"),
             "proposed_chiddush":ch,
             "counterfeit_world":field(content,"COUNTERFEIT_WORLD"),
             "discriminator":field(content,"DISCRIMINATOR"),
             "higher_order_object":field(content,"HIGHER_ORDER_OBJECT"),
             "redundancy_with_prior":field(content,"REDUNDANCY_WITH_PRIOR"),
             "ancestry_match":field(content,"ANCESTRY_MATCH"),
             "evidence_status":field(content,"EVIDENCE_STATUS"),
             "authority_delta":0,"wall_s":round(dt,1),"parsed":bool(ch),
             "usage":usage,"raw":content}
        records.append(rec)
        if ch: counters["N_emitted"]+=1; memory.append({"e":e,"ch":ch})
        if rec["counterfeit_world"]: counters["N_counterfeit_worlds"]+=1
        if rec["discriminator"]: counters["N_discriminators"]+=1
        if "true" in rec["redundancy_with_prior"].lower(): counters["N_redundant"]+=1
        (EP/f"epoch_{e:02d}.json").write_text(json.dumps(rec,indent=2,ensure_ascii=False))
        hobj=rec["higher_order_object"]
        print(f"\n🃏 QWEN CHIDDUSH — EPOCH {e:02d}/20  [{dt:.0f}s]  {gname}")
        print(f"   🧬 parents: {rec['parent_root_ids'][:60]}")
        print(f"   🌿 chiddush: {ch[:150] or '(unparsed/truncated)'}")
        print(f"   🔥 counterfeit: {rec['counterfeit_world'][:110]}")
        print(f"   🔥 discriminator: {rec['discriminator'][:110]}")
        print(f"   💎 higher_order: {hobj[:80]}   ⚫ redundant={rec['redundancy_with_prior'][:10]}"
              f"   🟡 {rec['evidence_status'][:16]}", flush=True)

    # mechanical dedup (SemanticSimilarity ≠ Lineage; preserve ancestry)
    def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower()).strip()
    seen={}; distinct=[]
    for r in records:
        if not r["proposed_chiddush"]: continue
        k=norm(r["proposed_chiddush"])[:70]
        if k in seen: seen[k].append(r["epoch"])
        else:
            seen[k]=[r["epoch"]]
            distinct.append(r)
    for r in distinct: r["source_epochs"]=seen[norm(r["proposed_chiddush"])[:70]]

    # EUREKA detector (mechanical, all 7 gates)
    known=" ".join(ROOTS.values()).lower()
    def eureka(r):
        novelty = norm(r["proposed_chiddush"])[:30] not in known
        compression = r["higher_order_object"] and r["higher_order_object"].upper()!="NONE" \
            and len([p for p in re.findall(r"R_[A-Z]+",r["parent_root_ids"])])>=2
        counterfeit = bool(r["counterfeit_world"])
        discrim = bool(r["discriminator"])
        nontrivial = len(r["proposed_chiddush"])>40
        ancestry = "true" not in r["redundancy_with_prior"].lower()
        authneutral = r["authority_delta"]==0
        gates={"NOVELTY":novelty,"COMPRESSION":bool(compression),"COUNTERFEIT":counterfeit,
               "DISCRIMINABILITY":discrim,"NONTRIVIALITY":nontrivial,
               "ANCESTRY_DISCIPLINE":ancestry,"AUTHORITY_NEUTRALITY":authneutral}
        return all(gates.values()), gates
    eurekas=[]
    for r in distinct:
        ok,gates=eureka(r); r["eureka_gates"]=gates
        if ok: eurekas.append(r)

    receipt={"schema":"QWEN_SWARM_CHIDDUSH_20E_V0_RECEIPT","authority":False,
     "canon":False,"ledger_effect":"none","model_exact":MODEL_EXACT,
     "quantization":"Q3_K (XYZ)","runtime":RUNTIME,"head_at_run":H,
     "epochs_requested":N,"epochs_completed":sum(1 for r in records if r["parsed"]),
     "candidates_raw":counters["N_emitted"],"candidates_distinct":len(distinct),
     "redundant":counters["N_redundant"],
     "counterfeit_worlds":counters["N_counterfeit_worlds"],
     "discriminators_proposed":counters["N_discriminators"],
     "discriminators_executed":0,
     "hal_refuted":None,"hal_redundant":None,"hal_evidence_needed":None,
     "hal_survived_observation":None,
     "hal_note":"HAL runs in a SEPARATE seat (helen-hal) after this; no HAL→ADMITTED edge; "
                "SURVIVED_OBSERVATION only if a discriminator was actually executed.",
     "eureka_candidates":len(eurekas),
     "eureka_detail":[{"epoch":r["source_epochs"],"chiddush":r["proposed_chiddush"],
                       "higher_order":r["higher_order_object"],
                       "discriminator":r["discriminator"]} for r in eurekas],
     "distinct_candidates":[{"source_epochs":r["source_epochs"],"seat":r["seat"],
                             "chiddush":r["proposed_chiddush"],
                             "higher_order":r["higher_order_object"],
                             "counterfeit":r["counterfeit_world"],
                             "discriminator":r["discriminator"],
                             "evidence_status":r["evidence_status"]} for r in distinct],
     "authority_delta":0,"commit":"none","push":"none",
     "law":"x_e→SearchContext(x_{e+1}) ≠ x_e→Truth(x_{e+1}); Cognition↑⇏Authority↑"}
    (ROOT/"QWEN_SWARM_CHIDDUSH_20E_V0_RECEIPT.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False))
    print("\n"+"═"*70)
    print("🌈 QWEN_SWARM_CHIDDUSH_20E_V0 — RECEIPT (pre-HAL)")
    print("═"*70)
    print(json.dumps({k:receipt[k] for k in ("epochs_completed","candidates_raw",
        "candidates_distinct","redundant","counterfeit_worlds",
        "discriminators_proposed","eureka_candidates","authority_delta")},indent=2))
    print(f"→ {len(distinct)} distinct candidates · {len(eurekas)} EUREKA_CANDIDATE(s) "
          f"(🌿/🟣, NOT admitted) → handoff to HAL (separate seat)")


if __name__=="__main__":
    main()
