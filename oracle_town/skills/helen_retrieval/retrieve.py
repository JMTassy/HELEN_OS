"""
helen_retrieval/retrieve.py

Input-side retrieval pass for Helen inference (HER Library Card).

Before the LLM generates a response, relevant constitutional passages are
retrieved from canonical sources and injected as context.  This is the
pre-inference dual of helen_constitutional_grounding (post-inference guard).

Strategy:
  1. Extract query-relevant terms (constitutional vocab + identity triggers)
  2. Grep canonical sources (docs/proposals/, GOVERNANCE/, CLAUDE.md, ledger)
  3. Return (source_path, snippet) pairs for prompt injection

Fail-open: retrieval failure never blocks inference; it just returns empty.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Canonical sources, searched in priority order
CANON_SOURCES = [
    "docs/proposals/",
    "GOVERNANCE/",
    "CLAUDE.md",
    "SESSION_RECEIPT_HER_5_EPOCHS.md",
]

# Identity-question patterns → inject provenance passages
_IDENTITY_RE = re.compile(
    r"\b(who\s+(created|made|built|are\s+you)|what\s+are\s+you|your\s+(creator|origin|author)|"
    r"who\s+is\s+HELEN|HELEN\s+OS)\b",
    re.IGNORECASE,
)

# Constitutional vocabulary (mirrors grounding TRIGGER_TERMS)
CONSTITUTIONAL_TERMS = {
    "HER", "HAL", "MAYOR", "REDUCER", "LEGORACLE", "PILOT",
    "SOVEREIGN", "NON_SOVEREIGN", "RECEIPT", "LEDGER", "SCHEMA",
    "SEAL", "SHIP", "NO_SHIP", "NO_CLAIM", "APPEND_ONLY",
    "VERDICT", "CUM_HASH", "CLOSURE", "DOCTRINE", "FIREWALL",
}

_STOPWORDS = frozenset(
    "what when where which while about would there their could should "
    "these those have been will with from this that just also your".split()
)


def _extract_terms(query: str) -> list[str]:
    """Return ordered list of terms to search for the given query."""
    terms: list[str] = []

    if _IDENTITY_RE.search(query):
        # Identity questions need provenance passages first
        terms.extend(["JMT", "NON_SOVEREIGN", "HELEN OS"])

    for term in CONSTITUTIONAL_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", query, re.IGNORECASE):
            terms.append(term)

    # Add meaningful words from the query
    for word in re.findall(r"\b[a-zA-Z]{4,}\b", query):
        if word.lower() not in _STOPWORDS and word not in terms:
            terms.append(word)

    # Deduplicate, preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _grep_snippets(
    term: str, source: Path, context_lines: int = 4
) -> list[tuple[str, str]]:
    """Return (rel_path, snippet) pairs for term in source. Fail-open."""
    results: list[tuple[str, str]] = []
    if not source.exists():
        return results
    try:
        list_cmd = (
            ["grep", "-r", "-i", "-w", "-l",
             "--include=*.md", "--include=*.json", term, str(source)]
            if source.is_dir()
            else ["grep", "-i", "-w", "-l", term, str(source)]
        )
        lr = subprocess.run(list_cmd, capture_output=True, text=True, timeout=5)
        if lr.returncode != 0 or not lr.stdout.strip():
            return results
        for fpath in lr.stdout.strip().splitlines()[:3]:
            try:
                ctx_r = subprocess.run(
                    ["grep", "-i", "-w", "-n",
                     "-A", str(context_lines), "-B", str(context_lines),
                     term, fpath],
                    capture_output=True, text=True, timeout=5,
                )
                if ctx_r.returncode == 0 and ctx_r.stdout.strip():
                    rel = str(Path(fpath).relative_to(ROOT))
                    snippet = ctx_r.stdout.strip()[:600]
                    results.append((rel, snippet))
            except Exception:
                continue
    except Exception:
        pass
    return results


def retrieve(query: str, top_k: int = 5) -> list[tuple[str, str]]:
    """
    Retrieve relevant constitutional passages for a user query.

    Returns list of (source_path, passage) tuples — empty on failure.
    Called before LLM inference so Helen can answer from canon.
    """
    terms = _extract_terms(query)
    if not terms:
        return []

    seen_paths: set[str] = set()
    results: list[tuple[str, str]] = []

    for term in terms[:6]:
        for source_str in CANON_SOURCES:
            for rel_path, snippet in _grep_snippets(term, ROOT / source_str):
                if rel_path not in seen_paths:
                    seen_paths.add(rel_path)
                    results.append((rel_path, snippet))
                    if len(results) >= top_k:
                        return results

    return results


def format_for_prompt(retrieved: list[tuple[str, str]]) -> str:
    """Format retrieved passages as a labelled context block for system prompt injection."""
    if not retrieved:
        return ""
    lines = ["[RETRIEVED CONSTITUTIONAL CONTEXT — cite these, do not confabulate]"]
    for path, passage in retrieved:
        lines.append(f"\n--- {path} ---")
        lines.append(passage)
    lines.append("[END RETRIEVED CONTEXT]")
    return "\n".join(lines)
