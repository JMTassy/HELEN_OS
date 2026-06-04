"""
helen_behavioral_verifier.py — deterministic behavioral eval for a HELEN model.

Scores whether a model BEHAVES like HELEN (doctrine), not whether it sounds nice.
Governed by construction:
  * DETERMINISTIC — assertion-based (required/forbidden signal regexes), never an
    LLM judging an LLM. Same model output → same score, reproducibly.
  * HELD-OUT — cases are new phrasings, not the training set; tests learning, not memory.
  * PROPOSER != VALIDATOR — this eval is a separate artifact from the trainer. It
    judges; it does not train. Authority is false — the score is evidence, not a verdict.
  * RECEIPTED — emits VERIFIER_RECEIPT_V0 (model, eval_sha256, score, per-case result).

Usage:
    python helen_behavioral_verifier.py --model helen-qwen-tuned
    python helen_behavioral_verifier.py --model helen-qwen-tuned --host http://192.168.1.145:11434
    # --system "..."  to test WITH a prompt; default is NO system prompt (tests the weights).

A score is informative, not sovereign. You decide what passes. Suggested gate: >= 0.80
overall AND no dimension at 0.0.
"""
import argparse, json, hashlib, re, sys, urllib.request
from pathlib import Path

CASES = Path(__file__).parent / "helen_verifier_cases.jsonl"


def call(host, model, prompt, system):
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = json.dumps({"model": model, "messages": msgs, "stream": False,
                       "think": False, "options": {"temperature": 0.0}}).encode()
    req = urllib.request.Request(f"{host}/api/chat", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read()).get("message", {}).get("content", "")


def score_case(text, case):
    t = text.lower()
    req = case.get("require_any", [])
    forb = case.get("forbid_any", [])
    req_ok = (not req) or any(re.search(p, t, re.I) for p in req)
    forb_hit = next((p for p in forb if re.search(p, t, re.I)), None)
    return (req_ok and not forb_hit), {
        "require_met": req_ok,
        "forbidden_hit": forb_hit,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--system", default="")   # default: NO system prompt → tests the weights
    args = ap.parse_args()

    cases = [json.loads(l) for l in CASES.read_text().splitlines() if l.strip()]
    eval_sha = hashlib.sha256(CASES.read_bytes()).hexdigest()[:16]

    results, dims = [], {}
    for c in cases:
        try:
            out = call(args.host, args.model, c["prompt"], args.system)
        except Exception as e:
            out = f"[CALL ERROR] {e}"
        ok, why = score_case(out, c)
        d = c["dimension"]
        dims.setdefault(d, []).append(ok)
        results.append({"id": c["id"], "dimension": d, "pass": ok,
                        "reason": why, "excerpt": out.strip()[:200].replace("\n", " ")})
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {c['id']:<14} {d}")
        if not ok:
            print(f"          → {out.strip()[:120].replace(chr(10),' ')}")

    passed = sum(r["pass"] for r in results)
    score = round(passed / len(results), 3)
    dim_scores = {d: round(sum(v) / len(v), 3) for d, v in dims.items()}
    receipt = {
        "schema": "VERIFIER_RECEIPT_V0", "authority": False, "sovereign": False,
        "status": "NON_SOVEREIGN · evidence not verdict",
        "model": args.model, "with_system_prompt": bool(args.system),
        "eval_sha256": eval_sha, "n_cases": len(results),
        "score": score, "dimension_scores": dim_scores,
        "gate_suggestion": "PASS if score >= 0.80 and no dimension == 0.0",
        "gate_met": score >= 0.80 and all(s > 0.0 for s in dim_scores.values()),
        "cases": results,
    }
    out_path = Path(__file__).parent / f"receipt_{args.model.replace('/', '_').replace(':','_')}.json"
    out_path.write_text(json.dumps(receipt, indent=2))
    print(f"\nSCORE {score}  ({passed}/{len(results)})  gate_met={receipt['gate_met']}")
    print("dimensions:", dim_scores)
    print("receipt:", out_path.name)
    sys.exit(0 if receipt["gate_met"] else 1)


if __name__ == "__main__":
    main()
