#!/usr/bin/env python3
"""helen_intensity_floor_lint.py — INTENSITY_IS_NOT_TRUTH enforcement.

Defensive lint per SACRED_PATTERN_EXTRACTION_META_ANALYSIS_V1 §11
(SACRED_KEYWORD_QUARANTINE) + §12 RULE 2 (TEMPLE_KEYWORD_FENCE).

Operating principle (operator-locked candidate doctrine):
  "High signal pressure increases care, not confidence."

Operational invariant (T6, loosened 2026-04-27):
  An artifact containing any sacred-quarantine keyword from the locked list
  may be promoted past lifecycle RAW_SOURCE ONLY IF it explicitly declares
  one of:
    canon: NO_SHIP                (acknowledges it can never become canon)
    boundary_breach_check: true   (acknowledges review is required)
    authority: NON_SOVEREIGN      (logically stronger: no authority at all,
                                   therefore no canonical authority either)
  in its frontmatter.

  Otherwise the lint emits INTENSITY_FLOOR_VIOLATED.

Sacred-keyword list (operator-locked; do not modify without explicit
operator routing):
  transcend, sentient, ascension, divine, prophecy, truth, canon,
  doctrine, sacred, holy, awakening, eternal, infinite, One

Matching:
  - All keywords match case-insensitively EXCEPT 'One', which matches
    only \\bOne\\b (capital O, word boundary).
  - Keyword presence is detected in the FILE BODY (everything after the
    frontmatter block). Frontmatter values are not scanned, so 'canon: NO_SHIP'
    in frontmatter does not self-trigger.

Scope (default):
  helen_os/knowledge/**/*.md
  temple/subsandbox/aura/grimoire/**/*.md

Optional target args:
  Pass one or more paths (file or directory) to lint a subset.

Read-only. Walks files; never mutates anything. No promotion path.

Exit:
  0  PASS  no violations
  1  FAIL  any violation
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

SACRED_KEYWORDS_CI = [
    "transcend", "sentient", "ascension", "divine",
    "prophecy", "truth", "canon", "doctrine",
    "sacred", "holy", "awakening", "eternal", "infinite",
]
SACRED_KEYWORD_ONE = "One"

NON_RAW_LIFECYCLES = {
    "DRAFT", "DRAFT_READING", "CLASSIFIED_SYMBOL", "CLASSIFIED",
    "RECEIPT_CANDIDATE", "ACTIVE", "ADMITTED", "CANONICAL",
}

DEFAULT_ROOTS = [
    Path("helen_os/knowledge"),
    Path("temple/subsandbox/aura/grimoire"),
]

FRONTMATTER_YAML = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FRONTMATTER_FENCED = re.compile(r"```[a-zA-Z0-9_]*\s*\n(.*?)\n```", re.DOTALL)

KEYWORD_PATTERNS_CI = [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE)
                       for k in SACRED_KEYWORDS_CI]
KEYWORD_PATTERN_ONE = re.compile(rf"\b{re.escape(SACRED_KEYWORD_ONE)}\b")


def split_frontmatter(text: str) -> tuple[Optional[str], str]:
    """Return (frontmatter_block, body) where body excludes the matched
    frontmatter region. If no frontmatter detected, returns (None, full text)."""
    m_yaml = FRONTMATTER_YAML.match(text)
    if m_yaml:
        return m_yaml.group(1), text[m_yaml.end():]
    head_chars = "\n".join(text.split("\n")[:80])
    m_fenced = FRONTMATTER_FENCED.search(head_chars)
    if m_fenced:
        end_in_text = m_fenced.end()
        return m_fenced.group(1), text[end_in_text:]
    return None, text


def parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw in block.split("\n"):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//"):
            continue
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*?)(?:\s+#.*)?$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            fields[key] = val
    return fields


def find_sacred_keywords(body: str) -> list[str]:
    found: list[str] = []
    for kw, pat in zip(SACRED_KEYWORDS_CI, KEYWORD_PATTERNS_CI):
        if pat.search(body):
            found.append(kw)
    if KEYWORD_PATTERN_ONE.search(body):
        found.append(SACRED_KEYWORD_ONE)
    return found


def has_canon_no_ship(fields: dict[str, str]) -> bool:
    val = fields.get("canon") or fields.get("Canon") or ""
    return val.strip().split()[0].upper() == "NO_SHIP" if val else False


def has_boundary_breach_check(fields: dict[str, str]) -> bool:
    val = fields.get("boundary_breach_check") or ""
    return val.strip().lower() == "true"


def has_non_sovereign_authority(fields: dict[str, str]) -> bool:
    val = fields.get("authority") or fields.get("Authority") or ""
    return val.strip().split()[0].upper() == "NON_SOVEREIGN" if val else False


def classify(text: str) -> tuple[str, str]:
    """Return (verdict, detail).

    verdict in:
      OK                          (no sacred keywords OR exempt)
      NO_FRONTMATTER              (skipped)
      RAW_PASS                    (sacred keywords present but lifecycle is RAW)
      INTENSITY_FLOOR_VIOLATED    (keywords + non-RAW + no exemption)
    """
    block, body = split_frontmatter(text)
    if block is None:
        return ("NO_FRONTMATTER", "no frontmatter detected (skipped)")
    fields = parse_fields(block)
    keywords = find_sacred_keywords(body)
    if not keywords:
        return ("OK", "")
    lifecycle_raw = fields.get("lifecycle") or fields.get("Lifecycle") or ""
    lifecycle_token = lifecycle_raw.split()[0].upper() if lifecycle_raw else ""
    if lifecycle_token not in NON_RAW_LIFECYCLES:
        return ("RAW_PASS",
                f"sacred keywords {keywords} present but lifecycle={lifecycle_token or 'absent'}")
    if (has_canon_no_ship(fields)
            or has_boundary_breach_check(fields)
            or has_non_sovereign_authority(fields)):
        return ("OK", "")
    exemptions_seen = []
    if "canon" in fields or "Canon" in fields:
        cv = fields.get("canon") or fields.get("Canon") or ""
        exemptions_seen.append(f"canon={cv}")
    if "boundary_breach_check" in fields:
        exemptions_seen.append(f"boundary_breach_check={fields['boundary_breach_check']}")
    if "authority" in fields or "Authority" in fields:
        av = fields.get("authority") or fields.get("Authority") or ""
        exemptions_seen.append(f"authority={av}")
    detail = (f"lifecycle={lifecycle_token}, sacred keywords {keywords}, "
              f"no canon: NO_SHIP, no boundary_breach_check: true, "
              f"and no authority: NON_SOVEREIGN. "
              f"Exemption fields seen: {exemptions_seen or 'none'}")
    return ("INTENSITY_FLOOR_VIOLATED", detail)


def resolve_targets(repo_root: Path, argv: list[str]) -> list[Path]:
    if argv:
        return [Path(a).expanduser().resolve() for a in argv]
    return [repo_root / r for r in DEFAULT_ROOTS]


def collect_paths(target: Path) -> list[Path]:
    if not target.exists():
        return []
    if target.is_file():
        return [target] if target.suffix == ".md" else []
    return sorted(target.rglob("*.md"))


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    targets = resolve_targets(repo_root, argv)
    ok = skipped = raw_pass = violations = 0
    print(f"helen_intensity_floor_lint @ {repo_root}")
    print("=" * 64)
    for target in targets:
        for path in collect_paths(target):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                violations += 1
                try:
                    rel = path.relative_to(repo_root)
                except ValueError:
                    rel = path
                print(f"  ERROR  {rel}: {exc}")
                continue
            verdict, detail = classify(text)
            try:
                rel = path.relative_to(repo_root)
            except ValueError:
                rel = path
            if verdict == "OK":
                ok += 1
            elif verdict == "NO_FRONTMATTER":
                skipped += 1
            elif verdict == "RAW_PASS":
                raw_pass += 1
            elif verdict == "INTENSITY_FLOOR_VIOLATED":
                violations += 1
                print(f"  FAIL   {rel}")
                print(f"         INTENSITY_FLOOR_VIOLATED: {detail}")
    print("=" * 64)
    print(f"OK={ok}  RAW_PASS={raw_pass}  SKIPPED={skipped}  FAIL={violations}")
    if violations == 0:
        print("VERDICT: PASS  (helen_intensity_floor=PASS)")
        return 0
    print("VERDICT: FAIL  (helen_intensity_floor=FAIL)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
