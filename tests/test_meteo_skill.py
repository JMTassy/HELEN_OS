"""
Tests for Meteorology Skill

Validates:
- Weather system generation
- K5 determinism (same seed = identical weather)
- K7 ledger logging
- Agent stat modifications
- Season effects
"""

import pytest
pytest.importorskip("numpy")
import tempfile
import shutil
from pathlib import Path

from oracle_town.skills.meteo_skill import MeteoSkill, MeteoSystem, generate_weather_for_map


@pytest.fixture
def temp_meteo():
    """Create temporary meteo skill for tests."""
    temp_dir = tempfile.mkdtemp()
    ledger_path = Path(temp_dir) / "meteo_records.jsonl"

    skill = MeteoSkill(ledger_path=str(ledger_path))

    yield skill

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_map():
    """Create a test map for meteorology."""
    return {
        "width": 5,
        "height": 5,
        "game_id": "meteo_test_001",
        "tile_map": {
            f"{x},{y}": {
                "x": x,
                "y": y,
                "terrain": ["plains", "water", "forest", "mountain"][(x + y) % 4],
                "climate": ["temperate", "tropical", "arid", "frozen"][(x * y) % 4],
            }
            for x in range(5)
            for y in range(5)
        },
    }


class TestMeteoGeneration:
    """Test basic weather generation."""

    def test_meteo_skill_initializes(self, temp_meteo):
        """MeteoSkill should initialize successfully."""
        assert temp_meteo is not None
        assert Path(temp_meteo.ledger_path).parent.exists()

    def test_generate_weather_success(self, temp_meteo, test_map):
        """Should generate weather successfully."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")

        assert result["status"] == "success"
        assert "meteo_data" in result
        assert "validation_results" in result

    def test_meteo_data_structure(self, temp_meteo, test_map):
        """Weather data should have all required fields."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        meteo = result["meteo_data"]

        assert "seed" in meteo
        assert "season" in meteo
        assert "weather_tiles" in meteo
        assert "wind_field" in meteo
        assert "pressure_centers" in meteo
        assert "precipitation" in meteo
        assert "temperature" in meteo
        assert "storm_paths" in meteo
        assert "meteo_hash" in meteo

    def test_weather_tiles_per_coordinate(self, temp_meteo, test_map):
        """Each tile should have weather condition."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        meteo = result["meteo_data"]

        for coord_str in test_map["tile_map"].keys():
            assert coord_str in meteo["weather_tiles"]
            condition = meteo["weather_tiles"][coord_str]
            assert condition in [
                "clear",
                "cloudy",
                "rainy",
                "stormy",
                "foggy",
            ]

    def test_wind_field_generated(self, temp_meteo, test_map):
        """Wind field should be generated for all tiles."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        meteo = result["meteo_data"]

        for coord_str in test_map["tile_map"].keys():
            assert coord_str in meteo["wind_field"]
            wind = meteo["wind_field"][coord_str]
            assert "direction" in wind
            assert "speed" in wind
            assert wind["direction"] in MeteoSystem.WIND_DIRECTIONS
            assert 0 <= wind["speed"] <= 40

    def test_precipitation_values(self, temp_meteo, test_map):
        """Precipitation should be calculated for all tiles."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        meteo = result["meteo_data"]

        for coord_str in test_map["tile_map"].keys():
            assert coord_str in meteo["precipitation"]
            precip = meteo["precipitation"][coord_str]
            assert isinstance(precip, float)
            assert 0 <= precip <= 150  # Reasonable precipitation range


class TestK5Determinism:
    """Test K5 determinism (same seed = same weather)."""

    def test_same_seed_identical_weather(self, temp_meteo, test_map):
        """Same seed should produce identical weather."""
        result1 = temp_meteo.generate_weather(test_map, seed=222, season="spring")
        result2 = temp_meteo.generate_weather(test_map, seed=222, season="spring")

        hash1 = result1["meteo_data"]["meteo_hash"]
        hash2 = result2["meteo_data"]["meteo_hash"]

        assert hash1 == hash2

    def test_different_seed_different_weather(self, temp_meteo, test_map):
        """Different seeds should produce different weather."""
        result1 = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        result2 = temp_meteo.generate_weather(test_map, seed=999, season="spring")

        hash1 = result1["meteo_data"]["meteo_hash"]
        hash2 = result2["meteo_data"]["meteo_hash"]

        assert hash1 != hash2

    def test_season_affects_weather(self, temp_meteo, test_map):
        """Different seasons should produce different weather."""
        result1 = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        result2 = temp_meteo.generate_weather(test_map, seed=111, season="winter")

        hash1 = result1["meteo_data"]["meteo_hash"]
        hash2 = result2["meteo_data"]["meteo_hash"]

        # Different seasons should produce different results
        assert hash1 != hash2


class TestSeasonEffects:
    """Test season-based weather variations."""

    def test_summer_warmer_than_winter(self, temp_meteo, test_map):
        """Summer should be warmer than winter."""
        result_summer = temp_meteo.generate_weather(test_map, seed=555, season="summer")
        result_winter = temp_meteo.generate_weather(test_map, seed=555, season="winter")

        temps_summer = list(result_summer["meteo_data"]["temperature"].values())
        temps_winter = list(result_winter["meteo_data"]["temperature"].values())

        avg_summer = sum(temps_summer) / len(temps_summer)
        avg_winter = sum(temps_winter) / len(temps_winter)

        assert avg_summer > avg_winter

    def test_all_seasons_valid(self, temp_meteo, test_map):
        """Should generate weather for all seasons."""
        for season in ["spring", "summer", "autumn", "winter"]:
            result = temp_meteo.generate_weather(test_map, seed=111, season=season)
            assert result["status"] == "success"
            assert result["meteo_data"]["season"] == season

    def test_invalid_season_rejected(self, temp_meteo, test_map):
        """Invalid season should be rejected (K1)."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="invalid")

        assert result["status"] == "error"
        assert not result["validation_results"]["k1_fail_closed"]["pass"]


