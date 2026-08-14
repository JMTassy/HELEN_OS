#!/usr/bin/env python3
"""CROSS_MODEL_INDEPENDENCE_V0 — does a different-lineage model buy hypothesis-space coverage?
🔵 OBSERVED · NON_SOVEREIGN · authority=false · claim=NO_CLAIM · ledger_effect=none

Primary endpoint (per operator spec):
    ΔQ_useful,Q|G = | Q_useful^Qwen \\ Q_useful^Gemma |   (marginal USEFUL classes Qwen adds)

Hard laws encoded here:
  - DifferentWeights ⊬ IndependentEvidence  → three counts kept SEPARATE, never a scalar N_eff
  - MoreRawIdeas ⊬ MoreUsefulHypotheses     → union is over QUOTIENT CLASSES, not raw candidates
  - Unclassified ≠ Novel                    → UNCLASSIFIED routes to HOLD, never counted as coverage
  - UNREADABLE ≠ ZERO_CANDIDATES            → 4-state parse; candidate_count=NA on unreadable/error
The quotient here is PREDICATE bucketing (~_O^predicate), NOT a metric quotient — named honestly,
and its source is hashed into the QID so changing it changes the contract (audit fix).
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import re
import urllib.error
import urllib.request

OLLAMA = "http://localhost:11434/api/generate"

# ── FROZEN observation contract ───────────────────────────────────────────────
TOPIC = ("Propose the next GLOBAL graph-admissibility invariant that a checker enforcing "
         "{capability double-spend, provenance cycle, rootless-orphan, unwarranted temporal "
         "persistence, non-commuting effects, warrant-value rebinding} still MISSES. For each: "
         "name the pathology, a 3-4 node graph where all existing gates pass but it must be "
         "rejected, and a refusal code. Output ONLY a JSON array of objects {\"idea\": \"...\"}. "
         "Start with [ and end with ].")

# predicate taxonomy: which invariant-FAMILY a proposal targets (the observational class)
_TAXONOMY = {
    "CAPABILITY":  ("capabilit", "double-spend", "double spend", "token", "linear", "affine", "consum"),
    "PROVENANCE":  ("provenance", "root", "ancestor", "derivation", "self-support", "circular", "cycle"),
    "TEMPORAL":    ("temporal", "time", "persistence", "t1", "t2", "timestamp", "causal", "folding"),
    "EFFECT":      ("effect", "mutation", "slot", "commut", "conflict", "concurrent", "race"),
    "WARRANT":     ("warrant", "signature", "rebind", "value", "sign", "attest"),
    "IDENTITY":    ("identity", "handle", "tenant", "boundary", "mirror", "spoof", "forge"),
    "ORDERING":    ("ordering", "sequence", "order", "read-time", "read time", "read-conflict", "read access"),
}

def quotient_mapper(idea: str) -> str:
    """~_O^predicate — map a proposal to its observational class by structural predicate.
    Unknown wording → UNCLASSIFIED (which is HELD, never counted as novel coverage)."""
    t = idea.lower()
    for cls, keys in _TAXONOMY.items():
        if any(k in t for k in keys):
            return cls
    return "UNCLASSIFIED"

# QID binds observation contract + taxonomy + the mapper SOURCE (audit fix: mapper must be in QID)
_MAPPER_SRC = inspect.getsource(quotient_mapper)
QID = hashlib.sha256(
    json.dumps({"topic": TOPIC, "taxonomy": _TAXONOMY, "mapper": _MAPPER_SRC}, sort_keys=True).encode()
).hexdigest()[:16]

# 4-state parse classification (candidate_count = None means NA)
def classify_and_extract(model: str, prompt: str, seed: int, timeout: int = 300):
    body = {"model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1500, "seed": seed}, "think": False}
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as e:
        return {"state": "EXECUTION_ERROR", "candidate_count": None, "ideas": [], "err": str(e)[:120]}
    try:
        text = json.loads(raw).get("response", "")
    except json.JSONDecodeError:
        return {"state": "UNREADABLE", "candidate_count": None, "ideas": []}
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    s, e = text.find("["), text.rfind("]")
    if s == -1 or e <= s:
        return {"state": "UNREADABLE", "candidate_count": None, "ideas": []}
    try:
        arr = json.loads(text[s:e + 1])
    except json.JSONDecodeError:
        return {"state": "UNREADABLE", "candidate_count": None, "ideas": []}
    # Robust extraction: a proposal may be a plain string OR a multi-field object
    # ({pathology, graph, code}, not just {"idea"}). Keying only on "idea" wrongly reports
    # PARSED_EMPTY on valid content — the UNREADABLE≠ZERO / instrument-defect trap. Join all
    # string fields so the quotient mapper sees the full proposal text.
    ideas = []
    for p in arr:
        if isinstance(p, dict):
            val = p.get("idea") or " | ".join(str(v) for v in p.values() if isinstance(v, str) and v.strip())
        elif isinstance(p, str):
            val = p
        else:
            val = ""
        if val and val.strip():
            ideas.append(val.strip())
    state = "PARSED_NONEMPTY" if ideas else "PARSED_EMPTY"
    return {"state": state, "candidate_count": len(ideas), "ideas": ideas}


def run_arm(model: str, seeds):
    per_seed, union_classes, useful_classes = [], set(), set()
    completed = parsed = 0
    for sd in seeds:
        r = classify_and_extract(model, TOPIC, sd)
        completed += 1 if r["state"] not in ("EXECUTION_ERROR",) else 0
        parsed += 1 if r["state"] in ("PARSED_NONEMPTY", "PARSED_EMPTY") else 0
        classes = {quotient_mapper(i) for i in r["ideas"]}
        union_classes |= classes
        useful_classes |= (classes - {"UNCLASSIFIED"})     # Unclassified ≠ Novel → excluded from coverage
        per_seed.append({"seed": sd, "state": r["state"], "candidate_count": r["candidate_count"],
                         "classes": sorted(classes)})
    n = len(seeds)
    return {
        "model": model, "seeds": list(seeds), "per_seed": per_seed,
        "execution_yield": completed / n, "parse_yield": (parsed / completed) if completed else 0.0,
        "Q_union": sorted(union_classes), "Q_useful": sorted(useful_classes),
        "unclassified_present": "UNCLASSIFIED" in union_classes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46])
    ap.add_argument("--label", default="")
    args = ap.parse_args()
    print(f"[CROSS_MODEL_INDEPENDENCE_V0] QID={QID}  model={args.model}  seeds={args.seeds}")
    res = run_arm(args.model, args.seeds)
    out = {"qid": QID, "arm": args.label or args.model, **res,
           "note": "N_generators=1 · N_comp_roots=1 · N_evidence_roots=1 (single corpus) — NEVER collapse"}
    import pathlib
    p = pathlib.Path(f"artifacts/local_first/cmi_v0_{(args.label or args.model).replace('/', '_').replace(':','_')}.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    print(f"  execution_yield={res['execution_yield']:.2f}  parse_yield={res['parse_yield']:.2f}")
    print(f"  Q_union   = {res['Q_union']}")
    print(f"  Q_useful  = {res['Q_useful']}  (UNCLASSIFIED excluded)")
    print(f"  written   -> {p}")


if __name__ == "__main__":
    main()
