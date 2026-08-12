"""Falsifiers for the daily corpus-scan protocol: the three laws,
container/owner/date discipline, vector scoring, and the end-of-loop
admission gate with its lawful halt. No corpus is scanned; fixtures
are generic.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import daily_scan as ds
from daily_scan import (
    DailyPacket,
    ElementScore,
    ScanElement,
    close_loop,
    coverage_is_deep,
    dedupe_by_content,
    existence_verdict,
    extract_claim,
)


def _el(eid, status="CONTENT_READ", ch="h1", root="r1", street="google_street"):
    return ScanElement(eid, street, container="Marketing 2024", owner="jm",
                       date="2024-06", title="Deck", status=status,
                       source_root=root, content_hash=ch)


# ── TITRE != CONTENU ────────────────────────────────────────────────────

def test_a_claim_cannot_be_extracted_from_a_title():
    listed = _el("e1", status="TITLE_ONLY", ch="")
    r = extract_claim(listed, "UZIK ran the Google brand refresh")
    assert r["verdict"] == "REFUSED"
    assert r["reason"] == "E_TITLE_IS_NOT_CONTENT"


def test_a_claim_from_read_content_is_grounded():
    read = _el("e2", status="CONTENT_READ", ch="abc")
    r = extract_claim(read, "the deck names a 2024 campaign")
    assert r["verdict"] == "CLAIM_EXTRACTED" and r["grounded_in"] == "abc"


def test_read_state_without_content_hash_is_unconstructible():
    with pytest.raises(ValueError, match="E_READ_CLAIM_WITHOUT_CONTENT"):
        ScanElement("e", "google_street", "c", "o", "d", "t",
                    "CONTENT_READ", "root", content_hash="")


# ── CLONE != ORIGINAL ───────────────────────────────────────────────────

def test_three_copies_of_one_artifact_are_one_artifact():
    els = (_el("a", ch="same", root="drive"),
           _el("b", ch="same", root="drive"),
           _el("c", ch="same", root="drive"))
    r = dedupe_by_content(els)
    assert r["artifacts"] == 1 and r["raw_elements"] == 3
    assert r["originals"][0]["copies"] == 3
    assert r["originals"][0]["independent_roots"] == 1
    assert r["originals"][0]["is_corroborated"] is False


def test_same_content_from_two_roots_is_corroborated():
    els = (_el("a", ch="same", root="drive"),
           _el("b", ch="same", root="gmail_attachment"))
    r = dedupe_by_content(els)
    assert r["originals"][0]["independent_roots"] == 2
    assert r["originals"][0]["is_corroborated"] is True


# ── EXISTENCE != PREUVE ─────────────────────────────────────────────────

def test_a_listed_element_proves_only_existence():
    listed = _el("e", status="LISTED", ch="")
    v = existence_verdict(listed)
    assert v["proves"] == "EXISTENCE_ONLY" and v["admissible_claims"] == 0


def test_read_content_can_carry_claims():
    assert existence_verdict(_el("e"))["proves"] == "CONTENT_AVAILABLE"


# ── search discipline ───────────────────────────────────────────────────

def test_keyword_only_coverage_is_shallow():
    r = coverage_is_deep(("by_keyword",))
    assert r["verdict"] == "SHALLOW"
    assert r["reason"] == "E_KEYWORD_ONLY_COVERAGE"
    assert set(r["missing_axes"]) == {"by_container", "by_owner", "by_date"}


def test_container_owner_date_coverage_is_deep():
    r = coverage_is_deep(("by_container", "by_owner", "by_date",
                          "by_keyword"))
    assert r["verdict"] == "DEEP"


# ── scoring is a vector, no scalar collapse ────────────────────────────

def test_high_skill_value_cannot_hide_high_rights_risk():
    s = ElementScore("e", novelty=0.9, confidence=0.8, skill_value=0.95,
                     rights_risk=0.8)
    assert "HIGH_RIGHTS_RISK" in s.flags()
    assert not hasattr(s, "overall")


def test_low_confidence_and_not_new_flags():
    s = ElementScore("e", novelty=0.1, confidence=0.3, skill_value=0.5,
                     rights_risk=0.1)
    assert "LOW_CONFIDENCE" in s.flags() and "NOT_NEW" in s.flags()


# ── end of loop: admission gate + lawful halt ──────────────────────────

_DEEP = coverage_is_deep(("by_container", "by_owner", "by_date"))


def test_a_grounded_packet_is_admissible():
    p = DailyPacket("2026-08-12", "google_street",
                    new_elements=(_el("e1", status="WITNESSED", ch="x"),),
                    new_claims=(("e1", "2024 campaign named", "r1"),),
                    gaps=("owner of container Y unknown",),
                    next_action="read container Y",
                    coverage=_DEEP)
    r = close_loop(p)
    assert r["verdict"] == "PACKET_ADMISSIBLE"
    assert r["new_claims"] == 1


def test_a_claim_citing_an_unread_element_is_rejected():
    p = DailyPacket("2026-08-12", "google_street",
                    new_elements=(_el("e1", status="LISTED", ch=""),),
                    new_claims=(("e1", "invented claim", "r1"),),
                    gaps=(), next_action="x", coverage=_DEEP)
    r = close_loop(p)
    assert r["verdict"] == "REJECTED" and r["reason"] == "E_UNGROUNDED_CLAIM"


def test_shallow_coverage_is_not_a_days_scan():
    p = DailyPacket("2026-08-12", "google_street", (), (), (), "x",
                    coverage=coverage_is_deep(("by_keyword",)))
    assert close_loop(p)["reason"] == "E_SHALLOW_COVERAGE"


def test_nothing_new_halts_lawfully_with_a_reason():
    p = DailyPacket("2026-08-12", "google_street", (), (),
                    gaps=("full read of container Z still pending",),
                    next_action="read container Z tomorrow",
                    coverage=_DEEP)
    r = close_loop(p)
    assert r["verdict"] == "LAWFUL_HALT"
    assert "nothing new" in r["reason"] and r["stated"]


def test_nothing_new_and_no_reason_is_a_silent_halt():
    p = DailyPacket("2026-08-12", "google_street", (), (), (), "",
                    coverage=_DEEP)
    assert close_loop(p)["verdict"] == "E_SILENT_HALT"


# ── the manifest is structure, not fabricated content ──────────────────

def test_the_google_manifest_is_schema_not_data():
    m = ds.GOOGLE_STREET_MANIFEST_SCHEMA
    assert m["status"] == "PRESENCE_OBSERVED_NOT_READ"
    assert m["required_axes"] == ("by_container", "by_owner", "by_date")
    assert "not fabricated here" in m["note"]
    # no owner names, dates, or container contents were invented
    assert "per_source_fields" in m and "skills_to_train_first" in m


def test_deterministic():
    els = (_el("a", ch="same", root="drive"),
           _el("b", ch="same", root="gmail"))
    assert ds.canon(dedupe_by_content(els)) == ds.canon(dedupe_by_content(els))
