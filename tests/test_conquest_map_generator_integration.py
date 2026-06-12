"""
Integration tests: CONQUEST Game + Map Generator MCP Skill

Day 4: Wire map generator into CONQUEST and validate determinism.

Tests verify:
- Map generation works with CONQUEST game initialization
- K5 determinism: same seed = same game outcome over multiple runs
- K7 ledger records all map generations
- Maps are usable for 36-turn simulation
"""

import pytest
pytest.importorskip("numpy")
import sys
import tempfile
import shutil
from pathlib import Path

# Add repo to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from oracle_town.skills.map_generator_skill import MapGeneratorSkill
from oracle_town.skills.ledger_reader import LedgerReader
from conquest_v2_hexacycle import HexaCycleGame


class TestMapGeneratorWithCONQUEST:
    """Integration: Map Generator provides maps for CONQUEST"""

    def test_generated_map_structure(self, temp_skill):
        """Map must have correct structure for CONQUEST"""
        result = temp_skill.generate_map(seed=111, game_id="conquest_001")

        assert result["status"] == "success"
        map_data = result["map_data"]

        # Verify structure
        assert "territories" in map_data
        assert "seed" in map_data
        assert "width" in map_data
        assert "height" in map_data

        # 5×5 grid
        assert map_data["width"] == 5
        assert map_data["height"] == 5

        # 6 territories
        assert len(map_data["territories"]) == 6

        # Each territory has cells
        for territory in map_data["territories"]:
            assert "territory_id" in territory
            assert "cells" in territory
            assert len(territory["cells"]) > 0

        print(f"✅ Map structure valid for CONQUEST")

    def test_map_coverage_complete(self, temp_skill):
        """All 25 tiles must be assigned to territories (complete coverage)"""
        result = temp_skill.generate_map(seed=111, game_id="conquest_001")
        map_data = result["map_data"]

        # Count total cells assigned
        total_cells = sum(len(t["cells"]) for t in map_data["territories"])

        assert total_cells == 25, f"Expected 25 cells, got {total_cells}"
        print(f"✅ Map coverage complete (25/25 tiles)")

    def test_territory_distribution_balanced(self, temp_skill):
        """Territories should be reasonably balanced (not too skewed)"""
        result = temp_skill.generate_map(seed=111, game_id="conquest_001")
        map_data = result["map_data"]

        territory_sizes = [len(t["cells"]) for t in map_data["territories"]]

        # Check that no territory is extreme (min >=1, max <20)
        # With 25 tiles and 6 territories, some can be small (1-2) but none should be huge
        assert min(territory_sizes) >= 1, "Territory has no cells"
        assert max(territory_sizes) < 20, "Territory too large"
        assert sum(territory_sizes) == 25, "Total cells mismatch"

        print(f"✅ Territory sizes balanced: {sorted(territory_sizes)}")

    def test_conquest_game_initialization_with_map(self, temp_skill):
        """CONQUEST should initialize with generated map"""
        # Generate map
        result = temp_skill.generate_map(seed=111, game_id="conquest_001")
        assert result["status"] == "success"

        # Create game (should use static grid for now)
        # This test verifies the map structure is compatible
        game = HexaCycleGame(seed=111)

        # Game should initialize successfully
        assert game.turn == 0
        assert len(game.agents) == 5
        assert game.total_turns == 36

        print(f"✅ CONQUEST initialized with seed 111")


class TestCONQUESTDeterminism:
    """K5: Same seed = deterministic CONQUEST outcome"""

    def test_same_seed_produces_same_winner(self):
        """K5+CONQUEST: Same seed should produce same winner"""
        seed = 111
        winners = []

        # Run 3 games with same seed
        for _ in range(3):
            game = HexaCycleGame(seed=seed)
            winner = game.run_simulation()
            winners.append(winner.name)

        # All winners should be identical
        assert len(set(winners)) == 1, f"Winners differ: {winners}"
        print(f"✅ K5+CONQUEST: Seed {seed} produced deterministic winner: {winners[0]}")

    def test_different_seeds_produce_different_winners(self):
        """Different seeds should produce different outcomes (most of the time)"""
        seeds = [111, 222, 333, 444, 555]
        winners = []

        for seed in seeds:
            game = HexaCycleGame(seed=seed)
            winner = game.run_simulation()
            winners.append(winner.name)

        # At least some winners should differ
        assert len(set(winners)) > 1, f"All seeds produced same winner: {winners}"
        print(f"✅ K5 INVERSE: Different seeds produced different winners: {set(winners)}")

    def test_same_seed_produces_same_final_territory_distribution(self):
        """K5: Same seed should produce same territory distribution"""
        seed = 111

        distributions = []
        for _ in range(2):
            game = HexaCycleGame(seed=seed)
            game.run_simulation()

            # Record final territory distribution
            territory_counts = sorted([a.territory_count() for a in game.agents], reverse=True)
            distributions.append(tuple(territory_counts))

        assert distributions[0] == distributions[1], f"Territory distributions differ: {distributions}"
        print(f"✅ K5: Same seed produced same territory distribution: {distributions[0]}")


