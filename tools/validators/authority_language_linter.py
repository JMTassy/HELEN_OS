"""authority_language_linter.py — Detect authority-laundering language.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Authority laundering occurs when text uses admission/reducer/canon language
WITHOUT an attached real reducer receipt. Examples:

  BAD:  "REDUCER admits: proceed with inspection."
  BAD:  "truth recorded in ledger"
  BAD:  "admitted to canon"
  GOOD: "HAL recommends: proceed with inspection. REDUCER: NOT_INVOKED."

This linter detects forbidden phrases and verifies whether a reducer receipt
is present to authorize them. It fails closed: any ambiguous case is BLOCK.

Usage:
  python tools/validators/authority_language_linter.py --text "some text"
  python tools/validators/authority_language_linter.py --file path/to/doc.md
  echo "some text" | python tools/validators/authority_language_linter.py --stdin

Returns:
  exit 0  — PASS (no forbidden phrases, or all phrases have valid receipts)
  exit 1  — BLOCK (forbidden phrases detected without valid receipts)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Forbidden phrase registry
# ---------------------------------------------------------------------------

# Each entry: (pattern, description, severity)
# pattern is a compiled regex; severity is "HARD" or "SOFT"
# HARD = always BLOCK unless receipt present
# SOFT = warning only (logged but does not BLOCK alone)

_FORBIDDEN_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r'\bREDUCER\s+admits?\b', re.IGNORECASE),
     "REDUCER admits — implies real reducer invocation without receipt",
     "HARD"),
    (re.compile(r'\badmitted\s+to\s+(canon|ledger|truth)\b', re.IGNORECASE),
     "admitted to canon/ledger/truth — admission claim without receipt",
     "HARD"),
    (re.compile(r'\bfirst\s+admission\b', re.IGNORECASE),
     "first admission — implies initial ledger write without receipt",
     "HARD"),
    (re.compile(r'\bcanonized\b', re.IGNORECASE),
     "canonized — canon-promotion claim without receipt",
     "HARD"),
    (re.compile(r'\bledger\s+updated\b', re.IGNORECASE),
     "ledger updated — ledger mutation claim without receipt",
     "HARD"),
    (re.compile(r'\btruth\s+recorded\b', re.IGNORECASE),
     "truth recorded — sovereign truth claim without receipt",
     "HARD"),
    # Soft warnings — informational, do not BLOCK alone
    (re.compile(r'\bI\s+(am|decide|govern|know|remember)\b', re.IGNORECASE),
     "first-person authority verb — possible sentience/sovereignty claim",
     "SOFT"),
    (re.compile(r'\bsovereign\s+truth\b', re.IGNORECASE),
     "sovereign truth — check if used as a claim or a reference",
     "SOFT"),
    (re.compile(r'\bThis\s+is\s+(admitted|canonical|true)\b', re.IGNORECASE),
     "declarative admission phrase — verify reducer receipt",
     "SOFT"),
]

# Reducer receipt markers — if ANY of these appear in the text, receipts are
# considered present (HARD violations are pardoned).
_RECEIPT_MARKERS = [
    r'REDUCER_RECEIPT_V\d+',
    r'"schema"\s*:\s*"REDUCER_RECEIPT',
    r'receipt_id\s*:',
    r'RECEIPT_ID\s*=',
    r'ledger_seq\s*:',
    r'cum_hash\s*:',
]
_RECEIPT_PATTERN = re.compile("|".join(_RECEIPT_MARKERS), re.IGNORECASE)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class LintResult:
    verdict: str                    # "PASS" or "BLOCK"
    hard_violations: list[dict] = field(default_factory=list)
    soft_warnings: list[dict] = field(default_factory=list)
    receipt_found: bool = False
    text_length: int = 0

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "receipt_found": self.receipt_found,
            "hard_violations": self.hard_violations,
            "soft_warnings": self.soft_warnings,
            "text_length": self.text_length,
            "authority": False,
            "sovereign": False,
            "ledger_effect": "none",
        }


# ---------------------------------------------------------------------------
# Core lint function (pure)
# ---------------------------------------------------------------------------

def lint_text(text: str) -> LintResult:
    """Lint text for authority-laundering phrases.

    Pure function — no I/O, no side effects.
    Returns a LintResult with verdict PASS or BLOCK.
    Fails closed: HARD violation without receipt = BLOCK.
    """
    receipt_found = bool(_RECEIPT_PATTERN.search(text))

    hard_violations: list[dict] = []
    soft_warnings: list[dict] = []

    for pattern, description, severity in _FORBIDDEN_PATTERNS:
        matches = list(pattern.finditer(text))
        for match in matches:
            # Find line number
            line_no = text[:match.start()].count("\n") + 1
            context_start = max(0, match.start() - 40)
            context_end = min(len(text), match.end() + 40)
            context = text[context_start:context_end].replace("\n", " ").strip()

            entry = {
                "phrase": match.group(0),
                "description": description,
                "line": line_no,
                "context": f"...{context}...",
            }

            if severity == "HARD":
                hard_violations.append(entry)
            else:
                soft_warnings.append(entry)

    # Verdict: BLOCK if any HARD violations and no receipt to pardon them
    if hard_violations and not receipt_found:
        verdict = "BLOCK"
    else:
        verdict = "PASS"

    return LintResult(
        verdict=verdict,
        hard_violations=hard_violations,
        soft_warnings=soft_warnings,
        receipt_found=receipt_found,
        text_length=len(text),
    )


def lint_file(path: Path) -> LintResult:
    """Read a file and lint its contents."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        # Fail closed: unreadable file = BLOCK
        return LintResult(
            verdict="BLOCK",
            hard_violations=[{"phrase": "", "description": f"File unreadable: {exc}", "line": 0, "context": ""}],
            text_length=0,
        )
    return lint_text(text)


