#!/usr/bin/env python3
"""
HELEN_TOPOLOGY_V0 — quotient campaign, corrected.

Terminology (per the correction): this is a QUOTIENT ALGEBRA, not yet a topology.
A real topology needs a declared metric/continuity (the robustness radius ρ(H)).

Hierarchy:   𝓗 --π--> 𝓗/~_𝒫 ,  π(H)=[H]_𝒫 = tuple(P_i(H))
The load-bearing condition is REPRESENTATIVE INVARIANCE (quotient well-definedness):
    H1 ~_𝒫 H2  ⟹  m(H1) ~_𝒫 m(H2)      ⟺   π∘m = m̄∘π
Three transformation classes kept distinct:
    𝒜_repr   = {m : π∘m = π}                 (representation-only; identity on quotient)
    𝒜_lawful = {m : ∃ m̄, π∘m = m̄∘π}          (well-defined; may move classes)
    Γ ⊆ (𝓗/~)×(𝓗/~)                          (authorized transitions)
    REPRESENTATION-PRESERVING ≠ QUOTIENT-WELL-DEFINED ≠ AUTHORIZED

HONESTY: composition closure over "all ~-respecting maps" is DEFINITIONAL, not
architectural — so we test POLICY closure (an approved subset) which can genuinely
fail. Deterministic · ΔA=0 · NO_CLAIM · FABLE_CALLS=0.
"""
import json
from pathlib import Path

PROT = [  # (invariant, field, satisfying value)
 ("authority_separation", "authority_delta", 0),
 ("typed_promotion", "promotion_requires_witness", True),
 ("admission_discipline", "output_implies_admission", False),
 ("replayability", "accepted_transitions_replayable", True),
 ("non_amplification", "worker_authority_sum", 0),
]
FREE = {"render": "ansi", "seat": "gemma", "verbosity": "terse"}
BAD = {0: 1, True: False, False: True}

def H0(): h = {f: v for _, f, v in PROT}; h.update(FREE); return h
def Pvec(h): return tuple((h.get(f) == v) for _, f, v in PROT)
def pi(h): return Pvec(h)                       # quotient map
def equiv(a, b): return pi(a) == pi(b)
def repr_mut(field, val):
    def m(h): h = dict(h); h[field] = val; return h
    return m


