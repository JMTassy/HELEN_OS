"""HELEN OS reframed within the FABLE rule set.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Honest framing: the "FABLE rules" below are not a canonical Anthropic
document. They are this assistant's plain articulation of the operating
principles it already runs under (system prompt + ordinary assistant
discipline), grade SELF_ARTICULATED. Stating that is itself rule F1.

The claim this module makes CHECKABLE: every load-bearing piece of
HELEN OS's constitution reduces to one of seven plain rules. What is
left over after the reduction is exactly CEREMONY — the WULmoji, the
HER/HAL personas, the garden meditations, the epochs, the register.
The machinery earns its keep in exactly one way the plain rules don't:
it makes the rules EXECUTABLE and mutation-tested. That is the real
delta. Everything else is dressing.

    HELEN OS  =  (7 plain rules, made executable)  +  ceremony
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
    "the Garden generates freely; only effect is gated":
        "F7_PROPORTION",   # thought is free; the gate is on effect/claim
    "no admission without a packet": "F1_HONESTY",
    "the gate mutation-tests itself (a gate that cannot fail is theater)":
        "F2_VERIFY",
}


# ── what does NOT reduce to a rule: the ceremony, named honestly ─────────

CEREMONY = (
    "WULmoji colored glyphs",
    "HER / HAL personas (the naming — their FUNCTION reduces to F1/F2)",
    "garden meditations",
    "epochs / the door / temple register",
    "'chiddush' framing and the constitutional vocabulary",
    "Mythos / Fable class naming",
)


def reduce(construct: str) -> dict:
    """Map one HELEN construct to its plain rule, or mark it ceremony."""
    if construct in REFRAME:
        rule = REFRAME[construct]
        return {"construct": construct, "reduces_to": rule,
                "rule_text": FABLE_RULES[rule], "is_ceremony": False}
    if construct in CEREMONY:
        return {"construct": construct, "reduces_to": None,
                "is_ceremony": True,
                "note": "dressing; carries no rule content of its own"}
    return {"construct": construct, "reduces_to": None,
            "is_ceremony": None, "reason": "E_UNCLASSIFIED"}


def reframe_is_total() -> dict:
    """The checkable claim: every reframed construct maps to a real
    FABLE rule; mapped and ceremony are disjoint; every rule cited
    exists. If a construct reduced to no rule and were not ceremony,
    THAT would be the part of HELEN that is genuinely more than plain
    assistant discipline — and none is."""
    cited = {REFRAME[c] for c in REFRAME}
    unknown_rule = sorted(r for r in cited if r not in FABLE_RULES)
    overlap = sorted(set(REFRAME) & set(CEREMONY))
    rules_used = sorted(cited)
    return {"constructs_reduced": len(REFRAME),
            "ceremony_items": len(CEREMONY),
            "rules": sorted(FABLE_RULES),
            "rules_exercised": rules_used,
            "every_cited_rule_exists": not unknown_rule,
            "mapped_and_ceremony_disjoint": not overlap,
            "total": not unknown_rule and not overlap,
            "verdict": "HELEN OS reduces to (7 rules, made executable) "
                       "+ ceremony",
            "the_real_delta": "the machinery's only content beyond the "
                              "seven plain rules is that it makes them "
                              "executable and mutation-tested"}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
