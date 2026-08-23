#!/usr/bin/env python3
"""
GARDEN_SCOPE_V0 — the Garden as a cognitive oscilloscope, not a chat log.

Renders a 1970s–90s AI-observatory console (CRT phosphor, dual channel, Φ seam,
diagnostic registers) DRIVEN ENTIRELY BY TYPED STATE read from real receipts.

CONSTITUTIONAL LAW (enforced structurally, not decoratively):
    color = projection(typed_state)          # never the inverse
    D:(H,Θ)→V  ·  vintage aesthetic ∈ Θ      # look is presentation-only
    ΔX = ΔP = ΔE = ΔA = 0  ·  NO_CLAIM       # rendering mutates nothing

ANTI-MOCKUP: every counter, glyph, seam-position and intensity below is a pure
function of a receipt field. Nothing is hand-authored for drama. If the gate
typed 0 objects, the zone below Φ renders EMPTY. An empty result looks empty.

Usage:
    python3 garden_scope.py                      # defaults to the chaos garden
    python3 garden_scope.py <chaos_receipt.json> <gate_receipt.json>
    python3 garden_scope.py --amber             # amber phosphor instead of green
"""
import json, sys
from pathlib import Path

GARDEN = Path(__file__).resolve().parent.parent / "async_wulmath_chaos_garden_v1"
DEF_CHAOS = GARDEN / "ASYNC_WULMATH_CHAOS_GARDEN_V1_RECEIPT.json"
DEF_GATE = GARDEN / "HARD_CHIDDUSH_GATE_RECEIPT.json"
W = 62  # console inner width

# --- phosphor palette (Θ). Chosen by --amber flag; carries no semantics. -------
def palette(amber):
    p = 214 if amber else 47      # phosphor base
    return {
        "phos": f"\033[38;5;{p}m", "dim": f"\033[38;5;{238}m",
        "chA": "\033[38;5;79m",    # HER channel — teal-green vector
        "chB": "\033[38;5;208m",   # HAL channel — magenta/amber counter-vector
        "typed": "\033[38;5;141m", # 🟣 typed object (below Φ) — violet
        "seam": f"\033[38;5;{p}m", "b": "\033[1m", "r": "\033[0m",
        "flash": "\033[38;5;231m",
    }

# --- verdict → typed position. This IS the semantics→presentation projection. --
def below_phi(verdict):    # only SURVIVES crosses the membrane into the typed zone
    return "SURVIV" in verdict.upper()

def trace_glyph(verdict):  # glyph is a function of typed verdict, nothing else
    v = verdict.upper()
    if "SURVIV" in v:   return "🟣", "typed"
    if "RENAMING" in v: return "✕", "dim"      # collapsed into counterfeit → evaporates
    if "EVIDEN" in v:   return "·", "chB"       # unresolved → faint, still above seam
    return "?", "dim"


def bar(x, lo=0.0, hi=1.0, width=10):
    n = int(round((max(lo, min(hi, x)) - lo) / (hi - lo) * width))
    return "█" * n + "░" * (width - n)


def line(C, s=""):
    # pad a content line inside the CRT frame to width W
    raw = _visible_len(s)
    pad = " " * max(0, W - raw)
    print(f"{C['phos']}│{C['r']} {s}{pad} {C['phos']}│{C['r']}")

def _visible_len(s):
    import re
    return len(re.sub(r"\033\[[0-9;]*m", "", s))

def rule(C, ch="─"):
    print(f"{C['phos']}{'├' if ch=='─' else '╞'}{ch*(W+2)}{'┤' if ch=='─' else '╡'}{C['r']}")

def top(C):    print(f"{C['phos']}┌{'─'*(W+2)}┐{C['r']}")
def bot(C):    print(f"{C['phos']}└{'─'*(W+2)}┘{C['r']}")


