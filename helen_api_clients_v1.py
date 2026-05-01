"""
HELEN OS API Clients v1.0

Unified interface for all supported LLM providers:
- Ollama (local)
- Claude (Anthropic)
- GPT (OpenAI)
- Grok (xAI)
- Gemini (Google)
- Qwen (Alibaba)

Each client implements:
- Async/sync query methods
- Streaming support
- Error handling & retries
- Token counting
- Cost calculation
"""

import os
import asyncio
import aiohttp
import httpx
from typing import Optional, List, Iterator, AsyncIterator, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import time
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# BASE CLIENT INTERFACE
# ============================================================================

class BaseAPIClient(ABC):
    """Base class for all LLM API clients"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0

    @abstractmethod
    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query model asynchronously"""
        pass

    @abstractmethod
    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query model synchronously"""
        pass

    @abstractmethod
    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream response asynchronously"""
        pass

    @abstractmethod
    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream response synchronously"""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "requests": self.request_count,
            "total_tokens": self.total_tokens,
            "total_cost": f"${self.total_cost:.4f}",
        }


# ============================================================================
# OLLAMA CLIENT (Local)
# ============================================================================

_HELEN_SYSTEM_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "prompts",
    "HELEN_SYSTEM_PROMPT_V1.md",
)
_helen_system_prompt_cache: Optional[str] = None


def load_helen_system_prompt() -> Optional[str]:
    """Load HELEN OS system prompt from disk (cached). Returns None if absent."""
    global _helen_system_prompt_cache
    if _helen_system_prompt_cache is not None:
        return _helen_system_prompt_cache
    try:
        with open(_HELEN_SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            _helen_system_prompt_cache = f.read().strip()
            logger.info(f"HELEN system prompt loaded ({len(_helen_system_prompt_cache)} chars)")
            return _helen_system_prompt_cache
    except FileNotFoundError:
        logger.warning(f"HELEN system prompt not found at {_HELEN_SYSTEM_PROMPT_PATH}; running without system context")
        return None


class OllamaClient(BaseAPIClient):
    """Local Ollama API client"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__()
        self.base_url = base_url
        self.model = model
        self.endpoint = f"{base_url}/api/generate"
        self.system_prompt = load_helen_system_prompt()

    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Ollama model asynchronously"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            if self.system_prompt:
                payload["system"] = self.system_prompt

            try:
                async with session.post(self.endpoint, json=payload) as resp:
                    if resp.status != 200:
                        raise Exception(f"Ollama error: {resp.status}")
                    data = await resp.json()
                    self.request_count += 1
                    return data.get("response", "")
            except Exception as e:
                logger.error(f"Ollama query failed: {e}")
                raise

    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Ollama model synchronously"""
        return asyncio.run(self.query_async(prompt, max_tokens, temperature, stream))

    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream Ollama response asynchronously"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            if self.system_prompt:
                payload["system"] = self.system_prompt

            try:
                async with session.post(self.endpoint, json=payload) as resp:
                    if resp.status != 200:
                        raise Exception(f"Ollama error: {resp.status}")

                    async for line in resp.content:
                        if line:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                    self.request_count += 1
            except Exception as e:
                logger.error(f"Ollama stream failed: {e}")
                raise

    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream Ollama response synchronously"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if self.system_prompt:
            payload["system"] = self.system_prompt
        with httpx.stream("POST", self.endpoint, json=payload) as resp:
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
            self.request_count += 1


# ============================================================================
# CLAUDE CLIENT (Anthropic)
# ============================================================================

class ClaudeClient(BaseAPIClient):
    """Anthropic Claude API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-6"):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Claude asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            try:
                async with session.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"Claude error: {error}")

                    data = await resp.json()
                    self.request_count += 1
                    self.total_tokens += data.get("usage", {}).get("output_tokens", 0)
                    content = data.get("content", [{}])[0].get("text", "")
                    return content
            except Exception as e:
                logger.error(f"Claude query failed: {e}")
                raise

    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Claude synchronously"""
        return asyncio.run(self.query_async(prompt, max_tokens, temperature, stream))

    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream Claude response asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            }

            try:
                async with session.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"Claude error: {resp.status}")

                    async for line in resp.content:
                        if line and line.startswith(b"data: "):
                            try:
                                data = json.loads(line[6:])
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        yield delta.get("text", "")
                            except json.JSONDecodeError:
                                continue
                    self.request_count += 1
            except Exception as e:
                logger.error(f"Claude stream failed: {e}")
                raise

    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream Claude response synchronously"""
        with httpx.stream(
            "POST",
            f"{self.base_url}/messages",
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            },
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        ) as resp:
            for line in resp.iter_lines():
                if line and line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield delta.get("text", "")
                    except json.JSONDecodeError:
                        continue
            self.request_count += 1


# ============================================================================
# GPT CLIENT (OpenAI)
# ============================================================================

