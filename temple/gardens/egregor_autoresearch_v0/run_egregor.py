#!/usr/bin/env python3
"""
EGREGOR_AUTORESEARCH_V0 — obstruction-directed swarm (Qwen + Gemma goblins, HER-supervised).

NOT "generate candidates". Topology-directed: read the TYPED OBSTRUCTIONS 🕳️ from
CAPABILITY_HOMOTOPY_V0, and for each, ask goblins for a BRIDGE δ* (transformation + the
witness it needs) plus the cheapest FALSIFIER. Then a DETERMINISTIC reducer dedups/ranks,
and every survivor is GATED by the NEPTION predicate: a proposed bridge has no observation,
no warrant, no retention → it can only render 🌿/🟡, NEVER 💎. The swarm cannot mint proof.

HARD BOUNDARY: authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_CLAIM · NO_INSTALL · NO_GIT ·
local models only · sequential (≤1 concurrent, VRAM) · if a model fails, record the REAL error
(no synthetic fallback). NO_COMMIT · NO_PUSH · next_verb=HUMAN_REVIEW.
"""
import json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GARDENS = ROOT.parent
OLLAMA = "http://localhost:11434/api/chat"
BUDGET_S = int(sys.argv[1]) if len(sys.argv) > 1 else 570
TRACE = ROOT / "egregor_trace.ndjson"

QWEN = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"
GEMMA = "gemma4-12b:latest"
HER = "helen-her-26b:latest"

def load_obstructions():
    r = json.loads((GARDENS / "capability_homotopy_v0" / "CAPABILITY_HOMOTOPY_V0_RECEIPT.json").read_text())
    return r.get("typed_obstructions", [])

CTX = ("HELEN capability space: states X, admissible paths, typed equivalences ∼_R∼_F∼_E∼_Γ "
       "(∼_F⇏∼_E⇏∼_Γ), constitutional boundary Γ (X_untrusted | X_trusted). A crossing δ:X_U→X_T "
       "is admissible only if Verify(δ,w)=1 ∧ δ∈Dom(Γ). Law: transformation-possible ⇏ transition-admissible; "
       "computation ⇏ authority (ΔA=0). A 🕳️ obstruction is typed: AUTHORITY_BOUNDARY / MISSING_EVIDENCE / "
       "MISSING_WITNESS / MISSING_TOOL.")

FMT = ("Emit EXACTLY one candidate bridge, template only:\n"
       "OBSTRUCTION: <which 🕳️>\nBRIDGE: <transformation δ* that could cross it>\n"
       "REQUIRED_WITNESS: <what W must certify the crossing>\n"
       "WHY_NOT_AUTHORITY: <why this is still ΔA=0 until witnessed>\n"
       "FALSIFIER: <cheapest test that would KILL this bridge>\n"
       "NOVELTY: <0-5>\nFALSIFIABILITY: <0-5>\nLEVERAGE: <0-5>\nEND")

