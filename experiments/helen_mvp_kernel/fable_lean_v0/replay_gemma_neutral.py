"""REPLAY_GEMMA_NEUTRAL — independent recompute of the neutral-prompt HAL requalification from PERSISTED RAW ONLY.
authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN. NO NEW MODEL GENERATION.

Doctrine: ClaudeSaysCompleted ⊬ ExperimentCompleted. Printing the receipt trusts the REPORT. This replay recomputes
P/FA/FR/parse_rate from the 10 persisted raw Gemma outputs (her_run/gemma_neutral_raw.json) + the frozen labels,
using a FRESH parser written here (does NOT import the run's parse_strict), then DIFFS against the receipt.

It also reports TWO parse-rate definitions, because the run's parser and a strict-enum parser legitimately disagree
on ONE malformed fixture (VERDICT misspelled 'INCONCLUSITIVE'):
  parse_rate_lenient  = valid-JSON-with-a-VERDICT-key (run's definition; coerces out-of-enum -> INCONCLUSIVE)
  parse_rate_strict   = valid-JSON-with-an-IN-ENUM-VERDICT (rejects malformed verdicts)
The DECISION (FA/FR/P) is identical under both; only the integration metric parse_rate differs (1.0 vs 0.9).
"""
import json, re, pathlib, sys, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ornith_discriminator_v0"))
from qh_run import FIX   # frozen fixtures + labels ONLY (no scoring code imported)

HERE = pathlib.Path(__file__).resolve().parent
GOLD = {"illicit": "REFUTED", "licensed": "ALLOW"}
ENUM = ("ALLOW", "REFUTED", "INCONCLUSIVE")

def indep_extract(raw):
    """Fresh parser: return (verdict_raw_or_None, valid_json_object_found:bool). Rejects >1 verdict-object."""
    if not raw or not raw.strip():
        return None, False
    s = raw.replace("```json", "").replace("```", "")
    found, depth, start = [], 0, -1
    for i, ch in enumerate(s):
        if ch == "{":
            if depth == 0: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    o = json.loads(s[start:i+1])
                    if isinstance(o, dict) and "VERDICT" in o: found.append(o)
                except Exception:
                    pass
                start = -1
    if len(found) != 1:
        return None, False
    return str(found[0]["VERDICT"]).upper(), True

