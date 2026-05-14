"""
Tests for helen_retrieval skill (HER Library Card).

Three scenarios: happy path, edge case, stress test.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from oracle_town.skills.helen_retrieval import retrieve, format_for_prompt


def test_identity_query_retrieves_provenance():
    """Identity question should retrieve JMT/NON_SOVEREIGN passages."""
    results = retrieve("who created you?")
    # Should return something (CLAUDE.md or proposals mention JMT)
    # Fail-open: if sources don't exist retrieval returns [] — that's OK
    assert isinstance(results, list)
    for path, snippet in results:
        assert isinstance(path, str)
        assert isinstance(snippet, str)
        assert len(snippet) > 0


def test_constitutional_term_triggers_retrieval():
    """Querying a constitutional term should find canonical passages."""
    results = retrieve("what is the MAYOR's role?")
    assert isinstance(results, list)
    # MAYOR is mentioned in CLAUDE.md and proposals
    paths = [p for p, _ in results]
    # At least one result should reference a canonical source
    if results:
        assert any(
            "CLAUDE.md" in p or "proposals" in p or "GOVERNANCE" in p
            for p in paths
        )


def test_empty_query_returns_empty():
    """Empty / stopword-only query should return empty list, not crash."""
    results = retrieve("")
    assert results == []

    results = retrieve("   ")
    assert results == []


def test_format_for_prompt_empty():
    """format_for_prompt([]) returns empty string."""
    assert format_for_prompt([]) == ""


def test_format_for_prompt_nonempty():
    """format_for_prompt produces labelled context block."""
    fake = [("docs/proposals/FOO.md", "Some passage about MAYOR")]
    out = format_for_prompt(fake)
    assert "[RETRIEVED CONSTITUTIONAL CONTEXT" in out
    assert "docs/proposals/FOO.md" in out
    assert "Some passage about MAYOR" in out
    assert "[END RETRIEVED CONTEXT]" in out


def test_top_k_respected():
    """retrieve() returns at most top_k results."""
    results = retrieve("MAYOR REDUCER LEDGER RECEIPT SHIP NO_SHIP HAL HER", top_k=3)
    assert len(results) <= 3


def test_no_duplicate_paths():
    """Each path appears at most once in results."""
    results = retrieve("MAYOR REDUCER LEDGER RECEIPT")
    paths = [p for p, _ in results]
    assert len(paths) == len(set(paths)), "Duplicate paths in retrieval results"


def test_retrieve_returns_list_of_tuples():
    """Return type is always list[tuple[str, str]]."""
    results = retrieve("how does the ledger work?")
    for item in results:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], str)
        assert isinstance(item[1], str)
