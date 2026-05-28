"""
Structural test for HELEN_LANGUAGE_LAYERS_V1.

Validates the doctrine has all required constitutional sections and metadata.
Bind point for doctrine_admission_gate.py receipt_pointer check.
"""
from pathlib import Path

DOCTRINE = Path(__file__).resolve().parents[1] / "docs/proposals/HELEN_LANGUAGE_LAYERS_V1.md"


def test_language_layers_doctrine_exists():
    assert DOCTRINE.exists(), f"Doctrine file missing: {DOCTRINE}"


def test_language_layers_non_sovereign():
    text = DOCTRINE.read_text()
    assert "NON_SOVEREIGN" in text


def test_language_layers_no_ship():
    text = DOCTRINE.read_text()
    assert "NO_SHIP" in text


def test_language_layers_append_only():
    text = DOCTRINE.read_text().upper()
    assert "APPEND" in text and "ONLY" in text


def test_language_layers_required_sections():
    text = DOCTRINE.read_text()
    required = ["§1", "§2", "§3", "§4", "§5", "§6", "§7"]
    for section in required:
        assert section in text, f"Missing required section {section}"


def test_language_layers_mapping_table():
    text = DOCTRINE.read_text()
    # 1:1 mapping table must exist with at least surface↔constitutional pairs
    assert "saved" in text or "receipt" in text
    assert "§2" in text


def test_language_layers_has_open_questions():
    text = DOCTRINE.read_text()
    assert "§5" in text  # open questions section
    assert "Q1" in text or "color" in text or "i18n" in text


def test_language_layers_receipt_sidecar():
    text = DOCTRINE.read_text()
    assert "sha256:dbd254370525087179876bd5dcb121b9f44e7261f9b12d1bca0823f3e5212bd0" in text


def test_language_layers_draft_status():
    text = DOCTRINE.read_text()
    assert "DRAFT_V1" in text or "DRAFT" in text
