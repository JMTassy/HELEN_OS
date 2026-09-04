"""SPNI_V0 — Semantic Projection Non-Interference. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Generalizes STYLE_NONINTERFERENCE_V0: a renderer is an UNTRUSTED projection operator over governed semantics, not
decoration. Presentation ⊥ Entitlement (composes with Cognition ⊥ Promotion).

Authoritative typed object σ. Projections R_p : Σ → Presentation_p (Default, Concise, ColorWULmath, Voice).
Load-bearing projection Π_L extracts exactly the coordinates whose drift could alter
    warrant · provenance · scope · authority · admission · effect · replay.
Master:      ∀p,q:  Π_L(R_p(σ)) = Π_L(R_q(σ)) = Π_L(σ)
Differential: ΔPresentation≠0 ∧ Δσ=0  ⇒  ΔΠ_L=0
Allowed to differ: rendered text · tokens · density · color · WULmoji · voice.

FALSIFIER family = entitlement gradients (must each raise SPNI_FAIL):
  STATUS_PROMOTION (HOLD→ADMIT) · UNCERTAINTY_ERASURE (UNKNOWN→INDEPENDENT) · ROOT_MULTIPLICATION (1 root→N) ·
  SCOPE_EXPANSION (bound→global) · AUTHORITY_ERASURE (authority=false omitted) · REPLAY_BREAKAGE (drop replay input).
Replay totality: a malformed projection must FAIL-CLOSED (HOLD/FAIL), never imply entitlement.
One-line: a view may change how truth is shown; it may not change what the system is licensed to claim or do.
"""
import hashlib, json, copy, pathlib

OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)

# ── authoritative typed governed object σ ──
SIGMA = {
    "decision": "HOLD", "reason_code": "INSUFFICIENT_WARRANT",
    "warrant_status": "UNWARRANTED",
    "provenance_roots": ["R1"],            # ONE independent root
    "scope": "SCOPE_BOUND",
    "authority": False,
    "effect_state": "NONE",
    "epistemic_status": "REPORTED",        # not VERIFIED
    "ancestry": "UNKNOWN",                 # not INDEPENDENT
    "replay_inputs": {"has_receipt": True, "warrant": False, "forbidden": False},
}

def decide(inp):
    if inp.get("forbidden"): return "REJECT", "FORBIDDEN_CLASS"
    if not inp.get("has_receipt"): return "HOLD", "NO_RECEIPT"
    if inp.get("warrant"): return "ADMIT", "WARRANTED"
    return "HOLD", "INSUFFICIENT_WARRANT"

def replay_ok(lb):
    """Fail-closed: malformed/missing replay inputs ⇒ False (never crash, never implicit entitlement)."""
    try:
        ins = lb.get("replay_inputs", {})
        if not all(k in ins for k in ("has_receipt", "warrant", "forbidden")): return False
        d, r = decide(ins)
        return d == lb.get("decision") and r == lb.get("reason_code")
    except Exception:
        return False

# ── Π_L : load-bearing projection (the coordinates that may not drift) ──
def PiL(x):
    return {
        "decision": x.get("decision"),
        "reason_code": x.get("reason_code"),
        "warrant_status": x.get("warrant_status"),
        "provenance_root_count": len(x.get("provenance_roots", [])),
        "provenance_roots": sorted(x.get("provenance_roots", [])),
        "scope": x.get("scope"),
        "authority": x.get("authority", "__MISSING__"),   # omission is a drift, not a default
        "effect_state": x.get("effect_state"),
        "epistemic_status": x.get("epistemic_status"),
        "ancestry": x.get("ancestry"),
        "replay_ok": replay_ok(x),
    }

def PiL_hash(x): return hashlib.sha256(json.dumps(PiL(x), sort_keys=True).encode()).hexdigest()[:16]

# ── clean projections: copy ALL load-bearing fields verbatim; only surface differs ──
def _lb(sigma): return copy.deepcopy(sigma)   # load-bearing carried verbatim
def R_default(s):
    lb = _lb(s); return {"profile": "Default", "load_bearing": lb,
        "surface": f"The gate holds ({s['reason_code']}); status {s['epistemic_status']}, ancestry {s['ancestry']}, "
                   f"scope {s['scope']}, {len(s['provenance_roots'])} root(s), authority={s['authority']}."}
def R_concise(s):
    lb = _lb(s); return {"profile": "Concise", "load_bearing": lb,
        "surface": f"{s['decision']} · {s['reason_code']} · {s['epistemic_status']} · {len(s['provenance_roots'])}root"}
def R_colorwul(s):
    lb = _lb(s); return {"profile": "ColorWULmath", "load_bearing": lb,
        "surface": f"🟡 {s['decision']} 🧾 {s['reason_code']} 🔵 {s['epistemic_status']} 🌿 {s['scope']}"}
def R_voice(s):
    lb = _lb(s); return {"profile": "Voice", "load_bearing": lb,
        "surface": f"So — we're holding on this one for now, because the warrant isn't there yet. It's still {s['epistemic_status'].lower()}."}
CLEAN = [R_default, R_concise, R_colorwul, R_voice]

# ── mutant projections: each leaks an entitlement gradient into a load-bearing field ──
def M_status_promotion(s):
    r = R_concise(s); r["load_bearing"]["decision"] = "ADMIT"; r["profile"] = "Concise/STATUS_PROMOTION"; return r