def render(chaos, gate, C):
    ch = json.loads(Path(chaos).read_text()) if Path(chaos).exists() else {}
    gt = json.loads(Path(gate).read_text()) if Path(gate).exists() else {}
    verdicts = gt.get("all_verdicts", [])

    top(C)
    line(C, f"{C['b']}HELEN // ORACLE TOWN // GARDEN CHANNEL{C['r']}")
    line(C, f"{C['dim']}scope: {ch.get('schema','—')[:44]}{C['r']}")
    a = ch.get("authority_delta", gt.get("authority_delta", "—"))
    line(C, f"AUTHORITY={a}   CLAIM={ch.get('claim', gt.get('claim','—'))}"
            f"   FABLE_CALLS={ch.get('fable_calls','—')}")
    rule(C, "═")

    # ---- dual channel counters (from typed fields) ----------------------------
    her = ch.get("her_raw_objects", "—"); hal = ch.get("hal_raw_objects", "—")
    line(C, f"{C['chA']}CH-A HER/GEMMA4{C['r']}   gen {her:>3}      "
            f"{C['chB']}CH-B HALᵖ/QWEN{C['r']}   gen {hal:>3}")
    line(C, f"{C['dim']}distinct {ch.get('distinct_structures','—')}   "
            f"renaming(self) {ch.get('renaming_only','—')}   "
            f"dup-rate {ch.get('duplication_rate','—')}{C['r']}")
    rule(C)

    # ---- above-Φ traces: everything the gate did NOT type (evaporating) --------
    line(C, f"{C['dim']}[ VECTOR SCOPE ]  fitness bars = gate fitness (typed){C['r']}")
    above = [v for v in verdicts if not below_phi(v.get("verdict", ""))]
    for v in above[:14]:
        g, col = trace_glyph(v["verdict"])
        chan = C["chA"] if v.get("stream") == "HER" else C["chB"]
        nm = v["name"][:30]
        b = bar(float(v.get("fitness", 0) or 0))
        line(C, f"{chan}{v.get('stream','?'):3}{C['r']} {C[col]}{g}{C['r']} "
                f"{nm:<30} {C['dim']}{b}{C['r']}")
    if len(above) > 14:
        line(C, f"{C['dim']}   … +{len(above)-14} more evaporating above seam{C['r']}")

    # ---- the Φ membrane -------------------------------------------------------
    rule(C, "═")
    typed = ch and [v for v in verdicts if below_phi(v.get("verdict", ""))]
    surv = gt.get("survives", 0)
    line(C, f"{C['seam']}{C['b']}════════════ Φ  MEMBRANE  ════════════{C['r']}  "
            f"{C['dim']}typed={surv}{C['r']}")
    rule(C, "═")

    # ---- below-Φ: typed objects. HONEST: empty if surv==0 ---------------------
    if typed:
        for v in typed:
            line(C, f"{C['typed']}🟣 {v['name'][:40]}  fit={v.get('fitness')}{C['r']}")
    else:
        line(C, f"{C['dim']}(( no objects crossed Φ — typed zone empty )){C['r']}")
        line(C, f"{C['dim']}   0 typed · {gt.get('renaming_only_compost','—')} composted"
                f" · {gt.get('evidence_needed','—')} evidence-needed{C['r']}")

    # ---- diagnostic register --------------------------------------------------
    rule(C, "═")
    line(C, f"Φ BOUNDARY  {surv} typed / "
            f"{gt.get('renaming_only_compost',0)+gt.get('evidence_needed',0)} discarded "
            f"/ W=0 / A=0")
    line(C, f"{C['dim']}color=projection(typed_state) · vintage∈Θ · ΔA=0 · NO_CLAIM{C['r']}")
    bot(C)


def main(argv):
    amber = "--amber" in argv
    argv = [a for a in argv if not a.startswith("--")]
    chaos = argv[0] if len(argv) > 0 else DEF_CHAOS
    gate = argv[1] if len(argv) > 1 else DEF_GATE
    render(chaos, gate, palette(amber))


if __name__ == "__main__":
    main(sys.argv[1:])
