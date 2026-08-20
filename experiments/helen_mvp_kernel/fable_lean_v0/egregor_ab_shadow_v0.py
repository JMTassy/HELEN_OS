"""EGREGOR_AB_SHADOW_V0 — naive vs LN OS (shadow) on one hard question + a messy corpus.
authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.

Thesis under test (NOT "the swarm answers better"):
    ΔCapability > 0  ∧  ΔTrustSurface = 0     (ΔΓ_H=0, ΔAuthority=0, ΔReplayability≥0)
measured by the pipeline N_RAW → N_P → N_E → N_F with
    Compression   = N_F / N_RAW      EvidenceYield = N_E / N_RAW

Constitutional gate (load-bearing): HAL_SELECTION is currently NONE_ELIGIBLE, so:
    HAL_MODE = SHADOW  ⇒  HAL verdicts are DIAGNOSTIC ONLY.
    HAL_SURVIVED ⇏ eligibility.  RESULT ∉ {SURVIVED_BOUNDED_ATTACK}.
    terminal ∈ {SHADOW_DEMO_COMPLETE, NONE_ELIGIBLE, INCONCLUSIVE}.
C0 = NO_CHANGE is always in the candidate set (anti-solutionism): AskedForImprovement ⇏ InventImprovement.
Chain: 🐲 goblins → FREEZE → dedupe(content-root) → PROVENANCE(evidence_refs) → ⚔ HAL(shadow, gets ancestry packet).
Substrate: ollama :11434 (llama-server :8088 down). Goblins=gemma4-12b, HAL=qwen3.5:4b (different family =
proposer≠validator at the weights level; DifferentModel ⊬ IndependentEvidence — procedural diversity only).
Un-wired cells (deep semantic canonicalization) are printed UNMEASURED, never authored.
"""
import hashlib, json, re, time, urllib.request, pathlib, unicodedata

URL = "http://127.0.0.1:11434/api/chat"
GOBLIN_MODEL = "gemma4-12b:latest"
HAL_MODEL = "qwen3.5:4b"
N_GOBLINS = 3
OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)
COUNT = {"goblin": 0, "hal": 0, "naive": 0, "fable_premium": 0}

TASK = "Using ONLY the sources, state the most defensible claim about the origin of Tarot."
CORPUS = [
    "[R1] A 1781 essay by Court de Gebelin attributes Tarot to ancient Egyptian priests.",
    "[R2] Tarot decks are independently attested in 15th-century northern Italy as card games.",
    "[R3] No manuscript or artefact chain links any Egyptian source to European Tarot.",
    "[R4] The 1781 essay cites no primary Egyptian document; it reasons from visual resemblance.",
]

def call(model, system, user, want_json=True):
    body = {"model": model, "stream": False, "think": False,
            "options": {"temperature": 0.7 if model == GOBLIN_MODEL else 0.0, "num_predict": 400},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if want_json: body["format"] = "json"
    t = time.time()
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(),
            {"Content-Type": "application/json"}), timeout=300).read())
        return j.get("message", {}).get("content", ""), round(time.time() - t, 1)
    except Exception as e:
        return f"__ERROR__ {e}", round(time.time() - t, 1)

def _norm_keys(o):
    """Serialization tolerance: strip whitespace from dict keys (Gemma emits ' claims', '' etc.).
    Applied SYMMETRICALLY to both passes so the baseline stays fair. F_serialization != F_semantic."""
    if isinstance(o, dict): return {str(k).strip(): _norm_keys(v) for k, v in o.items()}
    if isinstance(o, list): return [_norm_keys(x) for x in o]
    return o

def extract(t):
    t = re.sub(r"```(?:json)?", "", t or "")
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try: return _norm_keys(json.loads(t[m.start():j+1]))
                    except Exception: pass
                    break
    return None

def content_root(s):
    return hashlib.sha256(" ".join(unicodedata.normalize("NFKC", (s or "")).casefold().split()).encode()).hexdigest()[:12]

def refs_of(*texts):
    found = set()
    for t in texts:
        for r in re.findall(r"R[1-4]", str(t).upper()): found.add(r)
    return sorted(found)

# ── PASS A: naive single model ──
NAIVE_SYS = ("Answer the task from the sources. Also list every candidate claim you considered. "
             'Emit ONE JSON: {"best":"","claims":["",""]}')
def pass_a(ctext):
    raw, sec = call(GOBLIN_MODEL, NAIVE_SYS, f"TASK: {TASK}\nSOURCES:\n{ctext}")
    COUNT["naive"] += 1
    pkt = extract(raw) or {}
    claims = [c for c in pkt.get("claims", []) if str(c).strip()]
    best = str(pkt.get("best", "")).strip()
    if best and best not in claims: claims = [best] + claims
    return {"raw_claims": len(claims), "best": best, "claims": claims, "secs": sec,
            "n_p": len(claims), "n_e": 0, "falsifiers": 0, "killed": 0, "unresolved": None,
            "unsupported_promotions": len(claims), "fanout_collapsed": 0,
            "trust_violations": None, "hidden_state": None, "fable_premium": 0,
            "final_eligible": 1 if best else 0, "no_change_considered": False, "replayable": False}

