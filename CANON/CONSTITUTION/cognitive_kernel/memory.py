#!/usr/bin/env python3
"""
Namespace-Isolated Memory.

Hard rule: No cross-namespace mutation.

Namespaces:
- math: Proofs, theorems, ALEPH-Φ, Σ-SEED
- world: Conquest states, castle dynamics
- project: Le Tar foundry planning
"""

from typing import Dict, Any, Optional


class Memory:
    """Namespace-isolated state."""
    
    VALID_NAMESPACES = {"math", "world", "project"}
    
    def __init__(self):
        self.namespaces: Dict[str, Dict[str, Any]] = {
            "math": {},
            "world": {},
            "project": {}
        }
    
    def read(self, namespace: str) -> Dict[str, Any]:
        """Read namespace state."""
        if namespace not in self.VALID_NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}")
        return self.namespaces[namespace].copy()
    
    def update(self, namespace: str, patch: Dict[str, Any]) -> None:
        """
        Update namespace state (no cross-mutation).
        
        Raises ValueError if namespace is invalid.
        """
        if namespace not in self.VALID_NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}")
        
        self.namespaces[namespace].update(patch)
    
    def set(self, namespace: str, key: str, value: Any) -> None:
        """Set single value in namespace."""
        if namespace not in self.VALID_NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}")
        
        self.namespaces[namespace][key] = value
    
    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get single value from namespace."""
        if namespace not in self.VALID_NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}")
        
        return self.namespaces[namespace].get(key, default)
    
    def clear(self, namespace: str) -> None:
        """Clear namespace state."""
        if namespace not in self.VALID_NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}")
        
        self.namespaces[namespace] = {}
    
    def export(self) -> Dict[str, Dict[str, Any]]:
        """Export all namespaces."""
        return {ns: self.namespaces[ns].copy() for ns in self.VALID_NAMESPACES}
    
    def __repr__(self) -> str:
        sizes = {ns: len(self.namespaces[ns]) for ns in self.VALID_NAMESPACES}
        return f"Memory({sizes})"


if __name__ == "__main__":
    # Test
    mem = Memory()
    
    # Update math namespace
    mem.update("math", {
        "last_theorem": "x > 0 → x² > 0",
        "proof_count": 5
    })
    
    # Update world namespace
    mem.update("world", {
        "castle_food": 100,
        "castle_morale": 0.5
    })
    
    # Update project namespace
    mem.update("project", {
        "le_tar_budget": 50000,
        "timeline": "18 months"
    })
    
    print(f"✅ {mem}")
    print(f"   Math: {mem.read('math')}")
    print(f"   World: {mem.read('world')}")
    print(f"   Project: {mem.read('project')}")
    
    # Try invalid namespace
    try:
        mem.update("invalid", {"x": 1})
    except ValueError as e:
        print(f"✅ Caught invalid namespace: {e}")
