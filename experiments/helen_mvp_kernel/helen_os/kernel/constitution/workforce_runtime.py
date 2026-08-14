r"""Workforce Runtime — vNext round 2: the agentic layer hidden, not
erased, and the four locked laws.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: TARGET_ARCHITECTURE_CANDIDATE. Supersedes the two-law lock in
vnext_architecture with the four ruled laws (the five-verb string
stays there as history).

    External Boundary = Software.   Internal Cognition = Agentic.

The missing layer the workforce pattern exposed sits between the
cognitive core and the policy membrane: directors, specialists,
watchdogs, critics, scouts, escalation routing, telemetry. The
lesson is NOT "build 34 agents" — it is: move the human from task
initiation to policy, escalation and judgment.

THE FOUR LAWS (operator-locked):

    1. AI proposes. Software admits. Infrastructure isolates.
       Humans govern.
    2. Cognitive width may expand without expanding effect
       authority.
    3. Probabilistic cognition; deterministic state-transition
       governance.
    4. Never automate the task twice when you can productize the
       factory once.

LAW 2 is the Allie invariant, and it is Sigma_N's dA/dN = 0 observed
in commercial production: width up, risk tier flat, every effect
still through the human gate. The empirical argument FOR the
membrane, not against it.

LAW 3 is the operator's correction to "deterministic software" — too
strong, since inference stays probabilistic. What must be
deterministic is the governance of effects: authorization checks,
capability checks, workflow transitions, audit appends, release
identity. AI may be probabilistic. Authority cannot be.

"DO SMART THINGS" IS NOT A PROMPT. It is an index into a substrate
(goals + context + history + tools + permissions + telemetry +
evaluation + escalation rules), and its output is OPPORTUNITY
CANDIDATES, never direct mutations:

    SCAN -> PROPOSE -> RANK -> ADMIT -> EXECUTE -> RECEIPT -> LEARN

TWO METACOGNITIVE ROLES, both effect-free by construction:
- the WORKFORCE OBSERVER computes O(E) -> {friction, duplication,
  capability gaps, automation candidates} and holds no authority
  over the organization it observes;
- the COUNTERFACTUAL CRITIC asks "why this way at all?" and may only
  emit proposals.

AGENT COUNT IS NOT A KPI. An agent costs C_a = inference +
coordination + evaluation + observability + error + maintenance;
hire only when E[V_a] > C_a. Near-zero token cost is not near-zero
organizational cost — a 50-agent graph buys invisible coordination
entropy.

DICTATION IS NOT TRUTH. The tacit-capture loop closes the gap
between institutional reality and recorded reality, and its output
enters the Context Service as source_type=HUMAN_REPORT,
epistemic_state=REPORTED — promotion happens through the ordinary
witness door, never at capture.

NAMING COLLISION (cross-lane, resolved by factoring per T-COLOR-01):
"control plane" now requires a qualifier — POLICY_AUTHORITY is the
governance object; RELEASE_DISTRIBUTION is the fleet object.
Deployment infrastructure must never be mistakable for the policy
authority itself.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

STATUS = "TARGET_ARCHITECTURE_CANDIDATE"

LAWS = ("AI proposes. Software admits. Infrastructure isolates. "
        "Humans govern.",
        "Cognitive width may expand without expanding effect "
        "authority.",
        "Probabilistic cognition; deterministic state-transition "
        "governance.",
        "Never automate the task twice when you can productize the "
        "factory once.")

HUMAN_PRIMITIVES = ("SET_GOAL", "SET_POLICY", "APPROVE", "REJECT",
                    "CORRECT", "ESCALATE", "INSPECT")

ROLES = ("ORCHESTRATOR", "SCOUT", "PLANNER", "RESEARCHER",
         "EXTRACTOR", "VERIFIER", "CRITIC", "RED_TEAMER",
         "SYNTHESIZER", "EXECUTOR", "WATCHDOG", "WORKFORCE_OBSERVER")

OPPORTUNITY_PIPELINE = ("SCAN", "PROPOSE", "RANK", "ADMIT",
                        "EXECUTE", "RECEIPT", "LEARN")

OBSERVER_OUTPUTS = ("friction", "duplication", "capability_gaps",
                    "automation_candidates")

AGENT_COSTS = ("inference", "coordination", "evaluation",
               "observability", "error", "maintenance")

DETERMINISM = {
    "llm_recommendation": "PROBABILISTIC",
    "confidence_estimate": "PROBABILISTIC",
    "retrieval": "NONDETERMINISTIC_ALLOWED",
    "authorization_check": "DETERMINISTIC",
    "capability_check": "DETERMINISTIC",
    "workflow_transition": "DETERMINISTIC",
    "database_mutation": "TRANSACTIONAL",
    "audit_append": "DETERMINISTIC",
    "release_identity": "DETERMINISTIC",
}

PLANES = {"POLICY_AUTHORITY": "governance object (admission, policy)",
          "RELEASE_DISTRIBUTION": "fleet object (versions, manifests)"}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── law 2: width without authority ─────────────────────────────────────

def width_expansion(delta_width: float, delta_authority: float,
                    policy_change_admitted: bool) -> dict:
    """Agents may see more, reason more, coordinate more and propose
    more without automatically gaining more authority. Authority
    moves only through an admitted policy change — the dA/dN = 0
    invariant, observed in commercial production."""
    if delta_authority == 0:
        return {"lawful": True, "delta_width": delta_width,
                "delta_authority": 0,
                "invariant": "dA/dN = 0 held"}
    if not policy_change_admitted:
        return {"lawful": False, "reason": "E_WIDTH_BOUGHT_AUTHORITY",
                "law": "cognitive width may expand without expanding "
                       "effect authority; authority moves only "
                       "through the policy door"}
    return {"lawful": True, "delta_authority": delta_authority,
            "via": "admitted_policy_change"}


# ── law 3: probabilistic cognition, deterministic authority ────────────

def determinism_grade(component: str) -> dict:
    if component not in DETERMINISM:
        return {"ok": False, "reason": "E_UNKNOWN_COMPONENT"}
    return {"ok": True, "component": component,
            "grade": DETERMINISM[component]}


def boundary_promise(claim: str) -> dict:
    """Two overpromises, both refused: deterministic cognition (too
    strong — inference is probabilistic) and probabilistic authority
    (fatal — the governance of effects must be deterministic)."""
    if claim == "deterministic_cognition":
        return {"promisable": False,
                "reason": "E_OVERPROMISED_DETERMINISM",
                "correction": "probabilistic cognition; deterministic "
                              "state-transition governance"}
    if claim == "probabilistic_authority":
        return {"promisable": False,
                "reason": "E_PROBABILISTIC_AUTHORITY",
                "law": "AI may be probabilistic. Authority cannot be."}
    if claim == "deterministic_state_transition_governance":
        return {"promisable": True,
                "deterministic_components": tuple(
                    k for k, v in DETERMINISM.items()
                    if v in ("DETERMINISTIC", "TRANSACTIONAL"))}
    return {"promisable": None, "reason": "E_UNKNOWN_CLAIM"}


# ── the human as SVP, not first domino ─────────────────────────────────

def human_action(action: str) -> dict:
    if action in HUMAN_PRIMITIVES:
        return {"ok": True, "action": action,
                "role": "goal setter + policy maker + escalation judge"}
    if action == "PROMPT":
        return {"ok": True, "action": action,
                "role": "first domino",
                "note": "lawful but not the target: the target moves "
                        "the human from task initiation to policy, "
                        "escalation and judgment"}
    return {"ok": False, "reason": "E_UNKNOWN_PRIMITIVE"}


# ── the opportunity engine ─────────────────────────────────────────────

def opportunity_score(value: float, risk: float, cost: float,
                      opportunity_cost: float) -> dict:
    """Score(x) = V - R - C - O. Fix the EXPENSIVE bottleneck, not
    the first one found."""
    return {"score": round(value - risk - cost - opportunity_cost, 6)}


def pipeline_step(step: str, admitted: bool) -> dict:
    """'Do smart things' made enterprise-safe: the output of the scan
    is candidates, and nothing executes unadmitted."""
    if step not in OPPORTUNITY_PIPELINE:
        return {"ok": False, "reason": "E_UNKNOWN_STEP"}
    if step == "EXECUTE" and not admitted:
        return {"ok": False, "reason": "E_UNADMITTED_EXECUTION",
                "law": "SmartThings emits opportunity candidates, "
                       "never direct mutations; ADMIT precedes "
                       "EXECUTE"}
    return {"ok": True, "step": step,
            "position": OPPORTUNITY_PIPELINE.index(step)}


# ── the two metacognitive roles, effect-free ───────────────────────────

def observer_report(outputs: tuple) -> dict:
    """The Workforce Observer improves the organization WITHOUT
    holding authority over it. Anything shaped like an order is
    refused."""
    unknown = sorted(set(outputs) - set(OBSERVER_OUTPUTS))
    if unknown:
        return {"ok": False, "reason": "E_OBSERVER_HAS_NO_AUTHORITY",
                "refused_outputs": tuple(unknown),
                "law": "the observer computes friction, duplication, "
                       "capability gaps and automation candidates; "
                       "it commands nothing"}
    return {"ok": True, "outputs": tuple(sorted(set(outputs))),
            "authority": 0}


def critic_emission(kind: str) -> dict:
    """The counterfactual critic asks 'why this way at all?' and may
    only propose."""
    if kind != "proposal":
        return {"ok": False, "reason": "E_CRITIC_MAY_ONLY_PROPOSE"}
    return {"ok": True, "kind": "proposal",
            "questions": ("why does a human initiate this?",
                          "why this artifact at all?",
                          "why this cadence?",
                          "why is the source not continuously "
                          "materialized?")}


# ── agent economics ────────────────────────────────────────────────────

def hire_agent(expected_value: float, costs: dict) -> dict:
    """E[V_a] > C_a or no hire. All six cost terms must be priced —
    omitting one is how 'near-zero token cost' launders itself into
    'near-zero cost'."""
    missing = sorted(set(AGENT_COSTS) - set(costs))
    if missing:
        return {"hired": False, "reason": "E_UNPRICED_COST",
                "missing": tuple(missing),
                "law": "near-zero token cost is not near-zero "
                       "organizational cost"}
    total = sum(costs[k] for k in AGENT_COSTS)
    if expected_value <= total:
        return {"hired": False, "reason": "E_AGENT_COUNT_IS_NOT_A_KPI",
                "E_V": expected_value, "C_a": round(total, 6),
                "law": "optimize useful cognitive coverage, not "
                       "agent count"}
    return {"hired": True, "E_V": expected_value,
            "C_a": round(total, 6)}


# ── the tacit context capture loop ─────────────────────────────────────

def tacit_capture(speaker: str, claim: str) -> dict:
    """Dictation closes the reality/record gap and is NOT instant
    truth: it enters as HUMAN_REPORT / REPORTED. Promotion goes
    through the ordinary witness door."""
    return {"ok": True, "source_type": "HUMAN_REPORT",
            "epistemic_state": "REPORTED", "speaker": speaker,
            "claim": claim, "promoted": False,
            "law": "dictation is capture, not proof; the "
                   "institutional-memory doctrine survives the "
                   "convenience"}


# ── the factory law ────────────────────────────────────────────────────

def factory_gate(automations_of_same_task: int) -> dict:
    if automations_of_same_task < 0:
        raise ValueError("E_NEGATIVE_COUNT")
    if automations_of_same_task >= 2:
        return {"verdict": "PRODUCTIZE_THE_FACTORY",
                "law": "never automate the task twice when you can "
                       "productize the factory once"}
    return {"verdict": "AUTOMATE_THE_TASK",
            "note": "the first instance is allowed to be bespoke"}


# ── the plane collision, resolved by factoring ─────────────────────────

def plane(name: str, qualifier: str | None = None) -> dict:
    """Cross-lane collision: 'Guidance Control Plane' (governance)
    vs 'control plane' (fleet). Resolution per T-COLOR-01: factor,
    do not supersede. The bare term now requires a qualifier."""
    if name == "control_plane" and qualifier is None:
        return {"ok": False, "reason": "E_AMBIGUOUS_PLANE",
                "must_qualify_as": tuple(PLANES),
                "law": "deployment infrastructure must never be "
                       "mistakable for the policy authority itself"}
    key = qualifier or name
    if key in PLANES:
        return {"ok": True, "plane": key, "meaning": PLANES[key]}
    return {"ok": False, "reason": "E_UNKNOWN_PLANE"}
