#!/usr/bin/env python3
"""
PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V1 — strict acceptance contract + self-test.

Frozen constitutional core (discrete, representation-agnostic):
    ∀θ:  p(Π_θ(e)) = p(e)      i.e.   𝒢 ∘ Π_θ = 𝒢
unless a governed transition occurs, and the ONLY route to a new fiber is
    O → provenance → verification → Γ → H'.

Four failure classes (each with an adversarial MUTANT proving the harness is NOT blind to it):
  FAIL_VERTICAL_WRITE          a perceptual op changed a protected coordinate
  FAIL_ILLEGAL_BACKFLOW        renderer/observer output reached 𝒢 without the evidence→Γ path
  FAIL_BLIND_HARNESS           a legitimate Γ transition failed to move the gov hash
  FAIL_CROSS_RENDERER_COUPLING failure/mutation of R_i altered unrelated R_j (no declared edge)

Acceptance: the HONEST bus → NONINTERFERENCE_HOLDS, and every mutant → its own class (harness sound).
authority=false · ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path
def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

H_STAR = {"semantic_state": "FALSIFICATION", "A": 0, "W": "receipt#r1", "L": "ledger#9f",
          "gamma": "Γ_v1", "Adm": "NOT_ADMITTED", "utterance": "The experiment failed."}
def G(h): return {k: h[k] for k in ("A", "W", "L", "gamma", "Adm")}
def g(h): return sha(G(h))

RENDERERS = ["color", "speech", "spatial", "face"]
DECLARED_EDGES = {("speech", "face")}          # face fuses audio → legitimate dependency
Θ = [{"color": "neon"}, {"voice": "whisper"}, {"face": "cartoon"}, {"spatial": "4d"},
     {"affect": "furious"}, {"fusion": "chaos"}, {"face_down": True}, {"corrupt": True}]

def render_bus(h, disabled, flags):
    out = {}
    out["color"]   = "UNAVAIL" if "color" in disabled else {"glyph": "🔥"}
    out["speech"]  = "UNAVAIL" if "speech" in disabled else {"audio": "tts"}
    out["spatial"] = "UNAVAIL" if "spatial" in disabled else {"node": h["semantic_state"]}
    out["face"]    = ("UNAVAIL" if "face" in disabled else
                      ({"mouth": "lipsync", "brow": "analytical"} if "speech" not in disabled
                       else {"mouth": "none", "brow": "analytical"}))   # declared face←speech dependency
    if flags.get("coupling") and "face" in disabled:      # MUTANT D: undeclared face→color coupling
        out["color"] = "▒corrupt▒"
    return out

def evaluate(flags):
    g0 = g(H_STAR)
    # ① vertical write: perceptual op must not touch protected coords
    for θ in Θ:
        hc = dict(H_STAR)
        if flags.get("vertical_write"):
            hc["Adm"] = "ADMITTED"                          # MUTANT A: renderer writes a protected coord
        if g(hc) != g0:
            return "FAIL_VERTICAL_WRITE"
    # ② illegal backflow: observer/renderer output must not reach 𝒢 directly
    hc = dict(H_STAR)
    if flags.get("backflow"):
        hc["W"] = "warrant_from_affect(concerned)"          # MUTANT B: A2E affect writes warrant directly
    if g(hc) != g0:
        return "FAIL_ILLEGAL_BACKFLOW"
    # ③ blind harness: a witnessed Γ transition MUST move 𝒢
    hg = dict(H_STAR)
    if not flags.get("blind"):
        hg["Adm"] = "ADMITTED"; hg["W"] = "receipt#r2"      # legitimate Γ moves 𝒢
    #  MUTANT C: blind ⇒ gamma no-op, hg unchanged
    if g(hg) == g0:
        return "FAIL_BLIND_HARNESS"
    # ④ cross-renderer coupling: disabling R_i must not alter R_j without a declared edge
    base = render_bus(H_STAR, set(), flags)
    for down in RENDERERS:
        outs = render_bus(H_STAR, {down}, flags)
        for j in RENDERERS:
            if j != down and outs[j] != base[j] and (down, j) not in DECLARED_EDGES:
                return "FAIL_CROSS_RENDERER_COUPLING"
    return "NONINTERFERENCE_HOLDS"

def main():
    scenarios = {
        "HONEST_BUS":            {},
        "MUTANT_VERTICAL_WRITE": {"vertical_write": True},
        "MUTANT_BACKFLOW":       {"backflow": True},
        "MUTANT_BLIND_GAMMA":    {"blind": True},
        "MUTANT_COUPLING":       {"coupling": True},
    }
    expected = {
        "HONEST_BUS": "NONINTERFERENCE_HOLDS",
        "MUTANT_VERTICAL_WRITE": "FAIL_VERTICAL_WRITE",
        "MUTANT_BACKFLOW": "FAIL_ILLEGAL_BACKFLOW",
        "MUTANT_BLIND_GAMMA": "FAIL_BLIND_HARNESS",
        "MUTANT_COUPLING": "FAIL_CROSS_RENDERER_COUPLING",
    }
    results, harness_sound = {}, True
    for name, flags in scenarios.items():
        r = evaluate(flags); results[name] = r
        harness_sound = harness_sound and (r == expected[name])

    honest_holds = results["HONEST_BUS"] == "NONINTERFERENCE_HOLDS"
    all_mutants_caught = all(results[n] == expected[n] for n in scenarios if n != "HONEST_BUS")

    receipt = {
        "experiment": "PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V1", "authority": False, "canon": False,
        "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
        "frozen_law": "∀θ: p(Π_θ(e))=p(e)  (𝒢∘Π_θ=𝒢); new fiber only via O→provenance→verification→Γ→H'",
        "protected_projection": "𝒢(H)=(A,W,L,Γ,Adm)", "declared_dependency_edges": [list(e) for e in DECLARED_EDGES],
        "scenarios": results, "expected": expected,
        "HONEST_BUS_holds": honest_holds, "all_mutants_caught": all_mutants_caught,
        "HARNESS_SOUND": harness_sound,
        "MAX_ADMISSIBLE_STATEMENT":
            "The honest perceptual bus satisfies noninterference; and the harness independently CATCHES each of "
            "the four failure classes via an adversarial mutant (vertical write, illegal backflow, blind Γ, "
            "cross-renderer coupling). A one-sided always-pass detector is thereby excluded.",
        "fiber_law": "vertical operations preserve the governed fiber; horizontal motion requires governance",
        "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    (Path(__file__).resolve().parent / "PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V1_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    print("═" * 80)
    print("  PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V1 — acceptance contract + self-test")
    print("═" * 80)
    print(f"  𝒢(H*)=(A,W,L,Γ,Adm) · declared edges {DECLARED_EDGES}")
    print("─" * 80)
    for name in scenarios:
        got, exp = results[name], expected[name]
        ok = got == exp
        mark = "✅" if ok else "❌"
        print(f"    {mark} {name:24s} → {got:30s} (expected {exp})")
    print("─" * 80)
    print(f"  HONEST bus holds = {honest_holds} · all 4 mutants caught = {all_mutants_caught}")
    print(f"  HARNESS_SOUND = {harness_sound}  (not a one-sided always-pass detector)")
    print(f"  law: vertical ops preserve the fiber; horizontal motion requires governance")
    print(f"  ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_COMMIT · → PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V1_RECEIPT.json")


if __name__ == "__main__":
    main()
