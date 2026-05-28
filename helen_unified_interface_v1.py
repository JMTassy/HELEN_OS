"""
HELEN OS Unified Interface v1.0

Integrates:
- Configuration management
- Multi-model dispatcher
- API clients
- Task routing
- Response handling

Single interface for all HELEN OS multi-model operations.
"""

from typing import Optional, List, Dict, Any, Iterator
from pathlib import Path
from dataclasses import dataclass, asdict
import asyncio
import logging

from helen_config_manager_v1 import (
    ConfigManager,
    initialize_config,
    get_config_manager,
)
from helen_multimodel_dispatcher_v1 import (
    IntelligentModelRouter,
    create_dispatcher,
    TaskContext,
    TaskType,
    ModelProvider,
    RoutingDecision,
    ModelResponse,
)
from helen_api_clients_v1 import (
    create_client,
    BaseAPIClient,
    OllamaClient,
    ClaudeClient,
    GPTClient,
    GrokClient,
    GeminiClient,
    QwenClient,
)

logger = logging.getLogger(__name__)


# ============================================================================
# UNIFIED HELEN INTERFACE
# ============================================================================

class HELENMultiModel:
    """
    Unified HELEN OS interface for multi-model operations.

    Features:
    - Intelligent model selection
    - Automatic fallback
    - Cost tracking
    - Usage monitoring
    - Streaming support
    """

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        dispatcher: Optional[IntelligentModelRouter] = None,
    ):
        self.config = config_manager or get_config_manager()
        self.dispatcher = dispatcher or create_dispatcher()
        self.clients: Dict[str, BaseAPIClient] = {}
        self.response_history: List[ModelResponse] = []
        self.total_cost = 0.0

        logger.info("🧠 HELEN Multi-Model Interface initialized")

        # Initialize API clients for available providers
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize API clients for all configured providers"""
        for provider in ["ollama", "claude", "gpt", "grok", "gemini", "qwen"]:
            api_key = self.config.get_api_key(provider)

            try:
                if provider == "ollama":
                    # Ollama doesn't need API key
                    self.clients[provider] = OllamaClient()
                    logger.info(f"✅ {provider}: Client initialized")
                elif api_key:
                    self.clients[provider] = create_client(provider, api_key)
                    logger.info(f"✅ {provider}: Client initialized with API key")
                else:
                    logger.warning(f"⚠️  {provider}: No API key, client not initialized")
            except Exception as e:
                logger.error(f"❌ {provider}: Failed to initialize: {e}")

    def query(
        self,
        prompt: str,
        task_type: TaskType = TaskType.CONVERSATION,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        preferred_providers: Optional[List[ModelProvider]] = None,
        stream: bool = False,
    ) -> str:
        """
        Query with intelligent model selection.

        Process:
        1. Analyze task type
        2. Select optimal model
        3. Route to API client
        4. Handle response
        5. Track usage/cost
        """
        # Create task context
        task = TaskContext(
            task_type=task_type,
            query=prompt,
            require_streaming=stream,
            preferred_providers=preferred_providers or [],
        )

        # Get routing decision
        decision = self.dispatcher.select_model(task)
        logger.info(
            f"🎯 Routing to {decision.model_config.name} ({decision.reason})"
        )

        # Get client
        client = self.clients.get(decision.model_config.provider.value)

        if not client:
            # Try fallback
            if decision.alternatives:
                for alt in decision.alternatives:
                    fallback_client = self.clients.get(alt.provider.value)
                    if fallback_client:
                        logger.warning(
                            f"⚠️  Primary client unavailable, using fallback: {alt.name}"
                        )
                        client = fallback_client
                        decision.model_config = alt
                        break

        if not client:
            raise RuntimeError(
                f"No client available for {decision.model_config.provider.value}"
            )

        # Query model
        try:
            if stream:
                response_text = self._stream_response(
                    client,
                    prompt,
                    max_tokens,
                    temperature,
                )
            else:
                # Pass per-model metadata (Ollama-specific: real model name + think + num_ctx)
                meta = decision.model_config.metadata or {}
                extra: Dict[str, Any] = {}
                if decision.model_config.provider.value == "ollama":
                    if "ollama_model" in meta:
                        extra["model"] = meta["ollama_model"]
                    if "think" in meta:
                        extra["think"] = meta["think"]
                    if "num_ctx" in meta:
                        extra["num_ctx"] = meta["num_ctx"]
                response_text = client.query(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False,
                    **extra,
                )

            # Record response
            response = ModelResponse(
                provider=decision.model_config.provider,
                model_id=decision.model_config.model_id,
                content=response_text,
            )
            self.response_history.append(response)

            logger.info(
                f"✅ Response received ({len(response_text)} chars) "
                f"from {decision.model_config.name}"
            )

            return response_text

        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            raise

    def _stream_response(
        self,
        client: BaseAPIClient,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Stream response and accumulate"""
        full_response = ""

        try:
            for chunk in client.stream(prompt, max_tokens, temperature):
                print(chunk, end="", flush=True)
                full_response += chunk
        except NotImplementedError:
            # Fallback to non-streaming if not supported
            logger.warning("Streaming not supported, using standard mode")
            full_response = client.query(prompt, max_tokens, temperature)

        print()  # Newline after streaming
        return full_response

    async def query_async(
        self,
        prompt: str,
        task_type: TaskType = TaskType.CONVERSATION,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        preferred_providers: Optional[List[ModelProvider]] = None,
    ) -> str:
        """Async version of query"""
        task = TaskContext(
            task_type=task_type,
            query=prompt,
            require_streaming=False,
            preferred_providers=preferred_providers or [],
        )

        decision = self.dispatcher.select_model(task)
        client = self.clients.get(decision.model_config.provider.value)

        if not client:
            raise RuntimeError(f"No client for {decision.model_config.provider.value}")

        try:
            response_text = await client.query_async(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response = ModelResponse(
                provider=decision.model_config.provider,
                model_id=decision.model_config.model_id,
                content=response_text,
            )
            self.response_history.append(response)

            return response_text
        except Exception as e:
            logger.error(f"Async query failed: {e}")
            raise

    def get_routing_decision(
        self,
        task_type: TaskType,
        preferred_providers: Optional[List[ModelProvider]] = None,
    ) -> RoutingDecision:
        """Get routing decision without executing query"""
        task = TaskContext(
            task_type=task_type,
            query="",
            preferred_providers=preferred_providers or [],
        )
        return self.dispatcher.select_model(task)

    def list_available_models(self) -> Dict[str, Any]:
        """List all available models"""
        return self.dispatcher.list_models()

    def get_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "available_models": len(self.clients),
            "response_history": len(self.response_history),
            "total_cost": f"${self.total_cost:.4f}",
            "clients_initialized": list(self.clients.keys()),
            "config_status": self.config.get_status(),
            "dispatcher_ready": True,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        stats = {
            "total_requests": len(self.response_history),
            "responses": [],
        }

        for provider in set(r.provider.value for r in self.response_history):
            provider_responses = [r for r in self.response_history if r.provider.value == provider]
            stats["responses"].append({
                "provider": provider,
                "count": len(provider_responses),
                "total_tokens": sum(r.tokens_used for r in provider_responses),
                "total_cost": f"${sum(r.cost for r in provider_responses):.4f}",
            })

        return stats


# ============================================================================
# INTERACTIVE HELEN CLI
# ============================================================================

class HELENCLIInterface:
    """Interactive CLI for HELEN multi-model"""

    def __init__(self, helen: HELENMultiModel):
        self.helen = helen

    def print_welcome(self) -> None:
        """Print welcome banner"""
        print("\n" + "=" * 70)
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                                                                ║")
        print("║    🧠 HELEN OS — MULTI-MODEL UNIFIED INTERFACE 🧠              ║")
        print("║                                                                ║")
        print("║       Intelligent routing to 6 LLM providers                   ║")
        print("║                                                                ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print("=" * 70 + "\n")

    def print_help(self) -> None:
        """Print help message"""
        print("""
📖 HELEN MULTI-MODEL COMMANDS

Query Commands:
  ask <prompt>          — Query with auto-selected model
  ask-coding <prompt>   — Route to coding specialist
  ask-reasoning <prompt>— Route to reasoning specialist
  ask-creative <prompt> — Route to creative specialist
  ask-math <prompt>     — Route to math specialist
  ask-vision <prompt>   — Route to vision model

System Commands:
  models               — List available models
  routing <type>       — Show routing decision for task type
  status               — System status
  stats                — Usage statistics
  config               — Show configuration
  help                 — This message
  quit                 — Exit

Examples:
  ask What is Python?
  ask-coding Write a merge sort
  ask-reasoning Explain quantum entanglement
  ask-math Solve: 2x + 3 = 7
  routing reasoning
""")

    def run(self) -> None:
        """Run interactive CLI"""
        self.print_welcome()

        while True:
            try:
                user_input = input("\n[HELEN] > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 HELEN OS shutting down...")
                    break

                elif user_input.lower() == "help":
                    self.print_help()

                elif user_input.lower() == "models":
                    self._show_models()

                elif user_input.lower() == "status":
                    self._show_status()

                elif user_input.lower() == "stats":
                    self._show_stats()

                elif user_input.lower() == "config":
                    self._show_config()

                elif user_input.startswith("routing "):
                    task_type_str = user_input[8:].strip().upper()
                    self._show_routing(task_type_str)

                elif user_input.startswith("ask "):
                    prompt = user_input[4:].strip()
                    self._query(prompt, TaskType.CONVERSATION)

                elif user_input.startswith("ask-coding "):
                    prompt = user_input[11:].strip()
                    self._query(prompt, TaskType.CODING)

                elif user_input.startswith("ask-reasoning "):
                    prompt = user_input[14:].strip()
                    self._query(prompt, TaskType.REASONING)

                elif user_input.startswith("ask-creative "):
                    prompt = user_input[13:].strip()
                    self._query(prompt, TaskType.CREATIVE)

                elif user_input.startswith("ask-math "):
                    prompt = user_input[9:].strip()
                    self._query(prompt, TaskType.MATH)

                elif user_input.startswith("ask-vision "):
                    prompt = user_input[11:].strip()
                    self._query(prompt, TaskType.VISION)

                else:
                    print("❓ Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _query(self, prompt: str, task_type: TaskType) -> None:
        """Execute query"""
        try:
            print(f"\n🤔 Thinking (task type: {task_type.value})...\n")
            decision = self.helen.get_routing_decision(task_type)
            print(f"📦 Selected: {decision.model_config.name}")
            print(f"   Reason: {decision.reason}")
            print(f"   Confidence: {decision.confidence:.0%}\n")

            helen_node_context = (
                "SYSTEM CONTEXT - HELEN LOCAL NODE\n"
                "You are operating inside the user's local HELEN OS node.\n"
                "Architecture:\n"
                "- Windows host runs Ollama with NVIDIA RTX 5070 GPU acceleration.\n"
                "- WSL2 Ubuntu runs the HELEN repository and Python interface.\n"
                "- Active interface: helen_unified_interface_v1.\n"
                "- Active backend: Ollama HTTP API at http://127.0.0.1:11434.\n"
                "- Active local model: gemma3:12b.\n"
                "- Repository path: ~/helen-conquest.\n"
                "- Mode: local-first, private, zero cloud cost unless external API keys added.\n"
                "Behavior:\n"
                "- Do not claim to be a generic remote HELEN network node.\n"
                "- When asked about this HELEN node, refer to the local MRED/WSL2/Ollama/Gemma/RTX setup.\n"
                "- Be precise, operational, and concise. Do not ask the user for logs you already have above.\n"
            )
            prompt = helen_node_context + "\nUSER REQUEST:\n" + prompt

            response = self.helen.query(prompt, task_type=task_type, stream=True)
        except Exception as e:
            print(f"❌ Query failed: {e}")

    def _show_models(self) -> None:
        """Show available models"""
        models = self.helen.list_available_models()
        print("\n📋 AVAILABLE MODELS\n")
        for model_id, details in models.items():
            print(f"  {model_id}")
            for key, value in details.items():
                print(f"    • {key}: {value}")
            print()

    def _show_status(self) -> None:
        """Show system status"""
        status = self.helen.get_status()
        print("\n📊 SYSTEM STATUS\n")
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    • {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")
        print()

    def _show_stats(self) -> None:
        """Show usage statistics"""
        stats = self.helen.get_stats()
        print("\n📈 USAGE STATISTICS\n")
        print(f"  Total Requests: {stats['total_requests']}")
        if stats["responses"]:
            print(f"\n  By Provider:")
            for provider_stats in stats["responses"]:
                print(f"    {provider_stats['provider']}:")
                print(f"      • Requests: {provider_stats['count']}")
                print(f"      • Tokens: {provider_stats['total_tokens']}")
                print(f"      • Cost: {provider_stats['total_cost']}")
        print()

    def _show_config(self) -> None:
        """Show configuration"""
        status = self.helen.config.get_status()
        print("\n⚙️  CONFIGURATION\n")
        print("  Available Providers:")
        for p in status["available_providers"]:
            print(f"    ✅ {p}")
        print()

    def _show_routing(self, task_type_str: str) -> None:
        """Show routing decision"""
        try:
            task_type = TaskType[task_type_str]
            decision = self.helen.get_routing_decision(task_type)

            print(f"\n🎯 ROUTING: {task_type.value.upper()}\n")
            print(f"  Primary: {decision.model_config.name}")
            print(f"  Reason: {decision.reason}")
            print(f"  Confidence: {decision.confidence:.0%}")

            if decision.alternatives:
                print(f"\n  Alternatives:")
                for alt in decision.alternatives:
                    print(f"    • {alt.name}")
            print()
        except KeyError:
            print(f"❌ Unknown task type: {task_type_str}")
            print(f"   Valid types: {', '.join(t.name for t in TaskType)}")


# ============================================================================
# FACTORY & INITIALIZATION
# ============================================================================

def create_helen_interface(
    config_dir: Optional[str] = None,
) -> HELENMultiModel:
    """Factory function to create HELEN interface"""
    config = initialize_config() if not config_dir else initialize_config(Path(config_dir))
    helen = HELENMultiModel(config)
    return helen


if __name__ == "__main__":
    # Initialize HELEN
    helen = create_helen_interface()

    # Start CLI
    cli = HELENCLIInterface(helen)
    cli.run()
