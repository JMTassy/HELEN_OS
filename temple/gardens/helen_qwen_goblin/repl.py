#!/usr/bin/env python3
"""
HELEN_QWEN_GOBLIN direct REPL — JM ⇄ real local Qwen. Claude/HER/HAL/REDUCER are NOT in this path.
Everything is COMPOST (authority=0). /harvest exports the raw transcript for LATER HAL/REDUCER;
it does NOT admit anything. Run this in YOUR terminal:  python3 repl.py

Anti-fake: every GOBLIN line is a real Qwen inference. If Qwen is down → explicit error, no proxy.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from goblin_core import goblin_infer, QwenUnavailable, QWEN, GARDEN_SYSTEM

ROOT = Path(__file__).resolve().parent
BANNER = """╔════════════════════════════════════════════════════════════╗
║ 🌿 HELEN // DIRECT GARDEN DIALOG                            ║
║ MODEL      {model:<48}║
║ PERSONA    HELEN_QWEN_GOBLIN                                ║
║ AUTHORITY  0    CLAIMS ∅    LEDGER ∅    MODE COMPOST        ║
║ PATH       JM ⇄ QWEN   (no Claude/HER/HAL/REDUCER inline)   ║
╚════════════════════════════════════════════════════════════╝
/help /status /model /clear /save /harvest /quit"""

def main():
    print(BANNER.format(model=QWEN.split("/")[-1][:48]))
    history, sid = [], f"garden_{int(time.time())}"
    while True:
        try: line = input("\nYOU    > ").strip()
        except (EOFError, KeyboardInterrupt): print("\n🍃 garden closed."); break
        if not line: continue
        if line == "/quit": print("🍃 garden closed."); break
        if line == "/help": print("attack / go deeper / just talk. /save raw · /harvest → HAL later · /quit"); continue
        if line == "/model": print("GOBLIN backend =", QWEN, "· runtime = ollama · source = QwenRuntime"); continue
        if line == "/status": print(f"session={sid} turns={len(history)//2} authority=0 zone=GARDEN_SANDBOX claim=COMPOST"); continue
        if line == "/clear": history = []; print("context cleared (Garden only)."); continue
        if line == "/save":
            p = ROOT / f"transcript_{sid}.txt"; p.write_text("\n".join(f"{r}: {c}" for r, c in history))
            print(f"raw transcript saved (NON-SOVEREIGN Garden artifact) → {p.name}"); continue
        if line == "/harvest":
            p = ROOT / f"harvest_{sid}.json"
            p.write_text(json.dumps({"session": sid, "zone": "GARDEN_SANDBOX", "authority_delta": 0,
                "claim_status": "COMPOST_ONLY", "note": "exported for LATER HAL/REDUCER; harvest != admission",
                "turns": [{"role": r, "text": c} for r, c in history]}, indent=2, ensure_ascii=False))
            print(f"🌾 harvested for later HAL/REDUCER (NOT admitted) → {p.name}"); continue
        try:
            raw, meta = goblin_infer(line, history=history, num_predict=520, timeout=300)
        except QwenUnavailable as e:
            print("❌", e, "\n(NO Claude/HER proxy. Fix the Qwen runtime and retry.)"); continue
        print(f"\nGOBLIN > {raw}")
        print(f"        \x1b[2m[compost · out_hash {meta['raw_output_hash']} · ΔA=0]\x1b[0m")
        history += [("user", line), ("assistant", raw)]

if __name__ == "__main__":
    main()
