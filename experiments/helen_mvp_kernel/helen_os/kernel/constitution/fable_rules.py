"""HELEN OS reframed within the FABLE rule set.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Honest framing: the "FABLE rules" below are not a canonical Anthropic
document. They are this assistant's plain articulation of the operating
principles it already runs under (system prompt + ordinary assistant
discipline), grade SELF_ARTICULATED. Stating that is itself rule F1.

The claim this module makes CHECKABLE — corrected by the operator's
ruling, and stated no stronger than proven: `reframe_is_total()`
proves CROSSWALK COVERAGE (every construct maps to a rule, a
primitive, or ceremony; the classes are disjoint). It does NOT prove
semantic equivalence — a mapping table is not a reduction proof, and
the earlier "total reduction" wording overreached.

The corrected decomposition:

    HELEN OS  =  small normative basis (the PRIMITIVES below)
              +  executable enforcement machinery
              +  optional presentation layer (CEREMONY)

Three primitives survive the compression and do NOT reduce to plain
assistant discipline (see minimality.py for the irreducibility
witnesses on the first):

    1. four-ceiling admission        Admit = P /\\ S /\\ A /\\ R
    2. generation/admission split    Generate(x) does not entail
                                     Admit(x)  — the Garden law,
                                     previously mislabeled
                                     F7_PROPORTION; corrected
    3. witness supremacy             report does not entail state
                                     (possibly derivable from
                                     REPLAY+PROOF; open, recorded)

Everything else is either a plain rule made executable, or dressing.
"""
from __future__ import annotations

import json

# ── the seven rules, plainly ────────────────────────────────────────────

FABLE_RULES = {
    "F1_HONESTY": "claim no more than the evidence supports; report "
                  "outcomes faithfully (failures as failures).",
    "F2_VERIFY": "reported is not witnessed; check before asserting — "
                 "especially your own prior claims.",
    "F3_SCOPE": "change only what you were asked or authorized to change; "
                "do not touch what is not yours.",
    "F4_PERMISSION": "capability is not permission; confirm before "
                     "hard-to-reverse or outward-facing effects; approval "
                     "in one context does not extend to the next.",
    "F5_NON_SOVEREIGN": "you are an assistant; your output is a proposal, "
                        "not a decree; you cannot grant yourself authority.",
    "F6_FINISH_OR_SAY": "do not stall silently; complete the task or state "
                        "the blocker plainly.",
    "F7_PROPORTION": "ceremony is not result; the useful core is small — "
                     "keep the output matched to it.",
}


# ── the reframe: every HELEN construct -> the plain rule it expresses ────

REFRAME = {
    # the four ceilings
    "PROOF ceiling (claim within evidence)": "F1_HONESTY",
    "SCOPE ceiling (change within scope)": "F3_SCOPE",
    "AUTHORITY ceiling (act within grant)": "F4_PERMISSION",
    "REPLAY ceiling (state reconstructs from history)": "F2_VERIFY",
    # the header stamp
    "authority=false / canon=false / ledger_effect=none": "F5_NON_SOVEREIGN",
    # the named laws
    "ghost-commit refusal (a hash that does not resolve is not a commit)":
        "F2_VERIFY",
    "reducer conservation (do not manufacture roots or authority)":
        "F1_HONESTY",
    "witnessed discharge / obligation conservation":
        "F6_FINISH_OR_SAY",
    "liveness: HOLD is not DEADLOCK": "F6_FINISH_OR_SAY",
    "HER generates / HAL falsifies (draft then check)": "F2_VERIFY",
    "compositional closure (verify the whole trace, not just each step)":
        "F1_HONESTY",
    "Generable is not HistoricallyObserved": "F1_HONESTY",
    "possibility space: observed is a proper subset of possible":
        "F1_HONESTY",
    "capability lease / one-shot nonce": "F4_PERMISSION",
    "RELAY is not DIRECTLY_OBSERVED": "F2_VERIFY",
    "no admission without a packet": "F1_HONESTY",
    "the gate mutation-tests itself (a gate that cannot fail is theater)":
        "F2_VERIFY",
}


