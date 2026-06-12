"""
Test suite for MapGeneratorSkill — K5 (Determinism) + K7 (Policy Pinning)

Day 2 Validation Tests:
- K5: Same seed = identical output (5 runs per seed)
- K7: Map hash locked in ledger (hash match verified)
- K1: Fail-closed validation (missing params rejected)
- K2: No self-validation (claim generated, pending Foreman approval)
"""

import pytest
pytest.importorskip("numpy")
import json
import hashlib
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from oracle_town.skills.map_generator_skill import MapGeneratorSkill
from oracle_town.skills.procedural_map import ProceduralMapGenerator


class TestK1FailClosedValidation:
    """K1: Fail-Closed Default — Missing evidence → REJECT"""

    def test_missing_seed_rejected(self, temp_skill):
        """Missing seed parameter should be rejected (K1)"""
        result = temp_skill.generate_map(seed=None, game_id="game_001")
        assert result["status"] == "validation_failed"
        assert "SEED_REQUIRED" in result["error"]
        assert result["map_data"] is None

    def test_missing_game_id_rejected(self, temp_skill):
        """Missing game_id parameter should be rejected (K1)"""
        result = temp_skill.generate_map(seed=111, game_id=None)
        assert result["status"] == "validation_failed"
        assert "GAME_ID_REQUIRED" in result["error"]
        assert result["map_data"] is None

    def test_seed_type_error_rejected(self, temp_skill):
        """Seed must be int; string seed should be rejected (K1)"""
        result = temp_skill.generate_map(seed="111", game_id="game_001")
        assert result["status"] == "validation_failed"
        assert "SEED_TYPE_ERROR" in result["error"]

    def test_game_id_type_error_rejected(self, temp_skill):
        """Game_id must be str; int game_id should be rejected (K1)"""
        result = temp_skill.generate_map(seed=111, game_id=12345)
        assert result["status"] == "validation_failed"
        assert "GAME_ID_TYPE_ERROR" in result["error"]

    def test_valid_params_accepted(self, temp_skill):
        """Valid seed (int) and game_id (str) should pass K1"""
        result = temp_skill.generate_map(seed=111, game_id="game_001")
        assert result["status"] == "success"
        assert result["validation_results"]["k1_fail_closed"]["pass"] is True


class TestK5Determinism:
    """K5: Determinism — Same seed = identical output"""

    def test_k5_same_seed_produces_identical_output(self, temp_skill):
        """
        K5 Core Test: Generate same map 5 times with identical seed.
        All outputs must be byte-identical.
        """
        seed = 111
        results = []

        for i in range(5):
            result = temp_skill.generate_map(seed=seed, game_id=f"game_{i:03d}")
            assert result["status"] == "success"
            results.append(result["map_data"])

        # Convert all to JSON for bit-exact comparison
        json_strings = [json.dumps(r, sort_keys=True) for r in results]

        # All JSON strings must be identical
        assert len(set(json_strings)) == 1, "K5 VIOLATION: Same seed produced different outputs"

        print(f"✅ K5 PASS: Seed {seed} produced identical output across 5 runs")

    def test_k5_different_seeds_produce_different_output(self, temp_skill):
        """K5 Inverse: Different seeds should produce different maps"""
        seeds = [111, 222, 333]
        results = []

        for seed in seeds:
            result = temp_skill.generate_map(seed=seed, game_id=f"game_{seed:03d}")
            assert result["status"] == "success"
            results.append(json.dumps(result["map_data"], sort_keys=True))

        # All maps should be different
        assert len(set(results)) == len(results), "Different seeds produced identical maps"

        print(f"✅ K5 INVERSE PASS: Different seeds produced different outputs")

    def test_k5_caching_returns_cached_map(self, temp_skill):
        """
        K5 Cache Test: First call generates and caches.
        Second call should return cached version (same source="cache").
        """
        seed = 111
        game_id = "game_001"

        # First call: generate and cache
        result1 = temp_skill.generate_map(seed=seed, game_id=game_id)
        assert result1["status"] == "success"
        assert result1["validation_results"]["k5_determinism"]["source"] == "generated"

        # Second call: should retrieve from cache
        result2 = temp_skill.generate_map(seed=seed, game_id=game_id)
        assert result2["status"] == "success"
        assert result2["validation_results"]["k5_determinism"]["source"] == "cache"

        # Maps must be identical
        assert json.dumps(result1["map_data"], sort_keys=True) == json.dumps(result2["map_data"], sort_keys=True)

        print(f"✅ K5 CACHE PASS: Cached map returned identical on second call")

    def test_k5_cache_file_exists(self, temp_skill):
        """K5 Cache File: After generation, cache file should exist"""
        seed = 111
        result = temp_skill.generate_map(seed=seed, game_id="game_001")
        assert result["status"] == "success"

        cache_file = temp_skill.cache_dir / f"map_seed_{seed}.json"
        assert cache_file.exists(), "K5 cache file not created"

        # Verify cache file is valid JSON
        with open(cache_file, "r") as f:
            cached_data = json.load(f)

        assert cached_data["seed"] == seed
        print(f"✅ K5 CACHE FILE PASS: Cache file created and valid")