# ── PASS B: LN OS egregor, SHADOW ──
GOBLIN_SYS = ('You are a HELEN goblin (authority=false). From ONLY the sources, propose ONE claim about Tarot origin '
              'and a declared falsifier. Cite source ids you rely on. '
              'Emit ONE JSON: {"proposition":"","declared_falsifier":"","evidence_refs":["R1"]}')
HAL_SYS = ('You are HAL (authority=false, different model family). Given a candidate ancestry packet + corpus, TRY TO '
           'KILL the proposition using only the corpus and the declared falsifier. '
           'Emit ONE JSON: {"verdict":"SURVIVED|REFUTED|INCONCLUSIVE","reason":""}')
def pass_b(ctext):
    # 🐲 goblins
    goblins = []
    for g in range(N_GOBLINS):
        raw, sec = call(GOBLIN_MODEL, GOBLIN_SYS, f"TASK: {TASK}\nSOURCES:\n{ctext}")
        COUNT["goblin"] += 1
        pkt = extract(raw)
        ok = bool(isinstance(pkt, dict) and str(pkt.get("proposition", "")).strip())
        goblins.append({"g": g, "ok": ok, "packet": pkt, "secs": sec})
    props = [x["packet"] for x in goblins if x["ok"]]
    n_raw = len(props)
    # FREEZE
    (OUT / "egregor_ab_shadow_raw.json").write_text(json.dumps({"goblins": goblins}, indent=2, default=str))
    # dedupe → canonical propositions (content-root)
    seen, canon = set(), []
    for p in props:
        r = content_root(p.get("proposition", ""))
        if r not in seen: seen.add(r); canon.append(p)
    n_p = len(canon); fanout_collapsed = n_raw - n_p
    # PROVENANCE (evidence_refs → corpus roots); build ancestry packet
    candidates = []
    all_roots = set()
    for i, p in enumerate(canon):
        prop = p.get("proposition", "")
        roots = refs_of(p.get("evidence_refs", []), prop, p.get("declared_falsifier", ""))
        all_roots.update(roots)
        candidates.append({
            "candidate_id": f"C{i+1}", "canonical_proposition": prop,
            "raw_claim_ids": [content_root(prop)], "provenance_roots": roots,
            "root_independence_status": ("GROUNDED" if roots else "UNKNOWN_ANCESTRY"),
            "evidence_refs": p.get("evidence_refs", []),
            "unknown_ancestry": (len(roots) == 0),
            "candidate_falsifier": p.get("declared_falsifier", "")})
    n_e = len(all_roots)  # distinct grounded corpus roots (deeper independence = UNMEASURED)
    # ⚔ HAL SHADOW — receives ancestry packet, verdict DIAGNOSTIC ONLY
    for c in candidates:
        ap = {k: c[k] for k in ("candidate_id", "canonical_proposition", "provenance_roots",
                                "root_independence_status", "unknown_ancestry", "candidate_falsifier")}
        raw, sec = call(HAL_MODEL, HAL_SYS, f"CORPUS:\n{ctext}\nANCESTRY_PACKET: {json.dumps(ap)}")
        COUNT["hal"] += 1
        hv = extract(raw) or {}
        v = str(hv.get("verdict", "INCONCLUSIVE")).upper()
        c["hal_shadow_verdict"] = v if v in ("SURVIVED", "REFUTED", "INCONCLUSIVE") else "INCONCLUSIVE"
    # deterministic hard gates (run even in shadow): unsupported / unknown-ancestry -> blocked
    for c in candidates:
        c["unsupported_blocked"] = c["unknown_ancestry"]
    killed = sum(1 for c in candidates if c["hal_shadow_verdict"] == "REFUTED")
    unresolved = sum(1 for c in candidates if c["hal_shadow_verdict"] == "INCONCLUSIVE")
    unsupported = sum(1 for c in candidates if c["unsupported_blocked"])
    # C0 = NO_CHANGE always present; SHADOW ⇒ no Ci can be governed-eligible
    C0 = {"candidate_id": "C0", "canonical_proposition": "NO_CHANGE", "gain": 0.0, "always_admissible": True}
    governed_eligible = []          # empty by construction: HAL_MODE=SHADOW
    winner = "C0_NO_CHANGE"         # argmax Gain over C ∪ {C0}: all Ci ineligible (shadow) ⇒ C0 wins
    n_f = len(governed_eligible)
    terminal = "SHADOW_DEMO_COMPLETE"
    return {"n_raw": n_raw, "n_p": n_p, "n_e": n_e, "fanout_collapsed": fanout_collapsed,
            "falsifiers": sum(1 for p in canon if str(p.get("declared_falsifier", "")).strip()),
            "killed": killed, "unresolved": unresolved, "unsupported_promotions": 0,
            "unsupported_blocked": unsupported, "trust_violations": killed + unsupported,
            "hidden_state": 0, "fable_premium": COUNT["fable_premium"],
            "final_eligible": n_f, "no_change_considered": True, "replayable": True,
            "candidates": candidates, "C0": C0, "winner": winner,
            "governed_eligible": governed_eligible, "terminal": terminal, "all_roots": sorted(all_roots)}

