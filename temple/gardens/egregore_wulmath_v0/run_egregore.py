#!/usr/bin/env python3
"""
EGREGORE WULMATH — HIGHER-DIMENSIONAL OBJECT SEARCH V0.

An asynchronous multi-substrate research egregore. Five cognitive seats +
a non-sovereign synthesizer collaborate over a shared structured blackboard
to look for an object Ω of which WULMath / HELEN / J-space / Oracle Town /
POC Factory appear as projections, sections or restrictions.

CONSTITUTION
------------
The whole egregore lives inside cognition-only closure:
    E_WUL ⊂ Cl_C     ⇒     ΔAuthority = 0.
No internal consensus becomes proof or authority. Every artifact is
CANDIDATE_ONLY, evidence=NONE, authority=false. Output routes to
temple/gardens (NON_SOVEREIGN). Nothing here crosses to the spine.

Consensus is STRUCTURAL, not majority: an object gains persistence when it is
independently reconstructed across distinct roles and survives HAL's attacks —
    Persistence(X) = R_independent + D_cross_role + S_attack + G_compression.
The synthesizer builds the current state of the problem; it does not rule.

Substrate heterogeneity (loaded one at a time — SOLO seat discipline):
    JESTER   Qwen3.8-27B abliterated   inversion / counterexample / frame-break
    GOBLIN_1 gemma4-12b                 wild recombination / distant analogy
    GOBLIN_2 aura-gemma4                cross-domain transfer / representation
    HER      helen-her-26b             search geometry / reframe (M,φ,τ,O)
    HAL      helen-hal                  cold adversary / break the object
    SYNTH    helen-core                 non-sovereign integrator (blackboard)
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SOT = ROOT.parents[2]
ROUNDS_DIR = ROOT / "rounds"
ROUNDS_DIR.mkdir(exist_ok=True)
OLLAMA = "http://localhost:11434/api/chat"

N_ROUNDS = 3
SESSION_DATE = "2026-08-23"

SEED = (
    "WULMATH HIGHER-DIMENSIONAL OBJECT SEARCH V0.\n"
    "HELEN/WULMath currently has objects that look separate: typed state "
    "calculus (Σ), licensed-transition architecture (Λ,Γ), search geometry "
    "(J-space), witness/proof classes, observer geometry, an authority "
    "projection A, and Color WULMath (emoji projection). Also: Oracle Town "
    "(compositional cognition) and POC Factory (experiment/discrimination).\n\n"
    "Find the smallest object Ω such that these appear as projections, "
    "sections or restrictions of Ω — e.g. J-space = Ω|non-promoting-cognition, "
    "HELEN = Ω|licensed-promotion, CEAX = coordinate decomposition of Σ. "
    "Produce MULTIPLE INCOMPATIBLE candidates, then a discriminator: an "
    "observation or property that would tell them apart."
)

# (seat, role, model, temperature, think)
GEN_SEATS = [
    ("JESTER", "inversion / counterexample / frame-break — propose the "
     "IMPOSSIBLE object, invert the obvious assumption",
     "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K", 0.9),
    ("GOBLIN_1", "wild recombination — bridge two DISTANT fragments on the "
     "blackboard into one unexpected object",
     "gemma4-12b:latest", 0.85),
    ("GOBLIN_2", "cross-domain transfer — import a structure from math/physics "
     "(sheaf, fiber bundle, category, moduli space, gauge) as the object",
     "aura-gemma4:latest", 0.85),
]
HER_SEAT = ("HER", "helen-her-26b:latest", 0.6)
HAL_SEAT = ("HAL", "helen-hal:latest", 0.35)
SYNTH_SEAT = ("SYNTHESIZER", "helen-core:latest", 0.5)

GEN_SCHEMA = """Return ONLY one JSON object:
{
 "higher_order_object": "<name the object Ω-candidate>",
 "why_subsumes": "<how current WULMath objects become its projections>",
 "one_equation": "<a single compact equation or typed relation>",
 "relation_to_blackboard": "<supports|contradicts|generalizes|subsumes|orthogonal> : <which prior idea>",
 "counterexample": "<one case that would break a naive version>",
 "blind_spot": "<what other seats are likely missing>",
 "open_question": "<one sharp question>"
}"""

HER_SCHEMA = """Return ONLY one JSON object:
{
 "geometry_change": "<how to restructure the search space (M,phi,tau,O) so a better object becomes visible>",
 "reframe": "<restate the current best candidate under the new geometry>",
 "one_equation": "<compact relation>",
 "open_question": "<one question>"
}"""

HAL_SCHEMA = """Return ONLY one JSON object:
{
 "attack": "<the hardest objection to the current emergent object>",
 "does_it_predict_new": "<does the object predict anything the flat model does not? be specific or say NO>",
 "distinguishes_two_architectures": "<name two architectures it separates that the product-state view cannot, or say NO>",
 "verdict": "SURVIVES | BROKEN"
}"""

SYNTH_SCHEMA = """Return ONLY one JSON object:
{
 "common_structure": "<what independent seats keep reconstructing>",
 "major_disagreements": "<the live incompatibility between candidates>",
 "emergent_object": "<the current best higher-order object>",
 "master_equation": "<one compact equation for it>",
 "discriminator": "<one observation/test that would separate the incompatible candidates>"
}"""


def git_head():
    return subprocess.run(["git", "-C", str(SOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def ollama_chat(model, system, user, temperature, num_predict=700, timeout=420):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "stream": False, "think": False,
        "options": {"temperature": temperature, "num_predict": num_predict},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    msg = d.get("message", {}) or {}
    return msg.get("content") or msg.get("thinking") or ""


def _loads_tolerant(s):
    """Parse JSON, repairing invalid LaTeX backslash escapes (\\sigma, \\otimes)
    that reasoning-about-math models emit constantly inside string values."""
    try:
        return json.loads(s)
    except Exception:
        pass
    # double any backslash not starting a valid JSON escape
    repaired = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
    return json.loads(repaired)


def extract_json(text):
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return _loads_tolerant(text[start:i + 1])
                    except Exception:
                        break
        start = text.find("{", start + 1)
    return None


def render_blackboard(bb, limit=10):
    """Compact structured view — artifacts only, never private reasoning."""
    if not bb:
        return "(blackboard empty — first contributions)"
    lines = []
    for a in bb[-limit:]:
        obj = a.get("higher_order_object") or a.get("emergent_object") \
            or a.get("reframe") or a.get("attack") or "(—)"
        lines.append(f"- [{a['_seat']}] {str(obj)[:160]}")
        rel = a.get("relation_to_blackboard") or a.get("geometry_change")
        if rel:
            lines.append(f"    rel: {str(rel)[:140]}")
    return "\n".join(lines)


def call_seat(seat, model, role_or_none, schema, temperature, blackboard, tag):
    sys_p = (
        "You are seat " + seat + " in a NO-CLAIM research egregore searching "
        "for a higher-dimensional object in WULMath. authority=false: nothing "
        "you produce is proof, canon, or authority — only a candidate. "
        + (("Your cognitive role: " + role_or_none + ". ") if role_or_none else "")
        + "You see only structured artifacts from the shared blackboard, never "
        "other seats' private reasoning. Be concrete and structural, not "
        "poetic. " + schema)
    user = (SEED + "\n\nCURRENT BLACKBOARD:\n" + render_blackboard(blackboard)
            + "\n\nContribute now. " + schema)
    t0 = time.time()
    try:
        raw = ollama_chat(model, sys_p, user, temperature)
    except Exception as e:
        raw = ""
        err = str(e)
    else:
        err = None
    dt = time.time() - t0
    art = extract_json(raw) or {}
    art["_seat"] = seat
    art["_model"] = model
    art["_wall_s"] = round(dt, 1)
    art["_parsed"] = bool(art) and any(
        k for k in art if not k.startswith("_"))
    if err:
        art["_error"] = err
    return art, raw


def main():
    head = git_head()
    blackboard = []
    round_snapshots = []
    hal_survives = hal_broken = 0
    candidates = []

    print("═" * 70)
    print("  🌌 EGREGORE WULMATH — HIGHER-DIMENSIONAL OBJECT SEARCH V0")
    print("  E_WUL ⊂ Cl_C   ⇒   ΔAuthority = 0     (NO_CLAIM · CANDIDATE_ONLY)")
    print("  seats: JESTER · GOBLIN_1 · GOBLIN_2 · HER · HAL  +  SYNTH")
    print("═" * 70, flush=True)

    for r in range(1, N_ROUNDS + 1):
        print(f"\n{'─'*70}\n🌌 EGREGORE ROUND {r:02d}/{N_ROUNDS}\n{'─'*70}", flush=True)
        # snapshot BEFORE this round → independent generation (no premature converge)
        snapshot = list(blackboard)

        # 1) independent generative seats
        for seat, role, model, temp in GEN_SEATS:
            art, raw = call_seat(seat, model, role, GEN_SCHEMA, temp, snapshot, r)
            blackboard.append(art)
            obj = art.get("higher_order_object", "(unparsed)")
            if art.get("_parsed") and obj != "(unparsed)":
                candidates.append({"round": r, "seat": seat, "object": obj})
            print(f"  🃏 {seat:9s} [{art['_wall_s']:5.1f}s] {str(obj)[:150]}", flush=True)
            eq = art.get("one_equation")
            if eq:
                print(f"       eq: {str(eq)[:150]}", flush=True)

        # 2) HER restructures the geometry
        her, _ = call_seat("HER", HER_SEAT[1],
                           "search geometry: change (M,phi,tau,O) so a better "
                           "object becomes visible", HER_SCHEMA, HER_SEAT[2],
                           blackboard, r)
        blackboard.append(her)
        print(f"  🔭 HER       [{her['_wall_s']:5.1f}s] "
              f"{str(her.get('geometry_change','(unparsed)'))[:150]}", flush=True)

        # 3) HAL attacks the current emergent object
        hal, _ = call_seat("HAL", HAL_SEAT[1],
                          "cold adversary: break the emergent object; demand it "
                          "predict something new or distinguish two architectures",
                          HAL_SCHEMA, HAL_SEAT[2], blackboard, r)
        blackboard.append(hal)
        verdict = str(hal.get("verdict", "")).upper()
        if "SURVIV" in verdict:
            hal_survives += 1
        elif "BROKEN" in verdict:
            hal_broken += 1
        print(f"  🛡  HAL       [{hal['_wall_s']:5.1f}s] verdict={verdict or '?'} "
              f":: {str(hal.get('attack','(unparsed)'))[:120]}", flush=True)

        # 4) synthesizer builds current state (does not rule)
        syn, _ = call_seat("SYNTHESIZER", SYNTH_SEAT[1], None, SYNTH_SCHEMA,
                          SYNTH_SEAT[2], blackboard, r)
        blackboard.append(syn)
        round_snapshots.append({"round": r, **{k: v for k, v in syn.items()
                                              if not k.startswith("_")}})
        print(f"  🌿 SYNTH     [{syn['_wall_s']:5.1f}s] emergent: "
              f"{str(syn.get('emergent_object','(unparsed)'))[:150]}", flush=True)
        print(f"       master_eq: {str(syn.get('master_equation',''))[:150]}", flush=True)
        print(f"       discriminator: {str(syn.get('discriminator',''))[:150]}", flush=True)

        (ROUNDS_DIR / f"round_{r:02d}.json").write_text(
            json.dumps({"round": r, "blackboard_len": len(blackboard),
                       "her": her, "hal": hal, "synth": syn},
                      indent=2, ensure_ascii=False))

    # final synthesis pass — full-run integration
    final_user = (SEED + "\n\nFULL BLACKBOARD (" + str(len(blackboard))
                  + " artifacts):\n" + render_blackboard(blackboard, limit=40)
                  + "\n\nProduce the EGREGORE SYNTHESIS. " + SYNTH_SCHEMA)
    fin_raw = ""
    try:
        fin_raw = ollama_chat(SYNTH_SEAT[1],
            "You are the non-sovereign SYNTHESIZER. authority=false. Integrate "
            "the whole run into the current state of the problem. Do not rule "
            "on truth. " + SYNTH_SCHEMA, final_user, 0.45, num_predict=900)
    except Exception as e:
        fin_raw = f"__ERROR__ {e}"
    final_synth = extract_json(fin_raw) or {"raw": fin_raw[:2000]}

    receipt = {
        "schema": "EGREGORE_WULMATH_RECEIPT_V0",
        "authority": False, "sovereign": False, "canon": False,
        "layer": "TEMPLE", "ledger": "SLEEPING", "status": "PROPOSED",
        "claim_type": "egregore_search", "evidence": "NONE",
        "batch": "EGREGORE_WULMATH_HIGHERDIM_V0",
        "session_date": SESSION_DATE, "head_at_run": head,
        "constitution": "E_WUL ⊂ Cl_C ⇒ ΔAuthority=0; consensus is structural, "
                        "not majority; no artifact crosses to the spine.",
        "seats": {"JESTER": GEN_SEATS[0][2], "GOBLIN_1": GEN_SEATS[1][2],
                  "GOBLIN_2": GEN_SEATS[2][2], "HER": HER_SEAT[1],
                  "HAL": HAL_SEAT[1], "SYNTHESIZER": SYNTH_SEAT[1]},
        "rounds": N_ROUNDS,
        "structural_signal": {
            "n_candidate_objects": len(candidates),
            "hal_rounds_survived": hal_survives,
            "hal_rounds_broken": hal_broken,
            "candidates": candidates,
        },
        "round_snapshots": round_snapshots,
        "egregore_synthesis": final_synth,
        "_meta": {"not_admitted": True, "not_canon": True,
                  "note": "Structural persistence is a discovery signal, not a "
                          "truth claim. The discriminator is the actual "
                          "deliverable — a meta-vision without a discriminator "
                          "is only a nice theory."},
    }
    (ROOT / "EGREGORE_WULMATH_V0_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))

    print("\n" + "═" * 70)
    print("  🌌 EGREGORE SYNTHESIS")
    print("═" * 70)
    for k in ("common_structure", "major_disagreements", "emergent_object",
              "master_equation", "discriminator"):
        print(f"  {k.upper()}:\n    {str(final_synth.get(k,'(—)'))[:400]}\n")
    print(f"  structural signal: {len(candidates)} candidate objects, "
          f"HAL survived {hal_survives}/{N_ROUNDS} rounds, broken {hal_broken}")
    print("  authority=false · CANDIDATE_ONLY · evidence=NONE")


if __name__ == "__main__":
    main()