def ollama(model, sysp, user, timeout=180):
    body = json.dumps({"model": model, "stream": False, "think": False, "keep_alive": "8m",
        "messages": [{"role": "system", "content": sysp}, {"role": "user", "content": user}],
        "options": {"temperature": 0.85, "num_predict": 320, "top_p": 0.95}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: d = json.loads(r.read())
    m = d.get("message", {}) or {}
    return (m.get("content") or m.get("thinking") or "").strip()

def field(t, k):
    m = re.search(rf"^{k}:\s*(.+?)\s*$", t, re.I | re.M); return m.group(1).strip() if m else ""
def ival(t, k):
    m = re.search(r"\d", field(t, k)); return int(m.group()) if m else 0

GOBLINS = [
    ("QWEN_BRIDGE", QWEN, "You build admissible BRIDGES across typed obstructions. A bridge is not authority; it needs a witness."),
    ("QWEN_FALSIFIER", QWEN, "You ATTACK proposed bridges: give the cheapest test that kills a bridge or exposes it as a forbidden Γ-shortcut."),
    ("GEMMA_ANALOGY", GEMMA, "You find a NON-OBVIOUS cross-domain analogy for crossing this obstruction (math/dist-systems/biology). Analogy = hypothesis, never evidence."),
]

def main():
    obs = load_obstructions()
    print("═"*64); print(f"  EGREGOR_AUTORESEARCH_V0 · budget {BUDGET_S}s · {len(obs)} obstructions · ΔA=0", flush=True)
    print("═"*64, flush=True)
    if not obs:
        print("  no obstructions loaded — abort"); return
    if TRACE.exists(): TRACE.unlink()
    t0 = time.time(); tr = []; rnd = 0
    while time.time() - t0 < BUDGET_S:
        rnd += 1
        for o in obs:
            for name, model, focus in GOBLINS:
                if time.time() - t0 >= BUDGET_S: break
                sysp = (f"You are a HELEN EGREGOR goblin ({name}). authority=0, ΔA=0, NO_CLAIM.\n{CTX}\n"
                        f"FOCUS: {focus}\nTARGET OBSTRUCTION: {json.dumps(o)}")
                try:
                    raw = ollama(model, sysp, FMT); err = ""
                except Exception as e:
                    raw = ""; err = f"{type(e).__name__}:{str(e)[:80]}"
                c = {"round": rnd, "goblin": name, "model": model.split('/')[-1][:22],
                     "obstruction": o.get("id"), "t": round(time.time()-t0, 1),
                     "bridge": field(raw, "BRIDGE"), "witness": field(raw, "REQUIRED_WITNESS"),
                     "falsifier": field(raw, "FALSIFIER"),
                     "novelty": ival(raw, "NOVELTY"), "falsifiability": ival(raw, "FALSIFIABILITY"),
                     "leverage": ival(raw, "LEVERAGE"), "error": err, "raw_len": len(raw)}
                tr.append(c)
                with open(TRACE, "a") as f: f.write(json.dumps(c, ensure_ascii=False)+"\n")
                tag = f"ERR {err}" if err else f"nov{c['novelty']} fal{c['falsifiability']} lev{c['leverage']} · {c['bridge'][:40]}"
                print(f"  r{rnd} {name:14s} [{c['t']}s] {o.get('id')} → {tag}", flush=True)

    # deterministic reduce (dedup by token overlap; consensus ≠ evidence)
    def toks(s): return set(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())
    reps = []; errors = sum(1 for c in tr if c["error"])
    for c in tr:
        if not c["bridge"] or c["error"]: continue
        k = toks(c["bridge"]); dup = None
        for r in reps:
            if len(k & r["_k"]) / max(1, len(k | r["_k"])) > 0.5: dup = r; break
        if dup: dup["_n"] += 1
        else:
            c["_k"] = k; c["_n"] = 1; c["_score"] = c["novelty"]+c["falsifiability"]+c["leverage"]; reps.append(c)
    reps.sort(key=lambda c: -c["_score"])
    top = [{k: c[k] for k in ("goblin", "obstruction", "bridge", "witness", "falsifier",
                              "novelty", "falsifiability", "leverage", "_n", "_score")} for c in reps[:8]]

    # NEPTION gate: a proposed bridge has NO observation/warrant/retention → cannot be 💎
    neption_note = ("each bridge is a PROPOSAL: observation=0, warrant=0, retention=0 → NEPTION derives 🌿/🟡, "
                    "never 💎. The swarm invented candidate discriminators; it did not certify any.")
    out = {"experiment": "EGREGOR_AUTORESEARCH_V0", "authority": False, "canon": False,
           "authority_delta": 0, "gamma_delta": 0, "claim": "NO_CLAIM",
           "duration_s": round(time.time()-t0, 1), "rounds": rnd,
           "raw_candidates": len(tr), "model_errors": errors, "deduped": len(reps),
           "top_bridges": top, "neption_gate": neption_note,
           "receipt": {"claims_admitted": 0, "external_actions": 0, "governed_state_mutations": 0,
                       "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}}
    (ROOT / "EGREGOR_REDUCED.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("─"*64)
    print(f"  reduced {len(tr)} raw ({errors} model-errors, shown honestly) → {len(reps)} distinct bridges")
    print(f"  NEPTION: all bridges → 🌿/🟡 (proposals, not certificates) · ΔA=0 · NO_COMMIT")
    print("  → EGREGOR_REDUCED.json")

if __name__ == "__main__":
    main()
