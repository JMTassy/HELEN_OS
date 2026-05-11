"""
Structural test for HELEN_LAYERED_CANON_V1.

Validates the doctrine has all required constitutional sections and metadata.
Bind point for doctrine_admission_gate.py receipt_pointer check.
"""
from pathlib import Path

DOCTRINE = Path(__file__).resolve().parents[1] / "docs/proposals/HELEN_LAYERED_CANON_V1.md"


def test_layered_canon_doctrine_exists():
    assert DOCTRINE.exists(), f"Doctrine file missing: {DOCTRINE}"


def test_layered_canon_non_sovereign():
    text = DOCTRINE.read_text()
    assert "NON_SOVEREIGN" in text


def test_layered_canon_no_ship():
    text = DOCTRINE.read_text()
    assert "NO_SHIP" in text


def test_layered_canon_append_only():
    text = DOCTRINE.read_text().upper()
    assert "APPEND" in text and "ONLY" in text


def test_layered_canon_required_sections():
    text = DOCTRINE.read_text()
    required = ["§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8", "§9", "§10"]
    for section in required:
        assert section in text, f"Missing required section {section}"


def test_layered_canon_two_repos():
    text = DOCTRINE.read_text()
    assert "helen-conquest" in text
    assert "helen_os_v1" in text


def test_layered_canon_one_way_sync():
    text = DOCTRINE.read_text()
    assert "one-way" in text or "one_way" in text or "canon" in text.lower()


def test_layered_canon_has_open_questions():
    text = DOCTRINE.read_text()
    assert "§8" in text
    assert "Q1" in text or "submodule" in text


def test_layered_canon_receipt_sidecar():
    text = DOCTRINE.read_text()
    assert "sha256:0c9acf951669d47624432daa24c98c2421d75cb5f53520dd39b41386d798c7f1" in text


def test_layered_canon_draft_status():
    text = DOCTRINE.read_text()
    assert "DRAFT_V1" in text or "DRAFT" in text
