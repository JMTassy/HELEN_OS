#!/usr/bin/env python3
"""
Cognitive Kernel (Phase 1A L1 — Deterministic Spine).

CPU: Orchestration engine
Instruction set: JSON contracts
Memory: Namespace-isolated state
Ledger: Hash-chained execution log
Model: Deterministic Mistral 7B (T=0)

SEED CONTRACT (S0 - strict):
seed = H(json.dumps({"query": query, "role": role, "namespace": namespace}, 
                    sort_keys=True, separators=(',', ':')))

Same query → same seed, deterministically.
"""

import json
import hashlib
from typing import Dict, Any, Optional
from ledger import Ledger
from memory import Memory
from roles import ROLE_SCHEMAS, get_schema
from schema import validate_structure, validate_namespace_consistency, ValidationError
from model import MistralModel, ModelError


class KernelError(Exception):
    """Kernel execution failed."""
    pass


class CognitiveKernel:
    """
    Deterministic multi-domain orchestration engine.
    
    Namespaces:
    - math: Theorem proving, proof validation
    - world: Conquest simulation, political agents
    - project: Le Tar planning, foundry coordination
    
    No cross-namespace mutation.
    All state changes logged to immutable ledger.
    
    SEED CONTRACT (S0):
    Seed is deterministically derived from request payload.
    seed = H(canonical_request_json)
    Same query always gets same seed (fresh process, no ledger coupling).
    """
    
    def __init__(self, model: Optional[MistralModel] = None):
        self.model = model or MistralModel()
        self.ledger = Ledger()
        self.memory = Memory()
    
    @staticmethod
    def _derive_seed(query: str, role: str, namespace: str) -> int:
        """
        S0 Seed Contract: Deterministic from request payload.
        
        seed = int(H(canonical_json)) mod 2^31
        
        Same query/role/namespace → same seed, always.
        """
        payload = {
            "query": query,
            "role": role,
            "namespace": namespace
        }
        
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        hash_hex = hashlib.sha256(canonical.encode()).hexdigest()
        
        # Convert to int, mod 2^31 (positive int range)
        seed = int(hash_hex, 16) % (2**31)
        return seed
    
    def execute(
        self,
        query: str,
        role: str,
        namespace: str,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main execution pipeline (deterministic).
        
        Pipeline:
        1. Derive seed (S0 contract)
        2. Inject memory (namespace-scoped)
        3. Build prompt
        4. Generate (T=0, seed-locked)
        5. Parse JSON
        6. Validate structure
        7. Validate namespace semantics
        8. Append ledger
        9. Update memory
        10. Return entry
        
        Args:
            query: Input question/directive
            role: Agent role (must be in ROLE_SCHEMAS)
            namespace: Memory domain (math|world|project)
            seed: Override seed (for testing; default: derive from payload)
        
        Returns:
            Ledger entry (dict with hash, timestamp, seed, etc.)
        
        Raises:
            KernelError on any validation failure
        """
        
        try:
            # 1. Derive seed (S0 contract: deterministic from request)
            if seed is None:
                seed = self._derive_seed(query, role, namespace)
            
            # 2. Inject memory (namespace-scoped)
            context = {
                "query": query,
                "role": role,
                "namespace": namespace,
                "memory": self.memory.read(namespace)
            }
            
            # 3. Build prompt
            prompt = self._build_prompt(role, context)
            
            # 4. Generate (deterministic)
            try:
                raw_output = self.model.generate(
                    prompt=prompt,
                    max_tokens=1024,
                    seed=seed
                )
            except ModelError as e:
                raise KernelError(f"Model generation failed: {e}")
            
            # 5. Parse JSON
            try:
                structured_output = json.loads(raw_output)
            except json.JSONDecodeError:
                raise KernelError(f"Model output not valid JSON: {raw_output[:100]}")
            
            # 6. Validate structure (role contract)
            try:
                validate_structure(structured_output, role)
            except ValidationError as e:
                raise KernelError(f"Structure validation failed: {e}")
            
            # 7. Validate semantics (namespace constraints)
            try:
                validate_namespace_consistency(structured_output, namespace)
            except ValidationError as e:
                raise KernelError(f"Semantic validation failed: {e}")
            
            # 8. Append ledger (immutable)
            entry = self.ledger.append({
                "namespace": namespace,
                "role": role,
                "query": query,
                "output": structured_output,
                "seed": seed,
                "seed_contract": "S0"
            })
            
            # 9. Update memory (no cross-mutation)
            if "memory_update" in structured_output:
                self.memory.update(namespace, structured_output["memory_update"])
            
            # 10. Return entry
            return entry
        
        except KernelError:
            raise
        except Exception as e:
            raise KernelError(f"Unexpected error: {e}")
    
    def _build_prompt(self, role: str, context: Dict[str, Any]) -> str:
        """
        Build role-aware prompt.
        
        Format: JSON with context + explicit instruction.
        """
        
        instruction = self._get_role_instruction(role)
        
        _ns = context.get("namespace")
        role_header = f"[KERNEL ROLE HEADER]\nROLE_ID={role} ROLE_NS={_ns} ROLE_VER=v1\n"

        prompt = f"""{role_header}{instruction}

Context:
{json.dumps(context, indent=2)}

Respond with valid JSON only."""
        
        return prompt
    
    def _get_role_instruction(self, role: str) -> str:
        """Get instruction for role."""
        
        instructions = {
            # Math
            "theorem_writer": "You are a theorem writer. Output a complete theorem with proof sketch. Include 'type', 'statement', 'proof_sketch' in JSON.",
            "proof_checker": "You are a proof auditor. Validate the theorem. Output JSON with 'type', 'verdict' (true/false), 'issues' (list).",
            "lemma_auditor": "You are a lemma auditor. Assess logical consistency. Output JSON with 'type', 'assessment', 'gaps' (list).",
            
            # World
            "political_agent": "You are a political agent in Conquest. Propose an action. Output JSON with 'type', 'action', 'rationale', 'expected_outcome'.",
            "stability_monitor": "You are a stability monitor. Assess castle state. Output JSON with 'type', 'status', 'threats' (list).",
            "ledger_enforcer": "You are a ledger enforcer. Validate state transitions. Output JSON with 'type', 'validation', 'state_update'.",
            
            # Project
            "planner": "You are a Le Tar planner. Develop strategy. Output JSON with 'type', 'strategy', 'timeline', 'resources'.",
            "coordinator": "You are a coordinator. Propose next action. Output JSON with 'type', 'action', 'parties', 'next_steps'.",
            "validator": "You are a validator. Assess proposal. Output JSON with 'type', 'assessment', 'issues' (list).",
        }
        
        return instructions.get(role, "Output valid JSON.")
    
    def export_ledger(self, path: str = "ledger.jsonl") -> None:
        """Export ledger to file."""
        self.ledger.export(path)
    
    def get_ledger(self):
        """Get all ledger entries."""
        return self.ledger.get_all()
    
    def get_memory(self):
        """Get all memory state."""
        return self.memory.export()
    
    def verify_integrity(self) -> bool:
        """Verify ledger chain integrity."""
        return self.ledger.verify_chain()
    
    def __repr__(self) -> str:
        return f"CognitiveKernel(ledger_entries={len(self.ledger)}, chain_valid={self.verify_integrity()})"


if __name__ == "__main__":
    # Test seed derivation
    kernel = CognitiveKernel()
    
    query = "Test query"
    role = "theorem_writer"
    namespace = "math"
    
    seed1 = kernel._derive_seed(query, role, namespace)
    seed2 = kernel._derive_seed(query, role, namespace)
    
    print(f"✅ Seed S0 contract test:")
    print(f"   Query: {query}")
    print(f"   Seed 1: {seed1}")
    print(f"   Seed 2: {seed2}")
    print(f"   Match: {seed1 == seed2}")
