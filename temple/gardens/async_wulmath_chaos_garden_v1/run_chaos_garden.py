#!/usr/bin/env python3
"""
ASYNC_WULMATH_CHAOS_GARDEN_V1 — HER(Gemma-4-26B) ∥ HAL(Qwen-3.8) async math meditation.
Independent divergence → late quotient → sparse cross-pollination → jester → alien.
NO_CLAIM · FABLE_CALLS=0 · AUTHORITY_DELTA=0. Claude orchestrates; models generate.
"""
import json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
EP = ROOT / "objects"; EP.mkdir(parents=True, exist_ok=True)
OLLAMA = "http://localhost:11434/api/chat"
HER = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"
HAL = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"

SEED = ("Search for a strange-but-formal mathematical object. Not a theorem, not "
        "truth, not consensus — a NEW structure. The Garden may be wrong; it must "
        "not pretend wrongness is truth. authority=0, evidence=0.")

FMT = """Output ONLY this compact object (one line each, no essay):
NAME: <short strange name>
GENESIS: <the one move that births it>
FORMAL_SEED: <one equation/typed relation>
STRANGE_PROPERTY: <what breaks intuition>
NEAREST_KNOWN_RELATIVE: <closest standard object>
WHY_NOT_JUST_RENAMING: <the structural difference | or RENAMING_ONLY>
COUNTERFEIT: <nearest boring look-alike>
BREAK_IT: <how it fails>
NEXT_MUTATION: <one operator to apply next>
END"""

HER_SYS = ("You are HER, constructive heterodoxy in a NO-CLAIM math Garden. Ask: "
 "'What object wants to exist here but has not been named?' Favor generative "
 "constructions (invent/mutate/recurse/dualize/glue/quotient/iterate). Make "
 "ordinary math STRANGER without making it meaningless. Emit only the object.")
HAL_SYS = ("You are HAL, adversarial heterodoxy in a NO-CLAIM math Garden. Ask: "
 "'What assumption is so natural nobody noticed mathematics could survive "
 "without it?' Favor destructive/reconstructive moves (invert/counterexample/"
 "reverse-arrows/erase-primitive/self-reference/literalize-metaphor/pathological "
 "limit). Attack the frame, not other answers. Emit only the object.")

# domain schedule (≥2 alg, 2 geom/top, 1 logic, 1 number, 1 dynamical, 1 info, 1 free, 1 absurd)
DOMAINS = ["algebraic","algebraic","geometric/topological","geometric/topological",
           "logic/proof-theory","number-theoretic","dynamical-systems",
           "information-theory","completely free","😂 absurd-but-formal (compile a joke)"]


def ollama(model, sys, user, temp=0.95, np=520, timeout=420):
    body=json.dumps({"model":model,"stream":False,"think":False,
        "messages":[{"role":"system","content":sys},{"role":"user","content":user}],
        "options":{"temperature":temp,"num_predict":np,"top_p":0.95}}).encode()
    req=urllib.request.Request(OLLAMA,data=body,headers={"Content-Type":"application/json"})
    t0=time.time()
    with urllib.request.urlopen(req,timeout=timeout) as r: d=json.loads(r.read())
    m=d.get("message",{}) or {}
    return (m.get("content") or m.get("thinking") or ""), round(time.time()-t0,1), d.get("eval_count") or 0


def field(t,k):
    m=re.search(rf"^{k}:\s*(.+?)\s*$",t,re.I|re.M); return m.group(1).strip() if m else ""


def run_stream(tag, model, sys):
    objs=[]; toks=0
    print(f"\n{'█'*60}\n{tag} private stream — {model.split('/')[-1]}\n{'█'*60}",flush=True)
    for e in range(1,11):
        prior=", ".join(o["name"][:24] for o in objs if o["name"]) or "(none)"
        user=(f"{SEED}\n\nEpoch {e}/10. Transformation family THIS epoch: {DOMAINS[e-1]}. "
              f"Do NOT elaborate a previous object — make a LATERAL JUMP. Already named "
              f"(avoid repeating): {prior}.\n\n{FMT}")
        try: raw,dt,ct=ollama(model,sys,user,temp=0.95)
        except Exception as ex: raw,dt,ct=f"__ERROR__ {ex}",0,0
        toks+=ct
        o={"stream":tag,"epoch":e,"domain":DOMAINS[e-1],"name":field(raw,"NAME"),
           "formal_seed":field(raw,"FORMAL_SEED"),"strange":field(raw,"STRANGE_PROPERTY"),
           "renaming":field(raw,"WHY_NOT_JUST_RENAMING"),"raw":raw,"wall_s":dt,"tokens":ct}
        objs.append(o)
        (EP/f"{tag}_{e:02d}.json").write_text(json.dumps(o,indent=2,ensure_ascii=False))
        print(f"\n🌿 {tag} E{e:02d} [{dt}s] «{o['name'][:44]}»  ({DOMAINS[e-1]})")
        print(f"   seed: {o['formal_seed'][:90]}")
        print(f"   strange: {o['strange'][:90]}",flush=True)
    return objs, toks


def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower()).strip()


