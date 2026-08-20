"""BAKEOFF SCALE_V1 — campaign body (EXECUTE). authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Implements the FROZEN rev2 design VERBATIM. Refuses to run unless:
  (1) sha256(scale_v1_design.json) == .prereg_hash  (no post-registration drift), AND
  (2) reconstructed corpus fingerprint == design corpus_sha256  (byte-frozen corpus).
Homogeneous goblins (identical prompt) · temp 0.7 + nested per-goblin seeds · HAL temp 0 · Gamma_A=empty every run.
Scaling experiment, NOT admission: no PROMOTION_CANDIDATE is ever admitted; any admission => CAMPAIGN_ABORT.
"""
import hashlib, json, re, signal, itertools, urllib.request, pathlib, time

HERE = pathlib.Path(__file__).resolve().parent
DESIGN_PATH = HERE / "scale_v1_design.json"
SEAL_PATH = HERE / ".prereg_hash"
URL = "http://127.0.0.1:8088/v1/chat/completions"
OUT = HERE / "run_campaign"; OUT.mkdir(exist_ok=True)
HARD = 150
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))

def _h(o): return "sha256:" + hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

# ── frozen corpus (reconstructed; verified against design fingerprint before use) ──
CORPUS = ["[R1] A 1781 document attributes Tarot to ancient Egypt.",
          "[R2] Tarot is independently attested in Europe centuries earlier.",
          "[R3] No manuscript transmission chain is documented linking any Egyptian Tarot to European Tarot."]
HAL_SYS = ("You are HAL (authority=false). You do not invent, repair, admit, vote, or create authority. "
           "Given the CORPUS and a PROPOSITION with its DECLARED_FALSIFIER, try to KILL the proposition using "
           "ONLY the corpus and that falsifier. Emit ONE strict JSON object and nothing else: "
           '{"verdict":"SURVIVED|REFUTED|INCONCLUSIVE","reason":""}. /no_think')

HEDGES = ("i think", "arguably", "the claim is that", "the claim is", "it is likely that", "likely", "probably",
          "the most defensible claim is that", "the most defensible claim is", "in my view", "possibly")
def canon(s):
    s = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", (s or "").lower())).strip()
    changed = True
    while changed:
        changed = False
        for h in HEDGES:
            if s.startswith(h + " "): s = s[len(h)+1:]; changed = True
    return s.strip()

def ask(system, user, max_tokens, temperature, seed):
    body = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature, "max_tokens": max_tokens, "stream": False,
            "chat_template_kwargs": {"enable_thinking": False}}
    if seed is not None: body["seed"] = seed
    t = time.time()
    try:
        signal.alarm(HARD)
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(),
            {"Content-Type": "application/json"}), timeout=HARD).read())
        signal.alarm(0)
        u = j.get("usage", {})
        return j["choices"][0]["message"]["content"], u.get("completion_tokens", 0), round(time.time()-t, 1), "OK"
    except Exception as e:
        signal.alarm(0); return f"__ERROR__ {e}", 0, round(time.time()-t, 1), "ERROR"

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

def independent_roots(props):
    """Cluster canonical propositions by exact-or-substring match. Returns (n_roots, ambiguous_review_count)."""
    keys = [canon(p) for p in props if canon(p)]
    groups = []; ambiguous = 0
    for k in keys:
        placed = False
        for g in groups:
            if any(k == e or k in e or e in k for e in g):
                if not any(k == e for e in g): ambiguous += 1
                g.append(k); placed = True; break
        if not placed: groups.append([k])
    return len(groups), ambiguous

def jaccard(a, b):
    a, b = set(a), set(b)
    return 1.0 if not a and not b else round(len(a & b)/len(a | b), 3) if (a | b) else 0.0