class GPTClient(BaseAPIClient):
    """OpenAI GPT API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query GPT asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"GPT error: {error}")

                    data = await resp.json()
                    self.request_count += 1
                    self.total_tokens += data.get("usage", {}).get("completion_tokens", 0)
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content
            except Exception as e:
                logger.error(f"GPT query failed: {e}")
                raise

    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query GPT synchronously"""
        return asyncio.run(self.query_async(prompt, max_tokens, temperature, stream))

    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream GPT response asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            }

            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"GPT error: {resp.status}")

                    async for line in resp.content:
                        if line and line.startswith(b"data: "):
                            try:
                                data = json.loads(line[6:])
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                chunk = delta.get("content", "")
                                if chunk:
                                    yield chunk
                            except (json.JSONDecodeError, IndexError):
                                continue
                    self.request_count += 1
            except Exception as e:
                logger.error(f"GPT stream failed: {e}")
                raise

    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream GPT response synchronously"""
        with httpx.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            },
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        ) as resp:
            for line in resp.iter_lines():
                if line and line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        chunk = delta.get("content", "")
                        if chunk:
                            yield chunk
                    except (json.JSONDecodeError, IndexError):
                        continue
            self.request_count += 1


# ============================================================================
# GROK CLIENT (xAI)
# ============================================================================

class GrokClient(BaseAPIClient):
    """xAI Grok API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "grok-1"):
        super().__init__(api_key or os.getenv("XAI_API_KEY"))
        self.model = model
        self.base_url = "https://api.x.ai/v1"

    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Grok asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"Grok error: {error}")

                    data = await resp.json()
                    self.request_count += 1
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content
            except Exception as e:
                logger.error(f"Grok query failed: {e}")
                raise

    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Grok synchronously"""
        return asyncio.run(self.query_async(prompt, max_tokens, temperature, stream))

    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream Grok response asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            }

            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"Grok error: {resp.status}")

                    async for line in resp.content:
                        if line and line.startswith(b"data: "):
                            try:
                                data = json.loads(line[6:])
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                chunk = delta.get("content", "")
                                if chunk:
                                    yield chunk
                            except (json.JSONDecodeError, IndexError):
                                continue
                    self.request_count += 1
            except Exception as e:
                logger.error(f"Grok stream failed: {e}")
                raise

    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream Grok response synchronously"""
        raise NotImplementedError("Grok streaming not yet implemented in sync mode")


# ============================================================================
# GEMINI CLIENT (Google)
# ============================================================================

class GeminiClient(BaseAPIClient):
    """Google Gemini API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro-vision"):
        super().__init__(api_key or os.getenv("GOOGLE_API_KEY"))
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Gemini asynchronously"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                },
            }

            try:
                url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"Gemini error: {error}")

                    data = await resp.json()
                    self.request_count += 1
                    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return content
            except Exception as e:
                logger.error(f"Gemini query failed: {e}")
                raise

    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Gemini synchronously"""
        return asyncio.run(self.query_async(prompt, max_tokens, temperature, stream))

    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream Gemini response asynchronously"""
        raise NotImplementedError("Gemini streaming not yet implemented")

    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream Gemini response synchronously"""
        raise NotImplementedError("Gemini streaming not yet implemented")


# ============================================================================
# QWEN CLIENT (Alibaba)
# ============================================================================

class QwenClient(BaseAPIClient):
    """Alibaba Qwen API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-max"):
        super().__init__(api_key or os.getenv("QWEN_API_KEY"))
        self.model = model
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    async def query_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Qwen asynchronously"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            }

            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"Qwen error: {error}")

                    data = await resp.json()
                    self.request_count += 1
                    content = data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content
            except Exception as e:
                logger.error(f"Qwen query failed: {e}")
                raise

    def query(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """Query Qwen synchronously"""
        return asyncio.run(self.query_async(prompt, max_tokens, temperature, stream))

    async def stream_async(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream Qwen response asynchronously"""
        raise NotImplementedError("Qwen streaming not yet implemented")

    def stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """Stream Qwen response synchronously"""
        raise NotImplementedError("Qwen streaming not yet implemented")


# ============================================================================
# CLIENT FACTORY
# ============================================================================

def create_client(provider: str, api_key: Optional[str] = None) -> BaseAPIClient:
    """Factory function to create API clients"""
    provider_lower = provider.lower()

    clients = {
        "ollama": OllamaClient,
        "claude": ClaudeClient,
        "gpt": GPTClient,
        "grok": GrokClient,
        "gemini": GeminiClient,
        "qwen": QwenClient,
    }

    ClientClass = clients.get(provider_lower)
    if not ClientClass:
        raise ValueError(f"Unknown provider: {provider}")

    return ClientClass(api_key)


if __name__ == "__main__":
    print("✅ API Clients module loaded")
    print("\nSupported providers:")
    print("  • Ollama (local)")
    print("  • Claude (Anthropic)")
    print("  • GPT (OpenAI)")
    print("  • Grok (xAI)")
    print("  • Gemini (Google)")
    print("  • Qwen (Alibaba)")
