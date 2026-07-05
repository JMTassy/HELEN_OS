"""Tests for the live constitutional NPC (temple/gardens/goblin_garden_conquest/live_npc.py).

Proves the HELEN membrane blocks Generative Agents §7.2 Isabella-drift in a live
end-to-end agent loop: grounded reflections admit, ungrounded ones are rejected at
the gate and never contaminate identity; state replays deterministically.
NON_SOVEREIGN. tmp ledger; no real files.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "temple/gardens/goblin_garden_conquest"))
import live_npc  # noqa: E402
from typed_memory import GardenMemory, MemoryType  # noqa: E402


def test_grounded_reflection_admitted_ungrounded_rejected(tmp_path):
    log = live_npc.run_npc("Klaus", ledger_path=tmp_path / "npc.jsonl")
    assert log["gated"] == ["Klaus is dedicated to his research"], "grounded reflection must admit"
    assert log["rejected"] == ["Klaus loves shakespeare theatre"], "ungrounded drift must be rejected"


def test_drift_never_enters_identity(tmp_path):
    log = live_npc.run_npc("Klaus", ledger_path=tmp_path / "npc.jsonl")
    assert log["drift_in_identity"] is False, \
        "Isabella drift: unverified reflection must never surface in default identity retrieval"


def test_default_retrieval_excludes_reflections(tmp_path):
    log = live_npc.run_npc("Klaus", ledger_path=tmp_path / "npc.jsonl")
    assert "reflection" not in log["default_retrieval_types"], \
        "SEAM 2: reflections stay out of default working memory even in the live loop"


def test_replay_is_deterministic(tmp_path):
    log = live_npc.run_npc("Klaus", ledger_path=tmp_path / "npc.jsonl")
    assert log["replay_matches"] is True
    assert log["replay_entries"] == log["live_entries"]


def test_grounding_validator_rejects_no_evidence(tmp_path):
    m = GardenMemory("Klaus", ledger_path=tmp_path / "m.jsonl")
    m.observe("Klaus read a paper", importance=0.5)
    v = live_npc.grounding_validator(m)
    # candidate with no shared CONTENT word (agent name "Klaus" doesn't count) → reject
    cands = m.reflect("unrelated topic about dragons",
                      live_npc.make_stub_reasoner("Klaus fights dragons"))
    assert v(cands[0]) is False


def test_two_runs_same_ledger_replay_identical(tmp_path):
    """Same scenario, two fresh ledgers → identical entry-id sequences (seed-free determinism
    of the loop structure; timestamps differ but the typed sequence is stable)."""
    a = live_npc.run_npc("Klaus", ledger_path=tmp_path / "a.jsonl")
    b = live_npc.run_npc("Klaus", ledger_path=tmp_path / "b.jsonl")
    assert a["gated"] == b["gated"]
    assert a["rejected"] == b["rejected"]
    assert a["default_retrieval_types"] == b["default_retrieval_types"]
