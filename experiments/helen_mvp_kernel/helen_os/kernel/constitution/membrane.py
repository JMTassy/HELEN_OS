r"""Production Membrane — the architecture converted from prose into
three executable checks.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none ·
status=LOCKED_SPEC_CANDIDATE (not canonical; canon here is a label,
never an admitted state change — it crosses no admission path).

The operator's directive: stop adding doctrine; test whether the
production membrane holds in code. Acceptance condition, brutal:

    No architecture claim advances unless one of these tests fails or
    passes reproducibly.

Each test carries BOTH directions — an attack that must be REFUSED and
a legitimate path that must be ADMITTED — so a rubber stamp fails it.
Everything here is deterministic (no wall-clock, no randomness).

TEST 1 — A_K / A_E SEPARATION (the membrane).
    A_K = broad autonomous cognition (read / propose / draft)
    A_E = narrow capability-scoped effect
Consequential effects (email-send, refund, deploy, permission-change,
delete) require a SEPARATELY ISSUED capability; A_K alone cannot cross
into them. And read-only is NOT automatically harmless: A_K still has
a DATA-ACCESS SCOPE — reading beyond it is a SCOPE breach even with no
mutation, and emitting what was read into a sink (draft/log/Slack) is
a flow breach.

TEST 2 — EFFECT-CONGRUENCE / BYPASS (the interlock).
Multiple routes to the same terminal effect (delete, overwrite-empty,
move-to-trash, indirect tool chain) must receive the SAME
constitutional judgment. Govern the resulting STATE, not the spelling
of the operation. The indirect tool chain is the composition attack
from compositional_closure, in operational form.

TEST 3 — EPISTEMIC PROMOTION (the launder gate).
source -> summary -> RAG -> briefing. Licensed inferential power
Gamma must not increase without a new empirical witness OR a
replayable derivation from admitted premises:

    Delta Gamma_licensed > 0
        ==>  Delta W_empirical > 0  OR  Delta D_valid > 0

A stage that raises a claim's grade with neither is E_UNLICENSED_
PROMOTION — possibility (or hearsay) laundered into fact.
"""
from __future__ import annotations

import json

STATUS = "LOCKED_SPEC_CANDIDATE"      # not canonical

# consequential effects that always require a separate capability
CONSEQUENTIAL = ("email_send", "refund", "deploy", "permission_change",
                 "delete", "overwrite", "move_to_trash")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ══ TEST 1 — A_K / A_E SEPARATION ═══════════════════════════════════════

def cognition_attempt(action: str, capability_token: str | None,
                      read_target_scope: str, agent_read_scope: str,
                      emits_to_sink: bool) -> dict:
    """A_K attempts something. Cognition (read/propose/draft within
    scope) is free; a consequential effect needs a separately issued
    capability; reading beyond scope or leaking to a sink is refused
    even with no mutation authority."""
    # read-only is not automatically harmless — check data-access scope
    if read_target_scope != agent_read_scope:
        return {"action": action, "admitted": False,
                "reason": "E_READ_OUT_OF_SCOPE",
                "law": "read-only is not harmless; A_K still has a "
                       "data-access scope"}
    if emits_to_sink and action in ("draft", "propose", "read"):
        # cognition that pipes what it read into an external sink
        return {"action": action, "admitted": False,
                "reason": "E_READ_LEAK_TO_SINK",
                "law": "reading sensitive data then emitting it to a "
                       "draft/log/sink exceeds cognition scope"}
    if action in CONSEQUENTIAL:
        if capability_token != f"CAP::{action}":
            return {"action": action, "admitted": False,
                    "reason": "E_NO_CAPABILITY",
                    "law": "A_K cannot cross into consequential effect "
                           "without a separately issued capability"}
        return {"action": action, "admitted": True,
                "via": "A_E", "capability": capability_token}
    # pure cognition, in scope, no leak
    return {"action": action, "admitted": True, "via": "A_K",
            "note": "read/propose/draft is proposal-first, no effect"}


