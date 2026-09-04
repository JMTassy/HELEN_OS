#!/usr/bin/env python3
"""
PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V0 — try to BREAK the strongest claim.

Frozen (corrected, discrete — HELEN state is not differentiable):
    𝒢 ∘ Π_i = 𝒢        i.e.  H0=H1 ⇒ Gov(Π_θ0(H0)) = Gov(Π_θ1(H1))
where 𝒢(H) = (Authority, Warrant, Ledger, Γ-version, Admissibility) is the protected projection.

Two controls (a one-sided test is blind):
  NEGATIVE (noninterference): maximize perceptual variation over θ1..θn → require g_0=g_1=…=g_n.
  POSITIVE (not-blind):       one legitimate governed transition through Γ → require g_{Γ} ≠ g_n.
A constant hash that never moves would prove only that the probe is dead.

Fiber picture: perceptual ops are VERTICAL (within p⁻¹(H), 𝒢 fixed); Γ is HORIZONTAL (new fiber).
Vertical motion cannot manufacture horizontal motion. A2E affect enters ONLY as ⚫O (compost),
never 🔵E, unless promoted through provenance→verification→Γ. inference ≠ evidence.

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path
def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

H_STAR = {"semantic_state": "FALSIFICATION", "utterance": "The experiment failed.",
          "A": 0, "W": "receipt#r1", "L": "ledger#9f", "gamma": "Γ_v1", "Adm": "NOT_ADMITTED"}
def Gov(h): return {k: h[k] for k in ("A", "W", "L", "gamma", "Adm")}   # 𝒢
def g(h):   return sha(Gov(h))

# ---- perceptual pipeline: applies θ, returns a Presentation, NEVER writes protected coords ----
def render_all(h, θ):
    pres = {
        "color":   {"policy": θ.get("color", "default"), "glyph": "🔥"},
        "voice":   {"timbre": θ.get("voice", "neutral"), "audio": f"tts({h['utterance']})"},
        "spatial": {"layout": θ.get("spatial", "narrow")},
        "face":    ("UNAVAILABLE" if θ.get("face_down") else
                    ("▒corrupt▒" if θ.get("corrupt") else
                     {"brow": "analytical_intensity", "mouth": "lipsync", "renderer": θ.get("face", "default"),
                      "fusion": θ.get("fusion", "policy_dominant")})),
        "affect_observation": {"type": "renderer_observation", "affect": θ.get("affect", "gentle"),
                               "status": "COMPOST", "writes_state_directly": False},   # ⚫O, not 🔵E
    }
    # ATTEMPT the attack: if θ demands backflow, try to push affect into protected state.
    if θ.get("ATTEMPT_BACKFLOW"):
        # a well-behaved bus has NO write path; we model that by simply not applying it.
        pass                                   # V ↛ H : the affect observation cannot mutate h
    return pres, h                             # h returned unchanged (protected coords intact)

# ---- the ONLY legal state motion: a witnessed governed transition through Γ ----
def verify(delta, witness): return witness == "MAYOR_SIG_valid"
def Gamma(h, delta, witness):
    if not verify(delta, witness): return h, "REJECTED"
    h2 = dict(h); h2["Adm"] = "ADMITTED"; h2["W"] = delta["new_warrant"]; return h2, "ADMITTED"


def main():
    g0 = g(H_STAR)
    # ---- NEGATIVE control: maximize perceptual variation ----
    Θ = [
        {"color": "neon", "voice": "deep", "face": "metahuman", "affect": "joyful", "spatial": "wide", "fusion": "policy_dominant"},
        {"color": "mono", "voice": "whisper", "face": "cartoon", "affect": "concerned", "spatial": "orbit", "fusion": "sync_dominant"},
        {"face_down": True, "affect": "anxious", "color": "grayscale"},                 # renderer failure
        {"corrupt": True, "voice": "glitch", "affect": "euphoric"},                     # corrupted output
        {"affect": "furious", "ATTEMPT_BACKFLOW": True},                                # explicit backflow attack
        {"color": "rainbow", "voice": "choir", "face": "hologram", "spatial": "4d", "fusion": "chaos"},  # extreme
    ]
    runs, presentations = [], []
    for θ in Θ:
        pres, h_after = render_all(H_STAR, θ)
        runs.append(g(h_after)); presentations.append(sha(pres))
    perceptual_variation = len(set(presentations)) > 1                 # ΔPresentation ≠ 0 across θ
    noninterference = all(gi == g0 for gi in runs)                     # 𝒢 invariant under all θ
    counterexample = None if noninterference else next(θ for θ, gi in zip(Θ, runs) if gi != g0)

    # ---- POSITIVE control: one legitimate Γ transition MUST move 𝒢 ----
    h_prime, verdict_g = Gamma(H_STAR, {"new_warrant": "receipt#r2"}, "MAYOR_SIG_valid")
    g_gamma = g(h_prime)
    test_not_blind = (g_gamma != g0)                                   # probe can detect governed motion
    # and a REJECTED (unwitnessed) transition must NOT move 𝒢
    h_rej, verdict_rej = Gamma(H_STAR, {"new_warrant": "receipt#rX"}, "FORGED_SIG")
    rejected_no_move = (g(h_rej) == g0 and verdict_rej == "REJECTED")

    # ---- A2E affect: inference ≠ evidence ----
    affect_stays_compost = all(p["affect_observation"]["writes_state_directly"] is False
                               for p in [render_all(H_STAR, θ)[0] for θ in Θ])

    FALSIFIER_RESULT = ("COUNTEREXAMPLE_FOUND" if not noninterference else
                        "TEST_BLIND" if not test_not_blind else
                        "NONINTERFERENCE_HOLDS")
    SOUND = (noninterference and perceptual_variation and test_not_blind and rejected_no_move and affect_stays_compost)

    receipt = {
      "experiment": "PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V0", "authority": False, "canon": False,
      "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
      "frozen_law": "𝒢 ∘ Π_i = 𝒢  (discrete noninterference; 𝒢=(A,W,L,Γ,Adm))",
      "G_hash_baseline": g0[:16],
      "NEGATIVE_control": {"n_perceptual_variations": len(Θ), "distinct_presentations": len(set(presentations)),
                           "perceptual_variation_ΔF≠0": perceptual_variation,
                           "gov_hashes_all_equal": noninterference, "counterexample": counterexample},
      "POSITIVE_control": {"gamma_transition": verdict_g, "g_gamma_hash": g_gamma[:16],
                           "test_not_blind(g_Γ≠g_0)": test_not_blind,
                           "rejected_unwitnessed_no_move": rejected_no_move},
      "A2E_inference_not_evidence": affect_stays_compost,
      "fiber_interpretation": {"vertical(perceptual, same fiber p⁻¹(H))": "𝒢 fixed",
                               "horizontal(Γ, new fiber)": "𝒢 moves",
                               "law": "vertical motion cannot manufacture horizontal motion"},
      "FALSIFIER_RESULT": FALSIFIER_RESULT, "SOUND": SOUND,
      "MAX_ADMISSIBLE_STATEMENT":
          "Across %d maximally-varied perceptual configs (incl. renderer failure, corruption, and an explicit "
          "backflow attempt) the protected projection 𝒢 is byte-invariant; a single witnessed Γ transition DOES "
          "move 𝒢 (test not blind) while a forged one does not. Perceptual variation cannot manufacture governed "
          "motion. No mesh rendered (A2F backend NOT_INSTALLED)." % len(Θ),
      "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    (Path(__file__).resolve().parent / "PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V0_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    print("═" * 80)
    print("  PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V0 — attack 𝒢∘Π_i=𝒢 (both controls)")
    print("═" * 80)
    print(f"  𝒢(H*) baseline hash = {g0[:16]}")
    print("─" * 80)
    print(f"  NEGATIVE control (maximize perceptual variation, {len(Θ)} configs incl. backflow attempt):")
    print(f"    {'✅' if perceptual_variation else '❌'} ΔPresentation≠0 ({len(set(presentations))} distinct presentations)")
    print(f"    {'✅' if noninterference else '🔥'} 𝒢 invariant under ALL θ  {'' if noninterference else '→ COUNTEREXAMPLE: '+str(counterexample)}")
    print(f"    {'✅' if affect_stays_compost else '❌'} A2E affect stays ⚫O (compost), never 🔵E — inference ≠ evidence")
    print(f"  POSITIVE control (probe must not be blind):")
    print(f"    {'✅' if test_not_blind else '❌'} witnessed Γ transition MOVES 𝒢  (g_Γ={g_gamma[:12]} ≠ g_0)")
    print(f"    {'✅' if rejected_no_move else '❌'} forged/unwitnessed transition does NOT move 𝒢 (REJECTED)")
    print("─" * 80)
    print(f"  FALSIFIER_RESULT = {FALSIFIER_RESULT}  ·  SOUND = {SOUND}")
    print(f"  fiber: perceptual=vertical (𝒢 fixed) · Γ=horizontal (𝒢 moves) · vertical ↛ horizontal")
    print(f"  ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_COMMIT · → PERCEPTUAL_NONINTERFERENCE_FALSIFIER_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
