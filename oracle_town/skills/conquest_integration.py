"""
CONQUEST Integration with Procedurally Generated Maps

Bridges MapGeneratorSkill output to HexaCycleGame initialization.
Implements K5 (determinism) and K7 (policy pinning) for game reproducibility.

Workflow:
1. MapGeneratorSkill generates deterministic map (seeded)
2. render_conquest_map() converts map data to CONQUEST tile assignments
3. K7 hash pins the exact game state for this run
4. Game initialization uses the generated map
5. All decisions logged to ledger (append-only JSONL)
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime, UTC
from oracle_town.skills.map_generator_skill import MapGeneratorSkill
from oracle_town.skills.meteo_skill import MeteoSkill, generate_weather_for_map


class ConquestMapIntegration:
    """Integrates MapGeneratorSkill with CONQUEST game initialization."""

    def __init__(self, cache_dir: str = None, ledger_path: str = None):
        """
        Initialize integration.

        Args:
            cache_dir: Directory for K5 caching
            ledger_path: Path to K7 ledger file
        """
        self.skill = MapGeneratorSkill(cache_dir=cache_dir, ledger_path=ledger_path)
        self.cache_dir = cache_dir or "map_cache"
        self.ledger_path = ledger_path or "kernel/ledger/conquest_integration.jsonl"

    def generate_conquest_board(
        self,
        seed: int,
        game_id: str,
        render_svg: bool = True,
        svg_dir: str = "artifacts/map_renders",
        season: str = "spring",
        include_meteo: bool = True,
    ) -> Dict:
        """
        Generate a complete CONQUEST board from procedural map with weather.

        Args:
            seed: Random seed for deterministic map
            game_id: Unique identifier for this game run
            render_svg: Whether to render SVG visualization
            svg_dir: Directory for SVG output
            season: Season for weather generation (spring/summer/autumn/winter)
            include_meteo: Whether to generate weather systems

        Returns:
            Dict containing:
                - status: "success" or error
                - map_data: Raw map data from skill
                - board_data: CONQUEST-specific board initialization
                - meteo_data: Weather system (if include_meteo=True)
                - svg_path: Path to rendered map (if render_svg=True)
                - k_gates: K-gate validation results
                - ledger_entry_id: K7 ledger entry identifier
        """
        # Step 1: Generate map (K5 determinism, K7 pinning)
        skill_result = self.skill.generate_map(seed=seed, game_id=game_id)

        if skill_result["status"] != "success":
            return {
                "status": "error",
                "error": skill_result.get("error", "Map generation failed"),
                "error_details": skill_result.get("error_details"),
            }

        map_data = skill_result["map_data"]

        # Step 2: Convert map data to CONQUEST board
        board_data = self._map_data_to_conquest_board(map_data)

        result = {
            "status": "success",
            "map_data": map_data,
            "board_data": board_data,
            "k_gates": skill_result.get("validation_results", {}),
            "ledger_entry_id": skill_result.get("ledger_entry_id"),
            "claim": skill_result.get("claim"),
        }

        # Step 2.5: Generate weather systems (optional)
        if include_meteo:
            meteo_skill = MeteoSkill()
            meteo_result = meteo_skill.generate_weather(map_data, seed, season)
            if meteo_result["status"] == "success":
                result["meteo_data"] = meteo_result["meteo_data"]
                result["season"] = season

        # Step 3: Render SVG (optional)
        if render_svg:
            try:
                from oracle_town.skills.map_renderer_fmg import render_conquest_map

                svg_path = render_conquest_map(map_data, svg_dir)
                result["svg_path"] = svg_path
            except Exception as e:
                result["svg_error"] = str(e)

        # Step 4: Log integration event (K7)
        self._log_integration_event(game_id, seed, result)

        return result

    def _map_data_to_conquest_board(self, map_data: Dict) -> Dict:
        """
        Convert map data to CONQUEST board structure.

        Mapping strategy:
        - Each territory becomes a "region" assigned to an agent
        - Territory center becomes agent starting position
        - Territory terrain influences agent stats (modifiers)
        - Territory climate influences epoch bonuses

        Args:
            map_data: Output from MapGeneratorSkill.generate_map()

        Returns:
            Dict containing:
                - agent_assignments: List of (agent_id, starting_tiles, modifiers)
                - terrain_map: Tile-level terrain properties
                - climate_map: Tile-level climate properties
                - board_hash: SHA256 of complete board state
        """
        territories = map_data["territories"]
        tile_map = map_data["tile_map"]
        seed = map_data["seed"]

        # Validate territory count (must be ≥5 for CONQUEST agents)
        if len(territories) < 5:
            raise ValueError(
                f"Map must have ≥5 territories for CONQUEST (got {len(territories)})"
            )

        agent_assignments = []

        # Assign first 5 territories to 5 CONQUEST agents
        for agent_id, territory in enumerate(territories[:5]):
            starting_tiles = territory["cells"]
            terrain_dist = territory["terrain_distribution"]
            climate_dist = territory["climate_distribution"]

            # Compute stat modifiers based on terrain
            terrain_modifiers = self._terrain_to_modifiers(terrain_dist)
            climate_modifiers = self._climate_to_modifiers(climate_dist)

            assignment = {
                "agent_id": agent_id,
                "starting_tiles": starting_tiles,
                "center": territory["center"],
                "terrain_distribution": terrain_dist,
                "climate_distribution": climate_dist,
                "terrain_modifiers": terrain_modifiers,
                "climate_modifiers": climate_modifiers,
            }
            agent_assignments.append(assignment)

        # Build terrain and climate maps for quick lookup
        terrain_map = {}
        climate_map = {}
        for coord_str, tile_info in tile_map.items():
            terrain_map[coord_str] = tile_info["terrain"]
            climate_map[coord_str] = tile_info["climate"]

        board_data = {
            "seed": seed,
            "agent_assignments": agent_assignments,
            "terrain_map": terrain_map,
            "climate_map": climate_map,
            "board_hash": self._compute_board_hash(agent_assignments),
        }

        return board_data

    def _terrain_to_modifiers(self, terrain_dist: Dict) -> Dict:
        """
        Convert terrain distribution to CONQUEST stat modifiers.

        Terrain bonuses:
        - Water: stability +1 (naval defense)
        - Plains: power +1 (open expansion)
        - Forest: stability +1 (defensive cover)
        - Mountain: power +0, stability +1 (fortified position)
        """
        modifiers = {"power": 0, "stability": 0}

        if terrain_dist.get("water", 0) >= 1:
            modifiers["stability"] += 1

        if terrain_dist.get("plains", 0) >= 2:
            modifiers["power"] += 1

        if terrain_dist.get("forest", 0) >= 1:
            modifiers["stability"] += 1

        if terrain_dist.get("mountain", 0) >= 1:
            modifiers["stability"] += 1

        return modifiers

    def _climate_to_modifiers(self, climate_dist: Dict) -> Dict:
        """
        Convert climate distribution to CONQUEST epoch bonuses.

        Climate influences epoch alignment:
        - Temperate: balanced (no modifier)
        - Tropical: +1 power (vigorous growth)
        - Arid: +1 stability (conservation)
        - Frozen: +1 stability (endurance)
        """
        modifiers = {"power": 0, "stability": 0}

        if climate_dist.get("tropical", 0) >= 1:
            modifiers["power"] += 1

        if climate_dist.get("arid", 0) >= 1:
            modifiers["stability"] += 1

        if climate_dist.get("frozen", 0) >= 1:
            modifiers["stability"] += 1

        return modifiers

    def _compute_board_hash(self, agent_assignments: List[Dict]) -> str:
        """Compute deterministic hash of board state for K7 policy pinning."""
        import hashlib

        board_str = json.dumps(agent_assignments, sort_keys=True)
        return hashlib.sha256(board_str.encode()).hexdigest()

    def _log_integration_event(self, game_id: str, seed: int, result: Dict):
        """Log integration event to ledger for K7 audit trail."""
        Path(self.ledger_path).parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            "event": "conquest_board_generated",
            "game_id": game_id,
            "seed": seed,
            "status": result["status"],
            "board_hash": result.get("board_data", {}).get("board_hash", "N/A"),
            "map_hash": result.get("map_data", {}).get("map_hash", "N/A"),
            "svg_path": result.get("svg_path", "N/A"),
        }

        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def initialize_conquest_with_map(seed: int, game_id: str) -> Dict:
    """
    Quick initialization of CONQUEST with procedural map.

    One-liner to generate board and get agent assignments.

    Args:
        seed: Random seed for deterministic map
        game_id: Unique game identifier

    Returns:
        Dict with board_data and agent_assignments
    """
    integration = ConquestMapIntegration()
    result = integration.generate_conquest_board(seed, game_id, render_svg=True)

    if result["status"] == "success":
        return {
            "status": "success",
            "board_data": result["board_data"],
            "agent_assignments": result["board_data"]["agent_assignments"],
            "svg_path": result.get("svg_path"),
        }
    else:
        return {
            "status": "error",
            "error": result.get("error"),
            "error_details": result.get("error_details"),
        }


def get_agent_starting_position(
    agent_assignments: List[Dict], agent_id: int
) -> Tuple[int, int]:
    """
    Get starting position (x, y) for an agent from board data.

    Args:
        agent_assignments: List from board_data["agent_assignments"]
        agent_id: Agent ID (0-4)

    Returns:
        (x, y) tuple of agent's first tile
    """
    if agent_id >= len(agent_assignments):
        raise ValueError(f"Agent {agent_id} not found in assignments")

    assignment = agent_assignments[agent_id]
    starting_tiles = assignment["starting_tiles"]

    if not starting_tiles:
        raise ValueError(f"Agent {agent_id} has no starting tiles")

    return tuple(starting_tiles[0])


def apply_board_stats_to_agents(agents: List, board_data: Dict):
    """
    Apply procedurally-generated stat modifiers to agents.

    Modifies agents in place by adding terrain/climate bonuses.

    Args:
        agents: List of Agent objects from HexaCycleGame
        board_data: board_data from ConquestMapIntegration.generate_conquest_board()
    """
    for assignment in board_data["agent_assignments"]:
        agent_id = assignment["agent_id"]
        if agent_id < len(agents):
            agent = agents[agent_id]
            terrain_mods = assignment.get("terrain_modifiers", {})
            climate_mods = assignment.get("climate_modifiers", {})

            # Apply terrain modifiers
            agent.power += terrain_mods.get("power", 0)
            agent.stability += terrain_mods.get("stability", 0)

            # Log modifications (for audit trail)
            # print(f"{agent.name} terrain mods: +{terrain_mods.get('power',0)}P +{terrain_mods.get('stability',0)}S")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys

    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 111
    game_id = sys.argv[2] if len(sys.argv) > 2 else f"conquest_test_{seed}"

    print("=" * 80)
    print("CONQUEST INTEGRATION TEST")
    print("=" * 80)

    integration = ConquestMapIntegration()
    result = integration.generate_conquest_board(seed, game_id, render_svg=True)

    if result["status"] == "success":
        print("\n✅ Board generated successfully")
        print(f"\nSeed: {seed}")
        print(f"Game ID: {game_id}")

        board_data = result["board_data"]
        print(f"\nBoard Hash: {board_data['board_hash'][:32]}...")
        print(f"\nAgent Assignments:")

        for assignment in board_data["agent_assignments"]:
            agent_id = assignment["agent_id"]
            center = assignment["center"]
            terrain = assignment["terrain_distribution"]
            climate = assignment["climate_distribution"]
            terrain_mods = assignment["terrain_modifiers"]

            print(f"\nAgent {agent_id}:")
            print(f"  Starting position: {center}")
            print(f"  Starting tiles: {len(assignment['starting_tiles'])} tiles")
            print(f"  Terrain: {terrain}")
            print(f"  Climate: {climate}")
            print(f"  Modifiers: +{terrain_mods.get('power', 0)}P +{terrain_mods.get('stability', 0)}S")

        if "svg_path" in result:
            print(f"\n📊 SVG rendered: {result['svg_path']}")

        print(f"\n🔐 K-Gates:")
        for gate, status in result.get("k_gates", {}).items():
            if isinstance(status, dict):
                pass_status = "✅" if status.get("pass") else "❌"
                print(f"  {pass_status} {gate}")

    else:
        print(f"\n❌ Error: {result.get('error')}")
        print(f"Details: {result.get('error_details')}")