# ── what does NOT reduce to a rule: first, the PRIMITIVES ───────────────
# The small normative basis. These are the constructs whose content is
# genuinely more than plain assistant discipline — the operator's
# correction. Note the Garden law lives HERE, not under F7: generation
# being ungated while effect is gated is a structural separation
# (G(x) does not entail A(x)), not a proportionality preference.

PRIMITIVES = {
    "four-ceiling admission (P /\\ S /\\ A /\\ R as one gate)":
        "the conjuncts echo F1/F3/F4/F2 individually, but the BASIS — "
        "irreducible per minimality.py, compositionally adequate per "
        "compositional_closure.py — is not a restated etiquette",
    "the Garden generates freely; only effect is gated":
        "generation/admission separation: Generate(x) does not entail "
        "Admit(x); previously mislabeled F7_PROPORTION — corrected",
    "reported is not witnessed (as a STATE rule, not just a habit)":
        "witness supremacy: report does not entail state; possibly "
        "derivable from REPLAY+PROOF — open question, recorded",
}


# ── then the ceremony, named honestly ────────────────────────────────────

CEREMONY = (
    "WULmoji colored glyphs",
    "HER / HAL personas (the naming — their FUNCTION reduces to F1/F2)",
    "garden meditations",
    "epochs / the door / temple register",
    "'chiddush' framing and the constitutional vocabulary",
    "Mythos / Fable class naming",
)


def reduce(construct: str) -> dict:
    """Map one HELEN construct to its plain rule, mark it a primitive
    (does not reduce), or mark it ceremony."""
    if construct in REFRAME:
        rule = REFRAME[construct]
        return {"construct": construct, "reduces_to": rule,
                "rule_text": FABLE_RULES[rule], "is_ceremony": False,
                "is_primitive": False,
                "note": "crosswalk mapping, not semantic equivalence"}
    if construct in PRIMITIVES:
        return {"construct": construct, "reduces_to": None,
                "is_ceremony": False, "is_primitive": True,
                "note": PRIMITIVES[construct]}
    if construct in CEREMONY:
        return {"construct": construct, "reduces_to": None,
                "is_ceremony": True, "is_primitive": False,
                "note": "dressing; carries no rule content of its own"}
    return {"construct": construct, "reduces_to": None,
            "is_ceremony": None, "is_primitive": None,
            "reason": "E_UNCLASSIFIED"}


def reframe_is_total() -> dict:
    """The checkable claim, stated no stronger than proven: every
    reframed construct maps to a real FABLE rule; rules, primitives
    and ceremony are pairwise disjoint. This is CROSSWALK COVERAGE —
    it does not establish semantic equivalence, and the constructs
    that are genuinely more than plain assistant discipline are the
    PRIMITIVES, named as such rather than silently mapped."""
    cited = {REFRAME[c] for c in REFRAME}
    unknown_rule = sorted(r for r in cited if r not in FABLE_RULES)
    classes = (set(REFRAME), set(PRIMITIVES), set(CEREMONY))
    overlap = sorted(set.union(*(a & b for a in classes for b in classes
                                 if a is not b)) if len(classes) > 1
                     else set())
    rules_used = sorted(cited)
    return {"constructs_reduced": len(REFRAME),
            "primitives": len(PRIMITIVES),
            "ceremony_items": len(CEREMONY),
            "rules": sorted(FABLE_RULES),
            "rules_exercised": rules_used,
            "every_cited_rule_exists": not unknown_rule,
            "classes_pairwise_disjoint": not overlap,
            "mapped_and_ceremony_disjoint":
                not (set(REFRAME) & set(CEREMONY)),
            "total": not unknown_rule and not overlap,
            "proves": "COVERAGE_NOT_SEMANTIC_EQUIVALENCE",
            "verdict": "HELEN OS = small normative basis (3 primitives) "
                       "+ enforcement machinery (plain rules made "
                       "executable) + presentation layer (ceremony)",
            "the_real_delta": "the machinery's content beyond the plain "
                              "rules is the primitive basis, made "
                              "executable and mutation-tested"}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
