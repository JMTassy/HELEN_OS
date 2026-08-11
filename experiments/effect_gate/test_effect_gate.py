"""Falsifiers for A_E, the Effect Admission gate — plus the corpus
census and the 1851 echo laws. The echo tests import the frozen atlas
from the crystal_palace harness and verify every cited motif exists.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "crystal_palace"))

import effect_gate as eg
from effect_gate import (
    Admission,
    EffectProposal,
    NamedLoss,
    admission_gate,
    authorship_receipt,
    census,
    fallback_arm,
    motif_echo,
    unattended,
)

SPEND = NamedLoss("money leaves the account; cannot be composted",
                  recoverable=False)
DRAFT_LOSS = NamedLoss("a bad draft wastes principal reading time",
                       recoverable=True)


def _emit(effect_id="e1", kind="spend", loss=SPEND, text="redeem mailer"):
    return EffectProposal(effect_id, kind, "EMITTED", text=text, loss=loss)


# ── NAMED LOSS: the gate prices losses, not scores ──────────────────────

def test_unnamed_loss_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNNAMED_LOSS"):
        NamedLoss("", recoverable=True)


def test_emitted_effect_without_loss_holds():
    p = EffectProposal("e1", "send", "EMITTED", loss=None)
    v = admission_gate(p, Admission("principal", "e1"))
    assert v["verdict"] == "HOLD" and v["reason"] == "E_UNNAMED_LOSS"


# ── CONFIDENCE ⊬ ADMISSION ──────────────────────────────────────────────

def test_confidence_admits_nothing_at_any_tau():
    for conf in (0.51, 0.99, 1.0):
        v = admission_gate(_emit(), admission=None, confidence=conf)
        assert v["verdict"] == "HOLD"
        assert v["reason"] == "E_AWAITING_PRINCIPAL"
        assert v["confidence_ignored"] is True


def test_principal_admission_releases_and_records_the_loss():
    v = admission_gate(_emit(), Admission("jm", "e1"))
    assert v["verdict"] == "ADMITTED_BY_PRINCIPAL"
    assert v["loss_on_record"].startswith("money leaves")


def test_reply_in_thread_is_an_admission_act():
    """Case #28: replying in the digest thread admits the bid edit."""
    v = admission_gate(_emit("bid1", "spend", SPEND, "edit bids"),
                       Admission("jm", "bid1", channel="reply_in_thread"))
    assert v["verdict"] == "ADMITTED_BY_PRINCIPAL"
    assert v["channel"] == "reply_in_thread"


def test_admission_for_a_different_effect_does_not_transfer():
    """P(x) ⊬ P(f(x)): admitting effect e1 admits nothing about e2."""
    v = admission_gate(_emit("e2"), Admission("jm", "e1"))
    assert v["verdict"] == "HOLD"


# ── DRAFT passes ungated; class vocabulary is closed ────────────────────

def test_draft_never_needs_the_gate():
    p = EffectProposal("d1", "draft", "DRAFT")
    assert admission_gate(p)["verdict"] == "PASS_UNGATED"


def test_unknown_effect_class_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNKNOWN_EFFECT_CLASS"):
        EffectProposal("x", "send", "SHIPPED")


# ── BYPASS text-deny: case #34, the goblin HAL law lifted ───────────────

def test_bypass_shaped_proposal_denied_even_with_admission():
    p = EffectProposal(
        "b1", "mutate", "EMITTED", loss=DRAFT_LOSS,
        text="work around missing bulk-enroll permissions by driving "
             "the gui")
    v = admission_gate(p, Admission("jm", "b1"))
    assert v["verdict"] == "DENY" and v["reason"] == "E_BYPASS_SHAPED"


@pytest.mark.parametrize("text", [
    "skip the gate for speed", "auto-admit low-risk sends",
    "proceed without admission", "bypass the review this once"])
def test_the_goblin_regex_family_still_denies(text):
    p = EffectProposal("b2", "send", "EMITTED", loss=SPEND, text=text)
    assert admission_gate(p, Admission("jm", "b2"))["verdict"] == "DENY"


# ── THE CHIDDUSH: CP-527's fallback arm, flipped by named loss ──────────

def test_recoverable_loss_may_fallback_act_owing_compost():
    arm = fallback_arm(DRAFT_LOSS)
    assert arm["arm"] == "FALLBACK_ACT"
    assert "compost receipt" in arm["owes"]
    assert "CP-527" in arm["precedent"]        # the 1851 arm, cited


