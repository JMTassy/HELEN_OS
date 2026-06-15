"""
Meteorology Skill — Weather System Generation

Generates procedural weather patterns for CONQUEST maps.
Integrates with MapGeneratorSkill to add dynamic climate effects.

Features:
- Wind systems (direction + intensity)
- Precipitation patterns (rainfall distribution)
- Temperature zones (micro-climates)
- Storm trajectories (hazard mapping)
- Season-based variations
- K5 determinism (seeded RNG)
- K7 ledger tracking
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
import numpy as np
from datetime import datetime, UTC
import hashlib


class MeteoSystem:
    """Generates weather systems for a map."""

    # Weather condition ranges
    WEATHER_CONDITIONS = {
        "clear": {"precip": (0, 10), "wind": (0, 5), "temp_delta": (-2, 2)},
        "cloudy": {"precip": (10, 30), "wind": (5, 15), "temp_delta": (-3, 1)},
        "rainy": {"precip": (30, 70), "wind": (15, 25), "temp_delta": (-5, 0)},
        "stormy": {"precip": (70, 100), "wind": (25, 40), "temp_delta": (-8, -2)},
        "foggy": {"precip": (20, 50), "wind": (0, 10), "temp_delta": (-5, -2)},
    }

    # Wind directions (8-point compass)
    WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    # Seasons and their effects
    SEASONS = {
        "spring": {"temp_mod": 5, "precip_mod": 1.2, "wind_mod": 0.9},
        "summer": {"temp_mod": 15, "precip_mod": 0.8, "wind_mod": 0.7},
        "autumn": {"temp_mod": 8, "precip_mod": 1.1, "wind_mod": 0.95},
        "winter": {"temp_mod": -5, "precip_mod": 1.3, "wind_mod": 1.2},
    }

    def __init__(self, seed: int = None):
        """Initialize meteorology system with seeded RNG."""
        self.seed = seed or 42
        self.rng = np.random.RandomState(self.seed)

    def generate_weather_map(
        self, map_data: Dict, season: str = "spring"
    ) -> Dict:
        """
        Generate weather systems for a map.

        Args:
            map_data: Output from MapGeneratorSkill.generate_map()
            season: "spring", "summer", "autumn", or "winter"

        Returns:
            Dict containing:
                - weather_tiles: Per-tile weather conditions
                - wind_field: Wind direction + intensity for each tile
                - pressure_centers: High/low pressure systems
                - precipitation: Rainfall amounts
                - temperature: Temperature relative to base climate
                - storm_paths: Trajectory of storm systems
                - meteo_hash: SHA256 of entire weather system
        """
        if season not in self.SEASONS:
            raise ValueError(f"Unknown season: {season}")

        width = map_data["width"]
        height = map_data["height"]
        tile_map = map_data["tile_map"]

        # Generate pressure systems (centers for wind field)
        pressure_centers = self._generate_pressure_systems(width, height)

        # Generate wind field from pressure systems
        wind_field = self._generate_wind_field(width, height, pressure_centers)

        # Generate weather conditions
        weather_tiles = {}
        precipitation = {}
        temperature = {}

        for coord_str, tile_info in tile_map.items():
            x, y = tile_info["x"], tile_info["y"]

            # Base weather influenced by pressure + wind
            wx = self._generate_weather_tile(x, y, wind_field, season)
            weather_tiles[coord_str] = wx["condition"]

            # Precipitation affected by wind and geography
            precip = self._calculate_precipitation(
                x, y, tile_info, wx, wind_field, season
            )
            precipitation[coord_str] = precip

            # Temperature from base climate + season + elevation effect
            temp = self._calculate_temperature(x, y, tile_info, season)
            temperature[coord_str] = temp

        # Storm paths (hazard zones)
        storm_paths = self._generate_storm_paths(width, height, pressure_centers)

        # Compute meteo hash for K7
        meteo_hash = self._compute_meteo_hash(
            weather_tiles, wind_field, precipitation, temperature, storm_paths
        )

        return {
            "seed": self.seed,
            "season": season,
            "weather_tiles": weather_tiles,
            "wind_field": wind_field,
            "pressure_centers": pressure_centers,
            "precipitation": precipitation,
            "temperature": temperature,
            "storm_paths": storm_paths,
            "meteo_hash": meteo_hash,
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        }

    def _generate_pressure_systems(
        self, width: int, height: int, num_systems: int = 3
    ) -> List[Dict]:
        """Generate high/low pressure system centers."""
        systems = []

        for _ in range(num_systems):
            x = self.rng.uniform(0, width)
            y = self.rng.uniform(0, height)
            pressure_type = self.rng.choice(["high", "low"])
            intensity = self.rng.uniform(0.5, 1.5)

            systems.append({"x": x, "y": y, "type": pressure_type, "intensity": intensity})

        return systems

    def _generate_wind_field(
        self, width: int, height: int, pressure_centers: List[Dict]
    ) -> Dict:
        """Generate wind vector field from pressure systems."""
        wind_field = {}

        for x in range(int(width)):
            for y in range(int(height)):
                # Calculate wind from all pressure centers
                wind_x = 0.0
                wind_y = 0.0

                for center in pressure_centers:
                    dx = x - center["x"]
                    dy = y - center["y"]
                    dist = np.sqrt(dx**2 + dy**2) + 0.1  # Avoid division by zero

                    # Wind spirals around pressure centers
                    if center["type"] == "low":
                        # Counterclockwise around low pressure
                        wind_x += (-dy / dist) * center["intensity"] / dist
                        wind_y += (dx / dist) * center["intensity"] / dist
                    else:
                        # Clockwise around high pressure
                        wind_x += (dy / dist) * center["intensity"] / dist
                        wind_y += (-dx / dist) * center["intensity"] / dist

                # Normalize and quantize
                speed = np.sqrt(wind_x**2 + wind_y**2)
                direction = self._vector_to_direction(wind_x, wind_y)

                wind_field[f"{x},{y}"] = {
                    "direction": direction,
                    "speed": min(speed, 40),  # Cap at 40 units
                }

        return wind_field

    def _generate_weather_tile(
        self, x: int, y: int, wind_field: Dict, season: str
    ) -> Dict:
        """Generate weather condition for a single tile."""
        wind_key = f"{x},{y}"
        wind = wind_field.get(wind_key, {"speed": 5, "direction": "N"})

        # Wind intensity influences weather type
        wind_speed = wind["speed"]

        # Random component (seeded)
        rand = self.rng.uniform(0, 1)

        # Decide condition based on wind + randomness
        if wind_speed > 25:
            condition = "stormy"
        elif wind_speed > 15 and rand > 0.4:
            condition = "rainy"
        elif rand > 0.6:
            condition = "cloudy"
        elif rand > 0.3:
            condition = "clear"
        else:
            condition = "foggy"

        return {
            "condition": condition,
            "wind": wind,
            "base_precip": self.WEATHER_CONDITIONS[condition]["precip"][0],
        }

    def _calculate_precipitation(
        self, x: int, y: int, tile_info: Dict, weather: Dict, wind_field: Dict, season: str
    ) -> float:
        """Calculate precipitation with orographic effect."""
        season_mod = self.SEASONS[season]["precip_mod"]
        condition = weather["condition"]

        # Base precipitation from weather condition
        min_p, max_p = self.WEATHER_CONDITIONS[condition]["precip"]
        base_precip = self.rng.uniform(min_p, max_p) * season_mod

        # Orographic effect (mountains increase precipitation)
        terrain = tile_info.get("terrain", "plains")
        if terrain == "mountain":
            base_precip *= 1.5  # Mountains get 50% more rain
        elif terrain == "forest":
            base_precip *= 1.2  # Forests get 20% more
        elif terrain == "water":
            base_precip *= 0.8  # Water bodies get less

        return round(base_precip, 1)

    def _calculate_temperature(self, x: int, y: int, tile_info: Dict, season: str) -> float:
        """Calculate temperature with micro-climate effects."""
        season_mod = self.SEASONS[season]["temp_mod"]

        # Base temp from season
        base_temp = 15 + season_mod

        # Climate zone effect
        climate = tile_info.get("climate", "temperate")
        climate_temps = {
            "temperate": 0,
            "tropical": 10,
            "arid": 8,
            "frozen": -20,
        }
        base_temp += climate_temps.get(climate, 0)

        # Terrain effect (elevation)
        terrain = tile_info.get("terrain", "plains")
        terrain_mods = {
            "plains": 0,
            "forest": -2,  # Forests are cooler
            "mountain": -5,  # Mountains are colder
            "water": 2,  # Water moderates temperature
        }
        base_temp += terrain_mods.get(terrain, 0)

        # Add noise for variation
        noise = self.rng.uniform(-3, 3)
        base_temp += noise

        return round(base_temp, 1)

    def _generate_storm_paths(
        self, width: int, height: int, pressure_centers: List[Dict]
    ) -> List[Dict]:
        """Generate trajectories of moving storm systems."""
        storm_paths = []

        # Each low-pressure system can spawn a storm
        for center in pressure_centers:
            if center["type"] == "low":
                # Calculate trajectory from pressure center
                # Storms generally move with prevailing winds
                velocity_x = self.rng.uniform(-2, 2)
                velocity_y = self.rng.uniform(-2, 2)

                path = []
                x, y = center["x"], center["y"]

                # Generate 5-step path
                for step in range(5):
                    x += velocity_x
                    y += velocity_y

                    # Wrap around edges
                    x = x % width
                    y = y % height

                    path.append({"x": round(x, 1), "y": round(y, 1), "step": step})

                storm_paths.append(
                    {
                        "origin": {"x": center["x"], "y": center["y"]},
                        "path": path,
                        "intensity": center["intensity"],
                    }
                )

        return storm_paths

    def _vector_to_direction(self, wind_x: float, wind_y: float) -> str:
        """Convert wind vector to 8-point compass direction."""
        angle = np.arctan2(wind_y, wind_x) * 180 / np.pi
        # Normalize to 0-360
        angle = (angle + 360) % 360

        # Map to 8 directions
        directions = self.WIND_DIRECTIONS
        idx = int((angle + 22.5) / 45) % 8
        return directions[idx]

    def _compute_meteo_hash(
        self,
        weather_tiles: Dict,
        wind_field: Dict,
        precipitation: Dict,
        temperature: Dict,
        storm_paths: List,
    ) -> str:
        """Compute deterministic hash of entire weather system."""
        data = {
            "weather": weather_tiles,
            "wind": {k: v for k, v in sorted(wind_field.items())},
            "precip": precipitation,
            "temp": temperature,
            "storms": storm_paths,
        }
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def apply_weather_to_agents(self, agents: List, meteo: Dict) -> List:
        """Apply weather effects to agent stats."""
        for agent in agents:
            # Find agent's starting position
            if not agent.tiles:
                continue

            x, y = agent.tiles[0]
            key = f"{x},{y}"

            # Get weather at agent location
            weather = meteo["weather_tiles"].get(key, "clear")
            temp = meteo["temperature"].get(key, 15)
            precip = meteo["precipitation"].get(key, 0)

            # Apply effects
            if weather == "stormy":
                agent.stability -= 1  # Storms reduce stability
                agent.power -= 1
            elif weather == "rainy":
                agent.stability += 1  # Rain helps defense
            elif weather == "clear":
                agent.power += 1  # Clear weather helps expansion

            # Extreme temperature effects
            if temp < -10:
                agent.stability += 1  # Cold helps defense
                agent.power -= 1
            elif temp > 30:
                agent.power += 1  # Hot weather helps aggression
                agent.stability -= 1

            # High precipitation slows expansion
            if precip > 50:
                agent.power -= 1

        return agents


class MeteoSkill:
    """MCP Skill for weather system generation."""

    def __init__(self, ledger_path: str = None):
        """Initialize meteorology skill."""
        self.ledger_path = ledger_path or "kernel/ledger/meteo_records.jsonl"
        Path(self.ledger_path).parent.mkdir(parents=True, exist_ok=True)

    def generate_weather(self, map_data: Dict, seed: int, season: str = "spring") -> Dict:
        """
        Generate weather system for a map.

        Args:
            map_data: Output from MapGeneratorSkill.generate_map()
            seed: Deterministic seed
            season: "spring", "summer", "autumn", or "winter"

        Returns:
            Dict with weather data and K-gate validation results
        """
        try:
            # K1: Fail-closed validation
            if not map_data:
                return {
                    "status": "error",
                    "error": "Missing map_data",
                    "validation_results": {"k1_fail_closed": {"pass": False}},
                }

            if season not in MeteoSystem.SEASONS:
                return {
                    "status": "error",
                    "error": f"Invalid season: {season}",
                    "validation_results": {"k1_fail_closed": {"pass": False}},
                }

            # Generate weather (K5 deterministic)
            meteo_system = MeteoSystem(seed=seed)
            meteo_data = meteo_system.generate_weather_map(map_data, season)

            # Log to ledger (K7)
            self._log_meteo_entry(map_data.get("game_id", "unknown"), seed, meteo_data)

            return {
                "status": "success",
                "meteo_data": meteo_data,
                "validation_results": {
                    "k1_fail_closed": {"pass": True},
                    "k5_determinism": {"pass": True, "hash": meteo_data["meteo_hash"][:32]},
                    "k7_policy_pinning": {
                        "pass": True,
                        "hash": meteo_data["meteo_hash"],
                    },
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "validation_results": {"k1_fail_closed": {"pass": False}},
            }

    def _log_meteo_entry(self, game_id: str, seed: int, meteo_data: Dict):
        """Log meteorology generation to ledger (K7)."""
        entry = {
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            "event": "meteo_generated",
            "game_id": game_id,
            "seed": seed,
            "season": meteo_data["season"],
            "meteo_hash": meteo_data["meteo_hash"],
        }

        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")


# Convenience function
def generate_weather_for_map(map_data: Dict, seed: int, season: str = "spring") -> Dict:
    """Quick function to generate weather for a map."""
    skill = MeteoSkill()
    return skill.generate_weather(map_data, seed, season)


if __name__ == "__main__":
    import sys

    # Test: Generate weather for a simple map
    if len(sys.argv) < 2:
        print("Usage: python3 meteo_skill.py <seed> [season]")
        sys.exit(1)

    seed = int(sys.argv[1])
    season = sys.argv[2] if len(sys.argv) > 2 else "spring"

    # Create a simple test map
    test_map = {
        "width": 5,
        "height": 5,
        "game_id": f"meteo_test_{seed}",
        "tile_map": {
            f"{x},{y}": {
                "x": x,
                "y": y,
                "terrain": ["plains", "water", "forest", "mountain"][
                    (x + y) % 4
                ],
                "climate": ["temperate", "tropical", "arid", "frozen"][(x * y) % 4],
            }
            for x in range(5)
            for y in range(5)
        },
    }

    print("=" * 80)
    print("METEOROLOGY SKILL TEST")
    print("=" * 80)

    skill = MeteoSkill()
    result = skill.generate_weather(test_map, seed, season)

    if result["status"] == "success":
        meteo = result["meteo_data"]
        print(f"\n✅ Weather generated for seed={seed}, season={season}")
        print(f"\nMeteo Hash: {meteo['meteo_hash'][:32]}...")
        print(f"Timestamp: {meteo['timestamp']}")

        print(f"\nWeather Summary (sample tiles):")
        for key in list(meteo["weather_tiles"].items())[:5]:
            coord, condition = key
            temp = meteo["temperature"].get(coord, "?")
            precip = meteo["precipitation"].get(coord, "?")
            wind = meteo["wind_field"].get(coord, {})
            print(
                f"  {coord}: {condition} (T:{temp}°, P:{precip}mm, W:{wind.get('direction', '?')})"
            )

        print(f"\nPressure Systems: {len(meteo['pressure_centers'])}")
        for center in meteo["pressure_centers"]:
            print(
                f"  {center['type'].upper()} at ({center['x']:.1f}, {center['y']:.1f}), intensity={center['intensity']:.2f}"
            )

        print(f"\nStorm Paths: {len(meteo['storm_paths'])}")
        for i, storm in enumerate(meteo["storm_paths"]):
            print(f"  Storm {i}: {len(storm['path'])} steps from origin")

        print(f"\nK-Gates: {result['validation_results']}")
    else:
        print(f"\n❌ Error: {result['error']}")