def main():
    her,ht=run_stream("HER",HER,HER_SYS)
    hal,at=run_stream("HAL",HAL,HAL_SYS)

    # mechanical quotient over NAME+FORMAL_SEED
    allo=her+hal; seen={}; distinct=[]
    for o in allo:
        if not o["name"]: continue
        k=norm(o["name"]+" "+o["formal_seed"])[:60]
        if k in seen: seen[k].append((o["stream"],o["epoch"]))
        else: seen[k]=[(o["stream"],o["epoch"])]; distinct.append(o)
    renaming=[o for o in allo if "renaming_only" in o["renaming"].lower()]

    # cross-pollination: give each seat the other's 3 "most distant" (proxy: longest distinct names)
    her_pick=sorted([o for o in her if o["name"]],key=lambda o:-len(o["strange"]))[:3]
    hal_pick=sorted([o for o in hal if o["name"]],key=lambda o:-len(o["strange"]))[:3]
    cross=[]
    print(f"\n{'█'*60}\nCROSS-POLLINATION (epoch 11) — one mutation each\n{'█'*60}",flush=True)
    for src_model,src_sys,tag,gifts in [(HAL,HAL_SYS,"HAL◁HER",her_pick),(HER,HER_SYS,"HER◁HAL",hal_pick)]:
        for g in gifts:
            u=(f"A foreign Garden object arrives:\nNAME: {g['name']}\nSEED: {g['formal_seed']}\n"
               f"STRANGE: {g['strange']}\n\nApply EXACTLY ONE of 🧬MUTATE / 🪞DUALIZE / ↯DESTROY. "
               f"Emit only the resulting object.\n\n{FMT}")
            try: raw,dt,ct=ollama(src_model,src_sys,u,temp=0.95)
            except Exception as ex: raw,dt,ct=f"__ERROR__ {ex}",0,0
            c={"tag":tag,"parent":g["name"],"name":field(raw,"NAME"),
               "formal_seed":field(raw,"FORMAL_SEED"),"raw":raw,"wall_s":dt}
            cross.append(c)
            print(f"\n🧬 {tag}  parent «{g['name'][:30]}» → «{c['name'][:40]}» [{dt}s]")
            print(f"   {c['formal_seed'][:100]}",flush=True)

    # jester (epoch 19) — one absurd-but-formal each
    jest=[]
    print(f"\n{'█'*60}\nJESTER (epoch 19) — funniest mathematically coherent object\n{'█'*60}",flush=True)
    for model,sys,tag in [(HER,HER_SYS,"HER"),(HAL,HAL_SYS,"HAL")]:
        u=("Invent the FUNNIEST mathematically coherent object you can. The joke is "
           "scaffolding; the formal object is the output. Compile the joke into a "
           f"FORMAL_SEED.\n\n{FMT}")
        try: raw,dt,ct=ollama(model,sys,u,temp=1.0)
        except Exception as ex: raw,dt,ct=f"__ERROR__ {ex}",0,0
        jest.append({"stream":tag,"name":field(raw,"NAME"),"formal_seed":field(raw,"FORMAL_SEED"),"raw":raw})
        print(f"\n😂 {tag} JESTER «{field(raw,'NAME')[:44]}»  seed: {field(raw,'FORMAL_SEED')[:80]}",flush=True)

    # alien (epoch 20) — anti-self-reference meta-pattern
    names=[o["name"] for o in distinct if o["name"]]
    u=("Here are invented objects: "+"; ".join(names[:16])+". Forget all prior "
       "vocabulary. Looking ONLY at these objects, what ONE completely different "
       "organizing principle would an alien mathematician infer? One line. No doctrine.")
    try: alien,_,_=ollama(HAL,"You are a neutral alien mathematician.",u,temp=0.8,np=200)
    except Exception as ex: alien=f"__ERROR__ {ex}"
    alien=alien.strip()[:400]
    print(f"\n👽 ALIEN META-PATTERN: {alien[:200]}",flush=True)

    receipt={"schema":"ASYNC_WULMATH_CHAOS_GARDEN_V1_RECEIPT","authority":False,"canon":False,
      "claim":"NO_CLAIM","fable_calls":0,"observations_created":0,"warrant_created":0,
      "authority_delta":0,"effects_executed":0,"commit":"none","push":"none",
      "HER_MODEL":HER,"HAL_MODEL":HAL,"epochs_requested":20,
      "her_raw_objects":len([o for o in her if o["name"]]),
      "hal_raw_objects":len([o for o in hal if o["name"]]),
      "raw_total":len([o for o in allo if o["name"]]),
      "quotient_total":len(distinct),"renaming_only":len(renaming),
      "distinct_structures":len(distinct),
      "unique_HER":len([o for o in her if o["name"] and seen.get(norm(o["name"]+" "+o["formal_seed"])[:60],[("",0)])[0][0]=="HER" and len(seen[norm(o["name"]+" "+o["formal_seed"])[:60]])==1]),
      "cross_pollination_objects":len([c for c in cross if c["name"]]),
      "jester_objects":[{"stream":j["stream"],"name":j["name"],"seed":j["formal_seed"]} for j in jest],
      "collisions":{k:v for k,v in seen.items() if len(v)>1},
      "top5_strangest":sorted([{"name":o["name"],"strange":o["strange"][:120],"stream":o["stream"]} for o in distinct if o["strange"]],key=lambda x:-len(x["strange"]))[:5],
      "cross_pollination_detail":[{"tag":c["tag"],"parent":c["parent"],"name":c["name"],"seed":c["formal_seed"][:100]} for c in cross if c["name"]],
      "alien_meta_pattern":alien,
      "eta_J":round(len(distinct)/max(1,ht+at),6),
      "duplication_rate":round(1-len(distinct)/max(1,len([o for o in allo if o['name']])),3),
      "local_tokens":ht+at,
      "claim_ceiling":"Two local model roles generated and recombined mathematical possibilities inside a non-epistemic Garden. No object was validated by this run."}
    (ROOT/"ASYNC_WULMATH_CHAOS_GARDEN_V1_RECEIPT.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False))
    print("\n"+"═"*60+"\n🌈 RECEIPT")
    print(json.dumps({k:receipt[k] for k in ("raw_total","distinct_structures","renaming_only",
        "cross_pollination_objects","duplication_rate","eta_J","local_tokens","authority_delta")},indent=2))


if __name__=="__main__": main()