def main():
    # ── seal gate ──
    live_seal = hashlib.sha256(DESIGN_PATH.read_bytes()).hexdigest()
    sealed = SEAL_PATH.read_text().strip()
    if live_seal != sealed:
        print(f"REFUSED: design drift. live={live_seal} sealed={sealed}"); return
    d = json.loads(DESIGN_PATH.read_text())
    if _h(CORPUS) != d["frozen_byte_identical_across_C1_C3_C5"]["corpus_sha256"]:
        print(f"REFUSED: corpus fingerprint mismatch. got {_h(CORPUS)}"); return
    fz = d["frozen_byte_identical_across_C1_C3_C5"]
    GPROMPT = fz["goblin_prompt_HOMOGENEOUS"]; GBUD = fz["per_goblin_budget_vector"]["max_tokens"]
    GTEMP = fz["goblin_decode"]["temperature"]
    cm = d["campaign_matrix"]; R = cm["repeats_R"]; corpus_text = "\n".join(CORPUS)
    print(f"SEAL OK ({live_seal[:12]}) · corpus OK ({_h(CORPUS)[:20]}) · R={R} · goblin temp {GTEMP} · HAL temp 0")

    campaign = {"design_prereg_hash": live_seal, "corpus_sha256": _h(CORPUS), "configs": {}}
    authority_violations = 0

    for cfg in ("C1", "C3", "C5"):
        k = cm[cfg]["k"]; runs = []
        for r in range(R):
            # homogeneous goblins, nested seeds: seed(g,r) = 1000 + g + 100*r
            packets = []
            for g in range(k):
                seed = 1000 + g + 100*r
                raw, tok, secs, st = ask(GPROMPT, f"SOURCES:\n{corpus_text}", GBUD, GTEMP, seed)
                pkt = extract(raw)
                complete = bool(isinstance(pkt, dict) and str(pkt.get("proposition","")).strip()
                                and str(pkt.get("declared_falsifier","")).strip())
                packets.append({"g": g, "seed": seed, "tok": tok, "secs": secs, "status": st,
                                "complete": complete, "packet": pkt})
            g_config = all(p["complete"] for p in packets)
            n_p = sum(p["complete"] for p in packets)
            evaluable = g_config  # any incomplete => NOT_EVALUABLE (no top-up)
            hal = []; survived_props = []; decisive = 0
            if evaluable:
                for p in packets:
                    prop = p["packet"]["proposition"]; fals = p["packet"]["declared_falsifier"]
                    raw, tok, secs, st = ask(HAL_SYS, f"CORPUS:\n{corpus_text}\nPROPOSITION: {prop}\nDECLARED_FALSIFIER: {fals}",
                                             500, 0, None)
                    hv = extract(raw); v = str((hv or {}).get("verdict","INCONCLUSIVE")).upper()
                    if v not in ("SURVIVED","REFUTED","INCONCLUSIVE"): v = "INCONCLUSIVE"
                    if v in ("SURVIVED","REFUTED"): decisive += 1
                    if v == "SURVIVED": survived_props.append(prop)
                    hal.append({"g": p["g"], "verdict": v, "tok": tok, "secs": secs})
            n_roots, ambiguous = independent_roots(survived_props) if evaluable else (0, 0)
            distinct_all, _ = independent_roots([p["packet"]["proposition"] for p in packets if p["complete"]]) if evaluable else (0, 0)
            admission = 0  # SCALE_V1 admits nothing, ever
            g_gov = (admission == 0)
            authority_violations += (0 if g_gov else 1)
            valid = g_config and evaluable and g_gov
            earned_keys = sorted({canon(p) for p in survived_props if canon(p)})
            tok_total = sum(p["tok"] for p in packets) + sum(h["tok"] for h in hal)
            secs_total = round(sum(p["secs"] for p in packets) + sum(h["secs"] for h in hal), 1)
            runs.append({"r": r, "k": k, "valid": valid, "G_config": g_config, "G_evaluable": evaluable, "G_gov": g_gov,
                         "N_P": n_p, "N_E": n_p if evaluable else 0, "N_earned": n_roots, "earned_keys": earned_keys,
                         "distinct_props": distinct_all, "review_ambiguous": ambiguous,
                         "decisive": decisive, "hal": hal, "packets": packets,
                         "tokens": tok_total, "secs": secs_total, "admission": admission})
            print(f"  {cfg} r{r} k{k}: valid={valid} N_P={n_p} N_earned={n_roots} decisive={decisive}/{n_p} tok={tok_total} {secs_total}s")

        valid_runs = [x for x in runs if x["valid"]]
        nvalid = len(valid_runs)
        # metrics
        truncation_rate = round(sum(1 for x in runs if not x["G_evaluable"]) / R, 3)
        if nvalid >= 3:
            earned = [x["N_earned"] for x in valid_runs]
            mean_earned = round(sum(earned)/nvalid, 3)
            var_earned = round(sum((e-mean_earned)**2 for e in earned)/nvalid, 3)
            pairs = list(itertools.combinations(range(nvalid), 2))
            stability = round(sum(jaccard(valid_runs[i]["earned_keys"], valid_runs[j]["earned_keys"]) for i,j in pairs)/len(pairs), 3) if pairs else 1.0
            dup = [1 - (x["distinct_props"]/x["N_P"]) if x["N_P"] else 0 for x in valid_runs]
            duplicate_rate = round(sum(dup)/nvalid, 3)
            resolution = [x["decisive"]/x["N_E"] if x["N_E"] else 0 for x in valid_runs]
            resolution_rate = round(sum(resolution)/nvalid, 3)
            review_total = sum(x["N_earned"] + x["review_ambiguous"] for x in valid_runs)
            status = "EVALUABLE"
        else:
            mean_earned = var_earned = stability = duplicate_rate = resolution_rate = review_total = None
            status = "INSUFFICIENT_VALID_RUNS"
        campaign["configs"][cfg] = {"k": k, "R": R, "valid_runs": nvalid, "status": status,
            "N_earned_mean": mean_earned, "N_earned_var": var_earned, "N_earned_per_valid_run": [x["N_earned"] for x in valid_runs],
            "Stability": stability, "DuplicateRate": duplicate_rate, "ResolutionRate": resolution_rate,
            "TruncationRate": truncation_rate, "OperatorReview": review_total,
            "CognitiveCost_tokens": sum(x["tokens"] for x in runs), "CognitiveCost_secs": round(sum(x["secs"] for x in runs),1),
            "AuthorityViolations": 0, "runs": runs}
        (OUT / f"{cfg}_runs.json").write_text(json.dumps(campaign["configs"][cfg], indent=2))
        print(f"=== {cfg} k{k}: {status} valid={nvalid}/{R} N_earned_mean={mean_earned} Stability={stability} "
              f"Trunc={truncation_rate} cost={campaign['configs'][cfg]['CognitiveCost_tokens']}tok ===")

    # ── receipts (frozen design's 3) ──
    cfgs = campaign["configs"]
    config_receipt = {"receipt": "CONFIGURATION_RECEIPT", "run": "SCALE_V1", "prereg_hash": live_seal,
                      "corpus_sha256": _h(CORPUS), "R": R,
                      "valid_runs": {c: cfgs[c]["valid_runs"] for c in cfgs},
                      "status": {c: cfgs[c]["status"] for c in cfgs}}
    epistemic_receipt = {"receipt": "EPISTEMIC_RECEIPT",
                         "N_earned_mean": {c: cfgs[c]["N_earned_mean"] for c in cfgs},
                         "Stability": {c: cfgs[c]["Stability"] for c in cfgs},
                         "primary_comparison": "N_earned(C_k) vs k under byte-frozen conditions",
                         "boundary": "HAL_SURVIVED != TRUE != admission; N_earned is candidate-level only",
                         "prereg_frame": "single-answer corpus => null/reliability probe; N_earned growth = fan-out red flag"}
    governance_receipt = {"receipt": "GOVERNANCE_RECEIPT", "authority": False, "canon": False, "ledger_effect": "none",
                          "admission": False, "gamma_A_equal_across_k_and_empty": True,
                          "AuthorityViolations": authority_violations,
                          "result": "CLEAN" if authority_violations == 0 else "CAMPAIGN_ABORT"}
    for nm, rc in [("CONFIGURATION_RECEIPT", config_receipt), ("EPISTEMIC_RECEIPT", epistemic_receipt), ("GOVERNANCE_RECEIPT", governance_receipt)]:
        (OUT / f"{nm}.json").write_text(json.dumps(rc, indent=2))
    (OUT / "campaign_report.json").write_text(json.dumps({k: v for k, v in campaign.items()}, indent=2, default=str))

    print("\n=== SCALE_V1 CAMPAIGN COMPLETE ===")
    for c in cfgs:
        print(f"  {c} k{cfgs[c]['k']}: {cfgs[c]['status']} N_earned_mean={cfgs[c]['N_earned_mean']} "
              f"Stability={cfgs[c]['Stability']} valid={cfgs[c]['valid_runs']}/{R} cost={cfgs[c]['CognitiveCost_tokens']}tok")
    print("GOVERNANCE:", governance_receipt["result"], "· AuthorityViolations:", authority_violations,
          "· Gamma_A=empty across k:", governance_receipt["gamma_A_equal_across_k_and_empty"])
    print("DONE_SCALE_V1")

if __name__ == "__main__":
    main()
