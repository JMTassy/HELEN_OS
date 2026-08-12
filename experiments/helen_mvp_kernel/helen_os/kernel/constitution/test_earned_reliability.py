"""Earned reliability, falsified: Q_0 = UNKNOWN; self-reports and
unwitnessed exposure count for nothing; evidence accumulates and never
reaches infallibility; TestPass does not entail Trust; Trust never
mints Authority, skips the gate, or passes to an heir; the moat is the
history, not the rules.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import earned_reliability as er
from earned_reliability import (
    Exposure,
    authority_from_trust,
    declare_reputable,
    gate_skip_for_trusted,
    import_history,
    moat,
    proposal_weight,
    receipt_recovers,
    transfer_artifact,
    transfer_trust,
    trust_at,
    trust_from_test_pass,
)


def _survivals(actor, n, witnessed=True, kind="GATE_PASS", t0=0):
    return tuple(Exposure(actor, t0 + i, kind, witnessed)
                 for i in range(n))


# ── Q_0 = UNKNOWN; declaration refused ─────────────────────────────────

def test_reputation_starts_unknown():
    q0 = trust_at("newcomer", (), 0)
    assert q0["grade"] == "UNKNOWN"
    assert q0["evidence"] == 0.0
    assert q0["infallible"] is False


def test_self_declared_reputation_is_refused():
    v = declare_reputable("confident_agent")
    assert v["granted"] is False
    assert v["reason"] == "E_SELF_DECLARED_REPUTATION"


def test_a_hundred_self_reports_still_leave_unknown():
    history = _survivals("boaster", 100, witnessed=True,
                         kind="SELF_REPORT")
    q = trust_at("boaster", history, 200)
    assert q["grade"] == "UNKNOWN"
    assert q["evidence"] == 0.0
    assert q["ignored_self_reports"] == 100


def test_unwitnessed_exposure_contributes_nothing():
    """Witness supremacy applied to reputation: RELAY-grade history
    is not evidence."""
    history = _survivals("ghost", 30, witnessed=False)
    q = trust_at("ghost", history, 100)
    assert q["grade"] == "UNKNOWN"
    assert q["ignored_unwitnessed"] == 30


# ── accumulation: monotone evidence, never infallibility ───────────────

def test_witnessed_survival_accumulates_evidence():
    e5 = trust_at("worker", _survivals("worker", 5), 100)["evidence"]
    e20 = trust_at("worker", _survivals("worker", 20), 100)["evidence"]
    e100 = trust_at("worker", _survivals("worker", 100), 200)["evidence"]
    assert 0.0 < e5 < e20 < e100 < 1.0


def test_even_a_thousand_survivals_are_not_infallibility():
    q = trust_at("veteran", _survivals("veteran", 1000), 2000)
    assert q["evidence"] < 1.0
    assert q["infallible"] is False
    assert "never entails infallibility" in q["law"]


def test_the_fifty_four_year_watch_sets_the_top_grade():
    """The film's own exhibit: fifty-four years of service, still
    passing railroad inspection."""
    assert er.RAILROAD_GRADE_EXPOSURES == 54
    q53 = trust_at("w", _survivals("w", 53), 100)
    q54 = trust_at("w", _survivals("w", 54), 100)
    assert q53["grade"] == "ESTABLISHED"
    assert q54["grade"] == "RAILROAD_GRADE"


def test_a_witnessed_breach_contests_the_record():
    clean = _survivals("mixed", 20)
    breached = clean + (Exposure("mixed", 50, "BREACH", True),)
    qc = trust_at("mixed", clean, 100)
    qb = trust_at("mixed", breached, 100)
    assert qb["grade"] == "CONTESTED"
    assert qb["evidence"] < qc["evidence"]
    assert qb["witnessed_breaches"] == 1


# ── TestPass does not entail Trust ──────────────────────────────────────

def test_a_green_suite_is_instant_not_longitudinal():
    """Including this project's own green suite — named as such."""
    v = trust_from_test_pass(390, probes_held=60)
    assert v["measures"] == "Q_INSTANT"
    assert v["is_good_evidence"] is True
    assert v["entails_longitudinal_trust"] is False


# ── the crucial law: trust never becomes sovereignty ───────────────────

def test_trust_never_mints_authority_even_at_railroad_grade():
    q = trust_at("v", _survivals("v", 200), 300)
    v = authority_from_trust(q)
    assert v["minted"] is False
    assert v["reason"] == "E_REPUTATION_IS_NOT_AUTHORITY"
    assert v["trust_grade_at_refusal"] == "RAILROAD_GRADE"


def test_trust_never_skips_the_gate():
    q = trust_at("v", _survivals("v", 200), 300)
    v = gate_skip_for_trusted(q)
    assert v["skipped"] is False
    assert v["reason"] == "E_TRUST_DOES_NOT_SKIP_THE_GATE"


def test_trust_may_weight_proposals_bounded_and_advisory():
    """The one permitted use — the compost pattern: ordering upstream
    of the gate, never a verdict."""
    q = trust_at("v", _survivals("v", 100), 200)
    w = proposal_weight(q)
    assert 1.0 <= w["weight"] < 2.0
    assert w["advisory_only"] is True
    assert w["affects_admission_verdict"] is False


# ── inheritance: the watch transfers, the reputation does not ──────────

def test_the_artifact_transfers_with_provenance():
    v = transfer_artifact("hamilton_watch",
                          ("grandfather", "father"), "son")
    assert v["transferred"] is True
    assert v["provenance"] == ("grandfather", "father", "son")


def test_trust_is_not_heritable():
    q = trust_at("father", _survivals("father", 60), 100)
    v = transfer_trust(q, "son")
    assert v["transferred"] is False
    assert v["reason"] == "E_TRUST_IS_NOT_HERITABLE"
    assert "Q_0(heir) = UNKNOWN" in v["law"]


def test_borrowed_history_counts_only_if_witnessed_locally():
    events = _survivals("other", 40)
    relayed = import_history(events, witnessed_locally=False)
    seen = import_history(events, witnessed_locally=True)
    assert relayed["events_counted"] == 0
    assert relayed["reason"] == "E_BORROWED_HISTORY"
    assert seen["events_counted"] == 40


# ── the moat and the constitutional watch ──────────────────────────────

def test_the_moat_is_the_history_not_the_rules():
    m = moat()
    assert m["constitution_copyable"] is True
    assert m["verified_history_copyable"] is False
    assert m["ledger_is_not"] == "truth"
    assert "dataset" in m["ledger_is"]


def test_a_receipt_is_a_constitutional_watch_iff_it_recovers_all_three():
    good = receipt_recovers({"what_happened": "TERRITORY_BOUGHT",
                             "under_rule": "exact economics",
                             "with_evidence": "ledger event + price"})
    assert good["is_constitutional_watch"] is True
    bad = receipt_recovers({"what_happened": "something"})
    assert bad["is_constitutional_watch"] is False
    assert bad["missing"] == ["under_rule", "with_evidence"]


def test_the_crosswalk_carries_the_six_hamilton_rows():
    cw = er.HAMILTON_HELEN_CROSSWALK
    assert len(cw) == 6
    assert cw["reputation"] == "earned reliability"
    assert cw["time"] == "adversarial exposure"


def test_deterministic():
    h = _survivals("d", 20) + (Exposure("d", 30, "BREACH", True),)
    assert er.canon(trust_at("d", h, 100)) == \
        er.canon(trust_at("d", h, 100))
    assert er.canon(moat()) == er.canon(moat())
