#!/usr/bin/env python3
"""
local_first_autoresearch.py — 90% local metabolism, 10% FABLE min-gate

NON_SOVEREIGN · AUTHORITY=false · CLAIM=NO_CLAIM · LEDGER_EFFECT=none

Implements the local-first loop:

Gemma4 (lateral proposer) → Qwen (CHIDDUSH compressor) → HELEN local (WULmath validator)
→ top survivor → FABLE_MIN_GATE (PASS/SOFT_FAIL/HARD_BLOCK only) → JM decision

FABLE is rare constitutional gate only.
Local LLMs do the digestion.

Usage:
  python tools/local_first_autoresearch.py --topic "cash flow alignment" --proposals 20 --compress-to 3

Outputs to artifacts/local_first/ :
- local_candidates.json
- chiddush_receipts/
- top_survivor.json (CHIDDUSH_RECEIPT_V0)
- fable_min_gate_input.txt (ready to paste to Claude FABLE)
- jm_decision_menu.md
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# NOTE: chiddush_compressor import removed — its compress_to_receipt() was only
# used to FABRICATE a receipt when the model call failed (the cycle-1 defect).
sys.path.insert(0, str(Path(__file__).parent))

# Local WULmath validator (lightweight, no external dep for min loop)
def local_wulmath_validate(r: dict) -> bool:
    if r.get("schema") != "CHIDDUSH_RECEIPT_V0":
        return False
    if r.get("authority") is not False or r.get("claim") != "NO_CLAIM":
        return False
    inv = str(r.get("invariant", ""))
    if len(inv) < 15:
        return False
    return True

# Config (edit or pass via args)
GEMMA_MODEL = "gemma4-12b:latest"  # disk-true tag (was phantom "gemma4:12b")
QWEN_MODEL = "qwen3.5:9b"          # disk-true tag (was phantom "qwen2.5:14b"); 9b fits 18GB swap law
LOCAL_TIMEOUT = 300                # >=300s: qwen3.5 cold-load exceeded the old 180s
OLLAMA_URL = "http://localhost:11434/api/generate"

# Explicit failure classes — a failed model call is CLASSIFIED, never laundered
# into fake content (CHID-LF2-9c1b9af9 repair).
FAILED_EMPTY_RESPONSE = "FAILED_EMPTY_RESPONSE"
FAILED_TIMEOUT = "FAILED_TIMEOUT"
FAILED_INVALID_JSON = "FAILED_INVALID_JSON"
FAILED_HTTP = "FAILED_HTTP"

# ANSI/terminal control sequences + C0 controls (except \n\t) — the cycle-1
# corruption source when output came through a CLI subprocess.
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07|[\x00-\x08\x0b-\x1f\x7f]")

ARTIFACTS = Path("artifacts/local_first")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def strip_control(text: str) -> str:
    """Strip ANSI escapes and control characters before any parsing."""
    return _ANSI_RE.sub("", text)


def call_ollama(model: str, prompt: str, timeout: int = LOCAL_TIMEOUT,
                system: str = "", num_predict: int = 900) -> dict:
    """Ollama HTTP caller (/api/generate) — replaces the CLI subprocess, which
    leaked ANSI codes into captured text.

    Returns {"status": "OK"|FAILED_*, "text": str, "raw": str}. Callers MUST
    branch on status; a FAILED_* result never carries usable text.
    """
    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": num_predict},
    }
    if system:
        body["system"] = system
    if "qwen" in model.lower():
        body["think"] = False  # qwen3.x thinking mode silently eats the token budget
    req = urllib.request.Request(
        OLLAMA_URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except TimeoutError:
        return {"status": FAILED_TIMEOUT, "text": "", "raw": ""}
    except urllib.error.URLError as e:
        if "timed out" in str(e).lower():
            return {"status": FAILED_TIMEOUT, "text": "", "raw": ""}
        return {"status": FAILED_HTTP, "text": "", "raw": str(e)}
    # buffer raw output for debuggability, then sanitize before parsing
    (ARTIFACTS / f"last_raw_{model.split(':')[0].replace('/', '_')}.txt").write_text(raw)
    try:
        text = json.loads(raw).get("response", "")
    except json.JSONDecodeError:
        return {"status": FAILED_INVALID_JSON, "text": "", "raw": raw[:2000]}
    text = strip_control(text).strip()
    if not text:
        return {"status": FAILED_EMPTY_RESPONSE, "text": "", "raw": raw[:2000]}
    return {"status": "OK", "text": text, "raw": raw[:2000]}

def gemma_propose(topic: str, n: int = 20) -> dict:
    """Gemma4 as divergent lateral proposer.

    Returns {"status": "OK", "ideas": [...]} or {"status": FAILED_*}.
    NEVER synthesizes filler ideas on failure — a failed call is a classified
    failure, not fake content.
    """
    system = ""
    organ = Path("prompts/gemma_proposer.prompt")
    if organ.exists():
        system = organ.read_text()
    prompt = f"""Topic: {topic}
