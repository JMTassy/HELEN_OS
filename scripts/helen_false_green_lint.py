#!/usr/bin/env python3
"""
False-green test detector (HELEN_WITNESS_PROJECTION_V1 §5).

A false-green test is a test function that passes without making any
meaningful assertion. It creates a silent gap in the constitutional
invariant layer — "all green" without evidence.

Exit 0 if no false-green tests found.
Exit 1 if any false-green tests found.
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

_REPO_ROOT = Path(__file__).parent.parent
_TEST_ROOTS = [
    _REPO_ROOT / "helen_os" / "tests",
    _REPO_ROOT / "tests",
]

# Assertion expressions that convey no information
_TRIVIAL_NODES = (ast.Constant,)
_TRIVIAL_VALUES = {True, 1, None}

_SKIP_DECORATORS = {
    "skip", "skipif",           # @pytest.mark.skip / @pytest.mark.skipif
    "xfail",                    # @pytest.mark.xfail
    "pytest.mark.skip",
    "pytest.mark.skipif",
    "pytest.mark.xfail",
    "unittest.skip",
}

# Functions decorated with these are fixtures, not tests — exclude entirely
_FIXTURE_DECORATORS = {"fixture", "pytest.fixture"}

# Attribute names that constitute a meaningful assertion when called or used as context managers.
# pytest.raises / pytest.warns: `with pytest.raises(X):` is a real assertion.
# self.assert*: unittest-style assertion methods.
_RAISES_ATTRS = {"raises", "warns"}
_UNITTEST_ASSERT_PREFIX = "assert"


@dataclass
class FalseGreen:
    file: str
    function: str
    line: int
    reason: str


def _decorator_names(fn: ast.FunctionDef) -> List[str]:
    names = []
    for dec in fn.decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.append(f"{dec.attr}")
            names.append(f"{ast.unparse(dec)}")
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                names.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                names.append(dec.func.attr)
                names.append(ast.unparse(dec.func))
    return names


def _is_explicitly_skipped(fn: ast.FunctionDef) -> bool:
    decorators = _decorator_names(fn)
    return any(d in _SKIP_DECORATORS for d in decorators)


def _is_fixture(fn: ast.FunctionDef) -> bool:
    """True if the function is a pytest fixture (not a test)."""
    decorators = _decorator_names(fn)
    return any(d in _FIXTURE_DECORATORS for d in decorators)


def _is_meaningful_assert(node: ast.Assert) -> bool:
    """True if the assert conveys a real check (not `assert True` or `assert 1`)."""
    test = node.test
    if isinstance(test, _TRIVIAL_NODES) and test.value in _TRIVIAL_VALUES:
        return False
    return True


def _is_raises_context(node: ast.With) -> bool:
    """True if `with pytest.raises(...)` or `with pytest.warns(...)` or similar."""
    for item in node.items:
        ctx = item.context_expr
        if isinstance(ctx, ast.Call) and isinstance(ctx.func, ast.Attribute):
            if ctx.func.attr in _RAISES_ATTRS:
                return True
    return False


def _is_unittest_assert_call(node: ast.Call) -> bool:
    """True if `self.assertX(...)` (unittest-style assertion method)."""
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    attr = func.attr
    return (
        attr.startswith(_UNITTEST_ASSERT_PREFIX)
        and attr != "assert_"          # bare assert_ is not meaningful
        and len(attr) > len(_UNITTEST_ASSERT_PREFIX)
    )


def _is_assert_star_call(node: ast.Call) -> bool:
    """
    True if the call is to a function named `assert_*` — convention for
    functions that raise on failure (e.g. `assert_prefixed_sha256(val)`).
    """
    func = node.func
    if isinstance(func, ast.Name):
        return func.id.startswith("assert_") and len(func.id) > len("assert_")
    if isinstance(func, ast.Attribute):
        return func.attr.startswith("assert_") and len(func.attr) > len("assert_")
    return False


def _is_pytest_fail_call(node: ast.Call) -> bool:
    """True if the call is `pytest.fail(...)` — used as a conditional failure assertion."""
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "fail":
        return True
    if isinstance(func, ast.Name) and func.id == "fail":
        return True
    return False


def _count_meaningful_asserts(fn: ast.FunctionDef) -> int:
    count = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            if _is_meaningful_assert(node):
                count += 1
        elif isinstance(node, ast.With):
            if _is_raises_context(node):
                count += 1
        elif isinstance(node, ast.Call):
            if (_is_unittest_assert_call(node)
                    or _is_assert_star_call(node)
                    or _is_pytest_fail_call(node)):
                count += 1
    return count


def _scan_file(path: Path) -> List[FalseGreen]:
    results: List[FalseGreen] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        # Non-parseable file: report as a probe warning, not a false-green
        print(f"  WARN  cannot parse {path}: {e}", file=sys.stderr)
        return results

    try:
        rel = str(path.relative_to(_REPO_ROOT))
    except ValueError:
        rel = str(path)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        if _is_fixture(node):
            continue
        if _is_explicitly_skipped(node):
            continue

        n_asserts = _count_meaningful_asserts(node)
        if n_asserts == 0:
            results.append(FalseGreen(
                file=rel,
                function=node.name,
                line=node.lineno,
                reason="zero meaningful assert statements",
            ))

    return results


def scan(roots: Optional[List[Path]] = None) -> List[FalseGreen]:
    """Scan test roots and return all false-green test functions."""
    if roots is None:
        roots = _TEST_ROOTS
    found: List[FalseGreen] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("test_*.py")):
            found.extend(_scan_file(path))
    return found


def main() -> None:
    import argparse
    import json as _json

    parser = argparse.ArgumentParser(description="False-green test detector (HELEN §5)")
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Machine-readable JSON output")
    parser.add_argument("--roots", nargs="*", type=Path,
                        help="Override test root directories")
    args = parser.parse_args()

    roots = args.roots if args.roots else None
    found = scan(roots)

    if args.json_out:
        print(_json.dumps({
            "schema_name": "FALSE_GREEN_LINT_V1",
            "false_green_count": len(found),
            "false_green_tests": [
                {"file": fg.file, "function": fg.function,
                 "line": fg.line, "reason": fg.reason}
                for fg in found
            ],
            "invariant_pass": len(found) == 0,
        }, indent=2))
        sys.exit(0 if not found else 1)

    if not found:
        print("FALSE-GREEN LINT: PASS — no false-green tests detected")
        sys.exit(0)

    print(f"FALSE-GREEN LINT: FAIL — {len(found)} false-green test(s) found\n")
    for fg in found:
        print(f"  [{fg.file}:{fg.line}] {fg.function}  ({fg.reason})")
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
