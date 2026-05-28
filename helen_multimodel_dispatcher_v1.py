"""
HELEN OS Multi-Model Dispatcher v1.0

Intelligent routing system that can dispatch tasks to:
- Ollama (local, private)
- Claude (Anthropic API)
- GPT (OpenAI API)
- Grok (xAI API)
- Gemini (Google API)
- Qwen (Alibaba API)

Task-aware routing selects the best model based on:
- Task type (reasoning, coding, math, analysis, creative, vision)
- Required capability
- Latency/cost tradeoff
- Model availability
"""

import asyncio
import json
from typing import Dict, List, Optional, Literal, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class ModelProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    CLAUDE = "claude"
    GPT = "gpt"
    GROK = "grok"
    GEMINI = "gemini"
    QWEN = "qwen"


class TaskType(Enum):
    """Classification of tasks for intelligent routing"""
    REASONING = "reasoning"           # Complex logic, multi-step
    CODING = "coding"                 # Code generation, debugging
    MATH = "math"                     # Mathematical reasoning
    ANALYSIS = "analysis"             # Data analysis, synthesis
    CREATIVE = "creative"             # Creative writing, brainstorming
    VISION = "vision"                 # Image understanding
    CONVERSATION = "conversation"     # General chat
    RESEARCH = "research"             # Deep research, synthesis
    FACTUAL = "factual"               # Factual retrieval


class CapabilityTier(Enum):
    """Model capability rating"""
    BASIC = "basic"                   # Simple tasks only
    STANDARD = "standard"             # General purpose
    ADVANCED = "advanced"             # Complex reasoning
    EXPERT = "expert"                 # State-of-the-art


@dataclass
class ModelConfig:
    """Configuration for a single model"""
    provider: ModelProvider
    model_id: str
    name: str
    capability_tier: CapabilityTier
    api_endpoint: Optional[str] = None
    max_tokens: int = 2048
    supports_vision: bool = False
    supports_streaming: bool = True
    is_local: bool = False
    cost_per_1k_tokens: float = 0.0  # 0.0 for local
    latency_ms: float = 100.0
    available: bool = True
    priority: int = 5  # 1-10, higher = more preferred
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskContext:
    """Context for task execution"""
    task_type: TaskType
    query: str
    require_vision: bool = False
    require_streaming: bool = True
    max_latency_ms: Optional[float] = None
    max_cost: Optional[float] = None
    preferred_providers: List[ModelProvider] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingDecision:
    """Decision output from router"""
    model_config: ModelConfig
    reason: str
    confidence: float  # 0.0-1.0
    alternatives: List[ModelConfig] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ModelResponse:
    """Response from LLM"""
    provider: ModelProvider
    model_id: str
    content: str
    tokens_used: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# INTELLIGENT MODEL ROUTER
# ============================================================================

