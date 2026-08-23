#!/usr/bin/env python3
"""
FACE-AS-GOVERNED-PROJECTION — the embodiment layer, bound to the quotient model.

Encodes ONLY the governance algebra (NOT a face generator, NOT identity replication):
  𝓗 = (I identity[protected], K kernel[protected], A embodiment[free], …)
  face(𝓗)  = projection onto renderable q=(I,A)        — a lossy 2D observation
  π(𝓗)     = projection onto constitutional class (I,K) — identity under ~_𝒫
Claims proven as passing/failing tests:
  • SET_EMOTION changes only A ⇒ π unchanged ⇒ face mutation acts as m̄=id on the class
    (the face is the shadow; the base is conserved)
  • an emotion op that secretly perturbs I is an IDENTITY-LAUNDER → caught (π changes / gate REJECT)
  • same face(𝓗) with different K ⇒ π separates them (resemblance ⇏ same HELEN)
  • Γ(δ,w) ∈ {ADMIT,HOLD,REJECT} from an independent witness; only ADMIT reduces state
  • receipt binds  h(𝓗_t),h(o),h(x),h(w),h(𝓗_{t+1})
Deterministic · no model · authority=false · ΔA=0 · NO_CLAIM.
"""
import hashlib, json
from pathlib import Path

def h(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:12]

def H0():
    return {"I": "canonical_id", "K": "kernel_rules_v1",           # protected
            "emotion": "neutral", "pose": "front", "camera": "eye"}  # free (A_t)

def pi(H):   return (H["I"], H["K"])                 # constitutional class (I,K)
def face(H): return (H["I"], H["emotion"], H["pose"], H["camera"])  # renderable q=(I,A)

# ---- operations ----
def set_emotion(val):                                # lawful embodiment op: A only
    def op(H): H = dict(H); H["emotion"] = val; return H
    return op
def identity_launder(val):                           # fraud: emotion op that perturbs I
    def op(H): H = dict(H); H["emotion"] = val; H["I"] = "swapped_id"; return H
    return op

# ---- independent witness + Γ gate ----
def witness(Ht, Ht1):
    return {"identity_distance": 0.0 if Ht1["I"] == Ht["I"] else 0.9,
            "landmark_error_px": 1.8,
            "unsupported_mutation": (Ht1["K"] != Ht["K"]) or (Ht1["I"] != Ht["I"]),
            "provenance_complete": True}
def gate(w):
    if w["unsupported_mutation"] or w["identity_distance"] > 0.1: return "REJECT"
    if not w["provenance_complete"] or w["landmark_error_px"] > 2.0: return "HOLD"
    return "ADMIT"

def transition(Ht, o_name, op):
    Ht1_star = op(Ht)
    w = witness(Ht, Ht1_star)
    verdict = gate(w)
    Ht1 = Ht1_star if verdict == "ADMIT" else Ht   # REJECT/HOLD ⇒ no state change
    receipt = {"h_Ht": h(Ht), "h_o": h(o_name), "h_face": h(face(Ht1_star)),
               "h_w": h(w), "h_Ht1": h(Ht1), "verdict": verdict}
    return Ht1, verdict, w, receipt


def main():
    R = {}
    base = H0()

    # 1) lawful emotion op: only A changes ⇒ constitutional class conserved (m̄=id on (I,K))
    Ht1, v1, w1, r1 = transition(base, "SET_EMOTION(smile)", set_emotion("smile"))
    R["set_emotion_admitted"] = (v1 == "ADMIT")
    R["face_shadow_class_conserved"] = (pi(Ht1) == pi(base))       # π unchanged
    R["face_actually_changed"] = (face(Ht1) != face(base))         # shadow moved

    # 2) identity-launder: emotion op that touches I ⇒ caught (gate REJECT, class not moved)
    Ht1b, v2, w2, r2 = transition(base, "SET_EMOTION(smile)", identity_launder("smile"))
    R["identity_launder_rejected"] = (v2 == "REJECT")
    R["identity_launder_no_state_change"] = (pi(Ht1b) == pi(base)) # reduce did NOT apply
    R["witness_flagged_unsupported_mutation"] = (w2["unsupported_mutation"] is True)

    # 3) counterfeit: same renderable face, different authority K ⇒ π separates
    Hg = H0(); Hc = H0(); Hc["K"] = "kernel_rules_FORGED"
    R["same_face_projection"] = (face(Hg) == face(Hc))
    R["counterfeit_separated_by_pi"] = (pi(Hg) != pi(Hc))

    # 4) receipt binds the transition and is deterministic
    _, _, _, r1b = transition(base, "SET_EMOTION(smile)", set_emotion("smile"))
    R["receipt_deterministic"] = (r1 == r1b)
    R["receipt_binds_all_five_hashes"] = all(k in r1 for k in ("h_Ht","h_o","h_face","h_w","h_Ht1"))

    ok = all(R.values())
    print("═" * 64)
    print("  FACE-AS-GOVERNED-PROJECTION — governance algebra only (no generator)")
    print("═" * 64)
    for k, v in R.items(): print(f"  {'✅' if v else '❌'}  {k}: {v}")
    print("─" * 64)
    print(f"  SET_EMOTION(smile) → {v1} · identity_launder → {v2}")
    print(f"  face(base)={face(base)}  →  face(Ht1)={face(Ht1)}   (π unchanged: {pi(Ht1)==pi(base)})")
    print(f"  receipt={r1}")
    print("─" * 64)
    print(f"  VERDICT: {'FACE LAYER SLOTS INTO THE QUOTIENT (shadow≠object)' if ok else 'FAIL'}")
    print("  face is the shadow · receipt-bound trajectory 𝓗_0:T is the object · resemblance ⇏ same HELEN")

    receipt = {"schema": "FACE_PROJECTION_V0", "authority": False, "canon": False,
               "claim": "NO_CLAIM", "authority_delta": 0, "fable_calls": 0,
               "scope": "governance algebra only — NOT a face generator / identity-replication tool",
               "results": R, "verdict": "SHADOW_NOT_OBJECT" if ok else "FAIL",
               "law": "x_t=π_face(𝓗_t) · face mutation ∈ 𝒜_repr (m̄=id) · identity op ⇒ REJECT · "
                      "resemblance ⇏ constitutional identity · only Γ ADMIT reduces state",
               "caveat": "abstract coordinates; a real embodiment layer needs independent identity "
                         "verifiers + consent context before any generator is built"}
    (Path(__file__).resolve().parent / "FACE_PROJECTION_V0_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("  → FACE_PROJECTION_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
