r"""Editor Membrane — the commercial doctrine as refusals.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: CANDIDATE (commercial doctrine, operator-ruled 2026-08-14).

    We do not sell AI agents. We publish business applications that
    use AI. The agentic architecture is an implementation detail —
    and the cognitive capabilities stay sophisticated INSIDE; the
    outer membrane is industrial software.

This is the A_K/A_E separation, commercialized. The vocabulary table
(agent -> application, prompt -> configuration, memory -> knowledge
base ...) is the same factoring kappa_M/kappa_F already uses: what a
thing IS internally vs what it is SOLD as are two axes, and neither
may be inferred from the other.

THE ONE LAW THIS MODULE ADDS, because the doctrine is unusable
without it:

    RENAMING IS LAWFUL IFF THE PROPERTY IS WITNESSED

Calling an agent "une application métier" is lawful only if the
application-grade properties actually exist — versioned releases,
SLA, runbook, tested continuity. Otherwise the vocabulary table is
laundering: beautiful seal, no admission. Every row of the table
names the witness its rename requires.

THE NON-ENTAILMENTS, each already a family member:

    source recovered            !=>  application recoverable
    escrow release              !=>  IP transferred
    infra security properties   !=>  AI Act compliance of the app
    continuity ARCHITECTED      !=>  key-person risk ELIMINATED
    certification of provider   !=>  certification of each service
    application                 !=>  model vendor

And the positive-control law again: a continuity package that has
never survived a takeover test is an UNTESTED CLASS, not a guarantee
— same discipline as UNREADABLE=0 with nothing planted, and the
same as the REPLAY ceiling: continuity claimed is not continuity
demonstrated until the 48h staging-recovery test passes.

Certification states are a state machine (the corpus law again):
QUALIFIED != IN_PROGRESS != CERTIFIED_OTHER. No arrow skipped by
narration — a provider "engaged in the process" may not be sold as
qualified, and a qualification covers a defined service perimeter,
never the vendor's whole catalogue.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

STATUS = "CANDIDATE"

# internal term -> (external term, witness the rename requires)
VOCABULARY = {
    "agent IA": ("application métier", "versioned_release"),
    "bot": ("logiciel", "versioned_release"),
    "swarm": ("moteur d'automatisation", "orchestration_spec"),
    "prompt": ("configuration métier", "config_schema"),
    "memory": ("base de connaissances", "data_control_matrix"),
    "tool calling": ("intégration API", "api_contract"),
    "autonomous agent": ("workflow automatisé", "replayable_runs"),
    "model vendor": ("moteur IA sous-jacent", "llm_gateway"),
    "serveur dédié": ("environnement dédié mono-client",
                      "provisioning_receipt"),
}

CONTINUITY_PACKAGE = ("source_code", "dependency_lockfiles",
                      "dockerfiles", "db_migrations",
                      "infrastructure_as_code", "ci_cd_description",
                      "environment_spec", "build_instructions",
                      "deployment_instructions", "operations_runbook",
                      "sbom", "backup_restore_procedure",
                      "architecture_diagram", "release_checksums")

CERT_STATES = ("QUALIFIED", "IN_PROGRESS", "CERTIFIED_OTHER", "NONE")

KEY_PERSON_LADDER = ("DESIGNED", "IMPLEMENTED", "TESTED",
                     "DEMONSTRATED")

ESCROW_TRIGGERS = ("cessation", "liquidation",
                   "maintenance_interrupted", "persistent_sla_breach",
                   "provider_disappearance")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── renaming is lawful iff the property is witnessed ───────────────────

def rename(internal: str, witnesses: frozenset) -> dict:
    """The vocabulary table with its teeth. Each rename names the
    witness it requires; renaming without it is the seal without the
    admission."""
    if internal not in VOCABULARY:
        return {"ok": False, "reason": "E_UNKNOWN_TERM"}
    external, required = VOCABULARY[internal]
    if required not in witnesses:
        return {"ok": False, "reason": "E_SEAL_WITHOUT_ADMISSION",
                "internal": internal, "blocked_external": external,
                "missing_witness": required,
                "law": "renaming is lawful iff the property is "
                       "witnessed; a vocabulary table without "
                       "witnesses is laundering"}
    return {"ok": True, "internal": internal, "external": external,
            "witness": required,
            "law": "the agentic architecture is an implementation "
                   "detail — like Kubernetes or Redis"}


# ── source recovered !=> application recoverable ───────────────────────

def continuity_package(components: frozenset) -> dict:
    """A repo alone can be unusable. The package is complete or the
    recovery claim is refused."""
    missing = sorted(set(CONTINUITY_PACKAGE) - set(components))
    source_only = components == {"source_code"} or \
        (len(components) <= 2 and "source_code" in components)
    return {"complete": not missing, "missing": tuple(missing),
            "grade": "RECOVERABLE" if not missing else
                     ("SOURCE_ONLY" if source_only else "PARTIAL"),
            "reason": None if not missing
                      else "E_SOURCE_IS_NOT_RECOVERABILITY",
            "law": "source recovered does not entail application "
                   "recoverable"}


def takeover_test(package: dict, executed: bool,
                  staging_recovered: bool, hours: float | None) -> dict:
    """The annual falsifier: founder unavailable 48h, restart a
    staging copy from the continuity package alone. Untested
    continuity is an untested class, not a guarantee."""
    if not package.get("complete"):
        return {"scored": False, "reason": "E_INCOMPLETE_PACKAGE",
                "missing": package.get("missing")}
    if not executed:
        return {"scored": False, "reason": "E_UNTESTED_CONTINUITY",
                "law": "a continuity package that never survived a "
                       "takeover test is a slide, not a dispositif — "
                       "the positive-control law"}
    passed = staging_recovered and hours is not None and hours <= 48
    return {"scored": True, "passed": passed,
            "hours": hours,
            "key_person_risk_reduced": passed,
            "reason": None if passed else "E_TAKEOVER_FAILED"}


def key_person_status(designed: bool, implemented: bool,
                      tested_and_passed: bool) -> dict:
    """'We eliminated single-person dependency' is claimable only at
    DEMONSTRATED. Before the passed test it is 'architected for
    elimination' — no arrow skipped by narration. And the honest
    claim is never 'we are not small': smallness stays true; the
    key person becomes a replaceable operational role."""
    if tested_and_passed:
        state = "DEMONSTRATED"
    elif implemented:
        state = "IMPLEMENTED"
    elif designed:
        state = "DESIGNED"
    else:
        state = "NONE"
    return {"state": state,
            "eliminated_claimable": state == "DEMONSTRATED",
            "honest_claim": "single-person operational dependency "
                            "eliminated" if state == "DEMONSTRATED"
                            else "architected for elimination",
            "smallness_hidden": False,
            "law": "the company may be small; the key person becomes "
                   "a replaceable operational role — that is the "
                   "claim, not headcount"}


# ── escrow release !=> IP transferred ──────────────────────────────────

def escrow_release(trigger: str, conditions_met: bool) -> dict:
    """Release grants source + docs + a continuity license. The
    editor remains the IP owner in every branch — 'if I disappear
    they own the code' is both wrong and worse for the model."""
    if trigger not in ESCROW_TRIGGERS:
        return {"released": False, "reason": "E_UNKNOWN_TRIGGER"}
    if not conditions_met:
        return {"released": False, "trigger": trigger,
                "ip_transferred": False,
                "reason": "E_CONDITIONS_NOT_MET"}
    return {"released": True, "trigger": trigger,
            "grants": ("source", "documentation",
                       "continuity_license_irrevocable"),
            "ip_transferred": False,
            "law": "escrow release does not entail IP transfer; the "
                   "editor remains owner and the beneficiary gains "
                   "continuity rights"}