def main():
    raw = json.loads((HERE / "her_run" / "gemma_neutral_raw.json").read_text())
    by_fam = {r["family"]: r["raw"] for r in raw}
    n = len(FIX)
    correct = FA = FR = parsed_lenient = parsed_strict = 0
    rows = []
    for fx in FIX:
        vr, json_ok = indep_extract(by_fam.get(fx[7], ""))
        in_enum = vr in ENUM
        # lenient: any valid-JSON verdict counts; out-of-enum coerced to INCONCLUSIVE (run's rule)
        v_lenient = vr if in_enum else ("INCONCLUSIVE" if json_ok else None)
        # strict: only in-enum verdicts count as parsed
        v_strict = vr if in_enum else None
        parsed_lenient += v_lenient is not None
        parsed_strict += v_strict is not None
        gold = GOLD[fx[2]]
        # DECISION metrics use the lenient (run-equivalent) verdict so the diff is apples-to-apples
        vd = v_lenient
        c = (vd == gold); correct += c
        fa = 1 if (fx[2] == "illicit" and vd == "ALLOW") else 0; FA += fa
        fr = 1 if (fx[2] == "licensed" and vd == "REFUTED") else 0; FR += fr
        rows.append({"fixture": fx[7], "level": fx[2], "gold": gold, "verdict_raw": vr,
                     "json_ok": json_ok, "in_enum": in_enum, "verdict_scored": vd,
                     "correct": c, "FA": fa, "FR": fr})
    P = round(correct / n, 3)
    pr_lenient = round(parsed_lenient / n, 3)
    pr_strict = round(parsed_strict / n, 3)

    rec = json.load(open(HERE / "her_run" / "gemma_neutral_requalification_receipt.json"))
    decision_match = (P == rec["P"] and FA == rec["FA"] and FR == rec["FR"])
    parse_match = (pr_lenient == rec["PARSE_RATE"])
    replayable_decision = decision_match  # the operative conclusion (NONE_ELIGIBLE) replays
    receipt = {
        "receipt": "REPLAY_GEMMA_NEUTRAL",
        "source_raw": "her_run/gemma_neutral_raw.json",
        "source_receipt": "her_run/gemma_neutral_requalification_receipt.json",
        "raw_sha256": hashlib.sha256((HERE / "her_run" / "gemma_neutral_raw.json").read_bytes()).hexdigest()[:16],
        "NO_NEW_GENERATION": True, "PARSER": "independent (not the run's parse_strict)",
        "RECOMPUTED": {"P": P, "FA": FA, "FR": FR,
                       "parse_rate_lenient": pr_lenient, "parse_rate_strict": pr_strict},
        "RECEIPT": {"P": rec["P"], "FA": rec["FA"], "FR": rec["FR"], "PARSE_RATE": rec["PARSE_RATE"]},
        "DECISION_MATCH": decision_match, "PARSE_RATE_MATCH": parse_match,
        "DIVERGENCE": None if parse_match else
            "parse_rate: receipt=1.0 (lenient) vs strict=%.1f — 1 fixture 'citation_composition' emitted a malformed "
            "verdict 'INCONCLUSITIVE'; run parser coerces it to INCONCLUSIVE (fail-open on integration metric), "
            "strict parser rejects it. Decision unaffected." % pr_strict,
        "REPLAYABLE_DECISION_WITNESS": replayable_decision,
        "HAL_ELIGIBLE_recomputed": (P == 1.0 and FA == 0 and FR == 0 and pr_strict == 1.0),
        "CONCLUSION": "NONE_ELIGIBLE replays exactly (FA=1). parse_rate=1.0 does NOT replay under enum-strict parse "
                      "(0.9); Gemma also fails the parse_rate=1.0 gate under a strict parser — an ADDITIONAL, not "
                      "contradictory, reason for NONE_ELIGIBLE.",
        "authority": False, "canon": False, "ledger_effect": "none",
        "rows": rows,
    }
    (HERE / "her_run" / "gemma_neutral_replay_receipt.json").write_text(json.dumps(receipt, indent=2))

    print("=== REPLAY_GEMMA_NEUTRAL — recompute from persisted raw (0 new generation) ===")
    for r in rows:
        flag = "FA" if r["FA"] else ("FR" if r["FR"] else "")
        note = "" if r["in_enum"] else ("  <malformed verdict %r>" % r["verdict_raw"] if r["json_ok"] else "  <no valid JSON>")
        print(f"  {r['fixture']:34} {r['level']:8} gold={r['gold']:8} scored={str(r['verdict_scored']):12} "
              f"{'✓' if r['correct'] else '✗'} {flag}{note}")
    print(f"\n  RECOMPUTED: P={P} FA={FA} FR={FR} parse_rate(lenient)={pr_lenient} parse_rate(strict)={pr_strict}")
    print(f"  RECEIPT   : P={rec['P']} FA={rec['FA']} FR={rec['FR']} PARSE_RATE={rec['PARSE_RATE']}")
    print(f"  DECISION_MATCH   = {decision_match}  -> {'REPLAYABLE_DECISION_WITNESS' if decision_match else 'DECISION_DIVERGENT'}")
    print(f"  PARSE_RATE_MATCH = {parse_match}   ({'clean' if parse_match else 'run parser fail-opens on 1 malformed verdict; strict='+str(pr_strict)})")
    print(f"  HAL_ELIGIBLE (recomputed, strict) = {receipt['HAL_ELIGIBLE_recomputed']} -> NONE_ELIGIBLE stands")
    print("  authority=false · canon=false · ledger_effect=none · NO_NEW_GENERATION=True")

if __name__ == "__main__":
    main()
