#!/usr/bin/env python3
"""
HAL discrimination pass — SEPARATE SEAT (helen-hal via Ollama).
Reads the distinct PotentialDistinctions produced by Qwen/JESTER and classifies
each. HAL does NOT decide truth and CANNOT mint admission.

Constitutional constraint (frozen):
  no separator was EXECUTED in this run ⇒ OBSERVATION_STATUS ∈
  {NOT_EXECUTED, COUNTERFEIT_WINS, REDUNDANT}. SURVIVED requires
  SEPARATOR_OBSERVED, which is impossible here → SURVIVED is FORBIDDEN.
  A discriminator that exists but was not run ⇒ EVIDENCE_NEEDED, never REFUTED.
  REFUTED requires HAL to construct a separator-counterfeit that defeats the
  discriminator itself. REDUNDANT = collapses to a prior/known distinction.

Run AFTER the Qwen llama-server is stopped (seat freed).
"""
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
RECEIPT = ROOT / "QWEN_JESTER_20E_V0_RECEIPT.json"
OLLAMA = "http://localhost:11434/api/chat"
HAL_MODEL = "helen-hal:latest"

SYSTEM = """You are HAL, a cold adversarial discriminator in a SEPARATE seat
from the JESTER that produced these distinctions. Authority_HAL = 0. You cannot
admit, promote, or mint evidence. For each candidate distinction you receive its
proposed discriminator. Your job:
1. Construct the strongest COUNTERFEIT that keeps the observation but destroys
   the distinction (a world observationally equivalent yet structurally different).
2. State the SEPARATOR (use the given discriminator; strengthen if weak).
3. Set OBSERVATION_STATUS — but note: NO separator was executed in this run, so
   you may ONLY use NOT_EXECUTED, COUNTERFEIT_WINS, or REDUNDANT. SEPARATOR_OBSERVED
   is impossible and forbidden.
4. VERDICT rules (strict):
   - SURVIVED is FORBIDDEN (nothing was observed).
   - REFUTED only if you build a separator-counterfeit that defeats the
     discriminator itself (OBSERVATION_STATUS=COUNTERFEIT_WINS).
   - REDUNDANT if it collapses to a prior/standard distinction.
   - otherwise EVIDENCE_NEEDED (a valid unrun discriminator exists).
Output ONLY one JSON object per request, no prose."""

SCHEMA = """Return ONLY:
{"counterfeit":"<observationally-equivalent world>",
 "separator":"<the discriminating experiment>",
 "observation_status":"NOT_EXECUTED|COUNTERFEIT_WINS|REDUNDANT",
 "verdict":"EVIDENCE_NEEDED|REFUTED|REDUNDANT",
 "reason":"<one sentence>"}"""


def ollama(system, user, timeout=420):
    body = json.dumps({"model": HAL_MODEL, "stream": False, "think": False,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}],
                       "options": {"temperature": 0.3, "num_predict": 500}}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    m = d.get("message", {}) or {}
    return m.get("content") or m.get("thinking") or ""


def extract(t):
    s = t.find("{")
    while s != -1:
        depth = 0
        for i in range(s, len(t)):
            if t[i] == "{":
                depth += 1
            elif t[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(t[s:i + 1])
                    except Exception:
                        break
        s = t.find("{", s + 1)
    return None


def main():
    rc = json.loads(RECEIPT.read_text())
    distinct = rc.get("distinct_distinctions", [])
    print("═" * 66)
    print(f"  🔥 HAL DISCRIMINATION — {len(distinct)} distinct distinctions")
    print("  separate seat: helen-hal · Authority_HAL=0 · SURVIVED forbidden")
    print("═" * 66, flush=True)

    tally = {"EVIDENCE_NEEDED": 0, "REFUTED": 0, "REDUNDANT": 0, "SURVIVED": 0}
    results = []
    for k, d in enumerate(distinct, 1):
        user = (f"CANDIDATE DISTINCTION #{k} (from Qwen epochs {d.get('also_epochs')}):\n"
                f"{d['distinction']}\n\nProposed discriminator:\n"
                f"{d.get('discriminator','(none)')}\n\n{SCHEMA}")
        t0 = time.time()
        try:
            raw = ollama(SYSTEM, user)
        except Exception as e:
            raw = f"__ERROR__ {e}"
        v = extract(raw) or {}
        verdict = str(v.get("verdict", "EVIDENCE_NEEDED")).upper()
        if verdict == "SURVIVED":  # constitutionally forbidden → downgrade
            verdict = "EVIDENCE_NEEDED"
            v["verdict_note"] = "SURVIVED downgraded: no observation executed"
        tally[verdict] = tally.get(verdict, 0) + 1
        rec = {"id": k, "source_epochs": d.get("also_epochs"),
               "distinction": d["distinction"],
               "counterfeit": v.get("counterfeit"), "separator": v.get("separator"),
               "observation_status": v.get("observation_status"),
               "verdict": verdict, "reason": v.get("reason"),
               "wall_s": round(time.time() - t0, 1), "raw": raw}
        results.append(rec)
        print(f"\n🔥 HAL — DISTINCTION {k:02d}  (Qwen ep {d.get('also_epochs')})  [{rec['wall_s']}s]")
        print(f"   distinction: {d['distinction'][:130]}")
        print(f"   counterfeit: {str(v.get('counterfeit'))[:130]}")
        print(f"   obs_status : {v.get('observation_status')}")
        glyph = {"EVIDENCE_NEEDED": "🟡", "REFUTED": "🔥",
                 "REDUNDANT": "⚫", "SURVIVED": "🟢"}.get(verdict, "⚫")
        print(f"   {glyph} VERDICT : {verdict} — {str(v.get('reason'))[:110]}", flush=True)

    rc.update({
        "hal_survived": tally.get("SURVIVED", 0),
        "hal_refuted": tally.get("REFUTED", 0),
        "hal_redundant": tally.get("REDUNDANT", 0),
        "hal_evidence_needed": tally.get("EVIDENCE_NEEDED", 0),
        "hal_model": HAL_MODEL,
        "hal_results": results,
        "hal_law": "SURVIVED forbidden without executed observation; "
                   "unexecuted discriminator ⇒ EVIDENCE_NEEDED.",
    })
    RECEIPT.write_text(json.dumps(rc, indent=2, ensure_ascii=False))
    print("\n" + "═" * 66)
    print("  🌈 QWEN_JESTER_20E_V0 — FINAL RECEIPT (post-HAL)")
    print("═" * 66)
    print(json.dumps({k: rc[k] for k in (
        "epochs_requested", "epochs_completed", "potential_distinctions_raw",
        "potential_distinctions_distinct", "hal_survived", "hal_refuted",
        "hal_redundant", "hal_evidence_needed", "authority_delta",
        "ledger_effect", "canon")}, indent=2))


if __name__ == "__main__":
    main()