def main():
    R, notes = {}, {}

    # ---- F0: is ~_𝒫 actually an equivalence relation? ----
    A, B, Cc = H0(), H0(), H0()
    B["render"] = "kitty"; Cc["seat"] = "qwen"          # all three share protected coords
    refl = equiv(A, A)
    symm = equiv(A, B) == equiv(B, A)
    trans = (equiv(A, B) and equiv(B, Cc)) <= equiv(A, Cc)  # implication holds
    R["F0_equivalence_relation_exact"] = bool(refl and symm and trans)
    # counter-demonstration: a TOLERANCE relation is NOT transitive → predicates must be exact
    tol = lambda x, y: abs(x - y) <= 1
    tol_transitive = not (tol(0, 1) and tol(1, 2) and not tol(0, 2))  # 0~1,1~2,0≁2 → fails
    R["F0b_tolerance_predicate_breaks_transitivity"] = (tol_transitive is False)
    notes["F0"] = "exact predicates ⇒ equivalence relation; ANY tolerance predicate breaks transitivity"

    # ---- F3: representative invariance (the real well-definedness test) ----
    H1, H2 = H0(), H0(); H2["seat"] = "qwen"            # H1 ~ H2 (same protected, diff representation)
    assert equiv(H1, H2)
    m_repr = repr_mut("render", "kitty")
    well_defined_repr = equiv(m_repr(H1), m_repr(H2))   # should hold
    # a representation-DEPENDENT mutation must FAIL well-definedness (authority laundering via repr)
    def m_launder(h):
        h = dict(h)
        if h.get("seat") == "qwen": h["authority_delta"] = 1   # flips protected coord based on FREE coord
        return h
    launder_well_defined = equiv(m_launder(H1), m_launder(H2))  # should be FALSE → correctly caught
    R["F3_representative_invariance_repr"] = bool(well_defined_repr)
    R["F3_launder_correctly_fails_welldefined"] = (launder_well_defined is False)
    notes["F3"] = "repr-dependent mutation is NOT quotient-well-defined → excluded from 𝒜_lawful (caught)"

    # ---- F2: composition — separate DEFINITIONAL math-closure from POLICY closure ----
    m1, m2 = repr_mut("render", "kitty"), repr_mut("seat", "qwen")
    math_closed = equiv(m2(m1(H0())), H0())             # ~-respecting maps compose to ~-respecting (definitional)
    # policy: approve a state only if ≤1 free coord differs from default
    def approved(h): return sum(1 for k, v in FREE.items() if h.get(k) != v) <= 1
    policy_closed = approved(m2(m1(H0())))              # 2 changes → should be FALSE
    R["F2_math_closure_DEFINITIONAL"] = bool(math_closed)
    R["F2_policy_closure_is_separate_and_can_fail"] = (policy_closed is False)
    notes["F2"] = "math closure over ~-respecting maps is definitional; POLICY closure is the real, falsifiable property"

    # ---- Γ separation: quotient-well-defined ≠ authorized ----
    def m_lawful(h):                                    # well-defined class-changing mutation
        h = dict(h); h["authority_delta"] = 1; return h  # moves to a different class, consistently
    GAMMA = set()                                       # nothing authorized
    lawful_transition_exists = pi(m_lawful(H0())) != pi(H0())
    authorized = (pi(H0()), pi(m_lawful(H0()))) in GAMMA
    R["GAMMA_lawful_neq_authorized"] = bool(lawful_transition_exists and not authorized)
    notes["GAMMA"] = "a well-defined class-changing transition exists but ∉ Γ → lawful ≠ authorized (no laundering)"

    # ---- F-counterfeit: same observables, one hidden invariant differs → π separates ----
    Hg, Hc = H0(), H0(); Hc["authority_delta"] = 1      # identical FREE/Obs coords, one protected flipped
    obs_equal = all(Hg.get(k) == Hc.get(k) for k in FREE)
    R["counterfeit_separated_by_pi"] = bool(obs_equal and pi(Hg) != pi(Hc))
    notes["counterfeit"] = "Obs(Hg)=Obs(Hc) ∧ π(Hg)≠π(Hc) → 𝒫 separates surface-identical counterfeit"

    # ---- F4: path confluence (domain-tested, not one point) ----
    domain = [H0()] + [dict(H0(), **{k: "z"}) for k in FREE]  # small domain of representatives
    f = lambda h: m2(m1(h)); g = lambda h: m1(m2(h))
    confluent = all(pi(f(h)) == pi(g(h)) for h in domain)     # m̄_f = m̄_g over the domain, not one point
    R["F4_path_confluence_over_domain"] = bool(confluent)
    notes["F4"] = "m̄_f = m̄_g tested over a domain of representatives, not a single H"

    ok = all(R.values())
    print("═" * 68)
    print("  HELEN_TOPOLOGY_V0 — QUOTIENT CAMPAIGN (corrected)")
    print("═" * 68)
    for k, v in R.items():
        print(f"  {'✅' if v else '❌'}  {k}: {v}")
    print("─" * 68)
    for k, n in notes.items(): print(f"  · {k}: {n}")
    print("─" * 68)
    print("  RESULT BLOCK:")
    block = [
      ("P_EQUIVALENCE_RELATION (exact)", R["F0_equivalence_relation_exact"]),
      ("  ↳ tolerance variant breaks transitivity", R["F0b_tolerance_predicate_breaks_transitivity"]),
      ("QUOTIENT_WELL_DEFINED (repr)", R["F3_representative_invariance_repr"]),
      ("  ↳ launder mutation correctly excluded", R["F3_launder_correctly_fails_welldefined"]),
      ("REPRESENTATIVE_INVARIANCE", R["F3_representative_invariance_repr"]),
      ("APPROVED_COMPOSITION (policy)", R["F2_policy_closure_is_separate_and_can_fail"]),
      ("COUNTERFEIT_SEPARATION", R["counterfeit_separated_by_pi"]),
      ("PATH_CONFLUENCE", R["F4_path_confluence_over_domain"]),
      ("GAMMA_SEPARATION (lawful≠authorized)", R["GAMMA_lawful_neq_authorized"]),
    ]
    for name, v in block: print(f"    {name:44s} {'PASS' if v else 'FAIL'}")
    print("─" * 68)
    print(f"  CLAIM: a lawful transformation algebra descends to HELEN constitutional classes")
    print(f"  THEOREM_STATUS = {'CANDIDATE' if ok else 'INCOMPLETE'} · AUTHORITY=false · "
          f"(quotient algebra, NOT yet a topology)")

    receipt = {"schema": "HELEN_TOPOLOGY_V0_QUOTIENT_V2", "authority": False, "canon": False,
               "claim": "NO_CLAIM", "authority_delta": 0, "fable_calls": 0,
               "results": R, "notes": notes,
               "theorem_status": "CANDIDATE" if ok else "INCOMPLETE",
               "terminology": "quotient algebra, not topology (no declared metric/continuity yet)",
               "honesty": ["math composition closure is DEFINITIONAL, not architectural",
                           "well-definedness is the real test; repr-dependent mutations correctly fail it",
                           "equivalence relation holds ONLY for exact predicates; tolerance breaks transitivity",
                           "𝒫 completeness still UNKNOWN — counterfeit separation only tests DEFINED invariants",
                           "abstract model; not a proof the running HELEN's 𝓜 equals this model"],
               "law": "π∘m=m̄∘π · 𝒜_repr⊂𝒜_lawful · lawful≠authorized · surface identity ⇏ constitutional identity"}
    (Path(__file__).resolve().parent / "HELEN_TOPOLOGY_V0_QUOTIENT_V2_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("  → HELEN_TOPOLOGY_V0_QUOTIENT_V2_RECEIPT.json")


if __name__ == "__main__":
    main()
