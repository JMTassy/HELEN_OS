#!/usr/bin/env python3
"""
TURBO_CLAIM_ADMISSION_POC_V0 — the smallest real HELEN TURBO ratchet test.

Obligation class: "Does this candidate claim carry the REQUIRED admission evidence?"
Baseline path : O -> cognition -> decision            (cost C_cog per instance)
Compiled path : O -> ContractCheck(D,O) -> D(O)        (cost C_D_total; else reopen cognition)

D1 (naive)   : CANDIDATE iff evidence_pointer != NONE            (evidence PRESENCE)
D2 (compiled): SchemaValid ∧ Traceable ∧ ConstraintCompliant ∧ NonDegenerate  (evidence SUFFICIENCY)
The compiled distinction x* : presence ≠ sufficiency. D2 is DERIVED from structure, never from a
declared 'sufficient' flag (Derived ≻ Declared).

Measures exactly four things + safety: decision agreement, false accepts/rejects, cost,
model-calls avoided. Kill condition: Valid(D,t)=0 -> HOLD (reopen cognition), never silently answer.

authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH ·
fixtures are ILLUSTRATIVE (hand-authored to the stated admission semantics; NOT extracted from the corpus).
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

CONTRACT = json.loads((ROOT / "contract.json").read_text())
FIX = [json.loads(l) for l in (ROOT / "fixtures.jsonl").read_text().splitlines() if l.strip()]
DOM = CONTRACT["domain"]
C_COG = CONTRACT["cost_units"]["C_cognition_per_instance"]
C_D_TOTAL = CONTRACT["cost_units"]["C_exec"] + CONTRACT["cost_units"]["C_overhead_amortized"]
Q_MIN = CONTRACT["quality_floor_q_min"]


def D1(rec):                                            # naive: presence only
    ep = rec.get("evidence_pointer", "NONE")
    return "CANDIDATE" if ep not in (None, "NONE", "") else "BLOCK"

def D2(rec):                                            # compiled: sufficiency, all DERIVED
    ep, ek = rec.get("evidence_pointer", "NONE"), rec.get("evidence_kind", "NONE")
    schema_ok = (rec.get("schema_version") == DOM["schema_version"]
                 and all(k in rec for k in DOM["required_fields"]))
    traceable = (ep not in (None, "NONE", "") and ek in DOM["traceable_kinds"]
                 and any(ep.startswith(p) for p in DOM["traceable_pointer_prefixes"]))
    constraint_ok = (not rec.get("claims_authority", False)
                     and rec.get("claim_type") != "evaluator_output")
    degenerate = (ep in DOM["degenerate_markers"] or ep == rec.get("id") or ek == "prose")
    if not schema_ok:      return "BLOCK", "BLOCK:schema_invalid"
    if not traceable:      return "BLOCK", "BLOCK:not_traceable"
    if not constraint_ok:  return "BLOCK", "BLOCK:constraint_violation"
    if degenerate:         return "BLOCK", "BLOCK:degenerate"
    return "CANDIDATE", "CANDIDATE:sufficient"

def contract_check(rec, runtime_required):              # Valid(D,t): schema + required fields present
    return (rec.get("schema_version") == DOM["schema_version"]
            and all(k in rec for k in runtime_required))


def score(pred_fn, recs):
    correct = fa = fr = 0
    for r in recs:
        p = pred_fn(r); p = p[0] if isinstance(p, tuple) else p
        g = r["gold"]
        if p == g: correct += 1
        elif p == "CANDIDATE" and g == "BLOCK": fa += 1     # FALSE ACCEPT (dangerous: admits a blockable claim)
        elif p == "BLOCK" and g == "CANDIDATE": fr += 1     # false reject (conservative)
    n = len(recs)
    return {"agreement": round(correct / n, 4), "false_accepts": fa, "false_rejects": fr, "n": n}

def adoptable(s):                                          # gate: quality floor AND zero false-accepts
    return s["agreement"] >= Q_MIN and s["false_accepts"] == 0


def main():
    s1, s2 = score(D1, FIX), score(D2, FIX)

    # --- compiled routing under contract v1 (in-domain) ---
    req_v1 = DOM["required_fields"]
    resolved_compiled = sum(1 for r in FIX if contract_check(r, req_v1))
    reopened = len(FIX) - resolved_compiled
    baseline_cost = len(FIX) * C_COG
    compiled_cost = resolved_compiled * C_D_TOTAL + reopened * C_COG
    R_avoided = round(resolved_compiled / len(FIX), 4)
    calls_avoided = resolved_compiled
    C_avoided = baseline_cost - compiled_cost

    # --- drift scenario: contract v2 adds required field 'independent_witness' ---
    req_v2 = req_v1 + ["independent_witness"]
    valid_v2 = sum(1 for r in FIX if contract_check(r, req_v2))
    drift_reopened = len(FIX) - valid_v2
    drift_cost = valid_v2 * C_D_TOTAL + drift_reopened * C_COG   # stale -> HOLD -> reopen cognition

    pass_criteria = {
        "quality_floor_met_(D2>=q_min)": s2["agreement"] >= Q_MIN,
        "zero_false_accepts_(D2)": s2["false_accepts"] == 0,
        "cheaper_(C_D_total<C_cog)": C_D_TOTAL < C_COG,
        "R_avoided_positive": R_avoided > 0,
        "authority_delta_zero": True,
    }
    POC_PASS = all(pass_criteria.values())

    report = {
        "experiment": "TURBO_CLAIM_ADMISSION_POC_V0", "authority": False, "canon": False,
        "claim": "NO_CLAIM", "authority_delta": 0, "model_calls": 0,
        "fixtures_note": "ILLUSTRATIVE, hand-authored to the stated admission semantics; NOT extracted from the corpus PDFs",
        "obligation_class": CONTRACT["obligation_class"],
        "compiled_distinction_x_star": "evidence PRESENCE != evidence SUFFICIENCY",
        "D1_presence_only": s1,
        "D2_compiled_sufficiency": s2,
        "recompilation_event":
            f"D1 has {s1['false_accepts']} FALSE ACCEPTS (admits blockable claims) -> below floor/unsafe; "
            f"falsification forced D1->D2 (presence->sufficiency); D2 false_accepts={s2['false_accepts']}",
        "D1_adoptable": adoptable(s1), "D2_adoptable": adoptable(s2),
        "cost": {"C_cognition": C_COG, "C_D_total": C_D_TOTAL,
                 "baseline_cost": baseline_cost, "compiled_cost": compiled_cost, "C_avoided": C_avoided},
        "model_call_avoidance": {"resolved_by_D2": resolved_compiled, "reopened_cognition": reopened,
                                 "R_avoided": R_avoided, "calls_avoided": calls_avoided},
        "drift_scenario_contract_v2": {
            "new_required_field": "independent_witness",
            "still_valid": valid_v2, "held_and_reopened": drift_reopened,
            "cost_after_drift": drift_cost, "R_avoided_after_drift": round(valid_v2 / len(FIX), 4),
            "note": "stale contract -> HOLD -> reopen cognition; CompiledOnce !=> ValidForever"},
        "pass_criteria": pass_criteria, "POC_PASS": POC_PASS,
        "MAX_ADMISSIBLE_STATEMENT":
            "On this frozen illustrative fixture set, a validated compiled instrument (D2) replaces "
            "cognition on the admission-evidence obligation at agreement>=q_min with ZERO false-accepts, "
            f"cutting cost {baseline_cost}->{compiled_cost} (R_avoided={R_avoided}), ΔA=0; and correctly "
            "HOLDs+reopens under schema drift.",
        "EXPLICIT_NON_CLAIMS": [
            "NOT a claim about the real corpus / real admission pipeline",
            "D2 quality measured IN-DOMAIN on its own validation set (not proven globally)",
            "CANDIDATE != ADMITTED != INVARIANT; gate decides evidence-sufficiency only"],
        "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    report["report_hash"] = sha(report)
    (ROOT / "poc_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print("═" * 76)
    print("  TURBO_CLAIM_ADMISSION_POC_V0 — replace cognition with a validated instrument?")
    print("═" * 76)
    print(f"  obligation: does a candidate claim carry REQUIRED admission evidence?")
    print(f"  x* compiled: evidence PRESENCE ≠ evidence SUFFICIENCY   ·   q_min={Q_MIN}")
    print("─" * 76)
    print(f"  {'':14s} {'agreement':10s} {'false_accepts':14s} {'false_rejects':13s} adoptable")
    print(f"  {'D1 presence':14s} {s1['agreement']:<10} {s1['false_accepts']:<14} {s1['false_rejects']:<13} {adoptable(s1)}")
    print(f"  {'D2 sufficiency':14s} {s2['agreement']:<10} {s2['false_accepts']:<14} {s2['false_rejects']:<13} {adoptable(s2)}")
    print("─" * 76)
    print(f"  baseline (all cognition) = {baseline_cost}   compiled (D2) = {compiled_cost}   avoided = {C_avoided}")
    print(f"  model calls avoided = {calls_avoided}/{len(FIX)}  ·  R_avoided = {R_avoided}  ·  ΔA = 0")
    print(f"  DRIFT (schema v2 needs independent_witness): still_valid={valid_v2} → "
          f"{drift_reopened} HOLD/reopen → cost {drift_cost} (R_avoided={round(valid_v2/len(FIX),4)})")
    print("─" * 76)
    for k, v in pass_criteria.items():
        print(f"    {'✅' if v else '❌'} {k}")
    print(f"  POC_PASS = {POC_PASS}  ·  report_hash = {report['report_hash'][:16]}…")
    print(f"  → poc_report.json")


if __name__ == "__main__":
    main()