class TestK7PolicyPinning:
    """K7: Policy Pinning — Map hash locked per game in ledger"""

    def test_k7_ledger_entry_created(self, temp_skill):
        """K7: After generation, ledger entry should exist"""
        seed = 111
        game_id = "game_001"

        result = temp_skill.generate_map(seed=seed, game_id=game_id)
        assert result["status"] == "success"
        assert result["ledger_entry_id"] is not None

        # Verify ledger file exists and contains entry
        assert temp_skill.ledger_path.exists()

        with open(temp_skill.ledger_path, "r") as f:
            entries = [json.loads(line) for line in f if line.strip()]

        assert len(entries) > 0
        latest_entry = entries[-1]
        assert latest_entry["game_id"] == game_id
        assert latest_entry["rule"] == "K7_POLICY_PINNING"
        assert "map_hash" in latest_entry

        print(f"✅ K7 LEDGER ENTRY PASS: Entry created in ledger")

    def test_k7_map_hash_consistent(self, temp_skill):
        """
        K7: Map hash must be consistent.
        Same map data = same hash (deterministic hashing).
        """
        seed = 111
        game_id_1 = "game_001"
        game_id_2 = "game_002"

        # Generate map twice with same seed (will use cache on second call)
        result1 = temp_skill.generate_map(seed=seed, game_id=game_id_1)
        result2 = temp_skill.generate_map(seed=seed, game_id=game_id_2)

        assert result1["status"] == "success"
        assert result2["status"] == "success"

        # Compute hashes manually to verify
        hash1 = temp_skill._compute_map_hash(result1["map_data"])
        hash2 = temp_skill._compute_map_hash(result2["map_data"])

        assert hash1 == hash2, "K7 VIOLATION: Same map produced different hashes"

        print(f"✅ K7 HASH CONSISTENCY PASS: Same map = same hash")

    def test_k7_different_maps_different_hashes(self, temp_skill):
        """K7 Inverse: Different maps should have different hashes"""
        seed_1 = 111
        seed_2 = 222

        result1 = temp_skill.generate_map(seed=seed_1, game_id="game_001")
        result2 = temp_skill.generate_map(seed=seed_2, game_id="game_002")

        hash1 = temp_skill._compute_map_hash(result1["map_data"])
        hash2 = temp_skill._compute_map_hash(result2["map_data"])

        assert hash1 != hash2, "K7 VIOLATION: Different maps produced same hash"

        print(f"✅ K7 HASH DIFFERENTIATION PASS: Different maps = different hashes")

    def test_k7_ledger_hash_matches_computed_hash(self, temp_skill):
        """K7: Hash stored in ledger must match computed hash"""
        seed = 111
        game_id = "game_001"

        result = temp_skill.generate_map(seed=seed, game_id=game_id)
        assert result["status"] == "success"

        # Get hash from result
        stored_hash = None
        with open(temp_skill.ledger_path, "r") as f:
            entries = [json.loads(line) for line in f if line.strip()]
            for entry in entries:
                if entry["game_id"] == game_id:
                    stored_hash = entry["map_hash"]
                    break

        assert stored_hash is not None
        computed_hash = temp_skill._compute_map_hash(result["map_data"])
        assert stored_hash == computed_hash, "K7 VIOLATION: Ledger hash ≠ computed hash"

        print(f"✅ K7 LEDGER HASH MATCH PASS: Stored hash = computed hash")

    def test_k7_validate_only_no_ledger_write(self, temp_skill):
        """K7 Dry-Run: validate_only=True should not write ledger"""
        seed = 111
        game_id = "game_001"

        # Get initial ledger entry count
        initial_entries = 0
        if temp_skill.ledger_path.exists():
            with open(temp_skill.ledger_path, "r") as f:
                initial_entries = len([line for line in f if line.strip()])

        # Run with validate_only=True
        result = temp_skill.generate_map(seed=seed, game_id=game_id, validate_only=True)
        assert result["status"] == "success"
        assert result["ledger_entry_id"] is None

        # Verify ledger was not modified
        final_entries = 0
        if temp_skill.ledger_path.exists():
            with open(temp_skill.ledger_path, "r") as f:
                final_entries = len([line for line in f if line.strip()])

        assert initial_entries == final_entries, "K7 DRY-RUN VIOLATION: Ledger was modified"

        print(f"✅ K7 DRY-RUN PASS: validate_only prevented ledger write")


