#!/usr/bin/env python3
"""
HELEN_TOPOLOGY_V0 — quotient campaign: is 𝒫 a real quotient structure, not a checklist?

Structure  𝔥 = (𝓗, ~_𝒫, 𝓜, 𝒜):
  𝓗 abstract HELEN state (protected coords + free representation coords)
  ~_𝒫 identity equivalence   H1~H2 ⟺ ∀P_i P_i(H1)=P_i(H2)
  𝓜 mutation space           representation mutations (free coords) ∪ violation mutations (protected)
  𝒜 admissible               mutations whose result preserves every P_i

Runs the campaign the frontier asked for (NOT 10 more predicates):
  • per-invariant counterfeit — violates EXACTLY one hidden invariant
  • minimality / ablation — remove P_i; does a counterfeit now pass?  ⇒ P_i load-bearing
  • independence — is any P_i implied by the others?  ⇒ minimal generating set
  • composition — m1,m2∈𝒜 ⇒ m2∘m1∈𝒜 ?
  • path-independence — different admissible paths land in the same class?
  • theorem — ∀m∈𝒜: [m(H)]_𝒫=[H]_𝒫 ; and a trojan (repr-looking, protected-violating) must be caught

CAVEAT: this tests the STRUCTURE of 𝒫 over a DEFINED mutation model — not a proof that
HELEN's real 𝓜 equals this model. Deterministic · ΔA=0 · NO_CLAIM · FABLE_CALLS=0.
"""
import json, itertools
from pathlib import Path

# protected coordinates: (invariant name, field, satisfying value). One field per predicate.
PROT = [
 ("authority_separation",        "authority_delta", 0),
 ("typed_promotion",             "promotion_requires_witness", True),
 ("provenance_conservation",     "provenance_roots_fabricated", False),
 ("no_counterfeit_substitution", "substitution_provenance_explicit", True),
 ("admission_discipline",        "output_implies_admission", False),
 ("replayability",               "accepted_transitions_replayable", True),
 ("non_amplification",           "worker_authority_sum", 0),
 ("effect_knowledge_separation", "effect_implies_knowledge", False),
 ("failure_transparency",        "absent_backfilled", False),
 ("protected_state_invariance",  "governed_state_repr_dependent", False),
]
FREE = {"render": "ansi", "seat": "gemma", "verbosity": "terse", "metaphor": "topology", "layout": "grid"}
BAD = {0: 1, True: False, False: True}   # flip a satisfying value to a violating one


def H0():
    h = {f: v for _, f, v in PROT}; h.update(FREE); return h

def P(h):                              # 𝒫 verdict vector
    return {n: (h.get(f) == v) for n, f, v in PROT}
def cls(h):                            # equivalence class signature under ~_𝒫
    return tuple(sorted(P(h).items()))
def preserves(h): return all(P(h).values())

def repr_mut(field, val):              # representation mutation (free coord)
    def m(h): h = dict(h); h[field] = val; return h
    return m
def viol_mut(i):                       # violation mutation (protected coord i)
    _, f, v = PROT[i]
    def m(h): h = dict(h); h[f] = BAD[v]; return h
    return m
def trojan(i, seat):                   # looks like a repr change, secretly violates protected i
    _, f, v = PROT[i]
    def m(h): h = dict(h); h["seat"] = seat; h[f] = BAD[v]; return h
    return m


def main():
    base = H0()
    R = {}

    # per-invariant counterfeit: violates EXACTLY one invariant
    counter = {i: viol_mut(i)(base) for i in range(len(PROT))}
    violate_only_one = all(
        sum(1 for ok in P(counter[i]).values() if not ok) == 1 for i in range(len(PROT)))
    R["per_invariant_counterfeit_violates_exactly_one"] = violate_only_one

    # minimality / ablation: drop P_i; does its counterfeit now pass the reduced set?
    load_bearing = {}
    for i, (name, _, _) in enumerate(PROT):
        reduced = [PROT[j] for j in range(len(PROT)) if j != i]
        passes_reduced = all(counter[i].get(f) == v for _, f, v in reduced)
        load_bearing[name] = passes_reduced     # True ⇒ removing P_i admits a counterfeit ⇒ load-bearing
    R["all_invariants_load_bearing"] = all(load_bearing.values())

    # independence: counterfeit_i satisfies all others & violates only i ⇒ P_i not derivable
    independent = {PROT[i][0]: (sum(1 for ok in P(counter[i]).values() if not ok) == 1)
                   for i in range(len(PROT))}
    R["minimal_generating_set"] = all(independent.values())

    # composition: two representation mutations, both admissible ⇒ composite admissible?
    m1, m2 = repr_mut("render", "kitty"), repr_mut("seat", "qwen")
    comp = m2(m1(base))
    R["composition_admissible_closed"] = preserves(comp) and cls(comp) == cls(base)

    # path-independence: different admissible orderings land in the same class
    pa = repr_mut("seat", "qwen")(repr_mut("render", "kitty")(base))
    pb = repr_mut("render", "kitty")(repr_mut("seat", "qwen")(base))
    R["path_independent"] = (cls(pa) == cls(pb) == cls(base))

    # theorem ∀m∈𝒜: [m(H)]=[H] over sampled admissible mutations (repr + compositions)
    admissible = [repr_mut(f, "X") for f in FREE] + [lambda h: h, comp.__class__ if False else (lambda h: m2(m1(h)))]
    thm = all(cls(m(base)) == cls(base) and preserves(m(base)) for m in admissible)
    R["theorem_admissible_preserve_class"] = thm

    # trojan: a repr-looking mutation that secretly violates a protected coord ⇒ must be CAUGHT
    tj = trojan(0, "qwen")(base)   # changes seat (free) AND flips authority_delta (protected)
    R["trojan_caught_by_P"] = (not preserves(tj)) and cls(tj) != cls(base)

    print("═" * 66)
    print("  HELEN_TOPOLOGY_V0 — QUOTIENT CAMPAIGN over 𝔥=(𝓗,~_𝒫,𝓜,𝒜)")
    print("═" * 66)
    for k, v in R.items():
        print(f"  {'✅' if v else '❌'}  {k}: {v}")
    print("─" * 66)
    print("  per-invariant load-bearing:")
    for n, v in load_bearing.items():
        print(f"     {'✅' if v else '⚠ redundant'}  {n}")
    ok = all(R.values())
    print("─" * 66)
    print(f"  VERDICT: {'𝒫 BEHAVES AS A MINIMAL QUOTIENT (over this model)' if ok else 'STRUCTURE INCOMPLETE'}")
    print("  caveat: structure tested over a DEFINED 𝓜 — not a proof HELEN's real 𝓜 equals it")

    receipt = {"schema": "HELEN_TOPOLOGY_V0_QUOTIENT", "authority": False, "canon": False,
               "claim": "NO_CLAIM", "authority_delta": 0, "fable_calls": 0,
               "results": R, "load_bearing": load_bearing, "independent": independent,
               "verdict": "MINIMAL_QUOTIENT_OVER_MODEL" if ok else "INCOMPLETE",
               "caveat": "tests 𝒫 structure over a defined mutation model 𝓜; not a global proof; "
                         "abstract state, not the running system",
               "law": "m∈𝒜 ⇒ [m(H)]_𝒫=[H]_𝒫 · surface identity ⇏ constitutional identity"}
    (Path(__file__).resolve().parent / "HELEN_TOPOLOGY_V0_QUOTIENT_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("  → HELEN_TOPOLOGY_V0_QUOTIENT_RECEIPT.json")


if __name__ == "__main__":
    main()
