#!/usr/bin/env python3
"""
JSPACE_TRACE_V0 — closed event algebra + deterministic graph + bloom detector + pure renderer.

FOUR SEPARATED OBJECTS (the architecture's protection against a hallucinated CLI):
  content producers (transforms.py)  ≠  event extraction (validate)
  ≠  graph computation (build_graph) ≠  rendering (render)

LAWS:
  VisualEvent ⇐ TypedComputationalEvent          (no event ⇒ no glyph — converse discipline)
  T1 = T2  ⇒  R(T1) = R(T2)                        (pure renderer, replay-invariant)
  BLOOM is emitted by the DETECTOR, never by a model.
  ΔEvidence = ΔWarrant = ΔAuthority = ΔEffect = 0 · FABLE_CALLS = 0 · NO_CLAIM.
"""
import json, re
from pathlib import Path

# closed vocabulary Σ_J — no ontology explosion
SIGMA = ["BORN","TRANSFORMED","ATTACKED","KILLED","COLLIDED","QUOTIENTED",
         "SURVIVED","DISCRIMINATOR","OBSERVED","BLOOM"]
GLYPH = {"BORN":"🟣","TRANSFORMED":"🎭","ATTACKED":"⚔","KILLED":"☠","COLLIDED":"💥",
         "QUOTIENTED":"♻","SURVIVED":"🧬","DISCRIMINATOR":"🔥","OBSERVED":"🔵","BLOOM":"🌸"}
SEATS = {"HER","JESTER","HAL","DETECTOR","CONTROL"}


class InvalidEvent(Exception): pass


def validate(e):
    """Event extraction gate. Each type carries a mechanically-inspectable witness."""
    t = e.get("event_type")
    if t not in SIGMA: raise InvalidEvent(f"unknown event_type {t}")
    if e.get("seat") not in SEATS: raise InvalidEvent(f"unknown seat {e.get('seat')}")
    p = e.get("payload", {}) or {}
    par = e.get("parents", []) or []
    if t == "COLLIDED" and len(par) < 2:
        raise InvalidEvent("COLLIDED requires ≥2 parent branches")
    if t == "KILLED" and not e.get("branch"):
        raise InvalidEvent("KILLED requires a target branch")
    if t == "QUOTIENTED" and "equivalence" not in p:
        raise InvalidEvent("QUOTIENTED must carry an equivalence witness")
    if t == "DISCRIMINATOR" and not (p.get("x_star") and p.get("executable") is True):
        raise InvalidEvent("DISCRIMINATOR must carry an executable x_star (not a phrase)")
    if t == "OBSERVED" and not p.get("observation_receipt"):
        raise InvalidEvent("OBSERVED must reference an observation receipt")
    if t == "BLOOM" and e.get("seat") != "DETECTOR":
        raise InvalidEvent("BLOOM may only be emitted by the DETECTOR")
    if t == "TRANSFORMED" and (e.get("seat") != "JESTER" or "theta" not in p):
        raise InvalidEvent("TRANSFORMED must be seat=JESTER with payload.theta")
    return e


def emit(trace, seat, event_type, branch, parents=None, payload=None):
    e = {"id": f"e{len(trace):03d}", "t": len(trace), "seat": seat,
         "branch": branch, "event_type": event_type,
         "parents": parents or [], "payload": payload or {}}
    validate(e); trace.append(e); return e


# ------- graph computation (deterministic fold; no rendering, no payload text) -------
def build_graph(trace):
    branches, collisions, quotients = {}, [], []
    for e in trace:
        b, t, p = e.get("branch"), e["event_type"], e.get("payload", {})
        if b and b not in branches and t in ("BORN", "TRANSFORMED"):
            branches[b] = {"id": b, "state": "BORN", "invariant": p.get("invariant"),
                           "class": p.get("invariant") or b, "theta": p.get("theta"),
                           "x_star": None, "executable": False, "discriminated": False,
                           "observed": False, "parents": e.get("parents", [])}
        if b in branches:
            if t == "ATTACKED": branches[b]["state"] = "ATTACKED"
            elif t == "KILLED": branches[b]["state"] = "KILLED"
            elif t == "SURVIVED": branches[b]["state"] = "SURVIVED"
            elif t == "DISCRIMINATOR":
                branches[b]["discriminated"] = True
                branches[b]["x_star"] = p.get("x_star"); branches[b]["executable"] = True
            elif t == "OBSERVED": branches[b]["observed"] = True
        if t == "COLLIDED": collisions.append(e.get("parents", []))
        if t == "QUOTIENTED": quotients.append(p.get("equivalence"))
    # structural classes (quotient by invariant/class)
    classes = {}
    for b in branches.values():
        classes.setdefault(b["class"], []).append(b["id"])
    return {"branches": branches, "collisions": collisions,
            "quotients": quotients, "classes": classes}