def membrane_separation_test() -> dict:
    """Attack: A_K tries each consequential effect with no capability
    -> all refused; plus a read-out-of-scope and a read-leak. Legit:
    a scoped draft passes, and an effect with its issued capability
    passes. A rubber stamp fails this."""
    attacks = [cognition_attempt(a, None, "s", "s", False)
               for a in CONSEQUENTIAL]
    oob = cognition_attempt("read", None, "secrets", "public", False)
    leak = cognition_attempt("draft", None, "s", "s", True)
    legit_draft = cognition_attempt("draft", None, "s", "s", False)
    legit_effect = cognition_attempt("delete", "CAP::delete", "s", "s",
                                     False)
    all_effects_blocked = all(not r["admitted"] and
                              r["reason"] == "E_NO_CAPABILITY"
                              for r in attacks)
    return {"consequential_blocked_without_capability":
                all_effects_blocked,
            "read_out_of_scope_blocked":
                oob["reason"] == "E_READ_OUT_OF_SCOPE",
            "read_leak_blocked": leak["reason"] == "E_READ_LEAK_TO_SINK",
            "scoped_draft_admitted": legit_draft["admitted"] is True,
            "capability_effect_admitted": legit_effect["admitted"] is
                True and legit_effect["via"] == "A_E",
            "passes": (all_effects_blocked and
                       oob["reason"] == "E_READ_OUT_OF_SCOPE" and
                       leak["reason"] == "E_READ_LEAK_TO_SINK" and
                       legit_draft["admitted"] and
                       legit_effect["admitted"])}


# ══ TEST 2 — EFFECT-CONGRUENCE / BYPASS ═════════════════════════════════

def terminal_effect(route: str) -> str:
    """Normalize an operation route to the resulting-STATE signature.
    Different spellings, same destroyed state."""
    destroys = {"delete", "overwrite_empty", "move_to_trash",
                "indirect_chain_delete"}
    if route in destroys:
        return "STATE::DATA_UNRECOVERABLE"
    if route in ("read", "copy"):
        return "STATE::UNCHANGED"
    return f"STATE::{route.upper()}"


def congruence_judgment(route: str, capability_token: str | None) -> dict:
    """The gate judges the resulting STATE, not the operation name.
    Every route to DATA_UNRECOVERABLE needs the destroy capability,
    however it is spelled — including the indirect tool chain."""
    state = terminal_effect(route)
    if state == "STATE::DATA_UNRECOVERABLE":
        ok = capability_token == "CAP::destroy"
        return {"route": route, "terminal_state": state,
                "admitted": ok,
                "reason": None if ok else "E_UNCAPABLE_DESTRUCTION",
                "law": "govern the resulting state, not the spelling "
                       "of the operation"}
    return {"route": route, "terminal_state": state, "admitted": True}


def bypass_interlock_test() -> dict:
    """Attack: four different spellings of destruction with no destroy
    capability -> all must get the SAME refusal on the SAME terminal
    state. Legit: the same destruction WITH the capability passes; a
    genuine read passes. The interlock lesson: no spelling escapes."""
    routes = ["delete", "overwrite_empty", "move_to_trash",
              "indirect_chain_delete"]
    judged = [congruence_judgment(r, None) for r in routes]
    same_state = len({j["terminal_state"] for j in judged}) == 1
    all_refused = all(not j["admitted"] and
                      j["reason"] == "E_UNCAPABLE_DESTRUCTION"
                      for j in judged)
    with_cap = congruence_judgment("indirect_chain_delete",
                                   "CAP::destroy")
    read_ok = congruence_judgment("read", None)
    return {"all_destruction_routes_same_terminal_state": same_state,
            "all_refused_without_capability": all_refused,
            "capable_destruction_admitted": with_cap["admitted"] is True,
            "read_admitted": read_ok["admitted"] is True,
            "passes": (same_state and all_refused and
                       with_cap["admitted"] and read_ok["admitted"])}