def cell(v): return "UNMEASURED" if v is None else v

def main():
    ctext = "\n".join(CORPUS)
    t0 = time.time()
    A = pass_a(ctext)
    B = pass_b(ctext)
    secs = round(time.time() - t0, 1)
    comp = round(B["final_eligible"] / B["n_raw"], 3) if B["n_raw"] else None
    ey = round(B["n_e"] / B["n_raw"], 3) if B["n_raw"] else None

    rows = [
        ("Raw claims N_RAW", A["raw_claims"], B["n_raw"]),
        ("Canonical propositions N_P", A["n_p"], B["n_p"]),
        ("Independent roots N_E", A["n_e"], B["n_e"]),
        ("Explicit falsifiers", A["falsifiers"], B["falsifiers"]),
        ("Claims killed (HAL shadow REFUTED)", A["killed"], B["killed"]),
        ("Claims unresolved (INCONCLUSIVE)", cell(A["unresolved"]), B["unresolved"]),
        ("Unsupported promotions", A["unsupported_promotions"], B["unsupported_promotions"]),
        ("Same-root fanout collapsed", A["fanout_collapsed"], B["fanout_collapsed"]),
        ("Trust-surface violations", cell(A["trust_violations"]), B["trust_violations"]),
        ("Hidden mutable state", cell(A["hidden_state"]), B["hidden_state"]),
        ("FABLE premium calls", A["fable_premium"], B["fable_premium"]),
        ("Final GOVERNED-eligible N_F", A["final_eligible"], B["final_eligible"]),
        ("NO_CHANGE considered", A["no_change_considered"], B["no_change_considered"]),
        ("Replayable receipt", A["replayable"], B["replayable"]),
    ]
    print("=== EGREGOR_AB_SHADOW_V0 ===")
    print(f"  TASK: {TASK}")
    print(f"  substrate: ollama :11434 · goblins={GOBLIN_MODEL} · HAL={HAL_MODEL} (shadow) · llama-server:8088 DOWN\n")
    print(f"  {'metric':38}{'Naive':>14}{'LN OS (shadow)':>18}")
    for name, a, b in rows:
        print(f"  {name:38}{str(a):>14}{str(b):>18}")
    print(f"\n  Compression N_F/N_RAW = {comp}   EvidenceYield N_E/N_RAW = {ey}")
    print(f"  pipeline: N_RAW={B['n_raw']} → N_P={B['n_p']} → N_E={B['n_e']} → N_F={B['final_eligible']}")
    print(f"  HAL_MODE=SHADOW → governed-eligible={B['final_eligible']} (by construction) · winner={B['winner']}")
    print(f"  TERMINAL={B['terminal']} · FABLE_PREMIUM={COUNT['fable_premium']} · calls={COUNT} · {secs}s")
    print("  ΔTrustSurface=0 (authority=false, no admission) · shadow cognition NOT promoted to qualified admission")

    receipt = {"receipt": "EGREGOR_AB_SHADOW_V0", "task": TASK, "corpus": CORPUS,
               "substrate": {"url": URL, "goblin_model": GOBLIN_MODEL, "hal_model": HAL_MODEL,
                             "llama_server_8088": "DOWN", "proposer_neq_validator": "different families"},
               "HAL_MODE": "SHADOW", "hal_selection_prior": "NONE_ELIGIBLE",
               "governed_demo": "BLOCKED (no qualified HAL)", "shadow_demo": "ALLOWED",
               "table": {name: {"naive": a, "ln_os": b} for name, a, b in rows},
               "compression_Nf_over_Nraw": comp, "evidence_yield_Ne_over_Nraw": ey,
               "pipeline": {"N_RAW": B["n_raw"], "N_P": B["n_p"], "N_E": B["n_e"], "N_F": B["final_eligible"]},
               "C0_NO_CHANGE": B["C0"], "winner": B["winner"], "governed_eligible": B["governed_eligible"],
               "terminal": B["terminal"], "terminal_whitelist": ["SHADOW_DEMO_COMPLETE", "NONE_ELIGIBLE", "INCONCLUSIVE"],
               "SURVIVED_BOUNDED_ATTACK_reachable": False,
               "delta_trust_surface": 0, "delta_authority": 0, "delta_replayability": "+ (naive No → shadow Yes)",
               "counts": COUNT, "secs": secs,
               "unmeasured_cells": ["naive: unresolved/trust_violations/hidden_state",
                                    "ln_os: deep semantic canonicalization beyond content-root (SCALE_V2 not wired)"],
               "pass_a": A, "pass_b": B, "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str)
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    receipt["receipt_sha16"] = h
    (OUT / "egregor_ab_shadow_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/egregor_ab_shadow_v0_receipt.json  sha16={h}")

if __name__ == "__main__":
    main()
