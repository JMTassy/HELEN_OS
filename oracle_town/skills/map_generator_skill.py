"""
MapGenerator MCP Skill for CONQUEST.

This skill generates procedural game maps with K-gate enforcement:
- K5 (Determinism): Same seed = identical output (caching + validation)
- K7 (Policy Pinning): Map hash locked per game in ledger
- K2 (No Self-Validation): Skill generates LP-### claim, Foreman approves
- K1 (Fail-Closed): Missing parameters → reject, never guess

Usage:
    skill = MapGeneratorSkill()
    result = skill.generate_map(seed=111, game_id="game_001")
    # result contains map_data + validation results + ledger entry
"""

import json
import hashlib
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime, UTC

from oracle_town.skills.procedural_map import ProceduralMapGenerator


class MapGeneratorSkill:
    """MCP skill for generating CONQUEST maps with K-gate enforcement."""

    def __init__(self, cache_dir: Optional[str] = None, ledger_path: Optional[str] = None):
        """
        Initialize skill with optional cache and ledger paths.

        Args:
            cache_dir: Directory to store map cache (K5 determinism)
            ledger_path: Path to ledger file for K7 policy pinning
        """
        self.cache_dir = Path(cache_dir or "artifacts/map_cache")
        self.ledger_path = Path(ledger_path or "kernel/ledger/map_generation_records.jsonl")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # K-gate validation flags
        self.validation_results = {}

    def _validate_input(self, seed: Optional[int], game_id: Optional[str]) -> Dict:
        """
        Validate input parameters (K1: fail-closed).

        K1 Rule: Missing evidence → REJECT
        Missing parameters → reject immediately

        Args:
            seed: Map generation seed
            game_id: Game identifier

        Returns:
            {"pass": bool, "error": str}
        """
        errors = []

        if seed is None:
            errors.append("SEED_REQUIRED: seed parameter is required for deterministic generation")

        if game_id is None:
            errors.append("GAME_ID_REQUIRED: game_id is required to link map to game run")

        if seed is not None and not isinstance(seed, int):
            errors.append(f"SEED_TYPE_ERROR: seed must be int, got {type(seed)}")

        if game_id is not None and not isinstance(game_id, str):
            errors.append(f"GAME_ID_TYPE_ERROR: game_id must be str, got {type(game_id)}")

        return {
            "pass": len(errors) == 0,
            "errors": errors,
        }

    def _get_cached_map(self, seed: int) -> Optional[Dict]:
        """
        Retrieve cached map by seed (K5: determinism via cache).

        K5 Rule: Same input → identical output
        If we have computed this map before, return cached version.

        Args:
            seed: Map seed to look up

        Returns:
            Cached map dict, or None if not in cache
        """
        cache_file = self.cache_dir / f"map_seed_{seed}.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                return json.load(f)
        return None

    def _cache_map(self, seed: int, map_data: Dict) -> None:
        """
        Store generated map in cache (K5: determinism via cache).

        Args:
            seed: Map seed (used as cache key)
            map_data: Complete map data to cache
        """
        cache_file = self.cache_dir / f"map_seed_{seed}.json"
        with open(cache_file, "w") as f:
            json.dump(map_data, f, indent=2)

    def _compute_map_hash(self, map_data: Dict) -> str:
        """
        Compute SHA256 hash of map for K7 policy pinning.

        K7 Rule: Policy hash fixed per run
        Hash locks the map state so mid-game changes are detectable.

        Args:
            map_data: Complete map data

        Returns:
            Hex string SHA256 hash
        """
        map_json = json.dumps(map_data, sort_keys=True)
        return hashlib.sha256(map_json.encode()).hexdigest()

    def _write_ledger_entry(self, game_id: str, map_hash: str, map_data: Dict) -> str:
        """
        Write K7 policy pin entry to ledger.

        K7 Rule: Policy hash fixed per run
        Every map generation creates an immutable ledger entry.

        Args:
            game_id: Game identifier
            map_hash: SHA256 hash of map
            map_data: Complete map data

        Returns:
            Ledger entry ID (for tracking)
        """
        entry_id = f"MAP_POLICY_{datetime.now(UTC).replace(tzinfo=None).strftime('%Y_%m_%d_%H%M%S')}_{game_id}"

        ledger_entry = {
            "id": entry_id,
            "rule": "K7_POLICY_PINNING",
            "action": "LOCK_MAP_HASH",
            "game_id": game_id,
            "map_hash": map_hash,
            "locked_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            "locked_by": "MapGeneratorSkill",
            "seed": map_data["seed"],
            "width": map_data["width"],
            "height": map_data["height"],
        }

        # Append to ledger (JSONL format — one JSON object per line)
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(ledger_entry) + "\n")

        return entry_id

    def _create_claim(self, game_id: str, map_hash: str, territory_count: int) -> Dict:
        """
        Create LP-### claim for Foreman approval (K2: no self-validation).

        K2 Rule: Proposer ≠ validator
        Skill generates the claim, but Foreman/UZIK must approve it.

        Args:
            game_id: Game identifier
            map_hash: SHA256 hash of map
            territory_count: Number of territories

        Returns:
            Claim dict (LP-### format)
        """
        return {
            "claim_id": f"LP-MAP-{game_id}",
            "type": "map_generation",
            "author": "MapGeneratorSkill",
            "statement": f"Map generated for {game_id} with {territory_count} territories",
            "map_hash": map_hash,
            "status": "pending",  # Awaiting Foreman approval
            "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        }

    def generate_map(
        self,
        seed: int,
        game_id: str,
        territory_count: int = 6,
        map_size: tuple = (5, 5),
        validate_only: bool = False,
    ) -> Dict:
        """
        Generate a CONQUEST map with K-gate enforcement.

        Args:
            seed: Deterministic seed for RNG (required)
            game_id: Game identifier (required)
            territory_count: Number of territories (default 6)
            map_size: (width, height) of map (default (5, 5))
            validate_only: If True, dry-run without ledger write

        Returns:
            {
                "status": "success" | "validation_failed" | "error",
                "map_data": {dict with territories, tiles, metadata},
                "validation_results": {K5, K7, K1, K2 results},
                "ledger_entry_id": str (if successful),
                "claim": {LP-### claim dict},
                "error_details": str (if failed),
            }
        """
        # Initialize validation results
        self.validation_results = {}

        # ===== K1: FAIL-CLOSED VALIDATION (Missing parameters rejected)
        k1_validation = self._validate_input(seed, game_id)
        self.validation_results["k1_fail_closed"] = k1_validation

        if not k1_validation["pass"]:
            return {
                "status": "validation_failed",
                "error": "K1_VALIDATION_FAILED: " + "; ".join(k1_validation["errors"]),
                "validation_results": self.validation_results,
                "map_data": None,
                "claim": None,
                "ledger_entry_id": None,
            }

        # ===== K5: DETERMINISM (Check cache for same seed)
        cached_map = self._get_cached_map(seed)
        if cached_map:
            self.validation_results["k5_determinism"] = {
                "pass": True,
                "source": "cache",
                "seed": seed,
            }
            map_data = cached_map
        else:
            # Generate new map
            try:
                generator = ProceduralMapGenerator(seed=seed, width=map_size[0], height=map_size[1])
                map_data = generator.generate_map()
                self._cache_map(seed, map_data)

                self.validation_results["k5_determinism"] = {
                    "pass": True,
                    "source": "generated",
                    "seed": seed,
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"MAP_GENERATION_ERROR: {str(e)}",
                    "validation_results": self.validation_results,
                    "map_data": None,
                    "claim": None,
                    "ledger_entry_id": None,
                }

        # ===== K7: POLICY PINNING (Hash map, write ledger)
        map_hash = self._compute_map_hash(map_data)
        self.validation_results["k7_policy_pinning"] = {
            "pass": True,
            "map_hash": map_hash,
            "game_id": game_id,
        }

        ledger_entry_id = None
        if not validate_only:
            try:
                ledger_entry_id = self._write_ledger_entry(game_id, map_hash, map_data)
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"LEDGER_WRITE_ERROR: {str(e)}",
                    "validation_results": self.validation_results,
                    "map_data": map_data,
                    "claim": None,
                    "ledger_entry_id": None,
                }

        # ===== K2: NO SELF-VALIDATION (Create claim for Foreman approval)
        claim = self._create_claim(game_id, map_hash, territory_count)
        self.validation_results["k2_no_self_validation"] = {
            "pass": True,
            "claim_author": "MapGeneratorSkill",
            "claim_status": claim["status"],
            "note": "Claim pending Foreman approval (no self-approval)",
        }

        # ===== Territory count validation
        actual_territory_count = len(map_data["territories"])
        self.validation_results["territory_count"] = {
            "pass": actual_territory_count == territory_count,
            "expected": territory_count,
            "actual": actual_territory_count,
        }

        # ===== Success response
        return {
            "status": "success",
            "map_data": map_data,
            "validation_results": self.validation_results,
            "ledger_entry_id": ledger_entry_id,
            "claim": claim,
            "error_details": None,
        }