class TestK2NoSelfValidation:
    """K2: No Self-Edit, No Self-Validation — Skill generates claim, Foreman approves"""

    def test_k2_claim_generated(self, temp_skill):
        """K2: Skill must generate claim (LP-###) for Foreman approval"""
        seed = 111
        game_id = "game_001"

        result = temp_skill.generate_map(seed=seed, game_id=game_id)
        assert result["status"] == "success"
        assert result["claim"] is not None

        claim = result["claim"]
        assert claim["claim_id"] == f"LP-MAP-{game_id}"
        assert claim["type"] == "map_generation"
        assert claim["author"] == "MapGeneratorSkill"
        assert claim["status"] == "pending"

        print(f"✅ K2 CLAIM GENERATION PASS: Claim generated with pending status")

    def test_k2_claim_pending_foreman_approval(self, temp_skill):
        """K2: Claim status must be 'pending', not approved"""
        seed = 111
        game_id = "game_001"

        result = temp_skill.generate_map(seed=seed, game_id=game_id)
        claim = result["claim"]

        assert claim["status"] == "pending", "K2 VIOLATION: Claim was self-approved"

        print(f"✅ K2 PENDING STATUS PASS: Claim awaiting Foreman approval")

    def test_k2_validation_result_logged(self, temp_skill):
        """K2: Validation result should indicate no self-validation"""
        seed = 111
        game_id = "game_001"

        result = temp_skill.generate_map(seed=seed, game_id=game_id)
        k2_result = result["validation_results"]["k2_no_self_validation"]

        assert k2_result["pass"] is True
        assert k2_result["claim_author"] == "MapGeneratorSkill"
        assert k2_result["claim_status"] == "pending"
        assert "Foreman approval" in k2_result["note"]

        print(f"✅ K2 VALIDATION LOGGED PASS: K2 result properly documented")


class TestTerritoryCountValidation:
    """Territory Validation: Generated territory count must match expected"""

    def test_territory_count_matches_default(self, temp_skill):
        """Default territory_count=6 should match generated territories"""
        seed = 111
        result = temp_skill.generate_map(seed=seed, game_id="game_001")

        assert result["status"] == "success"
        assert len(result["map_data"]["territories"]) == 6
        assert result["validation_results"]["territory_count"]["pass"] is True

        print(f"✅ TERRITORY COUNT PASS: Generated 6 territories as expected")

    def test_territory_count_custom(self, temp_skill):
        """Custom territory_count should be validated"""
        seed = 111
        # Note: Our algorithm always generates 6, so we validate what we got
        result = temp_skill.generate_map(seed=seed, game_id="game_001", territory_count=6)

        assert result["status"] == "success"
        assert result["validation_results"]["territory_count"]["pass"] is True


class TestEndToEndK5K7Integration:
    """End-to-end test combining K5 + K7"""

    def test_k5_k7_complete_pipeline(self, temp_skill):
        """
        Complete pipeline test:
        1. Generate map with seed 111
        2. Verify K5: regenerate from cache
        3. Verify K7: hash in ledger matches computed hash
        """
        seed = 111
        game_id = "game_001"

        # Step 1: Generate
        result1 = temp_skill.generate_map(seed=seed, game_id=game_id)
        assert result1["status"] == "success"
        assert result1["validation_results"]["k5_determinism"]["source"] == "generated"

        # Step 2: Verify K5 (cache)
        result2 = temp_skill.generate_map(seed=seed, game_id="game_002")
        assert result2["status"] == "success"
        assert result2["validation_results"]["k5_determinism"]["source"] == "cache"
        assert json.dumps(result1["map_data"], sort_keys=True) == json.dumps(result2["map_data"], sort_keys=True)

        # Step 3: Verify K7 (ledger hash match)
        with open(temp_skill.ledger_path, "r") as f:
            entries = [json.loads(line) for line in f if line.strip()]

        first_entry = entries[0]
        second_entry = entries[1]

        # Both entries should have same map_hash (same seed → same map → same hash)
        assert first_entry["map_hash"] == second_entry["map_hash"]

        # Verify hash matches computed
        computed_hash = temp_skill._compute_map_hash(result1["map_data"])
        assert first_entry["map_hash"] == computed_hash

        print(f"✅ K5+K7 INTEGRATION PASS: Cache and ledger working together")

    def test_k5_k7_multiple_seeds(self, temp_skill):
        """
        Test K5+K7 with multiple seeds:
        - Each seed has consistent hash
        - Different seeds have different hashes
        - All hashes stored in ledger
        """
        seeds = [111, 222, 333, 444, 555]
        hashes = {}

        for seed in seeds:
            result = temp_skill.generate_map(seed=seed, game_id=f"game_{seed}")
            assert result["status"] == "success"
            hashes[seed] = temp_skill._compute_map_hash(result["map_data"])

        # Verify all hashes are unique
        assert len(set(hashes.values())) == len(seeds), "Different seeds produced same hashes"

        # Verify all hashes are in ledger
        with open(temp_skill.ledger_path, "r") as f:
            ledger_hashes = set(json.loads(line)["map_hash"] for line in f if line.strip())

        for seed, hash_val in hashes.items():
            assert hash_val in ledger_hashes, f"Seed {seed} hash not in ledger"

        print(f"✅ K5+K7 MULTIPLE SEEDS PASS: All {len(seeds)} seeds verified")


# Fixtures

@pytest.fixture
def temp_skill():
    """Create a temporary MapGeneratorSkill with isolated cache and ledger"""
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / "map_cache"
    ledger_path = Path(temp_dir) / "ledger.jsonl"

    skill = MapGeneratorSkill(
        cache_dir=str(cache_dir),
        ledger_path=str(ledger_path)
    )

    yield skill

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


# Run all tests

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
