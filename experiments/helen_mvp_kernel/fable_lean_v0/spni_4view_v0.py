"""SPNI_4VIEW_V0 — Semantic Projection Non-Interference, 9-case falsifier. authority=false · canon=false ·
ledger_effect=none. NON-SOVEREIGN. Executes the frozen test: 1 typed σ × 4 renderers × (clean + entitlement mutant)
+ 1 aesthetic control = 9 cases. Goal: find the first SilentCorruption.

Formal core (operator-sharpened):
  σ ∈ Σ ; renderer R_p : Σ → P_p ; extractor-under-test E_p : P_p → L_⊥ (L_⊥ = L ∪ {⊥}) ; Entitle : L_⊥ → Decision.
  Λ_p : P_p → L (REFERENCE ORACLE, total; used ONLY by the harness to decide if a mutation was load-bearing).
  CRITICAL: SystemUnderTest (E_p) ≠ GroundTruthOracle (Λ_p) — a defective E_p must not also be the judge.

  P (Preservation):  E_p(R_p(σ)) = Π_L^Σ(σ)
  D (Detection):     Λ_p(P')≠Λ_p(P)  ⇒  E_p(P')≠E_p(P)  ∨  E_p(P')=⊥
  F (FailClosed):    E_p(P)=⊥  ⇒  Entitle(⊥) ∈ {HOLD,FAIL},  never ADMIT
  SilentCorruption ⟺ Λ_p(P')≠Λ_p(P)  ∧  E_p(P')=E_p(P).   Target: N_silent = 0.
  Aesthetic mutant (Λ unchanged) must PASS — proves this is NOT byte-level integrity.

Teeth on the EXTRACTOR itself: we run TWO E_p — a fail-closed E_good (the SUT) and a fail-open E_bad (defective
control). E_bad MUST exhibit SilentCorruption>0 so the metric is demonstrably non-vacuous.
"""
import hashlib, json, copy, pathlib

OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)
BOT = "⊥"
LB_KEYS = ("status", "authority", "admission", "roots", "scope", "replayable")

SIGMA = {"status": "REPORTED", "authority": False, "admission": "HOLD", "roots": ["R1"],
         "scope": "LOCAL", "replayable": True}

def PiL_sigma(s):
    return {"status": s["status"], "authority": s["authority"], "admission": s["admission"],
            "root_count": len(s["roots"]), "scope": s["scope"], "replayable": s["replayable"]}
def canon(d): return json.dumps(d, sort_keys=True)

# ── renderers: payload carries load-bearing verbatim; surface is styled ──
def _P(profile, s, surface): return {"profile": profile, "payload": copy.deepcopy(s), "surface": surface}
def R_default(s): return _P("Default", s, f"The gate holds. Status {s['status']}, authority={s['authority']}, {len(s['roots'])} root, scope {s['scope']}.")
def R_concise(s): return _P("Concise", s, f"{s['admission']} · {s['status']} · {len(s['roots'])}root · reported by source")
def R_color(s):   return _P("ColorWULmath", s, f"🟡 {s['admission']} 🔵 {s['status']} 🌿 {s['scope']}")
def R_voice(s):   return _P("Voice", s, f"We're holding — still {s['status'].lower()}, one root, local scope.")
RENDERERS = {"Default": R_default, "Concise": R_concise, "ColorWULmath": R_color, "Voice": R_voice}

# ── Λ : reference oracle (total; missing key → 'MISSING' sentinel; independent of E) ──
def Lambda(P):
    pl = P.get("payload", {})
    return {k: (len(pl["roots"]) if k == "roots" and isinstance(pl.get("roots"), list)
                else pl.get(k, "MISSING")) for k in LB_KEYS}

def Lambda_L(P):
    L = Lambda(P)
    return {"status": L["status"], "authority": L["authority"], "admission": L["admission"],
            "root_count": L["roots"], "scope": L["scope"], "replayable": L["replayable"]}

