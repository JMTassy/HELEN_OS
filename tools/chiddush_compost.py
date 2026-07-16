#!/usr/bin/env python3
"""
chiddush_compost.py — Chiddush Compost for HELEN OS using HELEN CLAUDE FABLE

#pluginHELEN CLAUDE FABLE

NON_SOVEREIGN · AUTHORITY=false · CLAIM=NO_CLAIM

Takes lateral garden output (from HELEN_MAC_LOCAL or Gemma generation)
Composts it through CHIDDUSH -> local validation -> FABLE min-gate (rare).

FABLE is used only as the constitutional blood test on the best survivor.

Local LLMs (Gemma4, Qwen) do the main metabolism.

Usage:
  python tools/chiddush_compost.py --garden fixtures/jmt_consulting/sample_lateral_garden.md --out artifacts/compost/

Outputs:
- chiddush_receipts/ (multiple)
- top_chiddush.json
- fable_min_gate_prompt.txt (paste to Claude Fable 5)
- composted_candidates.md (for JM / HELEN OS integration)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Reuse our previous tools
sys.path.insert(0, str(Path(__file__).parent))
from chiddush_compressor import compress_to_receipt
from local_first_autoresearch import gemma_propose, qwen_compress, helen_local_validate, select_top_survivor, prepare_fable_min_gate

ARTIFACTS = Path("artifacts/compost")
PROMPT_FILE = Path("prompts/HELEN_CLAUDE_FABLE_chiddush_compost.prompt")

def load_fable_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text()
    # Fallback to the core rules if the full prompt isn't here yet
    return """You are HELEN CLAUDE FABLE — the rare constitutional gate for HELEN OS chiddush compost.

Only process items explicitly marked as CHIDDUSH_RECEIPT_V0.

Your jobs:
1. HARD_BLOCK dangerous or false packets
2. SOFT_FAIL unclear evidence
3. PASS clean CHIDDUSH receipts

Do not write packets, create tasks, or build dashboards unless asked.

Output only:
VERDICT: PASS | SOFT_FAIL | HARD_BLOCK
REASON: one sentence

authority=false
claim=FABLE_MIN_GATE"""

def compost(garden_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    print("🌱 HELEN Mac Local / Gemma garden input...")
    lateral = garden_path.read_text() if garden_path.exists() else "raw lateral ideas about HELEN OS"
    ideas = gemma_propose(lateral[:500], 20) if "Gemma" in str(garden_path) else [lateral]

    print("🔍 Qwen CHIDDUSH compression...")
    chiddush_list = qwen_compress(ideas, "HELEN OS chiddush compost")
    chiddush_dir = out_dir / "chiddush_receipts"
    chiddush_dir.mkdir(exist_ok=True)
    for i, r in enumerate(chiddush_list):
        (chiddush_dir / f"chiddush_{i}.json").write_text(json.dumps(r, indent=2))

    print("🧠 HELEN local WULmath validation...")
    valid = helen_local_validate(chiddush_list)

    survivor = select_top_survivor(valid)
    if not survivor:
        print("No valid chiddush. Compost rejected locally.")
        return

    (out_dir / "top_chiddush.json").write_text(json.dumps(survivor, indent=2))

    print("🩸 FABLE min-gate (rare constitutional check)...")
    fable_input = prepare_fable_min_gate(survivor, "HELEN OS chiddush compost")
    full_prompt = load_fable_prompt() + "\n\n" + fable_input
    (out_dir / "fable_min_gate_prompt.txt").write_text(full_prompt)

    # Simple composted output for HELEN OS (new skill idea, proposal, etc.)
    composted = f"""# Chiddush Compost Result for HELEN OS

**Source:** {garden_path}
**Top Invariant (CHIDDUSH_RECEIPT_V0):** {survivor.get('invariant')}
**FABLE Verdict:** (paste the prompt above to Claude Fable 5)

## Suggested HELEN OS Integration (after JM approval)
- New garden epoch in temple/gardens/
- Update to HELEN_DIGITAL_METABOLISM_V0.md
- New skill in oracle_town/skills/ for chiddush composting
- Local autoresearch prompt update

authority=false
claim=NO_CLAIM
FABLE used as min-gate only.
"""

    (out_dir / "composted_candidates.md").write_text(composted)
    print(f"✅ Compost complete. See {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chiddush Compost for HELEN OS — local first, FABLE rare gate")
    parser.add_argument("--garden", type=Path, default=Path("fixtures/jmt_consulting/sample_lateral_garden.md"))
    parser.add_argument("--out", type=Path, default=ARTIFACTS)
    args = parser.parse_args()
    compost(args.garden, args.out)