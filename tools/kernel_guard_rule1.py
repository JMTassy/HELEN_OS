#!/usr/bin/env python3
"""kernel_guard RULE 1 — AST-precise ledger-write detection.

Replaces the legacy single-line text-regex scan used by tools/kernel_guard.sh.

Why AST: the regex matched the literal text ``open("...ledger....ndjson", "a")``
anywhere on a line — including when that text appears INSIDE a Python string
literal, comment, or docstring (e.g. a spec/test fixture that deliberately
*quotes* the forbidden pattern so a scanner can be tested against it). Those are
false positives: no ledger write happens. This pass parses each file and only
flags real ``open(<ledger .ndjson literal>, "a"/"w"/...)`` call sites, so:

  * string-literal / comment / docstring occurrences are never flagged, and
  * every real call is still caught — including multi-line open() calls and
    ``io.open(...)`` forms the single-line regex could miss.

The path/mode heuristics mirror the legacy rule exactly (ledger-ish ``.ndjson``
path + append/write mode), so this is strictly more precise, never more
permissive.

Usage:
    kernel_guard_rule1.py <repo_root> [allowed_writer_relpath ...]

Prints one ``[VIOLATION] RULE 1`` block per real violation and a trailing
``RULE1_VIOLATIONS=<n>`` line. Exit 0 if none found, 1 otherwise.

NON_SOVEREIGN tooling · authority=false · no ledger writes.
"""
from __future__ import annotations

import ast
import os
import sys

# Ledger-path markers and write modes — mirror the legacy grep in kernel_guard.sh.
LEDGER_MARKERS = ("ledger", "events", "wisdom", "dialogue", "town")
WRITE_MODES = {"a", "w", "a+", "w+", "ab", "wb", "a+b", "w+b"}


def _is_ledger_path(value: str) -> bool:
    low = value.lower()
    return ".ndjson" in low and any(marker in low for marker in LEDGER_MARKERS)


def _str_const(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _path_arg(call: ast.Call) -> str | None:
    if call.args:
        p = _str_const(call.args[0])
        if p is not None:
            return p
    for kw in call.keywords:
        if kw.arg in ("file", "name"):
            return _str_const(kw.value)
    return None


def _mode_arg(call: ast.Call) -> str | None:
    if len(call.args) >= 2:
        m = _str_const(call.args[1])
        if m is not None:
            return m
    for kw in call.keywords:
        if kw.arg == "mode":
            return _str_const(kw.value)
    return None


def _is_open_call(func: ast.AST) -> bool:
    # Matches builtin open(...) and attribute forms like io.open(...) / os.open is
    # excluded implicitly (os.open uses int flags, never a "a"/"w" string mode).
    if isinstance(func, ast.Name):
        return func.id == "open"
    if isinstance(func, ast.Attribute):
        return func.attr == "open"
    return False


def violations_in(path: str):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
        tree = ast.parse(source, filename=path)
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_open_call(node.func):
            continue
        ledger_path = _path_arg(node)
        mode = _mode_arg(node)
        if ledger_path is None or mode is None:
            continue
        if mode in WRITE_MODES and _is_ledger_path(ledger_path):
            yield node.lineno, ledger_path, mode


def main(argv: list[str]) -> int:
    repo = os.path.abspath(argv[1]) if len(argv) > 1 else os.getcwd()
    allowed = {os.path.normpath(os.path.join(repo, w)) for w in argv[2:]}

    count = 0
    for dirpath, dirnames, filenames in os.walk(repo):
        # Skip hidden dirs (.git, .venv, …) and __pycache__.
        dirnames[:] = [
            d for d in dirnames if not d.startswith(".") and d != "__pycache__"
        ]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            full = os.path.normpath(os.path.join(dirpath, fn))
            if full in allowed:
                continue
            for lineno, ledger_path, mode in violations_in(full):
                rel = os.path.relpath(full, repo)
                print(f"  [VIOLATION] RULE 1: {rel}")
                print(f"    {lineno}:open({ledger_path!r}, {mode!r})")
                count += 1

    print(f"RULE1_VIOLATIONS={count}")
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
