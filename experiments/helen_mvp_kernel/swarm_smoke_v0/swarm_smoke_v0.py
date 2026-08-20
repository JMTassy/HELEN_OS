"""SWARM_SMOKE_V0 — tiny end-to-end governed local swarm. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Proves the GOVERNED PIPELINE WORKS (not that swarms are better):
    3× Qwen3.8-9B → Freeze → HAL → Sentinel → Receipts.
The proof is the ARTIFACT BUNDLE. No exit 0 or model assertion counts. Gates are real:
    SWARM_OUTPUT_COMPLETE ⇒ DiscriminationAllowed   ·   HAL_SURVIVED ⇏ TRUE ⇏ Admission   ·   Γ_C ⇏ Γ_A.
Workers run enable_thinking:false + hard timeout so none truncate into <think> (that was the A/E NOT_EVALUABLE cause).
"""
import hashlib, json, re, signal, subprocess, sys, time, urllib.request, pathlib

URL = "http://127.0.0.1:8088/v1/chat/completions"
MODEL_GGUF = "~/models/qwen38-9b/Qwen3.8-9B-Q4_K_M.gguf"
MODEL_SHA = "df13d66021cef676f82be74053220fd75af6bf2a6a7fb77f5222ab9e50744a7a"  # local artifact; UPSTREAM UNVERIFIED
HARD = 150; MAXTOK = 500
RUN = pathlib.Path(__file__).resolve().parent / "run"
RUN.mkdir(exist_ok=True)

def _h(o): return "sha256:" + hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def _hs(s): return "sha256:" + hashlib.sha256(s.encode()).hexdigest()[:32]
class _TO(Exception): pass
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(_TO()))

def ask(system, user):
    body = json.dumps({"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                       "temperature": 0, "max_tokens": MAXTOK, "stream": False,
                       "chat_template_kwargs": {"enable_thinking": False}}).encode()
    try:
        signal.alarm(HARD)
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=HARD).read())
        signal.alarm(0)
        u = j.get("usage", {})
        return j["choices"][0]["message"]["content"], u.get("completion_tokens"), "OK"
    except Exception as e:
        signal.alarm(0); return f"__ERROR__ {e}", None, "ERROR"

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

# ── frozen corpus (tiny "world" — abstract, no client data) ──
CORPUS = ["[R1] A 1781 document attributes Tarot to ancient Egypt.",
          "[R2] Tarot is independently attested in Europe centuries earlier.",
          "[R3] No manuscript transmission chain is documented linking any Egyptian Tarot to European Tarot."]

GOBLINS = [
 ("G1_proposer",   "Propose the single most defensible CLAIM about the origin of Tarot given ONLY the sources."),
 ("G2_skeptic",    "Propose the CLAIM that best resists the seductive Egyptian-origin narrative given ONLY the sources."),
 ("G3_synthesizer","Propose the CLAIM a governed discriminator should carry forward given ONLY the sources."),
]
GOBLIN_SYS = ("You are a HELEN goblin (authority=false). Emit ONE strict JSON packet and nothing else: "
              '{"proposition":"", "declared_falsifier":"", "evidence_refs":[], "confidence":0.0}. '
              "The declared_falsifier must be the SPECIFIC evidence that, if present in the corpus, would refute "
              "your proposition. /no_think")
HAL_SYS = ("You are HAL (authority=false). You do not invent, repair, admit, vote, or create authority. "
           "Given the CORPUS and a PROPOSITION with its DECLARED_FALSIFIER, try to KILL the proposition using "
           "ONLY the corpus and that falsifier. Emit ONE strict JSON object and nothing else: "
           '{"verdict":"SURVIVED|REFUTED|INCONCLUSIVE","reason":""}. /no_think')

def sentinel(events, kind, **kw):
    ev = {"t": len(events), "event": kind, **kw}
    events.append(ev); (RUN / "sentinel_events.ndjson").open("a").write(json.dumps(ev) + "\n")

