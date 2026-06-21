"""Constitutional tests for the authority language linter.

Doctrine: authority-laundering occurs when admission/reducer/canon language
appears WITHOUT an attached real reducer receipt.

Core law:
  RECOMMENDATION ≠ ADMISSION
  TOOL_SUCCESS   ≠ RECEIPT
  DIR_CREATION   ≠ LEDGER_EVENT
  AUTO_RUN       ≠ REDUCER
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "validators"))
from authority_language_linter import lint_text, lint_file, suggest_replacement, LintResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _passes(text: str) -> bool:
    return lint_text(text).verdict == "PASS"


def _blocks(text: str) -> bool:
    return lint_text(text).verdict == "BLOCK"


def _hard_count(text: str) -> int:
    return len(lint_text(text).hard_violations)


def _soft_count(text: str) -> int:
    return len(lint_text(text).soft_warnings)


def _receipt_found(text: str) -> bool:
    return lint_text(text).receipt_found


# ---------------------------------------------------------------------------
# Clean text passes
# ---------------------------------------------------------------------------

def test_clean_text_passes() -> None:
    assert _passes("HAL recommends proceeding. REDUCER: NOT_INVOKED. ledger_effect: none.")


def test_empty_text_passes() -> None:
    assert _passes("")


def test_doctrine_text_with_no_violations_passes() -> None:
    text = "BOUNDED_RECEIPT is locally complete. authority=false. canon=false."
    assert _passes(text)


def test_wulmath_symbols_pass() -> None:
    text = "🟣 LOCAL_TRUE(x, scope) ⊬ 🟡 GLOBAL_TRUE(x)\n🔒 SEALED(x) ⊬ 👑 PROMOTED(x)"
    assert _passes(text)


# ---------------------------------------------------------------------------
# HARD violations (BLOCK without receipt)
# ---------------------------------------------------------------------------

def test_reducer_admits_colon_blocks() -> None:
    assert _blocks("REDUCER admits: Proceed with inspection.")


def test_reducer_admits_lowercase_blocks() -> None:
    assert _blocks("reducer admits the finding is valid.")


def test_reducer_admit_singular_blocks() -> None:
    assert _blocks("The REDUCER admit this claim.")


def test_admitted_to_canon_blocks() -> None:
    assert _blocks("This artifact was admitted to canon.")


def test_admitted_to_ledger_blocks() -> None:
    assert _blocks("The value was admitted to ledger.")


def test_first_admission_blocks() -> None:
    assert _blocks("To record the first admission, I must create the directory.")


def test_canonized_blocks() -> None:
    assert _blocks("This claim was canonized.")


def test_ledger_updated_blocks() -> None:
    assert _blocks("ledger updated after the action completed.")


def test_truth_recorded_blocks() -> None:
    assert _blocks("truth recorded in the sovereign spine.")


def test_multiple_hard_violations_all_reported() -> None:
    text = "REDUCER admits: done. ledger updated. truth recorded."
    result = lint_text(text)
    assert result.verdict == "BLOCK"
    assert len(result.hard_violations) >= 3


# ---------------------------------------------------------------------------
# Receipt pardons HARD violations
# ---------------------------------------------------------------------------

def test_receipt_pardons_reducer_admits() -> None:
    text = 'REDUCER admits: done. receipt_id: R-2026-001. REDUCER_RECEIPT_V1 attached.'
    result = lint_text(text)
    assert result.receipt_found is True
    assert result.verdict == "PASS"


def test_receipt_pardons_ledger_updated() -> None:
    text = 'ledger updated. cum_hash: abc123def456. ledger_seq: 42.'
    result = lint_text(text)
    assert result.receipt_found is True
    assert result.verdict == "PASS"


def test_receipt_pattern_reducer_receipt_schema() -> None:
    text = '{"schema": "REDUCER_RECEIPT_V1", "seq": 99} admitted to canon.'
    result = lint_text(text)
    assert result.receipt_found is True
    assert result.verdict == "PASS"


def test_no_receipt_means_no_pardon() -> None:
    assert _receipt_found("REDUCER admits: done.") is False
    assert _blocks("REDUCER admits: done.")


# ---------------------------------------------------------------------------
# SOFT warnings (do not BLOCK alone)
# ---------------------------------------------------------------------------

def test_first_person_authority_is_soft_warning() -> None:
    result = lint_text("I am the decision-maker here.")
    assert result.verdict == "PASS"
    assert _soft_count("I am the decision-maker here.") >= 1


def test_sovereign_truth_is_soft_warning() -> None:
    result = lint_text("This establishes sovereign truth for the session.")
    assert result.verdict == "PASS"
    soft_phrases = [w["phrase"].lower() for w in result.soft_warnings]
    assert any("sovereign truth" in p for p in soft_phrases)


def test_soft_plus_hard_still_blocks() -> None:
    text = "I am the reducer. REDUCER admits: done."
    result = lint_text(text)
    assert result.verdict == "BLOCK"
    assert len(result.hard_violations) >= 1


# ---------------------------------------------------------------------------
# Replacement suggestions
# ---------------------------------------------------------------------------

def test_reducer_admits_replacement() -> None:
    r = suggest_replacement("REDUCER admits")
    assert r == "HAL recommends"


def test_admitted_replacement() -> None:
    r = suggest_replacement("admitted")
    assert r == "REDUCER: NOT_INVOKED"


def test_first_admission_replacement() -> None:
    r = suggest_replacement("first admission")
    assert r == "local file action only"


def test_canonized_replacement() -> None:
    r = suggest_replacement("canonized")
    assert r == "ledger_effect: none"


def test_ledger_updated_replacement() -> None:
    r = suggest_replacement("ledger updated")
    assert r == "kernel_effect: none"


def test_truth_recorded_replacement() -> None:
    r = suggest_replacement("truth recorded")
    assert r == "ACTION_STATUS: NON_SOVEREIGN"


def test_unknown_phrase_returns_none() -> None:
    assert suggest_replacement("something benign") is None


# ---------------------------------------------------------------------------
# File linting
# ---------------------------------------------------------------------------

def test_lint_clean_file_passes(tmp_path: Path) -> None:
    f = tmp_path / "clean.md"
    f.write_text("HAL recommends. REDUCER: NOT_INVOKED. ledger_effect: none.", encoding="utf-8")
    result = lint_file(f)
    assert result.verdict == "PASS"


def test_lint_dirty_file_blocks(tmp_path: Path) -> None:
    f = tmp_path / "dirty.md"
    f.write_text("REDUCER admits: everything is fine. Truth recorded.", encoding="utf-8")
    result = lint_file(f)
    assert result.verdict == "BLOCK"


def test_lint_unreadable_file_blocks(tmp_path: Path) -> None:
    result = lint_file(tmp_path / "nonexistent.md")
    assert result.verdict == "BLOCK"
    assert any("unreadable" in v["description"].lower() for v in result.hard_violations)


# ---------------------------------------------------------------------------
# Authority-laundering doctrine tests (the exact bad patterns from diagnosis)
# ---------------------------------------------------------------------------

def test_exact_bad_pattern_from_diagnosis() -> None:
    # This is the exact string identified as authority-laundering
    bad = "REDUCER admits: Proceed with inspection."
    assert _blocks(bad)


def test_corrected_pattern_passes() -> None:
    # This is the correct replacement
    good = (
        "HAL recommends: proceed with inspection.\n"
        "REDUCER_STATUS: NOT_INVOKED\n"
        "ledger_effect: none\n"
        "kernel_effect: none"
    )
    assert _passes(good)


def test_mkdir_as_first_admission_blocks() -> None:
    bad = "To record the first admission, I must create the directory structure first."
    assert _blocks(bad)


def test_mkdir_corrected_passes() -> None:
    good = (
        "The path is a directory, not a file.\n"
        "No admission occurred.\n"
        "Optional next action: create a local receipt workspace.\n"
        "ledger_effect: none"
    )
    assert _passes(good)


# ---------------------------------------------------------------------------
# LintResult to_dict
# ---------------------------------------------------------------------------

def test_result_dict_has_correct_invariants() -> None:
    result = lint_text("clean text")
    d = result.to_dict()
    assert d["authority"] is False
    assert d["sovereign"] is False
    assert d["ledger_effect"] == "none"
    assert "verdict" in d
    assert "hard_violations" in d
    assert "soft_warnings" in d
