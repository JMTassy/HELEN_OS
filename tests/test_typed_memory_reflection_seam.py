"""SEAM 2 — Isabella-drift defense in GardenMemory.retrieve() (typed_memory.py).

Generative Agents §7.2: unverified reflections re-enter the memory stream and
retrieve as if they were observations, contaminating identity ("Yes, I'm very
interested in literature!"). HELEN closes the seam: a REFLECTION is a candidate,
not admitted working memory — it must NOT be retrieved by default, only on
explicit type opt-in. Non-implication enforced: reflection ⊬ observation.

NON_SOVEREIGN. Uses tmp ledger paths; writes no real files.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "temple/gardens/goblin_garden_conquest"))
from typed_memory import GardenMemory, MemoryType  # noqa: E402


def _mem(tmp_path):
    return GardenMemory("test-agent", ledger_path=tmp_path / "mem.jsonl")


def test_retrieve_excludes_reflection_by_default(tmp_path):
    m = _mem(tmp_path)
    m.add_observation("Klaus read a paper on gentrification", importance=0.5)
    m.add_observation("Klaus visited the library", importance=0.5)
    # an UNVERIFIED reflection enters the stream
    m.reflect("what is Klaus like", local_reasoner=lambda p: "Klaus loves shakespeare theatre")
    hits = m.retrieve("shakespeare theatre", top_k=5)
    assert all(e.type != MemoryType.REFLECTION for e in hits), \
        "unverified reflection must NOT retrieve as default working memory (Isabella drift)"


def test_reflection_retrievable_only_after_gate(tmp_path):
    """SEAM 2 ∘ SEAM 3: a reflection becomes a retrievable REFLECTION only after it
    passes gate_reflection() — reflect() alone yields a candidate that never enters
    memory. Read-time filter + write-time gate compose."""
    m = _mem(tmp_path)
    m.add_observation("Klaus read a paper", importance=0.5)
    cands = m.reflect("what is Klaus like", local_reasoner=lambda p: "Klaus loves shakespeare theatre")
    # ungated: nothing retrievable, even with explicit opt-in
    assert m.retrieve("shakespeare theatre", top_k=5, type_filter=MemoryType.REFLECTION) == [], \
        "ungated reflection candidate must NOT be retrievable"
    # gate it (validator accepts) → now retrievable on explicit opt-in
    m.gate_reflection(cands[0], validator=lambda c: True)
    hits = m.retrieve("shakespeare theatre", top_k=5, type_filter=MemoryType.REFLECTION)
    assert any(e.type == MemoryType.REFLECTION for e in hits), \
        "gated reflection must be retrievable on explicit type_filter=REFLECTION"


def test_gated_reflection_still_excluded_from_default_retrieval(tmp_path):
    """Even a GATED reflection stays out of default retrieval (SEAM 2 holds post-gate):
    admitted ≠ working-memory-by-default."""
    m = _mem(tmp_path)
    m.add_observation("Klaus read a paper", importance=0.5)
    cands = m.reflect("q", local_reasoner=lambda p: "Klaus dedicated to shakespeare research")
    m.gate_reflection(cands[0], validator=lambda c: True)
    hits = m.retrieve("shakespeare research", top_k=5)  # default, no type_filter
    assert all(e.type != MemoryType.REFLECTION for e in hits), \
        "gated reflection must still be excluded from DEFAULT retrieval"


def test_reflection_cannot_compound_through_retrieval(tmp_path):
    """SEAM 3: reflect() builds context via default retrieve(), which excludes
    reflections — so a prior (even gated) reflection can never feed the next one."""
    m = _mem(tmp_path)
    m.add_observation("Klaus read a paper on gentrification", importance=0.5)
    c1 = m.reflect("first", local_reasoner=lambda p: "Klaus enjoys shakespeare deeply")
    m.gate_reflection(c1[0], validator=lambda c: True)  # admit it
    seen = {}

    def capture(prompt):
        seen["prompt"] = prompt
        return "Klaus organizes shakespeare festivals"

    m.reflect("second", local_reasoner=capture)
    assert "shakespeare deeply" not in seen.get("prompt", ""), \
        "reflection-of-reflection must not compound: prior reflection leaked into new context"


def test_observations_still_retrieve_by_default(tmp_path):
    m = _mem(tmp_path)
    m.add_observation("Klaus met Maria at the cafe", importance=0.7)
    hits = m.retrieve("Maria cafe", top_k=5)
    assert any(e.type == MemoryType.OBSERVATION for e in hits), \
        "observations must remain retrievable by default (no over-blocking)"
