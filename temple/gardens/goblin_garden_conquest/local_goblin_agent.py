#!/usr/bin/env python3
"""
local_goblin_agent.py — Local HELEN Goblin Brains (offline, Gemma4 + open source)

Purpose:
Migrate the HIGGSFIELD cloud agent setup to laptop-local using:
- Gemma4 (via Ollama) as the main "Goblin" brain
- Other local OSS models as needed
- Full HELEN invariants: authority=false, reflection ⊬ receipt, proposal ⊬ state
- Uses existing typed_memory.py for Garden Memory
- Produces only candidates; requires gate (e.g. operator stamp) to affect state

Run without WiFi:
1. Install Ollama + pull a model: ollama pull gemma2:9b   (or gemma2:2b for speed)
2. Run Ollama server (default http://localhost:11434)
3. python local_goblin_agent.py --role CHIDDUSH --query "patterns in proposals"

This is the starting point for the full migration of the game to LAPTOP HELEN LOCAL OS.
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Add the typed memory
sys.path.insert(0, str(Path(__file__).parent))
from typed_memory import GardenMemory, MemoryType

OLLAMA_URL = "http://localhost:11434/api/generate"

# The 200-epoch triad (hard constraint for all reasoning)
TRIAD = [
    "No location → no doctrine.",
    "No test → no gate.",
    "No replay → no admission."
]

ROLE_PROMPTS = {
    "GOBLIN": "You are a creative, chaotic goblin who loves low-cost hacks and mutations. Always suggest something practical but surprising.",
    "HER": "You are a nurturing, growth-oriented goblin who tends gardens and heals things. Focus on balance and beauty.",
    "CHIDDUSH": "You are a scholar goblin obsessed with patterns, laws, and higher-order insights. Always look for the underlying rule.",
    "CLAW": "You are a boundary guardian. You detect overreach, leaks, and violations. Be direct and protective.",
    "JESTER": "You are a chaos tester. You find the funny, surprising, or breaking edge case. Keep it bounded.",
    "ARCHIVIST": "You bind memories to receipts and keep the record clean. Everything must be locatable and replayable.",
    "WARDEN": "You watch for breaches and maintain stillness. Prioritize defense and verification.",
    "STEWARD": "You balance resources and routes. Make sure the whole system stays sustainable."
}

def call_local_model(prompt: str, model: str = "gemma2:9b", temperature: float = 0.7) -> str:
    """Call local Ollama. Falls back to stub if not available."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"[local] Ollama not reachable, using stub. ({e})")
    # Stub that still tries to respect the triad
    return f"Local candidate: {prompt[:80]}... [enforced: {TRIAD[0]}]"

def build_agent_prompt(role: str, query: str, memory_context: str) -> str:
    base = ROLE_PROMPTS.get(role, "You are a thoughtful goblin in the Warren.")
    triad_str = "\n".join(f"- {t}" for t in TRIAD)
    return f"""You are a {role} in the Goblin Warren, following the HELEN doctrine strictly.

TRIAD (non-negotiable):
{triad_str}

Your role guidance: {base}

Current context from memory:
{memory_context}

Task: {query}

Respond with ONE concise, actionable insight or proposal that respects the triad.
Start with "CANDIDATE:" and end with a short justification.
Do not claim truth. This is a proposal only."""

class LocalGoblin:
    """A single goblin brain running locally under HELEN rules."""

    def __init__(self, role: str, model: str = "gemma2:9b"):
        self.role = role
        self.model = model
        self.memory = GardenMemory(f"goblin_{role.lower()}")

    def observe(self, content: str):
        self.memory.add_observation(content, source=f"world:{self.role}", importance=0.6)

    def think(self, query: str) -> Dict[str, Any]:
        """Generate a reflection/plan CANDIDATE only. Never writes to state."""
        context = "\n".join(
            f"- [{e.type.value}] {e.content}"
            for e in self.memory.retrieve(query, top_k=5)
        )
        prompt = build_agent_prompt(self.role, query, context)
        raw = call_local_model(prompt, self.model)

        # Force it into candidate form
        content = raw.replace("CANDIDATE:", "").strip()
        candidate = {
            "role": self.role,
            "query": query,
            "content": content,
            "model": self.model,
            "triad_checked": any(t.split("→")[0].strip().lower() in content.lower() for t in TRIAD),
        }
        return candidate

    def propose(self, query: str) -> Dict[str, Any]:
        """Higher-level proposal. Still just a candidate."""
        cand = self.think(query)
        return {
            "type": "PROPOSAL_CANDIDATE",
            "from": self.role,
            "text": cand["content"],
            "triad_aligned": cand["triad_checked"],
            "requires_gate": True   # explicit
        }

def demo():
    print("=== HELEN LOCAL GOBLIN AGENT DEMO (offline) ===")
    print("Using Gemma4 (or fallback stub). All output is CANDIDATE only.\n")

    goblin = LocalGoblin("CHIDDUSH")
    goblin.observe("Observed repeated unconsumed packets in the outbox.")
    goblin.observe("The triad has held for 200 epochs.")

    proposal = goblin.propose("What pattern should we hunt next in the proposals?")
    print("Goblin proposal (CANDIDATE):")
    print(json.dumps(proposal, indent=2))
    print("\nThis must go through gate (stamp / operator / FABLE) before becoming memory or state.")
    print("reflection ⊬ receipt   |   proposal ⊬ state")

if __name__ == "__main__":
    demo()