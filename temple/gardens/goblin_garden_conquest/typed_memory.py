"""
typed_memory.py — HELEN's Typed Garden Memory for Generative Agents

This implements a strengthened version of the Generative Agents memory architecture,
adapted to HELEN's invariants:

- Typed artifacts (not just natural language)
- Proposal → Validation → Receipt → Ledger
- proposal ⊬ state
- authority=false for all internal cognition
- Full replay from ledger

Inspired by "Generative Agents: Interactive Simulacra of Human Behavior" (Park et al., UIST 2023)
but with constitutional membranes, typed knowledge, and deterministic replay.

All changes are garden-only. No sovereign writes.

Core flow:
Observation (from environment or other agents)
  ↓
Garden Memory (typed entry)
  ↓
Typed Retrieval (relevance + recency + importance + type filters)
  ↓
Local Reasoning / Reflection Candidates (local models or LLM with contracts)
  ↓
Independent Validation (schema, WULmath, tests)
  ↓
Human Constitutional Gate (or FABLE min-gate for proposals)
  ↓
Receipt (claimable action)
  ↓
Immutable Ledger (append-only in garden)
  ↓
Replayable State

"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
import json
import hashlib
from pathlib import Path

class MemoryType(Enum):
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    PLAN = "plan"
    PROPOSAL = "proposal"
    RECEIPT = "receipt"
    EVENT = "event"

@dataclass
class MemoryEntry:
    """Typed memory entry. Never raw string."""
    id: str
    type: MemoryType
    content: str  # natural language summary, but typed
    timestamp: str
    importance: float  # 0-1
    source: str  # e.g. "environment", "agent:John", "reflection"
    evidence: List[str] = field(default_factory=list)  # hashes or ids of prior entries
    metadata: Dict[str, Any] = field(default_factory=dict)  # e.g. {"role": "GOBLIN", "seed": 42}

    def to_dict(self):
        d = asdict(self)
        d['type'] = self.type.value
        return d

    @classmethod
    def from_dict(cls, d):
        d = d.copy()
        d['type'] = MemoryType(d['type'])
        return cls(**d)

class GardenMemory:
    """
    The 'Garden Memory' in HELEN terms.
    Stores typed entries.
    Retrieval is typed and scored.
    Changes produce receipts, never mutate in place without gate.
    """

    def __init__(self, agent_id: str, ledger_path: Optional[Path] = None):
        self.agent_id = agent_id
        self.entries: List[MemoryEntry] = []
        self.ledger_path = ledger_path or Path(f"scratch/{agent_id}_memory_ledger.jsonl")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def _hash_entry(self, entry: MemoryEntry) -> str:
        canon = json.dumps(entry.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode()).hexdigest()[:16]

    def add_observation(self, content: str, source: str = "environment", importance: float = 0.5, metadata: Optional[Dict] = None) -> MemoryEntry:
        """Add raw observation. This is a proposal stage."""
        entry = MemoryEntry(
            id=self._hash_entry(MemoryEntry("", MemoryType.OBSERVATION, content, "", 0.0, source, [], metadata or {})),
            type=MemoryType.OBSERVATION,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=importance,
            source=source,
            metadata=metadata or {}
        )
        # In full system, this would go through validation before commit.
        # Here we append directly for the garden layer (non-sovereign simulation).
        self.entries.append(entry)
        self._append_to_ledger(entry)
        return entry

    def retrieve(self, query: str, top_k: int = 5, type_filter: Optional[MemoryType] = None) -> List[MemoryEntry]:
        """
        Typed retrieval.
        Score = recency + importance + semantic (simple keyword for demo; in real use embedding).
        """
        scored = []
        now = datetime.now(timezone.utc)
        for e in self.entries:
            if type_filter is None:
                # SEAM 2 (Isabella drift, Generative Agents §7.2): a REFLECTION is a
                # candidate, not admitted working memory. It must NOT re-enter default
                # retrieval as if it were an observation — that is how unverified
                # reflection contaminates identity and compounds through the reflection
                # tree. Opt in explicitly with type_filter=MemoryType.REFLECTION.
                # Non-implication enforced: reflection ⊬ observation.
                if e.type == MemoryType.REFLECTION:
                    continue
            elif e.type != type_filter:
                continue
            # Recency (exponential decay)
            ts = datetime.fromisoformat(e.timestamp)
            recency = max(0, 1 - (now - ts).total_seconds() / (24*3600*7))  # decay over week
            # Importance
            imp = e.importance
            # Simple semantic (keyword overlap)
            keywords = set(query.lower().split())
            content_words = set(e.content.lower().split())
            sem = len(keywords & content_words) / max(1, len(keywords))
            score = 0.4 * recency + 0.4 * imp + 0.2 * sem
            scored.append((score, e))

        scored.sort(reverse=True)
        return [e for _, e in scored[:top_k]]

    def reflect(self, query: str, local_reasoner: callable) -> List[MemoryEntry]:
        """
        Generate reflection candidates.
        In HELEN, this would produce PROPOSAL, validated before commit.
        Here we use the provided local_reasoner (e.g. a stub or Ollama call).
        """
        relevant = self.retrieve(query, top_k=8)
        context = "\n".join([f"- [{e.type.value}] {e.content}" for e in relevant])
        prompt = f"Based on these memories for {self.agent_id}:\n{context}\n\nSynthesize a high-level reflection about: {query}\nReturn a single sentence insight."
        insight = local_reasoner(prompt)  # e.g. "Klaus is highly dedicated to research."
        reflection = MemoryEntry(
            id=self._hash_entry(MemoryEntry("", MemoryType.REFLECTION, insight, "", 0.8, "reflection", [e.id for e in relevant])),
            type=MemoryType.REFLECTION,
            content=insight,
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=0.8,
            source="reflection",
            evidence=[e.id for e in relevant]
        )
        self.entries.append(reflection)
        self._append_to_ledger(reflection)
        return [reflection]

    def plan(self, current_context: str, local_planner: callable) -> MemoryEntry:
        """
        Hierarchical plan from retrieval + reflection.
        Produces PLAN entry (as proposal candidate in full HELEN).
        """
        relevant = self.retrieve(current_context, top_k=5, type_filter=MemoryType.REFLECTION)
        context = "\n".join([e.content for e in relevant])
        plan_text = local_planner(f"Given reflections: {context}\nCurrent context: {current_context}\nCreate a short hierarchical plan (Day -> Morning -> specific actions).")
        plan = MemoryEntry(
            id=self._hash_entry(MemoryEntry("", MemoryType.PLAN, plan_text, "", 0.7, "plan", [e.id for e in relevant])),
            type=MemoryType.PLAN,
            content=plan_text,
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=0.7,
            source="plan",
            evidence=[e.id for e in relevant]
        )
        self.entries.append(plan)
        self._append_to_ledger(plan)
        return plan

    # --- HELEN 2026 strengthened pipeline (per Generative Agents critique) ---

    def observe(self, content: str, source: str = "environment", importance: float = 0.5, metadata: Optional[Dict] = None) -> MemoryEntry:
        """Entry point: raw observation into Garden Memory (typed)."""
        return self.add_observation(content, source, importance, metadata)

    def generate_reflection_candidates(self, query: str, local_reasoner: callable) -> List[MemoryEntry]:
        """Reflection Candidates stage (before validation)."""
        return self.reflect(query, local_reasoner)

    def validate_and_receipt(self, candidate: MemoryEntry, validator: callable) -> Optional[MemoryEntry]:
        """
        Independent Validation + Constitutional Gate (stub).
        In full system: run schema/WULmath/tests, then FABLE/human gate.
        Returns a RECEIPT entry only if valid.
        """
        if not validator(candidate):
            return None  # rejected
        receipt = MemoryEntry(
            id=self._hash_entry(MemoryEntry("", MemoryType.RECEIPT, f"RECEIPT for {candidate.id}: {candidate.content[:50]}", "", 0.9, "gate", [candidate.id])),
            type=MemoryType.RECEIPT,
            content=f"Validated and receipted: {candidate.content}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=0.9,
            source="constitutional_gate",
            evidence=[candidate.id],
            metadata={"validated": True, "proposal_id": candidate.id}
        )
        self.entries.append(receipt)
        self._append_to_ledger(receipt)
        return receipt

    def full_step(self, observation: str, reasoner: callable, planner: callable, validator: callable) -> Dict[str, Any]:
        """
        One full HELEN-strengthened cycle for a generative agent:
        Observe -> Garden Memory -> Retrieve -> Local Reasoning -> Reflection Candidates -> Validation -> Receipt
        """
        obs = self.observe(observation)
        reflections = self.generate_reflection_candidates(observation, reasoner)
        plan = self.plan(observation, planner)

        # Validate the reflection and/or plan as proposals
        validated = []
        for cand in reflections + [plan]:
            rec = self.validate_and_receipt(cand, validator)
            if rec:
                validated.append(rec)

        return {
            "observation": obs,
            "reflections": reflections,
            "plan": plan,
            "receipts": validated
        }

    def _append_to_ledger(self, entry: MemoryEntry):
        """Append-only ledger for replay."""
        with self.ledger_path.open("a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def replay(self) -> List[MemoryEntry]:
        """Deterministic replay from ledger."""
        if not self.ledger_path.exists():
            return []
        entries = []
        with self.ledger_path.open() as f:
            for line in f:
                if line.strip():
                    entries.append(MemoryEntry.from_dict(json.loads(line)))
        return entries

# Example local "reasoner" stub (in real, call Ollama/Qwen with contract)
def stub_reasoner(prompt: str) -> str:
    # In production this would be a contracted local model call.
    if "research" in prompt.lower():
        return "Klaus is highly dedicated to research and creative writing."
    return "The agent is focused on daily routines and social interactions."

def stub_planner(prompt: str) -> str:
    return "Morning: wake, breakfast, walk. Midday: work at pharmacy. Evening: social at cafe."

# Example usage in Warren simulation (CONQUEST roles)
def role_validator(entry: MemoryEntry) -> bool:
    """Stub constitutional validator (in real: schema + WULmath + FABLE min-gate)."""
    if entry.type == MemoryType.PROPOSAL:
        return False  # proposals need explicit gate
    return "proposal" not in entry.content.lower()  # simple check

if __name__ == "__main__":
    # Example for a CONQUEST role agent (e.g. CHIDDUSH scholar)
    mem = GardenMemory("chiddush_agent")
    mem.observe("Observed repeated patterns in garden proposals.", source="environment", importance=0.7, metadata={"role": "CHIDDUSH"})
    mem.observe("Klaus is highly dedicated to research.", source="reflection", importance=0.8, metadata={"role": "CHIDDUSH"})

    result = mem.full_step(
        observation="New proposal in outbox about unconsumed packets.",
        reasoner=stub_reasoner,
        planner=stub_planner,
        validator=role_validator
    )

    print("HELEN Generative Agent step (CHIDDUSH role):")
    print("  Observation:", result["observation"].content)
    print("  Reflections:", [r.content for r in result["reflections"]])
    print("  Plan:", result["plan"].content)
    print("  Receipts:", len(result["receipts"]))
    print("Replay length:", len(mem.replay()))