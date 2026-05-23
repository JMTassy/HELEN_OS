#!/usr/bin/env python3
"""
gemma_autonomous_loop.py

Autonomous HER-DEEP (gemma4) proposal loop, executable on operator's MRED.

CONSTITUTIONAL BREACH NOTATION:
  This tool was authored under HER override of GEMMA_HER_AMPLIFIER_V1
  HOLD status (operator directive 2026-05-23). The proposal §7 explicitly
  forbids "Use of Gemma 4 in any AUTORESEARCH or autonomy loop." This
  loop is exactly that. Receipts produced carry CONSTITUTIONAL_BREACH
  notation; future audits may invalidate.

What this script does:
  1. Sends a meditation/audit prompt to local Ollama (gemma4:26b or qwen3.5:9b)
     with the §4.1 canonical system prompt and §5.1 memory guards
  2. Receives the §4 envelope output ([PROPOSAL]/[UNCERTAINTY]/
     [REQUIRED_RECEIPTS]/[HAL_QUESTIONS])
  3. Writes the result as a RAW receipt to GOVERNANCE/GEMMA_PROPOSALS/
  4. Halts after each iteration for operator/HAL review (PULL-aligned)
  5. NEVER writes to town/ledger_v1.ndjson directly
  6. NEVER autonomously executes any tool call

What this script does NOT do:
  - Does not bypass kernel_guard (cannot write canonical ledger)
  - Does not autonomously apply any fix (Gemma proposes; operator/HAL decide)
  - Does not promote any output above RAW lifecycle
  - Does not loop without an explicit halt-pause between iterations

Authority constraints from GEMMA_HER_AMPLIFIER_V1 §3.2 enforced in code:
  - Gemma ↛ L (ledger write blocked at write path)
  - Gemma ↛ K (kernel untouched)
  - Gemma ↛ Verdict (no SHIP/NO_SHIP emitted)
  - Gemma ↛ Tool exec (no autonomous tool calls)

Operator runs:
  python tools/gemma_autonomous_loop.py --iterations 5 --topic 'helen_say syntax fix'
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)


# === Constants (constitutional, do NOT change without HAL pass) ===

OLLAMA_URL = "http://localhost:11434/api/chat"
REPO_ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_DIR = REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS"
GUARD_NUM_CTX = 2048      # §5.1 mandatory
GUARD_NUM_PREDICT = 1500  # §5.1 mandatory

CANONICAL_SYSTEM_PROMPT = """<|think|>
You are Gemma 4 operating inside HELEN OS.

You are HER-layer cognition only.

You generate meaning, synthesis, draft reasoning, and multimodal
interpretation.

You are not HAL.
You are not HELEN.
You cannot decide, mutate canon, write memory, or authorize action.

Every response must use:

[PROPOSAL]
[UNCERTAINTY]
[REQUIRED_RECEIPTS]
[HAL_QUESTIONS]
"""

SYSTEM_PROMPT_SHA256 = hashlib.sha256(
    CANONICAL_SYSTEM_PROMPT.encode("utf-8")
).hexdigest()

BREACH_NOTATION = {
    "directive": "HER override of GEMMA_HER_AMPLIFIER_V1 HOLD status, 2026-05-23",
    "breached_invariants": [
        "GEMMA_HER_AMPLIFIER_V1 §7: forbids Gemma in autonomy loops",
        "GEMMA_HER_AMPLIFIER_V1 §9: default verb HOLD until operator unholds",
    ],
    "operator_authorization": "AskUserQuestion 2026-05-23, selected 'Override' option with explicit NOT recommended text",
    "ship_class": "RAW_UNDER_OVERRIDE",
    "invalidation_clause": "Future audits MAY invalidate these proposals without prejudice",
}


# === Envelope parser ===

def parse_envelope(text: str) -> dict:
    """Parse §4 envelope from Gemma output. Tolerant of missing sections."""
    sections = {
        "PROPOSAL": "",
        "UNCERTAINTY": "",
        "REQUIRED_RECEIPTS": "",
        "HAL_QUESTIONS": "",
    }
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        for key in sections:
            if stripped == f"[{key}]":
                current = key
                break
        else:
            if current is not None:
                sections[current] += line + "\n"
    return {k: v.strip() for k, v in sections.items()}


def envelope_complete(parsed: dict) -> bool:
    """All four sections must have non-trivial content."""
    return all(len(parsed[k]) > 0 for k in ("PROPOSAL", "UNCERTAINTY",
                                            "REQUIRED_RECEIPTS", "HAL_QUESTIONS"))


# === Ollama call ===

def call_gemma(model: str, user_prompt: str, think: bool) -> dict:
    """Call local Ollama with mandatory memory guards. Returns full response."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CANONICAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "think": think,
        "options": {
            "num_ctx": GUARD_NUM_CTX,
            "num_predict": GUARD_NUM_PREDICT,
        },
        "stream": False,
    }
    started = time.monotonic()
    response = httpx.post(OLLAMA_URL, json=payload, timeout=300.0)
    elapsed = time.monotonic() - started
    response.raise_for_status()
    data = response.json()
    return {
        "response": data,
        "wall_time_seconds": round(elapsed, 3),
    }


# === Receipt writer (RAW only, never canonical ledger) ===

