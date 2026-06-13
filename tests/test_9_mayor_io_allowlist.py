"""
Constitutional Test 9: Mayor I/O Allowlist

This test enforces that Mayor cannot read UI/Creative/District artifacts
by file I/O, even if they exist on disk.

Test Strategy:
1. AST-scan Mayor source for open() calls
2. Check that any paths opened match allowlist
3. Check that source doesn't contain forbidden hint tokens

Receipt Value:
- Closes loophole: AST import check prevents `import creative`, but
  this prevents `open("ui_event_stream.json")` backdoors
- Enforces "Mayor reads only briefcase + ledger" at I/O level
- Complements test_3 (import purity) with I/O purity

Note:
The strictest enforcement is: Mayor accepts only in-memory objects
(briefcase, attestations, kill_switch_signals) and NEVER opens files.
If your architecture requires Mayor to read ledger by path, add that
path to ALLOWED_OPEN_PREFIXES. Otherwise, set it to empty tuple.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


MAYOR_PATH = Path(__file__).parent.parent / "oracle_town" / "core" / "mayor_v2.py"

# Fail-closed: Mayor can only read explicitly allowed paths.
# Strictest enforcement: () (no file I/O at all)
# If Mayor must read ledger: ("artifacts/ledger.jsonl",)
ALLOWED_OPEN_PREFIXES = (
    # Ideally empty; Mayor should receive objects, not read files
)

# Forbidden tokens (textual hints that Mayor might be reading creative outputs)
FORBIDDEN_HINT_TOKENS = (
    "oracle_town.creative",
    "oracle_town.districts",
    "creative_town",
    "districts/",
    "builder_packet",
    "proposal_envelope",
    "ui_event_stream",
    "ui_stream",
)


def test_mayor_file_exists():
    """Sanity check: Mayor V2 exists"""
    assert MAYOR_PATH.exists(), f"Expected Mayor at {MAYOR_PATH}"


def test_mayor_disallows_open_outside_allowlist():
    """
    Mayor must not call open() on paths outside allowlist.

    This prevents backdoors like:
        with open("ui_event_stream.json") as f:
            data = json.load(f)

    Even if Mayor doesn't import creative/districts, file I/O could
    bypass the import boundary.
    """
    content = MAYOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(content)

    violations = []

    class OpenCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # Detect: open("path", ...)
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if node.args and isinstance(node.args[0], ast.Constant):
                    if isinstance(node.args[0].value, str):
                        path = node.args[0].value
                        allowed = any(path.startswith(p) for p in ALLOWED_OPEN_PREFIXES)
                        if not allowed:
                            violations.append(("open", path, node.lineno))

            # Detect: Path("...").open(...) or Path(...).read_text(...)
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in {"open", "read_text", "read_bytes"}:
                    # Try to extract path from Path() constructor
                    if isinstance(node.func.value, ast.Call):
                        if (isinstance(node.func.value.func, ast.Name) and
                            node.func.value.func.id == "Path"):
                            if node.func.value.args and isinstance(node.func.value.args[0], ast.Constant):
                                if isinstance(node.func.value.args[0].value, str):
                                    path = node.func.value.args[0].value
                                    allowed = any(path.startswith(p) for p in ALLOWED_OPEN_PREFIXES)
                                    if not allowed:
                                        violations.append((node.func.attr, path, node.lineno))

            self.generic_visit(node)

    OpenCallVisitor().visit(tree)

    assert not violations, (
        "CONSTITUTIONAL VIOLATION: Mayor uses file I/O outside allowlist.\n"
        + "\n".join([f"  - line {ln}: {fn}('{p}')" for fn, p, ln in violations])
        + "\n\nMayor must not read UI/Creative/District artifacts directly.\n"
        + "Mayor should receive briefcase + attestations as in-memory objects.\n"
        + f"Allowed prefixes: {ALLOWED_OPEN_PREFIXES if ALLOWED_OPEN_PREFIXES else '(none)'}"
    )


def test_mayor_source_does_not_mention_forbidden_hint_tokens():
    """
    Textual check: Mayor source should not contain hints of creative/UI access.

    This is a cheap secondary check (AST open() scan is primary).
    Catches sloppy patterns like variable names or comments referencing
    creative outputs.

    Note: This is not the primary control. It's a "smoke test" that
    catches obvious violations. AST-based checks are authoritative.
    """
    content = MAYOR_PATH.read_text(encoding="utf-8")
    hits = [tok for tok in FORBIDDEN_HINT_TOKENS if tok in content]

    assert not hits, (
        "CONSTITUTIONAL VIOLATION: Mayor source contains forbidden hint tokens.\n"
        f"Found: {hits}\n\n"
        "Mayor source should not reference Creative Town, Districts, or UI artifacts.\n"
        "If these tokens appear in comments/docstrings explaining the boundary, "
        "that's acceptable but should be reviewed. If they appear in actual code logic, "
        "that's a violation."
    )


def test_mayor_decision_entrypoint_signature():
    """
    Verify Mayor.decide() accepts only allowed parameters.

    Allowed:
    - self (method)
    - briefcase (Briefcase object)
    - attestations (List[Attestation])
    - kill_switch_signals (Optional[List[str]])

    Forbidden:
    - ledger_path (should be passed as object, not path)
    - ui_stream (UI should never influence Mayor)
    - creative_context (Creative outputs should never reach Mayor)
    - builder_packet (Districts output via Concierge → Briefcase only)
    """
    content = MAYOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(content)

    # Find MayorV2.decide() method
    mayor_class = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "MayorV2":
            mayor_class = node
            break

    assert mayor_class is not None, "Could not find MayorV2 class"

    decide_method = None
    for node in mayor_class.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "decide":
            decide_method = node
            break

    assert decide_method is not None, "Could not find decide() method in MayorV2"

    # Extract parameter names
    param_names = [arg.arg for arg in decide_method.args.args]

    # Allowed parameters
    allowed_params = {
        "self",
        "briefcase",
        "attestations",
        "kill_switch_signals",
    }

    # Check for unexpected parameters
    unexpected = [p for p in param_names if p not in allowed_params]

    assert not unexpected, (
        "CONSTITUTIONAL VIOLATION: Mayor.decide() has unexpected parameters.\n"
        f"Found: {param_names}\n"
        f"Unexpected: {unexpected}\n"
        f"Allowed: {sorted(allowed_params)}\n\n"
        "Mayor.decide() must accept only:\n"
        "  - briefcase (Briefcase object with obligations)\n"
        "  - attestations (List[Attestation] from Factory)\n"
        "  - kill_switch_signals (Optional[List[str]])\n\n"
        "Mayor must NOT accept:\n"
        "  - ledger_path (pass ledger as object, not path)\n"
        "  - ui_stream (UI is non-sovereign)\n"
        "  - creative_context (Creative outputs via Translator only)\n"
        "  - builder_packet (Districts via Concierge → Briefcase only)"
    )


def test_mayor_does_not_import_pathlib_open_helpers():
    """
    Mayor should not import file I/O utilities unless necessary.

    If Mayor imports Path, it should only be for type hints, not for
    reading files. This test documents that expectation.
    """
    content = MAYOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(content)

    # Collect imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "pathlib":
                imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pathlib":
                    imports.append("pathlib")

    # Path is acceptable for type hints only. Any other pathlib name is unexpected.
    # (open() call enforcement is in test_mayor_disallows_open_outside_allowlist)
    non_path_imports = set(imports) - {"Path"}
    assert not non_path_imports, (
        f"Mayor imports unexpected names from pathlib: {non_path_imports!r}. "
        "Only 'Path' is permitted (type hints only)."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
