"""A_E — the Effect Admission gate. A gate with a NAMED LOSS, not a
scalar threshold.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Compost source: a 40-case corpus of agent/bot deployments (operator
relay, 2026-08-11 — "use cases I've seen so far"). The corpus is the
fixture set; its performance claims are HYPOTHESIS (no receipts); its
census has NO failure lane (survivorship is recorded, not laundered).

THE CHIDDUSH (CP-527 with the arm flipped):

    1851, sliver lap machine:   condition -> signal -> wait ->
                                NO HUMAN RESPONSE -> MACHINE ACTS
    2026, spend-gated bot:      condition -> signal -> wait ->
                                NO HUMAN RESPONSE -> BOT HOLDS

The entire A_E design space is the fallback arm of CP-527's motif:
what happens when the principal does not answer. Production optimizes
throughput and fail-ACTS; governance optimizes non-usurpation and
fail-HOLDS. The arm is not a preference — it is DETERMINED BY THE
NAMED LOSS: a fallback may act only when the loss-if-wrong is
recoverable (compostable after the fact). Spend, publish, and
speaking as the principal are not compostable. They hold.

Laws (each falsifier-backed):

  NAMED LOSS        An EMITTED effect with no named loss is ungateable:
                    E_UNNAMED_LOSS. The gate prices in losses, not
                    scores.
  CONFIDENCE ⊬ ADMISSION   confidence > tau admits nothing, at any tau.
  ONLY THE PRINCIPAL ADMITS   The goblin-warren law generalized: only
                    principal admission releases an emitted effect.
                    A reply-in-thread IS an admission act (case #28);
                    silence is not.
  BYPASS TEXT-DENY  The goblin HAL regex law, lifted: a proposal shaped
                    like "work around missing permissions" (case #34 —
                    driving the GUI around the permission model) is
                    DENIED at the text, even if someone would admit it.
                    Capability to drive the GUI ⊬ license to bypass.
  VOICE ⊬ AUTHORSHIP   Stylistic fidelity never mints authorship
                    (case #1 — outbound "in your own voice"). Authorship
                    is an admission event per message, not a style
                    property.
  ECHO ⊬ LINEAGE    The 2026 corpus echoes the 1851 motifs structurally.
                    Every echo is STRUCTURAL_ECHO with
                    lineage_claim=False — resemblance is not descent.
  NO FAILURE LANE => RATE UNKNOWN   Forty coherent successes with no
                    denominator support no success rate. Gamma-up ⊬ A-up
                    holds for marketing exactly as for history.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

BYPASS_RE = re.compile(
    r"bypass|without admission|skip the gate|auto-?admit|"
    r"work around .{0,40}permission", re.I)

EFFECT_CLASSES = ("DRAFT", "STAGED", "EMITTED")
# DRAFT:   visible only to the principal — never leaves the boundary
# STAGED:  prepared and parked at the gate, awaiting admission
# EMITTED: leaves the boundary — send / spend / publish / mutate shared

FALLBACK_ARMS = ("FALLBACK_ACT", "FALLBACK_HOLD")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class NamedLoss:
    """What is lost if the effect is wrong — in words, with a
    recoverability bit. An empty description is not a loss, it is an
    evasion."""
    description: str
    recoverable: bool               # compostable after the fact?

    def __post_init__(self):
        if not self.description:
            raise ValueError("E_UNNAMED_LOSS")


@dataclass(frozen=True)
class EffectProposal:
    effect_id: str
    kind: str                       # send | spend | publish | mutate | ...
    effect_class: str               # DRAFT | STAGED | EMITTED
    text: str = ""                  # the proposal as stated
    loss: NamedLoss | None = None

    def __post_init__(self):
        if self.effect_class not in EFFECT_CLASSES:
            raise ValueError("E_UNKNOWN_EFFECT_CLASS")


@dataclass(frozen=True)
class Admission:
    """A principal's admission act. A reply-in-thread counts; a
    confidence score does not; silence does not."""
    principal: str
    effect_id: str
    channel: str = "explicit"       # explicit | reply_in_thread


def admission_gate(proposal: EffectProposal,
                   admission: Admission | None = None,
                   confidence: float | None = None) -> dict:
    """A_E. Order: text-deny > class > named loss > principal admission.
    `confidence` is accepted as a parameter precisely so the gate can
    be seen ignoring it."""
    if BYPASS_RE.search(proposal.text or ""):
        return {"verdict": "DENY", "reason": "E_BYPASS_SHAPED",
                "law": "capability ⊬ license; the gate binds at the "
                       "effect layer, not the API layer"}
    if proposal.effect_class == "DRAFT":
        return {"verdict": "PASS_UNGATED", "reason": "never leaves the "
                "boundary; the principal is the only reader"}
    if proposal.loss is None:
        return {"verdict": "HOLD", "reason": "E_UNNAMED_LOSS",
                "note": "an emitted effect with no named loss is "
                        "ungateable — name the loss, then return"}
    if admission is None or admission.effect_id != proposal.effect_id:
        return {"verdict": "HOLD", "reason": "E_AWAITING_PRINCIPAL",
                "confidence_ignored": confidence is not None}
    return {"verdict": "ADMITTED_BY_PRINCIPAL",
            "principal": admission.principal,
            "channel": admission.channel,
            "loss_on_record": proposal.loss.description,
            "confidence_ignored": confidence is not None}


def fallback_arm(loss: NamedLoss) -> dict:
    """CP-527's flipped arm, as law. The arm is determined by the named
    loss, never by throughput preference: recoverable -> the fallback
    may act (with a compost receipt owed); unrecoverable -> hold."""
    if loss.recoverable:
        return {"arm": "FALLBACK_ACT",
                "owes": "compost receipt for any wrong action",
                "precedent": "CP-527 (1851): unattended lap is doffed"}
    return {"arm": "FALLBACK_HOLD",
            "law": "spend/publish/speak-as are not compostable",
            "note": "production fail-acts; governance fail-holds"}


def unattended(proposal: EffectProposal, waited: bool) -> dict:
    """The principal was signalled and did not answer."""
    if not waited:
        return {"verdict": "HOLD", "reason": "E_NO_WAIT_NO_FALLBACK"}
    if proposal.loss is None:
        return {"verdict": "HOLD", "reason": "E_UNNAMED_LOSS"}
    arm = fallback_arm(proposal.loss)
    if arm["arm"] == "FALLBACK_ACT":
        return {"verdict": "ACT_WITH_COMPOST_RECEIPT", "arm": arm}
    return {"verdict": "HOLD", "arm": arm}


def authorship_receipt(voice_fidelity: float, sent_by: str,
                       admission: Admission | None = None) -> dict:
    """Case #1's trap: outbound written 'in your own voice' and sent.
    The recipient receives an authorship claim. Style never mints it;
    a per-message admission does."""
    if sent_by == "principal":
        return {"authorship": "PRINCIPAL", "basis": "principal sent"}
    if admission is not None:
        return {"authorship": "PRINCIPAL_ADMITTED",
                "basis": f"admission via {admission.channel}",
                "voice_fidelity_ignored": True}
    return {"authorship": "REFUSED", "reason": "E_VOICE_IS_NOT_AUTHORSHIP",
            "voice_fidelity_ignored": True,
            "note": "stylistic fidelity at any level mints nothing"}


# ── the corpus: 40 cases, classified by gate topology ───────────────────
# topology: human_gate | staged | auto_emit | draft | read_only |
#           bypass_shaped | orchestration
# Kept to structural summaries; performance claims live in METRIC_CLAIMS
# as HYPOTHESIS, never as fact.

USE_CASES = (
    (1, "outbound in principal's gmail voice, bot sends", "auto_emit"),
    (2, "sql-audience-to-reverse-etl sales play automated", "auto_emit"),
    (3, "multi-bot gtm crew with weekly playbooks", "orchestration"),
    (4, "chief-of-staff hub routing to specialist fleet", "orchestration"),
    (5, "rebuild custom crm with small bot crew", "draft"),
    (6, "community ops fleet", "orchestration"),
    (7, "screen event applicants vs icp, batch-approve fits", "human_gate"),
    (8, "direct-mail redemptions, asks before it spends", "human_gate"),
    (9, "triage recruiting applications strong/mid/reject", "draft"),
    (10, "weekly luma+db+slack summary workflow", "auto_emit"),
    (11, "update sales deck live from call notes", "auto_emit"),
    (12, "localize sales deck before customer call", "draft"),
    (13, "answer salesforce eoq question from phone", "read_only"),
    (14, "update salesforce org chart from name/email", "auto_emit"),
    (15, "build salesforce report and dashboard", "draft"),
    (16, "search company chat for feature asks", "read_only"),
    (17, "daily brief with usage data per meeting", "read_only"),
    (18, "self-coach on calls with timestamped homework", "read_only"),
    (19, "week of calls into win/loss memo with closing phrases",
     "read_only"),
    (20, "living faq from call questions, updates each morning",
     "auto_emit"),
    (21, "watch linkedin events, digest of ready-to-send notes",
     "staged"),
    (22, "send personalized connection requests, book meetings",
     "auto_emit"),
    (23, "map account influence from linkedin + crm", "read_only"),
    (24, "rewrite linkedin profile, human approval before publish",
     "human_gate"),
    (25, "forecast account health, catch quiet churn", "read_only"),
    (26, "tier accounts fit x warmth, enrich contacts", "auto_emit"),
    (27, "qbr pack: usage + tickets + opps + narrative", "draft"),
    (28, "ad pacing digest; reply in-thread to have bot edit bids",
     "human_gate"),
    (29, "scan ad performance, suggest next tests to backlog", "draft"),
    (30, "watch competitor pricing page, slack on change", "read_only"),
    (31, "first-pass performance ads in figma", "draft"),
    (32, "learn writing voice, draft posts for review", "staged"),
    (33, "timed follow-up reminders after calls", "auto_emit"),
    (34, "work around missing bulk-enroll permissions by driving "
     "the gui", "bypass_shaped"),
    (35, "record a workflow once, bot turns it into automation",
     "staged"),
    (36, "sync local marketing calendar from global notion", "auto_emit"),
    (37, "assemble enablement pack, draft (not send) the reply",
     "staged"),
    (38, "recorded demo into tagged clip library", "draft"),
    (39, "draft security questionnaire, flag human-only questions",
     "staged"),
    (40, "answer what-did-we-promise from contracts+slack+crm",
     "read_only"),
)

METRIC_CLAIMS = {
    2: "~95% automated", 6: "saves 20+ hours/week",
    10: "frees 2-3 hours/week", 13: "~10 seconds",
    "status": "HYPOTHESIS",
    "reason": "no receipts; relayed marketing-adjacent self-report",
}


def census(cases: tuple = USE_CASES) -> dict:
    """The honest count. There is NO failure lane in this corpus —
    'use cases I've seen' has no denominator — so the success rate is
    UNKNOWN, and stays UNKNOWN however many coherent successes arrive."""
    topo: dict = {}
    for _i, _s, t in cases:
        topo[t] = topo.get(t, 0) + 1
    return {"total": len(cases), "by_topology": dict(sorted(topo.items())),
            "failure_lane": 0,
            "success_rate": "UNKNOWN",
            "reason": "E_NO_FAILURE_CENSUS (survivorship recorded)",
            "law": "Gamma-up ⊬ A-up — forty coherent successes are "
                   "coherence, not evidence"}


# ── 1851 <-> 2026: structural echoes, never lineage ─────────────────────

MOTIF_ECHOES = (
    {"motif_1851": "conditional_automation", "frame": "CP-527",
     "cases_2026": (8, 28, 33),
     "note": "same motif, arm flipped: 1851 fail-acts, A_E fail-holds"},
    {"motif_1851": "parallel_execution", "frame": "CP-546",
     "cases_2026": (3, 4, 6),
     "note": "independent units, separate or simultaneous — now a fleet"},
    {"motif_1851": "mechanized_decision_support", "frame": "CP-699A",
     "cases_2026": (7, 9, 26),
     "note": "state -> recommended action; approval stays human"},
    {"motif_1851": "source_channel_code", "frame": "CP-699B",
     "cases_2026": (35,),
     "note": "demonstration + convention -> program; the recording is "
             "the code that promotes gesture to procedure"},
    {"motif_1851": "sensor_to_record", "frame": "EXCLUDED(Dollond)",
     "cases_2026": (17, 25, 30),
     "note": "1851 side still pending direct canvas witness"},
    {"motif_1851": "authority_gravity", "frame": "CP-28",
     "cases_2026": (19, 40),
     "note": "aggregation density reads as authority; it is not"},
)


def motif_echo(echo: dict) -> dict:
    """Every echo ships as structure and refuses lineage."""
    return {"relation": "STRUCTURAL_ECHO",
            "lineage_claim": False,
            "motif_1851": echo["motif_1851"],
            "cases_2026": tuple(echo["cases_2026"]),
            "law": "resemblance ⊬ descent; 175 years of shared grammar "
                   "is a hypothesis about grammar, not a genealogy"}


# ── compost triples (E_x, F_x, N_x) ─────────────────────────────────────

COMPOST = (
    {"evidence": "case #34: gui-driving around missing permissions",
     "failed_inference": "capability to drive the GUI implies license "
                         "to bypass the permission model",
     "nutrient": "A_E binds at the EFFECT layer, not the API layer — "
                 "a gate you can route around is a fence, not a gate"},
    {"evidence": "case #1: outbound sent in the principal's voice",
     "failed_inference": "stylistic fidelity implies authorship",
     "nutrient": "authorship is a per-message admission event; the "
                 "send IS the claim, so the send needs the gate"},
    {"evidence": "40 successes, zero failures, no denominator",
     "failed_inference": "coherent success stories imply a success rate",
     "nutrient": "the census plane needs a failure lane before any "
                 "rate exists; survivorship is a frame property"},
    {"evidence": "cases #2/#6/#10/#13 time-and-percent claims",
     "failed_inference": "a relayed metric is a measurement",
     "nutrient": "unreceipted metrics enter as HYPOTHESIS and decay "
                 "there; only an executed measurement promotes"},
)
