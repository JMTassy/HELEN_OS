#!/usr/bin/env python3
"""ralph_ollama_once.py — one Ralph iteration via Ollama.

Reads a prompt file, sends it to an Ollama model, checks output for a
completion promise token.

Exit codes:
  0  — promise found  (loop should stop)
  1  — no promise yet (loop should continue)
  2  — error          (ollama unavailable, bad args, etc.)

Usage (single pass):
  python scripts/ralph_ollama_once.py --prompt PROMPT.md

Usage (Ralph loop):
  while ! python scripts/ralph_ollama_once.py --prompt PROMPT.md; do :; done

Usage (bounded loop, stops after N or on promise):
  for i in $(seq 1 20); do
      python scripts/ralph_ollama_once.py --prompt PROMPT.md && break
  done
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _run(model: str, prompt: str, timeout: int) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ollama exited non-zero")
    return result.stdout


def _write_sidecar(sidecar_path: Path, record: dict) -> None:
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    with sidecar_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="One Ralph iteration via Ollama")
    parser.add_argument("--prompt", default="PROMPT.md", help="Prompt file path")
    parser.add_argument("--model", default="helen-core", help="Ollama model name")
    parser.add_argument("--promise", default="COMPLETE", help="Completion token (exact match)")
    parser.add_argument("--timeout", type=int, default=300, help="Seconds before timeout")
    parser.add_argument("--sidecar", default=None, help="Append iteration record to this NDJSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress output to stdout")
    args = parser.parse_args()

    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        print(f"ERROR: prompt file not found: {prompt_path}", file=sys.stderr)
        return 2

    prompt = prompt_path.read_text(encoding="utf-8")
    prompt_hash = _sha256(prompt)

    try:
        output = _run(args.model, prompt, args.timeout)
    except FileNotFoundError:
        print("ERROR: ollama not found — is it installed and on PATH?", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print(f"ERROR: ollama timed out after {args.timeout}s", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    complete = args.promise in output
    output_hash = _sha256(output)

    if not args.quiet:
        print(output, end="")

    if args.sidecar:
        _write_sidecar(
            Path(args.sidecar),
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "model": args.model,
                "prompt_hash": prompt_hash,
                "output_hash": output_hash,
                "promise_found": complete,
                "promise_token": args.promise,
            },
        )

    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
