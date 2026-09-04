"""Base skill contract for non-sovereign HELEN cognitive layer.

All skills in this layer:
- authority = "NONE" (non-sovereign, no decision power)
- read-mostly (no ledger writes, no state mutation)
- deterministic (same inputs → same outputs)
- inspectable (typed, explicit outputs)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class SkillResult:
    """Immutable result of a skill execution."""
    skill_id: str
    authority: str
    ok: bool
    output: Dict[str, Any]
    errors: List[str] = field(default_factory=list)


def _ensure_non_sovereign(result: SkillResult) -> SkillResult:
    """Assert that the result carries no authority.

    This enforcement makes it impossible for a future edit
    to accidentally leak authority into the judgment layer.
    """
    assert result.authority == "NONE", \
        f"Skill {result.skill_id} violated non-sovereign boundary: authority={result.authority}"
    return result
