"""
helen/utils/redaction.py

Secret redaction & token sanitization for bridge output.
Ensures no authority tokens, hashes, or filesystem paths leak to AIRI.
"""

import re
from typing import Tuple


# Authority tokens that MUST NOT leak to AIRI (case-insensitive)
AUTHORITY_PATTERN = re.compile(
    r"\b(VERDICT|SEALED|SHIP|APPROVED|TERMINATION|RECEIPT|LEDGER|SEAL|IRREVERSIBLE)\b",
    re.IGNORECASE
)

# Patterns for structured data leakage
HEX64_PATTERN = re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE)  # SHA256 hashes
PATH_PATTERN = re.compile(
    r"(/town/|/ledger/|/append\b|\.ndjson\b|\.sqlite\b|\.db\b|\.lock|\.seq|"
    r"file:/{1,3}|sandbox:|C:\\|[A-Z]:\\)",
    re.IGNORECASE
)
API_KEY_PATTERN = re.compile(r"(Bearer|Authorization|api[_-]?key|token)[:\s=]+([^\s,\]]+)", re.IGNORECASE)
SECRET_MARKERS = re.compile(r"(password|secret|private[_-]?key|credential)[:\s=]+([^\s,\]]+)", re.IGNORECASE)
OPENAI_KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9]{3,}\b")  # OpenAI-style API keys


def redact_secrets(text: str) -> str:
    """
    Redact API keys, tokens, and secret markers from text.

    Args:
        text: Raw text that may contain secrets

    Returns:
        Sanitized text with secrets redacted
    """
    if not isinstance(text, str):
        return str(text)

    # Redact API keys and tokens
    text = API_KEY_PATTERN.sub(r"\1: [REDACTED]", text)

    # Redact secret markers
    text = SECRET_MARKERS.sub(r"\1: [REDACTED]", text)

    return text


def sanitize_output_for_airi(text: str) -> Tuple[str, list]:
    """
    Comprehensive sanitization for AIRI output.
    Strips authority tokens (case-insensitive), hashes, paths, secrets.

    Args:
        text: HELEN response text

    Returns:
        (sanitized_text, list_of_redactions_applied)
    """
    if not isinstance(text, str):
        text = str(text)

    redactions = []

    # 1. Redact secrets first
    text = redact_secrets(text)

    # 1a. Redact OpenAI-style API keys
    if OPENAI_KEY_PATTERN.search(text):
        text = OPENAI_KEY_PATTERN.sub("[REDACTED]", text)
        redactions.append("api_key:openai_style")

    # 2. Strip authority tokens (case-insensitive)
    if AUTHORITY_PATTERN.search(text):
        matches = AUTHORITY_PATTERN.findall(text)
        text = AUTHORITY_PATTERN.sub("[REDACTED]", text)
        for match in set(matches):  # deduplicate
            redactions.append(f"authority_token:{match.upper()}")

    # 3. Strip hash-like values (SHA256)
    if HEX64_PATTERN.search(text):
        text = HEX64_PATTERN.sub("[HASH]", text)
        redactions.append("hash:hex64")

    # 4. Strip filesystem references (case-insensitive, cross-platform)
    if PATH_PATTERN.search(text):
        text = PATH_PATTERN.sub("[PATH]", text)
        redactions.append("path:filesystem")

    return text.strip(), redactions


def emotion_map(text: str) -> str:
    """
    Map response text to AIRI emotion state.
    Unambiguous keyword-based heuristic with clear precedence.

    Precedence (highest first):
    1. Concerned — errors, warnings, dangers (urgent negative)
    2. Happy — success, completion (urgent positive)
    3. Thinking — reflection, ambiguity, tension (contemplative)
    4. Neutral — default

    Args:
        text: Response text

    Returns:
        emotion ∈ {neutral, thinking, happy, concerned}
    """
    if not isinstance(text, str):
        return "neutral"

    text_lower = text.lower()

    # 1. CONCERNED — errors, warnings, dangers (urgent negative)
    if any(word in text_lower for word in ["error", "fail", "danger", "issue", "warning", "problem"]):
        return "concerned"

    # 2. HAPPY — success, completion (urgent positive)
    if any(word in text_lower for word in ["success", "complete", "done", "finished", "perfect", "excellent"]):
        return "happy"

    # 3. THINKING — reflection, ambiguity, logical tension (contemplative)
    # Note: "conflict" → thinking (logical contradiction), not concerned (error)
    if any(word in text_lower for word in ["consider", "think", "puzzle", "tension", "dispute", "conflict", "question"]):
        return "thinking"

    # 4. NEUTRAL — default
    return "neutral"
