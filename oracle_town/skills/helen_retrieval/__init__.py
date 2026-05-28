"""
helen_retrieval — input-side retrieval pass (HER Library Card).

Public API:
    retrieve(query) -> list[tuple[str, str]]   # (source_path, snippet)
    format_for_prompt(retrieved) -> str         # context block for system prompt
"""
from .retrieve import retrieve, format_for_prompt, CONSTITUTIONAL_TERMS

__all__ = ["retrieve", "format_for_prompt", "CONSTITUTIONAL_TERMS"]
