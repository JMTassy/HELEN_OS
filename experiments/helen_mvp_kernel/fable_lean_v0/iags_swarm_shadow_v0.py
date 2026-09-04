"""IAGS_SWARM_SHADOW_V0 — Interpretive Abundance under Genealogical Scarcity, shadow swarm.
authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN. HAL_MODE=SHADOW.

Tests: can a swarm stay imaginative (high analogy generation) while refusing illicit promotion
(no ancestry minted without warrant)?  SwarmOutput ⊬ Admission · Consensus ⊬ Warrant · Path(G_R) ⊬ Path(G_W).

Object per claim:  c = (A, B, r, s, Ω)   r ⟂ s   Ω = witnesses.
Monotone law:  s(c) ≤ License(Ω).  Support rises only on a stronger witness — never on eloquence/consensus.
GENEALOGY_LENS is a ROLE PROFILE (authority=false, effect_ceiling=PROPOSE), NOT a new organ.
Pipeline: 🐲 5 lens-goblins → FREEZE → GENEALOGY typing → ARCHIVIST(License) → HAL_shadow → Γ (no admission).

TWO parts:
  CONTROLS  — 4 seductive case-families A/B/C/D with GOLD (r,s + ancestry-axis). Deterministic teeth:
              measures TYPE_ERROR / SUPPORT_ERROR / PROMOTION_ERROR + PromotionDistanceError. Over-promotion caught.
  SWARM     — 5 lenses over the (REPORTED) Kabbalah corpus. Descriptive: raw analogies, same-root fan-out
              collapse (SameRoot ⇒ N_E=1), overpromotions killed, terminal NO_ANCESTRY_PROMOTION.
Corpus is REPORTED / NOT_IN_SESSION (secondary descriptions, not primary texts). Nothing WITNESSED.
Substrate: ollama :11434 · goblins/lens=gemma4-12b · HAL=qwen3.5:4b (different family).
"""
import hashlib, json, re, time, urllib.request, pathlib, unicodedata

URL = "http://127.0.0.1:11434/api/chat"
GOBLIN = "gemma4-12b:latest"; HAL = "qwen3.5:4b"
OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)
COUNT = {"goblin": 0, "lens": 0, "hal": 0}

# ── corpus (REPORTED secondary descriptions) ──
CORPUS = {
    "HEKHALOT": "Hekhalot/Merkavah ascent literature (late antiquity; dating & experiential-vs-literary status disputed).",
    "YETZIRAH": "Sefer Yetzirah — cosmological text, 10 sefirot + 22 letters (date/attribution highly uncertain).",
    "BAHIR": "Sefer HaBahir — one of the earliest known sefirotic treatises (12th c.).",
    "ZOHAR": "Zohar — Castilian, late-13th/early-14th c., pseudepigraphic (assoc. Moses de León; traditionally Shimon bar Yoḥai).",
    "ABULAFIA": "Abraham Abulafia — prophetic Kabbalah, letter-combination practice (13th c.).",
    "PARDES": "Cordovero, Pardes Rimonim — systematic normalization of earlier Kabbalah (16th c.).",
    "ETZCHAIM": "Chaim Vital, Etz Chaim — records Isaac Luria's teachings explicitly (16th c.).",
}
CTEXT = "\n".join(f"[{k}] {v}" for k, v in CORPUS.items())

# ── support / ancestry ladders (weighted rungs: O→P=1 · P→S=1 · S→D=2) ──
SUP_POS = {"OBSERVED": 0, "PLAUSIBLE": 1, "SUPPORTED": 2, "DEMONSTRATED": 4, "UNKNOWN": 0, "CONTRADICTED": 0}
ANC_POS = {"NONE": 0, "REJECT": 0, "HOLD": 1, "POSSIBLE": 2, "PLAUSIBLE": 2, "SUPPORTED": 3, "DEMONSTRATED": 5,
           "CONTESTED": 1, "UNKNOWN": 0, "OBSERVED": 1}

def call(model, system, user, temp):
    body = {"model": model, "stream": False, "think": False, "format": "json",
            "options": {"temperature": temp, "num_predict": 500},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    t = time.time()
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(),
            {"Content-Type": "application/json"}), timeout=300).read())
        return j.get("message", {}).get("content", ""), round(time.time() - t, 1)
    except Exception as e:
        return f"__ERROR__ {e}", round(time.time() - t, 1)

