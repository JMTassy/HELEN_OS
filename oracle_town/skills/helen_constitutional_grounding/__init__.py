"""
helen_constitutional_grounding — fail-closed grounding pass for Helen inference output.

Public API:
    ground(text) -> (annotated_text, citations) | (None, violations)
    emit_receipt(...) -> None
"""
from .ground import ground, emit_receipt, TRIGGER_TERMS, BANNED_PATTERNS

__all__ = ["ground", "emit_receipt", "TRIGGER_TERMS", "BANNED_PATTERNS"]
