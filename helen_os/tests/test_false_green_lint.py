"""
Tests for scripts/helen_false_green_lint.py (HELEN_WITNESS_PROJECTION_V1 §5).

Invariant: FG = 0  (false-green tests must be zero)
"""
from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

# Import the scanner internals for unit testing
from scripts.helen_false_green_lint import (
    FalseGreen,
    _count_meaningful_asserts,
    _is_explicitly_skipped,
    _is_fixture,
    scan,
)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _parse_fn(src: str) -> ast.FunctionDef:
    """Parse a function definition string and return the first FunctionDef node."""
    tree = ast.parse(textwrap.dedent(src))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node
    raise ValueError("no function found in source")


# ── Test 1: plain assert → meaningful ────────────────────────────────────────

def test_plain_assert_is_meaningful():
    fn = _parse_fn("""
    def test_foo():
        assert result == 42
    """)
    assert _count_meaningful_asserts(fn) == 1


# ── Test 2: assert True → not meaningful ────────────────────────────────────

def test_assert_true_is_trivial():
    fn = _parse_fn("""
    def test_foo():
        assert True
    """)
    assert _count_meaningful_asserts(fn) == 0


# ── Test 3: pytest.raises → meaningful ───────────────────────────────────────

def test_pytest_raises_counts_as_assertion():
    fn = _parse_fn("""
    def test_foo():
        with pytest.raises(ValueError):
            do_thing()
    """)
    assert _count_meaningful_asserts(fn) == 1


# ── Test 4: pytest.warns → meaningful ────────────────────────────────────────

def test_pytest_warns_counts_as_assertion():
    fn = _parse_fn("""
    def test_foo():
        with pytest.warns(DeprecationWarning):
            do_thing()
    """)
    assert _count_meaningful_asserts(fn) == 1


# ── Test 5: pytest.fail() → meaningful ───────────────────────────────────────

def test_pytest_fail_counts_as_assertion():
    fn = _parse_fn("""
    def test_foo():
        for reason in reasons:
            if "bad" in reason:
                pytest.fail(f"should not appear: {reason}")
    """)
    assert _count_meaningful_asserts(fn) == 1


# ── Test 6: assert_* function call → meaningful ──────────────────────────────

def test_assert_star_function_call_counts():
    fn = _parse_fn("""
    def test_foo():
        assert_prefixed_sha256(hash_val)
    """)
    assert _count_meaningful_asserts(fn) == 1


# ── Test 7: self.assertEqual → meaningful ────────────────────────────────────

def test_unittest_style_assert_counts():
    fn = _parse_fn("""
    def test_foo(self):
        self.assertEqual(result, 42)
        self.assertIn(key, d)
    """)
    assert _count_meaningful_asserts(fn) == 2


# ── Test 8: self.assertRaises → meaningful ───────────────────────────────────

def test_unittest_assert_raises_counts():
    fn = _parse_fn("""
    def test_foo(self):
        with self.assertRaises(ValueError):
            parse_bad_input()
    """)
    # self.assertRaises used as context manager: caught by raises-context check
    assert _count_meaningful_asserts(fn) == 1


# ── Test 9: @pytest.skip decorated → not flagged ─────────────────────────────

def test_skip_decorator_excluded():
    fn = _parse_fn("""
    @pytest.mark.skip(reason="not implemented")
    def test_foo():
        pass
    """)
    assert _is_explicitly_skipped(fn) is True


# ── Test 10: @pytest.fixture decorated → not a test ─────────────────────────

def test_fixture_decorator_excluded():
    fn = _parse_fn("""
    @pytest.fixture
    def test_map():
        return {"key": "value"}
    """)
    assert _is_fixture(fn) is True


# ── Test 11: empty body → false-green ────────────────────────────────────────

def test_empty_body_is_false_green():
    fn = _parse_fn("""
    def test_foo():
        pass
    """)
    assert _count_meaningful_asserts(fn) == 0


# ── Test 12: print-only → false-green ────────────────────────────────────────

def test_print_only_is_false_green():
    fn = _parse_fn("""
    def test_foo():
        result = do_thing()
        print(result)
    """)
    assert _count_meaningful_asserts(fn) == 0


# ── Test 13: scan() on a synthetic tmp directory ─────────────────────────────

def test_scan_detects_false_green_in_tmp(tmp_path):
    """scan() must flag test functions with no meaningful assertions."""
    test_file = tmp_path / "test_synthetic.py"
    test_file.write_text(textwrap.dedent("""
    def test_actually_passes():
        assert 1 + 1 == 2

    def test_false_green():
        result = compute()
        print(result)
    """), encoding="utf-8")

    found = scan(roots=[tmp_path])
    names = [fg.function for fg in found]
    assert "test_false_green" in names
    assert "test_actually_passes" not in names


# ── Test 14: scan() clears on no false-greens ────────────────────────────────

def test_scan_clean_returns_empty(tmp_path):
    """scan() returns empty list when all tests have assertions."""
    test_file = tmp_path / "test_clean.py"
    test_file.write_text(textwrap.dedent("""
    import pytest

    def test_one():
        assert True is True

    def test_two():
        with pytest.raises(ValueError):
            int("not-a-number")
    """), encoding="utf-8")

    found = scan(roots=[tmp_path])
    assert found == []


# ── Test 15: FG invariant on the live repo ───────────────────────────────────

def test_false_green_count_reported(tmp_path):
    """
    Smoke test: scan() on the real test roots runs without exception.
    Result is informational — the invariant (FG==0) is enforced by CI,
    not by this individual test.
    """
    # Just verify the scanner runs without crashing on real files
    from scripts.helen_false_green_lint import _TEST_ROOTS
    existing_roots = [r for r in _TEST_ROOTS if r.exists()]
    if not existing_roots:
        pytest.skip("test roots not present")
    found = scan(roots=existing_roots)
    # Each result must have the required fields
    for fg in found:
        assert isinstance(fg.file, str)
        assert isinstance(fg.function, str)
        assert isinstance(fg.line, int)
        assert isinstance(fg.reason, str)
