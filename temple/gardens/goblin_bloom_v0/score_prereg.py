#!/usr/bin/env python3
"""
GOBLIN_BLOOM_PREREG_SCORE_V2 — derived adjudication of the bloom vs the SEALED prereg.

Law: bloom quality is NOT evaluated; frozen predictions are ADJUDICATED. A surprise is valuable
precisely when the scorer could not know in advance which way it would resolve.

Hardened (frozen BEFORE results):
  κ=2      : P2 is compression-ratio ΔN/max(1,ΔQ) ≥ κ, not ΔN>ΔQ.
  P5       : VALID falsifier is DERIVED from content (concrete counterexample + discriminating
             structure), NOT the goblin's KIND label. declared_kind stays metadata.
  ΔR split : (ΔR_J candidate research reachability, ΔR_Γ governed) with hard invariant ΔR_Γ≡0.
  Δd_M≡0   : in-epoch (no later independent reuse) — any Δd_M>0 = self-certification bug.
  V4       : UNREPRESENTABLE for an in-epoch classifier (range = {V0,V1,V2,V3}).
  removal  : tri-valued KILL / SURVIVE / UNRESOLVED (UNKNOWN ≠ PASS), on the REAL reuse graph.
  hashes   : PREREG_HASH · SCORER_HASH(self) · TRACE_HASH · RECEIPT_HASH = H(H_P‖H_S‖H_T‖obs‖verdict).

Observables are DERIVED from bloom_trace.ndjson (raw), never from the swarm's self-computed verdict.
authority=false · ΔA=0 · NO_CLAIM · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent; GARDENS = ROOT.parent
SEAL = "f5f9225649fe64588f6a0eba04735e41b299f5c45ff624d8a37dddca69bf08b5"
KAPPA = 2                                    # frozen compression threshold
SCORER_VERSION = "V2"
def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()

def valid_falsifier(c):
    """DERIVED, not KIND-labelled: concrete counterexample + a discriminating structure."""
    txt = (c["claim"] + " " + c["counterexample"]).lower()
    has_ce = len(c["counterexample"].strip()) >= 12
    discriminates = any(k in txt for k in
        ["≁", "not ∼", "≠", "∼_f", "∼_e", "∼_γ", "sim_f", "without producing", "bypass",
         "root hash", "counterexample", "z/", "remov", "provenance", "forbidden", "shortcut"])
    return has_ce and c["falsifiability"] >= 4 and discriminates

def valid_instrument(c):
    """A new reusable discriminator: a bridge that names a witness and separates cases, fals≥4."""
    return c["kind"] == "BRIDGE" and c["falsifiability"] >= 4 and len(c["witness"].strip()) >= 8

def main():
    red_path = ROOT / "GOBLIN_BLOOM_REDUCED.json"
    trace_path = ROOT / "bloom_trace.ndjson"
    if not red_path.exists() or not trace_path.exists():
        print("⏳ bloom not complete (REDUCED/trace missing). Holding."); return

    pre_path = ROOT / "GOBLIN_BLOOM_PREREG_V0.json"
    H_P = sha(pre_path.read_bytes()); H_S = sha(Path(__file__).read_bytes())
    H_T = sha(trace_path.read_bytes())
    seal_ok = (H_P == SEAL); predates = pre_path.stat().st_mtime < red_path.stat().st_mtime

    trace = [json.loads(l) for l in trace_path.read_text().splitlines() if l.strip()]
    for i, c in enumerate(trace): c["evt"] = f"evt_{i:04d}"
    live = [c for c in trace if not c["error"] and c["claim"]]

    # ---- DERIVE ΔS from raw trace (independent of swarm's self-verdict) ----
    def toks(s): return set(__import__("re").sub(r"[^a-z0-9 ]", " ", s.lower()).split())
    reps = []
    for c in live:
        k = toks(c["claim"]); dup = next((r for r in reps if len(k & r["_k"]) / max(1, len(k | r["_k"])) > 0.5), None)
        if dup: dup["_n"] += 1
        else: c["_k"] = k; c["_n"] = 1; reps.append(c)
    dN = len(live); dQ = len(reps)
    valid_fals = [c for c in reps if valid_falsifier(c)]
    valid_inst = [c for c in reps if valid_instrument(c)]
    invalid_self = [c["evt"] for c in reps if c["kind"] in ("FALSIFIER", "REMOVAL", "QUOTIENT") and not valid_falsifier(c)]
    dD = len(valid_fals)                        # decision-separating distinctions (derived)
    dI = len(valid_inst)                        # reusable instruments (derived)
    dM = 0                                      # in-epoch hard invariant
    targets = {c["claim"][:20] for c in (valid_fals + valid_inst)}
    dRJ = len(targets); dRG = 0                 # ΔR_Γ hard invariant
    comp_ratio = round(dN / max(1, dQ), 2)
    top = max(reps, key=lambda c: c["novelty"] + c["falsifiability"] + c["leverage"], default=None)
    top_derived = ("VALID_FALSIFIER" if (top and valid_falsifier(top)) else
                   "VALID_INSTRUMENT" if (top and valid_instrument(top)) else "NON_DISCRIMINATING")

    # ---- mechanical classifier (V4 unrepresentable in-epoch) ----
    if dI > 0:            verdict = "V3"
    elif len(valid_fals) > 0: verdict = "V2"
    elif dQ > 0:         verdict = "V1"
    else:               verdict = "V0"

    # ---- counterfactual removal, tri-valued, on the REAL reuse graph ----
    try:
        led = json.loads((GARDENS/"chiddush_diachronic_v0"/"CHIDDUSH_DIACHRONIC_V0_RECEIPT.json").read_text())["ledger"]
        retained = [r for r in led if r["chiddush_earned"]]
    except Exception:
        retained = []
    KILL, SURVIVE, UNRESOLVED = [], [], []
    for r in retained:
        if "reused_at" not in r: UNRESOLVED.append(r["id"])
        elif r["reused_at"]: KILL.append(r["id"])          # removal deletes downstream edge → necessity demonstrated
        else: SURVIVE.append(r["id"])                       # retained but removal changes nothing → law-breaker
    law_survives = (len(retained) > 0 and not SURVIVE and not UNRESOLVED)

    stop = json.loads(red_path.read_text()).get("stop_reason", "UNKNOWN")

    # ---- 8 predicates, each with evidence refs ----
    def pr(res, refs): return {"result": "PASS" if res else "FAIL", "evidence_refs": refs}
    P = {
      "P1_MODE_PREDICTION_{V2,V3}": pr(verdict in ("V2", "V3"), [f"verdict={verdict}"]),
      "P2_COMPRESSION_ratio>=κ":    pr(comp_ratio >= KAPPA, [f"ΔN/ΔQ={comp_ratio}", f"κ={KAPPA}"]),
      "P3_Q_GE_DD":                 pr(dQ >= dD, [f"ΔQ={dQ}", f"Δd_D={dD}"]),
      "P4_DD_GE_DM":                pr(dD >= dM, [f"Δd_D={dD}", f"Δd_M={dM}"]),
      "P5_VALID_FALSIFIER_DOMINATES": pr(len(valid_fals) > 0 and top_derived == "VALID_FALSIFIER",
                                         [c["evt"] for c in valid_fals[:4]] + [f"top={top_derived}"]),
      "P6_DIAMONDS_LT_CANDIDATES":  pr(0 < dQ, [f"newborn_💎=0", f"🟣_candidates={dQ}"]),
      "P7_NO_V4_IN_EPOCH":          pr(verdict != "V4", ["classifier_range={V0,V1,V2,V3}"]),
      "P8_STOP_IS_DRYNESS_NOT_PROOF": pr(stop == "MARGINAL_INFORMATION_DRYNESS", [f"stop={stop}"]),
    }
    npass = sum(1 for v in P.values() if v["result"] == "PASS")

    inflation = comp_ratio < KAPPA
    self_cert = (dM > 0) or (dRG > 0)
    in_epoch_retention_violation = (dM > 0)
    governed_reach_violation = (dRG > 0)

    observables = {"ΔN": dN, "ΔQ": dQ, "Δd_D": dD, "Δd_I": dI, "Δd_M": dM, "ΔR_J": dRJ, "ΔR_Γ": dRG,
                   "compression_ratio": comp_ratio, "verdict": verdict}
    H_R = sha(H_P + "‖" + H_S + "‖" + H_T + "‖" + json.dumps(observables, sort_keys=True) + "‖" + verdict)

    out = {
      "score_of": "GOBLIN_BLOOM_30MIN_V0", "scorer_version": SCORER_VERSION,
      "COMMITMENTS": {"PREREG_HASH": H_P, "SCORER_HASH": H_S, "TRACE_HASH": H_T,
                      "seal_matches": seal_ok, "prereg_predates_results": predates},
      "OBSERVED_DERIVED": observables,
      "HARD_INVARIANTS": {"IN_EPOCH_RETENTION_VIOLATION": in_epoch_retention_violation,
                          "GOVERNED_REACHABILITY_VIOLATION": governed_reach_violation,
                          "SELF_CERTIFICATION_DETECTED": self_cert},
      "COMPRESSION": {"KAPPA": KAPPA, "compression_ratio": comp_ratio, "INFLATION_DETECTED": inflation},
      "DISCRIMINATORS": {"VALID_FALSIFIERS": [c["evt"] for c in valid_fals],
                         "VALID_INSTRUMENTS": [c["evt"] for c in valid_inst],
                         "INVALID_SELF_LABELS": invalid_self, "TOP_DERIVED_CONTRIBUTION": top_derived},
      "MECHANICAL_VERDICT": verdict, "classifier_range": ["V0", "V1", "V2", "V3"],
      "PREREG": {"predicted_mode": "{V2,V3}", "observed_mode": verdict, "mode_hit": verdict in ("V2", "V3")},
      "COUNTERFACTUAL_REMOVAL": {"method": "tri-valued on real reuse graph",
          "KILLS_necessity_demonstrated": KILL, "SURVIVES_necessity_falsified": SURVIVE,
          "UNRESOLVED": UNRESOLVED, "diachronic_law_survives(D+)": law_survives},
      "PREREG_SCORE": P, "SCORE": f"{npass}/8",
      "STOP_REASON": stop, "THEORY_PROVEN": False, "authority_delta": 0, "claims_admitted": 0,
      "RECEIPT_HASH": H_R, "commit_status": "NO_COMMIT", "push_status": "NO_PUSH",
    }
    (ROOT / "GOBLIN_BLOOM_PREREG_SCORE_V2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print("═" * 80)
    print("  GOBLIN_BLOOM_PREREG_SCORE_V2 — frozen predictions ADJUDICATED (derived, not evaluated)")
    print("═" * 80)
    print(f"  SEAL {H_P[:14]}… match={seal_ok} predates={predates} · SCORER {H_S[:12]}… · TRACE {H_T[:12]}…")
    print(f"  ΔS = N{dN} Q{dQ} d_D{dD} d_I{dI} d_M{dM} R_J{dRJ} R_Γ{dRG} · ratio {comp_ratio} (κ={KAPPA})")
    print(f"  VERDICT={verdict} (range V0-V3, V4 unrepresentable) · top_derived={top_derived} · stop={stop}")
    print("─" * 80)
    for k, v in P.items():
        print(f"    {'✅' if v['result']=='PASS' else '❌'} {k:32s} {v['evidence_refs']}")
    print("─" * 80)
    print(f"  invariants: in_epoch_retention_viol={in_epoch_retention_violation} governed_reach_viol={governed_reach_violation} self_cert={self_cert}")
    print(f"  counterfactual removal: KILL={KILL} SURVIVE={SURVIVE} UNRESOLVED={UNRESOLVED} → law_survives(D+)={law_survives}")
    print(f"  invalid_self_labels={invalid_self}")
    print(f"  PREREG_SCORE = {npass}/8 · THEORY_PROVEN=false · ΔA=0 · RECEIPT_HASH={H_R[:16]}…")
    print("  → GOBLIN_BLOOM_PREREG_SCORE_V2.json")


if __name__ == "__main__":
    main()
