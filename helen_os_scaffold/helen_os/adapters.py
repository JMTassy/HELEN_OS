import os
import requests
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        pass

class OllamaAdapter(LLMAdapter):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        try:
            messages = []
            for h in history:
                role = h.get("metadata", {}).get("role")
                if role == "helen":
                    role = "assistant"
                elif role not in ["user", "system"]:
                    role = "user"
                messages.append({"role": role, "content": h.get("content", "")})
            
            messages.append({"role": "user", "content": prompt})

            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "No response from Ollama.")
        except Exception as e:
            return f"[Ollama Error] {str(e)}"

class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"), base_url=base_url)
        self.model = model

    def generate(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        try:
            messages = []
            for h in history:
                role = h.get("metadata", {}).get("role")
                if role == "helen":
                    role = "assistant"
                elif role not in ["user", "system"]:
                    role = "user"
                messages.append({"role": role, "content": h.get("content", "")})
            
            messages.append({"role": "user", "content": prompt})
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Error] {str(e)}"

class StubAdapter(LLMAdapter):
    """
    Deterministic stub — no LLM required.
    Used for offline mode, testing, and seed world simulation.
    Responses are deterministic given call count + prompt hash.
    """
    def __init__(self, model: str = "stub-v1"):
        self.model = model
        self._call_count = 0

    def generate(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        import hashlib
        self._call_count += 1
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        return (
            f"[STUB:{self.model}|call={self._call_count}|ph={prompt_hash}] "
            f"Receipt-bound deterministic response. "
            f"No LLM active — running in stub mode. Prompt: {prompt[:80]}"
        )
class HybridSerpentAdapter(LLMAdapter):
    """
    Wraps an existing LLM adapter and injects Hybrid Attention metaphors.
    Simulates the Gated Delta Rule (Solve et Coagula) for recurrent state.
    """
    def __init__(self, inner_adapter: LLMAdapter, state_decay: float = 0.05):
        self.inner_adapter = inner_adapter
        self.state_decay = state_decay
        self.recurrent_state_summary = "INITIAL_UNITY"

    def generate(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        # Inject Hybrid Metadata into the prompt
        hybrid_prompt = (
            f"[HYBRID_STATE: {self.recurrent_state_summary}]\n"
            f"[DECAY_RATE: {self.state_decay}]\n"
            f"Solve the following with Recurrent Gated logic: {prompt}"
        )
        
        response = self.inner_adapter.generate(hybrid_prompt, history)
        
        # Simulate state update (recurrent transition)
        # In a real implementation, this would update a torch tensor.
        # Here we update a narrative summary of the state.
        self.recurrent_state_summary = f"STATE_{hash(response) % 10000:04d}"
        
        return response


def get_adapter(config: Dict[str, Any]) -> LLMAdapter:
    adapter_type = config.get("adapter", {}).get("type", "ollama")
    if adapter_type == "ollama":
        opts = config.get("adapter", {}).get("ollama", {})
        return OllamaAdapter(
            base_url=opts.get("base_url", "http://localhost:11434"),
            model=opts.get("model", "mistral")
        )
    elif adapter_type == "openai":
        opts = config.get("adapter", {}).get("openai", {})
        return OpenAIAdapter(
            api_key=opts.get("api_key"),
            base_url=opts.get("base_url", "https://api.openai.com/v1"),
            model=opts.get("model", "gpt-4")
        )
    elif adapter_type == "lmstudio":
        opts = config.get("adapter", {}).get("lmstudio", {})
        return OpenAIAdapter(
            api_key="none",
            base_url=opts.get("base_url", "http://localhost:1234/v1"),
            model=opts.get("model", "qwen3.5-9b")
        )
    elif adapter_type == "stub":
        return StubAdapter()
    elif adapter_type == "hybrid":
        opts = config.get("adapter", {}).get("hybrid", {})
        inner_config = {"adapter": opts.get("inner", {"type": "ollama"})}
        inner = get_adapter(inner_config)
        return HybridSerpentAdapter(inner, state_decay=opts.get("state_decay", 0.05))
    else:
        # Safe fallback — never crash the OS on unknown adapter type
        import warnings
        warnings.warn(
            f"Unknown adapter type '{adapter_type}'. Falling back to StubAdapter.",
            stacklevel=2
        )
        return StubAdapter()
