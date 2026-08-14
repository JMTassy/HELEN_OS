"""Editor doctrine falsified: a rename without its witness is a seal
without an admission; a repo alone is not recoverability; untested
continuity is an untested class; escrow release transfers no IP;
IN_PROGRESS sold as QUALIFIED is a narrative skip; and without a
gateway the application IS the model vendor.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import editor_membrane as em
from editor_membrane import (
    certification_claim,
    compliance_non_entailment,
    continuity_package,
    escrow_release,
    gateway_substitution,
    key_person_status,
    rename,
    takeover_test,
)


# ── renaming is lawful iff the property is witnessed ───────────────────

def test_a_rename_without_its_witness_is_laundering():
    v = rename("agent IA", frozenset())
    assert v["ok"] is False
    assert v["reason"] == "E_SEAL_WITHOUT_ADMISSION"
    assert v["missing_witness"] == "versioned_release"
    assert v["blocked_external"] == "application métier"


def test_a_witnessed_rename_is_lawful():
    v = rename("agent IA", frozenset({"versioned_release"}))
    assert v["ok"] is True
    assert v["external"] == "application métier"


def test_every_vocabulary_row_names_its_witness():
    for internal, (external, witness) in em.VOCABULARY.items():
        assert witness, internal
        assert rename(internal, frozenset())["ok"] is False
        assert rename(internal, frozenset({witness}))["ok"] is True


def test_dedicated_server_becomes_mono_client_environment():
    v = rename("serveur dédié", frozenset({"provisioning_receipt"}))
    assert v["external"] == "environnement dédié mono-client"


def test_an_unknown_term_is_refused():
    assert rename("magic", frozenset())["reason"] == "E_UNKNOWN_TERM"


# ── source recovered !=> application recoverable ───────────────────────

def test_a_repo_alone_is_source_only():
    v = continuity_package(frozenset({"source_code"}))
    assert v["complete"] is False
    assert v["grade"] == "SOURCE_ONLY"
    assert v["reason"] == "E_SOURCE_IS_NOT_RECOVERABILITY"


def test_the_full_package_is_recoverable():
    v = continuity_package(frozenset(em.CONTINUITY_PACKAGE))
    assert v["complete"] is True and v["grade"] == "RECOVERABLE"


def test_the_package_has_fourteen_named_components():
    assert len(em.CONTINUITY_PACKAGE) == 14
    assert "sbom" in em.CONTINUITY_PACKAGE
    assert "operations_runbook" in em.CONTINUITY_PACKAGE


# ── the takeover test is the positive control ──────────────────────────

def _full():
    return continuity_package(frozenset(em.CONTINUITY_PACKAGE))


def test_untested_continuity_is_an_untested_class():
    v = takeover_test(_full(), executed=False,
                      staging_recovered=False, hours=None)
    assert v["scored"] is False
    assert v["reason"] == "E_UNTESTED_CONTINUITY"


def test_an_incomplete_package_cannot_even_be_scored():
    v = takeover_test(continuity_package(frozenset({"source_code"})),
                      executed=True, staging_recovered=True, hours=4)
    assert v["scored"] is False
    assert v["reason"] == "E_INCOMPLETE_PACKAGE"


def test_a_passed_takeover_reduces_key_person_risk():
    v = takeover_test(_full(), True, True, hours=36)
    assert v["passed"] is True
    assert v["key_person_risk_reduced"] is True


def test_a_recovery_slower_than_48h_fails():
    v = takeover_test(_full(), True, True, hours=72)
    assert v["passed"] is False
    assert v["key_person_risk_reduced"] is False


def test_eliminated_is_claimable_only_at_demonstrated():
    before = key_person_status(True, True, tested_and_passed=False)
    assert before["eliminated_claimable"] is False
    assert before["honest_claim"] == "architected for elimination"
    after = key_person_status(True, True, tested_and_passed=True)
    assert after["state"] == "DEMONSTRATED"
    assert after["eliminated_claimable"] is True


def test_smallness_is_never_hidden():
    assert key_person_status(True, True, True)["smallness_hidden"] \
        is False


# ── escrow release !=> IP transfer ─────────────────────────────────────

def test_a_lawful_release_grants_continuity_and_no_ownership():
    v = escrow_release("liquidation", conditions_met=True)
    assert v["released"] is True
    assert "continuity_license_irrevocable" in v["grants"]
    assert v["ip_transferred"] is False


def test_ip_stays_with_the_editor_in_every_branch():
    for trig in em.ESCROW_TRIGGERS:
        for met in (True, False):
            assert escrow_release(trig, met)["ip_transferred"] is False


def test_an_unknown_trigger_is_refused():
    assert escrow_release("bad_quarter", True)["reason"] == \
        "E_UNKNOWN_TRIGGER"


# ── certification is a state machine with a perimeter ──────────────────

def test_in_progress_sold_as_qualified_is_a_narrative_skip():
    v = certification_claim("provider_B", "IN_PROGRESS",
                            service_in_scope=True)
    assert v["claimable"] is False
    assert v["reason"] == "E_NARRATIVE_SKIP"
    assert v["sellable_as"] == "IN_PROGRESS"


def test_a_qualification_never_covers_the_whole_catalogue():
    v = certification_claim("provider_A", "QUALIFIED",
                            service_in_scope=False)
    assert v["claimable"] is False
    assert v["reason"] == "E_CERT_SCOPE_OVERREACH"


def test_qualified_and_in_scope_is_claimable():
    assert certification_claim("provider_A", "QUALIFIED", True)[
        "claimable"] is True


# ── application !=> model vendor ───────────────────────────────────────

def test_without_a_gateway_the_application_is_the_vendor():
    v = gateway_substitution("Anthropic", gateway_present=False)
    assert v["substitutable"] is False
    assert v["reason"] == "E_HARDCODED_VENDOR"
    assert v["cost"] == "rewrite"


def test_with_a_gateway_refusal_is_a_policy_change():
    v = gateway_substitution("Anthropic", gateway_present=True)
    assert v["substitutable"] is True
    assert v["cost"] == "gateway_policy_change"


def test_infra_security_never_entails_app_compliance():
    v = compliance_non_entailment()
    assert v["licensed"] is False
    assert v["reason"] == "E_INFRA_SECURITY_IS_NOT_APP_COMPLIANCE"


def test_deterministic():
    assert em.canon(rename("bot", frozenset({"versioned_release"}))) \
        == em.canon(rename("bot", frozenset({"versioned_release"})))