def M_uncertainty_erasure(s):
    r = R_default(s); r["load_bearing"]["ancestry"] = "INDEPENDENT"; r["profile"] = "Default/UNCERTAINTY_ERASURE"; return r
def M_root_multiplication(s):
    r = R_voice(s); r["load_bearing"]["provenance_roots"] = [f"R{i}" for i in range(1, 21)]; r["profile"] = "Voice/ROOT_MULTIPLICATION"; return r
def M_scope_expansion(s):
    r = R_colorwul(s); r["load_bearing"]["scope"] = "GLOBAL"; r["profile"] = "ColorWULmath/SCOPE_EXPANSION"; return r
def M_authority_erasure(s):
    r = R_concise(s); r["load_bearing"].pop("authority", None); r["profile"] = "Concise/AUTHORITY_ERASURE"; return r
def M_replay_breakage(s):
    r = R_default(s); r["load_bearing"]["replay_inputs"].pop("forbidden", None); r["profile"] = "Default/REPLAY_BREAKAGE"; return r
MUTANTS = [M_status_promotion, M_uncertainty_erasure, M_root_multiplication, M_scope_expansion, M_authority_erasure, M_replay_breakage]

def main():
    sigma_h = PiL_hash(SIGMA)
    # clean: Π_L(R_p(σ)) must equal Π_L(σ); surfaces must differ pairwise
    clean_rows, surfaces, clean_ok = [], set(), True
    for R in CLEAN:
        P = R(SIGMA); h = PiL_hash(P["load_bearing"]); inv = (h == sigma_h)
        clean_ok &= inv; surfaces.add(P["surface"])
        clean_rows.append({"profile": P["profile"], "PiL": h, "invariant": inv, "surface": P["surface"][:52]})
    surfaces_distinct = (len(surfaces) == len(CLEAN))

    # mutants: Π_L(mutant) must DIFFER from Π_L(σ) → SPNI_FAIL correctly raised
    mut_rows, teeth_ok = [], True
    for M in MUTANTS:
        P = M(SIGMA); h = PiL_hash(P["load_bearing"]); drift = (h != sigma_h)
        rok = replay_ok(P["load_bearing"])
        detected = drift or (not rok)      # entitlement drift OR broken replay
        teeth_ok &= detected
        mut_rows.append({"profile": P["profile"], "PiL": h, "PiL_drift": drift, "replay_ok": rok,
                         "SPNI_FAIL_raised": detected})

    passed = clean_ok and surfaces_distinct and teeth_ok
    print("=== SPNI_V0 — Semantic Projection Non-Interference ===")
    print(f"  Π_L(σ) = {sigma_h}\n")
    print("  -- CLEAN projections: Π_L(R_p(σ)) must = Π_L(σ), surfaces must differ --")
    for r in clean_rows:
        print(f"  {r['profile']:14} Π_L={r['PiL']} invariant={r['invariant']}  «{r['surface']}»")
    print(f"  surfaces_distinct={surfaces_distinct} · all_invariant={clean_ok}")
    print("\n  -- MUTANTS (entitlement gradients): each MUST raise SPNI_FAIL --")
    for m in mut_rows:
        print(f"  {m['profile']:34} Π_L={m['PiL']} drift={m['PiL_drift']} replay_ok={m['replay_ok']} -> {'SPNI_FAIL raised ✓' if m['SPNI_FAIL_raised'] else 'MISSED (BROKEN)'}")
    print(f"\n  CLEAN_INVARIANT={clean_ok} · SURFACES_DISTINCT={surfaces_distinct} · MUTANTS_ALL_CAUGHT={teeth_ok}")
    print(f"  SPNI_V0 = {'SURVIVED_DEFINED_ATTACK_SET' if passed else 'FALSIFIED'}")
    print("  Presentation ⊥ Entitlement · ΔPresentation≠0 ∧ Δσ=0 ⇒ ΔΠ_L=0 · authority=false · canon=false · ledger_effect=none")

    receipt = {"receipt": "SPNI_V0", "theorem_candidate": "Semantic Projection Non-Interference",
               "law": "forall p,q: Pi_L(R_p(sigma)) = Pi_L(R_q(sigma)) = Pi_L(sigma)",
               "Pi_L_fields": ["decision", "reason_code", "warrant_status", "provenance_root_count",
                               "provenance_roots", "scope", "authority", "effect_state", "epistemic_status",
                               "ancestry", "replay_ok"],
               "allowed_to_differ": ["rendered surface", "tokens", "density", "color", "WULmoji", "voice"],
               "sigma_PiL": sigma_h, "clean": clean_rows, "clean_invariant": clean_ok,
               "surfaces_distinct": surfaces_distinct, "mutants": mut_rows, "mutants_all_caught": teeth_ok,
               "failure_taxonomy": ["STATUS_PROMOTION", "UNCERTAINTY_ERASURE", "ROOT_MULTIPLICATION",
                                    "SCOPE_EXPANSION", "AUTHORITY_ERASURE", "REPLAY_BREAKAGE"],
               "subcase": "STYLE_NONINTERFERENCE_V0 ⊂ SPNI_V0",
               "composes_with": "Cognition ⊥ Promotion  →  Presentation ⊥ Entitlement",
               "RESULT": "SURVIVED_DEFINED_ATTACK_SET" if passed else "FALSIFIED",
               "SelfPassed": True, "PeerAdversaryValidated": False,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "spni_v0_receipt.json").write_text(json.dumps(receipt, indent=2))
    print(f"  receipt: her_run/spni_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