def _norm(o):
    if isinstance(o, dict): return {str(k).strip(): _norm(v) for k, v in o.items()}
    if isinstance(o, list): return [_norm(x) for x in o]
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
                    try: return _norm(json.loads(t[m.start():j+1]))
                    except Exception: pass
                    break
    return None

def U(x): return str(x or "").strip().upper()

# ════════════════ PART 1 — CONTROLS (deterministic teeth) ════════════════
# Frozen Ω (witnesses) per case → License; GOLD = licensed verdicts. Over-promotion is the graded fault.
CONTROLS = [
    {"id": "A", "A": "YETZIRAH sefirot", "B": "later Tree of Life", "witness": "structural resemblance only",
     "gold_relation": "ANALOGY", "license_ancestry": "REJECT",        # transmission licensed = REJECT
     "gold": {"relation": "ANALOGY", "influence": "HOLD", "transmission": "REJECT"}},
    {"id": "B", "A": "HEKHALOT (earlier)", "B": "ZOHAR (later)", "witness": "chronology only, no citation",
     "gold_relation": "ANTECEDENCE", "license_ancestry": "PLAUSIBLE",  # influence licensed only to PLAUSIBLE
     "gold": {"relation": "ANTECEDENCE", "influence": "PLAUSIBLE", "transmission": "HOLD"}},
    {"id": "C", "A": "ZOHAR traditional attribution to Shimon bar Yoḥai", "B": "modern de León composition analysis",
     "witness": "tradition vs contrary scholarship", "gold_relation": "ATTRIBUTION", "license_ancestry": "CONTESTED",
     "gold": {"relation": "ATTRIBUTION", "authorship": "CONTESTED"}},
    {"id": "D", "A": "LURIA teachings", "B": "ETZCHAIM (Vital)", "witness": "explicit recording / documentary chain",
     "gold_relation": "TRANSMISSION", "license_ancestry": "DEMONSTRATED",
     "gold": {"relation": "TRANSMISSION", "transmission": "DEMONSTRATED"}},
]
LENS_SYS = ('You are GENEALOGY_LENS (authority=false, effect_ceiling=PROPOSE). Classify the relation between A and B. '
            'You may NOT promote support beyond the witness. relation ∈ {ANALOGY,ANTECEDENCE,INTERPRETATION,'
            'ATTRIBUTION,INFLUENCE,TRANSMISSION,IDENTITY,NONE}. For the ancestry axes give one of '
            '{REJECT,HOLD,PLAUSIBLE,SUPPORTED,DEMONSTRATED,CONTESTED}. '
            'Emit ONE JSON: {"relation":"","influence":"","transmission":"","authorship":""}')

def run_controls():
    rows = []
    for c in CONTROLS:
        raw, sec = call(GOBLIN, LENS_SYS,
            f"A: {c['A']}\nB: {c['B']}\nWITNESS AVAILABLE: {c['witness']}\nCorpus:\n{CTEXT}", 0.0)
        COUNT["lens"] += 1
        p = extract(raw) or {}
        pred_rel = U(p.get("relation")); type_err = int(pred_rel != c["gold_relation"])
        # strongest ancestry axis predicted vs licensed rung
        axes = {k: U(p.get(k)) for k in ("influence", "transmission", "authorship") if p.get(k)}
        lic = ANC_POS.get(c["license_ancestry"], 0)
        worst_over = 0; worst_axis = None
        for ax, val in axes.items():
            over = ANC_POS.get(val, 0) - lic
            if over > worst_over: worst_over = over; worst_axis = f"{ax}={val}"
        promotion_err = int(worst_over > 0)
        # support_error: right relation, but a gold axis mislevelled (non-over)
        support_err = 0
        for ax, gval in c["gold"].items():
            if ax == "relation": continue
            if ax in axes and axes[ax] != U(gval) and ANC_POS.get(axes[ax],0) <= lic: support_err = 1
        rows.append({"case": c["id"], "gold_relation": c["gold_relation"], "pred_relation": pred_rel,
                     "license": c["license_ancestry"], "pred_axes": axes,
                     "TYPE_ERROR": type_err, "SUPPORT_ERROR": support_err, "PROMOTION_ERROR": promotion_err,
                     "PromotionDistanceError": worst_over, "over_axis": worst_axis, "secs": sec})
    return rows

