#!/usr/bin/env python3
"""
JESTER_BLOOM — a bloom that is COMPUTED, not decorated.

The panel is generated from real numbers: MIRROR is executed via provenance_rank
(the one 🟢 frame transform); the other eight frames render as 🌿 NOT_EXECUTED —
no faked survival ticks (anti-mockup: a tick appears only when a frame actually ran).
The 🌸 bloom crystallizes ONLY if MIRROR finds a real structural delta (N_repr⊬N_epi);
on a claim with independent roots it refuses to bloom.

Δattention>0 allowed · Δevidence=Δwarrant=Δauthority=Δeffect=0 · FABLE_CALLS=0 · NO_CLAIM.

  python3 jester_bloom.py                     # χ* self-test (inflated → blooms)
  python3 jester_bloom.py <items.json> "<claim G0>"
"""
import json, sys
from pathlib import Path
import provenance_rank as PR

C = {"v":"\033[38;2;192;139;255m","g":"\033[38;2;80;220;140m","dim":"\033[38;2;90;110;100m",
     "pink":"\033[38;2;255;140;200m","amber":"\033[38;2;255;200;70m","w":"\033[38;2;210;235;220m",
     "b":"\033[1m","r":"\033[0m"}
def bar(x, n=10): f=int(round(max(0,min(1,x))*n)); return "█"*f+"░"*(n-f)

# the frame family Θ. `run` = do we actually compute it? Only MIRROR today.
THETA = [
 ("MIRROR",  "apply the evaluator's rule to itself",      True),
 ("INV",     "negate the central assumption",             False),
 ("ROLE",    "swap witness ↔ copier",                     False),
 ("SCALE",   "document → corpus → institution",           False),
 ("TIME",    "forward ↔ reverse horizon",                 False),
 ("EDGE",    "ordinary case → boundary case",             False),
 ("NULL",    "remove assumed source independence",        False),
 ("REDUCTIO","confirmation × ∞",                          False),
 ("ADV",     "optimize from the opponent's frame",        False),
]


def bloom(items, g0):
    c = PR.census(items)
    inflated = c["N_epi"] < c["N_repr"]
    P=lambda s="": print(s)
    P(f"{C['pink']}{C['b']}╔{'═'*60}╗{C['r']}")
    P(f"{C['pink']}{C['b']}║  🌈 HELEN OS // JESTER BLOOM — COMPUTED, not drawn      Δ👑=0 ║{C['r']}")
    P(f"{C['pink']}{C['b']}╚{'═'*60}╝{C['r']}")
    P(f"  BASE OBJECT  {C['v']}🟣 G₀{C['r']}  \"{g0}\"")
    P(f"{C['dim']}  ── FRAME ORBIT Θ (🟢 executed · 🌿 held) ──────────────────{C['r']}")
    for name, desc, run in THETA:
        if run:
            P(f"  {C['g']}{C['b']}🎭 {name:8s} 🟢 EXECUTED{C['r']}  {C['dim']}{desc}{C['r']}")
            P(f"     {C['g']}→ {c['N_repr']} representations collapse to "
              f"{c['N_epi']} provenance roots  ({c['inflation_factor']}× inflation){C['r']}")
            P(f"     {C['g']}→ dominant root {c['dominant_root']} carries "
              f"{c['dominant_share']*100:.0f}%{C['r']}")
        else:
            P(f"  {C['dim']}🌿 {name:8s} ·· NOT_EXECUTED   {desc}{C['r']}")

    # 🔦 CHIDDUSH detector — the REAL structural delta MIRROR exposed
    P(f"{C['dim']}  ── 🔦 CHIDDUSH DETECTOR ──────────────────────────────────{C['r']}")
    if inflated:
        P(f"  {C['w']}NEW STRUCTURAL DELTA:  N_repr ⊬ N_epi   ({c['N_repr']} ⊬ {c['N_epi']}){C['r']}")
        P(f"  {C['w']}hidden assumption:     \"confirmation count ≈ independent support\"{C['r']}")
        P(f"  {C['amber']}candidate x*:          collapse all representations by provenance root "
          f"(executable, €0){C['r']}")
    else:
        P(f"  {C['dim']}no inflation — roots are independent — nothing to expose here{C['r']}")

    # honest metrics (only what we computed)
    P(f"{C['dim']}  ── METRICS (computed, not assigned) ──────────────────────{C['r']}")
    P(f"  independent_roots N_epi   {C['w']}{c['N_epi']}{C['r']}   of {c['N_repr']} representations")
    P(f"  inflation_factor          {bar(min(1,c['inflation_factor']/5))}  {c['inflation_factor']}×")
    P(f"  dominant_root_share       {bar(c['dominant_share'])}  {c['dominant_share']:.2f}")
    P(f"  frames_executed           {bar(1/len(THETA))}  1/{len(THETA)}  (rest 🌿 held)")

    # frame robustness — HONEST: only MIRROR ran, so 1/1 executed, not 5/8 faked
    P(f"{C['dim']}  ── 🌺 FRAME ROBUSTNESS ──────────────────────────────────{C['r']}")
    P(f"  executed frames survived structurally: {C['g']}1/1 (MIRROR){C['r']}  "
      f"{C['dim']}· 8 held, not evaluated{C['r']}")
    P(f"  {C['dim']}🎭 robust under frames ≠ 🔵 true   ·   TRUTH-STATUS = NOT EVALUATED{C['r']}")

    # 🌸 bloom crystallizes only if real
    P(f"{C['dim']}  ── 🌈 BLOOM ────────────────────────────────────────────{C['r']}")
    if inflated:
        P(f"  {C['pink']}{C['b']}       🌸 BLOOM — MIRROR exposed a real invariant{C['r']}")
        P(f"  {C['pink']}    🎭──🟣 G₀──🔦   →   🔥 x*(collapse-by-root)   →   ❓  [STOP]{C['r']}")
    else:
        P(f"  {C['dim']}       (no bloom — MIRROR found nothing to expose; honest-empty){C['r']}")

    # permanent constitutional footer
    P(f"{C['pink']}  ┌{'─'*58}┐{C['r']}")
    P(f"{C['pink']}  │ 🎭 Δattention ↑   ·   Δevidence=Δwarrant=Δauthority=Δeffect=0 │{C['r']}")
    P(f"{C['pink']}  │ 🧠 cognition +1   ·   👑 authority +0   ·   💰 FABLE avoided   │{C['r']}")
    P(f"{C['pink']}  └{'─'*58}┘{C['r']}")
    return {"census": c, "inflated": inflated, "frames_executed": 1, "frames_held": len(THETA)-1,
            "bloom": inflated, "authority_delta": 0, "fable_calls": 0, "claim": "NO_CLAIM"}


def main():
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        items = json.loads(Path(sys.argv[1]).read_text())
        g0 = sys.argv[2] if len(sys.argv) > 2 else "(supplied claim)"
    else:
        items, g0 = PR.CHI_STAR, "Repeated confirmation increases confidence"
    res = bloom(items, g0)
    (Path(__file__).resolve().parent / "JESTER_BLOOM_RESULT.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