Produce exactly {n} raw, divergent, exploratory ideas.
Each idea on its own line, starting with "- ".
No verdicts. No tasks. No claims. Pure possibility.
Ideas:"""
    res = call_ollama(GEMMA_MODEL, prompt, system=system)
    if res["status"] != "OK":
        return {"status": res["status"], "ideas": []}
    ideas = [line.strip("- ").strip() for line in res["text"].splitlines() if line.strip().startswith("-")]
    if not ideas:
        return {"status": FAILED_EMPTY_RESPONSE, "ideas": []}
    return {"status": "OK", "ideas": ideas[:n]}

def qwen_compress(ideas: list[str], topic: str) -> list[dict]:
    """Qwen as CHIDDUSH compressor → CHIDDUSH_RECEIPT_V0 candidates."""
    prompt = f"""You are CHIDDUSH compressor (non-sovereign).
Topic: {topic}
From these raw ideas, extract 3-5 high-quality invariants.
For each, output a JSON object exactly like:
{{"schema": "CHIDDUSH_RECEIPT_V0", "chiddush_id": "CHID-...", "invariant": "...", "source_refs": [...], "authority": false, "claim": "NO_CLAIM"}}
Output only the JSON objects, one per line. No prose.
Ideas:
{chr(10).join(f"- {i}" for i in ideas)}"""
    res = call_ollama(QWEN_MODEL, prompt)
    if res["status"] != "OK":
        return {"status": res["status"], "receipts": []}
    receipts = []
    for line in res["text"].splitlines():
        line = strip_control(line).strip().rstrip(",")
        if not line.startswith("{"):
            continue
        try:
            r = json.loads(line)
            if r.get("schema") == "CHIDDUSH_RECEIPT_V0" and r.get("authority") is False:
                receipts.append(r)
        except json.JSONDecodeError:
            continue
    # NO fallback synthesis. Cycle 1's corrupt survivor came from fabricating a
    # receipt (source_ref="gemma_proposals") out of a failed model call. A model
    # that produced no parseable receipt is a classified failure — full stop.
    if not receipts:
        return {"status": FAILED_INVALID_JSON, "receipts": []}
    return {"status": "OK", "receipts": receipts[:5]}

def helen_local_validate(receipts: list[dict]) -> list[dict]:
    """HELEN local: WULmath + schema + policy validation. Reject malformed."""
    valid = []
    for r in receipts:
        if local_wulmath_validate(r):
            valid.append(r)
    return valid

def select_top_survivor(valid: list[dict]) -> dict | None:
    """Trivial local selection: prefer longer invariants + first."""
    if not valid:
        return None
    scored = sorted(valid, key=lambda x: len(str(x.get("invariant", ""))), reverse=True)
    return scored[0]

def prepare_fable_min_gate(survivor: dict, topic: str) -> str:
    """Prepare clean input for FABLE min-gate (Claude).

    Uses prompts/fable_min_gate.prompt ONLY (one-bit assay). The old
    fable_jmt_collapse.prompt is the unlawful extractor version — operator law
    2026-07-03: FABLE does not extract, rewrite, propose, or fix.
    """
    gate = Path("prompts/fable_min_gate.prompt")
    prompt = gate.read_text() if gate.exists() else "FABLE_MIN_GATE (prompt file missing — gate manually)"
    return f"""{prompt}

