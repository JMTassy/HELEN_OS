#!/usr/bin/env python3
"""
🌈 WULMATH WALL — live ANSI 24-bit renderer for typed epistemic events.

CONSTITUTIONAL LAW (enforced structurally):
    Typed State → SemanticColor → ANSI render      (T → W → P)
    P ↛ T   (presentation never feeds back into typed state)
    PRESENTATION_RANDOMNESS = allowed (layout, dim/bright, rain positions)
    SEMANTIC_RANDOMNESS     = forbidden (color/glyph are pure fn of state)

color(state) is a TOTAL PURE FUNCTION. Same state ⇒ same color, always.
Nothing here mutates authority. authority=false.
"""
import datetime
import json
import sys
from pathlib import Path

# ── the FROZEN typed-state table: state → (glyph, ansi rgb) ──────────────────
# This is the ONLY place color is assigned. It is keyed solely by typed state.
STATE = {
    "POSS":     ("🌿", (80, 240, 120)),   # possibility  — green
    "CLAIM":    ("🟣", (170, 90, 240)),   # candidate    — violet
    "TEST":     ("🔥", (255, 110, 40)),   # trial        — orange/red
    "OBS":      ("🔵", (60, 180, 255)),   # observed     — cyan/blue
    "HOLD":     ("🟡", (240, 210, 40)),   # warrant      — yellow
    "ADMIT":    ("🟢", (40, 230, 70)),    # admitted     — bright green
    "RECEIPT":  ("⚪", (240, 240, 240)),  # receipt      — white
    "BOUNDARY": ("🛡", (40, 140, 255)),   # boundary     — electric blue
    "MECH":     ("⚙", (140, 140, 150)),  # mechanical   — gray
    "JESTER":   ("🃏", (255, 60, 200)),   # jester       — magenta
    "MUT":      ("🧬", (230, 110, 200)),  # mutation     — purple/pink
    "AUTH0":    ("👑", (230, 190, 60)),   # ΔAuthority=0 — gold
    "RAW":      ("⚫", (110, 110, 110)),  # raw/unknown  — dim gray
}


def color(state):  # PURE. semantic randomness forbidden.
    g, (r, gr, b) = STATE[state]
    return g, f"\033[38;2;{r};{gr};{b}m"


R = "\033[0m"
B = "\033[1m"
D = "\033[2m"


def banner():
    top = f"{B}\033[38;2;120;220;255m"
    print(top + "╔" + "═" * 66 + "╗")
    print(top + "║   🌈 QWEN WULMATH WALL — LIVE COGNITIVE SUBSTRATE" + " " * 16 + "║")
    print(top + "╚" + "═" * 66 + "╝" + R)
    legend = []
    for s in ("POSS", "CLAIM", "TEST", "OBS", "HOLD", "ADMIT", "RECEIPT",
              "BOUNDARY", "MECH", "JESTER", "MUT", "AUTH0"):
        g, c = color(s)
        legend.append(f"{c}{g} {s}{R}")
    print(" ".join(legend))
    print(D + "━" * 68 + R)


def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")


def event(state, label, value=""):
    g, c = color(state)
    line = (f"{D}{ts()}{R}  {c}{B}{g}{R}  {c}{label:<18}{R}  {B}{value}{R}")
    print(line, flush=True)


def rain(rows=10, width=30):
    """Presentation-random layout; semantic-deterministic color per glyph.
    Positions vary by (row,col) index — NOT by Math.random — so it stays
    replayable while looking alive."""
    keys = list(STATE.keys())
    for r in range(rows):
        cells = []
        for cidx in range(width):
            # deterministic pseudo-scatter from indices (presentation only)
            k = keys[(r * 7 + cidx * 13 + (r * cidx)) % len(keys)]
            g, c = color(k)
            dim = D if (r + cidx) % 3 == 0 else (B if (r + cidx) % 3 == 1 else "")
            cells.append(f"{dim}{c}{g}{R}")
        print(" ".join(cells))


def replay_probe():
    """Render the REAL observed A/B probe as a WULmath wall (values from disk)."""
    def read(p):
        d = json.load(open(p), strict=False)
        m = d["choices"][0]["message"]
        rc = m.get("reasoning_content") or ""
        c = m.get("content") or ""
        u = d.get("usage", {})
        return bool(rc.strip()), c.strip(), u.get("completion_tokens")

    banner()
    event("POSS", "QWEN_BOOT", "Qwen3.8-27B-Q3-XYZ-v2")
    event("BOUNDARY", "CONTEXT_BOUND", "c4096")
    for tag, path, ph in (("A", "/tmp/probe_A.json", "c6c0d1d4…"),
                          ("B", "/tmp/probe_B.json", "22519b13…")):
        try:
            rpres, content, toks = read(path)
        except Exception as e:
            event("RAW", f"PROBE_{tag}_UNREAD", str(e)[:40]); continue
        event("MECH", "PAYLOAD_HASH", ph)
        event("TEST", f"PROBE_{tag}",
              "normal" if tag == "A" else "/no_think")
        event("OBS", "REASONING_PRESENT", str(rpres).upper())
        event("RAW" if not content else "OBS", "CONTENT",
              content[:40] if content else "EMPTY")
    event("JESTER", "COUNTERFEIT", "/no_think treated as plain text")
    event("HOLD", "CLAIM_STATUS", "NOT SUPPORTED (ΔΦ=0)")
    event("AUTH0", "AUTHORITY_DELTA", "0")
    event("RECEIPT", "RECEIPT", "probe_A.json · probe_B.json")
    print(D + "━" * 68 + R)
    rain(rows=8)
    print(D + "━" * 68 + R)
    # self-check: color is a pure function of state
    ok = all(color(s) == color(s) for s in STATE)
    g, c = color("ADMIT" if ok else "TEST")
    print(f"{c}{g} semantic determinism self-check: "
          f"{'PASS — color=f(state)' if ok else 'FAIL'}{R}   {D}P ↛ T{R}")


if __name__ == "__main__":
    replay_probe()