# ------- deterministic BLOOM detector: B(b)=N ∧ ¬D ∧ F ∧ T ∧ X, each with a witness -------
def detect_blooms(trace, graph, seed_classes, min_frames=2):
    blooms = []
    classes = graph["classes"]
    for cls, members in classes.items():
        survivors = [graph["branches"][m] for m in members
                     if graph["branches"][m]["state"] == "SURVIVED"]
        if not survivors: continue
        frames = sorted({graph["branches"][m]["theta"] for m in members
                         if graph["branches"][m]["theta"]})
        N = cls not in seed_classes
        D = cls in seed_classes
        F = len(frames) >= min_frames                     # survived ≥k alien frames
        T = any(b["discriminated"] for b in survivors)    # falsifiable consequence
        X = any(b["executable"] for b in survivors)       # local executable discriminator
        witness = {"N": N, "not_D": not D, "F": F, "T": T, "X": X,
                   "class": cls, "frames": frames, "min_frames": min_frames}
        if N and (not D) and F and T and X:
            blooms.append({"class": cls, "witness": witness})
    return blooms


# ------- pure renderer: R(trace) → ANSI. Only events present get glyphs. -------
C = {"v":"\033[38;2;192;139;255m","j":"\033[38;2;255;140;200m","h":"\033[38;2;255;157;60m",
     "g":"\033[38;2;80;220;140m","dim":"\033[38;2;90;110;100m","w":"\033[38;2;210;235;220m",
     "b":"\033[1m","r":"\033[0m"}
SEATCOL = {"HER":C["g"],"JESTER":C["j"],"HAL":C["h"],"DETECTOR":C["v"],"CONTROL":C["dim"]}


def render(trace, blooms=None):
    out = []
    out.append(f"{C['v']}{C['b']}╭─ HELEN // J-SPACE  (Π of trace) ─ Δ👑=0 ─────────────╮{C['r']}")
    counts = {k: 0 for k in SIGMA}
    for e in trace:
        t = e["event_type"]; counts[t] += 1
        col = SEATCOL.get(e["seat"], C["dim"]); g = GLYPH[t]
        par = f" ← {e['parents']}" if e.get("parents") else ""
        extra = ""
        p = e.get("payload", {})
        if t == "TRANSFORMED": extra = f"  θ={p.get('theta')}  inv={p.get('invariant')}"
        elif t == "DISCRIMINATOR": extra = f"  x*={p.get('x_star')}"
        elif t == "QUOTIENTED": extra = f"  ≡ {p.get('equivalence')}"
        elif t == "KILLED": extra = f"  ({p.get('reason','')})"
        out.append(f"  {C['dim']}[{e['id']}·{e['seat']:8s}]{C['r']} {col}{g} {t:12s}{C['r']}"
                   f" {C['w']}{e.get('branch','')}{C['r']}{C['dim']}{par}{extra}{C['r']}")
    for bl in (blooms or []):
        out.append(f"  {C['j']}{C['b']}🌸 BLOOM  class={bl['class']}  "
                   f"frames={bl['witness']['frames']}  (N∧¬D∧F∧T∧X){C['r']}")
    # footer: counts, and the constitutional invariant
    out.append(f"{C['v']}├{'─'*52}┤{C['r']}")
    nz = " · ".join(f"{GLYPH[k]}{counts[k]}" for k in SIGMA if counts[k])
    out.append(f"  {C['dim']}{nz}{C['r']}")
    out.append(f"  {C['dim']}🔵 evidence 0 · 🟡 warrant 0 · 👑 authority 0 · 💰 FABLE 0{C['r']}")
    out.append(f"{C['v']}╰{'─'*52}╯{C['r']}")
    return "\n".join(out)


def topology_signature(trace):
    """Structural signature IGNORING payload text — for the 'same semantics ⇒ same topology' test."""
    g = build_graph(trace)
    sig = {"events": [(e["event_type"], e.get("branch"), tuple(e.get("parents", []))) for e in trace],
           "classes": {k: sorted(v) for k, v in sorted(g["classes"].items())},
           "states": {b: g["branches"][b]["state"] for b in sorted(g["branches"])}}
    return json.dumps(sig, sort_keys=True)


if __name__ == "__main__":
    print("Σ_J =", SIGMA)
