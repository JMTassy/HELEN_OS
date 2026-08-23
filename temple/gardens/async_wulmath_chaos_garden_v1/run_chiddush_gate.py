#!/usr/bin/env python3
"""
HARD CHIDDUSH GATE over the 20 chaos objects. Replaces self-report with a real
adversarial counterfeit test:

  R(X)=1  iff  D≠∅ ∧ M≠∅ ∧ C≠∅ ∧ F≠∅        (testable — structural completeness)
  SURVIVES iff ∃x*: O_{x*}(g) ≠ O_{x*}(c)     (novel — HAL fails to collapse g into a boring c)
  ∀x O_x(g)=O_x(c)  ⇒  RENAMING_ONLY → COMPOST

Garden fitness = novel_distinction × survival_under_counterfeit × discriminability × reproductive_potential
Freezes top-3 survivors → CHIDDUSH_S0.json (real seeds for the Genesis Loop).
authority=false · NO_CLAIM · ΔA=0.
"""
import json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
OBJ = ROOT / "objects"
OLLAMA = "http://localhost:11434/api/chat"
HAL = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"

SYS = ("You are the CHIDDUSH GATE, an adversarial mathematical referee. Given a "
       "Garden object g, your job is to COLLAPSE it: construct the nearest ordinary "
       "known structure c (its boring counterfeit), then decide whether any cheap "
       "observation/test x* actually distinguishes g from c. If g is just c wearing "
       "a strange name, say RENAMING_ONLY. Be strict: weirdness is not novelty. "
       "Emit only the verdict block.")

FMT = ("COUNTERFEIT: <the ordinary known structure g reduces to>\n"
       "DISCRIMINATOR: <cheapest x* where an observation of g differs from c, or NONE>\n"
       "VERDICT: <SURVIVES | RENAMING_ONLY | EVIDENCE_NEEDED>\n"
       "WHY: <one line>\nEND")


def ollama(user, timeout=300):
    body = json.dumps({"model": HAL, "stream": False, "think": False,
        "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": user}],
        "options": {"temperature": 0.4, "num_predict": 350}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: d = json.loads(r.read())
    m = d.get("message", {}) or {}
    return m.get("content") or m.get("thinking") or ""


def field(t, k):
    m = re.search(rf"^{k}:\s*(.+?)\s*$", t, re.I | re.M); return m.group(1).strip() if m else ""


def main():
    objs = []
    for f in sorted(OBJ.glob("*.json")):
        o = json.loads(f.read_text())
        raw = o.get("raw", "")
        objs.append({"stream": o["stream"], "epoch": o["epoch"], "name": o["name"],
                     "D": o.get("strange", ""), "M": o.get("formal_seed", ""),
                     "C": field(raw, "COUNTERFEIT"), "F": field(raw, "BREAK_IT")})
    print("═" * 66)
    print(f"  HARD CHIDDUSH GATE — {len(objs)} objects, HAL adversarial counterfeit test")
    print("═" * 66, flush=True)
    results = []
    for o in objs:
        if not o["name"]:
            continue
        # R(X): structural completeness (testable)
        complete = all([o["D"], o["M"], o["C"], o["F"]])
        u = (f"Garden object g:\nNAME: {o['name']}\nFORMAL_SEED: {o['M']}\n"
             f"STRANGE_PROPERTY: {o['D']}\n\nCollapse it.\n{FMT}")
        try: raw = ollama(u); err = None
        except Exception as e: raw, err = "", str(e)[:60]
        verdict = field(raw, "VERDICT").upper() or ("ERROR" if err else "EVIDENCE_NEEDED")
        disc = field(raw, "DISCRIMINATOR")
        survives = "SURVIV" in verdict
        renaming = "RENAMING" in verdict
        discriminable = bool(disc) and disc.upper() != "NONE"
        # Garden fitness (reproductive, NOT truth)
        fitness = round((1.0 if complete else 0.4)
                        * (1.0 if survives else (0.0 if renaming else 0.4))
                        * (1.0 if discriminable else 0.5)
                        * (1.0 if o["M"] else 0.3), 3)
        r = {**o, "R_complete": complete, "verdict": verdict, "counterfeit_hal": field(raw, "COUNTERFEIT"),
             "discriminator": disc, "discriminable": discriminable, "fitness": fitness, "err": err}
        results.append(r)
        tag = "🌱" if survives else ("🍄" if renaming else "🟡")
        print(f"{tag} [{o['stream']} E{o['epoch']:02d}] «{o['name'][:34]:34s}» "
              f"R={int(complete)} {verdict:14s} fit={fitness}  x*={disc[:40]}", flush=True)

    survivors = sorted([r for r in results if "SURVIV" in r["verdict"]],
                       key=lambda r: -r["fitness"])
    compost = [r for r in results if "RENAMING" in r["verdict"]]
    top3 = survivors[:3] if len(survivors) >= 3 else sorted(results, key=lambda r: -r["fitness"])[:3]

    # freeze S0 (real hard-gated seeds) for the Genesis Loop
    S0 = [{"id": f"S_{i}", "q": f"What theorem/object does «{r['name']}» make available that its "
           f"counterfeit «{r['counterfeit_hal'][:40]}» cannot?", "g": r["M"],
           "c": r["counterfeit_hal"], "lineage": [r["name"]], "origin": r["stream"],
           "discriminator": r["discriminator"], "fitness": r["fitness"]} for i, r in enumerate(top3)]
    (ROOT / "CHIDDUSH_S0.json").write_text(json.dumps(S0, indent=2, ensure_ascii=False))

    receipt = {"schema": "HARD_CHIDDUSH_GATE_RECEIPT", "authority": False, "canon": False,
        "claim": "NO_CLAIM", "authority_delta": 0, "fable_calls": 0,
        "objects_tested": len(results),
        "survives": len(survivors), "renaming_only_compost": len(compost),
        "evidence_needed": sum(1 for r in results if "EVIDEN" in r["verdict"]),
        "errors": sum(1 for r in results if r["verdict"] == "ERROR"),
        "hard_chiddush_count": len(survivors),
        "note": "hard gate replaces the self-reported 20; SURVIVES = HAL could not collapse g into a boring counterfeit + a discriminator exists.",
        "S0_top3": [{"name": r["name"], "fitness": r["fitness"], "verdict": r["verdict"],
                     "discriminator": r["discriminator"]} for r in top3],
        "all_verdicts": [{"name": r["name"], "stream": r["stream"], "verdict": r["verdict"],
                          "fitness": r["fitness"]} for r in results]}
    (ROOT / "HARD_CHIDDUSH_GATE_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print("\n" + "═" * 66)
    print(f"🌈 HARD CHIDDUSH: {len(survivors)}/{len(results)} survive · {len(compost)} composted (RENAMING_ONLY)")
    print("🌱 S0 (top-3 real seeds → CHIDDUSH_S0.json):")
    for r in top3: print(f"   «{r['name']}»  fit={r['fitness']}  {r['verdict']}")


if __name__ == "__main__":
    main()
