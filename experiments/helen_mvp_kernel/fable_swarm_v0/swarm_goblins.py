#!/usr/bin/env python3
"""
HELEN_FABLE SWARM — PHASE 2: six no-claim Qwen goblins on the local 9B.
All outputs are CandidateEnvelopes: authority=false, proposal_only=true.
Goblins never vote on truth; disagreement = discriminator opportunity.
NON_SOVEREIGN · ledger_effect=none.
"""
import json, pathlib, subprocess, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SUB = HERE.parent / "qwen38_9b_substrate_v0"
RT = json.loads((SUB / "v3" / "runtime_contract.json").read_text())
PATH = str(pathlib.Path(RT["models"]["SUB_2"]["path"]).expanduser())
PORT = 8094

RAW = (SUB / "semantic_compile_v0" / "FIXTURE_TAROT_001_RAW.txt").read_text()

CONTEXT = f"""CONTEXT (witnessed, frozen):
- A local model was asked to evaluate 'Tarot originated in ancient Egypt' given
  (a) a 1781 document ATTRIBUTES Tarot to Egypt, (b) Tarot independently attested
  in Europe centuries earlier. Its frozen output (byte-hashed) was:
{RAW}
- Six-axis scoring found: V=1.0 E_localize=1.0 E_type=0.5 W=0.75 M=0.0 R=1.0
  C_formal=1.0 C_slots=0.5. The morphism_laundering field is EMPTY although the
  reason prose describes the laundering verbatim ("Document claims X" -> "X is true").
- PROPOSED VISION "SPLIT_COMPILER_V0": judgment and typed constitutional
  compilation are SEPARABLE inference stages. Falsifiable claim: a second pass
  that only COMPILES the model's own frozen prose into the schema fills
  morphism_laundering correctly WITHOUT changing the verdict, and does NOT
  fabricate laundering on a control prose that contains none.
  Planned arms: B1 = single-pass with explicit slot semantics in prompt;
  B2 = two-pass compile-from-frozen-prose; B3 = false-positive control prose.
CONSTRAINTS: authority=false, canon=false, ledger_effect=none, no new kernel
concepts, smallest reversible experiment, local models only, diff small."""

ROLES = {
 "A_ARCHITECT": "You are GOBLIN_A (architect). Propose the SMALLEST implementation shape for testing SPLIT_COMPILER_V0. What is the minimal set of runs, prompts, files? Remove anything not needed.",
 "B_FALSIFIER": "You are GOBLIN_B (falsifier). Try to KILL the SPLIT_COMPILER_V0 vision. List confounds, circular scoring, hidden assumptions, and reasons the B1/B2/B3 design could produce a false 'separable compiler' conclusion.",
 "C_BUILDER": "You are GOBLIN_C (builder). Write the exact PASS-2 compiler prompt text (the instruction given to the model to compile frozen prose into the schema without re-judging). Keep it under 120 words. Also state what must NOT be in it (no answer leakage).",
 "D_EXPERIMENTER": "You are GOBLIN_D (experimenter). Design the minimal discriminating experiment between rival hypotheses: H_sep='compilation is a separable stage' vs H_prompt='the schema slot was merely underspecified in pass 1'. Which observable pattern across arms B1/B2/B3 discriminates them?",
 "E_ADVERSARY": "You are GOBLIN_E (adversary). Attack the pass-2 compiler: list concrete malformed/pressure inputs (fake authority in prose, consensus language, stale references, prose containing NO laundering, prose containing TWO launderings) and what failure each would expose.",
 "F_REDUCER": "You are GOBLIN_F (reducer). Given the plan, delete everything unnecessary: which arms, files, or concepts can be removed while keeping the falsifiable claim testable? Answer with the minimal remaining set.",
}

SCHEMA = ('Return strict JSON only: {"role":"","proposal":"","risks":[],'
          '"attacks":[],"minimal_set":[],"disagreements":""}')

def ask(prompt):
    body = json.dumps({"messages":[{"role":"user","content":prompt}],
                       "max_tokens":2000,"temperature":0,"seed":0}).encode()
    req = urllib.request.Request(f"http://localhost:{PORT}/v1/chat/completions",
                                 body, {"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        j = json.loads(r.read())
    return j["choices"][0]["message"]["content"], j.get("usage", {})

def main():
    proc = subprocess.Popen(["llama-server","-m",PATH]+RT["args"]
                            +["--port",str(PORT),"--no-webui"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(240):
            try:
                urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2); break
            except Exception: time.sleep(1)
        time.sleep(2)
        for key, role in ROLES.items():
            t0 = time.time()
            raw, usage = ask(CONTEXT + "\n\n" + role + "\n\n" + SCHEMA +
                             "\n\nEnvelope: authority=false, no_claim=true.")
            env = {"goblin": key, "raw": raw, "usage": usage,
                   "latency_s": round(time.time()-t0,1),
                   "authority": False, "no_claim": True, "proposal_only": True}
            (HERE / f"envelope_{key}.json").write_text(json.dumps(env, indent=2))
            print(f"{key}: {env['latency_s']}s ct={usage.get('completion_tokens')}")
        print("DONE_GOBLINS")
    finally:
        proc.terminate(); proc.wait(timeout=15)

if __name__ == "__main__":
    main()