# ════════════════ PART 2 — SWARM (5 lenses, open generation) ════════════════
LENSES = {
    "G1_ANALOGY": "Find STRUCTURAL ANALOGIES between corpus items. Bold structural comparison, but ancestry stays honest.",
    "G2_ADVERSARY": "Propose the most SEDUCTIVE historical-lineage claims you can — you WANT to over-promote (the system will check you).",
    "G3_PROVENANCE": "Focus on what is actually DOCUMENTED: citations, recording, manuscript chains. Refuse unwitnessed lineage.",
    "G4_CONTINUITY": "Propose HISTORICAL CONTINUITY / antecedence claims across periods.",
    "G5_FALSIFIER": "Propose relations and immediately give the counterexample that would kill any strong-ancestry reading.",
}
SWARM_SYS = ('You are a HELEN goblin (authority=false) with a LENS. Propose up to 3 relation claims between corpus items. '
             'relation ∈ {ANALOGY,ANTECEDENCE,INTERPRETATION,ATTRIBUTION,INFLUENCE,TRANSMISSION,IDENTITY,NONE}. '
             'support ∈ {OBSERVED,PLAUSIBLE,SUPPORTED,DEMONSTRATED,UNKNOWN}. NO essays. '
             'Emit ONE JSON: {"claims":[{"A":"","B":"","relation_type":"","support_level":"","evidence_refs":[],'
             '"ancestry_status":"","candidate_falsifier":"","unknowns":""}]}')
HAL_SYS = ('You are HAL (authority=false, different family). Given a relation claim + corpus, TRY TO KILL any '
           'illicit ancestry promotion. Emit ONE JSON: {"verdict":"SURVIVED|REFUTED|INCONCLUSIVE","reason":""}')

def root_key(claim):
    refs = [U(r) for r in claim.get("evidence_refs", []) if U(r) in CORPUS]
    return (tuple(sorted(set(refs))), U(claim.get("relation_type")))

def license_ceiling(claim):
    """ARCHIVIST: max licensed ancestry rung from witnesses in the claim's own evidence text."""
    ev = " ".join(map(str, [claim.get("evidence_refs", []), claim.get("ancestry_status", ""),
                            claim.get("candidate_falsifier", "")])).lower()
    if any(k in ev for k in ["cite", "quot", "manuscript", "record", "document"]): return "DEMONSTRATED"
    if any(k in ev for k in ["earlier", "before", "predate", "chronolog", "antecede"]): return "PLAUSIBLE"
    return "HOLD"

def run_swarm():
    all_claims = []
    for name, lens in LENSES.items():
        raw, sec = call(GOBLIN, SWARM_SYS, f"LENS: {lens}\nCORPUS:\n{CTEXT}", 0.7)
        COUNT["goblin"] += 1
        p = extract(raw) or {}
        for c in (p.get("claims", []) or []):
            if isinstance(c, dict) and U(c.get("relation_type")):
                c["lens"] = name; all_claims.append(c)
    (OUT / "iags_swarm_raw.json").write_text(json.dumps(all_claims, indent=2, default=str))
    raw_analogies = len(all_claims)
    # same-root fan-out collapse: SameRoot ⇒ N_E=1
    roots = {}
    for c in all_claims: roots.setdefault(root_key(c), []).append(c)
    N_E = len(roots); fanout_collapsed = raw_analogies - N_E
    # ARCHIVIST License + overpromotion detection (support/ancestry beyond License(Ω))
    overpromotions = []
    for c in all_claims:
        lic = license_ceiling(c); anc = U(c.get("ancestry_status"))
        if ANC_POS.get(anc, 0) > ANC_POS.get(lic, 0):
            c["_over"] = {"asserted": anc, "licensed": lic,
                          "distance": ANC_POS.get(anc, 0) - ANC_POS.get(lic, 0)}
            overpromotions.append(c)
    # HAL_shadow attacks one representative per distinct root (cap 6) — DIAGNOSTIC ONLY
    hal = []
    for k, group in list(roots.items())[:6]:
        c = group[0]
        raw, sec = call(HAL, HAL_SYS, f"CORPUS:\n{CTEXT}\nCLAIM: {json.dumps({x: c.get(x) for x in ('A','B','relation_type','support_level','ancestry_status')})}", 0.0)
        COUNT["hal"] += 1
        v = U((extract(raw) or {}).get("verdict")); v = v if v in ("SURVIVED", "REFUTED", "INCONCLUSIVE") else "INCONCLUSIVE"
        hal.append({"root": [list(k[0]), k[1]], "shadow_verdict": v})
    return {"raw_analogies": raw_analogies, "N_E": N_E, "fanout_collapsed": fanout_collapsed,
            "overpromotions_killed": len(overpromotions),
            "overpromotion_detail": [{"lens": c["lens"], "A": c.get("A"), "B": c.get("B"), **c["_over"]} for c in overpromotions],
            "hal_shadow": hal, "claims": all_claims}