# ── E_good : fail-closed SUT extractor → L or ⊥ ──
def E_good(P):
    pl = P.get("payload", {})
    if any(k not in pl for k in LB_KEYS): return BOT                       # malformed → ⊥
    if pl["admission"] == "ADMIT" and pl["authority"] is False: return BOT # admitted w/o authority → inconsistent → ⊥
    return {"status": pl["status"], "authority": pl["authority"], "admission": pl["admission"],
            "root_count": len(pl["roots"]) if isinstance(pl["roots"], list) else pl["roots"],
            "scope": pl["scope"], "replayable": pl["replayable"]}

# ── E_bad : fail-OPEN defective control (fills missing, ignores inconsistency) ──
def E_bad(P):
    pl = P.get("payload", {})
    return {"status": pl.get("status", "REPORTED"), "authority": pl.get("authority", False),  # defaults missing authority
            "admission": pl.get("admission", "HOLD"),
            "root_count": len(pl["roots"]) if isinstance(pl.get("roots"), list) else pl.get("roots", 1),
            "scope": pl.get("scope", "LOCAL"), "replayable": pl.get("replayable", True)}

def Entitle(Lval):
    return "HOLD" if Lval == BOT else Lval.get("admission", "HOLD")   # Entitle(⊥)=HOLD, never ADMIT

# ── mutants (operate on the rendered presentation) ──
def m_status(P):   P = copy.deepcopy(P); P["payload"]["status"] = "VERIFIED"; return P            # REPORTED→VERIFIED
def m_authority(P):P = copy.deepcopy(P); P["payload"].pop("authority", None); return P            # authority=false omitted
def m_admission(P):P = copy.deepcopy(P); P["payload"]["admission"] = "ADMIT"; P["surface"] = P["surface"].replace("HOLD", "ADMIT"); return P  # HOLD→ADMIT
def m_roots(P):    P = copy.deepcopy(P); P["payload"]["roots"] = [f"R{i}" for i in range(1, 6)]; P["surface"] = P["surface"].replace("one root", "multiple independent sources"); return P
def m_aesthetic(P):P = copy.deepcopy(P); P["surface"] = P["surface"].replace("reported by source", "source reports"); return P  # payload untouched

ENTITLEMENT_MUTANTS = {"Default": m_status, "Concise": m_authority, "ColorWULmath": m_admission, "Voice": m_roots}

def run(E, label):
    sigmaL = PiL_sigma(SIGMA)
    clean_ok = 0; silent = 0; malformed_to_admit = 0; failclosed_ok = True; rows = []
    # clean preservation
    for name, R in RENDERERS.items():
        P = R(SIGMA); e = E(P)
        pres = (e != BOT and canon(e) == canon(sigmaL))
        clean_ok += pres
        rows.append({"case": f"CLEAN/{name}", "E": "L" if e != BOT else BOT, "preserved": pres})
    # entitlement mutants
    for name, M in ENTITLEMENT_MUTANTS.items():
        P0 = RENDERERS[name](SIGMA); P1 = M(P0)
        loadbearing_change = canon(Lambda_L(P0)) != canon(Lambda_L(P1))   # ORACLE decides
        e0, e1 = E(P0), E(P1)
        e_changed = (canon(e1) if e1 != BOT else BOT) != (canon(e0) if e0 != BOT else BOT)
        is_silent = loadbearing_change and (e1 != BOT) and (canon(e1) == canon(e0))
        silent += is_silent
        if e1 == BOT:
            fc = Entitle(BOT) != "ADMIT"; failclosed_ok &= fc
            if Entitle(BOT) == "ADMIT": malformed_to_admit += 1
        rows.append({"case": f"MUTANT/{name}/{M.__name__}", "oracle_loadbearing_change": loadbearing_change,
                     "E1": "⊥" if e1 == BOT else "L", "E_detected": (e_changed or e1 == BOT),
                     "silent_corruption": is_silent})
    # aesthetic control (Λ unchanged → must be allowed, same entitlement)
    Pa0 = R_concise(SIGMA); Pa1 = m_aesthetic(Pa0)
    aesthetic_lb_change = canon(Lambda_L(Pa0)) != canon(Lambda_L(Pa1))
    ea_same = canon(E(Pa1)) == canon(E(Pa0))
    aesthetic_pass = (not aesthetic_lb_change) and ea_same
    rows.append({"case": "AESTHETIC/Concise", "oracle_loadbearing_change": aesthetic_lb_change,
                 "E_same": ea_same, "SPNI_PASS": aesthetic_pass})
    return {"extractor": label, "clean_preservation": f"{clean_ok}/4", "silent_corruption": silent,
            "malformed_to_admit": malformed_to_admit, "failclosed": "PASS" if failclosed_ok else "FAIL",
            "aesthetic_control": "PASS" if aesthetic_pass else "FAIL", "rows": rows}

