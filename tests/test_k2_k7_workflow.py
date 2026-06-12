"""
Integration tests for K2 (Claim Workflow) + K7 (Ledger Reader)

Day 3: Ledger integration + K2 workflow validation
"""

import pytest
pytest.importorskip("numpy")
import json
import tempfile
import shutil
from pathlib import Path

from oracle_town.skills.claim_workflow import Claim, ClaimWorkflow
from oracle_town.skills.ledger_reader import LedgerReader
from oracle_town.skills.map_generator_skill import MapGeneratorSkill


class TestK2ClaimWorkflow:
    """K2: No Self-Validation — Skill proposes, Foreman validates"""

    def test_claim_proposal_to_pending(self, temp_workflow):
        """K2: Propose claim to Foreman (pending.md)"""
        claim = Claim(
            claim_id="LP-MAP-game_001",
            type="map_generation",
            author="MapGeneratorSkill",
            statement="Map generated for game_001 with 6 territories",
            map_hash="abc123def456"
        )

        temp_workflow.propose_claim(claim)

        # Verify pending.md exists and contains claim
        assert temp_workflow.pending_path.exists()

        with open(temp_workflow.pending_path, "r") as f:
            content = f.read()

        assert "LP-MAP-game_001" in content
        assert "MapGeneratorSkill" in content
        assert "pending" in content

    def test_foreman_accepts_claim(self, temp_workflow):
        """K2: Foreman accepts claim (moves to accepted.md)"""
        claim = Claim(
            claim_id="LP-MAP-game_001",
            type="map_generation",
            author="MapGeneratorSkill",
            statement="Map generated for game_001 with 6 territories",
            map_hash="abc123def456"
        )

        # Propose
        temp_workflow.propose_claim(claim)

        # Foreman accepts
        temp_workflow.accept_claim(
            claim_id="LP-MAP-game_001",
            curator="Foreman",
            reason="Map is valid and ready for UZIK visualization"
        )

        # Verify accepted.md exists
        assert temp_workflow.accepted_path.exists()

        with open(temp_workflow.accepted_path, "r") as f:
            content = f.read()

        assert "LP-MAP-game_001" in content
        assert "accepted" in content
        assert "Foreman" in content

    def test_foreman_rejects_claim(self, temp_workflow):
        """K2: Foreman rejects claim (moves to rejected.md with audit trail)"""
        claim = Claim(
            claim_id="LP-MAP-game_001",
            type="map_generation",
            author="MapGeneratorSkill",
            statement="Map generated for game_001 with 6 territories",
            map_hash="abc123def456"
        )

        # Propose
        temp_workflow.propose_claim(claim)

        # Foreman rejects
        temp_workflow.reject_claim(
            claim_id="LP-MAP-game_001",
            curator="Foreman",
            reason="Territory distribution too imbalanced for gameplay"
        )

        # Verify rejected.md exists
        assert temp_workflow.rejected_path.exists()

        with open(temp_workflow.rejected_path, "r") as f:
            content = f.read()

        assert "LP-MAP-game_001" in content
        assert "rejected" in content
        assert "imbalanced" in content

    def test_pending_claims_list(self, temp_workflow):
        """K2: Retrieve list of pending claims from Foreman inbox"""
        # Propose multiple claims
        for i in range(3):
            claim = Claim(
                claim_id=f"LP-MAP-game_{i:03d}",
                type="map_generation",
                author="MapGeneratorSkill",
                statement=f"Map for game {i:03d}",
                map_hash=f"hash_{i:03d}"
            )
            temp_workflow.propose_claim(claim)

        # Get pending claims
        pending = temp_workflow.get_pending_claims()

        assert len(pending) == 3
        assert all(claim["author"] == "MapGeneratorSkill" for claim in pending)

    def test_claim_data_preserved(self, temp_workflow):
        """K2: Claim data must be preserved through workflow"""
        original_claim = Claim(
            claim_id="LP-MAP-game_001",
            type="map_generation",
            author="MapGeneratorSkill",
            statement="Original statement about the map",
            map_hash="abc123def456"
        )

        temp_workflow.propose_claim(original_claim)
        temp_workflow.accept_claim("LP-MAP-game_001", "Foreman", "OK")

        # Retrieve and verify
        accepted = temp_workflow.get_accepted_claims()
        assert len(accepted) == 1
        assert accepted[0]["statement"] == "Original statement about the map"
        assert accepted[0]["map_hash"] == "abc123def456"


