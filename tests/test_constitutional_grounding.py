"""
Test the helen_constitutional_grounding skill against the three-scenario
discipline: happy path, edge case, stress test.

Bound to oracle_town/skills/helen_constitutional_grounding/SKILL.md.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "oracle_town/skills/helen_constitutional_grounding"))

from ground import ground


def test_blocks_her_high_efficiency_runtime():
    text = "HER (High-Efficiency Runtime) manages execution."
    result, violations = ground(text)
    assert result is None
    assert any("High-Efficiency Runtime" in v for v in violations)


def test_blocks_hal_hardware_abstraction_layer():
    text = "HAL (Hardware Abstraction Layer) abstracts hardware."
    result, violations = ground(text)
    assert result is None
    assert any("Hardware Abstraction Layer" in v for v in violations)


def test_blocks_helen_remembers():
    text = "Helen remembers everything across sessions."
    result, violations = ground(text)
    assert result is None


def test_blocks_merkle_patricia_trie():
    text = "The ledger is a Sparse Merkle-Patricia trie."
    result, violations = ground(text)
    assert result is None


def test_blocks_multi_sig_governance():
    text = "Policy updates require multi-signature governance approval."
    result, violations = ground(text)
    assert result is None


def test_blocks_powershell_helen_full_confabulation():
    """The actual 2026-05-11 PowerShell Helen output — fail-closed regression test."""
    text = (
        "HELEN OS uses HER (High-Efficiency Runtime) and HAL (Hardware Abstraction Layer) "
        "to manage execution. The ledger is a Sparse Merkle-Patricia trie. "
        "Multi-signature governance ensures consensus."
    )
    result, violations = ground(text)
    assert result is None
    assert len(violations) >= 3  # HER, HAL, Merkle-Patricia, multi-sig


def test_happy_path_grounded_query():
    text = "REDUCER admits doctrine proposals. MAYOR signs the ledger."
    result, citations = ground(text)
    assert result is not None
    assert "Provenance" in result
    assert any("REDUCER" in c for c in citations)
    assert any("MAYOR" in c for c in citations)


def test_non_constitutional_passthrough():
    text = "The weather is nice today and the deployment succeeded."
    result, citations = ground(text)
    assert result == text  # unchanged
    assert citations == []


def test_grounded_terms_get_citations():
    text = "The ledger is hash-chained."
    result, citations = ground(text)
    assert result is not None
    assert "ledger" in result.lower()
    assert any("LEDGER" in c or "ledger" in c.lower() for c in citations)


def test_inverted_form_also_blocked():
    """Catch 'Hardware Abstraction Layer (HAL)' as well as 'HAL (Hardware Abstraction Layer)'."""
    text = "Hardware Abstraction Layer (HAL) translates hardware events."
    result, violations = ground(text)
    assert result is None


def test_blocks_created_by_google_identity_leak():
    """Regression on the actual localhost:5001 Helen output (2026-05-11 screenshot)."""
    text = "I am HELEN, an AI companion created by Google. It's lovely to meet you!"
    result, violations = ground(text)
    assert result is None
    assert any("created by" in v.lower() or "identity leak" in v.lower() for v in violations)


def test_blocks_i_am_gemini_identity_leak():
    """The model declaring itself by vendor name."""
    text = "I am Gemini, your AI assistant."
    result, violations = ground(text)
    assert result is None


def test_blocks_i_am_an_ai_made_by_openai():
    """Generic 'I am an AI made by X' identity leak."""
    text = "I am an AI assistant made by OpenAI."
    result, violations = ground(text)
    assert result is None


def test_passes_legitimate_helen_introspection():
    """When HELEN correctly identifies herself, grounding should allow it."""
    text = "HELEN OS was created by JMT. The underlying inference model is non-sovereign."
    result, citations = ground(text)
    assert result is not None  # not blocked
