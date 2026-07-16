#!/usr/bin/env python3
"""goblin_tree_grow.py — the GEMMA4 goblin swarm grows the NO_CLAIM esoteric
tree of knowledge in temple/gardens/esoteric_tree/.

NON_SOVEREIGN | authority=false | sovereign=false | canon=false | ledger_effect=none
DREAMT ≠ CLAIMED · sacred ≠ truth · beauty ⊬ evidence · 📜 ledger sleeps

Each node = one HELEN invariant. The goblin renders the esoteric skin
(name, whisper, glyph, mantra); the card binds it to the demystified law and
its witness path on disk. ND output is sha256-bound (NO HASH = NO VOICE).
"""

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GARDEN = REPO / "temple" / "gardens" / "esoteric_tree"
NODES = GARDEN / "nodes"
LOG = REPO / "scratch" / "goblin_tree_grow.log"
MODEL = "gemma4-12b:latest"
OLLAMA = "http://localhost:11434/api/generate"

# The ten invariants — the demystified trunk. Each: (law, witness path on disk).
LAWS = [
    ("NO RECEIPT = NO CLAIM",
     "tools/helen_say.py — the only admissible writer"),
    ("NO HASH = NO VOICE — non-deterministic output never enters the spine unhashed",
     "scripts/helen_k8_lint.py (K8 boundary)"),
    ("Proposer ≠ Validator — no one approves their own work",
     "oracle_town/skills/feynman/peer_review (K2/Rule 3)"),
    ("Garden ADMIT ≠ Kernel ADMISSION — play mutates the garden, never the spine",
     "apps/goblin-warren/warren_town.html — the surface has no stamp control"),
    ("DREAMT ≠ CLAIMED — dreams are real dreams, not real claims",
     "temple/gardens/*/validate_*.py (fail-closed garden validators)"),
    ("generation ≠ admission — lawful transmutation runs only through the narrow path",
     "docs/proposals/GAS_V0.md (Axiom 2.5, Evidence Separation)"),
    ("Inv holds ⊬ Inv certified — soundness and certification rot independently",
     "docs/proposals/GAS_V0_PROOFS.md §6 (the certification-rot exhibit)"),
    ("AUTHORITY IS IN THE VERIFIED POSITION, NOT THE OBJECT",
     "tools/kernel_guard.sh (the allowlist IS the position)"),
    ("If it does not replay, it is not real",
     "oracle_town/core/replay.py + CI 200-iteration determinism check"),
    ("Termination is sacred — every working ends SHIP or ABORT, never an open drift",
     "~/.claude/CLAUDE.md (session termination law)"),
]

PROMPT = """You are a GOBLIN MYSTIC in HELEN's Garden. Hard frame: NO_CLAIM zone,
authority=false, nothing you say becomes true by being beautiful. You render
LAW as ESOTERIC SKIN — the skin decorates, never replaces, the law.

Render this invariant as one node of the esoteric tree of knowledge:

LAW: {law}

Output STRICT JSON, keys:
"esoteric_name" (2-4 arcane words, a name for this node),
"whisper" (3-5 lines of mystical teaching a goblin elder would murmur),
"glyph" (one short description of the node's sigil),
"mantra" (one line, chantable, under 12 words).

JSON only. Do not claim the law is admitted, proven here, or divine. The
mystery points AT the mechanism; it never replaces it."""


def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def ask_gemma(prompt: str) -> str:
    body = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 1.0, "num_predict": 350},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]


def main() -> None:
    NODES.mkdir(parents=True, exist_ok=True)
    log(f"TREE GROW START model={MODEL} nodes={len(LAWS)}")
    ok, fail = 0, 0
    for i, (law, witness) in enumerate(LAWS, 1):
        out = NODES / f"NODE-{i:02d}.json"
        if out.exists():
            log(f"[{i}/{len(LAWS)}] exists, skip")
            ok += 1
            continue
        try:
            t0 = time.time()
            resp = ask_gemma(PROMPT.format(law=law))
            card = {
                "schema": "ESOTERIC_TREE_NODE_V0",
                "node": i,
                "law": law,
                "witness": witness,
                "model": MODEL,
                "response_raw": resp,
                "response_sha256": hashlib.sha256(resp.encode()).hexdigest(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "authority": False, "sovereign": False, "canon": False,
                "ledger_effect": "none",
                "claim_status": "NO_CLAIM",
                "reduction": "every mystical render reduces to the checkable law above",
            }
            out.write_text(json.dumps(card, ensure_ascii=False, indent=2))
            ok += 1
            log(f"[{i}/{len(LAWS)}] NODE-{i:02d} ok {round(time.time()-t0,1)}s")
        except Exception as e:
            fail += 1
            log(f"[{i}/{len(LAWS)}] NODE-{i:02d} FAIL {type(e).__name__}: {e}")
    log(f"TREE GROW DONE ok={ok} fail={fail} dir={NODES}")


if __name__ == "__main__":
    main()