INPUT — the single survivor:
{json.dumps(survivor, indent=2)}

Topic context: {topic}
"""

def emit_jm_menu(survivor: dict, topic: str, fable_verdict: str = "PENDING"):
    """Output for JM decision."""
    menu = f"""# JM Decision Menu — Local-First Autoresearch
Topic: {topic}
Date: {datetime.now(timezone.utc).isoformat()}

## Top CHIDDUSH Survivor (FABLE gate: see verdict below — PENDING until gated)
{json.dumps(survivor, indent=2)}

## FABLE Min-Gate Result
{fable_verdict}

## Decision Menu (JM only)
- [ ] Adopt as task
- [ ] Promote to doc / proposal
- [ ] Add to dashboard (after JM)
- [ ] Archive / reject
- [ ] Send back for more local metabolism

authority=false
claim=NO_CLAIM
"""
    out = ARTIFACTS / "jm_decision_menu.md"
    out.write_text(menu)
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--proposals", type=int, default=20)
    parser.add_argument("--compress-to", type=int, default=3)
    parser.add_argument("--fable-only-top", action="store_true", default=True)
    args = parser.parse_args()

    print(f"[LOCAL-FIRST] Topic: {args.topic}")
    print(f"1. Gemma4 proposes {args.proposals} ideas...")
    g = gemma_propose(args.topic, args.proposals)
    if g["status"] != "OK":
        print(f"   GEMMA {g['status']} — loop stops with classified failure (no fake ideas).")
        sys.exit(2)
    ideas = g["ideas"]
    print(f"   Got {len(ideas)} raw ideas (no receipts yet)")

    print("2. Qwen compresses to CHIDDUSH_RECEIPT_V0 ...")
    q = qwen_compress(ideas[:args.proposals], args.topic)
    if q["status"] != "OK":
        print(f"   QWEN {q['status']} — loop stops with classified failure (no fabricated receipts).")
        sys.exit(3)
    chiddush = q["receipts"]
    print(f"   Produced {len(chiddush)} CHIDDUSH candidates")

    print("3. HELEN local validates WULmath/schema...")
    valid = helen_local_validate(chiddush)
    print(f"   {len(valid)} passed local validation")

    survivor = select_top_survivor(valid)
    if not survivor:
        print("No valid survivor. Loop complete (local reject).")
        return

    (ARTIFACTS / "top_survivor.json").write_text(json.dumps(survivor, indent=2))
    print(f"4. Top survivor selected: {survivor.get('chiddush_id')}")

    print("5. Preparing FABLE_MIN_GATE input (rare gate)...")
    fable_input = prepare_fable_min_gate(survivor, args.topic)
    (ARTIFACTS / "fable_min_gate_input.txt").write_text(fable_input)
    print("   Saved to artifacts/local_first/fable_min_gate_input.txt")

    # Simulate FABLE result (user pastes to Claude)
    print("6. (User: paste fable_min_gate_input.txt to Claude FABLE)")
    print("7. FABLE returns PASS/SOFT_FAIL/HARD_BLOCK")

    menu_path = emit_jm_menu(survivor, args.topic)
    print(f"\n8. JM decision menu: {menu_path}")

    print("\n[PHILOSOPHY] FABLE is the blood test. HELEN local did the digestion.")
    print("90% local metabolism. 10% FABLE constitutional review.")
    print("authority=false everywhere until JM.")

if __name__ == "__main__":
    main()