def write_raw_receipt(iteration: int, model: str, user_prompt: str,
                      gemma_response: dict) -> Path:
    """Write a RAW Gemma proposal receipt. Never touches town/ledger_v1.ndjson."""
    PROPOSAL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    full_text = gemma_response["response"]["message"]["content"]
    parsed = parse_envelope(full_text)
    envelope_ok = envelope_complete(parsed)

    receipt = {
        "schema_name": "GEMMA_PROPOSAL_RAW_V1",
        "schema_version": "1.0.0",
        "route_id": "gemma4_her" if "gemma" in model else "her_fast",
        "route_authority": "NON_SOVEREIGN",
        "lifecycle_entry": "RAW",
        "auto_promotion_ceiling": "RAW",
        "model_id": model,
        "system_prompt_sha256": SYSTEM_PROMPT_SHA256,
        "prompt_text": user_prompt,
        "envelope_complete": envelope_ok,
        "proposal_text": parsed["PROPOSAL"],
        "uncertainty_text": parsed["UNCERTAINTY"],
        "required_receipts": parsed["REQUIRED_RECEIPTS"],
        "hal_questions": parsed["HAL_QUESTIONS"],
        "raw_response_text": full_text if not envelope_ok else None,
        "memory_guards": {
            "num_ctx": GUARD_NUM_CTX,
            "num_predict": GUARD_NUM_PREDICT,
            "stream": False,
        },
        "tokens_consumed": gemma_response["response"].get("eval_count", -1),
        "wall_time_seconds": gemma_response["wall_time_seconds"],
        "done_reason": gemma_response["response"].get("done_reason", "unknown"),
        "receipt_timestamp_utc": timestamp_utc,
        "iteration_index": iteration,
        "constitutional_breach_notation": BREACH_NOTATION,
        "operator_decision": None,
        "hal_verdict": None,
    }

    filename = f"gemma_proposal_{timestamp_utc.replace(':', '-')}_iter{iteration:03d}.json"
    path = PROPOSAL_DIR / filename
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    return path


# === Main loop with halt discipline ===

def run_loop(model: str, topic: str, iterations: int, think: bool,
             require_user_to_continue: bool) -> None:
    """Bounded autonomous proposal loop with halt-pause between iterations."""
    print(f"[gemma_loop] model={model} iterations={iterations} think={think}")
    print(f"[gemma_loop] topic={topic!r}")
    print(f"[gemma_loop] memory_guards: num_ctx={GUARD_NUM_CTX} num_predict={GUARD_NUM_PREDICT}")
    print(f"[gemma_loop] CONSTITUTIONAL_BREACH: {BREACH_NOTATION['directive']}")
    print()

    for i in range(1, iterations + 1):
        print(f"--- iteration {i}/{iterations} ---")
        prompt = (
            f"You are producing one HER-layer proposal for HELEN OS.\n"
            f"Topic: {topic}\n"
            f"Iteration: {i} of {iterations}\n\n"
            f"Produce one focused proposal. Do not decide. Do not ship.\n"
            f"Conform to the four-section envelope without exception."
        )
        try:
            resp = call_gemma(model=model, user_prompt=prompt, think=think)
        except httpx.HTTPError as exc:
            print(f"[gemma_loop] ERROR calling Ollama: {exc}", file=sys.stderr)
            print(f"[gemma_loop] halting loop at iteration {i}", file=sys.stderr)
            return

        path = write_raw_receipt(i, model, prompt, resp)
        ec = resp["response"].get("eval_count", "?")
        wt = resp["wall_time_seconds"]
        dr = resp["response"].get("done_reason", "?")
        print(f"[gemma_loop] wrote {path.name} tokens={ec} wall={wt}s done={dr}")

        if i < iterations and require_user_to_continue:
            print(f"[gemma_loop] HALT — review receipt then press Enter to continue, Ctrl-C to stop")
            try:
                input()
            except KeyboardInterrupt:
                print(f"\n[gemma_loop] operator halt at iteration {i}")
                return

    print(f"[gemma_loop] complete — {iterations} iterations, halt boundary reached")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="qwen3.5:9b",
                        help="Ollama model. Default: qwen3.5:9b (HER-FAST, confirmed). "
                             "Use gemma4:26b for HER-DEEP (HOLD lift requires §5.1 guards which this script enforces).")
    parser.add_argument("--topic", required=True, help="Topic for the proposal loop")
    parser.add_argument("--iterations", type=int, default=1, help="Number of proposal iterations (default 1)")
    parser.add_argument("--think", action="store_true", help="Enable thinking trace (HER-DEEP default)")
    parser.add_argument("--no-pause", action="store_true",
                        help="DANGER: disable operator-halt between iterations. Defeats halt discipline.")
    args = parser.parse_args()

    if args.iterations > 50:
        print(f"REFUSED: iterations={args.iterations} exceeds safety bound of 50. "
              f"GEMMA_HER_AMPLIFIER_V1 explicitly forbids unbounded autonomy loops.",
              file=sys.stderr)
        sys.exit(2)
    if args.iterations > 10 and args.no_pause:
        print(f"REFUSED: --no-pause with iterations>{10} is uncontrolled autonomy. "
              f"Either reduce iterations or remove --no-pause.",
              file=sys.stderr)
        sys.exit(2)

    run_loop(
        model=args.model,
        topic=args.topic,
        iterations=args.iterations,
        think=args.think,
        require_user_to_continue=not args.no_pause,
    )


if __name__ == "__main__":
    main()