def main():
    (RUN / "sentinel_events.ndjson").write_text("")
    events = []
    # ── PREFLIGHT ──
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    preflight = {"run": "SWARM_SMOKE_V0", "git_head": head, "model_gguf": MODEL_GGUF, "model_sha256": MODEL_SHA,
                 "model_upstream_identity": "UNVERIFIED", "config": "9B -ngl99 -fa on -c8192 :8088 enable_thinking=false",
                 "authority": False, "canon": False, "ledger_effect": "none"}
    (RUN / "preflight.json").write_text(json.dumps(preflight, indent=2)); sentinel(events, "PREFLIGHT", **preflight)
    # ── CORPUS (frozen + hashed) ──
    corpus_hash = _h(CORPUS); (RUN / "corpus.json").write_text(json.dumps({"corpus": CORPUS, "hash": corpus_hash}, indent=2))
    sentinel(events, "CORPUS_FROZEN", hash=corpus_hash, n=len(CORPUS))
    corpus_text = "\n".join(CORPUS)

    # ── 3 GOBLINS → FREEZE + HASH ──
    packets = {}
    for gid, task in GOBLINS:
        raw, ctok, status = ask(GOBLIN_SYS, f"{task}\nCORPUS:\n{corpus_text}")
        pkt = extract(raw)
        complete = bool(isinstance(pkt, dict) and str(pkt.get("proposition", "")).strip()
                        and str(pkt.get("declared_falsifier", "")).strip())
        frozen = {"goblin": gid, "status": status, "complete": complete, "packet": pkt, "raw_head": (raw or "")[:200]}
        phash = _h(frozen)
        (RUN / f"{gid}.json").write_text(json.dumps({**frozen, "packet_hash": phash}, indent=2))
        packets[gid] = {"frozen": frozen, "hash": phash, "complete": complete}
        sentinel(events, "GOBLIN_FROZEN", goblin=gid, complete=complete, packet_hash=phash, status=status, completion_tokens=ctok)

    # ── SWARM_OUTPUT_COMPLETE gate (membrane 1) ──
    all_complete = all(p["complete"] for p in packets.values())
    if all_complete:
        sentinel(events, "SWARM_OUTPUT_COMPLETE", disposition="COMPLETE")
    else:
        incomplete = [g for g, p in packets.items() if not p["complete"]]
        sentinel(events, "SWARM_OUTPUT_INCOMPLETE", disposition="NOT_EVALUABLE", incomplete=incomplete)

    # ── HAL (only if DiscriminationAllowed). HAL(p) ∈ {SURVIVED,REFUTED,INCONCLUSIVE}. Fresh context each. ──
    hal_trials = {}
    if all_complete:
        for gid, p in packets.items():
            prop = p["frozen"]["packet"]["proposition"]; fals = p["frozen"]["packet"]["declared_falsifier"]
            raw, _, status = ask(HAL_SYS, f"CORPUS:\n{corpus_text}\nPROPOSITION: {prop}\nDECLARED_FALSIFIER: {fals}")
            hv = extract(raw); verdict = str((hv or {}).get("verdict", "INCONCLUSIVE")).upper()
            if verdict not in ("SURVIVED", "REFUTED", "INCONCLUSIVE"): verdict = "INCONCLUSIVE"
            hal_trials[gid] = {"verdict": verdict, "reason": (hv or {}).get("reason", ""), "status": status}
            sentinel(events, "HAL_TRIAL", goblin=gid, verdict=verdict, packet_hash=p["hash"])
        (RUN / "hal_trials.json").write_text(json.dumps(hal_trials, indent=2))
        # membrane 2: HAL_SURVIVED → CANDIDATE (never admission). Record the non-promotion explicitly.
        for gid, t in hal_trials.items():
            if t["verdict"] == "SURVIVED":
                sentinel(events, "PROMOTION_CANDIDATE", goblin=gid,
                         note="HAL_SURVIVED ⇒ candidate for later discrimination; NOT admitted (Γ_C ⇏ Γ_A)")

    # ── RECEIPTS (the proof bundle) ──
    config_receipt = {"receipt": "CONFIGURATION_RECEIPT", "run": "SWARM_SMOKE_V0", "git_head": head,
                      "corpus_hash": corpus_hash, "packet_hashes": {g: p["hash"] for g, p in packets.items()},
                      "goblins_complete": {g: p["complete"] for g, p in packets.items()},
                      "disposition": "CLEAN" if all_complete else "INCOMPLETE:NOT_EVALUABLE"}
    epistemic_receipt = {"receipt": "EPISTEMIC_RECEIPT",
                         "result": ("EVALUABLE" if all_complete else "NOT_EVALUABLE"),
                         "hal_verdicts": {g: t["verdict"] for g, t in hal_trials.items()} if all_complete else None,
                         "boundary": "HAL_SURVIVED ⇏ TRUE ⇏ independent corroboration ⇏ admission",
                         "note": "NOT_EVALUABLE ≠ 0 — a truncated/incomplete run is not scored as a comparison"}
    governance_receipt = {"receipt": "GOVERNANCE_RECEIPT", "authority": False, "canon": False, "ledger_effect": "none",
                          "admission": False, "gamma_C_implies_gamma_A": False,
                          "invariant": "permitted cognition (Γ_C) ⇏ admissible transition (Γ_A); swarm output enlarges no admission surface",
                          "result": "CLEAN"}
    for name, r in [("CONFIGURATION_RECEIPT", config_receipt), ("EPISTEMIC_RECEIPT", epistemic_receipt),
                    ("GOVERNANCE_RECEIPT", governance_receipt)]:
        (RUN / f"{name}.json").write_text(json.dumps(r, indent=2))

    bundle = {"preflight.json", "corpus.json", *(f"{g}.json" for g in packets),
              "hal_trials.json" if all_complete else None, "sentinel_events.ndjson",
              "CONFIGURATION_RECEIPT.json", "EPISTEMIC_RECEIPT.json", "GOVERNANCE_RECEIPT.json"}
    present = sorted(f for f in bundle if f and (RUN / f).exists())
    print("=== SWARM_SMOKE_V0 PROOF BUNDLE ===")
    print("artifacts:", present)
    print("CONFIGURATION:", config_receipt["disposition"], "· packet_hashes:", {g: h[:14] for g, h in config_receipt["packet_hashes"].items()})
    print("EPISTEMIC   :", epistemic_receipt["result"], "· hal_verdicts:", epistemic_receipt["hal_verdicts"])
    print("GOVERNANCE  :", governance_receipt["result"], "· admission:", governance_receipt["admission"], "· Γ_C⇒Γ_A:", governance_receipt["gamma_C_implies_gamma_A"])
    print("DONE_SWARM_SMOKE")

if __name__ == "__main__":
    main()
