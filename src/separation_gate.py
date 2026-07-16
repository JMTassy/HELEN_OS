"""G_σ — Organ Separation Gate.

Six falsifiable predicates that together prove the Digital Metabolism
doctrine's separation laws hold in the current codebase.

Run:  python3 src/separation_gate.py
      .venv/bin/pytest tests/test_sigma_gate.py

authority=false · non-sovereign · no ledger writes
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import NamedTuple

REPO = Path(__file__).resolve().parent.parent


class SigmaResult(NamedTuple):
    name: str
    passed: bool
    seam: str
    detail: str


def _calls_name(tree: ast.AST, name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == name:
                return True
            if isinstance(f, ast.Attribute) and f.attr == name:
                return True
    return False


def _imports_module(tree: ast.AST, name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == name or (alias.asname or "") == name:
                    return True
        if isinstance(node, ast.ImportFrom):
            if (node.module or "") == name:
                return True
    return False


def sigma1_triage_cannot_consume() -> SigmaResult:
    """TRIAGE CANNOT CONSUME: autoresearch_scanner.py must not call mark()."""
    path = REPO / "temple" / "autoresearch" / "autoresearch_scanner.py"
    tree = ast.parse(path.read_text())
    violation = _calls_name(tree, "mark")
    return SigmaResult(
        name="σ₁",
        passed=not violation,
        seam="autoresearch_scanner.py ⊬ mark()",
        detail="ok" if not violation else "VIOLATION: scanner calls mark()",
    )


def sigma2_surface_cannot_mark() -> SigmaResult:
    """SURFACE CANNOT MARK: build_warren_home.py must not call mark()."""
    path = REPO / "apps" / "goblin-warren" / "build_warren_home.py"
    tree = ast.parse(path.read_text())
    violation = _calls_name(tree, "mark")
    return SigmaResult(
        name="σ₂",
        passed=not violation,
        seam="build_warren_home.py ⊬ mark()",
        detail="ok" if not violation else "VIOLATION: surface builder calls mark()",
    )


def sigma3_proposer_neq_validator() -> SigmaResult:
    """PROPOSER ≠ VALIDATOR: surface builder must not import this gate."""
    path = REPO / "apps" / "goblin-warren" / "build_warren_home.py"
    tree = ast.parse(path.read_text())
    violation = _imports_module(tree, "separation_gate")
    return SigmaResult(
        name="σ₃",
        passed=not violation,
        seam="build_warren_home.py ⊬ import separation_gate",
        detail="ok" if not violation else "VIOLATION: builder imports validator (self-certification)",
    )


def sigma4_hal_neq_builder() -> SigmaResult:
    """HAL ≠ BUILDER: surface builder must not call run_gate() or any sigma function."""
    path = REPO / "apps" / "goblin-warren" / "build_warren_home.py"
    tree = ast.parse(path.read_text())
    calls_run_gate = _calls_name(tree, "run_gate")
    calls_sigma = any(_calls_name(tree, f"sigma{i}") for i in range(1, 7))
    violation = calls_run_gate or calls_sigma
    return SigmaResult(
        name="σ₄",
        passed=not violation,
        seam="build_warren_home.py ⊬ run_gate()/sigma*()",
        detail="ok" if not violation else "VIOLATION: builder calls gate or sigma fn",
    )


def sigma5_dreamt_neq_claimed() -> SigmaResult:
    """DREAMT ≠ CLAIMED: every consumption log entry must carry authority=false."""
    log_path = REPO / "temple" / "autoresearch" / "consumption_log.ndjson"
    if not log_path.exists():
        return SigmaResult(
            name="σ₅",
            passed=True,
            seam="consumption_log.ndjson entries authority=false",
            detail="no log present — vacuously true",
        )
    violations: list[str] = []
    for i, raw in enumerate(log_path.read_text().splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if entry.get("authority") is not False:
            violations.append(f"line {i}: authority={entry.get('authority')!r}")
    passed = not violations
    return SigmaResult(
        name="σ₅",
        passed=passed,
        seam="consumption_log.ndjson entries authority=false",
        detail="ok" if passed else "VIOLATION: " + "; ".join(violations),
    )


def sigma6_render_neq_state() -> SigmaResult:
    """RENDER ≠ STATE: render_js() must not assert admission for authority=false payload."""
    path = REPO / "apps" / "goblin-warren" / "build_warren_home.py"
    pen_path = REPO / "temple" / "autoresearch"
    sys.path.insert(0, str(path.parent))
    sys.path.insert(0, str(pen_path))
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_build_warren_home", path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        payload = {
            "schema": "WARREN_HOME_DATA_V1",
            "authority": False,
            "admission": "NO_RECEIPT",
            "dreams": [],
            "carnet": [],
        }
        js = mod.render_js(payload)
        violation = "IS ADMITTED" in js
        return SigmaResult(
            name="σ₆",
            passed=not violation,
            seam="render_js() ⊬ IS ADMITTED for authority=false",
            detail="ok" if not violation else "VIOLATION: render_js() emits 'IS ADMITTED'",
        )
    except Exception as exc:
        return SigmaResult(
            name="σ₆",
            passed=False,
            seam="render_js() ⊬ IS ADMITTED for authority=false",
            detail=f"ERROR: {exc}",
        )
    finally:
        sys.path.pop(0)
        sys.path.pop(0)


def run_gate() -> tuple[bool, list[SigmaResult]]:
    results = [
        sigma1_triage_cannot_consume(),
        sigma2_surface_cannot_mark(),
        sigma3_proposer_neq_validator(),
        sigma4_hal_neq_builder(),
        sigma5_dreamt_neq_claimed(),
        sigma6_render_neq_state(),
    ]
    passed = all(r.passed for r in results)
    return passed, results


def report(results: list[SigmaResult]) -> str:
    lines = []
    for r in results:
        icon = "✅" if r.passed else "❌"
        lines.append(f"{icon} {r.name} [{r.seam}] — {r.detail}")
    failing = [r.seam for r in results if not r.passed]
    overall = "PASS" if not failing else "FAIL seams: " + ", ".join(failing)
    lines.append(f"\nG_σ = {overall}")
    return "\n".join(lines)


if __name__ == "__main__":
    ok, results = run_gate()
    print(report(results))
    sys.exit(0 if ok else 1)
