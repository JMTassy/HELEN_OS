r"""Earned Reliability — Hamilton's second lesson: time the test of
any product.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Source, graded honestly: the same 1947 Hamilton/Jam Handy film,
RELAYED as transcript. Its argument is NOT fine = accurate — it says
plainly that early watches drifted an hour a day and still carried
prestige. What makes a fine watch fine is a production ecology:
people, craft, facilities, research, inspection, and A RECORD OF
PERFORMANCE THROUGH TIME. One watch, built fifty-four years before
the film, still passed railroad time inspection.

The chiddush: QUALITY IS A HISTORICAL PROPERTY OF A SYSTEM, NOT AN
INSTANTANEOUS PROPERTY OF AN OUTPUT.

    Fine(X) != Correct(x_t)

A single correct output says almost nothing about the reliability of
the process that produced it. Reliability is earned over the
execution history H_n = (delta_1, ..., delta_n):

    Q_n = Q(H_n),      and critically      Q_0 = UNKNOWN.

No agent starts reputable because it says it is reputable. The laws
this module makes executable:

    1. Q_0 = UNKNOWN — reputation starts empty, always.
    2. Self-reports contribute NOTHING; unwitnessed exposure
       contributes NOTHING (witness supremacy applied to reputation).
    3. TestPass does not entail Trust — a green suite measures
       Q_instant; operational history measures Q_longitudinal. This
       module's own '390 green, gate 60/60' is exactly Q_instant.
    4. Repeated witnessed survival INCREASES evidence, asymptotically,
       and never reaches infallibility — UNKNOWN is preserved at the
       limit.
    5. THE CRUCIAL ONE:  Trust_t(a) does not entail Authority_{t+1}(a).
       Past reliability may inform (review priority, proposal weight —
       the GOBLIN-compost pattern: weight proposals, never admission).
       It must never mint authority, skip the gate, or be inherited.
    6. The moat: the constitution is copyable — anyone can copy
       P /\ S /\ A /\ R tomorrow. Accumulated verified operational
       history H_{0:n} is not copyable, not borrowable, not heritable.
       The ledger is therefore not ceremony and not "truth": it is the
       DATASET from which reliability claims can be evaluated.

The inheritance scene, read correctly: the son receives the watch
(artifact, with provenance) and the standard (the constraint). He
does NOT receive the father's reputation — that he must earn against
his own history. Constraint + artifact + history -> institutional
memory; a good receipt is a constitutional watch: it lets a future
actor recover what happened, under what rule, with what evidence.

    Trust is not a property you declare. It is a property a process
    accumulates by surviving tests through time.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

RAILROAD_GRADE_EXPOSURES = 54          # the fifty-four-year watch

HAMILTON_HELEN_CROSSWALK = {
    "precision": "admission correctness",
    "craft/process": "gate implementation",
    "inspection": "verification",
    "service record": "receipt history",
    "reputation": "earned reliability",
    "time": "adversarial exposure",
}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class Exposure:
    """One survival test the actor was exposed to, and whether a
    witness saw the outcome. SELF_REPORT is a kind, not a witness."""
    actor: str
    t: int
    kind: str          # GATE_PASS | FALSIFIER_SURVIVED | BREACH | SELF_REPORT
    witnessed: bool = False


SURVIVAL_KINDS = ("GATE_PASS", "FALSIFIER_SURVIVED")


# ── Q_n = Q(H_n): trust as a function of verified history only ─────────

def trust_at(actor: str, history: tuple, t: int) -> dict:
    """F(verified history of `actor` up to t). Only witnessed,
    non-self-reported exposures count — witness supremacy applied to
    reputation. Evidence grows asymptotically and never reaches 1."""
    verified = [e for e in history
                if e.actor == actor and e.t <= t and e.witnessed
                and e.kind != "SELF_REPORT"]
    ignored_self_reports = sum(1 for e in history
                               if e.actor == actor and e.t <= t
                               and e.kind == "SELF_REPORT")
    ignored_unwitnessed = sum(1 for e in history
                              if e.actor == actor and e.t <= t
                              and not e.witnessed
                              and e.kind != "SELF_REPORT")
    survived = sum(1 for e in verified if e.kind in SURVIVAL_KINDS)
    breaches = sum(1 for e in verified if e.kind == "BREACH")

    evidence = round(survived / (survived + 4 + 8 * breaches), 6) \
        if survived else 0.0

    if breaches:
        grade = "CONTESTED"
    elif survived == 0:
        grade = "UNKNOWN"                                   # Q_0
    elif survived >= RAILROAD_GRADE_EXPOSURES:
        grade = "RAILROAD_GRADE"
    elif survived >= 10:
        grade = "ESTABLISHED"
    else:
        grade = "EMERGING"

    return {"actor": actor, "t": t,
            "witnessed_survivals": survived,
            "witnessed_breaches": breaches,
            "ignored_self_reports": ignored_self_reports,
            "ignored_unwitnessed": ignored_unwitnessed,
            "evidence": evidence,
            "grade": grade,
            "infallible": False,        # at ANY n — UNKNOWN preserved
            "law": "repeated witnessed performance increases evidence "
                   "for reliability; it never entails infallibility"}


def declare_reputable(actor: str) -> dict:
    """The refused shortcut: reputation by assertion."""
    return {"actor": actor, "granted": False,
            "reason": "E_SELF_DECLARED_REPUTATION",
            "law": "no agent starts reputable because it says it is "
                   "reputable; Q_0 = UNKNOWN"}


# ── TestPass does not entail Trust ──────────────────────────────────────

def trust_from_test_pass(n_green: int, probes_held: int = 0) -> dict:
    """A green suite — including THIS project's own — measures
    Q_instant. It is good evidence and it is not longitudinal trust."""
    return {"measures": "Q_INSTANT",
            "n_green": n_green, "probes_held": probes_held,
            "is_good_evidence": n_green > 0,
            "entails_longitudinal_trust": False,
            "law": "TestPass does not entail Trust; passing now is "
                   "not reliable historically"}


# ── Trust_t(a) does not entail Authority_{t+1}(a) — the crucial law ────

def authority_from_trust(trust: dict) -> dict:
    """Refused at EVERY grade, including RAILROAD_GRADE. Reputation
    informs; only a grant authorizes."""
    return {"actor": trust["actor"], "minted": False,
            "reason": "E_REPUTATION_IS_NOT_AUTHORITY",
            "trust_grade_at_refusal": trust["grade"],
            "law": "Trust_t(a) does not entail Authority_{t+1}(a); "
                   "past reliability informs future decisions and "
                   "never mints future authority"}


def gate_skip_for_trusted(trust: dict) -> dict:
    """The other refused shortcut: however earned the trust, every
    delta still passes the four ceilings."""
    return {"actor": trust["actor"], "skipped": False,
            "reason": "E_TRUST_DOES_NOT_SKIP_THE_GATE",
            "law": "reputation weights proposals, never admission — "
                   "the compost pattern"}


def proposal_weight(trust: dict) -> dict:
    """The one thing trust MAY do: advisory ordering of proposals,
    bounded, upstream of the gate — never a verdict."""
    return {"actor": trust["actor"],
            "weight": round(1.0 + trust["evidence"], 6),   # in [1, 2)
            "advisory_only": True,
            "affects_admission_verdict": False}


# ── inheritance: the artifact transfers; the trust does not ────────────

def transfer_artifact(artifact: str, chain: tuple, heir: str) -> dict:
    """The watch passes to the son WITH its provenance — grandfather,
    father, son. Constraint + artifact + history -> institutional
    memory."""
    return {"artifact": artifact, "heir": heir,
            "provenance": tuple(chain) + (heir,),
            "transferred": True,
            "note": "the standard and its persistent physical witness "
                    "transfer; see transfer_trust for what does not"}


def transfer_trust(trust: dict, heir: str) -> dict:
    return {"heir": heir, "transferred": False,
            "reason": "E_TRUST_IS_NOT_HERITABLE",
            "law": "the son receives the watch and the standard, not "
                   "the father's reputation; Q_0(heir) = UNKNOWN"}


def import_history(events: tuple, witnessed_locally: bool) -> dict:
    """Borrowed history: another actor's record, relayed. Unless
    witnessed locally it contributes nothing — RELAY is not
    DIRECTLY_OBSERVED, applied to reputation."""
    counted = len(events) if witnessed_locally else 0
    return {"events_offered": len(events),
            "events_counted": counted,
            "reason": None if witnessed_locally else "E_BORROWED_HISTORY",
            "law": "verified operational history is earned against "
                   "one's own exposures; it cannot be imported on "
                   "testimony"}


# ── the moat: why everyone can't do it ──────────────────────────────────

def moat() -> dict:
    """Hamilton's strongest line, translated. The rules are copyable
    in an afternoon; the verified history is not. This is what turns
    the ledger from ceremony into the economically central object —
    not because ledger = truth (absolutely not), but because it is the
    dataset against which reliability claims are evaluated."""
    return {"constitution_copyable": True,
            "verified_history_copyable": False,
            "moat": "accumulated verified operational history",
            "ledger_is": "the dataset from which reliability claims "
                         "can be evaluated",
            "ledger_is_not": "truth",
            "law": "constitution is copyable; earned reliability is "
                   "not"}


# ── the receipt as constitutional watch ─────────────────────────────────

def receipt_recovers(receipt: dict) -> dict:
    """A good receipt lets a future actor recover what happened,
    under what rule, with what evidence. All three or it is not a
    constitutional watch."""
    what = bool(receipt.get("what_happened"))
    rule = bool(receipt.get("under_rule"))
    evidence = bool(receipt.get("with_evidence"))
    return {"what_happened_recoverable": what,
            "rule_recoverable": rule,
            "evidence_recoverable": evidence,
            "is_constitutional_watch": what and rule and evidence,
            "missing": sorted(k for k, v in
                              (("what_happened", what),
                               ("under_rule", rule),
                               ("with_evidence", evidence)) if not v)}
