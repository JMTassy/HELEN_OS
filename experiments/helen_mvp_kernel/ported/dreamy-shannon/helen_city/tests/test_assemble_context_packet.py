"""Tests for assemble_context_packet skill.

Verifies:
- Mixed-type output (one of each: law, project, thread, topic, next_action)
- Determinism (same inputs → same packet, input order irrelevant)
- Authority boundary (authority="NONE" always)
- Mode validation
- Rationale completeness
- Structural dominance (critical objects win regardless of type ordering)
"""

import pytest
import random
import os
from helen_city.knowledge.loader import load_knowledge_registry
from helen_city.skills.assemble_context_packet import assemble_context_packet


@pytest.fixture
def corpus():
    """Load test corpus."""
    test_dir = os.path.dirname(__file__)
    corpus_path = os.path.join(test_dir, "test_corpus.json")
    return load_knowledge_registry(corpus_path)


class TestStructure:
    """Test that the assembled packet has the right structure."""

    def test_returns_ok(self, corpus):
        """Should return ok=True for valid mode."""
        result = assemble_context_packet(corpus, "what matters now")
        assert result.ok is True
        assert result.authority == "NONE"

    def test_output_has_all_sections(self, corpus):
        """Output should contain all expected sections."""
        result = assemble_context_packet(corpus, "what matters now")
        output = result.output
        required = ["packet_id", "authority", "mode", "query",
                    "laws", "projects", "threads", "topics",
                    "suggested_next_action", "rationale"]
        for field in required:
            assert field in output, f"missing field: {field}"

    def test_laws_section_populated(self, corpus):
        """Should include at least one law object."""
        result = assemble_context_packet(corpus, "what matters now")
        assert len(result.output["laws"]) >= 1

    def test_projects_section_populated(self, corpus):
        """Should include at least one project."""
        result = assemble_context_packet(corpus, "what matters now")
        assert len(result.output["projects"]) >= 1

    def test_threads_section_populated(self, corpus):
        """Should include at least one thread."""
        result = assemble_context_packet(corpus, "what matters now")
        assert len(result.output["threads"]) >= 1

    def test_topics_section_populated(self, corpus):
        """Should include at least one topic."""
        result = assemble_context_packet(corpus, "what matters now")
        assert len(result.output["topics"]) >= 1

    def test_next_action_populated(self, corpus):
        """Should include a next action recommendation."""
        result = assemble_context_packet(corpus, "what matters now")
        assert result.output["suggested_next_action"] != {}
        assert "suggested_object_id" in result.output["suggested_next_action"]

    def test_rationale_is_non_empty(self, corpus):
        """Should explain what was selected and why."""
        result = assemble_context_packet(corpus, "what matters now")
        assert len(result.output["rationale"]) >= 1


class TestAuthorityBoundary:
    """Test that authority boundary is enforced."""

    def test_authority_is_none(self, corpus):
        """Authority must always be NONE."""
        result = assemble_context_packet(corpus, "any query")
        assert result.authority == "NONE"

    def test_output_authority_is_none(self, corpus):
        """Output packet authority must also be NONE."""
        result = assemble_context_packet(corpus, "any query")
        assert result.output["authority"] == "NONE"

    def test_invalid_mode_returns_ok_false(self, corpus):
        """Unknown mode should fail cleanly, not raise."""
        result = assemble_context_packet(corpus, "query", mode="sovereign")
        assert result.ok is False
        assert result.authority == "NONE"
        assert len(result.errors) > 0


class TestDeterminism:
    """Test that output is identical for same inputs."""

    def test_deterministic_same_inputs(self, corpus):
        """Same query + same corpus → identical packet."""
        r1 = assemble_context_packet(corpus, "what matters now", mode="companion")
        r2 = assemble_context_packet(corpus, "what matters now", mode="companion")
        assert r1.output["laws"] == r2.output["laws"]
        assert r1.output["projects"] == r2.output["projects"]
        assert r1.output["threads"] == r2.output["threads"]
        assert r1.output["topics"] == r2.output["topics"]
        assert r1.output["suggested_next_action"] == r2.output["suggested_next_action"]

    def test_deterministic_shuffled_corpus(self, corpus):
        """Shuffled input order must not change selected objects."""
        r1 = assemble_context_packet(corpus, "what matters now")

        corpus_shuffled = corpus.copy()
        random.shuffle(corpus_shuffled)
        r2 = assemble_context_packet(corpus_shuffled, "what matters now")

        # Selected object IDs must be identical
        assert r1.output["projects"][0]["id"] == r2.output["projects"][0]["id"]
        assert r1.output["threads"][0]["id"] == r2.output["threads"][0]["id"]
        assert r1.output["topics"][0]["id"] == r2.output["topics"][0]["id"]
        assert (
            r1.output["suggested_next_action"]["suggested_object_id"]
            == r2.output["suggested_next_action"]["suggested_object_id"]
        )

    def test_five_shuffles_all_identical(self, corpus):
        """Run 5 shuffled permutations — all must return same object selections."""
        baseline = assemble_context_packet(corpus, "what matters now")
        baseline_project = baseline.output["projects"][0]["id"]

        for _ in range(5):
            shuffled = corpus.copy()
            random.shuffle(shuffled)
            result = assemble_context_packet(shuffled, "what matters now")
            assert result.output["projects"][0]["id"] == baseline_project


