#!/usr/bin/env python3
"""
LIVE MATRIX WALL — independent observer for the Goblin event bus.

Tails traces/live_events.ndjson and renders each typed AgentEvent in ANSI 24-bit
as it arrives. On start it CATCHES UP from the append-only file (reconstructing
the witnessed stream) then follows the live frontier. It is a pure projection:
    Terminal = Π_CLI(Trace)
It runs standalone — start it before, during, or after the Garden; kill it and
restart it mid-run and it rebuilds from NDJSON. Claude-process death ≠ observer
death ≠ trace loss.   ΔA=0 · NO_CLAIM · reads only, writes nothing.

  python3 live_goblins.py            # follow forever (Ctrl-C to stop)
  python3 live_goblins.py --once     # render current trace and exit (for tests)
Also runnable as:  python3 -m ...garden_scope_v0.live_goblins
"""
import json, sys, time
from pathlib import Path

TRACE = Path(__file__).resolve().parent / "traces" / "live_events.ndjson"
C = {  # 24-bit truecolor by actor / op
    "HER_GEMMA": "\033[38;2;79;211;196m", "PREHAL_QWEN": "\033[38;2;255;157;60m",
    "CONTROL": "\033[38;2;140;255;206m", "dim": "\033[38;2;76;138;106m",
    "PROPOSE": "🌿", "MUTATE": "🧬", "COUNTERFEIT": "🃏", "ATTACK": "🔥",
    "DISTINCTION": "💎", "DISCRIMINATE": "🧪", "HOLD": "🟡", "COMPOST": "⚫",
    "CHIDDUSH_CANDIDATE": "🟣", "CROSS": "🧬", "RUN_END": "⏹", "r": "\033[0m",
}
COUNT = {}


def render(e):
    actor = e.get("actor", "?"); op = e.get("op", "?")
    col = C.get(actor, "\033[0m"); glyph = C.get(op, "•")
    tag = f"[E{e.get('epoch',0):02d}·{e.get('trace_seq',0):03d}]"
    who = {"HER_GEMMA": "HER/GEMMA", "PREHAL_QWEN": "PREHAL/QWEN", "CONTROL": "CONTROL"}.get(actor, actor)
    print(f"{C['dim']}{tag}{C['r']} {col}{glyph} {who:11s} {op:16s}{C['r']} "
          f"{C['dim']}{e.get('object_id','')}{C['r']}"
          + (f" ← {e.get('parent_ids')}" if e.get("parent_ids") else ""))
    for k in ("distinction", "mechanism", "counterfeit", "discriminator", "next_move"):
        v = e.get(k)
        if v: print(f"        {C['dim']}{k}:{C['r']} {v[:88]}")
    COUNT[actor] = COUNT.get(actor, 0) + 1


def footer():
    g = COUNT.get("HER_GEMMA", 0); q = COUNT.get("PREHAL_QWEN", 0)
    print(f"{C['dim']}── HER/GEMMA {g} · PREHAL/QWEN {q} events · "
          f"🔵 evidence 0 · ⚖ ΔA 0 · ⚡ effect 0 ──{C['r']}", flush=True)


def read_all():
    if not TRACE.exists(): return []
    out = []
    for ln in TRACE.read_text().splitlines():
        ln = ln.strip()
        if ln:
            try: out.append(json.loads(ln))
            except json.JSONDecodeError: pass
    return out


def main():
    once = "--once" in sys.argv
    print(f"{C['CONTROL']}🌈 LIVE MATRIX WALL — tailing {TRACE.name} (independent observer){C['r']}")
    seen = 0
    # catch-up from the append-only trace
    for e in read_all():
        render(e); seen += 1
        if e.get("op") == "RUN_END": footer()
    if once:
        footer(); return
    footer()
    # follow the frontier
    try:
        while True:
            evs = read_all()
            if len(evs) > seen:
                for e in evs[seen:]:
                    render(e)
                    if e.get("op") == "RUN_END": footer()
                seen = len(evs); footer()
            time.sleep(0.4)
    except KeyboardInterrupt:
        print(f"\n{C['dim']}↩ observer closed · trace intact · Garden unaffected{C['r']}")


if __name__ == "__main__":
    main()
