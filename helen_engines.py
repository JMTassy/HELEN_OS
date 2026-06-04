"""
helen_engines.py — local, non-sovereign executors for HELEN's three named loops.

These are the PROTOTYPE implementations that run inside conquest-oracle-town.
They genuinely execute (each calls the local Ollama model and emits a real
receipt with a sha256), but they are NOT the SOT's sovereign engines:

  - EGREGOR     — multi-agent coding pass: ARCHITECT → CODER → REVIEWER → TESTER
  - AUTORESEARCH— bounded PULL-mode loop: one falsifiable hypothesis per epoch,
                  7-field receipt, observable signals only
  - RALPH       — bounded epoch loop: TEMPLE(propose) → HAL(gate) → REDUCER(keep/reject)

Constitutional posture (honest by construction):
  * authority is ALWAYS false — these propose and record, they do not rule.
  * every run is BOUNDED (rounds/epochs capped) — termination is sacred.
  * every run writes ONE receipt to ~/.helen/receipts/ (non-sovereign local path,
    NOT the SOT ledger, NOT town/ledger_v1.ndjson).
  * receipts are labelled NON_SOVEREIGN / NO_SHIP. They are evidence, not verdicts.

The SOT carries the sovereign AUTORESEARCH doctrine and scripts/ralph/ralph.sh.
This file does not import, copy, or write to the SOT. It is a local twin.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
HELEN_MODEL = os.getenv("HELEN_MODEL", "helen-core:latest")
RECEIPTS_DIR = Path.home() / ".helen" / "receipts"

MAX_ROUNDS = 4    # EGREGOR review/repair rounds ceiling
MAX_EPOCHS = 50   # AUTORESEARCH / RALPH epoch ceiling (runaway guard; bounded tranches)


# ── Model call (silent, non-streaming — engines control their own output) ────
def _llm(system: str, user: str, temperature: float = 0.3) -> str:
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": HELEN_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": temperature},
                "think": False,
                "keep_alive": "30m",   # hold model in GPU between engine calls
            },
            timeout=300,
        )
        r.raise_for_status()
        return r.json().get("message", {}).get("content", "").strip() or "[no response]"
    except requests.exceptions.ConnectionError:
        return "[ENGINE ERROR] Ollama not reachable (ollama serve)"
    except Exception as exc:
        return f"[ENGINE ERROR] {exc}"


def _extract_json(text: str) -> Optional[dict]:
    """Brace-match the first JSON object in model output (tolerant of fences/prose)."""
    start = text.find("{")
    if start == -1:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            esc = (ch == "\\" and not esc)
            if ch == '"' and not esc:
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _sha(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str).encode()
    ).hexdigest()


def _write_receipt(engine: str, body: dict) -> Dict[str, str]:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    seq = len(list(RECEIPTS_DIR.glob(f"{engine}_*.json"))) + 1
    receipt = {
        "schema": f"HELEN_{engine.upper()}_RECEIPT_V0",
        "authority": False,
        "sovereign": False,
        "status": "NON_SOVEREIGN / NO_SHIP",
        "engine": engine,
        "seq": seq,
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": HELEN_MODEL,
        **body,
    }
    receipt["receipt_sha"] = _sha({k: v for k, v in receipt.items() if k != "receipt_sha"})
    path = RECEIPTS_DIR / f"{engine}_{seq:03d}.json"
    path.write_text(json.dumps(receipt, indent=2, default=str))
    return {"receipt_path": str(path), "receipt_sha": receipt["receipt_sha"]}


def _result(ok: bool, summary: str, detail: Any, receipt: Dict[str, str]) -> Dict[str, Any]:
    return {"success": ok, "summary": summary, "detail": detail, **receipt}


# ── EGREGOR ───────────────────────────────────────────────────────────────────
def run_egregor(task: str, rounds: int = 1) -> Dict[str, Any]:
    """ARCHITECT → CODER → REVIEWER → TESTER on `task`. Bounded review rounds."""
    rounds = max(1, min(int(rounds), MAX_ROUNDS))
    stages: List[Dict[str, str]] = []

    plan = _llm("You are ARCHITECT in the EGREGOR pipeline. Output a terse numbered "
                "implementation plan. No code.", f"TASK:\n{task}")
    stages.append({"role": "ARCHITECT", "output": plan})

    code = _llm("You are CODER in the EGREGOR pipeline. Implement the plan. Output ONLY "
                "code in one fenced block.", f"TASK:\n{task}\n\nPLAN:\n{plan}")
    stages.append({"role": "CODER", "output": code})

    review = _llm("You are REVIEWER in the EGREGOR pipeline. Find bugs and risks in the "
                  "code. Be specific and short.", f"TASK:\n{task}\n\nCODE:\n{code}")
    stages.append({"role": "REVIEWER", "output": review})

    for _ in range(rounds - 1):
        code = _llm("You are CODER. Apply the reviewer's fixes. Output ONLY corrected code "
                    "in one fenced block.", f"CODE:\n{code}\n\nREVIEW:\n{review}")
        stages.append({"role": "CODER(repair)", "output": code})
        review = _llm("You are REVIEWER. Re-review. Be specific and short.",
                      f"CODE:\n{code}")
        stages.append({"role": "REVIEWER", "output": review})

    test = _llm("You are TESTER in the EGREGOR pipeline. Decide PASS or FAIL and give a "
                "one-line reason. Start your reply with PASS or FAIL.",
                f"TASK:\n{task}\n\nCODE:\n{code}\n\nREVIEW:\n{review}")
    stages.append({"role": "TESTER", "output": test})

    verdict = "PASS" if test.lstrip().upper().startswith("PASS") else "FAIL"
    receipt = _write_receipt("egregor", {
        "task": task, "rounds": rounds, "verdict": verdict,
        "stages": [{"role": s["role"], "output_sha": _sha(s["output"])} for s in stages],
        "code_sha": _sha(code),
    })
    return _result(verdict == "PASS",
                   f"EGREGOR {verdict} ({len(stages)} stages, {rounds} round(s))",
                   {"verdict": verdict, "code": code[:1500], "review": review[:600],
                    "test": test[:300]}, receipt)


# ── AUTORESEARCH (PULL-mode, bounded) ─────────────────────────────────────────
_PULL_SYS = (
    "You are AUTORESEARCH in PULL mode. Emit ONE epoch as strict JSON with keys: "
    "carry_forward, hypothesis (observable + falsifiable), experiment (touches no "
    "kernel/schema/ledger), metric (baseline, observed, target), failure_mode, "
    "keep_reject_rule, upgrade_path. Observable signals only. authority is false. "
    "Output ONLY the JSON object."
)


def run_autoresearch(topic: str, epochs: int = 1) -> Dict[str, Any]:
    """Bounded PULL-mode loop: one falsifiable hypothesis per epoch."""
    epochs = max(1, min(int(epochs), MAX_EPOCHS))
    carry = "GENESIS"
    receipts: List[dict] = []
    for e in range(epochs):
        raw = _llm(_PULL_SYS,
                   f"TOPIC: {topic}\nCARRY_FORWARD: {carry}\nEPOCH: {e + 1}/{epochs}")
        rec = _extract_json(raw) or {"hypothesis": raw[:400], "parse": "unstructured"}
        rec["epoch"] = e + 1
        rec["epoch_sha"] = _sha(rec)
        receipts.append(rec)
        carry = rec.get("upgrade_path") or rec.get("hypothesis") or carry

    tranche_sha = _sha([r["epoch_sha"] for r in receipts])
    receipt = _write_receipt("autoresearch", {
        "topic": topic, "epochs": epochs, "tranche_cum_sha": tranche_sha,
        "sub_receipts": receipts,
    })
    last = receipts[-1]
    return _result(True,
                   f"AUTORESEARCH sealed {epochs} epoch(s) on '{topic}'",
                   {"last_hypothesis": last.get("hypothesis"),
                    "metric": last.get("metric"),
                    "keep_reject_rule": last.get("keep_reject_rule")}, receipt)


# ── RALPH (bounded epoch loop) ────────────────────────────────────────────────
def run_ralph(story: str, epochs: int = 1) -> Dict[str, Any]:
    """Bounded loop, one story per epoch: TEMPLE → HAL → REDUCER → receipt."""
    epochs = max(1, min(int(epochs), MAX_EPOCHS))
    epoch_log: List[dict] = []
    for e in range(epochs):
        temple = _llm("You are TEMPLE (non-sovereign, authority false). Propose ONE small "
                      "concrete move for the story. 2-3 sentences.", f"STORY: {story}")
        hal = _llm("You are HAL, the execution gate. Judge the TEMPLE proposal for "
                   "admissibility (bounded? non-sovereign? safe?). Start with ADMIT or "
                   "BLOCK and give a one-line reason.",
                   f"STORY: {story}\nPROPOSAL: {temple}")
        admitted = hal.lstrip().upper().startswith("ADMIT")
        reducer = _llm("You are the REDUCER. Given the gate verdict, output KEEP or REJECT "
                       "and a one-line rationale. Start with KEEP or REJECT.",
                       f"PROPOSAL: {temple}\nHAL: {hal}")
        kept = reducer.lstrip().upper().startswith("KEEP")
        epoch_log.append({
            "epoch": e + 1,
            "temple_sha": _sha(temple), "hal": hal[:200],
            "gate": "ADMIT" if admitted else "BLOCK",
            "reducer": "KEEP" if kept else "REJECT",
            "proposal": temple[:400],
        })

    kept_n = sum(1 for x in epoch_log if x["reducer"] == "KEEP")
    receipt = _write_receipt("ralph", {
        "story": story, "epochs": epochs, "kept": kept_n,
        "epoch_log": epoch_log,
    })
    return _result(True,
                   f"RALPH ran {epochs} epoch(s) on '{story}' — {kept_n} KEEP",
                   {"epochs": epoch_log}, receipt)


# ── dispatch table for the action bridge ─────────────────────────────────────
ENGINES = {
    "egregor":      run_egregor,
    "autoresearch": run_autoresearch,
    "ralph":        run_ralph,
}


def run_engine(name: str, **kwargs) -> Dict[str, Any]:
    fn = ENGINES.get(name)
    if fn is None:
        return {"success": False, "summary": f"unknown engine {name!r}", "detail": None}
    return fn(**kwargs)
