"""
Structural test for HELEN_SURFACE_DOCTRINE_V1.

Validates the doctrine has all required constitutional sections and metadata.
Bind point for doctrine_admission_gate.py receipt_pointer check.
"""
from pathlib import Path

DOCTRINE = Path(__file__).resolve().parents[1] / "docs/proposals/HELEN_SURFACE_DOCTRINE_V1.md"


def test_surface_doctrine_exists():
    assert DOCTRINE.exists(), f"Doctrine file missing: {DOCTRINE}"


def test_surface_doctrine_non_sovereign():
    text = DOCTRINE.read_text()
    assert "NON_SOVEREIGN" in text


def test_surface_doctrine_no_ship():
    text = DOCTRINE.read_text()
    assert "NO_SHIP" in text


def test_surface_doctrine_append_only():
    text = DOCTRINE.read_text().upper()
    assert "APPEND" in text and "ONLY" in text


def test_surface_doctrine_required_sections():
    text = DOCTRINE.read_text()
    required = ["§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8", "§9", "§10"]
    for section in required:
        assert section in text, f"Missing required section {section}"


def test_surface_doctrine_has_open_questions():
    text = DOCTRINE.read_text()
    assert "§8" in text
    assert "Q1" in text


def test_surface_doctrine_receipt_sidecar():
    text = DOCTRINE.read_text()
    assert "sha256:fa3bdcec4ebc89606ce88ead57a736e60cf71765dbcf46d4d8a41e1ec9558970" in text


def test_surface_doctrine_draft_status():
    text = DOCTRINE.read_text()
    assert "DRAFT_V1" in text or "DRAFT" in text
