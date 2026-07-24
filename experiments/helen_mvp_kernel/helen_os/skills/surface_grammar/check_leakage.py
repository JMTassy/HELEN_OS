"""
check_leakage.py — CSS governance-color leakage detector.

Scans HTML files that declare authority=false for CSS rules that assign
governance-palette tokens (ADMITTED green: #00ff88 / --green / --grn) to
semantic UI-state classes (live, done, committed, shipped, ...).

Source Atlas Doctrine: one meaning per color.
WULMOJI rule: authority=false files must not render ADMITTED green.

NON_SOVEREIGN · authority=false · NO_CLAIM · ledger_effect=none

Usage:
    python check_leakage.py [--root .] [--glob "apps/helen-surface/**/*.html"]
                            [--format json|yaml] [--out path]
    python check_leakage.py --file path/to/file.html
"""
from __future__ import annotations

import argparse
import glob as glob_module
import json
import re
import sys
from pathlib import Path
from typing import Any

from helen_os.skills.surface_grammar.manifest import (
    AUTHORITY_FALSE_PATTERNS,
    GOVERNANCE_GREEN_TOKENS,
    SEMANTIC_STATE_KEYWORDS,
)

# ── CSS extraction ────────────────────────────────────────────────────────────

_STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE)
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_CSS_RULE_RE = re.compile(r"([^{};][^{};]*?)\{([^}]*)\}", re.DOTALL)

# ── Pattern helpers ───────────────────────────────────────────────────────────

_SEMANTIC_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in SEMANTIC_STATE_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

_GOV_GREEN_RE = re.compile(
    "(" + "|".join(re.escape(t) for t in GOVERNANCE_GREEN_TOKENS) + ")",
    re.IGNORECASE,
)


def _has_authority_false(content: str) -> bool:
    return any(p in content for p in AUTHORITY_FALSE_PATTERNS)


def _extract_css_blocks(html: str) -> list[tuple[int, str]]:
    """Return list of (start_char_offset, css_text) for each <style> block."""
    return [(m.start(1), m.group(1)) for m in _STYLE_BLOCK_RE.finditer(html)]


def _char_to_line(html: str, char_offset: int) -> int:
    return html[:char_offset].count("\n") + 1


def _find_violations(html: str, path: str) -> list[dict[str, Any]]:
    if not _has_authority_false(html):
        return []

    violations: list[dict[str, Any]] = []

    for block_offset, css_text in _extract_css_blocks(html):
        css_clean = _CSS_COMMENT_RE.sub(" ", css_text)
        for rule_match in _CSS_RULE_RE.finditer(css_clean):
            selector = rule_match.group(1).strip()
            body = rule_match.group(2)

            if not _SEMANTIC_RE.search(selector):
                continue
            if not _GOV_GREEN_RE.search(body):
                continue

            gov_token = _GOV_GREEN_RE.search(body).group(1)
            semantic_kw = _SEMANTIC_RE.search(selector).group(1).lower()

            rule_char = block_offset + rule_match.start()
            line = _char_to_line(html, rule_char)

            violations.append(
                {
                    "file": str(path),
                    "line": line,
                    "selector": selector,
                    "token": gov_token,
                    "semantic_meaning": semantic_kw,
                    "body_excerpt": body.strip()[:80],
                }
            )

    return violations


# ── Public API ────────────────────────────────────────────────────────────────


def scan_file(path: str | Path) -> list[dict[str, Any]]:
    """Scan a single HTML file and return its violations."""
    content = Path(path).read_text(encoding="utf-8", errors="replace")
    return _find_violations(content, str(path))


def scan_glob(pattern: str, repo_root: str | Path = ".") -> list[dict[str, Any]]:
    """Scan all HTML files matching *pattern* relative to *repo_root*."""
    root = Path(repo_root)
    files = sorted(root.glob(pattern))
    if not files:
        # Try as absolute glob
        files = sorted(Path(f) for f in glob_module.glob(str(root / pattern), recursive=True))

    violations: list[dict[str, Any]] = []
    for f in files:
        violations.extend(scan_file(f))
    return violations


def run(
    path_glob: str = "apps/helen-surface/**/*.html",
    repo_root: str = ".",
    output_format: str = "json",
    out_path: str | None = None,
) -> dict[str, Any]:
    """Full scan run. Returns result dict and optionally writes it to disk."""
    violations = scan_glob(path_glob, repo_root)

    result: dict[str, Any] = {
        "skill_id": "surface_grammar_v1",
        "gate": "check_leakage",
        "authority": False,
        "claim_status": "NO_CLAIM",
        "scanned_glob": path_glob,
        "violation_count": len(violations),
        "violations": violations,
    }

    serialized = _emit(result, output_format)

    if out_path:
        Path(out_path).write_text(serialized, encoding="utf-8")
    else:
        print(serialized)

    return result


# ── Serialisation ─────────────────────────────────────────────────────────────


def _emit(data: dict, fmt: str) -> str:
    if fmt == "yaml":
        try:
            import yaml  # type: ignore[import]
            return yaml.dump(data, sort_keys=False, allow_unicode=True)
        except ImportError:
            print("warning: pyyaml not available — falling back to JSON", file=sys.stderr)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── CLI ───────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSS governance-color leakage detector")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", help="Scan a single HTML file")
    group.add_argument("--glob", default="apps/helen-surface/**/*.html",
                       help="Glob pattern (default: apps/helen-surface/**/*.html)")
    parser.add_argument("--root", default=".", help="Repo root (default: .)")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    parser.add_argument("--out", default=None, help="Write output to this path")
    args = parser.parse_args()

    if args.file:
        violations = scan_file(args.file)
        result = {
            "skill_id": "surface_grammar_v1",
            "gate": "check_leakage",
            "authority": False,
            "claim_status": "NO_CLAIM",
            "scanned_file": args.file,
            "violation_count": len(violations),
            "violations": violations,
        }
        out = _emit(result, args.format)
        if args.out:
            Path(args.out).write_text(out, encoding="utf-8")
        else:
            print(out)
    else:
        run(
            path_glob=args.glob,
            repo_root=args.root,
            output_format=args.format,
            out_path=args.out,
        )