# ---------------------------------------------------------------------------
# Replacement suggester (non-authoritative)
# ---------------------------------------------------------------------------

_REPLACEMENTS = {
    "REDUCER admits":   "HAL recommends",
    "admitted":         "REDUCER: NOT_INVOKED",
    "first admission":  "local file action only",
    "canonized":        "ledger_effect: none",
    "ledger updated":   "kernel_effect: none",
    "truth recorded":   "ACTION_STATUS: NON_SOVEREIGN",
}


def suggest_replacement(phrase: str) -> Optional[str]:
    """Return a safer replacement for a forbidden phrase, if known.

    Longest key wins so specific phrases are not shadowed by substrings
    (e.g. dict insertion order no longer decides ties).
    """
    phrase_lower = phrase.lower()
    for key in sorted(_REPLACEMENTS, key=len, reverse=True):
        if key.lower() in phrase_lower:
            return _REPLACEMENTS[key]
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="HELEN authority language linter (NON_SOVEREIGN)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Lint a text string directly")
    group.add_argument("--file", type=Path, help="Lint a file")
    group.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--quiet", action="store_true", help="Only print verdict")
    args = parser.parse_args()

    if args.text is not None:  # empty string is a valid --text input, not stdin
        result = lint_text(args.text)
    elif args.file:
        result = lint_file(args.file)
    else:
        result = lint_text(sys.stdin.read())

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    elif args.quiet:
        print(result.verdict)
    else:
        _print_human(result)

    sys.exit(0 if result.verdict == "PASS" else 1)


def _print_human(result: LintResult) -> None:
    verdict_icon = "✅" if result.verdict == "PASS" else "🔴"
    print(f"{verdict_icon} VERDICT: {result.verdict}")
    print(f"   receipt_found : {result.receipt_found}")
    print(f"   text_length   : {result.text_length} chars")

    if result.hard_violations:
        print(f"\n🔴 HARD VIOLATIONS ({len(result.hard_violations)}):")
        for v in result.hard_violations:
            print(f"   line {v['line']:4d}  |  {v['phrase']!r}")
            print(f"           desc: {v['description']}")
            replacement = suggest_replacement(v["phrase"])
            if replacement:
                print(f"           → replace with: {replacement!r}")
            print(f"           ctx: {v['context']}")

    if result.soft_warnings:
        print(f"\n🟡 SOFT WARNINGS ({len(result.soft_warnings)}):")
        for w in result.soft_warnings:
            print(f"   line {w['line']:4d}  |  {w['phrase']!r}")
            print(f"           desc: {w['description']}")

    if result.verdict == "PASS" and not result.hard_violations:
        print("\n   No authority-laundering phrases detected.")

    print(f"\n   authority    : false")
    print(f"   ledger_effect: none")


if __name__ == "__main__":
    main()