# ── certification is a state machine with a perimeter ──────────────────

def certification_claim(provider: str, status: str,
                        service_in_scope: bool) -> dict:
    """QUALIFIED may be claimed only for a qualified provider AND a
    service inside the qualified perimeter. IN_PROGRESS sold as
    qualified is a narrative skip; catalogue-wide claims overreach
    the perimeter."""
    if status not in CERT_STATES:
        return {"claimable": False, "reason": "E_UNKNOWN_CERT_STATE"}
    if status != "QUALIFIED":
        return {"claimable": False, "provider": provider,
                "status": status,
                "reason": "E_NARRATIVE_SKIP",
                "sellable_as": status,
                "law": "engaged in the process is not qualified; no "
                       "arrow skipped by narration"}
    if not service_in_scope:
        return {"claimable": False, "provider": provider,
                "reason": "E_CERT_SCOPE_OVERREACH",
                "law": "a qualification covers a defined service "
                       "perimeter, never the vendor's catalogue"}
    return {"claimable": True, "provider": provider,
            "status": "QUALIFIED", "scope": "verified"}


# ── application !=> model vendor ───────────────────────────────────────

def gateway_substitution(vendor_refused: str,
                         gateway_present: bool) -> dict:
    """'We refuse Anthropic' is a policy change, not a rewrite —
    but only if the gateway actually exists."""
    if not gateway_present:
        return {"substitutable": False,
                "reason": "E_HARDCODED_VENDOR",
                "cost": "rewrite",
                "law": "without a gateway the application IS the "
                       "model vendor, whatever the slide says"}
    return {"substitutable": True, "refused": vendor_refused,
            "cost": "gateway_policy_change",
            "law": "Application != ModelVendor"}


def compliance_non_entailment() -> dict:
    """Bedrock's security properties (EU routing, provider-blind
    prompts, EMEA contracting) are good RSSI answers — and none of
    them is AI Act compliance of the application, whose obligations
    depend on the system, the role and the use case."""
    return {"licensed": False,
            "reason": "E_INFRA_SECURITY_IS_NOT_APP_COMPLIANCE",
            "law": "BedrockSecurityProperties != "
                   "AIActComplianceOfYourApplication; transparency "
                   "obligations bind the system in its use case, not "
                   "the pipe"}
