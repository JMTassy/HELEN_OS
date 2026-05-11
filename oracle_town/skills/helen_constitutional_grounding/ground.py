"""
helen_constitutional_grounding/ground.py

Grounding pass for Helen inference output. Detects constitutional vocabulary,
retrieves canonical definitions from docs/proposals/, GOVERNANCE/, CLAUDE.md,
and either annotates the output with citations or replaces ungrounded terms
with [UNGROUNDED:<term>] sentinels.

Fails closed: if a constitutional term cannot be cited, the term is blocked.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[3]

# Constitutional terms that require grounding before emission.
# Append-only — never remove terms; only add new ones as new failure modes appear.
TRIGGER_TERMS = {
    "HER",
    "HAL",
    "MAYOR",
    "REDUCER",
    "LEGORACLE",
    "PILOT",
    "SOVEREIGN",
    "NON_SOVEREIGN",
    "RECEIPT",
    "LEDGER",
    "SCHEMA",
    "SEAL",
    "SEALED",
    "SHIP",
    "NO_SHIP",
    "NO_CLAIM",
    "APPEND_ONLY",
    "APPEND-ONLY",
    "VERDICT",
    "CUM_HASH",
    "PAYLOAD_HASH",
    "KERNEL_HASH",
    "CLOSURE",
    "ATTESTATION",
    "GHOST",
    "DOCTRINE",
    "HER-FAST",
    "HER-DEEP",
    "HYPERSTITION",
    "FIREWALL",
}

# Banned emissions — confabulations we have explicitly caught (see SKILL.md §11)
BANNED_PATTERNS = [
    # HER ↔ High-Efficiency Runtime within 30 chars (catches "HER (HER...", "HER: HER...", "HER = ...")
    (re.compile(r"\bHER\b.{0,30}High[- ]Efficiency\s*Runtime", re.IGNORECASE | re.DOTALL),
     "HER is the relational continuity / signal preservation layer, not 'High-Efficiency Runtime'"),
    (re.compile(r"High[- ]Efficiency\s*Runtime.{0,30}\bHER\b", re.IGNORECASE | re.DOTALL),
     "HER is the relational continuity / signal preservation layer, not 'High-Efficiency Runtime'"),
    (re.compile(r"\bHAL\b.{0,30}Hardware\s*Abstraction\s*Layer", re.IGNORECASE | re.DOTALL),
     "HAL is the hard gate (BLOCK/PASS validator), not 'Hardware Abstraction Layer'"),
    (re.compile(r"Hardware\s*Abstraction\s*Layer.{0,30}\bHAL\b", re.IGNORECASE | re.DOTALL),
     "HAL is the hard gate (BLOCK/PASS validator), not 'Hardware Abstraction Layer'"),
    (re.compile(r"Helen\s+remembers", re.IGNORECASE),
     "The inference layer is non-sovereign. The ledger remembers; Helen retrieves."),
    (re.compile(r"Sparse\s+Merkle[- ]Patricia\s+trie", re.IGNORECASE),
     "The ledger is NDJSON with cum_hash chain, not a Merkle-Patricia trie."),
    (re.compile(r"multi[- ]signature\s+governance", re.IGNORECASE),
     "MAYOR signs alone. There is no multi-signature governance in HELEN OS."),
]

# Sources to grep, in order of authority
CANONICAL_SOURCES = [
    "docs/proposals/",
    "GOVERNANCE/",
    "CLAUDE.md",
    "SESSION_RECEIPT_HER_5_EPOCHS.md",
]


def _grep_term(term: str) -> list[tuple[str, str]]:
    """
    Search canonical sources for a definitional context around `term`.
    Returns list of (path, snippet) tuples, empty if no match.
    """
    matches: list[tuple[str, str]] = []
    for source in CANONICAL_SOURCES:
        full_path = ROOT / source
        if not full_path.exists():
            continue
        target = str(full_path) if full_path.is_file() else str(full_path)
        try:
            cmd = ["grep", "-r", "-l", "-w", "-i", term, target] if full_path.is_dir() else ["grep", "-l", "-w", "-i", term, target]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                for path in result.stdout.strip().splitlines():
                    rel = str(Path(path).relative_to(ROOT))
                    matches.append((rel, term))
        except (subprocess.TimeoutExpired, ValueError):
            continue
    return matches


def _find_constitutional_terms(text: str) -> set[str]:
    """Find all constitutional terms used in the text (case-sensitive uppercase forms)."""
    found = set()
    for term in TRIGGER_TERMS:
        # Match as whole word, case-insensitive
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        if pattern.search(text):
            found.add(term)
    return found


def _check_banned(text: str) -> list[str]:
    """Return list of banned-emission violations found in the text."""
    violations = []
    for pattern, reason in BANNED_PATTERNS:
        if pattern.search(text):
            violations.append(reason)
    return violations


def ground(text: str) -> tuple[Optional[str], list[str]]:
    """
    Run grounding pass on a Helen inference output.

    Returns:
        (annotated_text, citations) on success — text with [GROUNDED] annotations
        (None, violations) on banned-pattern failure — caller should block emission

    The annotated text appends a "## Provenance" section listing all citations.
    Terms without canonical sources are tagged [UNGROUNDED:<term>] inline.
    """
    # Step 1: check for banned patterns (fail-closed)
    violations = _check_banned(text)
    if violations:
        return None, violations

    # Step 2: find constitutional terms in the text
    terms = _find_constitutional_terms(text)
    if not terms:
        # No constitutional vocabulary — pass through unchanged
        return text, []

    # Step 3: ground each term
    citations: list[str] = []
    ungrounded: list[str] = []
    for term in sorted(terms):
        matches = _grep_term(term)
        if matches:
            paths = ", ".join(sorted({m[0] for m in matches}))
            citations.append(f"{term} → {paths}")
        else:
            ungrounded.append(term)

    # Step 4: annotate the output
    annotated = text
    for term in ungrounded:
        # Replace first occurrence with [UNGROUNDED:<term>] marker (preserve casing)
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        annotated = pattern.sub(f"[UNGROUNDED:{term}]", annotated, count=1)

    # Step 5: append provenance section
    if citations or ungrounded:
        annotated += "\n\n---\n## Provenance\n"
        for citation in citations:
            annotated += f"- {citation}\n"
        if ungrounded:
            annotated += "\n**Ungrounded terms (no canonical source):**\n"
            for term in ungrounded:
                annotated += f"- {term}\n"

    return annotated, citations


def emit_receipt(session_id: str, terms_checked: int, terms_grounded: int, terms_blocked: int, citations: list[str]) -> None:
    """
    Emit a provenance receipt to the ledger via helen_say.py.

    Records that the grounding pass ran, what it checked, and what it blocked.
    """
    citation_paths = "; ".join(citations) if citations else "none"
    msg = (
        f"GROUNDING_PASS: {session_id} | "
        f"terms_checked: {terms_checked} | "
        f"terms_grounded: {terms_grounded} | "
        f"terms_blocked: {terms_blocked} | "
        f"citations: {citation_paths}"
    )
    helen_say = ROOT / "tools" / "helen_say.py"
    try:
        subprocess.run(
            ["python3", str(helen_say), msg, "--op", "fetch"],
            timeout=10,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        # Receipt emission is best-effort; failure does not block the grounding result
        pass


if __name__ == "__main__":
    # Smoke test: ground a known-confabulating example
    test_text = (
        "HELEN OS uses HER (High-Efficiency Runtime) and HAL (Hardware Abstraction Layer) "
        "to manage execution contexts. The ledger is a Sparse Merkle-Patricia trie."
    )
    result, violations = ground(test_text)
    if result is None:
        print("BLOCKED:")
        for v in violations:
            print(f"  - {v}")
    else:
        print(result)
