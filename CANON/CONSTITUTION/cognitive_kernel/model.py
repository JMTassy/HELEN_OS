#!/usr/bin/env python3
"""
Deterministic Mistral 7B Wrapper (Ollama).

Properties:
- Temperature = 0 (greedy decoding)
- Seed-locked for reproducibility
- JSON-only output expected
"""

import json
import requests
from typing import Optional


class ModelError(Exception):
    """Model generation failed."""
    pass


class MistralModel:
    """
    Wraps local Mistral 7B via Ollama.
    
    Ensures deterministic generation (T=0, no sampling).
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral:7b",
        timeout: int = 120
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
    
    def health_check(self) -> bool:
        """Verify Mistral is accessible."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            return any(self.model in name for name in model_names)
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        seed: int = 42
    ) -> str:
        """
        Generate text via Mistral (deterministic).
        
        Args:
            prompt: Input text (expect JSON in prompt)
            max_tokens: Max output length
            seed: Random seed (tracked but may not be used by Ollama)
        
        Returns:
            Generated text (should be JSON)
        
        Raises:
            ModelError on failure
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": 0.0,      # Greedy decoding
            "top_p": 1.0,            # No nucleus sampling
            "top_k": 1,              # Only top token
            "num_predict": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.ConnectionError:
            raise ModelError(
                f"Cannot connect to Mistral at {self.base_url}. "
                f"Is Ollama running? (ollama serve)"
            )
        except requests.exceptions.Timeout:
            raise ModelError(
                f"Mistral request timed out after {self.timeout}s"
            )
        except Exception as e:
            raise ModelError(f"Mistral generation failed: {e}")
    
    def get_available_models(self) -> list:
        """List available models in Ollama."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception:
            return []


if __name__ == "__main__":
    model = MistralModel()
    
    if model.health_check():
        print(f"✅ {model.model} is available")
        
        # Test deterministic generation
        prompt = json.dumps({
            "query": "What is 2+2?",
            "namespace": "math"
        })
        
        output = model.generate(prompt, max_tokens=50)
        print(f"\nGenerated: {output[:100]}")
    else:
        print(f"❌ {model.model} not found")
        print(f"Available models: {model.get_available_models()}")


class MockModel:
    """Deterministic offline model for tests + sign-off.

    Uses ROLE header when present (H2).
    """

    def health_check(self) -> bool:
        return True

    def get_available_models(self) -> list:
        return ["mock"]

    @staticmethod
    def _parse_role_header(prompt: str) -> tuple[str | None, str | None]:
        role_id = None
        role_ns = None
        for line in prompt.splitlines()[:5]:
            if line.startswith("ROLE_ID="):
                # Supports both 'ROLE_ID=x ROLE_NS=y' and newline-separated forms
                parts = line.strip().split()
                for p in parts:
                    if p.startswith("ROLE_ID="):
                        role_id = p.split("=", 1)[1]
                    if p.startswith("ROLE_NS="):
                        role_ns = p.split("=", 1)[1]
                continue
            if "ROLE_ID=" in line and "ROLE_NS=" in line:
                parts = line.strip().split()
                for p in parts:
                    if p.startswith("ROLE_ID="):
                        role_id = p.split("=", 1)[1]
                    if p.startswith("ROLE_NS="):
                        role_ns = p.split("=", 1)[1]
        # Alternate header line: ROLE_ID=... ROLE_NS=... ROLE_VER=v1
        for line in prompt.splitlines()[:8]:
            if "ROLE_ID=" in line and "ROLE_NS=" in line:
                parts = line.strip().split()
                for p in parts:
                    if p.startswith("ROLE_ID="):
                        role_id = p.split("=", 1)[1]
                    if p.startswith("ROLE_NS="):
                        role_ns = p.split("=", 1)[1]
                break
        return role_id, role_ns

    def generate(self, prompt: str, max_tokens: int = 1024, seed: int = 42) -> str:
        import json

        role_id, role_ns = self._parse_role_header(prompt)
        role_id = role_id or "unknown"
        role_ns = role_ns or "unknown"

        # Deterministic error trigger (Phase 3 E0/E1 gate): missing required fields
        if "FORCE_SCHEMA_ERROR" in prompt:
            return json.dumps({"type": role_id}, sort_keys=True, separators=(",", ":"))

        out = {"type": role_id}

        if role_id == "theorem_writer":
            out.update({
                "statement": f"THEOREM({seed})",
                "proof_sketch": f"SKETCH({seed})",
            })
        elif role_id == "proof_checker":
            out.update({
                "verdict": True,
                "issues": [],
            })
        elif role_id == "lemma_auditor":
            out.update({
                "assessment": "CONSISTENT",
                "gaps": [],
            })
        elif role_id == "political_agent":
            out.update({
                "action": "FORTIFY",
                "rationale": f"STABILIZE({seed})",
                "expected_outcome": "STABILITY_UP",
            })
        elif role_id == "stability_monitor":
            out.update({
                "status": "STABLE",
                "threats": [],
            })
        elif role_id == "ledger_enforcer":
            out.update({
                "validation": "OK",
                "state_update": {"food": 100, "morale": 0.7},
            })
        elif role_id == "planner":
            out.update({
                "strategy": f"PLAN({seed})",
                "timeline": "T+30D",
                "resources": "TEAM",
            })
        elif role_id == "coordinator":
            out.update({
                "action": "SYNC",
                "parties": ["A", "B"],
                "next_steps": ["STEP_1"],
            })
        elif role_id == "validator":
            out.update({
                "assessment": "PASS",
                "issues": [],
            })

        # Deterministic memory update (namespace-scoped)
        out["memory_update"] = {f"last_{role_id}": seed, "ns": role_ns}

        return json.dumps(out, sort_keys=True, separators=(",", ":"))