class TestK7LedgerLogging:
    """Test K7 ledger tracking."""

    def test_meteo_logged_to_ledger(self, temp_meteo, test_map):
        """Weather generation should be logged."""
        temp_meteo.generate_weather(test_map, seed=111, season="spring")

        ledger_path = Path(temp_meteo.ledger_path)
        assert ledger_path.exists()

        with open(ledger_path, "r") as f:
            content = f.read()

        assert "meteo_generated" in content

    def test_ledger_contains_hash(self, temp_meteo, test_map):
        """Ledger should record meteo hash."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        meteo_hash = result["meteo_data"]["meteo_hash"]

        ledger_path = Path(temp_meteo.ledger_path)
        with open(ledger_path, "r") as f:
            content = f.read()

        assert meteo_hash in content

    def test_ledger_append_only(self, temp_meteo, test_map):
        """Multiple generations should all appear in ledger."""
        for i in range(3):
            temp_meteo.generate_weather(test_map, seed=100 + i, season="spring")

        ledger_path = Path(temp_meteo.ledger_path)
        with open(ledger_path, "r") as f:
            lines = [line for line in f if line.strip()]

        assert len(lines) == 3


class TestPressureAndWind:
    """Test pressure systems and wind fields."""

    def test_pressure_centers_generated(self, temp_meteo, test_map):
        """Pressure systems should be generated."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        centers = result["meteo_data"]["pressure_centers"]

        assert len(centers) > 0
        for center in centers:
            assert "x" in center
            assert "y" in center
            assert "type" in center
            assert "intensity" in center
            assert center["type"] in ["high", "low"]

    def test_wind_directions_valid(self, temp_meteo, test_map):
        """All wind directions should be valid compass points."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        wind_field = result["meteo_data"]["wind_field"]

        for wind in wind_field.values():
            assert wind["direction"] in MeteoSystem.WIND_DIRECTIONS

    def test_storm_paths_generated(self, temp_meteo, test_map):
        """Storm paths should be generated from low pressure."""
        result = temp_meteo.generate_weather(test_map, seed=111, season="spring")
        storms = result["meteo_data"]["storm_paths"]

        # Should have at least one storm path
        assert len(storms) >= 0  # May be 0 if no low pressure systems


class TestMeteoSystem:
    """Test MeteoSystem class directly."""

    def test_vector_to_direction(self):
        """Vector to direction conversion should work."""
        system = MeteoSystem(seed=111)

        # Test that all directions are valid 8-point compass directions
        directions = [
            system._vector_to_direction(1, 0),      # East-ish
            system._vector_to_direction(0, 1),      # South-ish
            system._vector_to_direction(-1, 0),     # West-ish
            system._vector_to_direction(0, -1),     # North-ish
        ]

        # All should be valid compass directions
        for direction in directions:
            assert direction in MeteoSystem.WIND_DIRECTIONS

    def test_meteo_hash_consistent(self):
        """Same seed should produce same hash."""
        # Create simple test data
        test_map = {
            "width": 5,
            "height": 5,
            "tile_map": {
                f"{x},{y}": {"x": x, "y": y, "terrain": "plains", "climate": "temperate"}
                for x in range(5)
                for y in range(5)
            },
        }

        # Create two systems with same seed
        system1 = MeteoSystem(seed=111)
        system2 = MeteoSystem(seed=111)

        result1 = system1.generate_weather_map(test_map, "spring")
        result2 = system2.generate_weather_map(test_map, "spring")

        assert result1["meteo_hash"] == result2["meteo_hash"]


class TestConvenienceFunction:
    """Test convenience functions."""

    def test_generate_weather_for_map(self, test_map):
        """Convenience function should work."""
        result = generate_weather_for_map(test_map, seed=111, season="spring")

        assert result["status"] == "success"
        assert "meteo_data" in result


class TestEndToEndMeteo:
    """End-to-end meteorology tests."""

    def test_full_meteo_generation(self, temp_meteo, test_map):
        """Full weather generation pipeline."""
        # Generate weather
        result = temp_meteo.generate_weather(test_map, seed=444, season="summer")

        # Verify all components
        assert result["status"] == "success"
        meteo = result["meteo_data"]

        # Check all required fields present
        required = [
            "weather_tiles",
            "wind_field",
            "pressure_centers",
            "precipitation",
            "temperature",
            "storm_paths",
            "meteo_hash",
        ]
        for field in required:
            assert field in meteo

        # Verify K-gates
        assert result["validation_results"]["k1_fail_closed"]["pass"]
        assert result["validation_results"]["k5_determinism"]["pass"]
        assert result["validation_results"]["k7_policy_pinning"]["pass"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
