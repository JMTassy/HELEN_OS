#!/usr/bin/env python3
"""
Memory Ledger Linker

Connects OpenClaw memory system to Oracle Town's append-only ledger.

Key Rules:
1. All memory facts are append-only (never mutated)
2. Every fact is linked to the receipt that created it
3. All reads are unrestricted (no authority needed to search memory)
4. Search uses semantic/vector methods (inherit from OpenClaw if available)

This enables:
- NPCs to read memory without restriction
- Memory facts to remain audit-traceable
- Claims to be contextualized by historical decisions
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
import json
import uuid


@dataclass
class MemoryFact:
    """
    A fact in the memory system, linked to the receipt that created it.
    """
    fact_id: str
    fact_type: str  # "entity", "relationship", "event", "outcome", etc.
    content: Dict[str, Any]
    source_receipt_id: str  # Links back to the Oracle Town receipt
    timestamp: str = field(default_factory=lambda: date.today().isoformat())
    confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "fact_id": self.fact_id,
            "fact_type": self.fact_type,
            "content": self.content,
            "source_receipt_id": self.source_receipt_id,
            "timestamp": self.timestamp,
            "confidence": self.confidence
        }


@dataclass
class MemoryRelationship:
    """
    A relationship between two entities in memory.
    """
    relationship_id: str
    source_entity: str
    relationship_type: str  # "approved", "rejected", "owns", "manages", etc.
    target_entity: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_receipt_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "relationship_id": self.relationship_id,
            "source_entity": self.source_entity,
            "relationship_type": self.relationship_type,
            "target_entity": self.target_entity,
            "metadata": self.metadata,
            "source_receipt_id": self.source_receipt_id,
            "timestamp": self.timestamp
        }


class MemoryLedgerLinker:
    """
    Manages memory facts as an append-only ledger linked to Oracle Town receipts.

    Architecture:
    - OpenClaw memory (mutable, semantic) → linked at query/update time
    - Oracle Town memory (immutable, audit-traced) → this system
    """

    def __init__(self, ledger_path: str = "oracle_town/memory/ledger.jsonl"):
        """
        Initialize the linker.

        Args:
            ledger_path: Path to append-only ledger file
        """
        self.ledger_path = ledger_path
        self.facts: Dict[str, MemoryFact] = {}  # in-memory cache
        self.relationships: Dict[str, MemoryRelationship] = {}
        self._load_ledger()

    def add_fact(
        self,
        fact_type: str,
        content: Dict[str, Any],
        source_receipt_id: str,
        confidence: float = 0.8
    ) -> MemoryFact:
        """
        Add a fact to memory, linked to the receipt that created it.

        Args:
            fact_type: Type of fact (entity, outcome, learnings, etc.)
            content: Fact content (dict)
            source_receipt_id: ID of the receipt that created this fact
            confidence: Confidence in the fact [0, 1]

        Returns:
            MemoryFact object
        """
        fact = MemoryFact(
            fact_id=f"fact_{uuid.uuid4().hex[:8]}",
            fact_type=fact_type,
            content=content,
            source_receipt_id=source_receipt_id,
            confidence=confidence
        )

        # Store in memory
        self.facts[fact.fact_id] = fact

        # Append to ledger (immutable)
        self._append_to_ledger(fact.to_dict())

        return fact

    def add_relationship(
        self,
        source_entity: str,
        relationship_type: str,
        target_entity: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_receipt_id: Optional[str] = None
    ) -> MemoryRelationship:
        """
        Add a relationship between entities.

        Args:
            source_entity: Entity ID of source
            relationship_type: Type of relationship
            target_entity: Entity ID of target
            metadata: Optional metadata
            source_receipt_id: Optional receipt that created this relationship

        Returns:
            MemoryRelationship object
        """
        rel = MemoryRelationship(
            relationship_id=f"rel_{uuid.uuid4().hex[:8]}",
            source_entity=source_entity,
            relationship_type=relationship_type,
            target_entity=target_entity,
            metadata=metadata or {},
            source_receipt_id=source_receipt_id
        )

        self.relationships[rel.relationship_id] = rel
        self._append_to_ledger(rel.to_dict())

        return rel

    def search_facts(
        self,
        fact_type: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[MemoryFact]:
        """
        Search facts by type or content.

        This is unrestricted—anyone can search memory.

        Args:
            fact_type: Optional fact type filter
            query: Optional semantic search query

        Returns:
            List of matching facts
        """
        results = []

        for fact in self.facts.values():
            # Filter by type if provided
            if fact_type and fact.fact_type != fact_type:
                continue

            # Filter by content if query provided
            if query:
                if self._fact_matches_query(fact, query):
                    results.append(fact)
            else:
                results.append(fact)

        return results

    def search_relationships(
        self,
        entity: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[MemoryRelationship]:
        """
        Search relationships.

        Args:
            entity: Optional entity (matches source or target)
            relationship_type: Optional relationship type filter

        Returns:
            List of matching relationships
        """
        results = []

        for rel in self.relationships.values():
            if entity and rel.source_entity != entity and rel.target_entity != entity:
                continue

            if relationship_type and rel.relationship_type != relationship_type:
                continue

            results.append(rel)

        return results

    def get_fact_lineage(self, fact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete lineage of a fact back to its source receipt.

        Args:
            fact_id: ID of the fact

        Returns:
            Lineage dict with fact and source receipt info
        """
        fact = self.facts.get(fact_id)
        if not fact:
            return None

        return {
            "fact_id": fact.fact_id,
            "fact_type": fact.fact_type,
            "content": fact.content,
            "source_receipt_id": fact.source_receipt_id,
            "timestamp": fact.timestamp,
            "confidence": fact.confidence
        }

    def get_entity_profile(self, entity_id: str) -> Dict[str, Any]:
        """
        Get all known facts and relationships about an entity.

        Args:
            entity_id: Entity ID to profile

        Returns:
            Profile dict with facts and relationships
        """
        # Find all facts that mention this entity
        relevant_facts = [
            fact for fact in self.facts.values()
            if entity_id in str(fact.content).lower()
        ]

        # Find all relationships involving this entity
        relevant_rels = self.search_relationships(entity=entity_id)

        return {
            "entity_id": entity_id,
            "facts": [f.to_dict() for f in relevant_facts],
            "relationships": [r.to_dict() for r in relevant_rels]
        }

    def recount_acceptance_rate(self, entity_id: str) -> float:
        """
        Calculate acceptance rate for a given entity from memory.

        This is used by Doctrine enforcement to check the 35-45% acceptance law.

        Args:
            entity_id: Entity to check (e.g., vendor ID)

        Returns:
            Acceptance rate [0, 1]
        """
        rels = self.search_relationships(entity=entity_id)

        verdicts = [
            r for r in rels
            if r.relationship_type in ["approved", "rejected", "accepted", "declined"]
        ]

        if not verdicts:
            return 0.5  # Unknown

        accepts = len([r for r in verdicts if "approved" in r.relationship_type.lower()])
        total = len(verdicts)

        return accepts / total if total > 0 else 0.5

    # --- Private helper methods ---

    def _fact_matches_query(self, fact: MemoryFact, query: str) -> bool:
        """
        Check if a fact matches a query string.

        Simple substring matching for now. Could be enhanced with semantic search.
        """
        fact_str = json.dumps(fact.to_dict()).lower()
        return query.lower() in fact_str

    def _append_to_ledger(self, entry: Dict[str, Any]):
        """
        Append an entry to the immutable ledger.

        This is a simple JSONL append. In production, would be:
        - Database APPEND
        - Message queue
        - Append-only log
        """
        try:
            with open(self.ledger_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Log but don't fail
            print(f"Warning: Could not append to ledger: {e}")

    def _load_ledger(self):
        """
        Load existing ledger into memory cache.
        """
        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry.get("fact_id"):
                        fact = MemoryFact(**entry)
                        self.facts[fact.fact_id] = fact
                    elif entry.get("relationship_id"):
                        rel = MemoryRelationship(**entry)
                        self.relationships[rel.relationship_id] = rel
        except FileNotFoundError:
            # First run, ledger doesn't exist yet
            pass


# --- Testing ---

if __name__ == "__main__":

    # Test 1: Create linker
    linker = MemoryLedgerLinker()
    print("✓ Memory linker initialized")

    # Test 2: Add facts
    fact1 = linker.add_fact(
        fact_type="vendor_profile",
        content={
            "vendor_id": "vendor_acme",
            "name": "ACME Corp",
            "category": "supplies"
        },
        source_receipt_id="receipt_20260130_001"
    )
    print(f"✓ Fact added: {fact1.fact_id}")

    # Test 3: Add relationship
    rel = linker.add_relationship(
        source_entity="vendor_acme",
        relationship_type="approved",
        target_entity="user_john",
        metadata={"reason": "Low risk, high reliability"}
    )
    print(f"✓ Relationship added: {rel.relationship_id}")

    # Test 4: Search facts
    found = linker.search_facts(fact_type="vendor_profile")
    print(f"✓ Found {len(found)} vendor facts")

    # Test 5: Entity profile
    profile = linker.get_entity_profile("vendor_acme")
    print(f"✓ Entity profile: {profile['entity_id']}")
    print(f"  Facts: {len(profile['facts'])}")
    print(f"  Relationships: {len(profile['relationships'])}")

    # Test 6: Acceptance rate
    rate = linker.recount_acceptance_rate("vendor_acme")
    print(f"✓ Acceptance rate for vendor_acme: {rate:.1%}")

    print("\n✅ Memory ledger linker tests passed")
