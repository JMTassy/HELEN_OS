"""brand_voice gate — fail-closed UZIK-register linter. 🔵 OBSERVED · NON_SOVEREIGN · authority=0.

Reads UZIK_CORPUS_V1.json (the extracted corpus) and enforces its ban-lists and hard rules on
HELEN-generated copy. This is a CHECKER, not an authority: it returns a typed verdict
(PASS / FAIL with violations); it never admits, mutates state, or mints a capability.
render ⊬ admitted — a clean voice check is a candidate, not a decision.

Fail-closed: any banned term, negative parallelism, or unsourced metric ⇒ FAIL. The heuristics are
deliberately conservative (lexical + a few regexes) — false positives are preferred to false
negatives, and the checks are declared, not silent. Determinism: pure text in, verdict out; no clock,
no network, no randomness.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_CORPUS_PATH = Path(__file__).resolve().parents[1].parent / "corpus" / "uzik" / "UZIK_CORPUS_V1.json"


def load_corpus(path: Path = _CORPUS_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class Verdict(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class Violation:
    code: str          # e.g. BANNED_VOCAB, NEGATIVE_PARALLELISM, UNSOURCED_METRIC
    span: str          # the offending fragment
    line: int


@dataclass(frozen=True)
class VoiceResult:
    verdict: Verdict
    violations: tuple = field(default_factory=tuple)
    authority: int = 0            # always 0 — a voice check never carries authority
    checks_run: tuple = field(default_factory=tuple)   # non-vacuity: which checks actually ran


# --- source markers that discharge the "metric needs a source" obligation
_SOURCE_MARKERS = re.compile(
    r"(source\s*[:=]|per\s+\w|selon\s|d'après|\[\d|\bhttps?://|receipt|cf\.|\bibid\b|\bsee\s)",
    re.IGNORECASE,
)
# --- a metric: a percentage, a multiplier (3x), or a standalone number >= 2 digits
_METRIC = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?\s?%|\d+(?:[.,]\d+)?\s?x\b|\b\d{2,}(?:[.,]\d+)?)", re.IGNORECASE)
# --- negative parallelism (hard ban): EN + FR shapes
_NEG_PARALLEL = (
    re.compile(r"\bnot\s+(only|just|merely)?\b[^.;:\n]{1,60}?\bbut\b", re.IGNORECASE),
    re.compile(r"n['’]t\s+(just|only|merely)\b[^.;:\n]{1,60}?\bbut\b", re.IGNORECASE),  # don't just X but Y
    re.compile(r"\b(isn't|aren't|wasn't|weren't|it's not|is not)\b[^.;:\n]{1,50}?,\s*(it's|they're|it is)\b", re.IGNORECASE),
    re.compile(r"\bn['’e][^.;:\n]{0,40}?\bpas\b[^.;:\n]{1,40}?\bmais\b", re.IGNORECASE),  # n'est/ne ... pas ... mais
    re.compile(r"\bnon\s+pas\b[^.;:\n]{1,40}?\bmais\b", re.IGNORECASE),
)


def _banned_terms(corpus: dict) -> list:
    v = corpus.get("vocabulary", {}).get("ban", [])
    pv = corpus.get("production_verbs", {}).get("ban", [])
    # keep only single-token bans for word-boundary matching; multiword bans matched as phrases
    return sorted(set(v) | set(pv), key=len, reverse=True)


def check(text: str, corpus: dict | None = None) -> VoiceResult:
    """Lint `text` against the UZIK corpus. Fail-closed on any violation."""
    corpus = corpus or load_corpus()
    banned = _banned_terms(corpus)
    violations: list = []
    checks = ("banned_vocab", "negative_parallelism", "unsourced_metric")

    lines = text.splitlines() or [text]
    for i, line in enumerate(lines, 1):
        # 1. banned vocabulary (word-boundary for single tokens; substring for phrases)
        for term in banned:
            pat = r"\b" + re.escape(term) + r"\b" if " " not in term else re.escape(term)
            if re.search(pat, line, re.IGNORECASE):
                violations.append(Violation("BANNED_VOCAB", term, i))
        # 2. negative parallelism (hard ban)
        for rx in _NEG_PARALLEL:
            m = rx.search(line)
            if m:
                violations.append(Violation("NEGATIVE_PARALLELISM", m.group(0).strip(), i))
        # 3. unsourced metric
        if not _SOURCE_MARKERS.search(line):
            for m in _METRIC.finditer(line):
                violations.append(Violation("UNSOURCED_METRIC", m.group(0).strip(), i))

    verdict = Verdict.FAIL if violations else Verdict.PASS
    return VoiceResult(verdict, tuple(violations), authority=0, checks_run=checks)


def report(result: VoiceResult) -> dict:
    """Graph-ready structured report (nodes = checks, edges = violations). Projection only —
    authority ∉ codomain; a renderer may draw this but cannot admit it."""
    by_code: dict = {}
    for v in result.violations:
        by_code.setdefault(v.code, []).append({"span": v.span, "line": v.line})
    return {
        "verdict": result.verdict.value,
        "authority": 0,
        "canon": False,
        "checks_run": list(result.checks_run),
        "violation_count": len(result.violations),
        "violations_by_code": by_code,
        "note": "brand_voice gate is a candidate check — render ⊬ admitted",
    }
