#!/usr/bin/env python3
"""
QWEN_GOBLIN_CHIDDUSH_SWARM_V0 — 10-min bounded Temple research swarm (Qwen-only).

8 independent goblin seats search for genuinely NEW distinctions (CHIDDUSH) implied by
the current HELEN architecture. Then a deterministic reducer dedups by semantic overlap
(swarm consensus is NOT evidence: N_agents↑ ⇏ N_evidence↑) and ranks.

HARD BOUNDARY: authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_INSTALL · NO_SUDO ·
NO_NETWORK_TARGETING · NO_EXTERNAL_ACTION · NO_LEDGER/REDUCER/CANON MUTATION · NO_GIT ·
local Qwen only · reduce without promoting.
"""
import json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRACE = ROOT / "chiddush_candidates.ndjson"
OLLAMA = "http://localhost:11434/api/chat"
QWEN = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"
BUDGET_S = int(sys.argv[1]) if len(sys.argv) > 1 else 570

CTX = ("HELEN = governed cognitive OS. Law: cognition ⇏ authority (ΔA=0); only a witnessed "
 "licensed transition Γ mutates governed state. Current architecture:\n"
 "• Constitutional identity = equivalence class [H]_P under protected predicates P; "
 "A_repr ⊆ A_lawful ⊆ M; well-definedness H1~H2 ⇒ m(H1)~m(H2) so m̄([H])=[m(H)]; "
 "lawful ≠ authorized; A_lawful is a monoid acting on H/~_P. Quotient algebra, NOT yet topology.\n"
 "• Capability topology: a tool arsenal = space of discriminators; N_tools ⇏ N_cap ⇏ N_epi; "
 "quotient by capability & provenance; tool output ≠ evidence (needs receipt).\n"
 "• AUTORESEARCH VNEXT: no consequential decision delta → no epoch; D+ ≁_A D-; local-first; "
 "falsifier memory; provenance root-census.\n"
 "• Provenance idempotence: N_repr ⇏ N_epi (evidence combines by union of roots).\n"
 "• WUL: color=projection(typed_state), P↛T.\n"
 "Anti-laws: cognition⇏authority · surface identity⇏constitutional identity · projection⇏state.")

FMT = ("Emit EXACTLY one candidate, no prose outside the template:\n"
 "OBSERVATION: <one line>\nDISTINCTION: <the new distinction>\n"
 "CHIDDUSH_CANDIDATE: <precise proposition, mathematical form if possible>\n"
 "WHY_NOT_IN_DOCTRINE: <one line — why not already contained above>\n"
 "FALSIFIER: <cheapest counterexample/test>\nCONSEQUENCE_IF_TRUE: <architectural consequence>\n"
 "NOVELTY: <0-5>\nFALSIFIABILITY: <0-5>\nLEVERAGE: <0-5>\n"
 "EVIDENCE_STATUS: <SPECULATIVE|DERIVED|LOCALLY_TESTABLE>\nEND")

GOBLINS = {
 "ALGEBRA":   "Find MISSING algebraic structure in HELEN's quotient transformation algebra: kernel ker(A), image, generators, relations, congruences, monoid/category structure.",
 "FALSIFIER": "ACTIVELY try to construct a concrete counterexample: some protected set P and mutation m with H1~_P H2 but m(H1)≁_P m(H2) — breaking quotient well-definedness. One real witness beats 200 epochs praising the theory. If you can't, give the sharpest near-miss.",
 "RECEIPT":   "Ask whether proof-carrying transitions need STRONGER witness structure than current receipts. What can a receipt still hide?",
 "SWARM":     "Study whether many authority-0 workers create EMERGENT risk invisible worker-by-worker (0_A+...+0_A = 0_A — attack this).",
 "WUL":       "Find higher-dimensional agent-to-agent packet representations that reduce ambiguity vs prose, staying P↛T (presentation ⇏ typed state).",
 "CAPABILITY":"Treat the capability arsenal ONLY as a typed discriminator space (no operationalization). What mathematical structure does its capability graph induce?",
 "VNEXT":     "Find a BETTER experiment-selection objective than LexMax(IG_class, -cost): expected falsification value, discriminative gain, trust-surface growth. Attack 'D+ ≁_A D-'.",
 "WEIRD":     "Search mathematics/distributed-systems/biology/information-theory/PL/control-theory for a NON-OBVIOUS structural analogy to HELEN's quotient constitution. Analogy = hypothesis, never evidence.",
}


