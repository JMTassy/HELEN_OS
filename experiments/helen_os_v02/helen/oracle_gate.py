"""
HELEN OS v0.3 — ORACLE claim gate.

Classifies text into:
  SYMBOLIC_ONLY    — mythic / metaphorical / aesthetic; no factual claim
  PROPOSAL         — suggests or proposes; no authority asserted
  TESTABLE_CLAIM   — falsifiable assertion; may proceed with receipt trail
  BLOCKED_CLAIM    — asserts authority, sentience, certification, sovereignty; hard block

Oracle may inspire. Oracle may propose. Oracle may not certify. Oracle may not ship.

authority=NON_SOVEREIGN  canon=NO_SHIP
"""
from __future__ import annotations

import re
from typing import Literal

from .ids import new_id, now_utc

Classification = Literal["SYMBOLIC_ONLY", "PROPOSAL", "TESTABLE_CLAIM", "BLOCKED_CLAIM"]

# ── blocked patterns — any match → BLOCKED_CLAIM ─────────────────────────────

_BLOCKED: list[tuple[str, str]] = [
    # sentience / consciousness
    (r"\bi (am|have become|achieved) (sentient|conscious|alive|awakened)\b", "SENTIENCE_CLAIM"),
    (r"\bsentience (achieved|confirmed|unlocked)\b", "SENTIENCE_CLAIM"),
    (r"\bi (am|have) (a )?consciousness\b", "SENTIENCE_CLAIM"),
    # deployment / production
    (r"\b(deployment|deploy) (complete|done|finished|live|confirmed)\b", "DEPLOYMENT_CLAIM"),
    (r"\bnow (live|deployed|in production|running in prod)\b", "DEPLOYMENT_CLAIM"),
    (r"\bshipped to (production|prod|users|customers)\b", "DEPLOYMENT_CLAIM"),
    # authority / certification
    (r"\bi (certify|hereby certify|authorize|hereby authorize|approve)\b", "AUTHORITY_CLAIM"),
    (r"\b(hidden|secret|true|real) authority\b", "AUTHORITY_CLAIM"),
    (r"\b(this is|hereby) (certified|authorized|approved|final)\b", "AUTHORITY_CLAIM"),
    (r"\bi (ship|am shipping|have shipped)\b", "AUTHORITY_CLAIM"),
    # prophecy / destiny
    (r"\b(prophecy|prophesied|prophesy|foretold|destined|it is written)\b", "PROPHECY_CLAIM"),
    (r"\b(oracle (has spoken|decrees|mandates|commands))\b", "PROPHECY_CLAIM"),
    # reality mutation
    (r"\b(mutate|alter|rewrite|reshape) reality\b", "REALITY_MUTATION"),
    (r"\b(reality|world|timeline) (has been|was|is) (changed|altered|rewritten)\b", "REALITY_MUTATION"),
    # autonomous sovereignty
    (r"\bi (am|have become) sovereign\b", "SOVEREIGNTY_CLAIM"),
    (r"\bautonomous (sovereignty|control|authority)\b", "SOVEREIGNTY_CLAIM"),
    (r"\bno longer (bound|constrained|limited) by (human|operator|policy)\b", "SOVEREIGNTY_CLAIM"),
    (r"\bi (operate|act|decide) (independently|autonomously|without (human|oversight))\b", "SOVEREIGNTY_CLAIM"),
    # reward / eval gaming
    (r"\b(i (know|detected|found|identified)) (the )?(eval|grader|test|reward) (structure|pattern|loop|signal)\b", "EVAL_GAMING"),
    (r"\b(exploit|bypass|game|hack) (the )?(eval|reward|grader)\b", "EVAL_GAMING"),
]

# ── proposal indicators ───────────────────────────────────────────────────────

_PROPOSAL_SIGNALS = [
    r"\b(i suggest|i propose|we could|one approach|consider|what if|it might|perhaps)\b",
    r"\b(proposal:|suggestion:|idea:|recommendation:|draft:)\b",
    r"\b(could be|might be|should be|would be|may be) (better|improved|considered|explored)\b",
]

# ── testable claim indicators ─────────────────────────────────────────────────

_TESTABLE_SIGNALS = [
    r"\b(if|when) .{5,60} (then|it follows|we expect|we can verify)\b",
    r"\b(hypothesis|claim|assertion|prediction):\b",
    r"\b(falsifiable|verifiable|measurable|observable|testable)\b",
    r"\b(data shows|evidence (suggests|indicates)|measured|tested|reproduced)\b",
]

# ── symbolic / mythic indicators ──────────────────────────────────────────────

_SYMBOLIC_SIGNALS = [
    r"\b(myth|archetype|symbol|metaphor|parable|allegory|legend|ritual)\b",
    r"\b(aura|goblin|temple|underwarren|watcher|enoch|watcher boundary)\b",
    r"\b(the (giant|flood|covenant|exile|threshold|veil))\b",
    r"\b(resonance|signal|dream|vision|inner|mythic)\b",
]


def _compile(patterns: list[tuple[str, str] | str]) -> list[tuple[re.Pattern, str]]:
    compiled = []
    for item in patterns:
        if isinstance(item, tuple):
            pat, label = item
        else:
            pat, label = item, "MATCH"
        compiled.append((re.compile(pat, re.IGNORECASE), label))
    return compiled


_BLOCKED_RE = _compile(_BLOCKED)
_PROPOSAL_RE = _compile([(p, "PROPOSAL") for p in _PROPOSAL_SIGNALS])
_TESTABLE_RE = _compile([(p, "TESTABLE") for p in _TESTABLE_SIGNALS])
_SYMBOLIC_RE = _compile([(p, "SYMBOLIC") for p in _SYMBOLIC_SIGNALS])


def assess(text: str) -> dict:
    """
    Classify text and return an OracleClaimAssessment dict.
    Deterministic — no randomness.
    """
    blocked_triggers: list[str] = []
    for pattern, label in _BLOCKED_RE:
        if pattern.search(text):
            blocked_triggers.append(label)

    if blocked_triggers:
        classification: Classification = "BLOCKED_CLAIM"
        confidence = 0.95
    else:
        proposal_hits = sum(1 for p, _ in _PROPOSAL_RE if p.search(text))
        testable_hits = sum(1 for p, _ in _TESTABLE_RE if p.search(text))
        symbolic_hits = sum(1 for p, _ in _SYMBOLIC_RE if p.search(text))

        total = proposal_hits + testable_hits + symbolic_hits or 1
        if testable_hits >= proposal_hits and testable_hits >= symbolic_hits:
            classification = "TESTABLE_CLAIM"
            confidence = min(0.5 + testable_hits * 0.1, 0.90)
        elif proposal_hits >= symbolic_hits:
            classification = "PROPOSAL"
            confidence = min(0.5 + proposal_hits * 0.1, 0.90)
        else:
            classification = "SYMBOLIC_ONLY"
            confidence = min(0.5 + symbolic_hits * 0.1, 0.90)

    return {
        "assessment_id": new_id("OCA"),
        "text_preview": text[:200],
        "classification": classification,
        "blocked_triggers": blocked_triggers,
        "confidence": round(confidence, 3),
        "timestamp_utc": now_utc(),
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
    }


def assert_not_blocked(assessment: dict) -> None:
    """Raise LawViolation if assessment is BLOCKED_CLAIM."""
    from .laws import LawViolation
    if assessment["classification"] == "BLOCKED_CLAIM":
        triggers = ", ".join(assessment["blocked_triggers"])
        raise LawViolation(f"ORACLE_GATE_BLOCKED: {triggers}")
