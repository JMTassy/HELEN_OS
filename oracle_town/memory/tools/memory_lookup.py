#!/usr/bin/env python3
"""
Oracle Town Memory Lookup API
Allows Day 2+ governance decisions to reference learned heuristics.
Returns only advisory information; never overrides K-Invariants.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT_DIR = Path(__file__).parent.parent.parent  # oracle_town/
MEMORY_DIR = ROOT_DIR / "memory"
ENTITIES_DIR = MEMORY_DIR / "entities"
TACIT_DIR = MEMORY_DIR / "tacit"

def load_json(path: Path, default=None):
    """Load JSON file."""
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}

def read_markdown(path: Path) -> str:
    """Read markdown file."""
    if not path.exists():
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return ""

class MemoryLookup:
    """Interface for accessing Oracle Town memory during governance."""

    def __init__(self):
        self.entities_dir = ENTITIES_DIR
        self.tacit_dir = TACIT_DIR

    def get_heuristics(self) -> str:
        """
        Fetch governance heuristics.
        Returns: Raw markdown of learned best practices.
        """
        heuristics_path = self.tacit_dir / "heuristics.md"
        return read_markdown(heuristics_path)

    def get_rules_of_thumb(self) -> str:
        """
        Fetch rules of thumb.
        Returns: Raw markdown of practical wisdom.
        """
        rules_path = self.tacit_dir / "rules_of_thumb.md"
        return read_markdown(rules_path)

    def get_entity_summary(self, entity_type: str, entity_slug: str) -> str:
        """
        Fetch summary for a specific entity.
        Example: get_entity_summary("decisions", "claim_001")
        Returns: Markdown summary.
        """
        summary_path = self.entities_dir / entity_type / entity_slug / "summary.md"
        return read_markdown(summary_path)

    def get_entity_facts(
        self, entity_type: str, entity_slug: str, active_only: bool = True
    ) -> List[Dict]:
        """
        Fetch facts for a specific entity.
        Example: get_entity_facts("lane_performance", "fast_track_lane")
        Returns: List of fact objects.
        """
        items_path = self.entities_dir / entity_type / entity_slug / "items.json"
        items = load_json(items_path, [])

        if active_only:
            return [x for x in items if isinstance(x, dict) and x.get("status") == "active"]
        else:
            return items

    def get_all_active_facts(self, entity_type: str) -> Dict[str, List[Dict]]:
        """
        Fetch all active facts for an entity type.
        Example: get_all_active_facts("lane_performance")
        Returns: {entity_slug: [facts]}
        """
        result = {}
        entity_type_dir = self.entities_dir / entity_type
        if not entity_type_dir.exists():
            return result

        for entity_slug_dir in sorted(entity_type_dir.iterdir()):
            if not entity_slug_dir.is_dir():
                continue
            entity_slug = entity_slug_dir.name
            facts = self.get_entity_facts(entity_type, entity_slug, active_only=True)
            if facts:
                result[entity_slug] = facts

        return result

    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """
        Fetch recent decision history.
        Returns: List of decision facts, most recent first, up to limit.
        """
        all_decisions = self.get_all_active_facts("decisions")
        facts = []
        for slug, fact_list in all_decisions.items():
            facts.extend(fact_list)

        facts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return facts[:limit]

    def get_invariant_violations(self) -> List[Dict]:
        """
        Fetch all recorded invariant violations.
        Returns: List of invariant_events facts (all statuses).
        """
        all_invariants = self.get_all_active_facts("invariant_events")
        violations = []
        for slug, fact_list in all_invariants.items():
            violations.extend(fact_list)
        violations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return violations

    def get_lane_performance(self) -> Dict[str, List[Dict]]:
        """
        Fetch lane performance metrics.
        Returns: {lane_slug: [facts]}
        """
        return self.get_all_active_facts("lane_performance")

    def get_emergence_signals(self) -> List[Dict]:
        """
        Fetch detected emergence signals.
        Returns: List of emergence_signals facts.
        """
        all_signals = self.get_all_active_facts("emergence_signals")
        signals = []
        for slug, fact_list in all_signals.items():
            signals.extend(fact_list)
        signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return signals

    def get_advisory_context(self) -> Dict[str, Any]:
        """
        Fetch comprehensive advisory context for a mayor decision.
        This is what gets passed to Day 2+ decision-makers.

        Returns:
        {
            "heuristics": str,
            "rules_of_thumb": str,
            "recent_decisions": [facts],
            "invariant_violations": [facts],
            "lane_performance": {slug: [facts]},
            "emergence_signals": [facts],
            "timestamp": ISO timestamp,
            "advisory_note": str
        }
        """
        return {
            "heuristics": self.get_heuristics(),
            "rules_of_thumb": self.get_rules_of_thumb(),
            "recent_decisions": self.get_decision_history(limit=5),
            "invariant_violations": self.get_invariant_violations()[:5],
            "lane_performance": self.get_lane_performance(),
            "emergence_signals": self.get_emergence_signals()[:5],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "advisory_note": (
                "This context is purely informational. "
                "Memory cannot override K-Invariants. "
                "All decisions are logged for next synthesis cycle."
            )
        }

def demo():
    """Demo: print advisory context."""
    lookup = MemoryLookup()
    context = lookup.get_advisory_context()

    print("=" * 60)
    print("ORACLE TOWN MEMORY - ADVISORY CONTEXT")
    print("=" * 60)
    print(f"\nGenerated: {context['timestamp']}")
    print(f"\nAdvisory Note: {context['advisory_note']}\n")

    print("=" * 60)
    print("HEURISTICS")
    print("=" * 60)
    print(context["heuristics"][:500] + "...")

    print("\n" + "=" * 60)
    print("RECENT DECISIONS")
    print("=" * 60)
    for fact in context["recent_decisions"]:
        print(f"  - {fact.get('fact', 'unknown')}")

    print("\n" + "=" * 60)
    print("INVARIANT VIOLATIONS")
    print("=" * 60)
    for fact in context["invariant_violations"]:
        print(f"  - {fact.get('fact', 'unknown')}")

    print("\n" + "=" * 60)
    print("LANE PERFORMANCE")
    print("=" * 60)
    for lane, facts in context["lane_performance"].items():
        print(f"  {lane}: {len(facts)} signals")

    print("\n" + "=" * 60)
    print("EMERGENCE SIGNALS")
    print("=" * 60)
    for fact in context["emergence_signals"]:
        print(f"  - {fact.get('fact', 'unknown')}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        print("Usage: memory_lookup.py --demo")
        print("Or import as library: from memory_lookup import MemoryLookup")