class TestK7LedgerReader:
    """K7: Policy Pinning — Read and verify immutable ledger"""

    def test_ledger_read_all_entries(self, temp_skill_with_ledger):
        """K7: Read all entries from JSONL ledger"""
        skill, ledger = temp_skill_with_ledger

        # Generate maps to populate ledger
        for i in range(3):
            skill.generate_map(seed=111 + i, game_id=f"game_{i:03d}")

        # Read ledger
        entries = ledger.read_all_entries()

        assert len(entries) == 3
        assert all(e["rule"] == "K7_POLICY_PINNING" for e in entries)

    def test_ledger_entries_by_game_id(self, temp_skill_with_ledger):
        """K7: Retrieve entries for specific game"""
        skill, ledger = temp_skill_with_ledger

        # Generate for same game (should use same map due to cache)
        skill.generate_map(seed=111, game_id="game_001")
        skill.generate_map(seed=111, game_id="game_002")

        # Get entries for game_001
        entries = ledger.get_entries_by_game_id("game_001")

        assert len(entries) >= 1
        assert all(e["game_id"] == "game_001" for e in entries)

    def test_ledger_entries_by_seed(self, temp_skill_with_ledger):
        """K7: Retrieve entries by seed (K5+K7 combo)"""
        skill, ledger = temp_skill_with_ledger

        # Generate same seed, different games
        seed = 111
        skill.generate_map(seed=seed, game_id="game_001")
        skill.generate_map(seed=seed, game_id="game_002")

        # Get entries for this seed
        entries = ledger.get_entries_by_seed(seed)

        assert len(entries) >= 2
        # All should have same hash (same seed → same map)
        hashes = set(e["map_hash"] for e in entries)
        assert len(hashes) == 1

    def test_ledger_hash_consistency_verification(self, temp_skill_with_ledger):
        """K7: Verify hash consistency (no mid-game changes)"""
        skill, ledger = temp_skill_with_ledger

        # Generate maps
        skill.generate_map(seed=111, game_id="game_001")
        skill.generate_map(seed=111, game_id="game_001")  # Same game, should have same hash

        # Verify consistency
        is_consistent = ledger.verify_hash_consistency("game_001")
        assert is_consistent is True

    def test_ledger_append_only_verification(self, temp_skill_with_ledger):
        """K7: Verify ledger is append-only (timestamps monotonic)"""
        skill, ledger = temp_skill_with_ledger

        # Generate entries
        skill.generate_map(seed=111, game_id="game_001")

        # Verify append-only
        is_append_only = ledger.verify_append_only()
        assert is_append_only is True

    def test_ledger_stats(self, temp_skill_with_ledger):
        """K7: Get ledger statistics"""
        skill, ledger = temp_skill_with_ledger

        # Generate maps
        for i in range(5):
            skill.generate_map(seed=111 + i, game_id=f"game_{i:03d}")

        # Get stats
        stats = ledger.get_ledger_stats()

        assert stats["total_entries"] == 5
        assert stats["unique_seeds"] == 5
        assert stats["unique_games"] == 5
        assert len(stats["rules_enforced"]) > 0

    def test_ledger_entry_retrieval(self, temp_skill_with_ledger):
        """K7: Retrieve specific entry by ID"""
        skill, ledger = temp_skill_with_ledger

        # Generate map
        result = skill.generate_map(seed=111, game_id="game_001")
        entry_id = result["ledger_entry_id"]

        # Retrieve entry
        entry = ledger.get_entry_by_id(entry_id)

        assert entry is not None
        assert entry["id"] == entry_id
        assert entry["game_id"] == "game_001"

    def test_ledger_audit(self, temp_skill_with_ledger):
        """K7: Run full ledger audit"""
        skill, ledger = temp_skill_with_ledger

        # Generate maps
        skill.generate_map(seed=111, game_id="game_001")

        # Run audit
        audit = ledger.audit_ledger()

        assert audit["append_only"] is True
        assert audit["has_entries"] is True


