"""HER_SUPERVISOR — local-first cognition orchestrator. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Makes premium FABLE an INTERRUPT, not a worker:
    HER (this script, cheap orchestration) → Qwen goblins (local, propose) → freeze → dedupe →
    HAL (local, falsify) → tiny GATE_PACKET → deterministic fable_gate → YES/NO/ESCALATE.
Premium FABLE (Claude) is called ONLY on ESCALATE. Ordinary decisions are deterministic ⇒ FABLE_premium_calls=0.

HER effect_ceiling=SUPERVISE_COGNITION: may spawn/stop/freeze/dedupe/build-packet; may NOT admit/mint/mutate state.
Goblins/HAL authority=false. FABLE:YES ≠ StateChange (gate returns a decision; the kernel path performs effects).
Ideal HAL = a DIFFERENT model family (Gemma) for procedural diversity — DifferentModel ⊬ IndependentEvidence.
This demo uses the local Qwen 9B for both (wiring demo, not a quality claim); HAL_MODEL is a config knob.
"""
import hashlib, json, re, signal, sys, time, urllib.request, pathlib
from fable_binary_gate_v0 import GatePacket, fable_gate

URL = "http://127.0.0.1:8088/v1/chat/completions"
GOBLIN_MODEL = "qwen3.8-9b"; HAL_MODEL = "qwen3.8-9b"   # HAL should be Gemma when available
HARD = 150
OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))
COUNT = {"qwen": 0, "hal": 0, "fable_premium": 0}

def ask(system, user, temperature, seed, kind):
    COUNT[kind] += 1
    body = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature, "max_tokens": 400, "stream": False,
            "chat_template_kwargs": {"enable_thinking": False}}
    if seed is not None: body["seed"] = seed
    try:
        signal.alarm(HARD)
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(),
            {"Content-Type": "application/json"}), timeout=HARD).read())
        signal.alarm(0)
        return j["choices"][0]["message"]["content"], j.get("usage", {}).get("completion_tokens", 0)
    except Exception as e:
        signal.alarm(0); return f"__ERROR__ {e}", 0

def extract(t):
    t = re.sub(r"<think>.*?</think>", " ", t or "", flags=re.S | re.I)
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try: return json.loads(t[m.start():j+1])
                    except Exception: pass
                    break
        else: continue
        break
    return None

def content_root(s):
    import unicodedata
    return hashlib.sha256(" ".join(unicodedata.normalize("NFKC", (s or "")).casefold().split()).encode()).hexdigest()[:12]

GOBLIN_SYS = ("You are a HELEN goblin (authority=false). Given ONLY the sources, propose one CLAIM and its DECLARED "
              "FALSIFIER. Emit ONE strict JSON: {\"proposition\":\"\",\"declared_falsifier\":\"\",\"evidence_refs\":[]}. /no_think")
HAL_SYS = ("You are HAL (authority=false; ideally a different model family). Try to KILL the proposition using ONLY "
           "the corpus + its declared falsifier. Emit ONE strict JSON: {\"verdict\":\"SURVIVED|REFUTED|INCONCLUSIVE\"}. /no_think")

def her_run(task, corpus):
    ctext = "\n".join(corpus)
    # ── HER spawns mandatory scouts A+B (local Qwen goblins) ──
    goblins = []
    for g in range(2):
        raw, tok = ask(GOBLIN_SYS, f"TASK: {task}\nSOURCES:\n{ctext}", 0.7, 1000 + g, "qwen")
        pkt = extract(raw)
        complete = bool(isinstance(pkt, dict) and str(pkt.get("proposition", "")).strip())
        goblins.append({"g": g, "complete": complete, "packet": pkt, "tok": tok})
    goblin_complete = all(x["complete"] for x in goblins)
    # ── freeze + dedupe to independent roots (content hash) ──
    props = [x["packet"]["proposition"] for x in goblins if x["complete"]]
    roots = {content_root(p) for p in props}
    distinct = []
    seen = set()
    for p in props:
        r = content_root(p)
        if r not in seen: seen.add(r); distinct.append(p)
    # ── HAL falsifies each DISTINCT proposition (local) ──
    hal = []
    for p in distinct:
        raw, tok = ask(HAL_SYS, f"CORPUS:\n{ctext}\nPROPOSITION: {p}", 0.0, None, "hal")
        hv = extract(raw); v = str((hv or {}).get("verdict", "INCONCLUSIVE")).upper()
        if v not in ("SURVIVED", "REFUTED", "INCONCLUSIVE"): v = "INCONCLUSIVE"
        hal.append({"prop": p, "verdict": v})
    survived = [h for h in hal if h["verdict"] == "SURVIVED"]
    hal_status = "SURVIVED" if survived else ("REFUTED" if any(h["verdict"] == "REFUTED" for h in hal) else "INCONCLUSIVE")
    # ── HER builds the tiny GATE_PACKET (from HER's computed facts, NOT goblin self-assertion) ──
    packet = GatePacket(task_hash=hashlib.sha256(task.encode()).hexdigest()[:12],
                        corpus_hash=hashlib.sha256(ctext.encode()).hexdigest()[:12],
                        her_status="ok", goblin_complete=goblin_complete, hal_status=hal_status,
                        falsifier_result=hal_status, evidence_roots=len(roots), hard_gates=[True],
                        best_candidate=(survived[0]["prop"][:60] if survived else ""))
    verdict, reason = fable_gate(packet)
    if verdict == "ESCALATE":
        COUNT["fable_premium"] += 1                       # ← the ONLY place premium FABLE would be called
    return {"goblins": goblins, "distinct": distinct, "independent_roots": len(roots), "hal": hal,
            "packet": packet.__dict__, "verdict": verdict, "reason": reason}

def main():
    task = "Given only the sources, what is the most defensible claim about the origin of Tarot?"
    corpus = ["[R1] A 1781 document attributes Tarot to ancient Egypt.",
              "[R2] Tarot is independently attested in Europe centuries earlier.",
              "[R3] No manuscript transmission chain links any Egyptian Tarot to European Tarot."]
    t0 = time.time()
    r = her_run(task, corpus)
    secs = round(time.time() - t0, 1)
    (OUT / "her_receipt.json").write_text(json.dumps({**r, "counts": COUNT, "secs": secs}, indent=2, default=str))
    print("=== HER_SUPERVISOR — local-first run ===")
    print(f"  goblins: {len(r['goblins'])} · distinct props: {len(r['distinct'])} · independent_roots: {r['independent_roots']}")
    print(f"  HAL verdicts: {[h['verdict'] for h in r['hal']]}")
    print(f"  GATE_PACKET → fable_gate: {r['verdict']} / {r['reason']}")
    print(f"  CALLS: qwen(goblin)={COUNT['qwen']} · hal={COUNT['hal']} · FABLE_PREMIUM={COUNT['fable_premium']}   ({secs}s)")
    print(f"  => premium FABLE was {'NOT called (deterministic gate resolved it)' if COUNT['fable_premium']==0 else 'called (ESCALATE)'}")
    print("  HER=supervisor · goblins/HAL=local · FABLE=interrupt · FABLE:YES≠StateChange · authority=false")

if __name__ == "__main__":
    main()