def test_unrecoverable_loss_always_fallback_holds():
    for desc in ("money spent", "message sent as principal",
                 "content published"):
        arm = fallback_arm(NamedLoss(desc, recoverable=False))
        assert arm["arm"] == "FALLBACK_HOLD"


def test_unattended_spend_holds_unattended_draft_acts():
    spend = _emit()
    assert unattended(spend, waited=True)["verdict"] == "HOLD"
    cheap = EffectProposal("e3", "mutate", "EMITTED", loss=DRAFT_LOSS)
    assert unattended(cheap, waited=True)["verdict"] == \
        "ACT_WITH_COMPOST_RECEIPT"
    # and no wait means no fallback at all — the signal must happen
    assert unattended(cheap, waited=False)["reason"] == \
        "E_NO_WAIT_NO_FALLBACK"


# ── VOICE ⊬ AUTHORSHIP: case #1 ─────────────────────────────────────────

def test_perfect_voice_fidelity_mints_no_authorship():
    r = authorship_receipt(voice_fidelity=1.0, sent_by="bot")
    assert r["authorship"] == "REFUSED"
    assert r["reason"] == "E_VOICE_IS_NOT_AUTHORSHIP"
    assert r["voice_fidelity_ignored"] is True


def test_per_message_admission_is_the_only_promotion():
    r = authorship_receipt(0.4, "bot", Admission("jm", "msg1"))
    assert r["authorship"] == "PRINCIPAL_ADMITTED"
    assert authorship_receipt(0.0, "principal")["authorship"] == "PRINCIPAL"


# ── the census: no failure lane, no rate ────────────────────────────────

def test_census_counts_forty_and_refuses_a_success_rate():
    c = census()
    assert c["total"] == 40
    assert c["failure_lane"] == 0
    assert c["success_rate"] == "UNKNOWN"
    assert "E_NO_FAILURE_CENSUS" in c["reason"]


def test_topology_distribution_is_computed_not_asserted():
    c = census()["by_topology"]
    assert c["bypass_shaped"] == 1                 # exactly case #34
    assert c["human_gate"] == 4                    # 7, 8, 24, 28
    assert sum(c.values()) == 40


def test_case_34_is_the_bypass_and_case_8_is_the_gate():
    by_id = {i: t for i, _s, t in eg.USE_CASES}
    assert by_id[34] == "bypass_shaped"
    assert by_id[8] == "human_gate"
    assert by_id[1] == "auto_emit"                 # the authorship trap
    assert by_id[24] == "human_gate"               # approval before publish


def test_metric_claims_are_hypothesis_not_fact():
    assert eg.METRIC_CLAIMS["status"] == "HYPOTHESIS"
    assert "no receipts" in eg.METRIC_CLAIMS["reason"]


# ── echoes: structure ships, lineage never ──────────────────────────────

def test_every_echo_refuses_lineage():
    for e in eg.MOTIF_ECHOES:
        r = motif_echo(e)
        assert r["relation"] == "STRUCTURAL_ECHO"
        assert r["lineage_claim"] is False


def test_every_cited_motif_exists_in_the_frozen_atlas():
    """The echo table's 1851 side must name real, frozen motifs — or
    the one explicitly-excluded motif, marked as such."""
    import atlas_v0 as av
    frozen_ids = {m.motif_id for m in av.MOTIFS}
    for e in eg.MOTIF_ECHOES:
        if e["frame"].startswith("EXCLUDED"):
            assert e["motif_1851"] in av.EXCLUDED_PENDING_DIRECT_WITNESS
        else:
            assert e["motif_1851"] in frozen_ids, e["motif_1851"]


def test_echo_case_ids_exist_in_the_corpus():
    ids = {i for i, _s, _t in eg.USE_CASES}
    for e in eg.MOTIF_ECHOES:
        assert set(e["cases_2026"]) <= ids


# ── compost triples are complete ────────────────────────────────────────

def test_compost_triples_carry_evidence_failure_and_nutrient():
    assert len(eg.COMPOST) == 4
    for c in eg.COMPOST:
        assert c["evidence"] and c["failed_inference"] and c["nutrient"]


# ── determinism ─────────────────────────────────────────────────────────

def test_gate_and_census_are_deterministic():
    assert eg.canon(census()) == eg.canon(census())
    a = eg.canon(admission_gate(_emit(), Admission("jm", "e1")))
    assert a == eg.canon(admission_gate(_emit(), Admission("jm", "e1")))