def ollama(sysp, user, timeout=200):
    body = json.dumps({"model": QWEN, "stream": False, "think": False, "keep_alive": "10m",
        "messages": [{"role": "system", "content": sysp}, {"role": "user", "content": user}],
        "options": {"temperature": 0.9, "num_predict": 380, "top_p": 0.95}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: d = json.loads(r.read())
    m = d.get("message", {}) or {}
    return (m.get("content") or m.get("thinking") or "").strip()

def field(t, k):
    m = re.search(rf"^{k}:\s*(.+?)\s*$", t, re.I | re.M); return m.group(1).strip() if m else ""
def ival(t, k):
    v = field(t, k); m = re.search(r"\d", v); return int(m.group()) if m else 0


def main():
    print("═"*64); print(f"  QWEN_GOBLIN_CHIDDUSH_SWARM_V0 · budget {BUDGET_S}s · 8 seats · ΔA=0")
    print("═"*64, flush=True)
    if TRACE.exists(): TRACE.rename(TRACE.with_suffix(".ndjson.bak"))
    tr = []
    t0 = time.time(); rnd = 0
    while time.time() - t0 < BUDGET_S:
        rnd += 1
        for name, focus in GOBLINS.items():
            if time.time() - t0 >= BUDGET_S: break
            sysp = ("You are a HELEN Temple research GOBLIN. authority=0, ΔA=0, NO_CLAIM. "
                    "Reject paraphrase of existing doctrine, poetic renaming, generic multi-agent "
                    "advice, unsupported facts. A CHIDDUSH = new distinction + counterexample + cheap "
                    "falsifier.\n\nHELEN CONTEXT:\n" + CTX + "\n\nYOUR FOCUS: " + focus)
            try: raw = ollama(sysp, FMT)
            except Exception as e: raw = f"__ERR__ {str(e)[:60]}"
            c = {"round": rnd, "seat": name, "t": round(time.time()-t0,1),
                 "observation": field(raw,"OBSERVATION"), "distinction": field(raw,"DISTINCTION"),
                 "chiddush": field(raw,"CHIDDUSH_CANDIDATE"), "why_new": field(raw,"WHY_NOT_IN_DOCTRINE"),
                 "falsifier": field(raw,"FALSIFIER"), "consequence": field(raw,"CONSEQUENCE_IF_TRUE"),
                 "novelty": ival(raw,"NOVELTY"), "falsifiability": ival(raw,"FALSIFIABILITY"),
                 "leverage": ival(raw,"LEVERAGE"), "evidence": field(raw,"EVIDENCE_STATUS") or "SPECULATIVE",
                 "raw": raw}
            tr.append(c)
            with open(TRACE, "a") as f: f.write(json.dumps(c, ensure_ascii=False)+"\n")
            print(f"  r{rnd} {name:11s} [{c['t']}s] nov{c['novelty']} fals{c['falsifiability']} "
                  f"lev{c['leverage']} · {c['chiddush'][:52]}", flush=True)

    # ---- deterministic reduce (dedup by token-overlap; consensus ≠ evidence) ----
    def toks(s): return set(re.sub(r"[^a-z0-9 ]"," ",s.lower()).split())
    reps = []
    for c in tr:
        if not c["chiddush"]: continue
        k = toks(c["chiddush"]+" "+c["distinction"])
        dup = None
        for r in reps:
            j = len(k & r["_k"]) / max(1, len(k | r["_k"]))
            if j > 0.55: dup = r; break
        if dup: dup["_consensus"] += 1
        else: c["_k"] = k; c["_consensus"] = 1; c["_score"] = c["novelty"]+c["falsifiability"]+c["leverage"]; reps.append(c)
    reps.sort(key=lambda c: -c["_score"])
    top10 = reps[:10]
    killed = [c["chiddush"][:90] for c in reps if c["_score"] <= 3 or c["novelty"] <= 1][:12]
    unresolved = [c["chiddush"][:90] for c in reps if c["evidence"]=="SPECULATIVE" and c["leverage"]>=4][:8]
    # one best experiment: max falsifiability*leverage (cheap = LOCALLY_TESTABLE preferred)
    best = max(reps, key=lambda c: c["falsifiability"]*c["leverage"] + (2 if c["evidence"]=="LOCALLY_TESTABLE" else 0), default=None)

    out = {"experiment": "QWEN_GOBLIN_CHIDDUSH_SWARM_V0", "authority": False, "canon": False,
           "claim": "NO_CLAIM", "authority_delta": 0, "duration_s": round(time.time()-t0,1),
           "rounds": rnd, "raw_candidates": len(tr), "deduped_candidates": len(reps),
           "consensus_note": "N_agents↑ ⇏ N_evidence↑ — clusters counted once",
           "top10": [{k:c[k] for k in ("seat","chiddush","why_new","falsifier","consequence",
                      "novelty","falsifiability","leverage","evidence","_consensus","_score")} for c in top10],
           "killed_ideas": killed, "unresolved": unresolved,
           "one_best_experiment": ({k:best[k] for k in ("seat","chiddush","falsifier","evidence",
                      "falsifiability","leverage")} if best else None),
           "receipt": {"claims_admitted": 0, "external_actions": 0, "governed_state_mutations": 0,
                       "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}}
    (ROOT / "REDUCED_CHIDDUSH.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("─"*64); print(f"  reduced {len(tr)} raw → {len(reps)} distinct · top10 written · ΔA=0 · NO_COMMIT")
    print("  → REDUCED_CHIDDUSH.json")


if __name__ == "__main__":
    main()
