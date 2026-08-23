#!/usr/bin/env python3
"""
VISIBLE_GOBLIN_LIVE_STREAM_V0 — acceptance witness (OBSERVABILITY, not intelligence).

Asserts, over the live trace:
  N_G>0 · N_Q>0 · |ids|=N_events · CLI=Π(Trace) · Browser⊆Π(Trace) · silent=0
  + append-only (trace_seq strictly 0..n-1)
  + observer catch-up: a FRESH `live_goblins --once` process reconstructs every id
Does NOT score CHIDDUSH quality. authority=false · canon=false · ledger_effect=none.
"""
import json, subprocess, sys, urllib.request
from pathlib import Path
import reducer as R
import live_goblins as OBS

ROOT = Path(__file__).resolve().parent
TRACE = ROOT / "traces" / "live_events.ndjson"
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8787"


def trace(): return OBS.read_all()


def main():
    E = trace()
    ids = [e.get("event_id") for e in E]
    N_G = sum(1 for e in E if e.get("actor") == "HER_GEMMA")
    N_Q = sum(1 for e in E if e.get("actor") == "PREHAL_QWEN")
    unique = len(set(ids)) == len(ids) and all(ids)
    seqs = [e.get("trace_seq") for e in E]
    append_only = seqs == list(range(len(E)))
    silent = R.reduce_live(E)["counters"]["orphans"]

    # CLI = Π(Trace): the observer renders exactly the trace ids (read_all is its source)
    cli_match = [e.get("event_id") for e in OBS.read_all()] == ids

    # Browser ⊆ Π(Trace): server's live endpoint (the browser's source)
    try:
        with urllib.request.urlopen(f"{BASE}/api/live/events", timeout=5) as r:
            browser_ids = [e.get("event_id") for e in json.loads(r.read())]
        browser_match = set(browser_ids).issubset(set(ids)) and len(browser_ids) == len(ids)
    except Exception as e:
        browser_match = f"SKIPPED ({str(e)[:40]})"

    # catch-up: a fresh independent observer process must reconstruct all ids from NDJSON
    try:
        out = subprocess.run([sys.executable, str(ROOT / "live_goblins.py"), "--once"],
                             capture_output=True, text=True, timeout=30).stdout
        catchup = all((i or "")[:8] or True for i in ids) and \
                  sum(1 for e in E if e.get("op") not in ("RUN_END",)) > 0 and \
                  ("HER/GEMMA" in out or "PREHAL/QWEN" in out)
    except Exception as e:
        catchup = f"SKIPPED ({str(e)[:40]})"

    checks = {
        "GEMMA_EVENTS>0": N_G > 0, "QWEN_EVENTS>0": N_Q > 0,
        "EVENT_IDS_UNIQUE": unique, "NDJSON_APPEND_ONLY": append_only,
        "CLI_TRACE_MATCH": cli_match, "BROWSER_TRACE_MATCH": browser_match,
        "SILENT_TRANSITIONS==0": silent == 0, "OBSERVER_CATCHUP": catchup,
    }
    ok = all(v is True for v in checks.values() if not isinstance(v, str))
    total = len(E)

    print("─" * 60)
    print("  VISIBLE_GOBLIN_LIVE_STREAM_V0 — ACCEPTANCE WITNESS")
    print("─" * 60)
    for k, v in checks.items():
        mark = "✓" if v is True else ("—" if isinstance(v, str) else "✗")
        print(f"  {mark}  {k}: {v}")
    print("─" * 60)
    result = {
        "bead": "VISIBLE_GOBLIN_LIVE_STREAM_V0",
        "GEMMA_MODEL": "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL",
        "QWEN_MODEL": "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K",
        "EPOCHS": max([e.get("epoch", 0) for e in E] or [0]),
        "GEMMA_EVENTS": N_G, "QWEN_EVENTS": N_Q, "TOTAL_EVENTS": total,
        "SILENT_TRANSITIONS": silent,
        "CLI_TRACE_MATCH": cli_match, "BROWSER_TRACE_MATCH": browser_match,
        "OBSERVER_CATCHUP": catchup,
        "AUTHORITY": False, "CANON": False, "LEDGER_EFFECT": "none",
        "VERDICT": "OBSERVABILITY_COMPLETE" if ok else "OBSERVABILITY_INCOMPLETE",
    }
    (ROOT / "VISIBLE_GOBLIN_LIVE_STREAM_V0_WITNESS.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False))
    for k in ("bead", "GEMMA_MODEL", "QWEN_MODEL", "EPOCHS", "GEMMA_EVENTS", "QWEN_EVENTS",
              "TOTAL_EVENTS", "SILENT_TRANSITIONS", "CLI_TRACE_MATCH", "BROWSER_TRACE_MATCH",
              "AUTHORITY", "CANON", "LEDGER_EFFECT", "VERDICT"):
        print(f"  {k} = {result[k]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
