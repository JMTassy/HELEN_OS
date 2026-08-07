"""CONSENSUS STEP 0 — VOICE PROBE (cheapest rung, before any training). NON_SOVEREIGN.
Doctrine: prompt -> validator -> weights. Prove a system prompt CAN'T already draft in
JMT's voice before spending a LoRA. The true judge of "sounds like me" is JMT (the
discriminating human witness), not a metric. authority=false.

Input : probe_samples.jsonl  rows = {"text": <a REAL JMT passage>, "source_file_id": ...}
Run   : python3 voice_probe.py --tasks "Write a LinkedIn hook about governed AI"
"""
import json, argparse, urllib.request
MODEL="hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"
SYS=("You write in the voice of JMT — Polytechnique-precise, editorial, confident, concrete "
     "over abstract, receipts over claims, warm but sharp, short punchy sentences. Study the "
     "examples of his real writing, then write NEW text in that exact voice. Voice only — never "
     "assert facts or metrics you cannot cite.")
def gen(system,user):
    body={"model":MODEL,"stream":False,"think":False,
          "messages":[{"role":"system","content":system},{"role":"user","content":user}],
          "options":{"temperature":0.7,"num_predict":220}}
    req=urllib.request.Request("http://localhost:11434/api/chat",data=json.dumps(body).encode(),
                               headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req,timeout=180).read())["message"].get("content","").strip()
def fewshot(samples):
    ex="\n\n".join(f"— {s['text']}" for s in samples[:8])
    return SYS + "\n\nHIS REAL WRITING (study the cadence):\n" + ex
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",default="probe_samples.jsonl")
    ap.add_argument("--tasks",nargs="*",default=["Write a LinkedIn hook (2-3 lines) about governed AI, in JMT's voice."])
    ap.add_argument("--stand-in",action="store_true",help="use built-in stand-in text to TEST THE HARNESS ONLY")
    a=ap.parse_args()
    if a.stand_in:
        samples=[{"text":"AI made production free. So I sell what it never touched: 25 years of receipts, a voice, and the people who answer the phone.","source_file_id":"STANDIN"},
                 {"text":"In 2000 I bet creative and technical would fuse before anyone was ready. The AI age is that bet at maximum amplitude. I wasn't adapting to it. I was built for it.","source_file_id":"STANDIN"}]
        print("### HARNESS TEST — STAND-IN samples (NOT JMT's verified voice). Mechanism only. ###\n")
    else:
        samples=[json.loads(l) for l in open(a.samples) if l.strip()]
    sysp=fewshot(samples)
    for t in a.tasks:
        print(f"TASK: {t}\nDRAFT:\n{gen(sysp,t)}\n"+"-"*60)
    print("JUDGE: JMT. Does this sound like you? YES -> prompt may be sufficient (no/small LoRA). "
          "NO -> FINE_TUNE_JUSTIFIED; run the full pipeline.")
