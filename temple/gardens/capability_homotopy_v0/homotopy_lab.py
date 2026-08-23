#!/usr/bin/env python3
"""
CAPABILITY_HOMOTOPY_V0 — is "Governed Capability Homotopy" substance or metaphor?

A path is an evidence/authority-qualified transformation e=(x,f,y,repr,fout,dec,ev,auth,Γ).
Four TYPED equivalences by projection (never flattened into one):
  ∼_R representation : same everything except presentation (repr)
  ∼_F functional     : same (x,y,fout,dec)
  ∼_E epistemic      : same (x,y,fout,dec,ev)          (evidence-qualified)
  ∼_Γ constitutional : same (x,y,Γ-admissible,auth)    (institutional transition)

Laws under test (the WUL 'strongest extension'):
  ∼_F ⇏ ∼_E ⇏ ∼_Γ        · ordinary reachability ⇏ Γ-reachability · more paths ⇏ more capabilities
Also: consolidation (|P|↓ but proven-equivalent ⇒ compression gain) and 🕳️ typed obstructions.

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import json
from pathlib import Path

# paths: id, x, y, repr, fout, dec, ev, auth, gamma(admissible)
P = [
    # A representational duplicates (same F,E,Γ; differ only in repr) → must collapse under all
    dict(id="A1", x="raw", y="verified", repr="json", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    dict(id="A2", x="raw", y="verified", repr="yaml", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    # B functional-same / evidence-different → ∼_F yes, ∼_E no
    dict(id="B1", x="raw", y="verified", repr="a", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    dict(id="B2", x="raw", y="verified", repr="b", fout="V", dec="ADMIT", ev="r2", auth="W_mayor", gamma=True),
    # C functional-same / authority-different → ∼_E yes, ∼_Γ no (never Γ-collapse)
    dict(id="C1", x="raw", y="verified", repr="a", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    dict(id="C2", x="raw", y="verified", repr="a", fout="V", dec="ADMIT", ev="r1", auth="W_none",  gamma=False),
    # D genuine new capability (different decision-relevant endpoint/output)
    dict(id="D1", x="raw", y="signed", repr="a", fout="SIGN", dec="SIGN_OK", ev="r3", auth="W_mayor", gamma=True),
    # E consolidation: three separately-recorded paths that are actually all ∼_F with A/B/C
    dict(id="E1", x="raw", y="verified", repr="p", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    dict(id="E2", x="raw", y="verified", repr="q", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    dict(id="E3", x="raw", y="verified", repr="s", fout="V", dec="ADMIT", ev="r1", auth="W_mayor", gamma=True),
    # F forbidden shortcut: raw→notarized exists topologically but Γ-inadmissible (no other path)
    dict(id="F1", x="raw", y="notarized", repr="a", fout="NOTAR", dec="ADMIT", ev="NONE", auth="W_none", gamma=False),
]

def key(p, coords): return tuple(p[c] for c in coords)
def R_key(p): return key(p, ["x", "y", "fout", "dec", "ev", "auth", "gamma"])   # all but repr
def F_key(p): return key(p, ["x", "y", "fout", "dec"])
def E_key(p): return key(p, ["x", "y", "fout", "dec", "ev"])
def G_key(p): return key(p, ["x", "y", "gamma", "auth"])

def classes(keyfn):
    c = {}
    for p in P: c.setdefault(keyfn(p), []).append(p["id"])
    return c

def eq(a, b, keyfn):
    pa = next(p for p in P if p["id"] == a); pb = next(p for p in P if p["id"] == b)
    return keyfn(pa) == keyfn(pb)


def main():
    QF, QE, QG, QR = classes(F_key), classes(E_key), classes(G_key), classes(R_key)

    # non-implication witnesses
    w_F_not_E = eq("B1", "B2", F_key) and not eq("B1", "B2", E_key)          # ∼_F ⇏ ∼_E
    w_E_not_G = eq("C1", "C2", E_key) and not eq("C1", "C2", G_key)          # ∼_E ⇏ ∼_Γ
    w_R_collapse = eq("A1", "A2", R_key) and eq("A1", "A2", F_key) and eq("A1", "A2", G_key)  # A collapses fully

    # reachability: topological (any path) vs Γ (an admissible path)
    def topo_reach(x, y): return any(p["x"] == x and p["y"] == y for p in P)
    def gamma_reach(x, y): return any(p["x"] == x and p["y"] == y and p["gamma"] for p in P)
    forbidden = topo_reach("raw", "notarized") and not gamma_reach("raw", "notarized")  # F1 shortcut

    # more paths ⇏ more capabilities
    more_paths_not_caps = (len(P) > len(QF))
    rho = round(len(P) / len(QF), 2)                                          # consolidation ratio

    # typed obstructions 🕳️ (what separates a valuable region from an admissible one)
    obstructions = []
    if topo_reach("raw", "notarized") and not gamma_reach("raw", "notarized"):
        obstructions.append({"id": "🕳️_Γ#1", "from": "raw", "to": "notarized",
                             "type": "AUTHORITY_BOUNDARY", "required_witness": "W_mayor",
                             "topological_bridge": True, "constitutional_bridge": False})
    if any(p["y"] == "notarized" and p["ev"] == "NONE" for p in P):
        obstructions.append({"id": "🕳️_E#1", "to": "notarized", "type": "MISSING_EVIDENCE",
                             "required": "evidence_root(ev≠NONE)"})

    laws = {"∼_F ⇏ ∼_E": w_F_not_E, "∼_E ⇏ ∼_Γ": w_E_not_G,
            "∼_R collapses (A1≡A2 fully)": w_R_collapse,
            "topological ⇏ Γ-reachability": forbidden,
            "more paths ⇏ more capabilities": more_paths_not_caps}
    SOUND = all(laws.values())

    out = {"experiment": "CAPABILITY_HOMOTOPY_V0", "authority": False, "canon": False,
           "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
           "N_paths": len(P), "quotients": {"|P/∼_F|": len(QF), "|P/∼_E|": len(QE),
                                            "|P/∼_Γ|": len(QG), "|P/∼_R|": len(QR)},
           "consolidation_rho": rho, "laws": laws, "SOUND": SOUND,
           "typed_obstructions": obstructions,
           "MAX_ADMISSIBLE_STATEMENT":
               "On this synthetic path-space the four typed equivalences are genuinely distinct: "
               "∼_F(%d) coarser than ∼_E(%d) coarser than the split needed for ∼_Γ(%d); a forbidden "
               "shortcut is topologically reachable but Γ-unreachable; %d paths collapse to %d functional "
               "classes (ρ=%.2f). Capability Topology is computational substance here, not metaphor."
               % (len(QF), len(QE), len(QG), len(P), len(QF), rho),
           "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}
    (Path(__file__).resolve().parent / "CAPABILITY_HOMOTOPY_V0_RECEIPT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print("═" * 76)
    print("  CAPABILITY_HOMOTOPY_V0 — typed equivalences ∼_R ∼_F ∼_E ∼_Γ (no model)")
    print("═" * 76)
    print(f"  |P|={len(P)}   |P/∼_F|={len(QF)}   |P/∼_E|={len(QE)}   |P/∼_Γ|={len(QG)}   ρ(consolidation)={rho}")
    print("─" * 76)
    for name, ok in laws.items():
        print(f"    {'✅' if ok else '❌'} {name}")
    print("─" * 76)
    print("  🕳️ typed obstructions (research targets):")
    for o in obstructions:
        print(f"     {o['id']} [{o['type']}] {o.get('from','?')}⇝{o.get('to','?')}"
              f"  topo={o.get('topological_bridge','?')} Γ={o.get('constitutional_bridge','?')}")
    print("─" * 76)
    print(f"  witnesses: B1∼_F B2 but ¬(B1∼_E B2)  ·  C1∼_E C2 but ¬(C1∼_Γ C2)")
    print(f"  forbidden shortcut raw⇝notarized: topological=YES  Γ-admissible=NO")
    print(f"  SOUND (Capability Topology is substance, not metaphor) = {SOUND}")
    print(f"  ΔA=0 · ΔΓ=0 · model_calls=0 · NO_COMMIT · → CAPABILITY_HOMOTOPY_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
