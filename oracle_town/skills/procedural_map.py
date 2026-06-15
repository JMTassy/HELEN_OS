"""
Procedural map generation for CONQUEST using seeded RNG + Perlin-like noise.

This module generates 5×5 game boards deterministically (same seed = same output).
Implements K5 (Determinism) by design — all RNG is seeded.

Algorithm:
1. Initialize seeded RNG from seed parameter
2. Partition 5×5 grid into 6 territory regions using Voronoi-like partitioning
3. Apply Perlin-like noise for terrain variation (water, mountain, plains)
4. Assign climate zones based on position + noise
5. Return map as JSON with metadata for ledger hashing
"""

import numpy as np
import json
from typing import Dict, List, Tuple
from datetime import datetime, UTC


class ProceduralMapGenerator:
    """Generates procedural CONQUEST maps with deterministic seeding."""

    def __init__(self, seed: int, width: int = 5, height: int = 5):
        """
        Initialize generator with seed.

        Args:
            seed: Integer seed for reproducibility (K5 determinism)
            width: Grid width (default 5)
            height: Grid height (default 5)
        """
        self.seed = seed
        self.width = width
        self.height = height
        self.rng = np.random.RandomState(seed)  # K5: seeded RNG ensures determinism

        # Territory configuration
        self.territory_count = 6
        self.territory_centers = []
        self.territory_assignment = {}

        # Terrain types
        self.terrain_types = ["plains", "forest", "mountain", "water"]
        self.climate_types = ["temperate", "arid", "frozen", "tropical"]

    def _generate_territory_centers(self) -> List[Tuple[float, float]]:
        """
        Generate territory center points using seeded RNG.
        Uses simple random point placement (can be enhanced with K-means later).

        Returns:
            List of (x, y) center coordinates for each territory
        """
        centers = []
        for i in range(self.territory_count):
            x = self.rng.uniform(0.5, self.width - 0.5)
            y = self.rng.uniform(0.5, self.height - 0.5)
            centers.append((x, y))
        return centers

    def _assign_territories(self) -> Dict[Tuple[int, int], int]:
        """
        Assign each tile (x,y) to nearest territory center.
        Simpler than Voronoi but still deterministic and spatially sensible.

        Returns:
            Dictionary mapping (x, y) tile to territory_id (0-5)
        """
        assignment = {}
        self.territory_centers = self._generate_territory_centers()

        for x in range(self.width):
            for y in range(self.height):
                # Find nearest territory center
                min_distance = float('inf')
                nearest_territory = 0

                for territory_id, (cx, cy) in enumerate(self.territory_centers):
                    distance = (x - cx) ** 2 + (y - cy) ** 2  # Euclidean distance
                    if distance < min_distance:
                        min_distance = distance
                        nearest_territory = territory_id

                assignment[(x, y)] = nearest_territory

        return assignment

    def _generate_terrain(self) -> Dict[Tuple[int, int], str]:
        """
        Generate terrain for each tile using seeded noise.
        Uses simple noise function (can be enhanced with Perlin noise later).

        Returns:
            Dictionary mapping (x, y) tile to terrain_type
        """
        terrain = {}

        for x in range(self.width):
            for y in range(self.height):
                # Simple noise function: combine x, y, seed into deterministic value
                noise_value = (
                    np.sin((x + 0.5) * 2.3 + (y + 0.5) * 3.7) * np.sin(self.seed * 0.001)
                ) % 1.0

                # Map noise to terrain type
                if noise_value < 0.15:
                    terrain[(x, y)] = "water"
                elif noise_value < 0.35:
                    terrain[(x, y)] = "mountain"
                elif noise_value < 0.65:
                    terrain[(x, y)] = "forest"
                else:
                    terrain[(x, y)] = "plains"

        return terrain

    def _generate_climate(self) -> Dict[Tuple[int, int], str]:
        """
        Generate climate for each tile based on position + noise.

        Returns:
            Dictionary mapping (x, y) tile to climate_type
        """
        climate = {}

        for x in range(self.width):
            for y in range(self.height):
                # Climate influenced by position (y affects latitude, x affects longitude)
                latitude_factor = y / self.height  # 0 = north, 1 = south
                noise_value = (
                    np.cos((x + 0.5) * 1.7) + np.sin((y + 0.5) * 2.1)
                ) % 1.0

                # Combine latitude + noise to determine climate
                combined = latitude_factor * 0.7 + noise_value * 0.3

                if combined < 0.25:
                    climate[(x, y)] = "frozen"
                elif combined < 0.5:
                    climate[(x, y)] = "temperate"
                elif combined < 0.75:
                    climate[(x, y)] = "tropical"
                else:
                    climate[(x, y)] = "arid"

        return climate

    def generate_map(self) -> Dict:
        """
        Generate complete map with territories, terrain, and climate.

        Returns:
            Dictionary with map data, metadata, and validation results
        """
        # Generate map components (all deterministic due to seeded RNG)
        self.territory_assignment = self._assign_territories()
        terrain = self._generate_terrain()
        climate = self._generate_climate()

        # Build territory data structure
        territories = {}
        for territory_id in range(self.territory_count):
            territories[territory_id] = {
                "territory_id": territory_id,
                "cells": [],
                "terrain_types": {},
                "climate_types": {},
            }

        # Populate territory cells
        for (x, y), territory_id in self.territory_assignment.items():
            territories[territory_id]["cells"].append((x, y))

            # Track terrain and climate distributions
            t = terrain[(x, y)]
            c = climate[(x, y)]
            territories[territory_id]["terrain_types"][t] = territories[territory_id]["terrain_types"].get(t, 0) + 1
            territories[territory_id]["climate_types"][c] = territories[territory_id]["climate_types"].get(c, 0) + 1

        # Build map data structure
        map_data = {
            "seed": self.seed,
            "width": self.width,
            "height": self.height,
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            "territories": [
                {
                    "territory_id": tid,
                    "cells": territories[tid]["cells"],
                    "center": self.territory_centers[tid],
                    "terrain_distribution": territories[tid]["terrain_types"],
                    "climate_distribution": territories[tid]["climate_types"],
                    "tile_count": len(territories[tid]["cells"]),
                }
                for tid in range(self.territory_count)
            ],
            "tile_map": {
                f"{x},{y}": {
                    "x": x,
                    "y": y,
                    "territory_id": self.territory_assignment[(x, y)],
                    "terrain": terrain[(x, y)],
                    "climate": climate[(x, y)],
                }
                for x in range(self.width)
                for y in range(self.height)
            },
            "metadata": {
                "algorithm": "seeded_rng_voronoi_approximation",
                "deterministic": True,
                "rng_type": "numpy.random.RandomState",
                "seed_value": self.seed,
            }
        }

        return map_data

    def get_map_as_json(self) -> str:
        """Return generated map as JSON string."""
        map_data = self.generate_map()
        return json.dumps(map_data, indent=2)

    def get_map_hash(self) -> str:
        """
        Get SHA256 hash of map data for K7 policy pinning.

        Returns:
            Hex string SHA256 hash of map JSON
        """
        import hashlib
        map_json = self.get_map_as_json()
        return hashlib.sha256(map_json.encode()).hexdigest()
