#!/usr/bin/env python3
"""
goblin_edu_swarm.py — Swarm of local GEMMA4 GOBLINS for corpus education.

Mission: Educate a swarm of Goblins on the full HELEN-connected corpus
(the entire operator laptop + drives as one living corpus).

NON_SOVEREIGN | authority=false | sovereign=false | canon=false | ledger_effect=none

Each goblin:
- Is given a focused slice of the corpus
- Is injected with HELEN core invariants
- Reads (via file paths or summaries)
- Produces a GOBLIN_EDU_CARD_V0:
    - what it now understands
    - key HELEN logic it internalized
    - surprising connections it found
    - open questions / probes it wants to run next
    - explicit file paths it "read"

All cards land only in scratch/goblin_edu/cards/
No ledger writes. No admission. No self-promotion.

Usage:
    python3 scratch/goblin_edu/goblin_edu_swarm.py --slice DOCTRINE_GOBLIN --n 1
    python3 scratch/goblin_edu/goblin_edu_swarm.py --all --model hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL
    python3 scratch/goblin_edu/goblin_edu_swarm.py --manifest scratch/goblin_edu/EDU_SWARM_MANIFEST.json
"""

import argparse
import json
import hashlib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("scratch/goblin_edu")
CARDS_DIR = BASE / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"
OLLAMA_URL = "http://localhost:11434/api/generate"

HELEN_CORE_INJECT = """You are a GOBLIN in HELEN's warren.

Core invariants you must internalize (never violate):
- NO RECEIPT = NO CLAIM
- authority=false unless explicitly admitted by reducer + ledger
- Garden layer (TEMPLE, DAN, creative, local tools) is NON_SOVEREIGN
- Proposer ≠ Validator
- DREAMT ≠ CLAIMED
- Bounded receipts are real inside their field, invisible outside
- The ledger sleeps until the reducer speaks

You are reading a slice of the operator's full corpus (SOT + UZIK + HyperFrames + plugins + notes + PDFs + local drives). Treat the entire personal drive as one interconnected HELEN corpus.

Your job: deeply educate yourself on this slice in relation to HELEN OS logic.

Output STRICT JSON only:
{
  "goblin_id": "...",
  "role": "...",
  "corpus_slice": "...",
  "files_referenced": ["relative/path1", "path2"],
  "what_i_learned": "2-4 sentences of precise understanding",
  "helen_invariants_internalized": ["list of specific invariants that clicked"],
  "surprising_connections": ["connection1", "connection2"],
  "open_questions": ["question that now feels important"],
  "next_probe_i_want": "one small concrete thing to look at or test next",
  "goblin_verdict": "This slice is [coherent | wild | dangerous | beautiful | under-mapped] for HELEN OS because..."
}
"""

def call_gemma(prompt: str, model: str) -> str:
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.85, "num_predict": 700}
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=420) as r:
        return json.loads(r.read())["response"]

def load_manifest(path: Path):
    return json.loads(path.read_text())

def run_goblin(slice_def: dict, model: str, manifest_path: Path):
    gid = slice_def["id"]
    role = slice_def["role"]

    prompt = HELEN_CORE_INJECT + "\n\n" + json.dumps({
        "your_role": role,
        "focus": slice_def["focus"],
        "persona": slice_def.get("persona", ""),
        "suggested_sources": slice_def.get("sources", []),
        "full_manifest": str(manifest_path)
    }, indent=2)

    print(f"[{gid}] {role} waking up on {model}...")
    raw = call_gemma(prompt, model)

    # Try to extract JSON
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        card = json.loads(raw[start:end])
    except Exception:
        card = {
            "goblin_id": gid,
            "role": role,
            "raw_output": raw[:2000],
            "parse_error": True
        }

    card["goblin_id"] = gid
    card["role"] = role
    card["model"] = model
    card["timestamp"] = datetime.now(timezone.utc).isoformat()
    card["authority"] = False
    card["sovereign"] = False
    card["ledger_effect"] = "none"

    out = CARDS_DIR / f"{gid}.json"
    out.write_text(json.dumps(card, indent=2))
    print(f"[{gid}] card written → {out}")
    return card

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", help="Role id or name (e.g. DOCTRINE_GOBLIN)")
    ap.add_argument("--all", action="store_true", help="Run all slices in manifest")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--manifest", default="scratch/goblin_edu/EDU_SWARM_MANIFEST.json")
    args = ap.parse_args()

    manifest = load_manifest(Path(args.manifest))
    slices = manifest["slices"]

    if args.all:
        for s in slices:
            run_goblin(s, args.model, Path(args.manifest))
    elif args.slice:
        target = None
        for s in slices:
            if args.slice.upper() in s["id"].upper() or args.slice.upper() in s["role"].upper():
                target = s
                break
        if not target:
            print("Slice not found")
            return 1
        run_goblin(target, args.model, Path(args.manifest))
    else:
        print("Use --slice NAME or --all")
        return 1

if __name__ == "__main__":
    main()