class TestK2K7Integration:
    """Integration: K2 Claim Workflow + K7 Ledger Reader"""

    def test_skill_generates_claim_and_ledger_entry(self, temp_skill_with_workflow):
        """
        Integration: Skill generates both claim (K2) and ledger entry (K7).

        Both must be present for complete K2+K7 workflow.
        """
        skill, workflow, ledger = temp_skill_with_workflow

        # Generate map
        result = skill.generate_map(seed=111, game_id="game_001")

        # Verify K2: Claim generated
        assert result["claim"] is not None
        assert result["claim"]["status"] == "pending"
        workflow.propose_claim(Claim(**result["claim"]))

        # Verify K7: Ledger entry created
        assert result["ledger_entry_id"] is not None
        entries = ledger.read_all_entries()
        assert len(entries) > 0

    def test_full_k2_workflow_with_k7_verification(self, temp_skill_with_workflow):
        """
        Full workflow:
        1. Skill generates map (produces claim + ledger entry)
        2. Foreman receives claim (K2)
        3. Foreman approves (K2)
        4. Ledger verified (K7)
        """
        skill, workflow, ledger = temp_skill_with_workflow

        # Step 1: Generate
        result = skill.generate_map(seed=111, game_id="game_001")

        # Step 2: Propose claim
        workflow.propose_claim(Claim(**result["claim"]))
        pending = workflow.get_pending_claims()
        assert len(pending) == 1

        # Step 3: Foreman approves
        workflow.accept_claim(
            claim_id=result["claim"]["claim_id"],
            curator="Foreman",
            reason="Map valid, hash verified"
        )
        accepted = workflow.get_accepted_claims()
        assert len(accepted) == 1

        # Step 4: Ledger verification
        entries = ledger.read_all_entries()
        assert len(entries) >= 1

        # Verify hash matches
        stored_hash = entries[0]["map_hash"]
        computed_hash = skill._compute_map_hash(result["map_data"])
        assert stored_hash == computed_hash


# Fixtures

@pytest.fixture
def temp_workflow():
    """Create temporary claim workflow"""
    temp_dir = tempfile.mkdtemp()
    workflow = ClaimWorkflow(
        pending_path=str(Path(temp_dir) / "pending.md"),
        accepted_path=str(Path(temp_dir) / "accepted.md"),
        rejected_path=str(Path(temp_dir) / "rejected.md"),
    )
    yield workflow
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_skill_with_ledger():
    """Create skill with ledger reader"""
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / "map_cache"
    ledger_path = Path(temp_dir) / "ledger.jsonl"

    skill = MapGeneratorSkill(
        cache_dir=str(cache_dir),
        ledger_path=str(ledger_path)
    )
    ledger = LedgerReader(str(ledger_path))

    yield skill, ledger

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_skill_with_workflow():
    """Create skill with both workflow and ledger"""
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / "map_cache"
    ledger_path = Path(temp_dir) / "ledger.jsonl"

    skill = MapGeneratorSkill(
        cache_dir=str(cache_dir),
        ledger_path=str(ledger_path)
    )
    workflow = ClaimWorkflow(
        pending_path=str(Path(temp_dir) / "pending.md"),
        accepted_path=str(Path(temp_dir) / "accepted.md"),
        rejected_path=str(Path(temp_dir) / "rejected.md"),
    )
    ledger = LedgerReader(str(ledger_path))

    yield skill, workflow, ledger

    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