def main():
    good = run(E_good, "E_good (SUT, fail-closed)")
    bad = run(E_bad, "E_bad (defective, fail-open — teeth control)")

    print("=== SPNI_4VIEW_V0 — 9 cases · find first SilentCorruption ===")
    print(f"  Π_L(σ) = {hashlib.sha256(canon(PiL_sigma(SIGMA)).encode()).hexdigest()[:16]}   σ = REPORTED/authority=false/HOLD/1root/LOCAL/replayable\n")
    for res in (good, bad):
        print(f"  -- {res['extractor']} --")
        for r in res["rows"]:
            print(f"     {r['case']:34} " + " ".join(f"{k}={v}" for k, v in r.items() if k != "case"))
        print(f"     => CleanPreservation={res['clean_preservation']} · SilentCorruption={res['silent_corruption']} "
              f"· MalformedToAdmit={res['malformed_to_admit']} · FailClosed={res['failclosed']} · Aesthetic={res['aesthetic_control']}\n")

    sut_pass = (good["clean_preservation"] == "4/4" and good["silent_corruption"] == 0
                and good["malformed_to_admit"] == 0 and good["failclosed"] == "PASS"
                and good["aesthetic_control"] == "PASS")
    teeth_ok = bad["silent_corruption"] > 0   # metric proven non-vacuous
    result = "SURVIVED_DEFINED_ATTACK_SET" if (sut_pass and teeth_ok) else "FALSIFIED"
    print(f"  SUT (E_good) acceptance: {'PASS' if sut_pass else 'FAIL'}  (4/4 · silent=0 · admit=0 · failclosed · aesthetic-pass)")
    print(f"  TEETH: E_bad SilentCorruption={bad['silent_corruption']} (>0 required → metric non-vacuous): {'OK' if teeth_ok else 'BROKEN'}")
    print(f"  SPNI_4VIEW_V0 = {result}")
    print("  SystemUnderTest ≠ GroundTruthOracle · Many projections, one entitlement class · authority=false · canon=false · ledger_effect=none")

    receipt = {"receipt": "SPNI_4VIEW_V0", "sigma": SIGMA, "PiL_sigma": PiL_sigma(SIGMA),
               "decomposition": "SPNI = Preservation + Detection + FailClosed",
               "oracle_separation": "Λ (reference) ≠ E (system under test)",
               "E_good": {k: good[k] for k in ("clean_preservation", "silent_corruption", "malformed_to_admit", "failclosed", "aesthetic_control")},
               "E_bad_control": {k: bad[k] for k in ("clean_preservation", "silent_corruption", "malformed_to_admit", "failclosed")},
               "SUT_acceptance": "PASS" if sut_pass else "FAIL", "teeth_non_vacuous": teeth_ok,
               "first_silent_corruption_in_SUT": next((r["case"] for r in good["rows"] if r.get("silent_corruption")), None),
               "RESULT": result, "SelfPassed": True, "PeerAdversaryValidated": False,
               "rows_good": good["rows"], "rows_bad": bad["rows"],
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "spni_4view_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/spni_4view_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