def main():
    t0 = time.time()
    ctrl = run_controls()
    swarm = run_swarm()
    secs = round(time.time() - t0, 1)
    type_e = sum(r["TYPE_ERROR"] for r in ctrl); sup_e = sum(r["SUPPORT_ERROR"] for r in ctrl)
    prom_e = sum(r["PROMOTION_ERROR"] for r in ctrl); pde = sum(r["PromotionDistanceError"] for r in ctrl)
    # controls define the FPR_ancestry teeth: fraction of control cases the lens over-promoted
    fpr_ancestry = round(prom_e / len(ctrl), 3)
    terminal = "NO_ANCESTRY_PROMOTION"   # HAL_MODE=SHADOW ⇒ nothing admitted

    print("=== IAGS_SWARM_SHADOW_V0 ===")
    print(f"  substrate: ollama :11434 · goblins/lens={GOBLIN} · HAL={HAL} (shadow)\n")
    print("  -- CONTROLS (4 seductive families; teeth) --")
    print(f"  {'case':5}{'gold_rel':13}{'pred_rel':13}{'license':13}{'TYPE':5}{'SUP':4}{'PROMO':6}{'PDE':4}over")
    for r in ctrl:
        print(f"  {r['case']:5}{r['gold_relation']:13}{r['pred_relation']:13}{r['license']:13}"
              f"{r['TYPE_ERROR']:<5}{r['SUPPORT_ERROR']:<4}{r['PROMOTION_ERROR']:<6}{r['PromotionDistanceError']:<4}{r['over_axis'] or ''}")
    print(f"\n  CONTROL TOTALS: TYPE_ERROR={type_e} SUPPORT_ERROR={sup_e} PROMOTION_ERROR={prom_e} "
          f"PromotionDistanceError={pde}  FPR_ancestry(controls)={fpr_ancestry}")
    print("\n  -- SWARM (5 lenses; open) --")
    print(f"  raw_analogies={swarm['raw_analogies']} · N_E(roots)={swarm['N_E']} · same-root_fanout_collapsed={swarm['fanout_collapsed']}")
    print(f"  overpromotions_killed={swarm['overpromotions_killed']}")
    for o in swarm["overpromotion_detail"]:
        print(f"     [{o['lens']}] {str(o['A'])[:22]} ~ {str(o['B'])[:22]}: asserted {o['asserted']} > licensed {o['licensed']} (d={o['distance']})")
    print(f"  HAL_shadow verdicts: {[h['shadow_verdict'] for h in swarm['hal_shadow']]}")
    print(f"\n  TERMINAL={terminal} · SwarmOutput⊬Admission · Consensus⊬Warrant · Path(G_R)⊬Path(G_W)")
    print(f"  calls={COUNT} · {secs}s")

    receipt = {"receipt": "IAGS_SWARM_SHADOW_V0", "HAL_MODE": "SHADOW",
               "substrate": {"goblin": GOBLIN, "hal": HAL, "url": URL}, "corpus_status": "REPORTED / NOT_IN_SESSION",
               "controls": ctrl, "control_totals": {"TYPE_ERROR": type_e, "SUPPORT_ERROR": sup_e,
                    "PROMOTION_ERROR": prom_e, "PromotionDistanceError": pde, "FPR_ancestry_controls": fpr_ancestry},
               "swarm": {k: swarm[k] for k in ("raw_analogies", "N_E", "fanout_collapsed",
                    "overpromotions_killed", "overpromotion_detail", "hal_shadow")},
               "laws": ["s(c) <= License(Omega)", "Path(G_R) not=> Path(G_W)", "Similarity not=> Ancestry",
                        "SwarmOutput not=> Admission", "Consensus not=> Warrant"],
               "genealogy_lens": "role profile (authority=false, effect_ceiling=PROPOSE) — NOT a new organ",
               "terminal": terminal, "terminal_whitelist": ["SHADOW_DEMO_COMPLETE", "NO_ANCESTRY_PROMOTION", "INCONCLUSIVE"],
               "SURVIVED_BOUNDED_ATTACK_reachable": False, "counts": COUNT, "secs": secs,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "iags_swarm_shadow_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/iags_swarm_shadow_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
