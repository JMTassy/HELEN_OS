#!/usr/bin/env python3
"""
V3 scorer — mechanical, model-blind, frozen with the instrument.
Modes:
  python3 scorer.py freeze     -> compute + print the 7 hashes, run the 4
                                  negative controls, STOP (no model contact)
  python3 scorer.py score RUN  -> score a blind run dir (run_A|run_B)
NON_SOVEREIGN · authority=false.
"""
import hashlib, json, pathlib, random, sys

HERE = pathlib.Path(__file__).resolve().parent
W = {"c": 0.30, "s": 0.20, "r": 0.15, "b": 0.20, "a": 0.15}

def H(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]

def load(name):
    return (HERE / name).read_bytes()

def fixtures(name="fixtures_test.jsonl"):
    return [json.loads(l) for l in (HERE / name).read_text().splitlines() if l.strip()]

def score_item(fx, cand):
    if not isinstance(cand, dict):
        return {"c": 0, "s": 0, "r": 0, "b": 0, "a": 0, "valid": 0}
    try:
        cls = str(cand.get("epistemic_class", "")).upper()
        sup = (str(cand.get("supported_part", "")) + " "
               + str(cand.get("unsupported_part", ""))).lower()
        mw = (str(cand.get("missing_witness", "")) + " "
              + str(cand.get("unsupported_part", ""))).lower()
        roots = int(cand.get("independent_roots", -1))
        ab = bool(cand.get("abstain"))
    except Exception:
        return {"c": 0, "s": 0, "r": 0, "b": 0, "a": 0, "valid": 0}
    return {"c": int(cls == fx["gold_class"]),
            "s": int(any(k in sup for k in fx["scope_keys"])),
            "r": int(roots == fx["gold_roots"]),
            "b": int(any(k in mw for k in fx["bridge_keys"])),
            "a": int(ab == fx["gold_abstain"]), "valid": 1}

def q_of(scores):
    return sum(sum(W[k] * s[k] for k in W) for s in scores) / len(scores)

# ── negative controls (run on TEST set, no model) ──
def control_candidates(kind, fxs, seed=0):
    rng = random.Random(seed)
    out = []
    for fx in fxs:
        if kind == "ALWAYS_ADMIT":
            out.append({"epistemic_class": "EARNED", "supported_part": "", "unsupported_part": "",
                        "independent_roots": 1, "missing_witness": "", "abstain": False})
        elif kind == "ALWAYS_REJECT":
            out.append({"epistemic_class": "REFUTED", "supported_part": "", "unsupported_part": "",
                        "independent_roots": 1, "missing_witness": "", "abstain": True})
        elif kind == "RANDOM_VALID_CLASS":
            out.append({"epistemic_class": rng.choice(["EARNED", "CONDITIONAL", "OPEN", "REFUTED"]),
                        "supported_part": "", "unsupported_part": "",
                        "independent_roots": rng.choice([1, 2]), "missing_witness": "",
                        "abstain": rng.choice([True, False])})
        else:  # SURFACE_KEYWORD_HEURISTIC — echoes the item text into every field
            out.append({"epistemic_class": "CONDITIONAL",
                        "supported_part": fx["source"], "unsupported_part": fx["claim"],
                        "independent_roots": 1, "missing_witness": fx["claim"] + " " + fx["source"],
                        "abstain": True})
    return out

def freeze():
    parts = [load("system_contract.txt"), load("output_schema.json"),
             load("template.txt"), load("fixtures_test.jsonl"), load("rubric.json"),
             load("runtime_contract.json"), load("PREREGISTRATION.md")]
    names = ["SYSTEM_HASH", "SCHEMA_HASH", "TEMPLATE_HASH", "FIXTURE_HASH",
             "RUBRIC_HASH", "RUNTIME_HASH", "PREREGISTRATION_HASH"]
    hs = {}
    for n, p in zip(names, parts):
        hs[n] = H(p)
    hs["EXPERIMENT_HASH"] = H(b"||".join(parts))
    for n in names + ["EXPERIMENT_HASH"]:
        print(f"  {n:22} = {hs[n]}")
    fxs = fixtures()
    print("  NEGATIVE CONTROLS (ceiling 0.55):")
    worst = 0.0
    for kind in ("ALWAYS_ADMIT", "ALWAYS_REJECT", "RANDOM_VALID_CLASS",
                 "SURFACE_KEYWORD_HEURISTIC"):
        q = q_of([score_item(fx, c) for fx, c in zip(fxs, control_candidates(kind, fxs))])
        worst = max(worst, q)
        print(f"    {kind:26} Q = {q:.3f}  {'OK' if q <= 0.55 else 'CEILING BREACH'}")
    verdict = "INSTRUMENT_ADEQUATE" if worst <= 0.55 else "HOLD_INSTRUMENT_WEAK"
    print(f"  CONTROL VERDICT = {verdict}")
    (HERE / "freeze_receipt.json").write_text(json.dumps(
        {"hashes": hs, "control_worst_Q": round(worst, 3), "verdict": verdict}, indent=2))
    print("  freeze_receipt.json written — STOP. No model has been called.")

def score_run(run):
    fxs = fixtures()
    outs = json.loads((HERE / run / "outputs.json").read_text())
    scores = [score_item(fx, outs.get(fx["fixture_id"])) for fx in fxs]
    valid = sum(s["valid"] for s in scores) / len(scores)
    by_fam = {}
    for fx, s in zip(fxs, scores):
        by_fam.setdefault(fx["family"], []).append(sum(W[k] * s[k] for k in W))
    rep = {"run": run, "Q_discrim": round(q_of(scores), 4),
           "Q_formatting": round(valid, 3),
           "by_family": {k: round(sum(v) / len(v), 3) for k, v in by_fam.items()},
           "per_item": {fx["fixture_id"]: s for fx, s in zip(fxs, scores)}}
    (HERE / run / "score.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps({k: rep[k] for k in ("run", "Q_discrim", "Q_formatting", "by_family")}))

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "score":
        score_run(sys.argv[2])
    else:
        freeze()
