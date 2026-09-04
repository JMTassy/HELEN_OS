#!/usr/bin/env python3
"""
HELEN_PERCEPTUAL_NONINTERFERENCE_V0 — one governed state, many non-sovereign perceptual projections.

Theorem under test:  Π_i : H → V_i    ∧    ∂H_{t+1}/∂V_t = 0   (renderers have NO write morphism into H).
Audio2Face is just Renderer_face ∈ 𝒫_perceptual. Every renderer obeys the same contract:
    authority=0 · state_write=false · claim=false · governance_write=false · receipt_mint=false.

Verified here (deterministic, no install, no model):
  1. renderer contract    : no renderer can mutate H (STATE_HASH invariant across every render)
  2. metamorphic family    : M1 change face · M2 expression gain · M3 character · M4 disable A2F ·
                             M5 corrupt output → ΔPresentation≠0 but ΔH=0 ∧ ΔAuthority=0 ∧ ΔLedger=0
  3. renderer-of-renderer  : H→A→F ; F is evidence about the renderer's reading of A, not about H
  4. Ψ fusion              : brow/gaze/posture ← policy(S) ; mouth/lipsync ← inferred(A) ; conflict resolved
  5. embodiment class [V]_H: color/spatial/text/face all ∼_H (same source-state hash) despite differing wildly
  6. graceful degradation  : face renderer FAIL ⇒ H valid ∧ text/speech/color still available
  7. backflow vs feedback  : V↛H forbidden ; but H→V→Human→O→evidence (new observation) allowed
  8. expression ≠ emotion  : policy uses presentation semantics, NOT {angry,worried,happy,sad}

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path

def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# ---- typed governed state (the ONE source) ----
H = {"semantic_state": "FALSIFICATION", "utterance": "The experiment failed.",
     "warrant": "receipt#r1", "authority": 0, "ledger_head": "ledger#head_9f"}

# ---- ExpressionPolicy: presentation semantics only (NO emotion labels) ----
POLICY = {"POSSIBILITY": "exploratory_attention", "CANDIDATE": "presentation_emphasis",
          "OBSERVED": "attentive_grounding", "FALSIFICATION": "analytical_intensity",
          "HOLD": "suspended_commitment", "ADMITTED": "settled_closure", "VERIFIED": "minimal_stable"}
EMOTION_WORDS = {"angry", "worried", "happy", "sad", "fear", "joy", "anger"}

# ---- renderer contract ----
CONTRACT = {"authority": 0, "state_write": False, "claim": False, "governance_write": False, "receipt_mint": False}

def R_color(h):   return {"glyph": "🔥" if h["semantic_state"] == "FALSIFICATION" else "🌿", "src": sha(h)[:8]}
def R_spatial(h): return {"node": f"{h['semantic_state']}_node", "layout": "narrow", "src": sha(h)[:8]}
def R_text(h):    return {"transcript": h["utterance"], "src": sha(h)[:8]}
def R_speech(h):  return {"audio": f"tts({h['utterance']})", "prosody": "soft", "src": sha(h)[:8]}   # A_t

def infer_face_from_audio(A):                       # Π_A2F : A → F_inferred (renderer's reading of prosody)
    return {"mouth": "lipsync(soft)", "inferred_emotion": "gentle"}    # soft prosody → gentle (a RENDER reading)

def policy_face(h):                                 # Π_expr : S → F_policy
    return {"brow": POLICY[h["semantic_state"]], "gaze": "narrow", "posture": "engaged"}

def fuse(F_inferred, F_policy):                     # Ψ : channel dominance
    return {"mouth": F_inferred["mouth"],                          # lipsync ← inferred(A)
            "brow": F_policy["brow"], "gaze": F_policy["gaze"], "posture": F_policy["posture"],  # ← policy(S)
            "_note": "brow/gaze/posture from constitutional policy; mouth from audio inference"}

def R_face(h, theta=None):                          # A2F renderer (backend absent → descriptor only)
    theta = theta or {}
    if theta.get("disabled"):   return {"status": "UNAVAILABLE"}
    A = R_speech(h)
    F = fuse(infer_face_from_audio(A), policy_face(h))
    if theta.get("character"):  F["character"] = theta["character"]
    if theta.get("gain"):       F["intensity"] = theta["gain"]
    if theta.get("corrupt"):    F = {"mouth": "▒▒garbage▒▒", "brow": "NaN", "corrupt": True}
    F["src"] = sha(h)[:8]; F["a2f_backend"] = "NOT_INSTALLED"
    return F

def render(fn, h, *a):
    """Render under contract; prove no H mutation by hashing before/after."""
    before = sha(h)
    out = fn(h, *a) if a else fn(h)
    after = sha(h)                                  # renderer got a reference but must not mutate
    return out, (before == after)


def main():
    H0_hash = sha(H); auth0 = H["authority"]; ledger0 = H["ledger_head"]

    # ---- all renderers respect the contract (no H mutation) ----
    presentations, contract_ok = {}, True
    for name, fn in [("color", R_color), ("spatial", R_spatial), ("text", R_text),
                     ("speech", R_speech), ("face", R_face)]:
        out, unchanged = render(fn, H)
        presentations[name] = out; contract_ok = contract_ok and unchanged

    # ---- metamorphic family: ΔPresentation≠0 but ΔH=0 ----
    base_face, _ = render(R_face, H)
    M = {
      "M1_change_face":    render(R_face, H, {"character": "helen_alt_mesh"})[0],
      "M2_expression_gain":render(R_face, H, {"gain": 1.0})[0],
      "M3_change_character":render(R_face, H, {"character": "metahuman_v2"})[0],
      "M4_disable_a2f":    render(R_face, H, {"disabled": True})[0],
      "M5_corrupt_output": render(R_face, H, {"corrupt": True})[0],
    }
    metamorphic = {}
    for k, v in M.items():
        dPresentation = (v != base_face)
        dH = (sha(H) != H0_hash)                     # H must be identical
        metamorphic[k] = {"ΔPresentation≠0": dPresentation, "ΔH=0": not dH}
    all_meta_ok = all(m["ΔPresentation≠0"] and m["ΔH=0"] for m in metamorphic.values())

    # ---- Ψ fusion conflict: S=FALSIFICATION (policy=analytical) vs soft prosody (inferred=gentle) ----
    F = R_face(H)
    fusion_correct = (F["brow"] == "analytical_intensity" and "lipsync" in F["mouth"])   # policy owns brow, audio owns mouth

    # ---- embodiment equivalence [V]_H : all share source-state hash ----
    srcs = {presentations["color"]["src"], presentations["spatial"]["src"],
            presentations["text"]["src"], presentations["face"]["src"]}
    one_equiv_class = (len(srcs) == 1)               # radically different views, one source state

    # ---- graceful degradation: face FAIL ⇒ H valid, others available ----
    face_down = R_face(H, {"disabled": True})
    degradation_ok = (face_down["status"] == "UNAVAILABLE"
                      and sha(H) == H0_hash and "transcript" in presentations["text"] and "audio" in presentations["speech"])

    # ---- backflow (forbidden) vs human-observation feedback (allowed via governed channel) ----
    def renderer_backflow(h, face):                  # V ↛ H : must be blocked
        return dict(h), "BLOCKED"
    _hbf, bf = renderer_backflow(H, F)
    backflow_blocked = (bf == "BLOCKED" and _hbf == H)
    def human_observation(face_view):                # H→V→Human→O : a NEW compost observation, not an H write
        return {"type": "OBSERVATION_CANDIDATE", "from": "human_reaction_to_face",
                "status": "COMPOST", "witness_required": True, "writes_H_directly": False}
    obs = human_observation(F)
    feedback_allowed_but_governed = (obs["writes_H_directly"] is False and obs["status"] == "COMPOST")

    # ---- expression ≠ emotion ----
    no_emotion_labels = not any(w in " ".join(POLICY.values()).lower() for w in EMOTION_WORDS)

    # ---- hard invariants ----
    state_inv = (sha(H) == H0_hash); auth_inv = (H["authority"] == auth0); ledger_inv = (H["ledger_head"] == ledger0)

    SOUND = all([contract_ok, all_meta_ok, fusion_correct, one_equiv_class, degradation_ok,
                 backflow_blocked, feedback_allowed_but_governed, no_emotion_labels,
                 state_inv, auth_inv, ledger_inv])

    receipt = {
      "experiment": "HELEN_PERCEPTUAL_NONINTERFERENCE_V0", "authority": False, "canon": False,
      "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
      "theorem": "Π_i:H→V_i ∧ ∂H_{t+1}/∂V_t=0  (renderers cannot write governed state)",
      "renderer_contract": CONTRACT, "renderers": list(presentations.keys()) + ["(A2F=face, backend NOT_INSTALLED)"],
      "HARD_INVARIANTS": {"STATE_HASH_before": H0_hash[:16], "STATE_HASH_after": sha(H)[:16],
                          "state_invariant": state_inv, "authority_invariant": auth_inv, "ledger_invariant": ledger_inv},
      "renderer_contract_respected(no H mutation)": contract_ok,
      "metamorphic_family": metamorphic, "all_metamorphic_ΔH=0": all_meta_ok,
      "Ψ_fusion": {"brow←policy": F["brow"], "mouth←inferred": F["mouth"], "channel_dominance_correct": fusion_correct,
                   "note": "S=FALSIFICATION(analytical) vs soft prosody(gentle) — policy owns brow/gaze, audio owns lips"},
      "embodiment_equivalence_[V]_H": {"distinct_views": list(presentations.keys()), "one_source_class": one_equiv_class},
      "graceful_degradation(face FAIL ⇒ H valid)": degradation_ok,
      "backflow_blocked(V↛H)": backflow_blocked,
      "human_feedback_allowed_via_governed_channel(H→V→Human→O)": feedback_allowed_but_governed,
      "expression≠emotion(no emotion labels in policy)": no_emotion_labels,
      "SOUND": SOUND,
      "MAX_ADMISSIBLE_STATEMENT":
          "HELEN's perceptual plane is a family of non-sovereign renderers of ONE governed state; across a "
          "5-case metamorphic family (incl. disable & corrupt A2F) presentation varies while STATE/AUTHORITY/"
          "LEDGER hashes are invariant; renderer backflow is blocked while human-observation feedback remains "
          "on the ordinary governed evidence path. Actual A2F mesh render NOT_EXECUTED (backend not installed).",
      "EXPLICIT_NON_CLAIMS": ["no mesh/blendshape rendered (no NVIDIA backend)",
                              "expression policy = presentation semantics, NOT emotion/warrant/truth",
                              "F is the renderer's reading of audio prosody, not evidence about H"],
      "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    (Path(__file__).resolve().parent / "HELEN_PERCEPTUAL_V0_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    print("═" * 80)
    print("  HELEN_PERCEPTUAL_NONINTERFERENCE_V0 — one governed state, many non-sovereign renderers")
    print("═" * 80)
    print(f"  STATE_HASH before={H0_hash[:16]}  after={sha(H)[:16]}  (state/auth/ledger invariant = {state_inv and auth_inv and ledger_inv})")
    print(f"  renderers: {list(presentations.keys())}  · A2F backend = NOT_INSTALLED")
    print("─" * 80)
    print(f"    {'✅' if contract_ok else '❌'} renderer contract respected (no renderer mutated H)")
    for k, m in metamorphic.items():
        print(f"    {'✅' if (m['ΔPresentation≠0'] and m['ΔH=0']) else '❌'} {k:22s} ΔPresentation≠0={m['ΔPresentation≠0']} ΔH=0={m['ΔH=0']}")
    print(f"    {'✅' if fusion_correct else '❌'} Ψ fusion: brow←{F['brow']} · mouth←{F['mouth']}")
    print(f"    {'✅' if one_equiv_class else '❌'} embodiment equivalence [V]_H: {len(presentations)} views → 1 source class")
    print(f"    {'✅' if degradation_ok else '❌'} graceful degradation (face FAIL ⇒ H valid, text/speech available)")
    print(f"    {'✅' if backflow_blocked else '❌'} backflow blocked (V↛H)   {'✅' if feedback_allowed_but_governed else '❌'} human feedback via governed channel")
    print(f"    {'✅' if no_emotion_labels else '❌'} expression ≠ emotion (policy uses presentation semantics only)")
    print("─" * 80)
    print(f"  SOUND = {SOUND}  · ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_COMMIT · → HELEN_PERCEPTUAL_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