class IntelligentModelRouter:
    """
    Task-aware router that selects optimal model based on:
    - Task type
    - Required capabilities
    - Performance constraints
    - Cost constraints
    - Provider availability
    """

    def __init__(self, models: List[ModelConfig]):
        self.models = {m.model_id: m for m in models}
        self.task_to_preferred_models = self._build_task_preference_map()
        logger.info(f"Router initialized with {len(self.models)} models")

    def _build_task_preference_map(self) -> Dict[TaskType, List[ModelProvider]]:
        """Build preferred model routing map by task type"""
        return {
            TaskType.REASONING: [
                ModelProvider.CLAUDE,      # Best reasoning
                ModelProvider.GPT,         # Strong reasoning
                ModelProvider.GROK,        # Good reasoning
            ],
            TaskType.CODING: [
                ModelProvider.CLAUDE,      # Excellent code
                ModelProvider.GPT,         # Strong code
                ModelProvider.GROK,        # Good code
            ],
            TaskType.MATH: [
                ModelProvider.GPT,         # Strong math
                ModelProvider.CLAUDE,      # Good math
                ModelProvider.GROK,        # Capable math
            ],
            TaskType.ANALYSIS: [
                ModelProvider.CLAUDE,      # Excellent analysis
                ModelProvider.GPT,         # Strong analysis
                ModelProvider.GROK,        # Good analysis
            ],
            TaskType.CREATIVE: [
                ModelProvider.CLAUDE,      # Excellent creative
                ModelProvider.GROK,        # Strong creative
                ModelProvider.QWEN,        # Capable creative
            ],
            TaskType.VISION: [
                ModelProvider.GEMINI,      # Multimodal
                ModelProvider.GPT,         # Vision capable
                ModelProvider.CLAUDE,      # Vision capable
            ],
            TaskType.CONVERSATION: [
                ModelProvider.OLLAMA,      # Fast, local
                ModelProvider.CLAUDE,      # Excellent
                ModelProvider.GPT,         # Excellent
            ],
            TaskType.RESEARCH: [
                ModelProvider.CLAUDE,      # Excellent research
                ModelProvider.GPT,         # Strong research
                ModelProvider.GROK,        # Good research
            ],
            TaskType.FACTUAL: [
                ModelProvider.CLAUDE,      # Accurate
                ModelProvider.GPT,         # Accurate
                ModelProvider.GEMINI,      # Accurate
            ],
        }

    def select_model(self, task: TaskContext) -> RoutingDecision:
        """
        Select optimal model for task using multi-factor decision logic.

        Factors:
        1. Task type preference
        2. Required capabilities (vision, streaming)
        3. Performance constraints (latency, cost)
        4. Provider availability
        5. Model priority
        """
        candidates = self._get_candidate_models(task)

        if not candidates:
            raise ValueError(f"No suitable models found for task: {task.task_type}")

        # Score each candidate
        scored = [(model, self._score_model(model, task)) for model in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        best_model, best_score = scored[0]
        alternatives = [m for m, _ in scored[1:4]]  # Top 3 alternatives

        confidence = min(best_score / 100.0, 1.0)

        return RoutingDecision(
            model_config=best_model,
            reason=self._explain_choice(best_model, task),
            confidence=confidence,
            alternatives=alternatives,
        )

    def _get_candidate_models(self, task: TaskContext) -> List[ModelConfig]:
        """Get models that can handle the task"""
        candidates = []

        # If user preferred providers specified, start there
        if task.preferred_providers:
            for provider in task.preferred_providers:
                for model in self.models.values():
                    if model.provider == provider and model.available:
                        if self._can_handle_task(model, task):
                            candidates.append(model)

        # Add models by task type preference
        preferred_providers = self.task_to_preferred_models.get(task.task_type, [])
        for provider in preferred_providers:
            for model in self.models.values():
                if model.provider == provider and model.available:
                    if model not in candidates and self._can_handle_task(model, task):
                        candidates.append(model)

        # Add fallback models
        for model in self.models.values():
            if model.available and model not in candidates:
                if self._can_handle_task(model, task):
                    candidates.append(model)

        return candidates

    def _can_handle_task(self, model: ModelConfig, task: TaskContext) -> bool:
        """Check if model can handle task requirements"""
        # Vision requirement
        if task.require_vision and not model.supports_vision:
            return False

        # Streaming requirement
        if task.require_streaming and not model.supports_streaming:
            return False

        # Latency constraint
        if task.max_latency_ms and model.latency_ms > task.max_latency_ms:
            return False

        # Cost constraint
        if task.max_cost is not None and model.cost_per_1k_tokens > task.max_cost:
            return False

        return True

    def _score_model(self, model: ModelConfig, task: TaskContext) -> float:
        """
        Score model for task (0-100).

        Factors:
        - Task type alignment (40 points)
        - Capability tier (30 points)
        - Priority (20 points)
        - Latency bonus (-10 if slow)
        - Cost bonus (-10 if expensive)
        """
        score = 0.0

        # Task type alignment (40 points)
        preferred = self.task_to_preferred_models.get(task.task_type, [])
        if model.provider in preferred:
            score += 40 * (1 - (preferred.index(model.provider) / len(preferred)))
        else:
            score += 10  # Not preferred, but can handle

        # Capability tier (30 points)
        tier_scores = {
            CapabilityTier.BASIC: 10,
            CapabilityTier.STANDARD: 20,
            CapabilityTier.ADVANCED: 27,
            CapabilityTier.EXPERT: 30,
        }
        score += tier_scores.get(model.capability_tier, 0)

        # Priority (20 points)
        score += (model.priority / 10) * 20

        # Latency bonus/penalty
        if model.latency_ms < 100:
            score += 5  # Fast
        elif model.latency_ms > 1000:
            score -= 10  # Slow

        # Cost bonus/penalty
        if model.cost_per_1k_tokens == 0:
            score += 5  # Free (local)
        elif model.cost_per_1k_tokens < 0.01:
            score += 3  # Cheap
        elif model.cost_per_1k_tokens > 0.1:
            score -= 5  # Expensive

        return max(0, score)

    def _explain_choice(self, model: ModelConfig, task: TaskContext) -> str:
        """Generate explanation for model selection"""
        reasons = []

        preferred = self.task_to_preferred_models.get(task.task_type, [])
        if model.provider in preferred:
            idx = preferred.index(model.provider)
            rankings = ["top choice", "strong choice", "capable choice"]
            reasons.append(f"{rankings[min(idx, 2)]} for {task.task_type.value}")

        if model.is_local:
            reasons.append("local execution (privacy, speed)")

        if model.capability_tier == CapabilityTier.EXPERT:
            reasons.append("state-of-the-art capability")

        if model.latency_ms < 100:
            reasons.append(f"low latency ({model.latency_ms}ms)")

        return " + ".join(reasons) if reasons else "suitable for task"

    def list_models(self) -> Dict[str, Any]:
        """Return available models"""
        return {
            model_id: {
                "provider": model.provider.value,
                "name": model.name,
                "capability": model.capability_tier.value,
                "available": model.available,
                "vision": model.supports_vision,
                "streaming": model.supports_streaming,
                "local": model.is_local,
                "cost": f"${model.cost_per_1k_tokens}/1k tokens",
                "latency": f"{model.latency_ms}ms",
            }
            for model_id, model in self.models.items()
        }


# ============================================================================
# DEFAULT MODEL CONFIGURATIONS
# ============================================================================

def create_default_models() -> List[ModelConfig]:
    """Create default model configurations"""
    return [
        # OLLAMA (Local, Private)
        # HER-FAST tier — qwen3.5:9b with think:false (per GEMMA_HER_AMPLIFIER_V1)
        # Confirmed on MRED 2026-05-02: ~0.5s response, fits 12GB VRAM
        ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_id="her_fast",
            name="HER-FAST (qwen3.5:9b, no-think)",
            capability_tier=CapabilityTier.ADVANCED,
            api_endpoint="http://localhost:11434",
            supports_vision=False,
            supports_streaming=True,
            is_local=True,
            cost_per_1k_tokens=0.0,
            latency_ms=500,
            priority=9,
            metadata={"ollama_model": "qwen3.5:9b", "think": False},
        ),
        ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_id="ollama_llama2",
            name="Llama 2 (Local via Ollama)",
            capability_tier=CapabilityTier.STANDARD,
            api_endpoint="http://localhost:11434",
            supports_vision=False,
            supports_streaming=True,
            is_local=True,
            cost_per_1k_tokens=0.0,
            latency_ms=50,
            priority=8,
        ),
        ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_id="ollama_mistral",
            name="Mistral (Local via Ollama)",
            capability_tier=CapabilityTier.STANDARD,
            api_endpoint="http://localhost:11434",
            supports_vision=False,
            supports_streaming=True,
            is_local=True,
            cost_per_1k_tokens=0.0,
            latency_ms=50,
            priority=7,
        ),
        # CLAUDE (Anthropic)
        ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_id="claude-opus-4-6",
            name="Claude Opus 4.6 (Anthropic)",
            capability_tier=CapabilityTier.EXPERT,
            api_endpoint="https://api.anthropic.com",
            supports_vision=True,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.015,
            latency_ms=500,
            priority=10,
        ),
        ModelConfig(
            provider=ModelProvider.CLAUDE,
            model_id="claude-sonnet-4-6",
            name="Claude Sonnet 4.6 (Anthropic)",
            capability_tier=CapabilityTier.ADVANCED,
            api_endpoint="https://api.anthropic.com",
            supports_vision=True,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.003,
            latency_ms=500,
            priority=9,
        ),
        # GPT (OpenAI)
        ModelConfig(
            provider=ModelProvider.GPT,
            model_id="gpt-4-turbo",
            name="GPT-4 Turbo (OpenAI)",
            capability_tier=CapabilityTier.EXPERT,
            api_endpoint="https://api.openai.com/v1",
            supports_vision=True,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.01,
            latency_ms=800,
            priority=10,
        ),
        ModelConfig(
            provider=ModelProvider.GPT,
            model_id="gpt-4o",
            name="GPT-4o (OpenAI)",
            capability_tier=CapabilityTier.ADVANCED,
            api_endpoint="https://api.openai.com/v1",
            supports_vision=True,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.005,
            latency_ms=800,
            priority=9,
        ),
        # GROK (xAI)
        ModelConfig(
            provider=ModelProvider.GROK,
            model_id="grok-1",
            name="Grok-1 (xAI)",
            capability_tier=CapabilityTier.ADVANCED,
            api_endpoint="https://api.x.ai",
            supports_vision=False,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.002,
            latency_ms=600,
            priority=8,
        ),
        # GEMINI (Google)
        ModelConfig(
            provider=ModelProvider.GEMINI,
            model_id="gemini-pro-vision",
            name="Gemini Pro Vision (Google)",
            capability_tier=CapabilityTier.ADVANCED,
            api_endpoint="https://generativelanguage.googleapis.com",
            supports_vision=True,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.0005,
            latency_ms=700,
            priority=8,
        ),
        # QWEN (Alibaba)
        ModelConfig(
            provider=ModelProvider.QWEN,
            model_id="qwen-max",
            name="Qwen Max (Alibaba)",
            capability_tier=CapabilityTier.ADVANCED,
            api_endpoint="https://dashscope.aliyuncs.com/api/v1",
            supports_vision=True,
            supports_streaming=True,
            is_local=False,
            cost_per_1k_tokens=0.008,
            latency_ms=900,
            priority=7,
        ),
    ]