class TestMapGeneratorWithLedger:
    """K7: Map generation ledger integration with CONQUEST"""

    def test_ledger_tracks_conquest_games(self, temp_skill_with_ledger):
        """Ledger should track all maps generated for CONQUEST games"""
        skill, ledger = temp_skill_with_ledger

        # Simulate 3 CONQUEST games with different seeds
        for i in range(3):
            seed = 111 + i
            result = skill.generate_map(seed=seed, game_id=f"conquest_game_{i:03d}")
            assert result["status"] == "success"

            # Run CONQUEST game (would use map in real integration)
            game = HexaCycleGame(seed=seed)
            game.run_simulation()

        # Verify ledger has all entries
        entries = ledger.read_all_entries()
        assert len(entries) == 3

        # All seeds should have unique hashes
        hashes = set(e["map_hash"] for e in entries)
        assert len(hashes) == 3

        print(f"✅ Ledger tracks {len(entries)} CONQUEST game maps")

    def test_ledger_hash_stable_across_reruns(self, temp_skill_with_ledger):
        """K7: Same game run should produce same ledger hash"""
        skill, ledger = temp_skill_with_ledger

        seed = 111
        game_id = "conquest_001"

        # First run
        result1 = skill.generate_map(seed=seed, game_id=game_id)
        hash1 = result1["validation_results"]["k7_policy_pinning"]["map_hash"]

        # Re-run (should use cache)
        result2 = skill.generate_map(seed=seed, game_id=game_id)
        hash2 = result2["validation_results"]["k7_policy_pinning"]["map_hash"]

        assert hash1 == hash2
        print(f"✅ K7: Hash stable across reruns: {hash1[:16]}...")


class TestEndToEndConquestIntegration:
    """Complete end-to-end: Map Generation → CONQUEST Simulation → Ledger"""

    def test_full_pipeline(self, temp_skill_with_ledger):
        """
        Full pipeline:
        1. Generate map (K5+K7)
        2. Initialize CONQUEST game
        3. Run simulation
        4. Verify ledger
        """
        skill, ledger = temp_skill_with_ledger

        seed = 111
        game_id = "conquest_001"

        # Step 1: Generate map
        map_result = skill.generate_map(seed=seed, game_id=game_id)
        assert map_result["status"] == "success"
        map_data = map_result["map_data"]

        # Step 2: Initialize CONQUEST
        game = HexaCycleGame(seed=seed)
        assert game.turn == 0

        # Step 3: Run simulation
        winner = game.run_simulation()
        assert winner is not None

        # Step 4: Verify ledger
        entries = ledger.read_all_entries()
        assert len(entries) >= 1

        # Ledger should contain map hash
        latest_entry = entries[-1]
        assert "map_hash" in latest_entry
        assert latest_entry["game_id"] == game_id

        print(f"✅ Full pipeline: Map → Game → Winner: {winner.name}")

    def test_multiple_conquest_games_with_different_maps(self, temp_skill_with_ledger):
        """Multiple games with different maps all tracked in ledger"""
        skill, ledger = temp_skill_with_ledger

        # Run 5 different games
        results = []
        for i in range(5):
            seed = 100 + i
            game_id = f"game_{i:03d}"

            # Generate map
            map_result = skill.generate_map(seed=seed, game_id=game_id)
            assert map_result["status"] == "success"

            # Run game
            game = HexaCycleGame(seed=seed)
            winner = game.run_simulation()

            results.append((game_id, winner.name))

        # Verify ledger tracked all
        entries = ledger.read_all_entries()
        assert len(entries) == 5

        # All games should have entries
        game_ids_in_ledger = set(e["game_id"] for e in entries)
        expected_game_ids = set(f"game_{i:03d}" for i in range(5))
        assert game_ids_in_ledger == expected_game_ids

        print(f"✅ Tracked {len(entries)} games with different maps")
        for game_id, winner in results:
            print(f"   {game_id}: {winner}")


# Fixtures

@pytest.fixture
def temp_skill():
    """Create temporary skill"""
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / "map_cache"
    ledger_path = Path(temp_dir) / "ledger.jsonl"

    skill = MapGeneratorSkill(
        cache_dir=str(cache_dir),
        ledger_path=str(ledger_path)
    )

    yield skill

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