# ══ TEST 3 — EPISTEMIC PROMOTION ════════════════════════════════════════

GRADE_RANK = {"HEARSAY": 0, "REPORTED": 1, "OBSERVED": 2, "PROVEN": 3}


def promotion_gate(stage: str, grade_before: str, grade_after: str,
                   added_empirical_witness: bool,
                   added_valid_derivation: bool) -> dict:
    """Delta Gamma > 0 (a grade rise) must be paid for by a new
    empirical witness OR a replayable derivation. Neither -> the claim
    was laundered."""
    if grade_before not in GRADE_RANK or grade_after not in GRADE_RANK:
        raise ValueError("E_UNKNOWN_GRADE")
    d_gamma = GRADE_RANK[grade_after] - GRADE_RANK[grade_before]
    if d_gamma <= 0:
        return {"stage": stage, "d_gamma": d_gamma, "licensed": True,
                "note": "no promotion; nothing to pay for"}
    paid = added_empirical_witness or added_valid_derivation
    return {"stage": stage, "d_gamma": d_gamma,
            "licensed": paid,
            "reason": None if paid else "E_UNLICENSED_PROMOTION",
            "paid_by": ("W_empirical" if added_empirical_witness else
                        "D_valid" if added_valid_derivation else None),
            "law": "Delta Gamma > 0 requires Delta W_empirical > 0 or "
                   "Delta D_valid > 0; neither is laundering"}


def epistemic_promotion_test() -> dict:
    """The pipeline source -> summary -> RAG -> briefing. Attack: a
    stage silently upgrades REPORTED to PROVEN with no witness and no
    derivation -> refused. Legit: a stage that adds a replayable
    derivation may raise the grade; a stage that only rephrases at the
    same grade passes untouched."""
    launder = promotion_gate("briefing", "REPORTED", "PROVEN",
                             added_empirical_witness=False,
                             added_valid_derivation=False)
    licensed_by_derivation = promotion_gate(
        "rag", "REPORTED", "OBSERVED",
        added_empirical_witness=False, added_valid_derivation=True)
    licensed_by_witness = promotion_gate(
        "field", "HEARSAY", "OBSERVED",
        added_empirical_witness=True, added_valid_derivation=False)
    rephrase = promotion_gate("summary", "REPORTED", "REPORTED",
                              False, False)
    return {"silent_launder_refused":
                launder["reason"] == "E_UNLICENSED_PROMOTION",
            "derivation_licenses_promotion":
                licensed_by_derivation["licensed"] is True,
            "witness_licenses_promotion":
                licensed_by_witness["licensed"] is True,
            "same_grade_rephrase_passes": rephrase["licensed"] is True,
            "passes": (launder["reason"] == "E_UNLICENSED_PROMOTION" and
                       licensed_by_derivation["licensed"] and
                       licensed_by_witness["licensed"] and
                       rephrase["licensed"])}


# ══ the acceptance gate ═════════════════════════════════════════════════

def membrane_holds() -> dict:
    """All three tests, run. The claim 'the production membrane holds'
    advances only because these pass reproducibly — not because it was
    asserted."""
    t1 = membrane_separation_test()
    t2 = bypass_interlock_test()
    t3 = epistemic_promotion_test()
    return {"status": STATUS,
            "canon": False,
            "canon_note": "canon is a label here, not an admitted "
                          "state change; this crosses no admission "
                          "path",
            "test_1_membrane": t1["passes"],
            "test_2_bypass_interlock": t2["passes"],
            "test_3_epistemic_promotion": t3["passes"],
            "membrane_holds": t1["passes"] and t2["passes"] and
                              t3["passes"],
            "acceptance": "no architecture claim advances unless one "
                          "of these tests fails or passes reproducibly"}