# ============================================================================
# DISPATCHER INITIALIZATION
# ============================================================================

def create_dispatcher() -> IntelligentModelRouter:
    """Factory function to create dispatcher with default models"""
    models = create_default_models()
    return IntelligentModelRouter(models)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize dispatcher
    dispatcher = create_dispatcher()

    # Example: Route a coding task
    task = TaskContext(
        task_type=TaskType.CODING,
        query="Write a Python function to merge two sorted lists",
        require_streaming=True,
    )

    decision = dispatcher.select_model(task)
    print(f"\n📦 ROUTING DECISION")
    print(f"  Model: {decision.model_config.name}")
    print(f"  Provider: {decision.model_config.provider.value}")
    print(f"  Reason: {decision.reason}")
    print(f"  Confidence: {decision.confidence:.1%}")

    # Show alternatives
    if decision.alternatives:
        print(f"\n  Alternatives:")
        for alt in decision.alternatives:
            print(f"    • {alt.name}")

    # Example: Route different task types
    print(f"\n\n📊 MODEL ROUTING BY TASK TYPE")
    for task_type in TaskType:
        task = TaskContext(task_type=task_type, query="test")
        decision = dispatcher.select_model(task)
        print(f"  {task_type.value:15s} → {decision.model_config.name}")

    # List all available models
    print(f"\n\n📋 AVAILABLE MODELS")
    models = dispatcher.list_models()
    for model_id, details in models.items():
        print(f"  {model_id:25s} | {details['provider']:8s} | {details['capability']:10s} | Cost: {details['cost']}")