class TestRankingCorrectness:
    """Test that structural ranking governs selection."""

    def test_critical_project_selected_over_low(self, corpus):
        """critical priority project should be selected."""
        result = assemble_context_packet(corpus, "any query")
        project = result.output["projects"][0]
        # project_helen_os is critical/core_now — should win
        assert project["id"] == "project_helen_os"

    def test_core_now_topic_selected(self, corpus):
        """core_now/critical topic should be selected over active_supporting one."""
        result = assemble_context_packet(corpus, "any query")
        topic = result.output["topics"][0]
        # topic_memory_spine is critical/core_now — should win over oracle_reasoning
        assert topic["id"] == "topic_memory_spine"

    def test_core_now_law_selected_for_companion(self, corpus):
        """Companion district law with core_now should be selected."""
        result = assemble_context_packet(corpus, "continuity", mode="companion", district_hint="Companion")
        law = result.output["laws"][0]
        # law_memory_backed_continuity is core_now/critical for Companion
        assert law["id"] == "law_memory_backed_continuity"

    def test_critical_beats_query_match(self):
        """Critical/core_now object should win over low-priority query match."""
        test_corpus = [
            {
                "id": "critical_no_match",
                "object_type": "PROJECT_PROFILE",
                "title": "HELEN OS",
                "priority": "critical",
                "salience_now": "core_now",
                "helen_stance": "deep_helen_interest",
                "relevance": "Core system",
                "links": [],
            },
            {
                "id": "query_match_low",
                "object_type": "PROJECT_PROFILE",
                "title": "Casa memory Cielo",  # Contains query term "memory"
                "priority": "low",
                "salience_now": "watchlist",
                "helen_stance": "utility_only",
                "relevance": "Unimportant",
                "links": [],
            },
        ]
        result = assemble_context_packet(test_corpus, "memory", mode="default")
        assert result.ok is True
        # Critical object should win despite query matching the other title
        assert result.output["projects"][0]["id"] == "critical_no_match"


class TestModes:
    """Test mode-specific behavior."""

    def test_all_valid_modes_succeed(self, corpus):
        """All five modes should succeed without error."""
        for mode in ["companion", "oracle", "temple", "mayor", "default"]:
            result = assemble_context_packet(corpus, "query", mode=mode)
            assert result.ok is True, f"mode {mode} failed: {result.errors}"
            assert result.output["mode"] == mode

    def test_mode_recorded_in_packet(self, corpus):
        """Packet should record the operating mode."""
        result = assemble_context_packet(corpus, "query", mode="oracle")
        assert result.output["mode"] == "oracle"

    def test_query_recorded_in_packet(self, corpus):
        """Packet should record the query."""
        result = assemble_context_packet(corpus, "what is the law of Companion", mode="mayor")
        assert result.output["query"] == "what is the law of Companion"


class TestEmptyCornus:
    """Test graceful handling of sparse corpora."""

    def test_empty_corpus_still_returns(self):
        """Empty corpus should return ok=True with empty sections (no crash)."""
        result = assemble_context_packet([], "query")
        assert result.ok is True
        assert result.authority == "NONE"
        assert result.output["laws"] == []
        assert result.output["projects"] == []
        assert result.output["suggested_next_action"] == {}

    def test_no_actionable_objects_returns_empty_next_action(self):
        """Corpus with only archived objects should return empty next_action."""
        test_corpus = [
            {
                "id": "archived_project",
                "object_type": "PROJECT_PROFILE",
                "title": "Old Project",
                "priority": "low",
                "salience_now": "archive",
                "helen_stance": "utility_only",
                "relevance": "Archived",
                "links": [],
            }
        ]
        result = assemble_context_packet(test_corpus, "query")
        assert result.ok is True
        assert result.output["suggested_next_action"] == {}
